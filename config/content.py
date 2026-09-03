"""
OCTools/config/content.py
───────────────────────────────────────────────
内容样式映射配置（最小功能单元）：ContentStyles

包含：列表、引用块、代码块、表格、图片、超链接的样式。
"""

from dataclasses import dataclass
from typing import List


@dataclass
class ContentStyles:
    """内容样式映射配置"""
    # 列表
    list_bullet_char: str = "●"
    list_indent: float = 0.63       # cm

    # 引用块
    blockquote_bar_color: str = "#CCCCCC"
    blockquote_bg_color: str = "#F5F5F5"
    blockquote_left_indent: float = 1.27  # cm

    # 代码块
    code_font: str = "Consolas"
    code_font_size: float = 9.0     # pt
    code_bg_color: str = "#F4F4F4"
    code_border: bool = True

    # 表格
    table_header_bg: str = "#D9E2F3"
    table_border: bool = True
    table_border_color: str = "#000000"

    # 图片
    image_max_width_pct: float = 80.0  # 占页面宽度的百分比
    image_center: bool = True

    # 超链接
    link_color: str = "#0563C1"
    link_underline: bool = True

    def validate(self) -> List[str]:
        errors = []
        if self.image_max_width_pct <= 0 or self.image_max_width_pct > 100:
            errors.append(f"图片最大宽度应在 1-100% 之间（当前: {self.image_max_width_pct}%）")
        return errors
