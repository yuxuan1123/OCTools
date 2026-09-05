"""
OCTools/tests/test_overlay_resize.py
───────────────────────────────────────────────
悬浮窗缩放相关回归测试（offscreen，无需人工操作）。

覆盖：
  1. 最小尺寸来自配置：resizer 的 min_w/min_h == ui_config 的
     overlay_min_w / overlay_min_h（澄清「配置没生效」误判，代码一直接了）。
  2. 顶边缩放让位：标题栏顶部 top_resize_margin 内按下时，若缩放器存在且启用，
     不启动拖动（让事件冒泡给 WindowResizer）。
  3. 退化路径：缩放器禁用（pin）/ 不存在（resizable=False）时，顶边照常拖动。

用法：
  python tests/test_overlay_resize.py
退出码 0 = 全部通过；非 0 = 有失败。
"""

import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEvent, Qt, QPoint
from PySide6.QtGui import QMouseEvent
from PySide6.QtTest import QTest

_PASS = 0
_FAIL = 0


def _check(name, fn):
    global _PASS, _FAIL
    try:
        fn()
        _PASS += 1
        print(f"  OK  {name}")
    except Exception as e:  # noqa: BLE001 - 回归测试需捕获一切异常
        _FAIL += 1
        print(f"FAIL  {name}: {type(e).__name__}: {e}")


def _press(y: int, margin_field: int = 20):
    """构造一个左键按下事件，本地坐标 (margin_field, y)。"""
    return QMouseEvent(QEvent.MouseButtonPress,
                      QPoint(margin_field, y), QPoint(2000, y),
                      Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)


def main() -> int:
    from PySide6.QtWidgets import QApplication

    from config.ui_config import CONFIG as C
    from ui.ui_component.overlay import FloatingOverlay
    from ui.tabs.tab_translation import TabTranslation
    from ui.tabs.translation.registry import _APP_ROWS

    app = QApplication([])

    min_w = C.size("overlay_min_w")
    min_h = C.size("overlay_min_h")
    # 顶部不让位（top_yield=0）：标题栏不再 e.ignore 让位缩放，按钮上方整条可拖。
    # 顶部缩放由 WindowResizer edge (14) + 标题栏覆盖（截走事件）共同决定 → 顶部缩放失效，
    # 左/右/下边缘缩放保留。按钮上方 y 0-10 不再有"按不到"的无用窄带。
    top_yield = 0

    page = TabTranslation()

    # ── 1. 最小尺寸来自配置 ──
    print("[1/3] 缩放最小尺寸来自 ui_config")

    def _min_from_config():
        for key, (cls, *_r) in _APP_ROWS.items():
            a = cls(page, parent=page)
            ov = a._create_overlay()
            assert ov._resizer is not None, f"{key}: 未创建缩放器"
            assert ov._resizer._min_w == min_w, f"{key}: min_w={ov._resizer._min_w} 期望 {min_w}"
            assert ov._resizer._min_h == min_h, f"{key}: min_h={ov._resizer._min_h} 期望 {min_h}"

    _check(f"resizer min = overlay_min_w/h ({min_w}×{min_h})", _min_from_config)

    # ── 2. 顶部无让位（top_yield=0）：整条都可拖，按钮上方不再有"无用窄带" ──
    print("[2/3] 顶部无让位（按钮上方整条可拖）")

    def _top_no_yield():
        key0 = next(iter(_APP_ROWS))
        app_cls = _APP_ROWS[key0][0]
        a = app_cls(page, parent=page)
        ov = a._create_overlay()
        tb = ov._title_bar
        assert tb._top_resize_margin == top_yield, "标题栏 top_resize_margin 应为 0（删除按钮上方让位）"
        assert tb._resizer is ov._resizer, "缩放器未注入标题栏"
        assert ov._resizer.is_enabled(), "前置：缩放器应启用"
        # top_yield=0：y=2 不再让位（e.pos().y() <= 0 恒 False），整列走拖动
        tb._drag_pos = None
        tb.mousePressEvent(_press(2))
        assert tb._drag_pos is not None, "top_yield=0 时顶部按下应可拖动（无让位）"

        # 中部仍可拖
        tb._drag_pos = None
        tb.mousePressEvent(_press(15))
        assert tb._drag_pos is not None, "标题栏中部按下应可拖动"

    _check("顶部无让位 / 按钮上方整条可拖", _top_no_yield)

    # ── 3. 退化路径：无缩放器时顶边照常拖动；pin 时按锁定语义无操作 ──
    print("[3/3] 退化路径")

    def _pin_locks_top_edge():
        key0 = next(iter(_APP_ROWS))
        app_cls = _APP_ROWS[key0][0]
        a = app_cls(page, parent=page)
        ov = a._create_overlay()
        tb = ov._title_bar
        ov.set_pinned(True)                    # 禁用缩放器 + 关闭 draggable
        assert not ov._resizer.is_enabled(), "前置：pin 应禁用缩放器"
        tb._drag_pos = None
        tb.mousePressEvent(_press(2))          # 顶边
        # 锁定语义：顶边既不能缩放（resizer 禁用）也不能拖动（draggable 关闭）
        # → 无操作，符合「固定」预期
        assert tb._drag_pos is None, "pin（锁定）时顶边应无操作：既不能拖也不能拉"

    def _no_resizer_falls_back_to_drag():
        ov = FloatingOverlay(buttons=[], resizable=False)
        tb = ov._title_bar
        assert tb._resizer is None, "前置：resizable=False 不应有缩放器"
        tb._drag_pos = None
        tb.mousePressEvent(_press(2))          # 顶边
        assert tb._drag_pos is not None, "无缩放器时顶边应正常拖动"

    _check("pin（锁定）时顶边无操作", _pin_locks_top_edge)
    _check("resizable=False 顶边回退拖动", _no_resizer_falls_back_to_drag)

    # ── 4. 标题文字区可拖动：label 鼠标透传 ──
    print("[4/5] 标题文字区透传属性")

    def _title_label_transparent():
        ov = FloatingOverlay(buttons=[], resizable=False)
        ov.show()
        label = ov._title_bar._title_label
        assert label.testAttribute(Qt.WA_TransparentForMouseEvents), \
            "标题 label 未设置 WA_TransparentForMouseEvents：标题文字区无法触发拖动"

    _check("标题 label 鼠标透传已启用", _title_label_transparent)

    # ── 5. 落在标题文字上的点击穿透到标题栏并启动拖动 ──
    print("[5/5] 标题文字区点击穿透启动拖动")

    def _title_label_drag():
        ov = FloatingOverlay(buttons=[], resizable=False)
        ov.show()
        tb = ov._title_bar
        label = tb._title_label
        label.setFixedWidth(80)        # 保证有可命中的尺寸
        label.show()
        tb._drag_pos = None
        QTest.mousePress(label, Qt.LeftButton, Qt.NoModifier, QPoint(40, 8))
        assert tb._drag_pos is not None, "点击标题文字未穿透到标题栏（未启动拖动）"
        QTest.mouseRelease(label, Qt.LeftButton, Qt.NoModifier, QPoint(40, 8))

    _check("标题文字区点击穿透启动拖动", _title_label_drag)

    # ── 6. 拖动跟手：按下锁定鼠标到标题栏，移出标题栏也不中断 ──
    print("[6] 拖动跟手（grabMouse）")

    def _drag_follows_cursor():
        from PySide6.QtWidgets import QWidget as _QW
        ov = FloatingOverlay(buttons=[], resizable=False)
        ov.show()
        ov.move(100, 100)
        tb = ov._title_bar
        bar_local = QPoint(ov.width() // 2, tb.height() // 2 + 4)
        QTest.mousePress(tb, Qt.LeftButton, Qt.NoModifier, bar_local)
        # 修复核心：按下即锁定鼠标到标题栏，否则移出标题栏事件丢失 → 中断
        assert _QW.mouseGrabber() is tb, "按下后未锁定鼠标到标题栏（拖动易中断）"
        QTest.mouseMove(tb, QPoint(bar_local.x() + 30, bar_local.y() + 10))
        assert ov.pos() != QPoint(100, 100), "拖动未使窗口移动"
        QTest.mouseRelease(tb, Qt.LeftButton, Qt.NoModifier, bar_local)
        assert _QW.mouseGrabber() is None, "释放后未解除鼠标锁定"

    _check("拖动跟手：grab→移动→释放", _drag_follows_cursor)

    print(f"\n结果: {_PASS} 通过, {_FAIL} 失败")
    return 1 if _FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
