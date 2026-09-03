"""
OCTools/core/engines/translation_engine.py
───────────────────────────────────────────────
中英互译引擎（完全离线）—— 核心引擎层，支持两种模型后端，可配置并持久化：

  1. hy     : Hy-MT2-1.8B（默认，llama_cpp 本地大模型，参考 mvp/hy.py）
              中英双向，提示词式翻译，质量更好
  2. opusmt : Opus-MT（CTranslate2 + SentencePiece，参考 mvp/l2l.py）
              英→中 opus-mt-en-zh-ct2（需加语言标记 >>cmn_Hans<<）
              中→英 opus-mt-zh-en-ct2

设计要点：
  - TranslatorConfig 数据模型（引擎选择 + 各引擎参数），可保存 / 加载
  - 模型按需懒加载（首次翻译时才加载，避免程序启动卡顿），并做进程内缓存
  - translate() 支持 中→英 / 英→中 / 自动检测 三种方向
  - 长文本按段落切分翻译；输入自动清洗（OCR 噪声防护）

旧路径 src/translator.py 保留为兼容 shim（re-export 本模块）。
"""

import os
import re

from core.utils.file_handler import file_exists, read_text, write_text
from config.translator_config import (
    ENGINE_LABELS, OPUS_MT_BASE, TranslatorConfig, default_config,
)

# ════════════════════════════════════════════
#  模型路径
# ════════════════════════════════════════════
# 模型根目录与引擎参数常量（OPUS_MT_BASE / HY_DEFAULT_MODEL_PATH /
# ENGINE_LABELS / ENGINE_ORDER）定义见 config/translator_config.py。

# 英 → 中：CT2 模型 + 原始目录的 SentencePiece 分词器
EN2ZH_CT2_DIR = os.path.join(OPUS_MT_BASE, "opus-mt-en-zh-ct2")
EN2ZH_SRC_SPM = os.path.join(OPUS_MT_BASE, "raw_en-zh", "source.spm")
EN2ZH_TGT_SPM = os.path.join(OPUS_MT_BASE, "raw_en-zh", "target.spm")

# 中 → 英
ZH2EN_CT2_DIR = os.path.join(OPUS_MT_BASE, "opus-mt-zh-en-ct2")
ZH2EN_SRC_SPM = os.path.join(OPUS_MT_BASE, "raw_zh-en", "source.spm")
ZH2EN_TGT_SPM = os.path.join(OPUS_MT_BASE, "raw_zh-en", "target.spm")

# 翻译方向（UI 下拉 / 命令行共用）
DIRECTION_LABELS = {
    "zh2en": "中 → 英",
    "en2zh": "英 → 中",
    "auto": "自动检测",
}
DIRECTION_ORDER = ["zh2en", "en2zh", "auto"]


# ════════════════════════════════════════════
#  语言检测（自动方向用）
# ════════════════════════════════════════════

def detect_language(text: str) -> str:
    """粗略判断原文语言：含较多 CJK 字符视为中文，否则视为英文"""
    text = text or ""
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    return "zh" if cjk >= 2 else "en"


# ════════════════════════════════════════════
#  文本清洗（OCR / 屏幕翻译噪声防护）
# ════════════════════════════════════════════

# 乱码 / 不可显示字符（⁇ 双问号、� 替换符、□ 缺字）
_NOISE_CHARS = frozenset("\u2047\ufffd\u25a1\uFFFD")


def clean_text(text: str) -> str:
    """清洗 OCR / 输入文本：
    去控制字符、折叠空白、丢弃噪声行（纯符号 / 反斜杠代码痕迹 / 乱码字符），
    保留空行作为段落分隔。返回清洗后的纯文本（空串 = 无可翻译内容）。
    """
    lines = []
    for raw in (text or "").splitlines():
        line = raw.replace("\u00a0", " ").replace("\u3000", " ")
        line = "".join(ch for ch in line if ch >= " " and ch != "\x7f")
        line = re.sub(r"[ \t]+", " ", line).strip()
        if not line:
            if lines and lines[-1] != "":
                lines.append("")   # 保留一个空行作段落分隔
            continue
        if any(ch in _NOISE_CHARS for ch in line):
            continue
        # 反斜杠占比过高 = 代码 / 转义噪声
        if line.count("\\") / max(len(line), 1) > 0.2:
            continue
        alnum = sum(1 for ch in line if ch.isalnum())
        # 无字母数字，或符号占比过高（纯符号 / 乱码）
        if alnum == 0 or alnum / max(len(line), 1) < 0.35:
            continue
        lines.append(line)
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def _strip_tag_leak(text: str) -> str:
    """剥离模型偶尔回显的语言标记（cmn_Hans / >>cmn_Hans<< / * cmn_Hans …）"""
    text = re.sub(r"^\s*[*>\s\u00bb]*cmn\s*[-_ ]?\s*Hans\s*[<*\s\u00ab]*",
                  "", text, flags=re.I)
    return text.strip(" *>\t\u00bb\u00ab")


def _is_garbage_output(text: str) -> bool:
    """输出是否几乎全是乱码（⁇ � □）或空白"""
    text = text or ""
    if not text.strip():
        return True
    junk = sum(1 for ch in text if ch in _NOISE_CHARS)
    if junk / max(len(text), 1) > 0.2:
        return True
    meaningful = sum(1 for ch in text if ch.isalnum())
    return meaningful == 0


# ════════════════════════════════════════════
#  引擎懒加载单例
# ════════════════════════════════════════════

_EN2ZH = {"translator": None, "sp_src": None, "sp_tgt": None}
_ZH2EN = {"translator": None, "sp_src": None, "sp_tgt": None}


def _check_models_ready():
    """预检模型/分词器文件是否存在，给出明确报错"""
    missing = [p for p in (
        EN2ZH_CT2_DIR, EN2ZH_SRC_SPM, EN2ZH_TGT_SPM,
        ZH2EN_CT2_DIR, ZH2EN_SRC_SPM, ZH2EN_TGT_SPM,
    ) if not os.path.exists(p)]
    if missing:
        raise RuntimeError(
            "❌ 翻译模型缺失，请先准备好 Opus-MT 模型目录（与 mvp/l2l.py 相同）：\n  "
            + "\n  ".join(missing)
            + f"\n模型根目录: {OPUS_MT_BASE}")


def _ensure_deps():
    try:
        import ctranslate2  # noqa: F401
        import sentencepiece as spm  # noqa: F401
        return spm
    except ImportError as e:
        raise RuntimeError(
            "ctranslate2 / sentencepiece 未安装，请执行:\n"
            "  pip install ctranslate2 sentencepiece") from e


def _ensure_en2zh():
    """加载 英→中 引擎（懒加载 + 缓存）"""
    if _EN2ZH["translator"] is not None:
        return _EN2ZH
    _check_models_ready()
    spm = _ensure_deps()
    import ctranslate2
    _EN2ZH["translator"] = ctranslate2.Translator(
        EN2ZH_CT2_DIR, device="cpu", compute_type="int8")
    _EN2ZH["sp_src"] = spm.SentencePieceProcessor(model_file=EN2ZH_SRC_SPM)
    _EN2ZH["sp_tgt"] = spm.SentencePieceProcessor(model_file=EN2ZH_TGT_SPM)
    return _EN2ZH


def _ensure_zh2en():
    """加载 中→英 引擎（懒加载 + 缓存）"""
    if _ZH2EN["translator"] is not None:
        return _ZH2EN
    _check_models_ready()
    spm = _ensure_deps()
    import ctranslate2
    _ZH2EN["translator"] = ctranslate2.Translator(
        ZH2EN_CT2_DIR, device="cpu", compute_type="int8")
    _ZH2EN["sp_src"] = spm.SentencePieceProcessor(model_file=ZH2EN_SRC_SPM)
    _ZH2EN["sp_tgt"] = spm.SentencePieceProcessor(model_file=ZH2EN_TGT_SPM)
    return _ZH2EN


# ════════════════════════════════════════════
#  配置
# ════════════════════════════════════════════
# TranslatorConfig / default_config 定义见 config/translator_config.py。


# ════════════════════════════════════════════
#  Hy-MT2 引擎（llama_cpp）懒加载单例
# ════════════════════════════════════════════

_HY_LLM = None
_HY_LLM_KEY = None


def _ensure_hy(cfg: TranslatorConfig):
    """创建/复用 Hy-MT2 模型（按 模型路径+上下文参数 缓存）"""
    global _HY_LLM, _HY_LLM_KEY
    key = (cfg.hy_model_path, int(cfg.hy_n_ctx),
           int(cfg.hy_n_threads), int(cfg.hy_n_gpu_layers))
    if _HY_LLM is not None and _HY_LLM_KEY == key:
        return _HY_LLM
    if not os.path.exists(cfg.hy_model_path):
        raise RuntimeError(f"Hy-MT 模型文件不存在: {cfg.hy_model_path}")
    try:
        from llama_cpp import Llama
    except ImportError as e:
        raise RuntimeError(
            "llama-cpp-python 未安装，请执行: pip install llama-cpp-python") from e
    _HY_LLM = Llama(
        model_path=cfg.hy_model_path,
        n_ctx=int(cfg.hy_n_ctx),
        n_threads=int(cfg.hy_n_threads),
        n_gpu_layers=int(cfg.hy_n_gpu_layers),
        verbose=False,
    )
    _HY_LLM_KEY = key
    return _HY_LLM


def _translate_hy_once(text: str, target_lang: str, cfg: TranslatorConfig) -> str:
    """Hy-MT2 提示词式翻译（参考 mvp/hy.py）"""
    llm = _ensure_hy(cfg)
    prompt = (f"将以下文本翻译为{target_lang},注意只需要输出翻译后的结果,"
              f"不要额外解释:\n\n{text}")
    out = llm(
        prompt,
        max_tokens=int(cfg.hy_max_tokens),
        temperature=float(cfg.hy_temperature),
        top_p=float(cfg.hy_top_p),
        top_k=int(cfg.hy_top_k),
        repeat_penalty=float(cfg.hy_repeat_penalty),
        stop=["\n\n"],
        echo=False,
    )
    return out["choices"][0]["text"].strip()


def models_ready(config=None) -> bool:
    """当前所选翻译引擎是否已就绪（用于 UI 提示，不做加载）"""
    cfg = config or default_config()
    try:
        if cfg.engine == "hy":
            return os.path.exists(cfg.hy_model_path)
        _check_models_ready()
        return True
    except Exception:
        return False


def warmup(direction: str = "auto", config=None) -> bool:
    """后台预热：按所选引擎预加载翻译模型（屏幕实时翻译等场景减少首次等待）"""
    cfg = config or default_config()
    try:
        if cfg.engine == "hy":
            _ensure_hy(cfg)
            return True
        if direction in ("auto", "zh2en"):
            _ensure_zh2en()
        if direction in ("auto", "en2zh"):
            _ensure_en2zh()
        return True
    except Exception:
        return False


# ════════════════════════════════════════════
#  核心翻译
# ════════════════════════════════════════════

def _translate_once(text: str, direction: str) -> str:
    """翻译单段文本（不切分），方向已归一化到 zh2en / en2zh。
    返回译文；输出为乱码/空白时返回 ""。
    """
    if direction == "zh2en":
        eng = _ensure_zh2en()
        tokens = eng["sp_src"].encode(text, out_type=str) + [""]
        results = eng["translator"].translate_batch([tokens])
        out = eng["sp_tgt"].decode(results[0].hypotheses[0])
        return "" if _is_garbage_output(out) else out.strip()
    # en2zh：需要加语言标记 >>cmn_Hans<<（并防模型回显该标记）
    eng = _ensure_en2zh()
    tokens = eng["sp_src"].encode(f">>cmn_Hans<< {text}", out_type=str) + [""]
    results = eng["translator"].translate_batch([tokens])
    out = _strip_tag_leak(eng["sp_tgt"].decode(results[0].hypotheses[0]))
    return "" if _is_garbage_output(out) else out.strip()


def _split_paragraphs(text: str) -> list:
    """按空行切段（保留翻译可读性），单段过长时再按句切分"""
    paras = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    if not paras:
        paras = [text.strip()]
    out = []
    for p in paras:
        if len(p) > 800:
            # 超长段落：按句号切分为更小的子段
            sentences = [s.strip() for s in re.split(
                r"(?<=[。！？!?；;])\s*", p) if s.strip()]
            out.extend(sentences or [p])
        else:
            out.append(p)
    return out or [text.strip()]


def translate(text: str, direction: str = "auto", log=None, config=None) -> str:
    """中英互译统一入口（按 TranslatorConfig 自动选择引擎）。

    参数:
      text      : 原文
      direction : zh2en（中→英）/ en2zh（英→中）/ auto（自动检测）
      log       : 可选日志回调（线程安全由调用方保证）
      config    : TranslatorConfig；缺省用默认（hy 引擎）
    返回译文；输入为空返回 ""。
    """
    text = str(text or "").strip()
    if not text:
        return ""
    text = clean_text(text)
    if not text.strip():
        return ""
    cfg = config or default_config()
    direction = direction if direction in DIRECTION_LABELS else "auto"
    if direction == "auto":
        direction = "zh2en" if detect_language(text) == "zh" else "en2zh"

    hy_target = "中文" if direction == "en2zh" else "英文"
    eng_label = ENGINE_LABELS.get(cfg.engine, cfg.engine)
    paras = _split_paragraphs(text)
    parts = []
    for i, para in enumerate(paras):
        if log:
            log(f"   🌐 翻译第 {i + 1}/{len(paras)} 段（{len(para)} 字符，{eng_label}）…")
        try:
            if cfg.engine == "hy":
                out = _translate_hy_once(para, hy_target, cfg)
            else:
                out = _translate_once(para, direction)
        except Exception as e:
            if log:
                log(f"   ⚠ 第 {i + 1} 段翻译失败: {e}")
            continue
        out = _strip_tag_leak(out)
        if out and not _is_garbage_output(out):
            parts.append(out)
    return "\n\n".join(parts)


# ════════════════════════════════════════════
#  文件翻译（txt / md → txt，供 CLI / 转换链路使用）
# ════════════════════════════════════════════

def translate_file(input_path, output_path, log=lambda m: print(m),
                   direction: str = "auto", config=None) -> bool:
    """把文本文件（txt / md）翻译并写入 output_path（txt）。

    签名与转换引擎统一：(input_path, output_path, log) -> bool
    config: TranslatorConfig（缺省用默认 hy 引擎）
    """
    if not file_exists(input_path, log):
        return False
    try:
        raw = read_text(input_path)
        if not raw.strip():
            log("❌ 文件内容为空，无法翻译")
            return False
        log(f"🌐 开始翻译（{direction}，共 {len(raw)} 字符）…")
        out = translate(raw, direction, log, config=config)
        if not out.strip():
            log("❌ 翻译结果为空")
            return False
        os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
        write_text(output_path, out)
        log(f"✅ 完成 → {output_path}")
        return True
    except Exception as e:
        log(f"❌ {e}")
        return False


# ════════════════════════════════════════════
#  自测
# ════════════════════════════════════════════

if __name__ == "__main__":
    import time
    start = time.perf_counter()
    print(f"引擎: {ENGINE_LABELS[default_config().engine]}")
    print("英→中:", translate("Hello, how are you?", "en2zh"))
    print("中→英:", translate("人工智能正在改变世界。", "zh2en"))
    print("自动:", translate("Hello, how are you?"))
    print(f"\n⏱ 总耗时: {time.perf_counter() - start:.3f} 秒")
