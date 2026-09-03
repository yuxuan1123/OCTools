"""
octool/config/screen_region_config.py
───────────────────────────────────────────────
截图框（OCR 识别区域）配置（唯一配置层）

配置项：
  - fixed        : 是否固定截图框。固定后，按热键 / 托盘触发屏幕翻译时
                   直接使用 fixed_rect 区域，不再弹出框选。
  - x / y / w / h: 固定区域（屏幕坐标，像素）
  - border_color : 截图框边框颜色（#RRGGBB，框选遮罩高亮色）

支持命名预设（保存/加载/删除/导出/导入），方便用户在不同区域配置间切换。
"""

import os
import json
from dataclasses import dataclass
from typing import List, Optional

# 默认边框颜色（与主题主色一致）
DEFAULT_BORDER_COLOR = "#3B82F6"

# 常用边框颜色预设（供 UI 快速选择）
BORDER_COLOR_PRESETS = [
    ("蓝色（默认）", "#3B82F6"),
    ("红色", "#EF4444"),
    ("绿色", "#10B981"),
    ("橙色", "#F59E0B"),
    ("紫色", "#8B5CF6"),
    ("粉色", "#EC4899"),
    ("青色", "#06B6D4"),
    ("白色", "#FFFFFF"),
]


@dataclass
class ScreenRegionConfig:
    """截图框（OCR 识别区域）配置"""
    fixed: bool = False
    x: int = 0
    y: int = 0
    w: int = 0
    h: int = 0
    border_color: str = DEFAULT_BORDER_COLOR

    # ── 区域工具 ──

    def set_rect(self, x: int, y: int, w: int, h: int):
        self.x, self.y, self.w, self.h = int(x), int(y), int(w), int(h)

    def has_rect(self) -> bool:
        return self.w > 0 and self.h > 0

    def rect_tuple(self) -> tuple:
        """返回 (x, y, w, h)；无有效区域时返回 None"""
        return (self.x, self.y, self.w, self.h) if self.has_rect() else None

    def summary(self) -> str:
        if not self.has_rect():
            return "未设置区域"
        state = "固定" if self.fixed else "未固定"
        return f"{state} · ({self.x}, {self.y}) {self.w}×{self.h}"

    def validate(self) -> List[str]:
        errors = []
        if self.w < 0 or self.h < 0 or self.x < 0 or self.y < 0:
            errors.append("区域坐标/尺寸不能为负数")
        bc = str(self.border_color or "").strip()
        if bc and not (bc.startswith("#") and len(bc) == 7):
            errors.append(f"边框颜色应为 #RRGGBB 格式（当前: {bc}）")
        return errors

    # ── 序列化（与 TtsConfig / SttConfig 保持一致接口）──

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items()}

    @classmethod
    def from_dict(cls, d):
        cfg = cls()
        for k, v in (d or {}).items():
            if hasattr(cfg, k):
                try:
                    setattr(cfg, k, v)
                except Exception:
                    pass
        return cfg

    def to_json(self, indent=2):
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_json(cls, s):
        return cls.from_dict(json.loads(s))

    def save_to_file(self, path):
        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json())

    @classmethod
    def from_file(cls, path):
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return cls.from_json(f.read())
        except Exception:
            return None


def default_config() -> ScreenRegionConfig:
    return ScreenRegionConfig()
