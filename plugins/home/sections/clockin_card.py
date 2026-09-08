"""智能打卡卡片：状态点 + 说明 + 打卡按钮。

对外只发 punch_clicked 信号；按钮文案 / 启用由 set_state 决定。
"""

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from home.constants import INK, MUTED, FAINT, SUCCESS
from home.styles import (
    card_qss, card_shadow, card_title_style, dot_style, status_label_style,
    sub_text_style, foot_text_style, primary_btn_qss,
)

_STATUS_TEXT = {"pending": "待打卡", "done": "已完成", "off": "等待中"}
_STATUS_COLOR = {"pending": INK, "done": SUCCESS, "off": FAINT}


class ClockInCard(QFrame):
    """上午 / 下午打卡。"""

    punch_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ClockCard")
        self.setStyleSheet(card_qss("ClockCard"))
        card_shadow(self)
        self._build_ui()

    # ──────────────────────────────────────
    #  UI
    # ──────────────────────────────────────
    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 20, 22, 20)
        lay.setSpacing(10)

        head = QHBoxLayout()
        head.setSpacing(8)
        title = QLabel("智能打卡", self)
        title.setStyleSheet(card_title_style())
        head.addWidget(title)
        head.addStretch(1)
        self.dot = QLabel(self)
        self.dot.setFixedSize(8, 8)
        self.dot.setStyleSheet(dot_style(FAINT))
        head.addWidget(self.dot)
        self.status_label = QLabel("—", self)
        self.status_label.setStyleSheet(status_label_style(MUTED))
        head.addWidget(self.status_label)
        lay.addLayout(head)

        self.sub = QLabel("", self)
        self.sub.setStyleSheet(sub_text_style())
        self.sub.setWordWrap(True)
        lay.addWidget(self.sub)
        lay.addStretch(1)

        self.btn = QPushButton("立即打卡", self)
        self.btn.setMinimumHeight(48)
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.setStyleSheet(primary_btn_qss())
        self.btn.clicked.connect(self.punch_clicked)
        lay.addWidget(self.btn)

        self.last_label = QLabel("最近打卡：—", self)
        self.last_label.setStyleSheet(foot_text_style())
        lay.addWidget(self.last_label)

    # ──────────────────────────────────────
    #  刷新
    # ──────────────────────────────────────
    def set_state(self, slot: str, status: str, hint: str,
                  am_iso: str = "", pm_iso: str = "", am_today: bool = False):
        """按打卡状态刷新整卡。

        slot     : 'am' / 'pm' / 'none'
        status   : 'pending' / 'done' / 'off'
        am_iso   : 上午打卡 ISO 串（可空）
        pm_iso   : 下午打卡 ISO 串（可空）
        am_today : 上午打卡是否为今天
        """
        color = _STATUS_COLOR.get(status, FAINT)
        self.dot.setStyleSheet(dot_style(color))
        self.status_label.setText(_STATUS_TEXT.get(status, "—"))
        self.status_label.setStyleSheet(status_label_style(color))
        self.sub.setText(hint)

        if status == "pending":
            self.btn.setEnabled(True)
            self.btn.setText(f"立即打{'上午' if slot == 'am' else '下午'}卡")
            shown = (am_iso if slot == "am" else pm_iso)[11:19]
            self.last_label.setText(f"最近打卡：{shown}" if shown else "最近打卡：—")
        elif status == "done":
            self.btn.setEnabled(False)
            self.btn.setText("本时段已完成")
            iso = am_iso if slot == "am" else pm_iso
            self.last_label.setText(f"最近打卡：{iso[11:19]}" if iso else "最近打卡：—")
        else:
            self.btn.setEnabled(False)
            self.btn.setText("暂不可打卡")
            am_t = am_iso[11:19] if am_today and am_iso else ""
            self.last_label.setText(f"上午打卡：{am_t}" if am_t else "最近打卡：—")
