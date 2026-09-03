"""
OCTools/config/page_layout.py
───────────────────────────────────────────────
页面布局配置（最小功能单元）：PageLayout

包含：纸张大小、页面方向、上下左右边距、装订线（单位：厘米）。
"""

from dataclasses import dataclass
from typing import List

from config.enums import PaperSize, Orientation


@dataclass
class PageLayout:
    """页面布局配置"""
    paper_size: PaperSize = PaperSize.A4
    orientation: Orientation = Orientation.PORTRAIT
    margin_top: float = 2.54       # 厘米
    margin_bottom: float = 2.54    # 厘米
    margin_left: float = 3.18      # 厘米（中文排版左边距较大）
    margin_right: float = 3.18     # 厘米
    gutter: float = 0.0            # 装订线（厘米）

    def validate(self) -> List[str]:
        errors = []
        for name in ("margin_top", "margin_bottom", "margin_left", "margin_right", "gutter"):
            v = getattr(self, name)
            if v < 0:
                errors.append(f"{name} 不能为负数（当前: {v}cm）")
            if v > 10:
                errors.append(f"{name} 数值过大（当前: {v}cm，建议 ≤10cm）")
        return errors
