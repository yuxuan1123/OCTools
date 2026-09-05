"""
OCTools/ui/tabs/translation/app_controller.py
──────────────────────────────────────────────────────
最终应用控制：创建应用实例、启动/停止/切换、状态更新、日志追加、退出清理。

所有逻辑照抄原 TranslatePage 的实现（stopped 信号复位、_APP_ROWS 名称、
danger/primary objectName 切换、icon 切换等）。

启动前一律最小化主窗口（window_ctl.minimize_host）：截图类应用不能被主窗口
遮挡，字幕类应用需要独占视野。宿主是页面子控件，必须经 window_ctl 取顶层窗口。
"""

from PySide6.QtCore import QSize

from ui import icon_res

from ui.tabs.translation.registry import _APP_ROWS
from ui.ui_component import window_ctl


def init_apps(page):
    """创建最终应用实例；悬浮窗被关闭（stopped）时自动复位行按钮"""
    for key, (cls, *_rest) in _APP_ROWS.items():
        # 宿主 = 页面自身：提供 log / translator_config / stt_config / screen_region_config / 窗口显隐
        app = cls(page, parent=page)
        app.stopped.connect(lambda k=key: set_app_running(page, k, False))
        page._apps[key] = app


def app(page, key):
    """按 key 获取最终应用实例（main_window 托盘/热键查询用）"""
    return page._apps.get(key)


def is_app_running(page, key) -> bool:
    a = page._apps.get(key)
    return bool(a is not None and a.is_running())


def toggle_app(page, key):
    """启动 ⇄ 停止：页面按钮 / 热键 / 托盘菜单共用入口"""
    a = page._apps.get(key)
    if a is None:
        return
    if is_app_running(page, key):
        stop_app(page, key)
    else:
        start_app(page, key)


def start_app(page, key):
    a = page._apps[key]
    label = _APP_ROWS[key][1]
    # 启动前最小化主窗口：五个应用（3 个截图类 + 屏幕字幕 / 语音翻译）都不该
    # 被主窗口遮挡。此处是页面按钮 / 热键 / 托盘的唯一入口，覆盖全部来源。
    # 注意：宿主是页面子控件，必须经 window_ctl 取顶层窗口才有效。
    try:
        window_ctl.minimize_host(page)
    except Exception:
        pass
    try:
        a.start()
    except Exception as e:
        page.log(f"❌ {label} 启动失败: {e}")
        set_app_running(page, key, False)
        return
    if a.is_running():
        set_app_running(page, key, True)


def stop_app(page, key):
    a = page._apps[key]
    try:
        a.stop()
    except Exception:
        pass
    # stop() 关闭悬浮窗 → stopped 信号已复位按钮；此处再兜底复位一次
    set_app_running(page, key, False)


def set_app_running(page, key, running: bool):
    """更新应用行的 启动/停止 按钮与状态标签"""
    btn = page._app_btns.get(key)
    if btn is None:
        return
    status = page._app_status.get(key)
    _cls, _label, icon, _hint, _hk = _APP_ROWS[key]
    if running:
        btn.setText("停止")
        btn.setIcon(icon_res.colored_icon("square"))
        btn.setObjectName("danger")
        if status is not None:
            status.setText("运行中")
    else:
        btn.setText("启动")
        btn.setIcon(icon_res.colored_icon(icon))
        btn.setObjectName("primary")
        if status is not None:
            status.setText("未启动")
    repolish(btn)


def stop_all_apps(page):
    """退出前停止全部最终应用（幂等）"""
    for key in list(page._apps):
        try:
            page._apps[key].stop()
        except Exception:
            pass


def repolish(w):
    """动态切换 objectName 后刷新样式表（否则新样式不生效）"""
    try:
        w.style().unpolish(w)
        w.style().polish(w)
        w.update()
    except Exception:
        pass


def append_log(page, msg):
    """追加一行日志（主线程调用）"""
    if page.log_text is not None:
        page.log_text.append(msg)
        sb = page.log_text.verticalScrollBar()
        if sb is not None:
            sb.setValue(sb.maximum())


def clear_log(page):
    if page.log_text is not None:
        page.log_text.clear()