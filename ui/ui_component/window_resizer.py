"""
window_resizer.py
====================
为无边框窗口（Qt.FramelessWindowHint）提供**边缘 / 角落拖拽缩放**能力，
并将鼠标悬停在对应区域时**即时切换为方向拉伸光标**。

光标可靠性的关键修复点：
  - 目标窗口开启鼠标跟踪（setMouseTracking(True)），使未按下时也能收到
    HoverMove，从而在边缘区域即时切换为拉伸光标。
  - 但当鼠标位于**子部件**（分栏/标题栏/文本等）或半透明窗口上时，子部件
    不产生 hover 事件，窗口收不到移动事件，拉伸光标会"卡住"不恢复。
    因此组件内部用轻量 QTimer 轮询全局光标位置（QCursor.pos），直接按
    命中测试刷新光标，保证从边缘移入内部/离开窗口时光标一定恢复。

用法（在业务窗口中一行接入）::

    from window_resizer import attach_resizer
    self.resizer = attach_resizer(self, margin=6, min_width=600, min_height=400)

也可脱离业务单独运行本文件查看效果::

    python window_resizer.py
"""
from __future__ import annotations

from PySide6.QtCore import QEvent, QPoint, Qt, QRect, QTimer
from PySide6.QtGui import QGuiApplication, QCursor
from PySide6.QtWidgets import QWidget


# 8 个拉伸区域标识
class Edge:
    NONE = 0
    LEFT = 1
    RIGHT = 2
    TOP = 4
    BOTTOM = 8
    # 组合即代表四个角
    TOP_LEFT = TOP | LEFT
    TOP_RIGHT = TOP | RIGHT
    BOTTOM_LEFT = BOTTOM | LEFT
    BOTTOM_RIGHT = BOTTOM | RIGHT


# 区域 -> 对应 Qt 光标形状
EDGE_CURSOR = {
    Edge.LEFT: Qt.SizeHorCursor,
    Edge.RIGHT: Qt.SizeHorCursor,
    Edge.TOP: Qt.SizeVerCursor,
    Edge.BOTTOM: Qt.SizeVerCursor,
    Edge.TOP_LEFT: Qt.SizeFDiagCursor,
    Edge.BOTTOM_RIGHT: Qt.SizeFDiagCursor,
    Edge.TOP_RIGHT: Qt.SizeBDiagCursor,
    Edge.BOTTOM_LEFT: Qt.SizeBDiagCursor,
}


def _hit_test(pos: QPoint, rect: QRect, margin: int) -> int:
    """根据鼠标位置命中测试，返回 Edge 组合值。"""
    x, y = pos.x(), pos.y()
    w, h = rect.width(), rect.height()
    if w <= 0 or h <= 0:
        return Edge.NONE

    on_left = x <= margin
    on_right = x >= w - margin
    on_top = y <= margin
    on_bottom = y >= h - margin

    # 角落优先于单边
    if on_left and on_top:
        return Edge.TOP_LEFT
    if on_right and on_top:
        return Edge.TOP_RIGHT
    if on_left and on_bottom:
        return Edge.BOTTOM_LEFT
    if on_right and on_bottom:
        return Edge.BOTTOM_RIGHT
    if on_left:
        return Edge.LEFT
    if on_right:
        return Edge.RIGHT
    if on_top:
        return Edge.TOP
    if on_bottom:
        return Edge.BOTTOM
    return Edge.NONE


class WindowResizer(QWidget):
    """无边框窗口边缘/角落拖拽缩放辅助器（独立可复用组件）。

    设计要点：
    * 以事件过滤器方式挂到目标窗口，不侵入其类继承体系；
    * 主动开启目标窗口的鼠标跟踪（setMouseTracking(True)），使未按下时
      的鼠标移动也能触发 HoverMove，从而实时更新拉伸光标；
    * 按下后记录起始几何与起始鼠标位置，移动时按命中区域计算新 geometry；
      释放后恢复箭头光标并重新进入"悬停判定"模式。
    """

    def __init__(self, window: QWidget, margin: int = 6,
                 min_width: int = 200, min_height: int = 150):
        super().__init__(window)
        if not isinstance(window, QWidget):
            raise TypeError("WindowResizer: window 必须是 QWidget 实例")
        self._win = window
        self._margin = max(1, int(margin))
        self._min_w = max(1, int(min_width))
        self._min_h = max(1, int(min_height))

        self._resizing = False
        self._edge = Edge.NONE
        self._start_geo = None
        self._start_pos = None
        self._enabled = True          # 是否允许缩放（如「固定」时禁用）

        # 关键：开启鼠标跟踪，确保未按下时也能收到鼠标移动事件，
        # 从而在边缘区域即时切换为拉伸光标。
        self._win.setMouseTracking(True)
        self._win.installEventFilter(self)

        # 光标轮询：鼠标位于子部件/半透明区域上时窗口收不到 HoverMove，
        # 仅靠事件更新光标会"卡住"不恢复。用轻量 QTimer 轮询全局光标位置，
        # 直接按命中测试刷新拉伸光标，保证任何位置都即时切换/恢复。
        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(20)   # ms，约 50Hz，足够跟手
        self._poll_timer.timeout.connect(self._poll_cursor)
        self._poll_timer.start()

    # ---------------------------------------------------------- #
    # 光标轮询（修复：从边缘移入内部/离开窗口时拉伸光标卡住不恢复）
    # ---------------------------------------------------------- #
    def _poll_cursor(self):
        if not self._enabled or self._resizing:
            return
        win = self._win
        if not win.isVisible():
            return
        local = win.mapFromGlobal(QCursor.pos())
        if not win.rect().contains(local):
            # 鼠标已移出窗口：恢复默认箭头，避免离开后仍残留拉伸光标
            win.setCursor(Qt.ArrowCursor)
            return
        edge = _hit_test(local, win.rect(), self._margin)
        win.setCursor(EDGE_CURSOR.get(edge, Qt.ArrowCursor))

    # ---------------------------------------------------------- #
    # 事件过滤
    # ---------------------------------------------------------- #
    def eventFilter(self, obj, event):  # noqa: N802 (Qt 命名)
        if obj is not self._win:
            return super().eventFilter(obj, event)

        et = event.type()

        # 鼠标移动：未按下时更新光标；按下时执行缩放
        if et == QEvent.HoverMove or et == QEvent.MouseMove:
            return self._on_move(event)

        if et == QEvent.MouseButtonPress:
            return self._on_press(event)

        if et == QEvent.MouseButtonRelease:
            return self._on_release(event)

        # 鼠标离开窗口：恢复默认箭头光标
        if et == QEvent.Leave:
            self._win.setCursor(Qt.ArrowCursor)
            return False

        return False

    # ---------------------------------------------------------- #
    # 鼠标处理
    # ---------------------------------------------------------- #
    def _on_move(self, event):
        if not self._enabled:
            return False
        pos = event.position().toPoint() if hasattr(event, "position") else event.pos()
        rect = self._win.rect()

        if self._resizing:
            self._do_resize(pos)
            return True

        # 未按下：根据命中区域设置对应拉伸光标
        edge = _hit_test(pos, rect, self._margin)
        if edge != Edge.NONE:
            self._win.setCursor(EDGE_CURSOR[edge])
        else:
            self._win.setCursor(Qt.ArrowCursor)
        return False

    def _on_press(self, event):
        if not self._enabled or event.button() != Qt.LeftButton:
            return False
        pos = event.position().toPoint() if hasattr(event, "position") else event.pos()
        edge = _hit_test(pos, self._win.rect(), self._margin)
        if edge == Edge.NONE:
            return False
        self._resizing = True
        self._edge = edge
        self._start_geo = self._win.geometry()
        self._start_pos = event.globalPosition().toPoint() if hasattr(event, "globalPosition") else event.globalPos()
        # 按下后锁定光标为当前方向光标
        self._win.setCursor(EDGE_CURSOR.get(edge, Qt.ArrowCursor))
        return True

    def _on_release(self, event):
        if event.button() != Qt.LeftButton or not self._resizing:
            return False
        self._resizing = False
        self._edge = Edge.NONE
        self._start_geo = None
        self._start_pos = None
        # 恢复为"悬停判定"模式的光标
        self._win.setCursor(Qt.ArrowCursor)
        return True

    # ---------------------------------------------------------- #
    # 缩放计算
    # ---------------------------------------------------------- #
    def _do_resize(self, local_pos: QPoint):
        if self._start_geo is None or self._start_pos is None:
            return
        cur_global = QCursor_global()
        delta = cur_global - self._start_pos
        dx, dy = delta.x(), delta.y()

        geo = QRect(self._start_geo)
        edge = self._edge

        if edge & Edge.RIGHT:
            geo.setRight(self._start_geo.right() + dx)
        if edge & Edge.BOTTOM:
            geo.setBottom(self._start_geo.bottom() + dy)
        if edge & Edge.LEFT:
            new_left = self._start_geo.left() + dx
            if self._start_geo.right() - new_left >= self._min_w:
                geo.setLeft(new_left)
            else:
                geo.setLeft(self._start_geo.right() - self._min_w)
        if edge & Edge.TOP:
            new_top = self._start_geo.top() + dy
            if self._start_geo.bottom() - new_top >= self._min_h:
                geo.setTop(new_top)
            else:
                geo.setTop(self._start_geo.bottom() - self._min_h)

        # 兜底：保证不小于最小尺寸
        if geo.width() < self._min_w:
            if edge & Edge.LEFT:
                geo.setLeft(geo.right() - self._min_w)
            else:
                geo.setRight(geo.left() + self._min_w)
        if geo.height() < self._min_h:
            if edge & Edge.TOP:
                geo.setTop(geo.bottom() - self._min_h)
            else:
                geo.setBottom(geo.top() + self._min_h)

        self._win.setGeometry(geo)

    # ---------------------------------------------------------- #
    # 公共 API
    # ---------------------------------------------------------- #
    def set_margin(self, margin: int):
        self._margin = max(1, int(margin))

    def set_minimum_size(self, min_width: int, min_height: int):
        self._min_w = max(1, int(min_width))
        self._min_h = max(1, int(min_height))

    def set_enabled(self, enabled: bool):
        """启用 / 禁用边缘缩放（如「固定」时禁用，恢复为默认箭头光标）。

        >>> resizer.set_enabled(False)   # 锁定尺寸，禁止边缘拉伸
        >>> resizer.set_enabled(True)    # 恢复边缘拉伸
        """
        self._enabled = bool(enabled)
        if not self._enabled:
            self._resizing = False
            self._edge = Edge.NONE
            self._start_geo = None
            self._start_pos = None
            self._win.setCursor(Qt.ArrowCursor)


def QCursor_global():
    # PySide6 中直接用 QCursor.pos() 获取全局光标位置
    from PySide6.QtGui import QCursor
    pos = QCursor.pos()
    return QPoint(int(pos.x()), int(pos.y()))


def attach_resizer(window: QWidget, margin: int = 6,
                   min_width: int = 200, min_height: int = 150) -> WindowResizer:
    """便捷接入函数：为目标无边框窗口绑定边缘拉伸能力。

    >>> resizer = attach_resizer(my_window, margin=6, min_width=600, min_height=400)
    """
    return WindowResizer(window, margin=margin,
                         min_width=min_width, min_height=min_height)


# ============================================================ #
# 独立可运行演示：一个无边框窗口，可四边/四角拉伸，边缘悬停即
# 显示对应方向拉伸箭头光标。
# ============================================================ #
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout

    app = QApplication([])

    win = QWidget()
    win.setWindowTitle("WindowResizer 演示")
    win.setWindowFlags(win.windowFlags() | Qt.FramelessWindowHint)
    win.resize(700, 450)
    win.setStyleSheet("background:#F3F5F9;")

    layout = QVBoxLayout(win)
    layout.setContentsMargins(20, 20, 20, 20)
    label = QLabel("无边框窗口\n\n将鼠标移到窗口边缘/角落，\n应即时显示对应方向的拉伸箭头光标；\n按下并拖动即可缩放窗口。")
    label.setAlignment(Qt.AlignCenter)
    layout.addWidget(label)

    attach_resizer(win, margin=6, min_width=300, min_height=200)
    win.show()
    app.exec()
