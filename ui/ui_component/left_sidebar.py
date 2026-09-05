"""
OCTools/ui/ui_component/left_sidebar.py
───────────────────────────────────────
左侧功能导航栏：根据 manifests 目录动态生成入口按钮。

视觉/布局参数来自 config/ui_config.json 的 sidebar 段。
tab 注册支持 module_path：JSON 中 class_name + module_path 决定导入模块与类。
"""
import os
import json
from typing import List, Dict, Any

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QScrollArea,
    QLabel, QButtonGroup
)
from config.ui_config import CONFIG as C
from ui.style_hook import StyleHookMixin
from .button_component import create_function_entry_button
from ui.icon_res import nav_icon, NAV_ICON_SIZE, NAV_ICON_NAMES
from ui.tabs.plugin_registry import (
    iter_manifest_dirs,
    ensure_plugin_dirs as _ensure_plugin_dirs,
)


def _align(qt_align_str: str) -> Qt.AlignmentFlag:
    mapping = {
        "left": Qt.AlignLeft,
        "center": Qt.AlignCenter,
        "right": Qt.AlignRight,
        "top": Qt.AlignTop,
        "bottom": Qt.AlignBottom,
    }
    return mapping.get(qt_align_str.lower(), Qt.AlignCenter)


def _margins(margin_list: list) -> tuple:
    if len(margin_list) != 4:
        return (0, 0, 0, 0)
    return tuple(margin_list)


class LeftSidebar(StyleHookMixin, QWidget):
    """左侧功能导航栏。

    标题与空态提示的内联样式随主题变化，故混入 StyleHookMixin：
    主题切换时由 QEvent.StyleChange 自动重刷。
    """

    entry_clicked = Signal(str, str, str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cfg = C.section("sidebar")
        self._title_label = None
        self._empty_hint = None

        # 窗口设置
        win_cfg = self.cfg.get("window", {})
        self.setWindowTitle(win_cfg.get("title", "OCTools"))

        # 主布局
        layout_cfg = self.cfg.get("layout", {})
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(*_margins(layout_cfg.get("margins", [0, 0, 0, 0])))
        main_layout.setSpacing(layout_cfg.get("spacing", 15))

        # 标题
        title_cfg = self.cfg.get("title", {})
        self._title_label = QLabel(title_cfg.get("text", "OCTools"))
        self._title_label.setAlignment(_align(title_cfg.get("alignment", "center")))
        main_layout.addWidget(self._title_label)

        # 滚动区域
        scroll_cfg = self.cfg.get("scroll_area", {})
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        h_policy = scroll_cfg.get("horizontal_scrollbar", "off").upper()
        v_policy = scroll_cfg.get("vertical_scrollbar", "as_needed").upper()
        scroll_area.setHorizontalScrollBarPolicy(
            getattr(Qt.ScrollBarPolicy, f"ScrollBar{h_policy}", Qt.ScrollBarAlwaysOff)
        )
        scroll_area.setVerticalScrollBarPolicy(
            getattr(Qt.ScrollBarPolicy, f"ScrollBar{v_policy}", Qt.ScrollBarAsNeeded)
        )
        scroll_area.setObjectName("bareScroll")

        scroll_widget = QWidget()
        scroll_widget.setObjectName("bareSurface")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(scroll_cfg.get("button_spacing", 10))

        # 扫描 tab 信息
        try:
            _ensure_plugin_dirs()
        except OSError as e:
            print(f"警告：插件清单目录不可用：{e}")
        self.tab_infos = []
        for _m_dir in iter_manifest_dirs():
            self.tab_infos += self._scan_tab_infos(_m_dir)
        self.tab_infos.sort(key=lambda x: (x["order"], x["name"]))

        # 生成按钮
        button_group = QButtonGroup(self)
        button_group.setExclusive(True)

        btn_cfg = self.cfg.get("button", {})
        btn_fixed_width = btn_cfg.get("fixed_width", 220)
        btn_fixed_height = btn_cfg.get("fixed_height", C.size("btn_h"))
        btn_checkable = btn_cfg.get("checkable", True)

        empty_cfg = self.cfg.get("empty_hint", {})

        if not self.tab_infos:
            self._empty_hint = QLabel(
                empty_cfg.get("text", "暂无可用工具，请在 manifests 下添加 JSON 配置文件"))
            self._empty_hint.setAlignment(_align(empty_cfg.get("alignment", "center")))
            scroll_layout.addWidget(self._empty_hint)
        else:
            for info in self.tab_infos:
                name = info["name"]
                class_name = info["class_name"]
                module_path = info.get("module_path")
                plugin_id = info.get("plugin_id", "")
                ui_mode = info.get("ui_mode", "direct")
                btn = create_function_entry_button(
                    text=name,
                    on_click=lambda checked, n=name, cn=class_name, mp=module_path,
                        pid=plugin_id, um=ui_mode: self.entry_clicked.emit(n, cn, mp, pid, um),
                    fixed_width=btn_fixed_width,
                    fixed_height=btn_fixed_height,
                    checkable=btn_checkable,
                )
                if name in NAV_ICON_NAMES:
                    btn.setIcon(nav_icon(name, False))
                    btn.setIconSize(QSize(NAV_ICON_SIZE, NAV_ICON_SIZE))
                    btn.toggled.connect(
                        lambda checked, b=btn, n=name: b.setIcon(nav_icon(n, checked))
                    )
                button_group.addButton(btn)
                btn_container = QVBoxLayout()
                btn_container.setContentsMargins(0, 0, 0, 0)
                btn_container.addWidget(btn)
                scroll_layout.addLayout(btn_container)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)

        self._apply_inline_style()

    def _apply_inline_style(self):
        """重刷侧栏自身底色、标题与空态提示（样式钩子混入时自动调用）。

        必须幂等：单次 app.setStyleSheet 会重复派发 2~4 次 StyleChange。
        """
        bg = C.color("sidebar_bg") or self.cfg.get("background", "#F5F5F5")
        self.setStyleSheet(f"background-color: {bg};")

        if self._title_label is not None:
            tc = self.cfg.get("title", {})
            self._title_label.setStyleSheet(
                f"font-size: {tc.get('font_size', 0)}px; "
                f"font-weight: {tc.get('font_weight', 'bold')}; "
                f"color: {C.color('text') or tc.get('color', '#333333')}; "
                f"margin-bottom: {tc.get('margin_bottom', 0)}px;"
            )

        if self._empty_hint is not None:
            ec = self.cfg.get("empty_hint", {})
            self._empty_hint.setStyleSheet(
                f"color: {C.color('text_light') or ec.get('color', '#999999')}; "
                f"font-size: {ec.get('font_size', 13)}px;"
            )

    def _scan_tab_infos(self, json_dir: str) -> List[dict]:
        """扫描单目录下的 JSON，返回 [{name, class_name, module_path, order, plugin_id, ui_mode}, ...]"""
        infos = []
        if not os.path.isdir(json_dir):
            return infos
        for fname in sorted(os.listdir(json_dir)):
            if not fname.lower().endswith(".json"):
                continue
            fpath = os.path.join(json_dir, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                name = data.get("name", "").strip()
                class_name = data.get("class_name", "").strip()
                if not name or not class_name:
                    continue
                order = data.get("order", 9999)
                module_path = data.get("module_path", "").strip() or None
                infos.append({
                    "name": name,
                    "class_name": class_name,
                    "module_path": module_path,
                    "order": order,
                    # 外部插件以 manifest 文件名作 plugin_id（desc/window 模式定位用）
                    "plugin_id": fname[:-5] if fname.lower().endswith(".json") else fname,
                    "ui_mode": data.get("ui_mode", "direct"),
                })
            except Exception as e:
                print(f"读取 {fpath} 出错: {e}")
        return infos