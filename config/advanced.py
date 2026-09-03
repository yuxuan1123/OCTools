"""
OCTools/config/advanced.py
───────────────────────────────────────────────
高级排版特性配置（最小功能单元）：AdvancedFeatures

包含：标题编号、目录、页眉页脚、封面、水印。
"""

from dataclasses import dataclass
from typing import List


@dataclass
class AdvancedFeatures:
    """高级排版特性配置"""
    heading_numbering: bool = False
    heading_numbering_format: str = "1."   # 如 "1.", "1)", "第1章"

    auto_toc: bool = False
    toc_depth: int = 3                      # 目录深度（H1-H3）

    header_text: str = ""
    footer_text: str = ""

    cover_enabled: bool = False
    cover_title: str = ""
    cover_author: str = ""
    cover_date: str = ""                    # 空字符串表示自动使用当前日期

    watermark_text: str = ""
    watermark_font_size: float = 72.0       # pt
    watermark_opacity: float = 0.1          # 0-1

    def validate(self) -> List[str]:
        errors = []
        if self.toc_depth < 1 or self.toc_depth > 9:
            errors.append(f"目录深度应在 1-9 之间（当前: {self.toc_depth}）")
        if self.watermark_opacity < 0 or self.watermark_opacity > 1:
            errors.append(f"水印透明度应在 0-1 之间（当前: {self.watermark_opacity}）")
        if self.watermark_font_size < 8 or self.watermark_font_size > 200:
            errors.append(f"水印字号不合理（当前: {self.watermark_font_size}pt）")
        return errors
