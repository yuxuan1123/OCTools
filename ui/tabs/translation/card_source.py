"""
OCTools/ui/tabs/translation/card_source.py
────────────────────────────────────────────────────
原文卡片：标题「原文」+ 输入 QTextEdit + 载入文件 / 清空 按钮。

按钮 click 回调接 actions.load_file / actions.clear_input。
"""

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QTextEdit

from ui import icon_res
from config.ui_config import CONFIG as C

from ui.tabs.tab_component.card_widgets import make_card, make_title_row
from ui.tabs.translation import actions


def build_source_card(parent, **ctx):
    """原文卡片，返回 QFrame。

    ctx 需含 page（TabTranslation），用于登记 input_edit。
    """
    page = ctx["page"]

    card, c2 = make_card(parent)
    make_title_row(card, "source", "原文", c2)

    page.input_edit = QTextEdit(card)
    page.input_edit.setPlaceholderText("输入要翻译的文本（中英文皆可），或点击「载入文件」…")
    page.input_edit.setMinimumHeight(C.size("input_min_h_140"))
    c2.addWidget(page.input_edit)

    tool2 = QWidget(card)
    t2_lay = QHBoxLayout(tool2)
    t2_lay.setContentsMargins(0, 0, 0, 0)
    t2_lay.setSpacing(C.size("header_row_spacing"))
    load_btn = QPushButton("载入文件…", tool2)
    load_btn.setObjectName("primary")
    load_btn.setIcon(icon_res.colored_icon("folder"))
    load_btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
    load_btn.clicked.connect(lambda: actions.load_file(page))
    t2_lay.addWidget(load_btn)
    clear_btn = QPushButton("清空", tool2)
    clear_btn.setObjectName("ghost")
    clear_btn.setIcon(icon_res.colored_icon("trash"))
    clear_btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
    clear_btn.clicked.connect(lambda: actions.clear_input(page))
    t2_lay.addWidget(clear_btn)
    t2_lay.addStretch(1)
    c2.addWidget(tool2)

    return card