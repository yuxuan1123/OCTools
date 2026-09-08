"""一键工作模式卡片：静态展示 + 启动信号。"""

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from home.constants import INK, GRAPHITE
from home.styles import (
    card_qss, card_shadow, card_title_style, dot_style, sub_text_style,
    foot_text_style, outline_btn_qss,
)


class WorkModeCard(QFrame):
    """启动 home.bat · 一键就位。"""

    start_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("WorkCard")
        self.setStyleSheet(card_qss("WorkCard"))
        card_shadow(self)
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 20, 22, 20)
        lay.setSpacing(10)

        head = QHBoxLayout()
        head.setSpacing(8)
        title = QLabel("工作模式", self)
        title.setStyleSheet(card_title_style())
        head.addWidget(title)
        head.addStretch(1)
        dot = QLabel(self)
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(dot_style(INK))
        head.addWidget(dot)
        ready = QLabel("就绪", self)
        ready.setStyleSheet(
            f"color: {GRAPHITE}; font-size: 11px; font-weight: 700;"
            f" background: transparent;"
        )
        head.addWidget(ready)
        lay.addLayout(head)

        sub = QLabel("启动 home.bat · 一键就位", self)
        sub.setStyleSheet(sub_text_style())
        sub.setWordWrap(True)
        lay.addWidget(sub)
        lay.addStretch(1)

        self.btn = QPushButton("一键开启", self)
        self.btn.setMinimumHeight(48)
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.setStyleSheet(outline_btn_qss())
        self.btn.clicked.connect(self.start_clicked)
        lay.addWidget(self.btn)

        hint = QLabel("后台静默运行 · 不打扰", self)
        hint.setStyleSheet(foot_text_style())
        lay.addWidget(hint)
