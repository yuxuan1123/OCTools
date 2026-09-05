"""
OCTools/ui/main_window.py
───────────────────────────────────────────────
主窗口组装与 tab 动态加载。

- 以 TestWindow（split_titlebar.py）为主窗口框架，左侧 LeftSidebar、右侧内容区。
- tab 注册统一走 manifests：class_name + module_path 决定导入模块与类；
  未声明 module_path 时回退到 `tabs.<蛇形类名>` 推导。
- 设置页（settings.json）同样通过 module_path 注册。
"""

import sys
import re
import os
import json
import importlib
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel   # 补上 QLabel
from PySide6.QtCore import Qt, QTimer

from ui.ui_component.split_titlebar import TestWindow
from ui.ui_component.left_sidebar import LeftSidebar
from ui.ui_component.hotkeys import (
    HotkeyService, ERR_OCCUPIED, ERR_INVALID, ERR_UNAVAILABLE,
)

from ui.theme import apply_theme
from ui.toast import show_toast
from services.ext_plugins import detection
from services.ext_plugins.manager import PluginManager
from ui.tabs.plugin_ui.host_tab import HostTabWidget
from ui.tabs.plugin_registry import iter_manifest_dirs


def camel_to_snake(name: str) -> str:
    """
    驼峰命名转蛇形命名，例如：
    TabConversion -> tab_conversion
    PDFToWord   -> pdf_to_word
    """
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def _resolve_module_path(class_name: str, module_path: str = None) -> str:
    """返回可导入的模块名：优先用 manifests 的 module_path，否则按类名推导。"""
    if module_path:
        return module_path
    return f"tabs.{camel_to_snake(class_name)}"


def _iter_manifest_hotkeys():
    """遍历所有 manifest，产出 (manifest, 热键声明)；仅 direct 模式插件参与。

    非 direct（desc/window）插件由隔离子进程承载，热键后续走 IPC 注册，
    本轮不在主进程装配。
    """
    for directory in iter_manifest_dirs():
        try:
            names = sorted(os.listdir(directory))
        except OSError:
            continue
        for n in names:
            if not n.endswith(".json"):
                continue
            fpath = os.path.join(directory, n)
            try:
                with open(fpath, encoding="utf-8") as f:
                    manifest = json.load(f)
            except (OSError, ValueError):
                continue
            if manifest.get("ui_mode", "direct") != detection.UI_DIRECT:
                continue
            for decl in manifest.get("hotkeys") or []:
                yield manifest, decl


_ERR_TEXT = {
    ERR_OCCUPIED: "已被其他程序占用",
    ERR_INVALID: "格式非法",
    ERR_UNAVAILABLE: "当前系统不支持全局热键",
}


def _make_hotkey_cb(main_app: "MainApp", manifest: dict, decl: dict):
    """构造热键回调：取该插件 tab widget → 调 widget.<action>(**params)。"""
    def cb():
        action = decl.get("action")
        params = decl.get("params") or {}
        widget = main_app._get_or_create_widget(
            manifest.get("class_name", ""),
            manifest.get("module_path"),
            manifest.get("plugin_id", ""),
            manifest.get("ui_mode", detection.UI_DIRECT))
        fn = getattr(widget, action, None)
        if not callable(fn):
            print(f"[热键] 插件 {manifest.get('name')} 缺少方法 {action}")
            return
        try:
            fn(**params)
        except Exception as e:  # noqa: BLE001 - 热键回调不因插件异常影响主进程
            print(f"[热键] {action} 执行失败: {e}")
    return cb


class MainApp:
    def __init__(self):
        self.window = TestWindow()
        self.window.setWindowTitle("OCTools - 文件格式转换")

        # 左侧栏
        self.sidebar = LeftSidebar()
        self.window.set_left_content(self.sidebar)

        # 右侧 widget 缓存
        self._right_widgets = {}

        # 当前激活的 tab
        self._current = None

        # 连接信号
        self.sidebar.entry_clicked.connect(self._on_entry_clicked)
        # 主题切换不再重建页面：apply_theme 调 app.setStyleSheet 时会向所有
        # widget 派发 QEvent.StyleChange，已接入 StyleHookMixin 的控件自动重刷
        # 内联样式，滚动位置 / 展开状态 / 输入内容全部保留。

        # 默认显示第一个 tab
        if self.sidebar.tab_infos:
            first = self.sidebar.tab_infos[0]
            self._switch_to(
                first["name"], first["class_name"], first.get("module_path"),
                first.get("plugin_id", ""), first.get("ui_mode", "direct"))
        self._preimport_all_tabs()
        self._install_hotkeys()

    def _install_hotkeys(self):
        """装配 manifest 声明的全局热键（direct 插件通用机制）。

        - 遍历所有 manifest 的 hotkeys 段 → HotkeyService.bind；
        - 回调 = 取该插件 tab widget 实例 → 调 widget.<action>(**params)；
        - 绑定失败按原因 toast 提示；窗口隐藏/最小化到托盘时全局热键仍生效。
        """
        self._hotkeys = HotkeyService(self.window)
        failed = []
        for manifest, decl in _iter_manifest_hotkeys():
            spec = decl.get("spec")
            if not spec:
                continue
            if not self._hotkeys.bind(spec, _make_hotkey_cb(self, manifest, decl)):
                reason = _ERR_TEXT.get(self._hotkeys.last_error,
                                       "未知原因")
                failed.append(f"{spec}（{reason}）")
        if failed:
            QTimer.singleShot(1200, lambda: show_toast(
                self.window,
                "热键绑定失败：" + "、".join(failed),
                kind="warn"))

    def _preimport_all_tabs(self):
        """提前导入 direct 模式 tab 模块，避免首次切换时的延迟。
        desc/window 插件由子进程加载，主进程不 import。
        """
        for info in self.sidebar.tab_infos:
            if info.get("ui_mode", "direct") != detection.UI_DIRECT:
                continue
            class_name = info["class_name"]
            module_name = _resolve_module_path(class_name, info.get("module_path"))
            try:
                importlib.import_module(module_name)
            except Exception as e:
                print(f"[预导入] {module_name} 失败: {e}")

    def _placeholder_page(self, text: str) -> QWidget:
        """desc/window 模式切换时的占位页。"""
        placeholder = QWidget()
        layout = QVBoxLayout(placeholder)
        label = QLabel(text)
        label.setObjectName("hint")
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        layout.addWidget(label)
        return placeholder

    def _get_or_create_widget(self, class_name: str, module_path: str = None,
                              plugin_id: str = "", ui_mode: str = detection.UI_DIRECT) -> QWidget:
        # desc/window 以 plugin_id 缓存（同一插件的容器/占位页复用）
        if ui_mode != detection.UI_DIRECT:
            if plugin_id in self._right_widgets:
                return self._right_widgets[plugin_id]
            if ui_mode == detection.UI_DESC:
                widget = HostTabWidget(plugin_id)
            else:  # window：触发子进程自建独立窗口，主进程显示占位页
                PluginManager.instance().activate(plugin_id)
                widget = self._placeholder_page(
                    "已触发独立窗口（由插件子进程自建，可在系统任务栏切换）。\n"
                    "若未出现窗口，请到「插件」页检查依赖是否安装、插件是否启用。")
            self._right_widgets[plugin_id] = widget
            return widget

        if class_name in self._right_widgets:
            return self._right_widgets[class_name]
        module_name = _resolve_module_path(class_name, module_path)
        try:
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            widget = cls()
            self._right_widgets[class_name] = widget
            return widget
        except (ImportError, AttributeError) as e:
            print(f"无法加载 {class_name} (模块 {module_name}): {e}")
            placeholder = QWidget()
            layout = QVBoxLayout(placeholder)
            label = QLabel(f"组件 {class_name} 未找到\n请检查模块路径和类名")
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
            return placeholder

    def _on_entry_clicked(self, name: str, class_name: str, module_path: str = None,
                          plugin_id: str = "", ui_mode: str = detection.UI_DIRECT):
        self._switch_to(name, class_name, module_path, plugin_id, ui_mode)

    def _switch_to(self, name: str, class_name: str, module_path: str = None,
                   plugin_id: str = "", ui_mode: str = detection.UI_DIRECT):
        widget = self._get_or_create_widget(class_name, module_path, plugin_id, ui_mode)
        self._current = (name, class_name, module_path, plugin_id, ui_mode)
        self.window.set_right_content(widget)

    def show(self):
        self.window.show()


def main():
    app = QApplication(sys.argv)
    from config import presets
    apply_theme(app, presets.load_app_settings() or {}, notify=False)   # 全局应用已保存主题
    from services.ext_plugins.manager import PluginManager
    app.aboutToQuit.connect(PluginManager.instance().shutdown)
    main_app = MainApp()
    app.aboutToQuit.connect(main_app._hotkeys.unbind_all)
    main_app.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
