"""
octool/ui/toast.py
───────────────────────────────────────────────
右下角轻提示（toast）：短暂显示后自动淡出关闭，不打断用户操作。

用法:
  from ui.toast import show_toast
  show_toast(window, "翻译完成", duration_ms=1500)
"""

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation
from PySide6.QtWidgets import QLabel, QGraphicsOpacityEffect


def show_toast(parent, message, duration_ms=1500, kind="success"):
    """在 parent 窗口右下角弹出一个轻提示，duration_ms 后自动淡出关闭。

    参数:
      parent     : 宿主窗口（QMainWindow / QWidget），toast 跟随其右下角定位
      message    : 提示文本
      duration_ms: 显示时长（毫秒），默认 1500
      kind       : success / info / warn，决定配色

    配色由全局 QSS 的 QLabel#toast[kind="..."] 规则承载（theme.py 生成），
    随主题切换自动跟随，不再在模块加载时缓存 C.color（修掉旧实现的配色过期 bug）。
    """
    toast = QLabel(message, parent)
    toast.setObjectName("toast")
    toast.setAlignment(Qt.AlignCenter)
    toast.setWordWrap(True)
    toast.setAttribute(Qt.WA_TransparentForMouseEvents)   # 不拦截鼠标点击
    toast.setProperty("kind", kind)
    toast.style().polish(toast)

    # 长文本限制宽度，短文本自适应
    if len(message) > 16:
        max_w = max(200, min(360, parent.width() // 2))
        toast.setFixedWidth(max_w)
    else:
        toast.adjustSize()

    # 右下角定位（略高于状态栏）
    x = parent.width() - toast.width() - 24
    y = parent.height() - toast.height() - 56
    toast.move(max(x, 12), max(y, 12))
    toast.show()
    toast.raise_()

    # 淡入
    effect = QGraphicsOpacityEffect(toast)
    toast.setGraphicsEffect(effect)
    anim_in = QPropertyAnimation(effect, b"opacity", toast)
    anim_in.setDuration(160)
    anim_in.setStartValue(0.0)
    anim_in.setEndValue(1.0)
    anim_in.start(QPropertyAnimation.DeleteWhenStopped)

    # 到时淡出并销毁
    def _fade_out():
        anim_out = QPropertyAnimation(effect, b"opacity", toast)
        anim_out.setDuration(300)
        anim_out.setStartValue(1.0)
        anim_out.setEndValue(0.0)
        anim_out.finished.connect(toast.deleteLater)
        anim_out.start(QPropertyAnimation.DeleteWhenStopped)

    QTimer.singleShot(max(0, int(duration_ms)), _fade_out)
    return toast
