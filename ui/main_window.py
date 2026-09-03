"""
octool/ui/main_window.py
───────────────────────────────────────────────
主窗口组装与 tab 动态加载。

- 以 TestWindow（split_titlebar.py）为主窗口框架，左侧 LeftSidebar、右侧内容区。
- tab 注册统一走 manifests：class_name + module_path 决定导入模块与类；
  未声明 module_path 时回退到 `tabs.<蛇形类名>` 推导。
- 设置页（settings.json）同样通过 module_path 注册。
"""

import sys
import re
import importlib
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel   # 补上 QLabel
from PySide6.QtCore import Qt, QTimer

from ui.ui_component.split_titlebar import TestWindow
from ui.ui_component.left_sidebar import LeftSidebar

from ui.theme import apply_theme


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


class MainApp:
    def __init__(self):
        self.window = TestWindow()
        self.window.setWindowTitle("OCTools - 文件格式转换")

        # 左侧栏
        self.sidebar = LeftSidebar()
        self.window.set_left_content(self.sidebar)

        # 右侧 widget 缓存（按 class_name 缓存）
        self._right_widgets = {}

        # 当前激活的 tab（主题切换后重建成该页）
        self._current = None

        # 连接信号
        self.sidebar.entry_clicked.connect(self._on_entry_clicked)
        # 主题切换不再重建页面：apply_theme 调 app.setStyleSheet 时会向所有
        # widget 派发 QEvent.StyleChange，已接入 StyleHookMixin 的控件自动重刷
        # 内联样式，滚动位置 / 展开状态 / 输入内容全部保留。

        # 默认显示第一个 tab
        if self.sidebar.tab_infos:
            first = self.sidebar.tab_infos[0]
            self._switch_to(first["name"], first["class_name"], first.get("module_path"))
        self._preimport_all_tabs()

    def _preimport_all_tabs(self):
        """提前导入所有 tab 模块，避免首次切换时的延迟"""
        for info in self.sidebar.tab_infos:
            class_name = info["class_name"]
            module_name = _resolve_module_path(class_name, info.get("module_path"))
            try:
                importlib.import_module(module_name)
            except Exception as e:
                print(f"[预导入] {module_name} 失败: {e}")

    def _get_or_create_widget(self, class_name: str, module_path: str = None) -> QWidget:
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

    def _on_entry_clicked(self, name: str, class_name: str, module_path: str = None):
        self._switch_to(name, class_name, module_path)

    def _switch_to(self, name: str, class_name: str, module_path: str = None):
        widget = self._get_or_create_widget(class_name, module_path)
        self._current = (name, class_name, module_path)
        self.window.set_right_content(widget)

    def show(self):
        self.window.show()


def main():
    app = QApplication(sys.argv)
    from config import presets
    apply_theme(app, presets.load_app_settings() or {}, notify=False)   # 全局应用已保存主题
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
