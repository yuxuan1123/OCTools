"""
octool/core/engines/tts_engine.py
───────────────────────────────────────────────
文本 → 语音（TTS）引擎：txt / md → 音频 —— 核心引擎层

支持三种引擎（通过预设选择，默认 Kokoro）：
  - kokoro : Kokoro KPipeline（离线）
             · 保留 mvp/md_to_mp3_kokoro.py 的自定义分词：clean_markdown + split_sentences
               （逐句合成，避免 Kokoro 内部乱切导致句子截断）
             · 中文音色列表来自 assets/voices_model（zf_* 女声 / zm_* 男声）
  - edge   : Edge-TTS（在线，voice / rate / volume / pitch）
  - moss   : MOSS-TTS ONNX 运行时（离线，需 GPU 更佳）
             · 可选模型目录来自 assets/voices_model 下的子目录（默认见 paths.models.moss）
             · 支持「模仿音频」：prompt_audio_path 参考音频做声音克隆

所有引擎统一输出中间 WAV，再按目标格式转码（复用 core/engines/audio_engine._audio_encode）。

模型目录与 eSpeak 数据目录来自 config/ui_config.json：
  paths.models.moss / paths.models.kokoro / paths.espeak_data
换机/换盘只改 JSON，无需动代码。
"""

import os
import re
import glob
import shutil
import tempfile
import asyncio

from config.tts_config import ENGINE_LABELS, ENGINE_ORDER, TtsConfig, default_config
from config.ui_config import CONFIG as _C
from core.utils.file_handler import file_exists, read_text

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ════════════════════════════════════════════
#  资源目录 / 常量
# ════════════════════════════════════════════

# 语音与模型资源目录（kokoro 中文音色 wav、moss 可选模型子目录）
VOICES_MODEL_DIR = os.path.normpath(os.path.join(_ROOT, "assets", "voices_model"))
# MOSS 默认模型目录
MOSS_DEFAULT_MODEL_DIR = _C.model_path("moss")
# MOSS 运行时源码目录（外部依赖 external/moss_tts）
MOSS_RUNTIME_DIR = os.path.join(_ROOT, "external", "moss_tts")

KOKORO_HF_HOME = _C.model_path("kokoro")
KOKORO_ESPEAK_DATA = _C.espeak_data()
KOKORO_REPO_ID = "hexgrad/Kokoro-82M"
KOKORO_SAMPLE_RATE = 24000

# 引擎标签 / 顺序（ENGINE_LABELS / ENGINE_ORDER）见 config/tts_config.py。

# 中文常用 Edge 音色
EDGE_ZH_VOICES = [
    "zh-CN-XiaoxiaoNeural", "zh-CN-XiaoyiNeural", "zh-CN-YunjianNeural",
    "zh-CN-YunxiNeural", "zh-CN-YunxiaNeural", "zh-CN-YunyangNeural",
    "zh-CN-XiaomoNeural", "zh-CN-XiaoruiNeural", "zh-CN-XiaoshuangNeural",
    "zh-CN-liaoning-XiaobeiNeural", "zh-CN-shaanxi-XiaoniNeural",
    "zh-TW-HsiaoChenNeural", "zh-TW-YunJheNeural",
    "zh-HK-HiuGaaiNeural", "zh-HK-HiuMaanNeural", "zh-HK-WanLungNeural",
]

# Kokoro 语言代码
KOKORO_LANGS = [
    ("z", "中文"), ("a", "美式英语"), ("b", "英式英语"), ("e", "西班牙语"),
    ("f", "法语"), ("h", "印地语"), ("i", "意大利语"), ("j", "日语"),
    ("p", "巴西葡语"),
]

_KOKORO_FALLBACK_VOICES = ["zf_xiaoxiao", "zf_xiaobei", "zf_xiaoni", "zf_xiaoyi",
                           "zm_yunjian", "zm_yunxi", "zm_yunxia", "zm_yunyang"]


# ════════════════════════════════════════════
#  资源扫描
# ════════════════════════════════════════════

def list_kokoro_voices() -> list:
    """扫描 assets/voices_model 下的中文音色（.wav 文件名即 kokoro voice 名）"""
    voices = []
    if os.path.isdir(VOICES_MODEL_DIR):
        for f in sorted(glob.glob(os.path.join(VOICES_MODEL_DIR, "*.wav"))):
            voices.append(os.path.splitext(os.path.basename(f))[0])
    return voices or list(_KOKORO_FALLBACK_VOICES)


def list_moss_models() -> list:
    """MOSS 可选模型目录：assets/voices_model 下的子目录（用户可自行放入模型文件夹）"""
    models = []
    if os.path.isdir(VOICES_MODEL_DIR):
        for name in sorted(os.listdir(VOICES_MODEL_DIR)):
            p = os.path.join(VOICES_MODEL_DIR, name)
            if os.path.isdir(p):
                models.append(p)
    # 始终附带默认模型目录（mvp 实际使用）
    if MOSS_DEFAULT_MODEL_DIR not in models and os.path.isdir(MOSS_DEFAULT_MODEL_DIR):
        models.append(MOSS_DEFAULT_MODEL_DIR)
    return models


# ════════════════════════════════════════════
#  配置
# ════════════════════════════════════════════
# 配置模型与常量（ENGINE_LABELS / ENGINE_ORDER / TtsConfig / default_config）
# 见 config/tts_config.py，本模块不再重复定义。


# ════════════════════════════════════════════
#  文本处理（保留 mvp kokoro 的自定义分词）
# ════════════════════════════════════════════

def clean_markdown(text: str) -> str:
    """移除 Markdown 格式标记，保留纯文本（来自 mvp/md_to_mp3_kokoro.py）"""
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)   # 标题
    text = re.sub(r'\*\*|\*|_+', '', text)                   # 粗体/斜体
    text = re.sub(r'`[^`]*`', '', text)                      # 行内代码
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)     # 链接文字
    text = re.sub(r'!\[([^\]]*)\]\([^)]*\)', r'\1', text)    # 图片
    text = re.sub(r'<[^>]+>', '', text)                      # HTML 标签
    text = re.sub(r'\n{3,}', '\n\n', text)                   # 压缩空行
    return text.strip()


def split_sentences(text: str) -> list:
    """
    按中文/英文句末标点切分句子（来自 mvp/md_to_mp3_kokoro.py），
    避免 Kokoro 内部乱切导致句子不完整。
    """
    text = text.strip()
    pattern = r'(?<=[。！？!?；;])\s*'
    parts = re.split(pattern, text)
    return [p.strip() for p in parts if p.strip()]


def _chunk_text(text: str, max_len: int = 3000) -> list:
    """按段落/句子把长文本切成不超过 max_len 的片段（Edge 单请求限制）"""
    segments, current = [], ""
    paragraphs = [p.strip() for p in re.split(r"\n+", text) if p.strip()]
    for para in paragraphs:
        if len(para) > max_len:
            for s in split_sentences(para) or [para]:
                if len(current) + len(s) + 1 <= max_len:
                    current += s
                else:
                    if current:
                        segments.append(current)
                    current = s
        elif len(current) + len(para) + 1 <= max_len:
            current = f"{current}\n{para}" if current else para
        else:
            if current:
                segments.append(current)
            current = para
    if current:
        segments.append(current)
    return segments or [text]


# ════════════════════════════════════════════
#  引擎单例
# ════════════════════════════════════════════

_KOKORO_PIPES = {}
_MOSS_RT = None
_MOSS_RT_MODEL = None


def _ensure_kokoro(lang_code: str):
    """创建/复用 Kokoro KPipeline（按语言缓存）"""
    lang = lang_code or "z"
    if lang not in _KOKORO_PIPES:
        os.environ.setdefault("HF_HOME", KOKORO_HF_HOME)
        os.environ.setdefault("ESPEAK_DATA_PATH", KOKORO_ESPEAK_DATA)
        try:
            from kokoro import KPipeline
        except ImportError:
            raise RuntimeError("Kokoro 未安装，请执行: pip install kokoro misaki[zh]")
        _KOKORO_PIPES[lang] = KPipeline(lang_code=lang, repo_id=KOKORO_REPO_ID)
    return _KOKORO_PIPES[lang]


def _ensure_moss(model_dir: str):
    """创建/复用 MOSS ONNX 运行时"""
    global _MOSS_RT, _MOSS_RT_MODEL
    import sys
    resolved = model_dir or MOSS_DEFAULT_MODEL_DIR
    if _MOSS_RT is not None and _MOSS_RT_MODEL == resolved:
        return _MOSS_RT
    if MOSS_RUNTIME_DIR not in sys.path:
        sys.path.insert(0, MOSS_RUNTIME_DIR)
    try:
        from onnx_tts_runtime import OnnxTtsRuntime
    except ImportError as e:
        raise RuntimeError(f"MOSS 运行时不可用（需 torch/torchaudio/onnxruntime）: {e}")
    _MOSS_RT = OnnxTtsRuntime(model_dir=resolved)
    _MOSS_RT_MODEL = resolved
    return _MOSS_RT


# ════════════════════════════════════════════
#  各引擎合成
# ════════════════════════════════════════════

def _synth_kokoro(text, wav_path, cfg, log):
    """Kokoro 逐句合成（保留 mvp 自定义分句）"""
    import numpy as np
    import soundfile as sf
    pipe = _ensure_kokoro(cfg.kokoro_lang)
    voice = cfg.kokoro_voice or None
    speed = float(cfg.kokoro_speed or 1.0)
    chunks = []
    if cfg.kokoro_split_pattern:
        # 用户自定义 split_pattern：整段交给 Kokoro
        for _, _, audio in pipe(text, voice=voice, speed=speed,
                                split_pattern=cfg.kokoro_split_pattern):
            chunks.append(audio)
    else:
        # 默认：mvp 自定义分句，逐句合成
        sentences = split_sentences(text) or [text]
        for i, sentence in enumerate(sentences):
            log(f"   🔉 Kokoro 第 {i + 1}/{len(sentences)} 句: {sentence[:30]}")
            for _, _, audio in pipe(sentence, voice=voice, speed=speed):
                chunks.append(audio)
    if not chunks:
        raise RuntimeError("Kokoro 未生成任何音频")
    full = np.concatenate(chunks)
    sf.write(wav_path, full, KOKORO_SAMPLE_RATE)
    return True


def _synth_edge(text, wav_path, cfg, log):
    """Edge-TTS（在线）：分段合成 mp3 → 合并 → wav"""
    import edge_tts
    tmpdir = tempfile.mkdtemp(prefix="edge_tts_")
    mp3_files = []
    try:
        segments = _chunk_text(text)
        async def _run():
            for i, seg in enumerate(segments):
                log(f"   🔉 Edge 第 {i + 1}/{len(segments)} 段（{len(seg)} 字）")
                out = os.path.join(tmpdir, f"seg_{i:03d}.mp3")
                comm = edge_tts.Communicate(
                    seg, voice=cfg.edge_voice,
                    rate=cfg.edge_rate, volume=cfg.edge_volume, pitch=cfg.edge_pitch)
                with open(out, "wb") as f:
                    async for chunk in comm.stream():
                        if chunk["type"] == "audio":
                            f.write(chunk["data"])
                if os.path.getsize(out) > 0:
                    mp3_files.append(out)
        asyncio.run(_run())
        if not mp3_files:
            raise RuntimeError("Edge-TTS 未生成任何音频（请检查网络）")
        from pydub import AudioSegment
        merged = AudioSegment.empty()
        for m in mp3_files:
            merged += AudioSegment.from_mp3(m)
        merged.export(wav_path, format="wav")
        return True
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def _synth_moss(text, wav_path, cfg, log):
    """MOSS-TTS ONNX：支持模仿音频（prompt_audio_path 声音克隆）"""
    rt = _ensure_moss(cfg.moss_model_dir)
    if cfg.moss_reference and os.path.exists(cfg.moss_reference):
        log(f"   🎭 使用模仿音频: {os.path.basename(cfg.moss_reference)}")
    result = rt.synthesize(
        text=text,
        voice=cfg.moss_voice or None,
        prompt_audio_path=cfg.moss_reference or None,
        output_audio_path=wav_path,
        enable_wetext=False,
        enable_normalize_tts_text=False,
        voice_clone_max_text_tokens=int(cfg.moss_voice_clone_max_text_tokens or 75),
        max_new_frames=cfg.moss_max_new_frames or None,
        do_sample=bool(cfg.moss_do_sample),
        seed=cfg.moss_seed if cfg.moss_seed is not None and cfg.moss_seed >= 0 else None,
    )
    return bool(result.get("audio_path")) and os.path.exists(wav_path)


# ════════════════════════════════════════════
#  统一入口
# ════════════════════════════════════════════

def synthesize_text_to_audio(text, output_path, log=lambda m: print(m), config=None):
    """把文本合成为音频文件（目标格式由 output_path 扩展名决定）"""
    cfg = config or default_config()
    text = str(text or "").strip()
    if not text:
        log("❌ 文本为空，无法合成")
        return False
    errors = cfg.validate()
    if errors:
        for e in errors:
            log(f"❌ {e}")
        return False

    os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
    tmpdir = tempfile.mkdtemp(prefix="tts_")
    try:
        tmp_wav = os.path.join(tmpdir, "out.wav")
        engine = cfg.engine
        log(f"🔊 语音引擎: {ENGINE_LABELS.get(engine, engine)}")
        if engine == "edge":
            ok = _synth_edge(text, tmp_wav, cfg, log)
        elif engine == "moss":
            ok = _synth_moss(text, tmp_wav, cfg, log)
        else:
            ok = _synth_kokoro(text, tmp_wav, cfg, log)
        if not ok or not os.path.exists(tmp_wav) or os.path.getsize(tmp_wav) == 0:
            log("❌ 语音合成失败")
            return False

        # 时长
        duration = 0.0
        try:
            import soundfile as sf
            duration = len(sf.read(tmp_wav)[0]) / KOKORO_SAMPLE_RATE
        except Exception:
            pass

        dst = os.path.splitext(output_path)[1].lower().lstrip(".")
        if dst in ("", "wav"):
            shutil.move(tmp_wav, output_path)
            log(f"✅ 完成 → {output_path}（{duration:.1f}s）")
            return True
        # 其他音频格式：wav → 目标格式
        from core.engines.audio_engine import _audio_encode
        if _audio_encode(tmp_wav, output_path, log, src_is_video=False):
            log(f"✅ 完成 → {output_path}（{duration:.1f}s）")
            return True
        return False
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def text_to_audio(input_path, output_path, log=lambda m: print(m), config=None):
    """txt / md → 音频（md 先清理 Markdown 标记）"""
    if not file_exists(input_path, log):
        return False
    try:
        ext = os.path.splitext(input_path)[1].lower()
        raw = read_text(input_path)
        text = clean_markdown(raw) if ext == ".md" else raw
        if not text.strip():
            log("❌ 文件内容为空")
            return False
        log(f"🔄 {ext[1:].upper()} → 音频: {os.path.basename(input_path)}")
        return synthesize_text_to_audio(text, output_path, log, config)
    except Exception as e:
        log(f"❌ {e}")
        return False


# ════════════════════════════════════════════
#  自测
# ════════════════════════════════════════════

if __name__ == "__main__":
    log = lambda m: print(m)
    tmp = tempfile.mkdtemp(prefix="tts_self_")
    print("kokoro 音色:", list_kokoro_voices())
    print("moss 模型:", list_moss_models())
    print("→ 测试 Kokoro 合成（默认引擎）")
    text_to_audio(os.path.join(_ROOT, "mvp", "test.png") if False else
                  __file__, os.path.join(tmp, "self.mp3"), log=log,
                  config=TtsConfig())
    print("产物目录:", tmp)
