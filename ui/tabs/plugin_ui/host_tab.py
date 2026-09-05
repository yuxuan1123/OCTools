"""
OCTools/ui/tabs/plugin_ui/host_tab.py
───────────────────────────────────────────────
desc 模式插件的容器 tab（主进程侧）。

职责：
  - 作为主窗口右侧内容区容器，加载时显示「加载中…」；
  - 请求插件 describe_ui() → 用 DescRenderer 渲染控件树 → 嵌入；
  - 子控件事件 → PluginManager.invoke_action() → 响应含 update 则局部刷新；
  - 插件进程异常（崩溃/重启）时显示提示并自动重连渲染。
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea,
)

from config.ui_config import CONFIG as C
from services.ext_plugins.manager import PluginManager
from ui.tabs.plugin_ui.desc_renderer import DescRenderer
from ui.toast import show_toast


class HostTabWidget(QWidget):
    """desc 模式插件的容器 tab。"""

    def __init__(self, plugin_id: str, parent=None):
        super().__init__(parent)
        self._plugin_id = plugin_id
        self._mgr = PluginManager.instance()
        self._renderer = DescRenderer(plugin_id, self._on_invoke)
        self._inner = None
        self._build_ui()
        # 信号接线：结构化响应 → 渲染；状态变化 → 提示/重连
        self._mgr.call_response.connect(self._on_call_response)
        self._mgr.plugin_state_changed.connect(self._on_plugin_state)
        self._reload()

    # ── 信号入口（按插件过滤）─────────────────
    def _on_call_response(self, plugin_id: str, ok: bool, result):
        if plugin_id != self._plugin_id:
            return
        self.on_call_result(ok, result)

    def _on_plugin_state(self, plugin_id: str, state: str):
        if plugin_id != self._plugin_id:
            return
        self.on_plugin_state(state)

    # ── 构建 ──────────────────────────────
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(C.size("card_spacing"))

        self._status = QLabel("加载中…")
        self._status.setObjectName("hint")
        self._status.setAlignment(Qt.AlignCenter)
        self._status.setWordWrap(True)
        outer.addWidget(self._status)

        self._body = QWidget()
        self._body.setObjectName("bareSurface")
        self._body_lay = QVBoxLayout(self._body)
        self._body_lay.setContentsMargins(0, 0, 0, 0)
        self._body_lay.setSpacing(C.size("card_spacing"))
        self._body_lay.setAlignment(Qt.AlignTop)
        outer.addWidget(self._body)
        self._body.setVisible(False)

    def _set_status(self, text: str, error: bool = False):
        self._status.setText(text)
        self._status.setVisible(True)
        self._body.setVisible(False)

    # ── 渲染 ──────────────────────────────
    def _reload(self):
        """请求插件控件树并渲染。"""
        self._set_status("加载中…")
        self._mgr.call(self._plugin_id, "describe_ui")

    def on_call_result(self, ok: bool, result):
        """接收 describe_ui / invoke_action 的响应。

        result 为字符串（旧日志通道）时原样展示；为 dict 时按协议渲染。
        协议扩展：响应可带 "toast": {"message": ..., "kind": success|info|warn}，
        由主进程统一弹出轻提示（子进程不直接 import ui.toast）。
        """
        if not ok:
            self._set_status(f"插件调用失败：{result}", error=True)
            return
        if isinstance(result, dict):
            self._show_response_toast(result.get("toast"))
            update = result.get("update")
            if isinstance(update, dict):
                self._renderer.apply_update(update)
                return
            desc = result.get("ui") or result
            if isinstance(desc, dict) and "type" in desc:
                self._apply_desc(desc)
                return
            # 无控件树：展示返回的 result 文本
            text = result.get("result") if isinstance(result.get("result"), str) else ""
            self._set_status(text or "插件已返回结果")
        else:
            self._set_status(str(result))

    def _show_response_toast(self, toast):
        """响应内嵌 toast 协议 → ui.toast 轻提示。"""
        if not isinstance(toast, dict):
            return
        message = toast.get("message")
        if not message:
            return
        kind = toast.get("kind", "success")
        show_toast(self, str(message), kind=kind)

    def _apply_desc(self, desc: dict):
        """用渲染器重建内容区。"""
        while self._body_lay.count():
            it = self._body_lay.takeAt(0)
            w = it.widget()
            if w is not None:
                w.deleteLater()
        widget = self._renderer.render(desc)
        self._body_lay.addWidget(widget)
        self._status.setVisible(False)
        self._body.setVisible(True)

    def _on_invoke(self, action_id: str, params: dict):
        """子控件事件 → invoke_action。"""
        self._mgr.invoke_action(self._plugin_id, action_id, params)

    # ── 生命周期 ──────────────────────────
    def on_plugin_state(self, state: str):
        """插件进程状态变化时给出反馈（崩溃自动重连由 manager 负责）。"""
        if state in ("CRASHED", "STOPPING", "STARTING"):
            self._set_status("插件进程状态变化，正在恢复…")

    def closeEvent(self, event):
        super().closeEvent(event)
