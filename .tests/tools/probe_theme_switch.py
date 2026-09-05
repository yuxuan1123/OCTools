"""探针：验证主题切换时各内联样式的实际刷新情况。

重点验证一个怀疑：split_titlebar._refresh_theme 更新的是 self._top_cfg，
而 CustomTitleBar 持有的是 load_config() 深合并产生的新 dict ——
两者不是同一对象，标题栏可能根本没跟着换肤。

用法：QT_QPA_PLATFORM=offscreen python tools/probe_theme_switch.py
"""

import re
import os
import sys

# 让脚本无论从何处调用都能 import ui / config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication

from config.ui_config import CONFIG as C
from ui.ui_component.split_titlebar import TestWindow
from ui.theme import apply_theme


def first_bg(widget) -> str:
    """从内联样式表里抠出第一个 background 色值。"""
    ss = widget.styleSheet() or ""
    m = re.search(r"background\s*:\s*(#[0-9A-Fa-f]{3,8})", ss)
    return m.group(1) if m else "(无)"


def snapshot(win, tag):
    print(f"\n──────── {tag} ────────")
    print(f"  当前主题             : {C.theme()}")
    print(f"  C.color('sidebar_bg'): {C.color('sidebar_bg')}")
    print(f"  C.color('bg')        : {C.color('bg')}")
    print(f"  顶栏内联 background  : {first_bg(win.top_bar)}")
    print(f"  底栏内联 background  : {first_bg(win.bottom_bar)}")
    print(f"  左栏 _Pane background: {first_bg(win.left_pane)}")
    print(f"  右栏 _Pane background: {first_bg(win.right_pane)}")
    print(f"  侧栏(LeftSidebar)    : {first_bg(getattr(win, 'sidebar', None))}"
          if hasattr(win, "sidebar") else "")


def main():
    app = QApplication(sys.argv)
    apply_theme(app, {}, notify=False)

    win = TestWindow()
    win.show()
    app.processEvents()

    snapshot(win, "切换前")

    # 切到另一主题
    target = "dark" if C.theme() != "dark" else "light"
    print(f"\n>>> apply_theme(theme={target})")
    apply_theme(app, {"ui_theme": target}, notify=True)
    app.processEvents()
    app.processEvents()

    snapshot(win, f"切换后（{target}）")

    # ───────── 判定 ────────
    print("\n──────── 判定 ────────")
    checks = [
        ("顶栏", first_bg(win.top_bar), C.color("sidebar_bg")),
        ("底栏", first_bg(win.bottom_bar), C.color("sidebar_bg")),
        ("左栏", first_bg(win.left_pane), C.color("sidebar_bg")),
        ("右栏", first_bg(win.right_pane), C.color("bg")),
    ]
    all_ok = True
    for name, actual, expect in checks:
        ok = actual.lower() == (expect or "").lower()
        all_ok = all_ok and ok
        print(f"  {'✔' if ok else '✘'} {name}: 实际={actual}  期望={expect}")
    print(f"\n  结论: {'全部跟随主题 ✔' if all_ok else '存在未跟随的内联样式 ✘'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
