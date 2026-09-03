"""
octool/ui/tabs/translation/registry.py
────────────────────────────────────────────────
翻译页的常量注册表与共享引用：
  - _APP_ROWS          最终应用注册表（key → 应用类 / 行标签 / 图标 / 提示 / 热键属性）
  - _SCREEN_APP_CARD   屏幕翻译卡片内的应用顺序
  - _VOICE_APP_CARD    语音翻译卡片内的应用顺序
  - TRANSLATOR / TR_ENGINE_LABELS / TR_ENGINE_ORDER  （原文写在文件顶部的翻译引擎常量引用）
"""

from core.engines import translation_engine as TRANSLATOR
from config.translator_config import (
    TranslatorConfig, ENGINE_LABELS as TR_ENGINE_LABELS,
    ENGINE_ORDER as TR_ENGINE_ORDER,
)

from ui.tabs.translation.apps import (
    ScreenOcrApp,
    OneShotScreenTranslateApp,
    RealtimeScreenTranslateApp,
    ScreenSubtitleApp,
    SpeechTranslateApp,
)


# ── 最终应用注册表：key → (应用类, 行标签, 启动图标, 行提示, 热键配置属性或 None) ──
_APP_ROWS = {
    "screen_ocr":       (ScreenOcrApp,              "屏幕OCR",        "scan",       "截图识别为文字", None),
    "one_shot":         (OneShotScreenTranslateApp, "屏幕翻译",       "bolt",       "截图识别并翻译（单次）", "hotkey_ocr_once"),
    "realtime":         (RealtimeScreenTranslateApp, "屏幕实时翻译",  "bulb",       "定时截图并翻译", "hotkey_ocr_live"),
    "subtitle":         (ScreenSubtitleApp,         "屏幕字幕",       "microphone", "识别系统内置声音为字幕", None),
    "speech_translate": (SpeechTranslateApp,        "语音翻译",       "music",      "系统声音识别并翻译为中文", None),
}

# 各卡片内的应用顺序（卡片标题沿用旧布局：屏幕翻译 / 语音翻译）
_SCREEN_APP_CARD = ["screen_ocr", "one_shot", "realtime"]
_VOICE_APP_CARD = ["subtitle", "speech_translate"]