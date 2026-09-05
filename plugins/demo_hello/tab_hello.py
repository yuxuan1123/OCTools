# -*- coding: utf-8 -*-
"""
OCTools 插件 demo_hello：direct 模式示例。
───────────────────────────────────────────────
direct：主进程直接 import 模块 → 取类 → 实例化 QWidget，无需依赖隔离。
requirements.txt 为空（或仅 PySide6），无第三方依赖。
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class TabHello(QWidget):
    """direct 模式示例：主进程直接加载的普通 QWidget。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        label = QLabel(
            "Hello, OCTools 插件！\n\n"
            "direct 模式：主进程直接 import，无依赖隔离。\n"
            "（requirements.txt 为空 → 自动判定为 direct）",
            self,
        )
        label.setObjectName("hint")
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        lay.addWidget(label)
