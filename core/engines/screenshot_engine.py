"""
octool/core/engines/screenshot_engine.py
───────────────────────────────────────────────
截图引擎 · 屏幕区域 → PIL Image —— 核心引擎层（原子能力）

与其他引擎完全独立，仅关注自身的输入与输出：
  输入：屏幕坐标区域 rect（QRect 或 (x, y, w, h)）
  输出：PIL Image（RGB）

使用注意：
  - 桌面抓屏必须运行在 Qt GUI 线程（存在 QGuiApplication）。
  - 截取前调用方应临时隐藏会被拍进图里的窗口（悬浮框 / 区域框等），
    再等待 CAPTURE_EXCLUDE_DELAY 秒让桌面合成器刷新，避免循环拍摄。
"""

from PIL import Image
import numpy as np

from PySide6.QtCore import QRect
from PySide6.QtGui import QGuiApplication, QImage

# 截屏前隐藏悬浮窗后，等待桌面合成器刷新，避免把悬浮窗拍进截图（秒）
CAPTURE_EXCLUDE_DELAY = 0.06


def _as_qrect(rect) -> QRect:
    """兼容 QRect / (x, y, w, h) 两种区域传入"""
    if isinstance(rect, QRect):
        return rect
    x, y, w, h = rect
    return QRect(int(x), int(y), int(w), int(h))


def qimage_to_pil(qimg: QImage) -> Image.Image:
    """QImage → PIL Image（RGB）

    兼容不同 PySide6 版本：旧版 QImage.bits() 返回 sip.voidptr（需 setsize），
    新版返回 memoryview（长度已正确）。
    """
    qimg = qimg.convertToFormat(QImage.Format.Format_RGB888)
    w, h = qimg.width(), qimg.height()
    if w <= 0 or h <= 0:
        return Image.new("RGB", (1, 1), (0, 0, 0))
    ptr = qimg.bits()
    if hasattr(ptr, "setsize"):            # 旧版 PySide6：sip.voidptr
        ptr.setsize(h * qimg.bytesPerLine())
    arr = np.frombuffer(ptr, np.uint8).reshape((h, qimg.bytesPerLine()))
    arr = arr[:, : w * 3].reshape((h, w, 3))
    return Image.fromarray(arr)


def grab_region(rect) -> Image.Image:
    """截取屏幕坐标 rect 区域的图像，返回 PIL Image。

    支持多显示器：按 rect 中心所在屏幕抓取，并做坐标偏移。
    """
    rect = _as_qrect(rect)
    screen = QGuiApplication.screenAt(rect.center()) or QGuiApplication.primaryScreen()
    geo = screen.geometry()
    local = QRect(rect.x() - geo.x(), rect.y() - geo.y(),
                  rect.width(), rect.height())
    pix = screen.grabWindow(0, local.x(), local.y(), local.width(), local.height())
    return qimage_to_pil(pix.toImage())


def grab_fullscreen() -> Image.Image:
    """截取主屏幕完整图像，返回 PIL Image"""
    screen = QGuiApplication.primaryScreen()
    if screen is None:
        return Image.new("RGB", (1, 1), (0, 0, 0))
    geo = screen.geometry()
    pix = screen.grabWindow(0, geo.x(), geo.y(), geo.width(), geo.height())
    return qimage_to_pil(pix.toImage())


def screen_rect() -> QRect:
    """主屏幕几何（QRect），供区域框选 / 全屏遮罩定位使用"""
    screen = QGuiApplication.primaryScreen()
    if screen is None:
        return QRect(0, 0, 1920, 1080)
    return screen.geometry()