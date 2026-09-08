"""网络加速卡片：整行长滑块 + 状态轮询。

对外：toggled(turn_on) 信号；对内：8s 后台探测（异步、静默、不阻塞 UI）。
"""

from PySide6.QtCore import Signal, QTimer
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel

from home.constants import SUCCESS, MUTED, FAINT
from home.services import net_service
from home.styles import (
    card_qss, card_shadow, card_title_style, dot_style, status_label_style,
    sub_text_style,
)
from home.widgets import SlideSwitch

_POLL_MS = 8000
_HOLD_MS = 30000   # 用户操作后保持指定状态 30s，期间探测不反向同步滑块

_TEXT = {"on": "已开启", "off": "已关闭", "unknown": "未知"}
_COLOR = {"on": SUCCESS, "off": MUTED, "unknown": FAINT}


class NetCard(QFrame):
    """滑块即状态：探测结果会反向同步滑块（不触发切换）。

    用户拖动后进入 30s 保持期，期间探测结果只更新状态点/文案，
    不反向扳动滑块；保持期结束自动探测一次对齐真实 IP 状态。
    """

    toggled = Signal(bool)
    state_ready = Signal(object)

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
        self._timer.start()

        # 用户操作后的保持期：到期后探测一次对齐真实状态
        self._hold_timer = QTimer(self)
        self._hold_timer.setSingleShot(True)
        self._hold_timer.setInterval(_HOLD_MS)
        self._hold_timer.timeout.connect(self.refresh)

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

        sub = QLabel("当前 IP：检测中…", self)
        sub.setStyleSheet(sub_text_style())
        lay.addWidget(sub)
        self.ip_label = sub

        # 整行长滑块（占满卡片内容宽度）
        self.switch = SlideSwitch(self)
        self.switch.clicked.connect(self._on_user_toggle)
        lay.addWidget(self.switch)

    # ──────────────────────────────────────
    #  状态
    # ──────────────────────────────────────
    def _on_user_toggle(self):
        """用户拖动滑块：进入 30s 保持期，再对外发切换信号。

        保持期内探测结果不反向扳动滑块，让 net.ps1 有时间完成
        UAC 提权 + 网络切换，避免"刚开就被探测拉回去"。
        """
        self._hold_timer.start()
        self.toggled.emit(self.switch.isChecked())

    def refresh(self):
        """后台异步探测（子线程执行 PowerShell）。"""
        net_service.probe_state_async(self.state_ready.emit)

    def set_net_state(self, payload):
        """外部（探测线程 / 业务层）写入状态并同步 UI。

        payload 为 dict：{"state": "on"/"off"/"unknown", "ip": "x.x.x.x"}
        用户操作的 30s 保持期内：只更新状态点/文案/当前 IP，不反向扳动滑块，
        让用户指定的状态保持到 hold 结束后由真实 IP 状态对齐。
        """
        if isinstance(payload, dict):
            state = payload.get("state", "unknown")
            ip = payload.get("ip", "—")
        else:
            state, ip = payload, "—"

        self._net_state = state or "unknown"
        c = _COLOR.get(self._net_state, FAINT)
        self.dot.setStyleSheet(dot_style(c))
        self.status_label.setText(_TEXT.get(self._net_state, "未知"))
        self.status_label.setStyleSheet(status_label_style(c))
        self.ip_label.setText(f"当前 IP：{ip}")

        # 保持期内不同步滑块（让用户指定状态保持 30s）
        if self._hold_timer.isActive():
            return

        # 同步滑块（阻断信号避免误触发切换）
        self.switch.blockSignals(True)
        self.switch.setChecked(self._net_state == "on")
        self.switch.blockSignals(False)

    @property
    def net_state(self) -> str:
        return self._net_state
