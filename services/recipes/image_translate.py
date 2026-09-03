"""
octool/services/recipes/image_translate.py
──────────────────────────────────────────────
拼接配方 · 图翻译 = 图像识别 + 文字翻译

纯逻辑拼接，不可增减功能：
  1. 图像识别（core/engines/ocr_engine）把图像转换为文本
  2. 文字翻译（core/engines/translation_engine）翻译 OCR 文本

输出：识别文本 + 译文 (orig, trans)。
图翻译不包含截图（截图属于原子能力，由调用方决定来源）；
慢操作（识别/翻译）应交给调用方的工作线程执行。
"""

from core.engines.ocr_engine import ocr_pil_image, ocr_image
from core.engines.translation_engine import translate


def recognize(image) -> str:
    """仅识别一张图像（图翻译配方中的识别步骤），返回识别文本；失败返回空串"""
    try:
        return (ocr_pil_image(image) or "").strip()
    except Exception:
        return ""


def recognize_translate(image, direction: str = "auto", log=None, config=None):
    """识别一张图像并翻译，返回 (识别文本, 译文)

    识别为空时不翻译（译文为空串）。任一环节失败返回 ("", "")。
    """
    text = recognize(image)
    if not text:
        return "", ""
    try:
        trans = translate(text, direction, log=log, config=config) or ""
    except Exception:
        trans = ""
    return text, trans


def recognize_translate_file(image_path: str, direction: str = "auto",
                             log=None, config=None):
    """识别一个本地图片文件并翻译，返回 (识别文本, 译文)"""
    try:
        text = (ocr_image(image_path) or "").strip()
    except Exception:
        return "", ""
    if not text:
        return "", ""
    try:
        trans = translate(text, direction, log=log, config=config) or ""
    except Exception:
        trans = ""
    return text, trans