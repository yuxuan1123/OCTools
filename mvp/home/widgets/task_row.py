"""单条任务行：方块勾选图标 + 文本 + 删除。

纯展示控件：勾选 / 删除通过回调上报，不持有 TabHome 引用。
图标：
  未完成 → square.svg
  已完成 → square-check.svg
"""

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QLabel

from config.ui_config import CONFIG as C

from home.constants import INK, MUTED, FAINT, BORDER, BORDER_HV
from home.styles import del_btn_qss

from ui import icon_res

# 图标尺寸（与卡片图标统一）
_ICON_SIZE = C.size("icon_card") or 18


class TaskRow(QFrame):
    """一条任务。on_toggle(tid, done) / on_delete(tid) 由外部注入。"""

    def __init__(self, task: dict, on_toggle=None, on_delete=None, parent=None):
        super().__init__(parent)
        self._task = task
        self._on_toggle = on_toggle
        self._on_delete = on_delete
        self.setObjectName("TaskRow")
        self._build_ui()

    # ──────────────────────────────────────
    #  UI
    # ──────────────────────────────────────
    def _build_ui(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 10, 12, 10)
        lay.setSpacing(12)
        self.setStyleSheet(
            "QFrame#TaskRow {"
            " background: #FCFCFD;"
            f" border: 1px solid {BORDER};"
            f" border-radius: {C.size('radius_section') or 12}px;"
            "}"
            f"QFrame#TaskRow:hover {{ border-color: {BORDER_HV};"
            " background: #FFFFFF; }"
        )

        # 勾选图标按钮（square / square-check 切换）
        self.check_btn = QPushButton(self)
        self.check_btn.setCheckable(True)
        self.check_btn.setChecked(self._task.get("done", False))
        self.check_btn.setFixedSize(_ICON_SIZE + 4, _ICON_SIZE + 4)
        self.check_btn.setCursor(Qt.PointingHandCursor)
        self.check_btn.setStyleSheet(
            "QPushButton { border: none; background: transparent; padding: 0; }"
        )
        self._refresh_icon()
        self.check_btn.toggled.connect(self._handle_toggle)
        lay.addWidget(self.check_btn)

        # 任务文本
        self.label = QLabel(self._task.get("text", ""))
        self.label.setWordWrap(True)
        self._apply_label_style()
        lay.addWidget(self.label, 1)

        # 删除
        del_btn = QPushButton("✕", self)
        del_btn.setFixedSize(26, 26)
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setStyleSheet(del_btn_qss())
        del_btn.clicked.connect(lambda _=False: self._fire_delete())
        lay.addWidget(del_btn)

    # ──────────────────────────────────────
    #  交互
    # ──────────────────────────────────────
    def _refresh_icon(self):
        """按勾选状态切换 SVG 图标：未完成→square，已完成→square-check。"""
        if self.check_btn.isChecked():
            self.check_btn.setIcon(
                icon_res.colored_icon("square-check", INK, _ICON_SIZE)
            )
        else:
            self.check_btn.setIcon(
                icon_res.colored_icon("square", MUTED, _ICON_SIZE)
            )
        self.check_btn.setIconSize(QSize(_ICON_SIZE, _ICON_SIZE))

    def _apply_label_style(self):
        """勾选后：文字变灰 + 删除线。"""
        if self.check_btn.isChecked():
            self.label.setStyleSheet(
                f"color: {FAINT}; font-size: 13px;"
                f" background: transparent; text-decoration: line-through;"
            )
        else:
            self.label.setStyleSheet(
                f"color: {INK}; font-size: 13px; background: transparent;"
            )

    def _handle_toggle(self, _checked: bool):
        self._refresh_icon()
        self._apply_label_style()
        if self._on_toggle:
            self._on_toggle(self._task["id"], self.check_btn.isChecked())

    def _fire_delete(self):
        if self._on_delete:
            self._on_delete(self._task["id"])
