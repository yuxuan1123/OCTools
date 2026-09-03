"""
octool/services/recipes/builtin_speech_recognize.py
───────────────────────────────────────────────────────
拼接配方 · 内置语音识别 = 录音 + 语音识别

纯逻辑拼接，不可增减功能：
  1. 录音（core/engines/audio_capture_engine）持续采集系统内置声音 / 麦克风
  2. 语音识别（core/engines/speech_engine）把音频转换为文本

输出：result_ready(识别文本)，status 阶段反馈，error 异常（不中断循环）。
运行中可暂停（set_paused）——暂停时停止定时识别但保持录音缓冲。
本组件是控制器（QObject + 信号），不含任何 UI 控件。
"""

import threading

from PySide6.QtCore import QObject, Signal

from core.engines.audio_capture_engine import (
    VOICE_TARGET_RATE, record, to_16k_mono,
)
from core.engines.speech_engine import transcribe_pcm16k
from ui.ui_component.timer import TimerComponent

# 默认识别间隔（毫秒）
DEFAULT_INTERVAL_MS = 3000

# 小于该时长（秒）的音频忽略（避免静音片段触发识别）
MIN_SECONDS = 0.3


class BuiltinSpeechRecognize(QObject):
    """定时循环：后台录音 → 定时取走缓冲音频做语音识别"""

    result_ready = Signal(str)   # 识别文本（空文本不发）
    status = Signal(str)
    error = Signal(str)
    paused_changed = Signal(bool)

    def __init__(self, mode: str = "loopback", interval_ms: int = DEFAULT_INTERVAL_MS,
                 stt_config=None, parent=None):
        super().__init__(parent)
        self._mode = mode if mode in ("loopback", "mic") else "loopback"
        self._stt_config = stt_config
        self._busy = False
        self._stopped = False
        self._paused = False
        self._capture = None
        self._frames = []
        self._lock = threading.Lock()
        self._target_rate = VOICE_TARGET_RATE
        self._timer = TimerComponent(interval_ms=interval_ms, on_tick=self._on_tick)

    # ── 控制 ──

    def start(self):
        """启动录音与定时识别"""
        if self._stopped is False and self._capture is not None:
            return   # 已在运行
        self._stopped = False
        self._paused = False
        self._lock = threading.Lock()
        self._frames = []
        self._capture = record(self._mode, self._on_frames,
                               self._on_capture_error)
        self._capture.start()
        self._timer.start()
        self._on_tick()  # 立即尝试第一轮（缓冲未满时自动跳过）

    def stop(self):
        """停止录音与定时识别（幂等）"""
        self._stopped = True
        self._timer.stop()
        if self._capture is not None:
            try:
                self._capture.stop()
            except Exception:
                pass
            self._capture = None
        with self._lock:
            self._frames = []

    def set_paused(self, paused: bool):
        """暂停（True）/ 恢复（False）定时识别；暂停期间录音继续缓冲"""
        paused = bool(paused)
        if paused == self._paused or self._stopped:
            return
        self._paused = paused
        if paused:
            self._timer.stop()
        else:
            self._timer.start()
            self._on_tick()
        self.paused_changed.emit(self._paused)

    def is_paused(self) -> bool:
        return self._paused

    def is_running(self) -> bool:
        return not self._stopped and self._capture is not None

    def refresh_now(self):
        """手动触发一轮识别（上一轮未完成则自动跳过）"""
        if not self._stopped and not self._paused:
            self._on_tick()

    def set_interval(self, ms: int):
        self._timer.set_interval(max(500, int(ms)))

    # ── 音频回调（采集线程）──

    def _on_frames(self, rate, channels, data):
        try:
            frame = to_16k_mono(rate, channels, data)
        except Exception:
            return
        with self._lock:
            if not self._stopped:
                self._frames.append(frame)

    def _on_capture_error(self, msg):
        self.error.emit(f"录音失败: {msg}")

    # ── 定时识别 ──

    def _on_tick(self):
        if self._busy or self._stopped or self._paused:
            return
        with self._lock:
            if not self._frames:
                return
            data = b"".join(self._frames)
            self._frames = []
        min_len = int(self._target_rate * MIN_SECONDS * 2)
        if not data or len(data) < min_len:
            return
        self._busy = True
        threading.Thread(target=self._process, args=(data,), daemon=True).start()

    def _process(self, data):
        """工作线程：语音识别 → 信号回传（不碰任何 Qt 控件）"""
        try:
            self.status.emit("⏳ 正在加载语音识别模型（首次约 20-30 秒）…")
            text = transcribe_pcm16k(
                data, log=lambda m: None, config=self._stt_config)
            if self._stopped:
                return
            if not text:
                self.status.emit("（未识别到有效语音）")
                return
            self.result_ready.emit(text)
        except RuntimeError:
            pass   # 控制器已被销毁（退出中），忽略跨线程回传
        except Exception as e:
            if not self._stopped:
                self.error.emit(str(e))
        finally:
            self._busy = False