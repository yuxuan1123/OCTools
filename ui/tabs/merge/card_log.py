"""
octool/ui/tabs/merge/card_log.py
────────────────────────────────
日志卡片：标题「拼接日志」+ 只读 QTextEdit#log。
"""

from PySide6.QtWidgets import QTextEdit

from config.ui_config import CONFIG as C

from ui.tabs.tab_component.card_widgets import make_card, make_title_row


def build_log_card(parent, **ctx):
    """日志卡片，返回 QFrame。

    ctx 需含 page（TabMerge），用于登记 log_text。
    """
    page = ctx["page"]

    card, c4 = make_card(parent)
    make_title_row(card, "log", "拼接日志", c4)

    page.log_text = QTextEdit(card)
    page.log_text.setObjectName("log")
    page.log_text.setReadOnly(True)
    page.log_text.setMinimumHeight(C.size("txn_log_min_h"))
    c4.addWidget(page.log_text)

    return card
