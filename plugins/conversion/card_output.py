"""
OCTools/ui/tabs/conversion/card_output.py
────────────────────────────────────────
输出卡片：输出文件夹选择（转换模式专用）。

对应原 tab_conversion.py 中「卡片 3：输出」整段。
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

    ctx 需含 page（TabConversion），用于登记 output_folder_entry / output_folder_browse_btn。
    """
    page = ctx["page"]

    card, c3 = make_card(parent)
    make_title_row(card, "output", "输出", c3)

    form3 = QFormLayout()
    form3.setHorizontalSpacing(12)
    form3.setVerticalSpacing(9)
    form3.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

    # 输出文件夹（转换模式专用）
    page.output_folder_entry = QLineEdit(card)
    page.output_folder_entry.setPlaceholderText("选择输出文件夹（每个源文件单独转换后输出到此）…")
    page.output_folder_browse_btn = QPushButton("浏览文件夹", card)
    page.output_folder_browse_btn.setObjectName("primary")
    page.output_folder_browse_btn.setIcon(icon_res.colored_icon("folder"))
    page.output_folder_browse_btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
    page.output_folder_browse_btn.clicked.connect(page._browse_output_folder)
    oo_row = QWidget(card)
    oo_lay = QHBoxLayout(oo_row)
    oo_lay.setContentsMargins(0, 0, 0, 0)
    oo_lay.setSpacing(C.size("action_spacing"))
    oo_lay.addWidget(page.output_folder_entry, 1)
    oo_lay.addWidget(page.output_folder_browse_btn)
    form3.addRow(make_icon_label("输出文件夹", "folder", card), oo_row)

    hint3 = QLabel("（转换模式下所有文件逐个转换后输出到此文件夹）", card)
    hint3.setObjectName("hint")
    hint3.setWordWrap(True)
    form3.addRow("", hint3)

    c3.addLayout(form3)

    return card
