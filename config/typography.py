"""
OCTools/config/typography.py
───────────────────────────────────────────────
字体与排版配置（最小功能单元）：Typography

包含：正文字体、标题样式、行距、段间距、首行缩进、对齐方式。
"""

from dataclasses import dataclass, field
from typing import Dict, List

from config.enums import Alignment, LineSpacingMode
from config.heading import HeadingStyle


@dataclass
class Typography:
    """字体与排版配置"""
    # 正文字体
    body_font_cn: str = "宋体"
    body_font_en: str = "Times New Roman"
    body_font_size: float = 12.0   # pt（小四）
    body_color: str = "#000000"

    # 标题样式（按级别）
    headings: Dict[str, HeadingStyle] = field(default_factory=lambda: {
        "h1": HeadingStyle(font_cn="黑体", font_en="Arial", font_size=22.0, bold=True, color="#000000"),
        "h2": HeadingStyle(font_cn="黑体", font_en="Arial", font_size=18.0, bold=True, color="#000000"),
        "h3": HeadingStyle(font_cn="黑体", font_en="Arial", font_size=14.0, bold=True, color="#000000"),
    })

    # 行距
    line_spacing_mode: LineSpacingMode = LineSpacingMode.MULTIPLE
    line_spacing: float = 1.5       # 倍数模式下为倍数，固定模式下为磅值
    line_spacing_fixed: float = 20.0  # 固定值模式下的磅值

    # 段间距
    para_space_before: float = 0.0  # pt
    para_space_after: float = 0.0   # pt

    # 首行缩进
    first_line_indent_chars: float = 0.0  # 字符数（中文标准为2）

    # 对齐方式
    alignment: Alignment = Alignment.LEFT

    def validate(self) -> List[str]:
        errors = []
        if self.body_font_size < 6 or self.body_font_size > 72:
            errors.append(f"正文字号不合理（当前: {self.body_font_size}pt）")
        if self.line_spacing_mode == LineSpacingMode.MULTIPLE and self.line_spacing <= 0:
            errors.append("行距倍数必须 > 0")
        if self.line_spacing_mode == LineSpacingMode.FIXED and self.line_spacing_fixed <= 0:
            errors.append("固定行距必须 > 0")
        if self.first_line_indent_chars < 0:
            errors.append("首行缩进不能为负数")
        for level, hs in self.headings.items():
            if hs.font_size < 8 or hs.font_size > 72:
                errors.append(f"{level} 字号不合理（当前: {hs.font_size}pt）")
        return errors
