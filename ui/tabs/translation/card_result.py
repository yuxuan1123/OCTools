"""
OCTools/ui/tabs/translation/card_result.py
────────────────────────────────────────────────────
译文卡片：标题「译文」+ 只读 QTextEdit + 复制译文 / 保存译文 按钮。

回调接 actions.copy_result / actions.save_result。
"""

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QTextEdit

from ui import icon_res
from config.ui_config import CONFIG as C

from ui.tabs.tab_component.card_widgets import make_card, make_title_row
from ui.tabs.translation import actions


def build_result_card(parent, **ctx):
    """译文卡片，返回 QFrame。

    ctx 需含 page（TabTranslation），用于登记 output_edit。
    """
    page = ctx["page"]

    card, c3 = make_card(parent)
    make_title_row(card, "result", "译文", c3)

    page.output_edit = QTextEdit(card)
    page.output_edit.setReadOnly(True)
    page.output_edit.setPlaceholderText("翻译结果将显示在这里…")
    page.output_edit.setMinimumHeight(C.size("input_min_h_140"))
    c3.addWidget(page.output_edit)

    tool3 = QWidget(card)
    t3_lay = QHBoxLayout(tool3)
    t3_lay.setContentsMargins(0, 0, 0, 0)
    t3_lay.setSpacing(C.size("header_row_spacing"))
    copy_btn = QPushButton("复制译文", tool3)
    copy_btn.setObjectName("primary")
    copy_btn.setIcon(icon_res.colored_icon("copy"))
    copy_btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
    copy_btn.clicked.connect(lambda: actions.copy_result(page))
    t3_lay.addWidget(copy_btn)
    save_btn = QPushButton("保存译文…", tool3)
    save_btn.setObjectName("primary")
    save_btn.setIcon(icon_res.colored_icon("download"))
    save_btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
    save_btn.clicked.connect(lambda: actions.save_result(page))
    t3_lay.addWidget(save_btn)
    t3_lay.addStretch(1)
    c3.addWidget(tool3)

    return card