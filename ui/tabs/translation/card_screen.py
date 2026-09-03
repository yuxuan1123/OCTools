"""
OCTools/ui/tabs/translation/card_screen.py
────────────────────────────────────────────────────
屏幕翻译卡片：标题「屏幕翻译」+ 屏幕OCR / 屏幕翻译 / 屏幕实时翻译 三个应用行。

应用行由 app_hooks.build_app_rows 生成（启动/停止 切换按钮 + 名称 + 说明 + 状态）。
"""

from PySide6.QtWidgets import QWidget

from ui.tabs.tab_component.card_widgets import make_card, make_title_row
from ui.tabs.translation import app_hooks
from ui.tabs.translation.registry import _SCREEN_APP_CARD


def build_screen_card(parent, **ctx):
    """屏幕翻译卡片，返回 QFrame。

    ctx 需含 page（TabTranslation）；keys 可选（默认 _SCREEN_APP_CARD）。
    """
    page = ctx["page"]
    keys = ctx.get("keys", _SCREEN_APP_CARD)

    card, csr = make_card(parent)
    make_title_row(card, "live", "屏幕翻译", csr)

    # 应用行：屏幕OCR / 屏幕翻译 / 屏幕实时翻译（启动/停止 切换）
    for _key, row in app_hooks.build_app_rows(card, keys, page):
        csr.addWidget(row)

    return card