"""
octool/ui/ui_component/region_box.py
────────────────────────────────────────────────
可拓展业务层 · 区域框选（UI）

两个独立组件（供最终应用使用）：
  - RegionSelectDialog：全屏遮罩，拖拽框选识别区域（松开后可继续调整，
    双击 / Enter 确认，Esc / 右键取消）
  - LiveRegionBox：任务运行中的「识别区域调整框」，可拖动 / 缩放并实时
    发出 region_changed(QRect)，供定时截图动态修改范围

边框 / 遮罩 / 手柄等全部参数来自 config/ui_config.json
（通过 config.ui_config.CONFIG）。
"""

from PySide6.QtCore import Qt, QRect, QPoint, Signal
from PySide6.QtGui import QCursor, QColor, QGuiApplication, QPainter, QPen
from PySide6.QtWidgets import QDialog, QLabel, QWidget

from config.ui_config import CONFIG as C
from ui.style_hook import StyleHookMixin


class RegionSelectDialog(StyleHookMixin, QDialog):
    """全屏半透明遮罩：拖拽框选区域，松开后 **可继续调整**（拖动移动 /
    拖四角与边缘缩放），双击或 Enter 确认，Esc / 右键取消。

    交互流程：
      1. 按住左键拖拽 → 出现选区框（用户配置的边框颜色）
      2. 松开 → 进入调整模式：框内拖动移动，四角/四边手柄缩放
      3. 双击框内 或 按 Enter → 确认；Esc / 右键 → 取消

    边框高亮颜色可用 border_color 指定（#RRGGBB）。
    """

    MIN_SIZE = C.size("screen_min_size")  # 小于该尺寸视为误触，取消
    _HANDLE = C.size("screen_handle")     # 缩放手柄大小（px）

    def __init__(self, parent=None, border_color: str = None):
        if border_color is None:
            border_color = C.color("screen_border")
        super().__init__(parent,
                         Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # 工具窗口关闭不应退出整个程序
        self.setAttribute(Qt.WA_QuitOnClose, False)
        # 真正透明背景：遮罩半透明绘制在 paintEvent 中
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        screen = QGuiApplication.screenAt(QCursor.pos()) \
            or QGuiApplication.primaryScreen()
        self.setGeometry(screen.geometry())
        self.setCursor(Qt.CrossCursor)
        self.setMouseTracking(True)

        self._start = None      # 拖拽起点（绘制阶段）
        self._current = None    # 当前鼠标位置（绘制阶段）
        self._rect = None       # 调整阶段的有效选区（QRect）
        self._mode = "draw"     # draw=拖拽绘制 / adjust=可调整
        self._drag_action = None    # 调整动作：move / nw / ne / se / sw / n / e / s / w
        self._drag_anchor = None    # move 时的按下点与 rect 左上角偏移
        self.selected_rect = None

        # 边框颜色
        self.border_color = str(border_color or C.color("screen_border"))
        if not self.border_color.startswith("#"):
            self.border_color = "#" + self.border_color

        # 顶部操作提示（参数来自 JSON）
        self._hint = QLabel(C.text("hint_region_select"), self)
        self._hint.adjustSize()
        self._hint.move((self.width() - self._hint.width()) // 2, 24)
        self._hint.raise_()
        self._apply_inline_style()

    def _apply_inline_style(self):
        """主题切换时由 StyleHookMixin 调用：重刷框选提示条配色。"""
        self._hint.setStyleSheet(
            f"background: {C.color('screen_hint_bg')}; color: {C.color('screen_hint_fg')};"
            f"border-radius: {C.size('radius_btn')}px; padding: {C.text('region_hint_padding')};"
            f"font-size: {C.font('body')}px; font-weight: {C.font('checked_weight')};")

    # ── 手柄几何 ──

    def _handles(self, rect) -> list:
        """返回 8 个缩放手柄的 (hit_rect, action) 列表"""
        hs = self._HANDLE
        x0, y0, x1, y1 = rect.left(), rect.top(), rect.right(), rect.bottom()
        cx, cy = rect.center().x(), rect.center().y()
        return [
            (QRect(x0 - hs // 2, y0 - hs // 2, hs, hs), "nw"),
            (QRect(x1 - hs // 2, y0 - hs // 2, hs, hs), "ne"),
            (QRect(x1 - hs // 2, y1 - hs // 2, hs, hs), "se"),
            (QRect(x0 - hs // 2, y1 - hs // 2, hs, hs), "sw"),
            (QRect(cx - hs // 2, y0 - hs // 2, hs, hs), "n"),
            (QRect(x1 - hs // 2, cy - hs // 2, hs, hs), "e"),
            (QRect(cx - hs // 2, y1 - hs // 2, hs, hs), "s"),
            (QRect(x0 - hs // 2, cy - hs // 2, hs, hs), "w"),
        ]

    def _hit_test(self, pos) -> str:
        """返回 pos 命中的动作：缩放手柄 / move / None"""
        if self._rect is None:
            return None
        for hrect, action in self._handles(self._rect):
            if hrect.contains(pos):
                return action
        if self._rect.contains(pos):
            return "move"
        return None

    def _cursor_for(self, action) -> Qt.CursorShape:
        mapping = {
            "nw": Qt.SizeFDiagCursor, "se": Qt.SizeFDiagCursor,
            "ne": Qt.SizeBDiagCursor, "sw": Qt.SizeBDiagCursor,
            "n": Qt.SizeVerCursor, "s": Qt.SizeVerCursor,
            "e": Qt.SizeHorCursor, "w": Qt.SizeHorCursor,
            "move": Qt.SizeAllCursor,
        }
        return mapping.get(action, Qt.CrossCursor)

    # ── 事件 ──

    def mousePressEvent(self, e):
        if e.button() != Qt.LeftButton:
            return
        pos = e.position().toPoint()
        if self._mode == "draw":
            self._start = pos
            self._current = pos
        else:
            action = self._hit_test(pos)
            if action is None:
                return
            self._drag_action = action
            if action == "move":
                self._drag_anchor = (self._rect.topLeft() - pos)
            else:
                self._drag_anchor = (action, pos)
        self.update()

    def mouseMoveEvent(self, e):
        pos = e.position().toPoint()
        if self._mode == "draw" and self._start is not None:
            self._current = pos
            self.update()
            return
        if self._mode == "adjust":
            if self._drag_action is None:
                self.setCursor(self._cursor_for(self._hit_test(pos)))
                return
            self._apply_drag(pos)
            self.update()

    def mouseReleaseEvent(self, e):
        if e.button() != Qt.LeftButton:
            return
        if self._mode == "draw" and self._start is not None:
            rect = self._finalize_rect(self._start, e.position().toPoint())
            self._start = self._current = None
            if rect is None:
                self.reject()
                return
            self._rect = rect
            self._mode = "adjust"
            self.setCursor(Qt.SizeAllCursor)
            self.update()
            return
        if self._mode == "adjust":
            self._drag_action = None
            self._drag_anchor = None

    def mouseDoubleClickEvent(self, e):
        """双击框内 = 确认"""
        if self._mode == "adjust" and self._rect is not None \
                and self._rect.contains(e.position().toPoint()):
            self._confirm()

    def _apply_drag(self, pos):
        """按当前动作应用拖动/缩放"""
        r = QRect(self._rect)
        if self._drag_action == "move":
            r.moveTopLeft(pos + self._drag_anchor)
        else:
            action = self._drag_action
            anchor = self._drag_anchor[1]
            if "n" in action:
                r.setTop(min(pos.y(), r.bottom() - self.MIN_SIZE))
            if "s" in action:
                r.setBottom(max(pos.y(), r.top() + self.MIN_SIZE))
            if "w" in action:
                r.setLeft(min(pos.x(), r.right() - self.MIN_SIZE))
            if "e" in action:
                r.setRight(max(pos.x(), r.left() + self.MIN_SIZE))
        geo = self.rect()
        r = r.intersected(geo)
        if r.width() >= self.MIN_SIZE and r.height() >= self.MIN_SIZE:
            self._rect = r

    def _confirm(self):
        if self._rect is None:
            self.reject()
            return
        self.selected_rect = QRect(self._rect)
        self.accept()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.reject()
        elif e.key() in (Qt.Key_Return, Qt.Key_Enter):
            if self._mode == "adjust":
                self._confirm()
        else:
            super().keyPressEvent(e)

    def paintEvent(self, e):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(C.color("screen_mask")))
        border_q = QColor(self.border_color)
        if not border_q.isValid():
            border_q = QColor(C.color("screen_border"))

        if self._mode == "draw" and self._start is not None and self._current is not None:
            rect = QRect(self._start, self._current).normalized()
            self._paint_selection(p, rect, border_q)
        elif self._mode == "adjust" and self._rect is not None:
            self._paint_selection(p, self._rect, border_q)
            fill_q = QColor(border_q)
            fill_q.setAlpha(C.size("overlay_handle_alpha"))
            p.setBrush(fill_q)
            p.setPen(Qt.NoPen)
            for hrect, _action in self._handles(self._rect):
                p.drawRect(hrect)
            p.setBrush(Qt.NoBrush)
        p.end()

    def _paint_selection(self, p, rect, border_q):
        """画选区：半透明填充 + 边框"""
        fill_q = QColor(border_q)
        fill_q.setAlpha(C.size("overlay_hint_fill_alpha"))
        p.fillRect(rect, fill_q)
        pen = QPen(border_q, 2)
        p.setPen(pen)
        p.drawRect(rect)

    # ── 工具 ──

    @staticmethod
    def _finalize_rect(start: QPoint, end: QPoint):
        """把拖拽起止点归一化为有效 QRect；区域太小返回 None"""
        rect = QRect(start, end).normalized()
        if rect.width() < RegionSelectDialog.MIN_SIZE or \
                rect.height() < RegionSelectDialog.MIN_SIZE:
            return None
        return rect


class LiveRegionBox(QWidget):
    """任务运行中的「识别区域调整框」：置顶透明，框住当前识别区域。

    - 框内拖动 → 移动识别区域
    - 四角/四边手柄 → 缩放识别区域
    - 区域变化时发出 region_changed(QRect)，供上层实时更新截屏区域

    边框颜色来自参数（默认 JSON screen_border）。截屏前由上层临时隐藏。
    """

    region_changed = Signal(object)   # QRect

    _HANDLE = C.size("screen_handle")

    def __init__(self, region_rect, border_color: str = None, parent=None):
        if border_color is None:
            border_color = C.color("screen_border")
        super().__init__(parent,
                         Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setMouseTracking(True)
        self._border = str(border_color or C.color("screen_border"))
        self._drag_action = None
        self._drag_anchor = None
        self.setGeometry(QRect(region_rect))

    def region(self) -> QRect:
        """当前识别区域（窗口几何 = 区域）"""
        g = self.geometry()
        return QRect(g.x(), g.y(), g.width(), g.height())

    # ── 手柄几何（窗口坐标系，手柄中心贴边框内侧）──

    def _handles(self):
        hs = self._HANDLE
        r = self.rect()
        x0, y0 = r.left(), r.top()
        x1, y1 = r.right(), r.bottom()
        cx, cy = r.center().x(), r.center().y()
        ins = hs // 2   # 手柄中心内缩，避免被窗口裁剪
        pts = {
            "nw": (x0 + ins, y0 + ins), "ne": (x1 - ins, y0 + ins),
            "se": (x1 - ins, y1 - ins), "sw": (x0 + ins, y1 - ins),
            "n": (cx, y0 + ins), "s": (cx, y1 - ins),
            "e": (x1 - ins, cy), "w": (x0 + ins, cy),
        }
        return [(QRect(px - hs // 2, py - hs // 2, hs, hs), action)
                for action, (px, py) in pts.items()]

    def _hit_test(self, pos):
        for hrect, action in self._handles():
            if hrect.contains(pos):
                return action
        return "move"

    def _cursor_for(self, action):
        mapping = {
            "nw": Qt.SizeFDiagCursor, "se": Qt.SizeFDiagCursor,
            "ne": Qt.SizeBDiagCursor, "sw": Qt.SizeBDiagCursor,
            "n": Qt.SizeVerCursor, "s": Qt.SizeVerCursor,
            "e": Qt.SizeHorCursor, "w": Qt.SizeHorCursor,
            "move": Qt.SizeAllCursor,
        }
        return mapping.get(action, Qt.CrossCursor)

    # ── 事件 ──

    def mousePressEvent(self, e):
        if e.button() != Qt.LeftButton:
            return
        self._drag_action = self._hit_test(e.position().toPoint())
        if self._drag_action == "move":
            self._drag_anchor = (e.globalPosition().toPoint()
                                 - self.frameGeometry().topLeft())
        else:
            self._drag_anchor = e.globalPosition().toPoint()
        self.update()

    def mouseMoveEvent(self, e):
        if self._drag_action is None:
            self.setCursor(self._cursor_for(self._hit_test(e.position().toPoint())))
            return
        g = e.globalPosition().toPoint()
        if self._drag_action == "move":
            self.move(g - self._drag_anchor)
        else:
            geo = self.geometry()
            r = QRect(geo)
            a = self._drag_action
            if "n" in a:
                r.setTop(min(g.y(), r.bottom() - RegionSelectDialog.MIN_SIZE))
            if "s" in a:
                r.setBottom(max(g.y(), r.top() + RegionSelectDialog.MIN_SIZE))
            if "w" in a:
                r.setLeft(min(g.x(), r.right() - RegionSelectDialog.MIN_SIZE))
            if "e" in a:
                r.setRight(max(g.x(), r.left() + RegionSelectDialog.MIN_SIZE))
            if r.width() >= RegionSelectDialog.MIN_SIZE \
                    and r.height() >= RegionSelectDialog.MIN_SIZE:
                self.setGeometry(r)
        self.region_changed.emit(self.region())
        self.update()

    def mouseReleaseEvent(self, e):
        self._drag_action = None
        self._drag_anchor = None

    def paintEvent(self, e):
        p = QPainter(self)
        border_q = QColor(self._border)
        if not border_q.isValid():
            border_q = QColor(C.color("screen_border"))
        pen = QPen(border_q, 2)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        r = self.rect().adjusted(1, 1, -1, -1)
        p.drawRect(r)
        fill_q = QColor(border_q)
        fill_q.setAlpha(C.size("overlay_handle_alpha"))
        p.setBrush(fill_q)
        p.setPen(Qt.NoPen)
        for hrect, _action in self._handles():
            p.drawRect(hrect)
        p.setBrush(Qt.NoBrush)
        p.end()