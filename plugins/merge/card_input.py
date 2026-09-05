"""
OCTools/ui/tabs/merge/card_input.py
──────────────────────────────────
输入卡片：源文件 / 源文件夹（二选一）+ 源文件格式选择器（仅源文件夹时显示）。
"""

from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel,
)

from ui import icon_res
from config.ui_config import CONFIG as C

from ui.tabs.tab_component.card_widgets import make_card, make_title_row, make_icon_label
from plugins.merge.registry import (
    ALL_SOURCE_FORMATS, FormatPicker, _categories_for,
)


def build_input_card(parent, **ctx):
    """输入卡片，返回 QFrame。

    ctx 需含 page（TabMerge），用于登记 input_entry / folder_entry /
    source_picker / _src_fmt_widget 并连接浏览与格式选择信号。
    """
    page = ctx["page"]

    card, c1 = make_card(parent)
    make_title_row(card, "input", "输入", c1)

    form1 = QFormLayout()
    form1.setHorizontalSpacing(12)
    form1.setVerticalSpacing(9)
    form1.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

    # 源文件
    page.input_entry = QLineEdit(card)
    page.input_entry.setPlaceholderText("选择源文件（单文件拼接）…")
    browse_in = QPushButton("浏览", card)
    browse_in.setObjectName("primary")
    browse_in.setIcon(icon_res.colored_icon("folder"))
    browse_in.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
    browse_in.clicked.connect(page._browse_input)
    in_row = QWidget(card)
    ir_lay = QHBoxLayout(in_row)
    ir_lay.setContentsMargins(0, 0, 0, 0)
    ir_lay.setSpacing(C.size("action_spacing"))
    ir_lay.addWidget(page.input_entry, 1)
    ir_lay.addWidget(browse_in)
    form1.addRow(make_icon_label("源文件", "file", card), in_row)

    # 源文件夹
    page.folder_entry = QLineEdit(card)
    page.folder_entry.setPlaceholderText("选择源文件夹（多文件拼接为单个文件）…")
    browse_folder = QPushButton("浏览文件夹", card)
    browse_folder.setObjectName("primary")
    browse_folder.setIcon(icon_res.colored_icon("folder"))
    browse_folder.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
    browse_folder.clicked.connect(page._browse_folder)
    folder_row = QWidget(card)
    fr_lay = QHBoxLayout(folder_row)
    fr_lay.setContentsMargins(0, 0, 0, 0)
    fr_lay.setSpacing(C.size("action_spacing"))
    fr_lay.addWidget(page.folder_entry, 1)
    fr_lay.addWidget(browse_folder)
    form1.addRow(make_icon_label("源文件夹", "folder", card), folder_row)

    hint1 = QLabel("（源文件与源文件夹二选一；多文件拼接为单个文件）", card)
    hint1.setObjectName("hint")
    hint1.setWordWrap(True)
    form1.addRow("", hint1)

    # 源文件格式（仅源文件夹时显示）
    page._src_fmt_widget = QWidget(card)
    sf_lay = QHBoxLayout(page._src_fmt_widget)
    sf_lay.setContentsMargins(0, 0, 0, 0)
    sf_lay.setSpacing(C.size("form_row_spacing"))
    page.source_picker = FormatPicker(_categories_for(ALL_SOURCE_FORMATS),
                                      page._src_fmt_widget)
    page.source_picker.format_selected.connect(page._on_folder_fmt_selected)
    page.source_picker.set_available(ALL_SOURCE_FORMATS)
    sf_lay.addWidget(page.source_picker, 1)
    form1.addRow(make_icon_label("源文件格式", "tag", card), page._src_fmt_widget)
    page._src_fmt_widget.setVisible(False)

    c1.addLayout(form1)

    return card
