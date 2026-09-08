"""今日任务卡片：计数 chip + 新增输入 + 列表渲染。

对外信号：add_requested(text) / toggle_requested(id, done) / delete_requested(id)
数据通过 render(tasks) 单向流入。
"""

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton

from home.styles import (
    card_qss, card_shadow, card_title_style, count_chip_qss, input_qss,
    add_btn_qss,
)
from home.widgets import TaskRow


class TaskCard(QFrame):
    """任务清单容器。"""

    add_requested = Signal(str)
    toggle_requested = Signal(int, bool)
    delete_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TaskCard")
        self.setStyleSheet(card_qss("TaskCard"))
        card_shadow(self)
        self._build_ui()

    # ──────────────────────────────────────
    #  UI
    # ──────────────────────────────────────
    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 20, 22, 20)
        lay.setSpacing(14)

        head = QHBoxLayout()
        head.setSpacing(10)
        title = QLabel("今日任务", self)
        title.setStyleSheet(card_title_style())
        head.addWidget(title)
        self.count_chip = QLabel("0 / 0", self)
        self.count_chip.setStyleSheet(count_chip_qss())
        head.addWidget(self.count_chip)
        head.addStretch(1)
        lay.addLayout(head)

        add_row = QHBoxLayout()
        add_row.setSpacing(10)
        self.input = QLineEdit(self)
        self.input.setPlaceholderText("添加一项任务，回车确认")
        self.input.setMinimumHeight(40)
        self.input.setStyleSheet(input_qss())
        self.input.returnPressed.connect(self._emit_add)
        add_row.addWidget(self.input, 1)
        add_btn = QPushButton("＋", self)
        add_btn.setFixedSize(40, 40)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet(add_btn_qss())
        add_btn.clicked.connect(self._emit_add)
        add_row.addWidget(add_btn)
        lay.addLayout(add_row)

        self.list_widget = QFrame(self)
        self.list_widget.setStyleSheet("background: transparent;")
        self.list_lay = QVBoxLayout(self.list_widget)
        self.list_lay.setContentsMargins(0, 0, 0, 0)
        self.list_lay.setSpacing(8)
        lay.addWidget(self.list_widget)

    # ──────────────────────────────────────
    #  渲染
    # ──────────────────────────────────────
    def render(self, tasks: list):
        """按数据重建列表并刷新计数。"""
        while self.list_lay.count():
            item = self.list_lay.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)      # 立即脱离布局，避免旧行残留
                w.deleteLater()
        for t in tasks:
            row = TaskRow(
                t,
                on_toggle=lambda tid, done: self.toggle_requested.emit(tid, done),
                on_delete=lambda tid: self.delete_requested.emit(tid),
                parent=self.list_widget,
            )
            self.list_lay.addWidget(row)
        done = sum(1 for t in tasks if t.get("done"))
        self.count_chip.setText(f"{done} / {len(tasks)}")

    def set_count(self, done: int, total: int):
        """只更新计数（勾选时用，避免整表重建）。"""
        self.count_chip.setText(f"{done} / {total}")

    # ──────────────────────────────────────
    #  输入
    # ──────────────────────────────────────
    def _emit_add(self):
        text = self.input.text().strip()
        if not text:
            return
        self.input.clear()
        self.add_requested.emit(text)
