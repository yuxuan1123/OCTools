"""
OCTools/ui/tabs/translation/button_translate.py
────────────────────────────────────────────────────────
「开始翻译」主按钮：objectName convertBtn，图标 globe，高度 cta_h。
"""

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QPushButton

from ui import icon_res
from config.ui_config import CONFIG as C

from ui.tabs.translation import runner


def build_translate_button(parent, **ctx):
    """开始翻译按钮，返回 QPushButton；clicked 触发 runner.run_translation(page)。

    ctx 需含 page（TabTranslation），用于登记 translate_btn 并连接翻译执行。
    """
    page = ctx["page"]

    btn = QPushButton("开始翻译", parent)
    btn.setObjectName("convertBtn")
    btn.setIcon(icon_res.colored_icon("globe"))
    btn.setIconSize(QSize(C.size("icon_card"), C.size("icon_card")))
    btn.setMinimumHeight(C.size("cta_h"))
    btn.clicked.connect(lambda: runner.run_translation(page))

    page.translate_btn = btn
    return btn