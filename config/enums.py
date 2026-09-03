"""
OCTools/config/enums.py
───────────────────────────────────────────────
MD → DOCX 排版配置使用的全部枚举类型（最小功能单元）。

一个枚举 = 一个文件内定义：
  - PaperSize        纸张大小（A4/A3/A5/Letter/Legal）
  - Orientation      页面方向（纵向/横向）
  - LineSpacingMode  行距模式（倍数/固定值）
  - Alignment        对齐方式（左/中/右/两端）
"""

from enum import Enum


class PaperSize(str, Enum):
    A4 = "A4"
    A3 = "A3"
    A5 = "A5"
    LETTER = "Letter"
    LEGAL = "Legal"

    @classmethod
    def labels(cls):
        return {
            cls.A4: "A4 (210×297mm)",
            cls.A3: "A3 (297×420mm)",
            cls.A5: "A5 (148×210mm)",
            cls.LETTER: "Letter (216×279mm)",
            cls.LEGAL: "Legal (216×356mm)",
        }

    def dimensions_cm(self):
        """返回 (width_cm, height_cm)"""
        return {
            PaperSize.A4: (21.0, 29.7),
            PaperSize.A3: (29.7, 42.0),
            PaperSize.A5: (14.8, 21.0),
            PaperSize.LETTER: (21.59, 27.94),
            PaperSize.LEGAL: (21.59, 35.56),
        }[self]


class Orientation(str, Enum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


class LineSpacingMode(str, Enum):
    MULTIPLE = "multiple"
    FIXED = "fixed"


class Alignment(str, Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFY = "justify"
