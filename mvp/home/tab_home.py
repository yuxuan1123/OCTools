"""首页 · OCTools 工作台（白灰高级 · 墨黑强调 · 动态长滑块）

组装层：只做三件事——
  1. 摆布局（Hero / 双卡 / 网络 / 任务）
  2. 每秒 tick 把 state 推给各区块
  3. 把区块信号接到 state 与 services

所有 PowerShell / bat 调用完全静默（无弹窗）。
"""

import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QScrollArea,
)

# ── 路径引导 ──────────────────────────────
# _MVP_ROOT  : home 包的父目录 → 让 `from home.xxx import` 生效
# _ROOT      : 项目根         → 让 `from config.ui_config import` 生效
_MVP_ROOT = Path(__file__).resolve().parent.parent
_ROOT = _MVP_ROOT.parent
for _p in (str(_ROOT), str(_MVP_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from config.ui_config import CONFIG as C      # noqa: E402
from ui.toast import show_toast               # noqa: E402

from home.greeting import greeting        # noqa: E402
from home.constants import MUTED          # noqa: E402
from home.state import HomeState          # noqa: E402
from home.styles import page_qss, scroll_qss  # noqa: E402
from home.sections import (
    HeroSection, HeroModel, ClockInCard, WorkModeCard, NetCard, TaskCard,
)                                             # noqa: E402
from home.services import net_service, workmode_service  # noqa: E402

_WEEKDAYS = "一二三四五六日"


class TabHome(QWidget):
    """首页：白灰高级 · 智能打卡 · 一键工作模式 · 任务清单 · 网络加速。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TabHome")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.state = HomeState()

        self._build_ui()
        self._connect()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)
        self._tick()
        self._render_tasks()

    # ──────────────────────────────────────
    #  布局
    # ──────────────────────────────────────
    def _build_ui(self):
        self.setStyleSheet(page_qss("TabHome"))

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(C.size("card_spacing") or 18)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(scroll_qss())
        scroll.viewport().setStyleSheet("background: transparent;")
        body = QWidget()
        body.setObjectName("scrollInner")
        body.setStyleSheet("QWidget#scrollInner { background: transparent; }")
        lay = QVBoxLayout(body)
        lay.setContentsMargins(
            C.size("page_margin_l") or 32, C.size("page_margin_t") or 28,
            C.size("scroll_gutter_right") or 24, C.size("page_margin_b") or 28,
        )
        lay.setSpacing(C.size("card_spacing") or 18)
        lay.setAlignment(Qt.AlignTop)
        scroll.setWidget(body)
        outer.addWidget(scroll, 1)

        # 区块
        self.hero = HeroSection(body)
        self.clock_card = ClockInCard(body)
        self.work_card = WorkModeCard(body)
        self.net_card = NetCard(body)
        self.task_card = TaskCard(body)

        lay.addWidget(self.hero)
        lay.addWidget(self._action_row(body))
        lay.addWidget(self.net_card)
        lay.addWidget(self.task_card)
        lay.addStretch(1)

    def _action_row(self, parent) -> QWidget:
        """打卡 + 工作模式 双卡并排。"""
        host = QWidget(parent)
        host.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(host)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(C.size("card_spacing") or 18)
        lay.addWidget(self.clock_card, 1)
        lay.addWidget(self.work_card, 1)
        return host

    # ──────────────────────────────────────
    #  信号
    # ──────────────────────────────────────
    def _connect(self):
        self.clock_card.punch_clicked.connect(self._do_clockin)
        self.work_card.start_clicked.connect(self._do_workmode)
        self.net_card.toggled.connect(self._do_net_toggle)
        self.task_card.add_requested.connect(self._add_task)
        self.task_card.toggle_requested.connect(self._toggle_task)
        self.task_card.delete_requested.connect(self._delete_task)

    # ──────────────────────────────────────
    #  每秒刷新
    # ──────────────────────────────────────
    def _tick(self):
        now = datetime.now()
        st = self.state

        # ── Hero ──
        tip, clock_txt, color, badge = greeting(now, am_done=st.am_done, pm_done=st.pm_done)
        cur = now.strftime("%H:%M:%S")
        is_countdown = clock_txt != cur
        last = st.last_iso
        if is_countdown:
            hint, hint_color = f"› 现在 {cur}", MUTED
        else:
            hint = f"› 最近打卡 {last[11:19]}" if last else "› 今日尚未打卡"
            hint_color = color

        self.hero.apply_model(HeroModel(
            date_text=f"{now.strftime('%Y 年 %m 月 %d 日')}  星期{_WEEKDAYS[now.weekday()]}",
            tip=tip, clock=clock_txt, color=color, badge=badge,
            hint=hint, hint_color=hint_color, is_countdown=is_countdown,
        ))

        # ── 打卡卡 ──
        slot, status, hint_text = st.clockin_state()
        self.clock_card.set_state(
            slot, status, hint_text,
            am_iso=st.am_time, pm_iso=st.pm_time, am_today=st.am_done,
        )

    # ──────────────────────────────────────
    #  打卡
    # ──────────────────────────────────────
    def _do_clockin(self):
        slot, status, _ = self.state.clockin_state()
        if status != "pending":
            show_toast(self, "当前时间不可打卡", duration_ms=1600, kind="warn")
            return
        self.state.punch(slot)
        self._tick()
        show_toast(self, f"{'上午' if slot == 'am' else '下午'}打卡成功",
                   duration_ms=1500, kind="success")

    # ──────────────────────────────────────
    #  一键工作模式（静默）
    # ──────────────────────────────────────
    def _do_workmode(self):
        if not workmode_service.script_exists():
            show_toast(self, "未找到 home.bat（同级目录）", duration_ms=2000, kind="warn")
            return
        ok, err = workmode_service.start_workmode()
        if ok:
            show_toast(self, "工作模式已启动", duration_ms=1500, kind="success")
        else:
            show_toast(self, f"启动失败：{err}", duration_ms=2000, kind="warn")

    # ──────────────────────────────────────
    #  网络加速（静默）
    # ──────────────────────────────────────
    def _do_net_toggle(self, turn_on: bool):
        if not net_service.script_exists():
            show_toast(self, "未找到 net.ps1（同级目录）", duration_ms=2000, kind="warn")
            return
        label = "开启" if turn_on else "关闭"
        ok, err = net_service.apply_action(turn_on)
        if ok:
            show_toast(self, f"正在{label}网络加速", duration_ms=2000, kind="info")
            QTimer.singleShot(1500, self.net_card.refresh)
        else:
            show_toast(self, f"{label}失败：{err}", duration_ms=2000, kind="warn")

    # ──────────────────────────────────────
    #  任务
    # ──────────────────────────────────────
    def _render_tasks(self):
        self.task_card.render(self.state.tasks)

    def _add_task(self, text: str):
        self.state.add_task(text)
        self._render_tasks()

    def _toggle_task(self, tid: int, done: bool):
        self.state.toggle_task(tid, done)
        self.task_card.set_count(self.state.done_count(), len(self.state.tasks))

    def _delete_task(self, tid: int):
        self.state.remove_task(tid)
        self._render_tasks()
