"""
octool/core/engines/audio_capture_engine.py
───────────────────────────────────────────────
音频采集（录音）引擎——核心引擎层，只封装第三方库，不写业务。

提供（采集模式统一由 record() 收口）：
  - default_loopback_device()          定位默认扬声器对应的回环采集设备
  - LoopbackCapture(on_frames, on_error) 后台线程持续采集系统内置声音（WASAPI 回环）
  - MicCapture(on_frames, on_error)      后台线程持续采集麦克风（默认输入设备）
  - record(mode, on_frames, on_error)    按模式（loopback / mic）启动采集线程
  - to_16k_mono(rate, channels, data)   任意采样率 / 声道 → 16kHz 单声道 int16
  - write_16k_mono_wav(path, data)      16kHz 单声道 → WAV 文件

依赖：PyAudioWPatch（回环）/ pyaudio（麦克风）。
"""

import threading
import wave

import numpy as np

# 语音识别采样率（SenseVoice 推荐）
VOICE_TARGET_RATE = 16000


# ════════════════════════════════════════════
#  设备定位
# ════════════════════════════════════════════

def default_loopback_device():
    """定位默认扬声器对应的 WASAPI Loopback（回环）采集设备。

    返回 (index, sample_rate, channels)，找不到则抛 RuntimeError。
    """
    import pyaudiowpatch as pyaudio
    p = pyaudio.PyAudio()
    try:
        wasapi = p.get_host_api_info_by_type(pyaudio.paWASAPI)
        out = p.get_device_info_by_index(wasapi["defaultOutputDevice"])
        out_name = out["name"]
        best = None
        for lp in p.get_loopback_device_info_generator():
            if out_name in lp["name"]:
                best = lp
                break
        if best is None:
            # 兜底：取第一个回环设备
            for lp in p.get_loopback_device_info_generator():
                best = lp
                break
        if best is None:
            raise RuntimeError("未找到可用的系统内置声音（WASAPI 回环）采集设备")
        return (int(best["index"]),
                int(best.get("defaultSampleRate", 48000)),
                int(best.get("maxInputChannels", 2) or 2))
    finally:
        p.terminate()


# ════════════════════════════════════════════
#  音频转换工具
# ════════════════════════════════════════════

def to_16k_mono(rate: int, channels: int, data: bytes) -> bytes:
    """把任意采样率 / 声道数的 int16 PCM 下混 + 重采样为 16kHz 单声道"""
    rate = int(rate) if rate else 48000
    channels = max(1, int(channels or 1))
    a = np.frombuffer(data, dtype=np.int16)
    if len(a) == 0:
        return b""
    if channels > 1:
        usable = len(a) - len(a) % channels
        a = a[:usable].reshape(-1, channels).mean(axis=1).astype(np.int16)
    if rate != VOICE_TARGET_RATE and len(a) > 1:
        n_out = max(1, int(len(a) * VOICE_TARGET_RATE / rate))
        a = np.interp(
            np.linspace(0, len(a) - 1, n_out),
            np.arange(len(a)),
            a.astype(np.float32)).astype(np.int16)
    return a.tobytes()


def write_16k_mono_wav(path: str, mono16k: bytes):
    """把 16kHz 单声道 int16 PCM 写入 WAV 文件"""
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(VOICE_TARGET_RATE)
        wf.writeframes(mono16k)


# ════════════════════════════════════════════
#  后台采集线程（WASAPI Loopback）
# ════════════════════════════════════════════

class LoopbackCapture(threading.Thread):
    """持续采集系统内置声音，经 on_frames(rate, channels, data) 回传原始帧；
    on_error(msg) 回传采集异常。停止通过 stop() 置事件标志。"""

    def __init__(self, on_frames, on_error):
        super().__init__(daemon=True)
        self._on_frames = on_frames
        self._on_error = on_error
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def run(self):
        import pyaudiowpatch as pyaudio
        index, rate, channels = default_loopback_device()
        p = pyaudio.PyAudio()
        stream = None
        try:
            stream = p.open(
                format=pyaudio.paInt16,
                channels=channels,
                rate=rate,
                input=True,
                input_device_index=index,
                frames_per_buffer=2048,
            )
            while not self._stop.is_set():
                data = stream.read(2048, exception_on_overflow=False)
                self._on_frames(rate, channels, data)
        except Exception as e:  # noqa: BLE001
            try:
                self._on_error(str(e))
            except Exception:
                pass
        finally:
            if stream is not None:
                try:
                    stream.stop_stream()
                    stream.close()
                except Exception:
                    pass
            try:
                p.terminate()
            except Exception:
                pass


# ════════════════════════════════════════════
#  后台采集线程（麦克风）
# ════════════════════════════════════════════

class MicCapture(threading.Thread):
    """麦克风采集线程（默认输入设备），回调签名与 LoopbackCapture 一致

    回调：on_frames(rate, channels, pcm_bytes)；on_error(msg)。
    停止：stop()（线程安全，置事件标志后优雅退出）。
    """

    def __init__(self, on_frames, on_error, rate: int = 48000,
                 channels: int = 1, frames_per_buffer: int = 2048):
        super().__init__(daemon=True)
        self._on_frames = on_frames
        self._on_error = on_error
        self._rate = rate
        self._channels = channels
        self._frame_size = frames_per_buffer
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def run(self):
        import pyaudio
        p = pyaudio.PyAudio()
        stream = None
        try:
            rate = self._rate
            channels = self._channels
            # 默认输入设备不可用时，尝试系统默认采样率
            try:
                dev = p.get_default_input_device_info()
                rate = int(dev.get("defaultSampleRate", rate) or rate)
                channels = min(max(1, int(dev.get("maxInputChannels", channels) or 1)), 2)
            except Exception:
                pass
            stream = p.open(
                format=pyaudio.paInt16,
                channels=channels,
                rate=rate,
                input=True,
                frames_per_buffer=self._frame_size,
            )
            while not self._stop.is_set():
                data = stream.read(self._frame_size, exception_on_overflow=False)
                if data:
                    self._on_frames(rate, channels, data)
        except Exception as e:  # noqa: BLE001
            try:
                self._on_error(str(e))
            except Exception:
                pass
        finally:
            if stream is not None:
                try:
                    stream.stop_stream()
                    stream.close()
                except Exception:
                    pass
            try:
                p.terminate()
            except Exception:
                pass


# ════════════════════════════════════════════
#  统一采集入口
# ════════════════════════════════════════════

def record(mode: str = "loopback", on_frames=None, on_error=None):
    """启动一次录音，返回可 stop() 的采集线程对象

    mode："loopback" 采集系统内置声音；"mic" 采集麦克风。
    on_frames(rate, channels, pcm)：每帧回调；on_error(msg)：异常回调。
    """
    if mode == "mic":
        return MicCapture(on_frames, on_error)
    return LoopbackCapture(on_frames, on_error)


# ════════════════════════════════════════════
#  自测
# ════════════════════════════════════════════

if __name__ == "__main__":
    # 验证能定位到系统回环设备
    try:
        idx, rate, ch = default_loopback_device()
        print(f"✅ 系统内置声音（回环）设备: index={idx} {rate}Hz {ch}ch")
    except Exception as e:
        print(f"ℹ 回环设备不可用（不影响麦克风）: {e}")