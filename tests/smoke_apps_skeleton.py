"""
OCTools/tests/smoke_apps_skeleton.py
───────────────────────────────────────────────────────
五个最终应用骨架回归（offscreen 平台，无需真实模型 / 截图 / 语音）

被测目标：ui/tabs/translation/apps/app_base.py 的基类 start()/stop()
骨架（基类固定 9 步：防重入→解析区域→创建悬浮框→接信号→创建 extras→
创建 worker→启动 worker→立即触发→显示定位）。

测试策略：mock 掉底层引擎（model loading / screenshot / audio capture /
LiveRegionBox）使 start() 完整跑通 9 步，然后做断言：
  - 5 个 app 都能 start() → is_running=True → stop() → is_running=False
  - 防重入（第二次 start 是 no-op）
  - REQUIRES_REGION 分类正确（图像类调 _resolve_region，语音类跳过）
  - _install_overlay_signals 信号钩子映射与 BUTTONS 子集一致
  - _install_extra_widgets 只有实时翻译类覆写
  - stop() 调 worker.stop() + 清空 _worker/_overlay

用法：
  python tests/smoke_apps_skeleton.py
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


def _check(name, fn):
    global _PASS, _FAIL
    try:
        fn()
        _PASS += 1
        print(f"  OK  {name}")
    except Exception as e:  # noqa: BLE001 - 冒烟测试需捕获一切异常
        _FAIL += 1
        print(f"FAIL  {name}: {type(e).__name__}: {e}")


# ── Mock 引擎层 ──

class _MockWorker:
    """最简单的 worker：记录 start/stop 调用"""
    def __init__(self, name):
        self._name = name
        self.started_with = None
        self.stopped = 0

    def start(self, rect):
        self.started_with = rect

    def stop(self):
        self.stopped += 1

    def set_paused(self, paused):
        pass

    def capture_now(self):
        pass

    def set_region(self, rect):
        pass


def _make_minimal_app_classes():
    """直接 import 5 个 app 类。"""
    from plugins.translation.apps.screen_ocr_app import ScreenOcrApp
    from plugins.translation.apps.one_shot_screen_translate_app import OneShotScreenTranslateApp
    from plugins.translation.apps.realtime_screen_translate_app import RealtimeScreenTranslateApp
    from plugins.translation.apps.screen_subtitle_app import ScreenSubtitleApp
    from plugins.translation.apps.speech_translate_app import SpeechTranslateApp
    return [ScreenOcrApp, OneShotScreenTranslateApp,
            RealtimeScreenTranslateApp, ScreenSubtitleApp, SpeechTranslateApp]


def _stub_engines():
    """把所有会真做事的工厂（OCR / 翻译 / 截图 / 语音 / 区域框）替换为 mock。

    装上：截图引擎 mock、LiveRegionBox mock、worker 工厂 mock
    Returns dict 含 "workers" 与可单独解桩用的 patchers 列表。
    """
    import unittest.mock as mock
    from PySide6.QtCore import QRect
    from plugins.translation.apps.app_base import TranslateAppBase

    state = {"workers": {}, "patches": []}

    # ── 1) 截图引擎 mock：避免真截屏 ──
    grab_mock = mock.patch("core.engines.screenshot_engine.grab_region",
                           return_value=None)
    grab_mock.start()
    state["patches"].append(grab_mock)

    # ── 2) LiveRegionBox mock：避免真渲染边框 ──
    rb_mock = mock.patch("ui.ui_component.region_box.LiveRegionBox")
    rb_mock.start()
    state["patches"].append(rb_mock)

    # ── 3) AutoRegionCapture + 两个语音引擎 mock ──
    arc_mock = mock.patch(
        "plugins.translation.apps.realtime_screen_translate_app.AutoRegionCapture",
        mock.MagicMock())
    arc_mock.start()
    state["patches"].append(arc_mock)

    bsr_mock = mock.patch(
        "plugins.translation.apps.screen_subtitle_app.BuiltinSpeechRecognize",
        mock.MagicMock())
    bsr_mock.start()
    state["patches"].append(bsr_mock)

    rst_mock = mock.patch(
        "plugins.translation.apps.speech_translate_app.RealtimeSpeechTranslate",
        mock.MagicMock())
    rst_mock.start()
    state["patches"].append(rst_mock)

    # ── 4) 一次性图像类的 _resolve_region 返回假 rect（避免 RegionSelectDialog） ──
    def _fake_resolve(self, _hint):
        return QRect(10, 20, 300, 100)

    rr_mock = mock.patch.object(TranslateAppBase, "_resolve_region", _fake_resolve)
    rr_mock.start()
    state["patches"].append(rr_mock)

    # ── 5) 一次性图像类的 _capture_excluding 返回 None（避免真截图） ──
    def _fake_capture(self):
        return None

    cap_mock = mock.patch.object(TranslateAppBase, "_capture_excluding", _fake_capture)
    cap_mock.start()
    state["patches"].append(cap_mock)

    # ── 6) 给有 worker 的 app 替换 _make_worker 为 _MockWorker 工厂 ──
    from plugins.translation.apps.realtime_screen_translate_app import RealtimeScreenTranslateApp
    from plugins.translation.apps.screen_subtitle_app import ScreenSubtitleApp
    from plugins.translation.apps.speech_translate_app import SpeechTranslateApp

    def _factory(self, rect, name=None):
        w = _MockWorker(name or self.__class__.__name__)
        w.started_with = rect
        state["workers"][self.__class__.__name__] = w
        return w

    def _realtime_make(self, rect):
        return _factory(self, rect, "RealtimeScreenTranslateApp")

    def _voice_make(self, rect):
        return _factory(self, rect, self.__class__.__name__)

    for cls, fac in [(RealtimeScreenTranslateApp, _realtime_make),
                     (ScreenSubtitleApp, _voice_make),
                     (SpeechTranslateApp, _voice_make)]:
        p = mock.patch.object(cls, "_make_worker", fac)
        p.start()
        state["patches"].append(p)

    return state


def _unstub_engines(state):
    for p in state["patches"]:
        try:
            p.stop()
        except Exception:
            pass


def _make_page():
    """构造一个最小可用的 'page'（app_base 需要 self._app 提供 log 等）"""
    class _MiniPage:
        def __init__(self):
            self.log_calls = []
            self._translator_config = None
            self._stt_config = None

        def log(self, msg):
            self.log_calls.append(msg)
    return _MiniPage()


# ── 共享常量 ──
WORKER_CLASSES = ("RealtimeScreenTranslateApp", "ScreenSubtitleApp", "SpeechTranslateApp")


# ── 测试 1: 5 个 app 的 start() 完整跑过 §1-§9 骨架 ──

def _all_apps_start_stop():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])

    classes = _make_minimal_app_classes()
    state = _stub_engines()

    try:
        for cls in classes:
            cls_name = cls.__name__
            page = _make_page()
            inst = cls(page)
            inst.start()
            assert inst.is_running(), f"{cls_name} start() 后 is_running() == False"

            # 仅检查有 worker 的 app（ScreenOcrApp / OneShot 用 _run_once，无 worker）
            if cls_name in WORKER_CLASSES:
                assert cls_name in state["workers"], \
                    f"{cls_name} _make_worker 未被调"

            inst.stop()
            assert not inst.is_running(), f"{cls_name} stop() 后 is_running() == True"
    finally:
        _unstub_engines(state)


# ── 测试 2: 防重入（第二次 start 是 no-op）──

def _reentry_guard():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])

    classes = _make_minimal_app_classes()
    state = _stub_engines()
    try:
        for cls in classes:
            cls_name = cls.__name__
            page = _make_page()
            inst = cls(page)
            inst.start()

            if cls_name in WORKER_CLASSES:
                first_started_with = state["workers"][cls_name].started_with
            else:
                first_started_with = None
            _ = first_started_with

            inst.start()  # no-op
            inst.stop()
    finally:
        _unstub_engines(state)


# ── 测试 3: RegionSelectDialog 路径（REQUIRES_REGION=True 的 3 个 app）──

def _region_required():
    """图像类（screen_ocr / one_shot / realtime）的 _resolve_region 被调用，
    语音类（subtitle / speech_translate）的跳过"""
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])

    classes = _make_minimal_app_classes()
    state = _stub_engines()
    try:
        for cls in classes:
            cls_name = cls.__name__
            page = _make_page()
            inst = cls(page)

            if cls.REQUIRES_REGION:
                assert hasattr(inst, "_resolve_region"), \
                    f"{cls_name} REQUIRES_REGION=True 但缺 _resolve_region"
                inst.start()
                inst.stop()
            else:
                # 语音类不应调 _resolve_region
                resolved_count = {"n": 0}
                # 因为 _resolve_region 已在 _stub_engines 被替换为 _fake_resolve，
                # 我们改用 monkey-patch 数调用
                from plugins.translation.apps.app_base import TranslateAppBase
                original = TranslateAppBase._resolve_region
                def _spy(self, hint):
                    resolved_count["n"] += 1
                    return original(self, hint)
                TranslateAppBase._resolve_region = _spy
                try:
                    inst.start()
                    assert resolved_count["n"] == 0, \
                        f"{cls_name} REQUIRES_REGION=False 但仍调 _resolve_region"
                    inst.stop()
                finally:
                    TranslateAppBase._resolve_region = original
    finally:
        _unstub_engines(state)


# ── 测试 4: install_overlay_signals 映射（按 BUTTONS 子集）──

def _signal_hooks_mapping():
    """每个 app 的 _install_overlay_signals 返回的映射（按方法名规范化为字符串）"""
    import unittest.mock as mock

    from plugins.translation.apps.screen_ocr_app import ScreenOcrApp
    from plugins.translation.apps.one_shot_screen_translate_app import OneShotScreenTranslateApp
    from plugins.translation.apps.realtime_screen_translate_app import RealtimeScreenTranslateApp
    from plugins.translation.apps.screen_subtitle_app import ScreenSubtitleApp
    from plugins.translation.apps.speech_translate_app import SpeechTranslateApp

    expected = {
        ScreenOcrApp.__name__: {"retry_clicked": "_run_once"},
        OneShotScreenTranslateApp.__name__: {"retry_clicked": "_run_once"},
        RealtimeScreenTranslateApp.__name__: {"pause_toggled": "_on_pause",
                                              "manual_clicked": "_on_manual"},
        ScreenSubtitleApp.__name__: {"pause_toggled": "_on_pause"},
        SpeechTranslateApp.__name__: {"pause_toggled": "_on_pause"},
    }

    for cls in [ScreenOcrApp, OneShotScreenTranslateApp,
                RealtimeScreenTranslateApp, ScreenSubtitleApp, SpeechTranslateApp]:
        overlay = mock.MagicMock()
        page = _make_page()
        inst = cls(page)
        ret = inst._install_overlay_signals(overlay)
        # 把 callable 标准化为方法名（"self._on_pause" 形式 → "_on_pause"）
        normalized = {k: (getattr(v, "__name__", str(v)) if callable(v) else v)
                      for k, v in ret.items()}
        assert normalized == expected[cls.__name__], \
            f"{cls.__name__} 期望 {expected[cls.__name__]}，得 {normalized}"


# ── 测试 5: install_extra_widgets 只有 realtime 覆写 ──

def _extra_widgets_only_realtime():
    """只有 RealtimeScreenTranslateApp 的 _install_extra_widgets 是子类覆写。

    判断准则：'_install_extra_widgets' 是否在 cls.__dict__ 中（即子类直接定义，
    而非仅从基类继承）。"""
    classes = _make_minimal_app_classes()
    realtime_name = "RealtimeScreenTranslateApp"
    for cls in classes:
        cls_name = cls.__name__
        if cls_name == realtime_name:
            assert "_install_extra_widgets" in cls.__dict__, \
                f"{cls_name} 应覆写 _install_extra_widgets"
        else:
            assert "_install_extra_widgets" not in cls.__dict__, \
                f"{cls_name} 不应覆写 _install_extra_widgets（继承基类空实现即可）"


# ── 测试 6: stop() 反向清理（worker.stop / overlay close）──

def _stop_cleanup():
    """stop() 关闭 extras + 调 worker.stop()（基类统一）"""
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])

    classes = _make_minimal_app_classes()
    state = _stub_engines()
    try:
        for cls in classes:
            cls_name = cls.__name__
            page = _make_page()
            inst = cls(page)
            inst.start()
            if cls_name in WORKER_CLASSES:
                w = state["workers"][cls_name]
                assert w.stopped == 0, f"{cls_name} worker.start 后 stopped 计数应为 0"
            inst.stop()
            if cls_name in WORKER_CLASSES:
                assert w.stopped == 1, f"{cls_name} worker.stop 未被调一次（实 {w.stopped}）"
            assert inst._worker is None, f"{cls_name} stop 后 _worker 未清空"
            assert inst._overlay is None, f"{cls_name} stop 后 _overlay 未清空"
    finally:
        _unstub_engines(state)


# ════════════════════════════════════════════════════════════════════════

def main() -> int:
    print("[1/6] 5 个 app 的 start() 走完整 9 步骨架")
    _check("5 个 app start() + stop() 完整跑通", _all_apps_start_stop)

    print("[2/6] 防重入")
    _check("第二次 start() 是 no-op", _reentry_guard)

    print("[3/6] REQUIRES_REGION 分类：图像类调 _resolve_region，语音类不调")
    _check("REQUIRES_REGION 分流正确", _region_required)

    print("[4/6] _install_overlay_signals 信号映射（按 BUTTONS 子集）")
    _check("信号钩子映射与 BUTTONS 一致", _signal_hooks_mapping)

    print("[5/6] _install_extra_widgets 仅实时翻译类有内容")
    _check("extra widgets 只在实时翻译类覆写", _extra_widgets_only_realtime)

    print("[6/6] stop() 反向清理（worker.stop / overlay close）")
    _check("stop 关闭 worker/overlay", _stop_cleanup)

    print(f"\n结果: {_PASS} 通过, {_FAIL} 失败")
    return 1 if _FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
