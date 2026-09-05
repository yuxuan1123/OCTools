"""
OCTools/ui/ui_component/window_ctl.py
──────────────────────────────────────────────────────────
顶层窗口显隐控制（通用组件层）。

适用场景：截图 / 框选 / 字幕浮窗等需要「先让主窗口让开」的功能，
典型如：
  - 翻译页五个最终应用启动前（app_controller.start_app）
  - 「设置 → 截图区域」的框选按钮（set_screen_region._pick_region）

── 本模块存在的唯一理由（Qt 硬约束）──
业务代码拿到的宿主几乎总是 **页面子控件**（tab 页经 `_Pane.set_body` →
`addWidget` 被 reparent 进主窗口）。而 Qt 的窗口状态 / 可见性操作只对
`isWindow()` 为真的顶层窗口生效：

    child.showMinimized()   → 空操作（子控件，静默无效）
    child.hide()            → 藏的是子控件本身，主窗口纹丝不动
    self.parent().hide()    → parent 往往也是子控件，同样藏错对象

正确姿势是先 `widget.window()` 解析出顶层窗口再操作 —— 本模块封装的就是
这套「解析 + 操作 + 等落地」的组合。

── 为什么要 pump ──
showMinimized() / hide() 只是投递请求，窗口动画与合成器需要事件循环配合。
不泵事件就立刻截图，抓到的很可能是还没缩下去的主窗口。

── 时间参数 ──
来自 config/ui_config.json → timing 段：
    minimize_settle_ms        最小化/隐藏后泵事件的时长（等动画落地）
    minimize_wait_timeout_ms  截图前等待「真的已最小化」的上限
    capture_delay_ms          最小化确认后到真正抓帧的延迟
    pump_step_ms              泵事件循环的单步睡眠

── 策略留给调用方 ──
本模块不做策略判断，只提供原子操作。是否恢复由调用方决定：
  - 应用启动（app_controller）：最小化后**不恢复**，用户从任务栏/托盘手动恢复；
  - 模态设置对话框（set_screen_region）：框选结束后**必须恢复**，否则用户以为卡死。
"""

import time

from PySide6.QtCore import QElapsedTimer
from PySide6.QtWidgets import QApplication

from config.ui_config import CONFIG as C

# 配置缺失/被改坏时的兜底值（保证行为依旧可用）
_FALLBACK_SETTLE_MS = 220
_FALLBACK_TIMEOUT_MS = 900
_FALLBACK_DELAY_MS = 120
_FALLBACK_STEP_MS = 8


def top_window(widget):
    """返回 widget 所在的顶层窗口；解析不到（或入参为 None）时返回 None。"""
    if widget is None:
        return None
    try:
        w = widget.window()
    except RuntimeError:      # C++ 对象已销毁
        return None
    except Exception:
        return None
    return w if (w is not None and w.isWindow()) else None


def is_minimized(widget) -> bool:
    """主窗口当前是否处于最小化状态（传页面子控件同样有效）。"""
    w = top_window(widget)
    return bool(w is not None and w.isMinimized())


def _step_ms() -> int:
    s = C.timing("pump_step_ms", _FALLBACK_STEP_MS)
    return max(1, min(50, s))


def pump(ms: int, step_ms: int = None):
    """阻塞 ms 毫秒，期间持续泵送 Qt 事件，保证窗口操作真正落地。"""
    if ms <= 0:
        return
    step = step_ms if isinstance(step_ms, int) and step_ms > 0 else _step_ms()
    step = max(1, min(50, step))
    t = QElapsedTimer()
    t.start()
    while t.elapsed() < ms:
        QApplication.processEvents()
        try:
            QApplication.sendPostedEvents()
        except Exception:
            pass
        time.sleep(step / 1000.0)


def _settle(settle_ms) -> int:
    if isinstance(settle_ms, int) and settle_ms >= 0:
        return settle_ms
    return max(0, C.timing("minimize_settle_ms", _FALLBACK_SETTLE_MS))


def minimize_host(host, settle_ms: int = None) -> bool:
    """最小化主窗口（截图 / 框选 / 字幕浮窗前调用）。

    - host 可以是页面子控件（内部自动 window() 取顶层窗口）
    - 已最小化 / 未显示 / 解析不到主窗口 → 返回 False，不做任何事
    - 幂等：重复调用不会重复触发动画
    """
    win = top_window(host)
    if win is None or not win.isVisible() or win.isMinimized():
        return False
    try:
        win.showMinimized()
    except Exception:
        return False
    pump(_settle(settle_ms))
    return True


def ensure_minimized(host, timeout_ms: int = None) -> bool:
    """确保主窗口处于最小化状态（截图前兜底，有上限不卡死）。

    未最小化时先补一次最小化请求（幂等），再等它真正落地；主窗口本就隐藏
    视为通过。返回 True 表示已确认最小化；超时返回 False（此时截图可能拍到
    主窗口，但绝不无限阻塞用户）。
    """
    win = top_window(host)
    if win is None:
        return False
    if win.isMinimized():
        return True
    if not win.isVisible():
        return True          # 主窗口本来就藏着，不算遮挡
    minimize_host(host, settle_ms=0)
    ms = timeout_ms if isinstance(timeout_ms, int) and timeout_ms > 0 \
        else C.timing("minimize_wait_timeout_ms", _FALLBACK_TIMEOUT_MS)
    step = _step_ms()
    t = QElapsedTimer()
    t.start()
    while t.elapsed() < ms:
        QApplication.processEvents()
        try:
            QApplication.sendPostedEvents()
        except Exception:
            pass
        if win.isMinimized():
            return True
        time.sleep(step / 1000.0)
    return win.isMinimized()


def restore_host(host, settle_ms: int = None) -> bool:
    """把最小化的主窗口恢复显示（模态任务结束后调用）。

    幂等：主窗口本来就没最小化 / 解析不到 → 返回 False。
    恢复后会 raise_ + activateWindow，确保窗口抢到前台。
    """
    win = top_window(host)
    if win is None or not win.isMinimized():
        return False
    try:
        win.showNormal()
        win.raise_()
        win.activateWindow()
    except Exception:
        return False
    pump(_settle(settle_ms))
    return True


def capture_delay_ms() -> int:
    """最小化确认后到真正抓帧的延迟（等窗口动画完全消失）。"""
    return max(0, C.timing("capture_delay_ms", _FALLBACK_DELAY_MS))
