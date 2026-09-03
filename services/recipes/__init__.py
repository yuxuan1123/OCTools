"""
octool/services/recipes/__init__.py
──────────────────────────────────
拼接配方层：纯逻辑组合 原子能力引擎（core/engines）与 通用组件
（services/components），不可增减功能。

配方：
  1. 屏幕OCR         = 截图 + 图像识别
  2. 图翻译           = 图像识别 + 文字翻译
  3. 一次性屏幕翻译    = 截图 + 图翻译
  4. 内置语音识别      = 录音 + 语音识别
  5. 实时语音翻译      = 录音 + 语音识别 + 文字翻译
  6. 自动区域截图      = 截图 + 定时器（实时）

本层不含任何 UI 控件；慢操作（OCR / 翻译 / 语音识别）需由调用方
放在工作线程执行，本层提供的是纯逻辑拼接接口。
"""

from services.recipes import (
    auto_region_capture,
    builtin_speech_recognize,
    image_translate,
    one_shot_screen_translate,
    realtime_speech_translate,
    screen_ocr,
)

__all__ = [
    "screen_ocr",
    "image_translate",
    "one_shot_screen_translate",
    "builtin_speech_recognize",
    "realtime_speech_translate",
    "auto_region_capture",
]