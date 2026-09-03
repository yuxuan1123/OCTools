"""
OCTools/services/recipes/auto_region_capture.py
──────────────────────────────────────────────────
拼接配方 · 自动区域截图 = 截图 + 定时器（实时）

纯逻辑拼接，不可增减功能：
  1. 定时器（ui/ui_component/timer）按固定间隔触发
  2. 截图（core/engines/screenshot_engine）抓取用户选择的屏幕区域

输出：每帧发出 frame(QRect, PIL Image)。
运行中可随时 set_region 修改识别范围（用户拖动/缩放区域框时调用）。
截图依赖 Qt GUI 线程，本组件设计在主线程使用。
"""

from PySide6.QtCore import QObject, QRect, Signal

from ui.ui_component.timer import TimerComponent
from services.recipes.common import capture_excluded


class AutoRegionCapture(QObject):
    """定时截取指定区域（区域可运行中修改）"""

    frame = Signal(object, object)   # QRect（本帧生效区域）, PIL Image

    def __init__(self, interval_ms: int = 1000, exclude_widgets=None, parent=None):
        super().__init__(parent)
        self._region = QRect()
        self._exclude = list(exclude_widgets or [])
        self._timer = TimerComponent(interval_ms=interval_ms, on_tick=self.capture_now)

    # ── 控制 ──

    def set_region(self, rect):
        """设置/修改截图区域（运行中调用实时生效）"""
        self._region = QRect(rect)

    def region(self) -> QRect:
        return QRect(self._region)

    def set_exclude_widgets(self, widgets):
        """设置截图前需临时隐藏的窗口（悬浮框 / 区域框等）"""
        self._exclude = list(widgets or [])

    def set_interval(self, ms: int):
        self._timer.set_interval(ms)

    def interval(self) -> int:
        return self._timer.interval()

    def start(self, region=None):
        """启动定时截图；region 缺省使用当前区域"""
        if region is not None:
            self.set_region(region)
        if self._region.isNull() or self._region.isEmpty():
            raise ValueError("自动区域截图需要先设置截图区域")
        self._timer.start()

    def stop(self):
        """停止定时截图（区域与隐藏窗口列表保留）"""
        self._timer.stop()

    @property
    def is_running(self) -> bool:
        return self._timer.is_running

    # ── 触发 ──

    def capture_now(self):
        """立即截取一帧（手动翻译 / 首帧立即输出）"""
        if self._region.isNull() or self._region.isEmpty():
            return
        rect = QRect(self._region)
        try:
            img = capture_excluded(self._exclude, rect)
        except Exception:
            return
        self.frame.emit(rect, img)


# 便捷函数：单帧截图（可独立于定时器使用）
def capture_frame(rect, exclude_widgets=None):
    """截取指定区域返回 PIL Image（截图失败返回 None）"""
    try:
        return capture_excluded(exclude_widgets, rect)
    except Exception:
        return None