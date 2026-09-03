"""
octool/ui/tabs/translation/apps/__init__.py
──────────────────────────────────────────
最终应用层：拼接配方（services/recipes）+ 悬浮显示框（services/components）
挂载为 UI 可启动的成品应用。

每个应用 = 拼接配方 + 悬浮显示框（services/components/overlay）
                 + 区域框选（services/components/region_box，按需）

导出：
  - TranslateAppBase                 公共基类
  - ScreenOcrApp                     屏幕OCR应用（重复执行 / 复制 / 关闭）
  - OneShotScreenTranslateApp        一次性屏幕翻译应用（双语 / 重复执行 / 复制 / 关闭）
  - RealtimeScreenTranslateApp       屏幕实时翻译应用（双语 / 暂停 / 手动 / 复制 / 关闭）
  - ScreenSubtitleApp                屏幕字幕（暂停 / 复制 / 关闭）
  - SpeechTranslateApp               语音翻译应用（双语 / 暂停 / 复制 / 关闭）
"""

from .app_base import TranslateAppBase
from .screen_ocr_app import ScreenOcrApp
from .one_shot_screen_translate_app import OneShotScreenTranslateApp
from .realtime_screen_translate_app import RealtimeScreenTranslateApp
from .screen_subtitle_app import ScreenSubtitleApp
from .speech_translate_app import SpeechTranslateApp

__all__ = [
    "TranslateAppBase",
    "ScreenOcrApp",
    "OneShotScreenTranslateApp",
    "RealtimeScreenTranslateApp",
    "ScreenSubtitleApp",
    "SpeechTranslateApp",
]