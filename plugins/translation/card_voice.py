"""
OCTools/ui/tabs/translation/card_voice.py
────────────────────────────────────────────────────
语音翻译卡片：标题「语音翻译」+ 屏幕字幕 / 语音翻译 两个应用行 + 底部字幕设置提示。

点击「启动」时 app_controller 会先最小化主窗口（window_ctl.minimize_host），
让悬浮字幕独占视野；主窗口不自动恢复。
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel

from config.ui_config import CONFIG as C

from ui.tabs.tab_component.card_widgets import make_card, make_title_row
from plugins.translation import app_hooks
from plugins.translation.registry import _VOICE_APP_CARD


def build_voice_card(parent, **ctx):
    """语音翻译卡片，返回 QFrame。

    ctx 需含 page（TabTranslation）；keys 可选（默认 _VOICE_APP_CARD）。
    """
    page = ctx["page"]
    keys = ctx.get("keys", _VOICE_APP_CARD)

    card, cv = make_card(parent)
    make_title_row(card, "audio", "语音翻译", cv, hint="识别电脑内置声音")

    # 应用行：屏幕字幕 / 语音翻译（启动/停止 切换）
    for _key, row in app_hooks.build_app_rows(card, keys, page):
        cv.addWidget(row)

    # 提示行：字幕设置入口
    voice_hint_row = QWidget(card)
    vh_lay = QHBoxLayout(voice_hint_row)
    vh_lay.setContentsMargins(0, 0, 0, 0)
    vh_lay.setSpacing(C.size("header_row_spacing"))
    voice_hint = QLabel("可在「设置 → 翻译」中独立设置语音字幕背景与是否显示原文", voice_hint_row)
    voice_hint.setObjectName("hint")
    vh_lay.addWidget(voice_hint)
    vh_lay.addStretch(1)
    cv.addWidget(voice_hint_row)

    return card