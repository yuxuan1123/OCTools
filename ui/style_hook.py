"""
OCTools/ui/style_hook.py
───────────────────────────────
主题热切换：让内联样式跟随主题变化，无需重建控件。

背景：
app.setStyleSheet(新QSS) 只替换全局样式表，代码中的内联样式（widget.setStyleSheet(...)）是独立字符串，
Qt 不会在全局 QSS 变化时重新求值。本模块利用 app.setStyleSheet() 向所有 widget 派发 QEvent.StyleChange，
控件在该事件里重算内联样式。

注意事项（已处理）：
1. setStyleSheet() 会再次触发 StyleChange 导致递归 → 用 _style_applying 守卫阻断。
2. 单次 app.setStyleSheet() 会重复派发 2~4 次 StyleChange → _apply_inline_style() 必须幂等且轻量。

用法：
    class Sidebar(StyleHookMixin, QWidget):
        def __init__(self):
            super().__init__()
            self._apply_inline_style()      # 首次手动调用

        def _apply_inline_style(self):
            self.setStyleSheet(f"background: {C.color('sidebar_bg')};")

注意混入顺序：StyleHookMixin 必须在 Qt 类之前。
若子类重写 changeEvent，必须调用 super().changeEvent(event)。
"""

from PySide6.QtCore import QEvent


class StyleHookMixin:
    """内联样式随主题自动刷新。

    子类必须实现幂等的 _apply_inline_style()，在其中重新设置内联样式。
    """

    _style_applying = False

    def _apply_inline_style(self):
        """重新应用内联样式。子类必须重写。"""
        raise NotImplementedError(f"{type(self).__name__} 必须实现 _apply_inline_style()")

    def refresh_inline_style(self):
        """手动触发重刷（配色数据变了但主题没变时用）。"""
        self._exec_apply()

    def _exec_apply(self):
        """带递归守卫地执行 _apply_inline_style。"""
        if self._style_applying:   # 阻断 setStyleSheet → StyleChange → 递归
            return
        self._style_applying = True
        try:
            self._apply_inline_style()
        finally:
            self._style_applying = False

    def changeEvent(self, event):
        """QEvent.StyleChange 时重算内联样式，其余照常。"""
        if event.type() == QEvent.StyleChange:
            self._exec_apply()
        super().changeEvent(event)
