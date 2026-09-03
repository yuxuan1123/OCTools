"""
octool/core/formats/model.py
───────────────────────────────────────────────
格式元数据模型（最小功能单元）：Format

一种格式 = 一条 Format 记录（id / 显示名 / 图标 / 文件过滤器 / 别名 / 家族 / 能力位）。
"""

from dataclasses import dataclass
from typing import FrozenSet, Tuple


@dataclass(frozen=True)
class Format:
    """一种格式的完整元数据"""
    id: str                                   # 格式标识，如 "png" / "txt-ocr"
    filter_desc: str                          # 文件对话框描述，如 "PNG 图片"
    patterns: Tuple[str, ...]                 # 文件通配符，如 ("*.png",)
    family: str                               # 家族：doc/table/presentation/video/audio/image
    icon: str = "📦"
    label: str = ""                           # 显示名；空 = 默认 id.upper()
    aliases: Tuple[str, ...] = ()             # 别名（归一化到本格式）
    capabilities: FrozenSet[str] = frozenset()

    @property
    def display(self) -> str:
        return self.label or self.id.upper()

    def filter(self) -> Tuple[str, str]:
        return (self.filter_desc, " ".join(self.patterns))


# ── 家族展示元信息（一级分类）──
FAMILY_META: Tuple[Tuple[str, str, str], ...] = (
    ("doc", "文档类", "📄"),
    ("table", "表格类", "📊"),
    ("presentation", "演示类", "📽️"),
    ("video", "视频类", "🎬"),
    ("audio", "音频类", "🎵"),
    ("image", "图像类", "🖼️"),
)
