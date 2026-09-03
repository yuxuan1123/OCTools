"""
octool/ui/style_hook.py
───────────────────────────────────────────────
主题热切换支撑：让「内联样式」跟随主题变化，无需销毁重建控件。

背景
────
`app.setStyleSheet(新QSS)` 只替换全局样式表字符串。写在代码里的内联样式
（`widget.setStyleSheet(f"...{C.color('x')}...")`）是**独立的样式字符串**，
Qt 不会在全局 QSS 变化时重新求值 —— 主题切换后它们仍是旧配色。

历史上本项目的解法是「销毁并重建整个页面」（main_window 里 600ms 去抖后
重建侧栏+当前 tab），代价是滚动位置、展开状态、输入内容全部丢失。

本模块改走 Qt 原生事件：`app.setStyleSheet()` 会向**所有** widget 派发
`QEvent.StyleChange`（实测隐藏的 tab 页面、无 parent 的控件也会收到），
控件只需在该事件里把自己那部分内联样式重算一遍即可。

两个必须知道的坑（都已在本模块内处理或标注）
──────────────────────────────────────────
1. `QWidget.setStyleSheet()` **自身会向自己派发 `StyleChange`**。
   在 `changeEvent` 里直接调用 = 无限递归（实测直接栈溢出）。
   → 本模块用 `_style_applying` 守卫阻断。
2. 单次 `app.setStyleSheet()` 会向每个控件**重复派发 2~4 次** `StyleChange`。
   → `_apply_inline_style()` 必须**幂等**且轻量（只做字符串拼接 + 赋值）。

用法
────
    class Sidebar(StyleHookMixin, QWidget):
        def __init__(self):
            super().__init__()
            self._apply_inline_style()      # 首次需手动调一次

        def _apply_inline_style(self):
            self.setStyleSheet(f"background: {C.color('sidebar_bg')};")

注意混入顺序：`StyleHookMixin` 必须写在 Qt 类**之前**，否则 MRO 中
`super().changeEvent()` 走不到 `QWidget.changeEvent`。

若子类本身也要重写 `changeEvent`，必须调用 `super().changeEvent(event)`，
否则本模块的钩子不会触发。
"""

from PySide6.QtCore import QEvent


class StyleHookMixin:
    """内联样式随主题自动重刷。

    子类必须实现 `_apply_inline_style()`：无参、无返回值、**幂等**。
    该方法里应重新应用本控件及其直属子控件的全部内联样式。
    """

    # 类级默认值，实例首次 _exec_apply 时会创建同名实例属性
    _style_applying = False

    def _apply_inline_style(self):
        """重新应用内联样式。子类必须重写。"""
        raise NotImplementedError(
            f"{type(self).__name__} 必须实现 _apply_inline_style()")

    def refresh_inline_style(self):
        """外部手动触发重刷（配色数据变了但主题没变时用，如切换浮层配色）。"""
        self._exec_apply()

    def _exec_apply(self):
        """带递归守卫地执行 _apply_inline_style。"""
        if self._style_applying:      # 阻断 setStyleSheet → StyleChange → 递归
            return
        self._style_applying = True
        try:
            self._apply_inline_style()
        finally:
            self._style_applying = False

    def changeEvent(self, event):
        """QEvent.StyleChange 时重算内联样式，其余事件照常上抛。"""
        if event.type() == QEvent.StyleChange:
            self._exec_apply()
        super().changeEvent(event)
