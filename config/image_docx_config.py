"""
octool/config/image_docx_config.py
───────────────────────────────────────────────
图片 → DOCX 排版配置（最小功能单元）：ImageDocxConfig

把多张图片按网格排进 Word：
  - images_per_row    : 每行放几张图片（列数）
  - images_per_column : 每列放几张图片（每页行数）
  - image_width_cm    : 图片宽度（cm），0 表示自动（按比例适配单元格）
  - image_height_cm   : 图片高度（cm），0 表示自动
  - keep_aspect       : 是否保持宽高比（False 时按设定宽高拉伸）
  - show_filename     : 是否在图片下方显示文件名
  - cell_spacing_pt   : 单元格内图片与文件名的间距（pt）
  - table_border_color: 网格表格边框颜色（#RRGGBB）；""/"透明" 表示透明（无边框）
"""

import os
import json
from dataclasses import dataclass
from typing import List


@dataclass
class ImageDocxConfig:
    """图片 → DOCX 排版配置"""
    images_per_row: int = 2
    images_per_column: int = 2
    image_width_cm: float = 0.0
    image_height_cm: float = 0.0
    keep_aspect: bool = True
    show_filename: bool = True
    cell_spacing_pt: float = 4.0
    table_border_color: str = ""   # "" 或 "透明" = 无边框

    def validate(self) -> List[str]:
        errors = []
        if not (1 <= self.images_per_row <= 8):
            errors.append(f"每行图片数应在 1-8 之间（当前: {self.images_per_row}）")
        if not (1 <= self.images_per_column <= 8):
            errors.append(f"每列图片数应在 1-8 之间（当前: {self.images_per_column}）")
        if self.image_width_cm < 0 or self.image_width_cm > 40:
            errors.append(f"图片宽度应在 0-40cm 之间（当前: {self.image_width_cm}）")
        if self.image_height_cm < 0 or self.image_height_cm > 40:
            errors.append(f"图片高度应在 0-40cm 之间（当前: {self.image_height_cm}）")
        if self.cell_spacing_pt < 0 or self.cell_spacing_pt > 100:
            errors.append(f"间距应在 0-100pt 之间（当前: {self.cell_spacing_pt}）")
        if self.table_border_color:
            c = self.table_border_color.strip().lower()
            if c not in ("透明", "transparent") and \
               not (c.startswith("#") and len(c) == 7 and
                    all(ch in "0123456789abcdef" for ch in c[1:])):
                errors.append(f"表格边框颜色应为 #RRGGBB 或「透明」（当前: {self.table_border_color}）")
        return errors

    def to_dict(self) -> dict:
        return {
            "images_per_row": self.images_per_row,
            "images_per_column": self.images_per_column,
            "image_width_cm": self.image_width_cm,
            "image_height_cm": self.image_height_cm,
            "keep_aspect": self.keep_aspect,
            "show_filename": self.show_filename,
            "cell_spacing_pt": self.cell_spacing_pt,
            "table_border_color": self.table_border_color,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ImageDocxConfig":
        return ImageDocxConfig(
            images_per_row=int(d.get("images_per_row", 2)),
            images_per_column=int(d.get("images_per_column", 2)),
            image_width_cm=float(d.get("image_width_cm", 0.0)),
            image_height_cm=float(d.get("image_height_cm", 0.0)),
            keep_aspect=bool(d.get("keep_aspect", True)),
            show_filename=bool(d.get("show_filename", True)),
            cell_spacing_pt=float(d.get("cell_spacing_pt", 4.0)),
            table_border_color=str(d.get("table_border_color", "")),
        )

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> "ImageDocxConfig":
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_file(cls, path: str) -> "ImageDocxConfig":
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_json(f.read())

    def save_to_file(self, path: str):
        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json())
