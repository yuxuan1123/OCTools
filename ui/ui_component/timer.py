"""
OCTools/ui/ui_component/timer.py
───────────────────────────
可拓展业务层 · 定时器

通用周期定时器组件（基于 QTimer），供各拼接功能 / 应用循环使用：
  - 间隔毫秒可通过参数给出（默认 1000ms）
  - start / stop / set_interval 随时可切换
  - 每轮触发 on_tick 回调并 emit tick 信号
"""

from PySide6.QtCore import QObject, QTimer, Signal


class TimerComponent(QObject):
    """可复用周期定时器

    用法：
      t = TimerComponent(interval_ms=1000, on_tick=my_tick)
      t.start()  # 开始
      t.stop()   # 停止
      t.set_interval(500)  # 运行中改间隔（自动生效）
    """

    tick = Signal()

    def __init__(self, interval_ms: int = 1000, on_tick=None, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._interval_ms = max(50, int(interval_ms))
        self._timer.setInterval(self._interval_ms)
        self._timer.timeout.connect(self._on_timeout)
        self._on_tick = on_tick

    # ── 控制 ──

    def start(self):
        """启动定时器；若已运行则重置计数"""
        if not self._timer.isActive():
            self._timer.start()

    def stop(self):
        """停止定时器"""
        self._timer.stop()

    def restart(self):
        """立即重启（停止并清零间隔计数）"""
        self._timer.stop()
        self._timer.start()

    @property
    def is_running(self) -> bool:
        return self._timer.isActive()

    # ── 间隔 ──

    def set_interval(self, ms: int):
        """设置间隔（毫秒）；运行中调用会自动生效"""
        self._interval_ms = max(50, int(ms))
        self._timer.setInterval(self._interval_ms)

    def interval(self) -> int:
        return self._interval_ms

    # ── 内部 ──

    def _on_timeout(self):
        if self._on_tick is not None:
            self._on_tick()
        self.tick.emit()