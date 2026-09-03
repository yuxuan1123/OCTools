"""
octool/services/recipes/one_shot_screen_translate.py
────────────────────────────────────────────────────────
拼接配方 · 一次性屏幕翻译 = 截图 + 图翻译

纯逻辑拼接，不可增减功能：
  1. 截图（core/engines/screenshot）按屏幕坐标区域抓取图像
  2. 图翻译（image_translate = 图像识别 + 文字翻译）

输出：识别文本 + 译文 (orig, trans)。
截图依赖 Qt GUI 线程；慢操作（识别/翻译）由调用方的工作线程执行。
"""

from services.recipes.common import capture_excluded
from services.recipes.image_translate import recognize_translate


def screen_translate_once(rect, direction: str = "auto", exclude_widgets=None,
                          log=None, config=None):
    """截取区域 → OCR → 翻译，返回 (识别文本, 译文)"""
    try:
        img = capture_excluded(exclude_widgets, rect)
    except Exception:
        return "", ""
    return recognize_translate(img, direction, log=log, config=config)