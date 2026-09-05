"""offscreen 烟测：构造 vertical_split_titlebar.VerticalWindow，1 秒后退出。
退出码 0 = OK。

验证 VerticalWindow 的结构（单标题栏 + 上下两栏）：
  * 仅顶部一个标题栏（attach 到 window）
  * 不存在底部标题栏 / 不存在折叠按钮 / 不存在 _toggle_upper_pane
  * 垂直 QSplitter，两个 _Pane（上分区 + 下分区）
  * WindowResizer 已挂 + enabled
  * showEvent 走完后无错误
"""
from __future__ import annotations
import os
import sys

_PROJ_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
)
if _PROJ_ROOT not in sys.path:
    sys.path.insert(0, _PROJ_ROOT)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication

from ui.ui_component.vertical_split_titlebar import VerticalWindow
from ui.ui_component.window_resizer import WindowResizer
from ui.ui_component.split_window import _Pane


def _check(name, cond, detail=""):
    print(f"  [{'OK' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
    return cond


def main():
    app = QApplication(sys.argv)

    failures = 0
    w = VerticalWindow()
    w.show()

    # ── 单标题栏 ──
    failures += not _check("window shown", w.isVisible())
    failures += not _check(
        "存在顶部标题栏",
        hasattr(w, "top_bar") and w.top_bar is not None,
    )
    failures += not _check(
        "顶部标题栏 attach 到 window",
        w.top_bar._window is w,
    )
    failures += not _check(
        "无底部标题栏（单标题栏变体）",
        not hasattr(w, "bottom_bar"),
    )
    failures += not _check(
        "无折叠按钮（单标题栏变体）",
        not hasattr(w, "collapse_btn"),
    )
    failures += not _check(
        "无折叠状态字段（单标题栏变体）",
        not hasattr(w, "_upper_visible"),
    )
    failures += not _check(
        "无折叠动作方法（单标题栏变体）",
        not hasattr(w, "_toggle_upper_pane"),
    )

    # ── 上下两栏 ──
    failures += not _check(
        "splitter 存在",
        hasattr(w, "_splitter"),
    )
    failures += not _check(
        "splitter 是 Vertical",
        w._splitter.orientation() == Qt.Vertical,
        f"got {w._splitter.orientation()}",
    )
    failures += not _check(
        "splitter 有 2 个 pane",
        w._splitter.count() == 2,
        f"got count={w._splitter.count()}",
    )
    failures += not _check(
        "upper_pane 是 _Pane",
        isinstance(w.upper_pane, _Pane),
    )
    failures += not _check(
        "lower_pane 是 _Pane",
        isinstance(w.lower_pane, _Pane),
    )

    # ── 公共 API ──
    failures += not _check(
        "set_upper_content 可调用",
        callable(getattr(w, "set_upper_content", None)),
    )
    failures += not _check(
        "set_lower_content 可调用",
        callable(getattr(w, "set_lower_content", None)),
    )

    # ── WindowResizer 接入 ──
    failures += not _check(
        "resizer 是 WindowResizer",
        isinstance(w.resizer, WindowResizer),
    )
    failures += not _check(
        "resizer enabled",
        w.resizer.is_enabled(),
    )
    failures += not _check(
        "setMinimumSize 已设置",
        w.minimumWidth() > 0 and w.minimumHeight() > 0,
        f"min={w.minimumWidth()}x{w.minimumHeight()}",
    )

    # ── 抓帧 ──
    pm = w.grab()
    failures += not _check("grab 非空", not pm.isNull(), f"size={pm.size()}")

    QTimer.singleShot(1000, app.quit)
    rc = app.exec()
    print(f"\nexit code = {rc}, failures = {failures}")
    sys.exit(0 if (rc == 0 and failures == 0) else 1)


if __name__ == "__main__":
    main()
