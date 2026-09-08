"""整行长滑块（真实拖拽 · 流光 · 呼吸 · 回弹）。

纯控件，不含业务逻辑：只负责"开 / 关"这一件事的视觉与交互。
"""

import math

from PySide6.QtCore import (
    Qt, QTimer, Signal, QRectF, QPointF, QPropertyAnimation,
    QEasingCurve, Property, QSize,
)
from PySide6.QtGui import QColor, QPainter, QPen, QLinearGradient, QPainterPath
from PySide6.QtWidgets import QAbstractButton, QSizePolicy

from home.constants import TRACK_OFF, TRACK_ON, THUMB_C
from home.format_utils import lerp


class SlideSwitch(QAbstractButton):
    """整行宽自适应滑块开关。

    动效清单：
      · 真实拖拽 —— 按下任意位置即跟手，实时插值轨道颜色
      · 松手回弹 —— OutBack 缓动，越界时圆钮被"挤压"（squash）
      · 开启流光 —— 白色柔光带循环扫过墨黑轨道
      · 呼吸脉冲 —— 开启后圆钮外圈持续呼吸光晕
      · 两端图标 —— ✕ / ✓ 随进度淡入淡出（几何绘制，无字体依赖）
    """
    thumbPosChanged = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)

        # ── 尺寸：整行宽（高度固定，宽度随布局自适应）──
        self._H = 58
        self._margin = 5
        self._W = 260
        self.setMinimumHeight(self._H)
        self.setMaximumHeight(self._H)
        self.setMinimumWidth(200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # 配色（均可外部覆盖）
        self.track_off = QColor(TRACK_OFF)
        self.track_on = QColor(TRACK_ON)
        self.thumb_color = QColor(THUMB_C)

        # ── 状态 ──
        self._pos = 0.0          # 归一化位置 0..1（可越界用于挤压）
        self._dragging = False
        self._grab = 0.0         # 按下时鼠标相对圆钮左边的偏移
        self._hover = False

        # 回弹动画
        self._anim = QPropertyAnimation(self, b"thumbPos", self)
        self._anim.setEasingCurve(QEasingCurve.OutBack)
        self._anim.setDuration(420)
        self._anim.finished.connect(self._on_anim_done)

        # 流光 + 呼吸（开启后循环驱动）
        self._fx = QTimer(self)
        self._fx.setInterval(16)
        self._fx.timeout.connect(self._fx_step)
        self._shimmer = 0.0      # 0..1.45（>1 为扫完停顿）
        self._pulse = 0.0

        self.setMouseTracking(True)
        self._sync_pos()

    # ── 尺寸自适应：resize 时重算宽度 ──────
    def resizeEvent(self, event):
        self._W = max(1, event.size().width())
        super().resizeEvent(event)

    def sizeHint(self):
        return QSize(360, self._H)

    # ── 动画属性 ────────────────────────────
    def get_thumb_pos(self) -> float:
        return self._pos

    def set_thumb_pos(self, v):
        self._pos = float(v)
        self.update()
        self.thumbPosChanged.emit(self._pos)

    thumbPos = Property(float, fget=get_thumb_pos, fset=set_thumb_pos,
                        notify=thumbPosChanged)

    # ── 内部：几何 ──────────────────────────
    def _thumb_d(self):
        return self._H - 2 * self._margin

    def _travel(self):
        return max(1.0, self._W - self._thumb_d() - 2 * self._margin)

    def _sync_pos(self):
        self._pos = 1.0 if self.isChecked() else 0.0
        self.update()

    # ── 外部状态设置 ────────────────────────
    def setChecked(self, checked: bool):
        super().setChecked(checked)
        if checked and not self._fx.isActive():
            self._shimmer = 0.0
            self._fx.start()
        elif not checked:
            self._fx.stop()
            self._shimmer = 0.0
            self._pulse = 0.0
        self._animate_to(1.0 if checked else 0.0)

    def _on_anim_done(self):
        # 动画结束后把位置精确吸附到端点，消除浮点残留
        self._pos = 1.0 if self.isChecked() else 0.0
        self.update()

    def _animate_to(self, target: float):
        self._anim.stop()
        self._anim.setStartValue(self._pos)
        self._anim.setEndValue(target)
        self._anim.start()

    # ── 流光 / 呼吸步进 ─────────────────────
    def _fx_step(self):
        self._shimmer += 0.012
        if self._shimmer > 1.45:
            self._shimmer = 0.0
        self._pulse += 0.055
        self.update()

    # ── 鼠标：真实拖拽 ──────────────────────
    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return
        self._dragging = True
        self._anim.stop()
        left = self._margin + self._pos * self._travel()
        self._grab = event.position().x() - left
        self.setCursor(Qt.ClosedHandCursor)
        self.update()

    def mouseMoveEvent(self, event):
        if not self._dragging:
            return
        left = event.position().x() - self._grab
        pos = (left - self._margin) / self._travel()
        # 越界留 4% 用于"挤压"视觉
        self._pos = max(-0.04, min(1.04, pos))
        self.update()

    def mouseReleaseEvent(self, event):
        if not self._dragging:
            return
        self._dragging = False
        self.setCursor(Qt.PointingHandCursor)
        target = 1.0 if self._pos > 0.5 else 0.0
        will_change = (target > 0.5) != self.isChecked()
        self.setChecked(target > 0.5)
        if will_change:
            self.clicked.emit()

    def enterEvent(self, event):
        self._hover = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover = False
        self.update()
        super().leaveEvent(event)

    # ── 绘制 ────────────────────────────────
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        W, H = self._W, self._H
        if W <= 0 or H <= 0:
            return

        prog = max(0.0, min(1.0, self._pos))
        r = H / 2.0
        track_rect = QRectF(0, 0, W, H)

        # 1) 轨道（颜色随进度插值：浅灰 → 墨黑）
        track = lerp(self.track_off, self.track_on, prog)
        p.setPen(Qt.NoPen)
        p.setBrush(track)
        p.drawRoundedRect(track_rect, r, r)

        # 2) hover 时轨道加深一层（微妙的交互反馈）
        if self._hover and not self.isChecked():
            p.setBrush(QColor(0, 0, 0, 12))
            p.drawRoundedRect(track_rect, r, r)

        # 3) 开启后：流光扫过（裁剪在轨道内）
        if self.isChecked() and self._shimmer <= 1.0:
            path = QPainterPath()
            path.addRoundedRect(track_rect, r, r)
            p.save()
            p.setClipPath(path)
            sw = W * 0.42
            x = -sw + self._shimmer * (W + sw)
            g = QLinearGradient(x, 0, x + sw, 0)
            g.setColorAt(0.0, QColor(255, 255, 255, 0))
            g.setColorAt(0.5, QColor(255, 255, 255, 46))
            g.setColorAt(1.0, QColor(255, 255, 255, 0))
            p.setBrush(g)
            p.setPen(Qt.NoPen)
            p.drawRect(QRectF(x, 0, sw, H))
            p.restore()

        # 4) 两端图标（✕ 左 / ✓ 右，几何绘制）
        self._draw_cross(p, prog, H)
        self._draw_check(p, prog, W, H)

        # 5) 圆钮（越界挤压 + 呼吸光晕 + 投影）
        d0 = self._thumb_d()
        over = 0.0 if 0.0 <= self._pos <= 1.0 else min(abs(self._pos), abs(self._pos - 1.0))
        squash = min(0.16, over * 1.6)
        d = d0 * (1.0 - squash)
        left = self._margin + self._pos * self._travel()
        left = max(0.0, min(W - d, left))
        top = (H - d) / 2.0
        cx, cy = left + d / 2.0, H / 2.0

        # 呼吸光晕（开启后）
        if self.isChecked():
            a = int(30 * (0.5 + 0.5 * math.sin(self._pulse)))
            p.setBrush(QColor(255, 255, 255, a))
            p.setPen(Qt.NoPen)
            p.drawEllipse(QRectF(cx - d / 2 - 5, cy - d / 2 - 5, d + 10, d + 10))

        # 投影
        p.setBrush(QColor(0, 0, 0, 55))
        p.drawEllipse(QRectF(left + 1, top + 3, d, d))
        # 主体
        p.setBrush(self.thumb_color)
        p.setPen(QPen(QColor(228, 228, 231), 1.2))
        p.drawEllipse(QRectF(left, top, d, d))

        # 圆钮内两道竖纹（可拖动暗示）
        pen = QPen(QColor(200, 200, 205), 2)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        gap = d * 0.16
        for dx in (-gap, gap):
            p.drawLine(QPointF(cx + dx, cy - 5), QPointF(cx + dx, cy + 5))

    def _draw_cross(self, p: QPainter, prog: float, H: float):
        """左侧 ✕：关闭时显现，颜色 #52525B。"""
        alpha = int(210 * (1.0 - prog))
        if alpha <= 4:
            return
        pen = QPen(QColor(82, 82, 91, alpha), 2.2)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        s = 5.0
        cx = self._margin + self._thumb_d() / 2.0
        cy = H / 2.0
        p.drawLine(QPointF(cx - s, cy - s), QPointF(cx + s, cy + s))
        p.drawLine(QPointF(cx + s, cy - s), QPointF(cx - s, cy + s))

    def _draw_check(self, p: QPainter, prog: float, W: float, H: float):
        """右侧 ✓：开启时显现，颜色 #FAFAFA。"""
        alpha = int(235 * prog)
        if alpha <= 4:
            return
        pen = QPen(QColor(250, 250, 250, alpha), 2.4)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen)
        cx = W - self._margin - self._thumb_d() / 2.0
        cy = H / 2.0
        p.drawPolyline([
            QPointF(cx - 6, cy),
            QPointF(cx - 1.5, cy + 4.5),
            QPointF(cx + 6, cy - 5),
        ])
