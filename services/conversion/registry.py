"""
OCTools/services/conversion/registry.py
───────────────────────────────────────────────
转换注册表（业务逻辑层）：把「(源格式 → 目标格式) 的直达转换函数 + 需要的配置类型」
声明成一条条 ConversionSpec。

单一真相：
  - 直达边集合来自 services.conversion.direct_table.CONVERSION_TABLE
  - 每条边标注 config_type，统一入口（pipeline）按 spec 自动装配配置

"""

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class ConversionSpec:
    """一条直达转换的完整声明"""
    func: Callable                        # (input, output, log, ...) -> bool
    config_type: Optional[type] = None    # FormatConfig / ImageDocxConfig / TtsConfig / SttConfig
    config_kwarg: str = "config"          # 传给 func 的关键字（image_config 等）
    output_is_folder: bool = False        # 输出是一整个文件夹（如 文档→按页图片）
    transitive: bool = True               # 是否可作为星型寻路的中转边（音频→txt 语音识别除外）


def _norm(fmt: str) -> str:
    return str(fmt or "").strip().lower().lstrip(".")


class Registry:
    """(src, dst) → ConversionSpec 的有序查找表"""

    def __init__(self):
        self._specs: Dict[Tuple[str, str], ConversionSpec] = {}

    def add(self, src: str, dst: str, spec: ConversionSpec):
        self._specs[(_norm(src), _norm(dst))] = spec

    def get(self, src: str, dst: str) -> Optional[ConversionSpec]:
        return self._specs.get((_norm(src), _norm(dst)))

    def has(self, src: str, dst: str) -> bool:
        return (_norm(src), _norm(dst)) in self._specs

    def edges(self) -> List[Tuple[str, str]]:
        """全部直达边（去点号的小写格式名）"""
        return [(s, d) for (s, d) in sorted(self._specs.keys())]

    def funcs(self) -> Dict[Tuple[str, str], Callable]:
        return {k: v.func for k, v in self._specs.items()}

    def __len__(self):
        return len(self._specs)

    def __contains__(self, key):
        if isinstance(key, tuple) and len(key) == 2:
            return self.has(key[0], key[1])
        return False


# ════════════════════════════════════════════
#  配置类型推导（原 convert() 里的三个硬编码特判）
# ════════════════════════════════════════════

def config_for(src: str, dst: str) -> Tuple[Optional[type], str]:
    """按 (源, 目标) 决定转换函数需要的配置类型与关键字

    - MD → DOCX            → FormatConfig（高级排版）
    - 图片 → DOCX          → ImageDocxConfig（网格排版）
    - PDF → DOCX           → PdfDocxConfig（LibreOffice / 文本提取）
    - TXT/MD → 音频        → TtsConfig（语音引擎）
    - 音频 → TXT           → SttConfig（语音识别引擎）
    其余为 None（无配置）。
    """
    from config.format_config import FormatConfig
    from config.image_docx_config import ImageDocxConfig
    from config.pdf_docx_config import PdfDocxConfig
    from config.tts_config import TtsConfig
    from config.stt_config import SttConfig
    from services.conversion.direct_table import _IMAGE_TO_DOCX_EXTS, AUDIO_TARGET_EXTS

    src, dst = _norm(src), _norm(dst)
    if src == "md" and dst == "docx":
        return FormatConfig, "config"
    if dst == "docx" and f".{src}" in _IMAGE_TO_DOCX_EXTS:
        return ImageDocxConfig, "image_config"
    if src == "pdf" and dst == "docx":
        return PdfDocxConfig, "config"
    if src in ("txt", "md") and f".{dst}" in AUDIO_TARGET_EXTS:
        return TtsConfig, "config"
    if dst == "txt" and f".{src}" in AUDIO_TARGET_EXTS:
        return SttConfig, "config"
    return None, "config"


# 输出是「文件夹」的直达边（文档 → 按页图片），不能作为星型中转跳
_FOLDER_OUTPUT_PAIRS = frozenset({
    (".md", ".png"), (".md", ".jpg"), (".md", ".jpeg"),
    (".docx", ".png"), (".docx", ".jpg"), (".docx", ".jpeg"),
    (".pdf", ".png"), (".pdf", ".jpg"), (".pdf", ".jpeg"),
})

# 音频 → txt（语音识别）：只作为直达转换目标，
# 不作为星型中转跳（否则会导出 mp3 → txt → docx 等跨类路径）
def _is_stt_edge(src: str, dst: str) -> bool:
    from services.conversion.direct_table import AUDIO_TARGET_EXTS
    return dst == ".txt" and src in AUDIO_TARGET_EXTS


def build_registry(table: Dict[Tuple[str, str], Callable]) -> Registry:
    """从直达转换表构建注册表（逐条标注配置类型）"""
    reg = Registry()
    for (src, dst), func in table.items():
        cfg_type, kwarg = config_for(src, dst)
        reg.add(src, dst, ConversionSpec(
            func=func,
            config_type=cfg_type,
            config_kwarg=kwarg,
            output_is_folder=(src, dst) in _FOLDER_OUTPUT_PAIRS,
            transitive=not _is_stt_edge(src, dst)))
    return reg


# ── 默认单例：基于 direct_table.CONVERSION_TABLE ──
def _default_registry() -> Registry:
    from services.conversion.direct_table import CONVERSION_TABLE
    return build_registry(CONVERSION_TABLE)


REGISTRY: Registry = _default_registry()
