"""
octool/ui/tabs/merge/card_output.py
───────────────────────────────────
输出卡片：输出文件选择（拼接模式：合并后的单个文件）。
"""

from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel,
)

from ui import icon_res
from config.ui_config import CONFIG as C

from ui.tabs.tab_component.card_widgets import make_card, make_title_row, make_icon_label


def build_output_card(parent, **ctx):
    """输出卡片，返回 QFrame。

    ctx 需含 page（TabMerge），用于登记 output_entry / output_browse_btn。
    """
    page = ctx["page"]

    card, c3 = make_card(parent)
    make_title_row(card, "output", "输出", c3)

    form3 = QFormLayout()
    form3.setHorizontalSpacing(12)
    form3.setVerticalSpacing(9)
    form3.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

    # 输出文件（拼接后的单个文件）
    page.output_entry = QLineEdit(card)
    page.output_entry.setPlaceholderText("选择输出文件（拼接后的单个文件）…")
    page.output_browse_btn = QPushButton("浏览", card)
    page.output_browse_btn.setObjectName("primary")
    page.output_browse_btn.setIcon(icon_res.colored_icon("folder"))
    page.output_browse_btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
    page.output_browse_btn.clicked.connect(page._browse_output_file)
    of_row = QWidget(card)
    of_lay = QHBoxLayout(of_row)
    of_lay.setContentsMargins(0, 0, 0, 0)
    of_lay.setSpacing(C.size("action_spacing"))
    of_lay.addWidget(page.output_entry, 1)
    of_lay.addWidget(page.output_browse_btn)
    form3.addRow(make_icon_label("输出文件", "download", card), of_row)

    hint3 = QLabel("（所有文件合并为单个文件后保存到此路径）", card)
    hint3.setObjectName("hint")
    hint3.setWordWrap(True)
    form3.addRow("", hint3)

    c3.addLayout(form3)

    return card
