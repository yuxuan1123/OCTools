"""
OCTools/ui/tabs/conversion/button_convert.py
────────────────────────────────────────────
「开始转换」主按钮：objectName convertBtn，图标 transfer，高度 cta_h。
"""

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QPushButton

from ui import icon_res
from config.ui_config import CONFIG as C

from ui.tabs.conversion import runner


def build_convert_button(parent, **ctx):
    """开始转换按钮，返回 QPushButton；clicked 触发 runner.run_conversion(page)。

    ctx 需含 page（TabConversion），用于登记 convert_btn。
    """
    page = ctx["page"]

    btn = QPushButton("开始转换", parent)
    btn.setObjectName("convertBtn")
    btn.setIcon(icon_res.colored_icon("transfer"))
    btn.setIconSize(QSize(C.size("icon_large"), C.size("icon_large")))
    btn.setMinimumHeight(C.size("cta_h"))
    btn.clicked.connect(lambda: runner.run_conversion(page))

    page.convert_btn = btn
    return btn
