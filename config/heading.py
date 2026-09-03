"""
OCTools/config/heading.py
───────────────────────────────────────────────
标题样式（最小功能单元）：HeadingStyle

单个标题级别（h1/h2/h3...）的字体、字号、加粗、颜色、对齐方式。
"""

from dataclasses import dataclass

from config.enums import Alignment


@dataclass
class HeadingStyle:
    """单个标题级别的样式"""
    font_cn: str = "黑体"
    font_en: str = "Arial"
    font_size: float = 16.0        # pt
    bold: bool = True
    color: str = "#000000"
    alignment: Alignment = Alignment.LEFT
