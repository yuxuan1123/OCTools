"""
OCTools/tests/test_window_ctl.py
───────────────────────────────────────────────
「主窗口让开屏幕」的回归测试（offscreen 平台，无需人工操作）。

被测公共组件：ui/ui_component/window_ctl.py

覆盖：
  1. top_window 能从页面子控件解析出顶层主窗口
     （直接对子控件调 showMinimized() 是空操作 —— 这正是整类需求的坑点）；
  2. minimize_host / restore_host 幂等与兜底；
  3. 五个最终应用（屏幕OCR / 屏幕翻译 / 屏幕实时翻译 / 屏幕字幕 / 语音翻译）
     经 app_controller.start_app 启动后主窗口确实最小化；
  4. 应用框选路径：RegionSelectDialog.exec() 被调用时主窗口已最小化；
  5. 应用截图路径：_capture_excluding 抓帧前主窗口已最小化；
  6. 设置页「截图区域 → 框选」路径（SetScreenRegion._pick_region）：
     框选期间主窗口最小化，结束后恢复 —— 这里曾误用 self.parent().hide()，
     而 parent 是 tab 页子控件，藏错对象。

模型加载与框选对话框被桩替换，测试只验证窗口状态，不启动任何引擎。

用法：
  python tests/test_app_start_minimize.py
退出码 0 = 全部通过；非 0 = 有失败。
"""

import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_PASS = 0
_FAIL = 0

_FIVE_KEYS = ["screen_ocr", "one_shot", "realtime", "subtitle", "speech_translate"]


def _check(name, fn):
    global _PASS, _FAIL
    try:
        fn()
        _PASS += 1
        print(f"  OK  {name}")
    except Exception as e:  # noqa: BLE001 - 回归测试需捕获一切异常
        _FAIL += 1
        print(f"FAIL  {name}: {type(e).__name__}: {e}")


def _mounted_page():
    """把真实翻译页挂进真实主窗口，返回 (win, page)。"""
    from PySide6.QtWidgets import QVBoxLayout, QWidget

    from ui.ui_component.split_titlebar import TestWindow
    from plugins.translation.tab_translation import TabTranslation

    win = TestWindow()
    page = TabTranslation()
    win.set_right_content(page)
    return win, page


def _stub_apps(page):
    """用桩替换 start/stop/is_running：不加载任何模型。"""
    state = {}
    for key, real in page._apps.items():
        real.start = lambda k=key: state.__setitem__(k, True)
        real.stop = lambda k=key: state.__setitem__(k, False)
        real.is_running = lambda k=key: bool(state.get(k))


def main() -> int:
    from PySide6.QtWidgets import QApplication

    app = QApplication([])

    # ── 1. 顶层窗口解析 ──
    print("[1/6] window_ctl 顶层窗口解析")
    from ui.ui_component import window_ctl

    def _top_window():
        win, page = _mounted_page()
        win.show()
        app.processEvents()
        assert window_ctl.top_window(page) is win, "子控件未解析出主窗口"
        assert not page.isWindow(), "翻译页不应是顶层窗口"
        # 回归点：直接对子控件最小化无效
        page.showMinimized()
        app.processEvents()
        assert not win.isMinimized(), "子控件 showMinimized 竟生效了（预期空操作）"

    _check("top_window 解析 + 子控件最小化为空操作", _top_window)

    # ── 2. minimize_host 幂等与兜底 ──
    print("[2/6] minimize_host / restore_host 幂等与兜底")

    def _minimize_idempotent():
        win, page = _mounted_page()
        win.show()
        app.processEvents()
        assert window_ctl.minimize_host(page) is True, "首次最小化未执行"
        assert win.isMinimized(), "主窗口未最小化"
        assert window_ctl.minimize_host(page) is False, "重复最小化未跳过"
        assert window_ctl.ensure_minimized(page) is True, "ensure_minimized 未确认"
        assert window_ctl.restore_host(page) is True, "restore_host 未恢复"
        assert not win.isMinimized(), "主窗口未恢复"
        assert window_ctl.restore_host(page) is False, "重复恢复未跳过"

    def _minimize_noop():
        assert window_ctl.minimize_host(None) is False, "None 宿主应安全返回"
        assert window_ctl.restore_host(None) is False, "None 宿主恢复应安全返回"
        from PySide6.QtWidgets import QWidget
        hidden = QWidget()          # 从未 show 过的窗口
        assert window_ctl.minimize_host(hidden) is False, "不可见窗口不应最小化"
        assert window_ctl.restore_host(hidden) is False, "未最小化窗口不应恢复"

    _check("minimize_host / restore_host 幂等", _minimize_idempotent)
    _check("minimize_host / restore_host 兜底", _minimize_noop)

    # ── 3. 五个应用启动即最小化 ──
    print("[3/6] 五个最终应用启动即最小化")

    def _five_apps():
        from plugins.translation import app_controller
        for key in _FIVE_KEYS:
            win, page = _mounted_page()
            win.show()
            app.processEvents()
            _stub_apps(page)
            app_controller.start_app(page, key)
            assert win.isMinimized(), f"{key} 启动后主窗口未最小化"

    _check("start_app → 主窗口最小化（5 个应用）", _five_apps)

    def _click_buttons():
        for key in _FIVE_KEYS:
            win, page = _mounted_page()
            win.show()
            app.processEvents()
            _stub_apps(page)
            page._app_btns[key].click()          # 真实点击「启动」
            app.processEvents()
            assert win.isMinimized(), f"{key} 点击启动后主窗口未最小化"
            assert page._app_btns[key].text() == "停止", f"{key} 按钮未切换为停止"

    _check("按钮点击 → 主窗口最小化（5 个应用）", _click_buttons)

    # ── 4. 框选路径：弹窗执行时主窗口已最小化 ──
    print("[4/6] 应用区域框选路径")

    def _region_before_dialog():
        import unittest.mock as mock

        from plugins.translation.apps.app_base import TranslateAppBase
        win, page = _mounted_page()
        win.show()
        app.processEvents()
        a = TranslateAppBase(page, parent=page)
        with mock.patch("ui.ui_component.region_box.RegionSelectDialog") as Dlg:
            seen = {}
            inst = Dlg.return_value
            inst.selected_rect = None

            def _exec(*_a, **_kw):
                seen["minimized"] = win.isMinimized()
                return 0                      # Rejected → 取消
            inst.exec.side_effect = _exec
            a._resolve_region("屏幕OCR")
        assert seen.get("minimized") is True, "框选对话框弹出时主窗口仍可见"

    _check("RegionSelectDialog 执行前已最小化", _region_before_dialog)

    # ── 5. 截图路径：抓帧前已最小化 ──
    print("[5/6] 应用截图路径")

    def _capture_after_minimize():
        import unittest.mock as mock

        from plugins.translation.apps.app_base import TranslateAppBase
        win, page = _mounted_page()
        win.show()
        app.processEvents()
        a = TranslateAppBase(page, parent=page)
        seen = {"minimized": False}
        with mock.patch("core.engines.screenshot_engine.grab_region") as grab:
            def _grab(_rect):
                seen["minimized"] = win.isMinimized()
                return None
            grab.side_effect = _grab
            with mock.patch.object(TranslateAppBase, "_resolve_region",
                                   lambda self, _hint: None):
                a._resolve_region = lambda _h: None
                from PySide6.QtCore import QRect
                a._region = QRect(0, 0, 10, 10)
                a._capture_excluding()
        assert seen["minimized"] is True, "抓帧时主窗口尚未最小化"

    _check("_capture_excluding 抓帧前已最小化", _capture_after_minimize)

    # ── 6. 设置页「截图区域 → 框选」：临时最小化，结束后恢复 ──
    print("[6/6] 设置页框选路径（SetScreenRegion）")

    def _settings_pick_region():
        import unittest.mock as mock

        from config.screen_region_config import default_config as sr_cfg
        from plugins.translation.set_screen_region import SetScreenRegion

        win, page = _mounted_page()
        win.show()
        app.processEvents()

        dlg = SetScreenRegion(sr_cfg(), page)   # 真实调用方式：parent 是 tab 页
        dlg.show()
        app.processEvents()
        assert not win.isMinimized(), "前置条件：主窗口应可见"

        seen = {"during": False}
        with mock.patch("ui.ui_component.region_box.RegionSelectDialog") as Dlg:
            inst = Dlg.return_value
            inst.selected_rect = None

            def _exec(*_a, **_kw):
                seen["during"] = win.isMinimized()
                return 0                        # Rejected → 取消
            inst.exec.side_effect = _exec
            dlg._pick_region()

        assert seen["during"] is True, "框选期间主窗口未最小化"
        assert not win.isMinimized(), "框选结束后主窗口未恢复"
        assert dlg.isVisible(), "设置对话框未恢复显示"

    _check("SetScreenRegion._pick_region 最小化并恢复", _settings_pick_region)

    print(f"\n结果: {_PASS} 通过, {_FAIL} 失败")
    return 1 if _FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
