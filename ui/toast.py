"""
OCTools/ui/toast.py
───────────────────────────────────────────────
右下角轻提示（toast）：短暂显示后自动淡出关闭，不打断用户操作。

用法:
  from ui.toast import show_toast
  show_toast(window, "翻译完成", duration_ms=1500)

调试版本：打印全局 QSS 中 toast 规则，强制刷新样式。
"""

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation
from PySide6.QtWidgets import QLabel, QGraphicsOpacityEffect, QApplication
from config.ui_config import CONFIG

def show_toast(parent, message, duration_ms=1500, kind="success"):
    # 从配置读取颜色
    bg_key = {
        "success": "toast_success",
        "info":    "toast_info",
        "warn":    "toast_warning",
    }.get(kind, "toast_success")
    bg = CONFIG.color(bg_key) or "#10B981"          # 背景色
    text_color = CONFIG.color("toast_text") or "#1F2430"  # 文字色

    toast = QLabel(message, parent)
    toast.setObjectName("toast_" + kind)  # 保留 objectName（不影响显示）
    toast.setStyleSheet(
        f"background: {bg}; color: {text_color}; "
        f"border-radius: 8px; padding: 10px 18px; "
        f"font-size: 12px; font-weight: 600;"
    )
    toast.setAlignment(Qt.AlignCenter)
    toast.setWordWrap(True)
    toast.setAttribute(Qt.WA_TransparentForMouseEvents)

    # 长文本限制宽度
    if len(message) > 16:
        max_w = max(200, min(360, parent.width() // 2))
        toast.setFixedWidth(max_w)
    else:
        toast.adjustSize()

    # 右下角定位
    x = parent.width() - toast.width() - 24
    y = parent.height() - toast.height() - 56
    toast.move(max(x, 12), max(y, 12))
    toast.show()
    toast.raise_()

    # 淡入动画
    effect = QGraphicsOpacityEffect(toast)
    toast.setGraphicsEffect(effect)
    anim_in = QPropertyAnimation(effect, b"opacity", toast)
    anim_in.setDuration(160)
    anim_in.setStartValue(0.0)
    anim_in.setEndValue(1.0)
    anim_in.start(QPropertyAnimation.DeleteWhenStopped)

    # 定时淡出
    def _fade_out():
        anim_out = QPropertyAnimation(effect, b"opacity", toast)
        anim_out.setDuration(300)
        anim_out.setStartValue(1.0)
        anim_out.setEndValue(0.0)
        anim_out.finished.connect(toast.deleteLater)
        anim_out.start(QPropertyAnimation.DeleteWhenStopped)

    QTimer.singleShot(max(0, int(duration_ms)), _fade_out)
    return toast