"""
OCTools/core/engines/ocr_engine.py
───────────────────────────────────────────────
OCR 文字识别引擎（图片 / PDF → 文本）—— 核心引擎层

基于 mvp/ocr_paddle.py 的最小示例完善为可复用模块：
  - 与 mvp 保持一致的 PaddleOCR 运行参数（PP-OCRv6_tiny、onnxruntime）
  - 惰性单例初始化（首次调用加载模型，之后复用）
  - 提供 ocr_image / ocr_pil_image / ocr_images / ocr_pdf 入口

依赖（见 requirements.txt）：
  pip install paddleocr onnxruntime

模型缓存目录来自 config/ui_config.json 的 paths.models.paddle_cache，
也可用环境变量 PADDLE_PDX_CACHE_HOME 覆盖。
"""

import os
import tempfile
import shutil
import threading

from config.ui_config import CONFIG as _C

# ════════════════════════════════════════════
#  运行环境（须在 import paddleocr 之前设置）
# ════════════════════════════════════════════

# 本机模型缓存目录（用户可通过环境变量覆盖）
_PADDLE_CACHE = _C.model_path("paddle_cache")

if not os.environ.get("PADDLE_PDX_CACHE_HOME"):
    if _PADDLE_CACHE and os.path.isdir(_PADDLE_CACHE):
        os.environ["PADDLE_PDX_CACHE_HOME"] = _PADDLE_CACHE

os.environ.setdefault("FLAGS_use_mkldnn", "false")
os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "true")

# 可 OCR 的图片扩展名
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".tiff", ".heic")


# ════════════════════════════════════════════
#  单例
# ════════════════════════════════════════════

_OCR = None
_OCR_FAILED = None  # 记录初始化失败原因，避免反复尝试
_OCR_LOCK = threading.Lock()  # 防止多线程同时初始化


def get_ocr():
    """惰性创建 PaddleOCR 实例（与 mvp/ocr_paddle.py 相同的参数），线程安全"""
    global _OCR, _OCR_FAILED
    if _OCR is not None:
        return _OCR
    if _OCR_FAILED is not None:
        raise _OCR_FAILED
    with _OCR_LOCK:
        if _OCR is not None:   # 双重检查：等待锁期间可能已被其他线程初始化
            return _OCR
        if _OCR_FAILED is not None:
            raise _OCR_FAILED
        try:
            from paddleocr import PaddleOCR
            _OCR = PaddleOCR(
                text_detection_model_name="PP-OCRv6_tiny_det",
                text_recognition_model_name="PP-OCRv6_tiny_rec",
                engine="onnxruntime",
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
            )
            return _OCR
        except Exception as e:
            _OCR_FAILED = RuntimeError(
                f"OCR 初始化失败（请确认已安装 paddleocr / onnxruntime）: {e}")
            raise _OCR_FAILED


def warmup_ocr() -> bool:
    """后台预热：提前加载 OCR 模型（屏幕实时翻译等场景可显著减少首次等待）"""
    try:
        get_ocr()
        return True
    except Exception:
        return False


# ════════════════════════════════════════════
#  识别入口
# ════════════════════════════════════════════

def ocr_image(image_path: str) -> str:
    """识别单张图片，返回识别出的文本（每行一条识别结果）"""
    ocr = get_ocr()
    result = ocr.predict(image_path)
    lines = []
    for res in result:
        if not isinstance(res, dict):
            continue
        for t in res.get("rec_texts", []):
            if t and str(t).strip():
                lines.append(str(t).strip())
    return "\n".join(lines)


def ocr_pil_image(pil) -> str:
    """识别内存中的 PIL 图片（屏幕截图等），返回识别出的文本。

    与 ocr_image 相同的结果格式，但无需把截图写到磁盘。
    """
    import numpy as np
    ocr = get_ocr()
    img = pil.convert("RGB")
    result = ocr.predict(np.array(img))
    lines = []
    for res in result:
        if not isinstance(res, dict):
            continue
        for t in res.get("rec_texts", []):
            if t and str(t).strip():
                lines.append(str(t).strip())
    return "\n".join(lines)


def ocr_images(image_paths) -> str:
    """识别多张图片，按顺序拼接（每张之间空一行）"""
    parts = []
    for p in image_paths:
        parts.append(ocr_image(p))
    return "\n\n".join(parts).strip()


def ocr_pdf(pdf_path: str, log=lambda m: print(m)) -> str:
    """识别 PDF：先把每页渲染为图片，再逐页 OCR，返回拼接文本"""
    pages = _render_pdf_pages(pdf_path, log)
    if not pages:
        log("❌ 无法渲染 PDF 页面（缺少 pypdfium2 等渲染依赖）")
        return ""
    try:
        parts = []
        for i, pg in enumerate(pages):
            log(f"   🔍 OCR 第 {i + 1}/{len(pages)} 页")
            try:
                parts.append(ocr_image(pg))
            except Exception as e:
                log(f"   ⚠ 第 {i + 1} 页 OCR 失败: {e}")
        return "\n\n".join(parts).strip()
    finally:
        # 清理渲染出的临时页面图片
        cleanup_temp_dir(os.path.dirname(pages[0]))


def _render_pdf_pages(pdf_path: str, log):
    """把 PDF 每页渲染为临时 PNG，返回文件列表（渲染后由调用方清理目录）"""
    tmp_dir = tempfile.mkdtemp(prefix="pdf_ocr_")
    generated = []
    try:
        import pypdfium2 as pdfium
        pdf = pdfium.PdfDocument(pdf_path)
        try:
            n_pages = len(pdf)
            for i in range(n_pages):
                bitmap = pdf[i].render(scale=200 / 72.0)  # 200 DPI
                pil = bitmap.to_pil()
                p = os.path.join(tmp_dir, f"page_{i + 1:03d}.png")
                pil.save(p, "PNG")
                generated.append(p)
        finally:
            pdf.close()
    except Exception as e:
        log(f"⚠ pypdfium2 渲染失败: {e}")
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return []
    return generated


def cleanup_temp_dir(tmp_dir: str):
    """清理临时目录（渲染 PDF 页面后调用）"""
    if tmp_dir:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ════════════════════════════════════════════
#  自测
# ════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        path = sys.argv[1]
        print(ocr_image(path) if os.path.isfile(path) else "参数应为图片路径")
    else:
        print("用法: python core/engines/ocr_engine.py <image.png>")
