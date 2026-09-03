"""
OCTools/ui/ui_component/split_window.py
───────────────────────────────────────────────
JSON 驱动的 PySide6 两栏分割窗口组件（纯分割，无按钮）。

特性：
- 左右两栏由 QSplitter 承载，比例/颜色/文字全部从 JSON 加载。
- 无任何折叠/展开按钮，仅提供内容区设置 API。
- 不传 config 时回退到 config/ui_config.json 的 split 段（CONFIG 单例）。

用法：
    from split_window import SplitWindow
    w = SplitWindow(config="split_config.json")
    w.set_left_content(QLabel("业务：左侧树"))
    w.set_right_content(QLabel("业务：右侧编辑器"))
    w.show()
"""
from __future__ import annotations

import sys
import json
import os
from typing import Optional

from PySide6.QtCore import Qt, QSize
from ui.style_hook import StyleHookMixin
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QSplitter, QMainWindow,
)

from config.ui_config import CONFIG as C

# 资源根目录（保留以备将来扩展）
_RESOURCE_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "resources")
)

# --------------------------------------------------------------------------- #
#  默认配置
# --------------------------------------------------------------------------- #
def _default_config() -> dict:
    return {
        "window": {
            "title": "两栏分割窗口", "width": 1000, "height": 700,
            "frameless": False, "background": "#F3F5F9",
        },
        "splitter": {
            "orientation": "horizontal",
            "sizes": [0, 580],
            "stretch": [1, 1],
            "collapsible": [False, False],
            "handle_width": 4,
        },
        "panes": {
            "left": {
                "background": "#FBFCFE", "foreground": "#1F2430",
                "label": "左栏", "font": {"family": "Microsoft YaHei", "size": 28},
            },
            "right": {
                "background": "#F3F5F9", "foreground": "#1F2430",
                "label": "右栏", "font": {"family": "Microsoft YaHei", "size": 28},
            },
        },
    }

def load_config(config) -> dict:
    base = _default_config()
    if config is None:
        user = C.section("split")   # 回退到统一配置（ui_config.json 的 split 段）
    elif isinstance(config, str):
        with open(config, "r", encoding="utf-8") as f:
            user = json.load(f)
    elif isinstance(config, dict):
        user = config
    else:
        raise TypeError("config 必须是 JSON 文件路径或 dict")
    _deep_merge(base, user)
    return base

def _deep_merge(base: dict, user: dict):
    for k, v in user.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v

# --------------------------------------------------------------------------- #
#  单栏容器：仅放置业务控件
# --------------------------------------------------------------------------- #
class _Pane(QWidget):
    """单栏容器：主体放业务控件。"""

    def __init__(self, cfg: dict, parent=None):
        super().__init__(parent)
        self.pane_cfg = cfg

        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(0,0,0,0)
        self._root.setSpacing(0)

        self._body = QWidget()
        self._body_layout = QVBoxLayout(self._body)
        self._body_layout.setContentsMargins(0, 0, 0, 0) 
        self._body_layout.setSpacing(0)
        self.set_pane_style(self._body, cfg)

        self._root.addWidget(self._body, 1)

        self.set_pane_style(self, {"background": cfg.get("background")})

    def set_pane_style(self, w: QWidget, cfg: dict):
        bg = cfg.get("background")
        if bg:
            w.setStyleSheet(f"background:{bg};")

    def set_body(self, widget: QWidget):
        for child in self._body.children():
            if isinstance(child, QWidget) and child is not widget:
                child.setParent(None)
        self._body_layout.addWidget(widget)

# --------------------------------------------------------------------------- #
#  两栏分割窗口
# --------------------------------------------------------------------------- #
class SplitWindow(StyleHookMixin, QMainWindow):
    """开箱即用的两栏分割窗口（无折叠按钮）。"""

    def __init__(self, config=None, parent=None):
        super().__init__(parent)
        self.cfg = load_config(config)
        w = self.cfg["window"]
        self.setWindowTitle(w.get("title", "两栏分割窗口"))
        self.resize(w.get("width", 1000), w.get("height", 700))
        if w.get("frameless"):
            self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

        scfg = self.cfg["splitter"]
        orient = Qt.Horizontal if scfg.get("orientation", "horizontal") == "horizontal" else Qt.Vertical
        self._splitter = QSplitter(orient)
        self._splitter.setChildrenCollapsible(False)
        # 左栏
        self._left = _Pane(self.cfg["panes"]["left"])
        # 右栏
        self._right = _Pane(self.cfg["panes"]["right"])

        self._splitter.addWidget(self._left)
        self._splitter.addWidget(self._right)

        sizes = scfg.get("sizes") or [450, 550]
        self._splitter.setSizes(sizes)
        stretch = scfg.get("stretch") or [1, 1]
        for i, s in enumerate(stretch):
            self._splitter.setStretchFactor(i, s)
        collapsible = scfg.get("collapsible") or [False, False]
        self._splitter.setChildrenCollapsible(False)

        self.setCentralWidget(self._splitter)
        self._apply_inline_style()

    # -------------------------- 公共 API -------------------------- #

    def _apply_inline_style(self):
        """主题切换时由 StyleHookMixin 调用：重刷分隔条配色（随主题变）。"""
        scfg = self.cfg["splitter"]
        if scfg.get("handle_width"):
            self._splitter.setStyleSheet(
                f"QSplitter::handle{{background:{C.color('border')};"
                f"width:{scfg['handle_width']}px;}}")
    def set_left_content(self, widget: QWidget):
        self._left.set_body(widget)

    def set_right_content(self, widget: QWidget):
        self._right.set_body(widget)

# --------------------------------------------------------------------------- #
#  演示
# --------------------------------------------------------------------------- #
def main():
    app = QApplication(sys.argv)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "split_config.json")
    if not os.path.exists(config_path):
        config_path = None  # 回退到默认配置
    w = SplitWindow(config=config_path)
    w.set_left_content(QLabel("左栏业务内容"))
    w.set_right_content(QLabel("右栏业务内容"))
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()