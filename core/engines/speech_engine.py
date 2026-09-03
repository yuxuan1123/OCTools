"""
octool/core/engines/speech_engine.py
───────────────────────────────────────────────
语音识别（ASR / STT）引擎：音频 → 文本（txt）—— 核心引擎层

实现参考 mvp/stt.py：
  - funasr AutoModel + SenseVoiceSmall 本地模型（默认路径与 mvp 完全一致）
  - disable_update=True 完全离线，不联网
  - 识别结果用 rich_transcription_postprocess 做标点恢复
  - 识别前用 ffmpeg 统一转为 16kHz 单声道 WAV（SenseVoice 推荐输入）

设计要点（与 core/engines/tts_engine.py 对齐）：
  - SttConfig 数据模型（模型目录 / 设备 / 语言 / 数字归一化）
  - 模型按需懒加载 + 进程内缓存，避免启动卡顿
  - audio_to_text() 签名与转换引擎统一：(input, output, log) -> bool

旧路径 src/stt.py 保留为兼容 shim（re-export 本模块）。
"""

import os
import tempfile

from core.utils.file_handler import file_exists, write_text
from config.stt_config import (
    STT_LANGUAGE_LABELS, SttConfig, default_config,
)

# ════════════════════════════════════════════
#  配置
# ════════════════════════════════════════════
# 配置模型与常量（STT_DEFAULT_MODEL_DIR / STT_DEVICE_LABELS /
# STT_LANGUAGE_LABELS / SttConfig / default_config）见 config/stt_config.py，
# 本模块不再重复定义。


# ════════════════════════════════════════════
#  引擎懒加载单例
# ════════════════════════════════════════════

_STT_MODEL = None
_STT_MODEL_KEY = None


def _ensure_model(cfg: SttConfig):
    """创建/复用 funasr 模型（按 模型目录+设备 缓存）"""
    global _STT_MODEL, _STT_MODEL_KEY
    key = (cfg.model_dir, cfg.device)
    if _STT_MODEL is not None and _STT_MODEL_KEY == key:
        return _STT_MODEL
    try:
        from funasr import AutoModel
    except ImportError as e:
        raise RuntimeError(
            "funasr 未安装，请执行: pip install funasr（音频转文字需要）") from e
    _STT_MODEL = AutoModel(
        model=cfg.model_dir,   # 本地路径，不是模型名
        device=cfg.device,
        disable_update=True,   # 阻止一切联网请求
    )
    _STT_MODEL_KEY = key
    return _STT_MODEL


# ════════════════════════════════════════════
#  音频预处理（ffmpeg → 16kHz 单声道 WAV）
# ════════════════════════════════════════════

def _to_16k_mono_wav(audio_path: str, log) -> str:
    """把任意音频转为 SenseVoice 推荐的 16kHz 单声道 WAV，返回临时路径"""
    from core.engines.ffmpeg_utils import _run_ffmpeg
    tmp = tempfile.mktemp(prefix="stt_", suffix=".wav")
    ok, _ = _run_ffmpeg(
        ["-i", audio_path, "-ar", "16000", "-ac", "1", "-vn", tmp],
        log, quiet=True)
    if ok and os.path.exists(tmp) and os.path.getsize(tmp) > 0:
        return tmp
    # ffmpeg 失败（如 amr 解码问题）：直接交给 funasr 尝试原始文件
    if os.path.exists(tmp):
        try:
            os.remove(tmp)
        except Exception:
            pass
    log("   ⚠ ffmpeg 预处理失败，尝试直接识别原始音频…")
    return audio_path


# ════════════════════════════════════════════
#  识别
# ════════════════════════════════════════════

def transcribe_audio(audio_path, log=lambda m: print(m), config=None) -> str:
    """识别音频并返回文本（含标点）；失败抛异常或返回 ""。"""
    cfg = config or default_config()
    errors = cfg.validate()
    if errors:
        for e in errors:
            log(f"❌ {e}")
        return ""

    wav = _to_16k_mono_wav(audio_path, log)
    try:
        model = _ensure_model(cfg)
        lang_label = dict(STT_LANGUAGE_LABELS).get(cfg.language, cfg.language)
        log(f"🎙️ 语音识别中（语言: {lang_label}，模型: {os.path.basename(cfg.model_dir)}）…")
        result = model.generate(
            input=wav,
            language=cfg.language,
            use_itn=cfg.use_itn,
        )
        if not result:
            log("❌ 识别无结果")
            return ""
        from funasr.utils.postprocess_utils import rich_transcription_postprocess
        return rich_transcription_postprocess(result[0].get("text", ""))
    finally:
        if wav != audio_path and os.path.exists(wav):
            try:
                os.remove(wav)
            except Exception:
                pass


def transcribe_pcm16k(mono16k: bytes, log=lambda m: print(m), config=None) -> str:
    """识别一段 16kHz 单声道 int16 PCM（bytes），返回文本

    内部写入临时 wav 再识别，完成后自动清理。config: SttConfig。
    """
    from core.engines.audio_capture_engine import write_16k_mono_wav
    tmp = None
    try:
        tmp = tempfile.mktemp(prefix="asr_", suffix=".wav")
        write_16k_mono_wav(tmp, mono16k)
        return transcribe_audio(tmp, log=log, config=config)
    finally:
        if tmp and os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass


# ════════════════════════════════════════════
#  转换函数（与转换引擎统一签名）
# ════════════════════════════════════════════

def audio_to_text(input_path, output_path, log=lambda m: print(m), config=None) -> bool:
    """音频 → TXT（语音识别）。config: SttConfig（引擎/语言等）"""
    if not file_exists(input_path, log):
        return False
    try:
        ext = os.path.splitext(input_path)[1].lower().lstrip(".")
        log(f"🔄 {ext.upper()} → TXT（语音识别）: {os.path.basename(input_path)}")
        text = transcribe_audio(input_path, log, config)
        text = (text or "").strip()
        if not text:
            log("❌ 未能识别出文本（音频可能为空或无人声）")
            return False
        os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
        write_text(output_path, text)
        log(f"✅ 完成 → {output_path}（{len(text)} 字符）")
        return True
    except Exception as e:
        log(f"❌ {e}")
        return False


# ════════════════════════════════════════════
#  自测
# ════════════════════════════════════════════

if __name__ == "__main__":
    import time
    import os as _os
    _root = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
    sample = _os.path.join(_root, "assets", "voices_model", "zf_xiaobei.wav")
    if not os.path.exists(sample):
        print("未找到测试音频，跳过自测")
    else:
        start = time.perf_counter()
        text = transcribe_audio(sample)
        print(f"识别结果: {text}")
        print(f"\n⏱ 总耗时: {time.perf_counter() - start:.3f} 秒")
