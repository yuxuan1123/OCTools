"""网络加速卡片：整行长滑块 + 状态轮询。

对外：toggled(turn_on) 信号；对内：8s 后台探测（异步、静默、不阻塞 UI）。
"""

from PySide6.QtCore import Signal, QTimer
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel

from home.constants import SUCCESS, MUTED, FAINT, NET_STATIC_IP
from home.services import net_service
from home.styles import (
    card_qss, card_shadow, card_title_style, dot_style, status_label_style,
    sub_text_style, foot_text_style,
)
from home.widgets import SlideSwitch

_POLL_MS = 8000

_TEXT = {"on": "已开启", "off": "已关闭", "unknown": "未知"}
_COLOR = {"on": SUCCESS, "off": MUTED, "unknown": FAINT}


class NetCard(QFrame):
    """滑块即状态：探测结果会反向同步滑块（不触发切换）。"""

    toggled = Signal(bool)
    state_ready = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("NetCard")
        self.setStyleSheet(card_qss("NetCard"))
        card_shadow(self)

        self._net_state = "unknown"
        self.state_ready.connect(self.set_net_state)   # 跨线程 → 排队到 UI 线程
        self._build_ui()

        self._timer = QTimer(self)
        self._timer.setInterval(_POLL_MS)
        self._timer.timeout.connect(self.refresh)
        self.refresh()

    # ──────────────────────────────────────
    #  UI
    # ──────────────────────────────────────
    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 20, 22, 20)
        lay.setSpacing(12)

        head = QHBoxLayout()
        head.setSpacing(8)
        title = QLabel("网络加速", self)
        title.setStyleSheet(card_title_style())
        head.addWidget(title)
        head.addStretch(1)
        self.dot = QLabel(self)
        self.dot.setFixedSize(8, 8)
        self.dot.setStyleSheet(dot_style(FAINT))
        head.addWidget(self.dot)
        self.status_label = QLabel("检测中…", self)
        self.status_label.setStyleSheet(status_label_style(MUTED))
        head.addWidget(self.status_label)
        lay.addLayout(head)

        sub = QLabel(f"静态 IP {NET_STATIC_IP} · 拖动滑块即可切换", self)
        sub.setStyleSheet(sub_text_style())
        lay.addWidget(sub)

        # 整行长滑块（占满卡片内容宽度）
        self.switch = SlideSwitch(self)
        self.switch.clicked.connect(
            lambda: self.toggled.emit(self.switch.isChecked())
        )
        lay.addWidget(self.switch)

        foot = QLabel("后台静默执行 · 无需关注控制台", self)
        foot.setStyleSheet(foot_text_style())
        lay.addWidget(foot)

    # ──────────────────────────────────────
    #  状态
    # ──────────────────────────────────────
    def refresh(self):
        """后台异步探测（子线程执行 PowerShell）。"""
        net_service.probe_state_async(self.state_ready.emit)

    def set_net_state(self, state: str):
        """外部（探测线程 / 业务层）写入状态并同步 UI。"""
        self._net_state = state or "unknown"
        c = _COLOR.get(self._net_state, FAINT)
        self.dot.setStyleSheet(dot_style(c))
        self.status_label.setText(_TEXT.get(self._net_state, "未知"))
        self.status_label.setStyleSheet(status_label_style(c))

        # 同步滑块（阻断信号避免误触发切换）
        self.switch.blockSignals(True)
        self.switch.setChecked(self._net_state == "on")
        self.switch.blockSignals(False)

    @property
    def net_state(self) -> str:
        return self._net_state
