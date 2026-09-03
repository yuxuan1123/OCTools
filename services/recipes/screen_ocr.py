"""
octool/services/recipes/screen_ocr.py
─────────────────────────────────────────
拼接配方 · 屏幕 OCR = 截图 + 图像识别

纯逻辑拼接，不可增减功能：
  1. 截图（core/engines/screenshot）按屏幕坐标区域抓取图像
  2. 图像识别（core/engines/ocr_engine）把图像转换为文本

输出：识别文本 str（OCR 失败返回空串，不抛异常）。
注意：截图依赖 Qt GUI 线程；OCR 较慢（首次加载模型约 20 秒），
慢操作应交给调用方的工作线程执行，本函数自身是阻塞的。
"""

from core.engines.ocr_engine import ocr_pil_image
from services.recipes.common import capture_excluded


def screen_ocr(rect, exclude_widgets=None) -> str:
    """截图指定区域 → OCR 识别 → 返回文本

    参数：
      rect            屏幕坐标区域（QRect 或 (x, y, w, h)）
      exclude_widgets 截图前需临时隐藏的窗口（悬浮框 / 区域框等）
    """
    try:
        img = capture_excluded(exclude_widgets, rect)
    except Exception:
        return ""
    try:
        return (ocr_pil_image(img) or "").strip()
    except Exception:
        return ""