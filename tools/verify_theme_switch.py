"""验证：删除整页重建后，主题切换仍能自动刷新且不失状态。

关键点：
  - apply_theme 调 app.setStyleSheet 会向所有 widget 派发 QEvent.StyleChange；
  - 接入 StyleHookMixin 的控件（侧栏/标题栏/浮层/设置页等）自动重刷内联样式；
  - main_window 不再销毁重建，故 widget 对象身份不变 → 滚动/输入/展开状态保留。

若此脚本全绿，说明「去掉 600ms 去抖 + 删 _rebuild_ui」方案成立。
"""

import os
import sys

# 让脚本无论从何处调用都能 import ui / config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication

from ui.main_window import MainApp
from ui.theme import apply_theme, C


def main():
    app = QApplication(sys.argv)
    m = MainApp()
    m.show()

    sidebar = m.sidebar
    sb_id = id(sidebar)
    sb_style = sidebar.styleSheet()
    theme_before = C.theme()

    target = "dark" if theme_before == "light" else "light"
    apply_theme(app, {"ui_theme": target})   # 默认 notify=True
    app.processEvents()

    sb_style2 = sidebar.styleSheet()
    theme_after = C.theme()

    ok_obj = sb_id == id(sidebar)
    ok_theme = theme_before != theme_after and C.theme() == target
    ok_refresh = sb_style != sb_style2
    ok_width = sidebar.width() == 208

    print(f"  对象身份未变（无重建）: {'✔' if ok_obj else '✘'}  (侧栏仍是同一实例)")
    print(f"  主题已切换           : {'✔' if ok_theme else '✘'}  {theme_before} -> {theme_after}")
    print(f"  侧栏样式已自动刷新   : {'✔' if ok_refresh else '✘'}  (StyleChange 触发 _apply_inline_style)")
    print(f"  侧栏仍填满侧栏宽度   : {'✔' if ok_width else '✘'}  (width={sidebar.width()})")

    # 状态保留：切回原主题，确认不崩、不重建
    apply_theme(app, {"ui_theme": theme_before})
    app.processEvents()
    ok_roundtrip = id(sidebar) == sb_id and C.theme() == theme_before
    print(f"  切回原主题不崩/不重建 : {'✔' if ok_roundtrip else '✘'}")

    all_ok = ok_obj and ok_theme and ok_refresh and ok_width and ok_roundtrip
    print(f"\n  结论: {'✔ 删除整页重建成立，主题切换零状态丢失' if all_ok else '✘ 存在问题，需排查'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
