"""
octool/ui/tabs/tab_plugin.py
───────────────────────────────────────────────
插件管理页：导入 / 重载 / 卸载本地 tab 插件。

导入流程（用户选两样）：
  1. 插件文件夹（必选）  —— 内含 tab_xxx.py（主类）、set_xxx.py（设置页）及其他依赖；
  2. JSON 清单（必选）    —— 插件清单（name / class_name / order / settings 等）。

选择后实时显示「导入清单预览」：tab 主文件是谁、set_*.py 有哪些、其他文件有哪些，
并在校验通过时允许「开始导入」。整个文件夹内容（含 set_/helper）一律复制进插件目录。

安装位置：
  - 代码：<插件根>/<插件名>/（含 __init__.py，保证可被 importlib 导入）
  - 清单：<插件根>/manifests/<插件名>.json（module_path 指向插件模块）
  - 源码运行时插件根为 ui/tabs/plugins，打包（PyInstaller）后为 exe 同目录 plugins/
    （路径 / 包前缀 / sys.path 挂载统一由 plugin_registry 提供，兼容打包环境）。

安装 / 卸载 / 重载成功后通过 THEME_BUS 广播触发左侧导航重建，
新 tab 按钮立即出现在侧栏。所有视觉/布局参数统一从
config/ui_config.json 读取（CONFIG 单例）。
"""

import ast
import importlib
import json
import os
import re
import shutil

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QFileDialog, QScrollArea, QFrame, QMessageBox, QToolButton,
)

from config.ui_config import CONFIG as C
from ui import icon_res
from ui.theme import THEME_BUS
from ui.tabs.tab_component.page_header import build_page_header

# 插件路径 / 包前缀 / sys.path 挂载 / 模块清理统一走注册表（兼容打包）。
from ui.tabs.plugin_registry import (
    plugins_dir as PLUGINS_DIR,
    plugin_manifests_dir as PLUGIN_MANIFESTS_DIR,
    module_prefix as _module_prefix,
    purge_plugin_modules as _purge_plugin_modules,
    ensure_plugin_dirs as _ensure_dirs,
)


def _top_level_classes(path: str) -> list:
    """ast 解析 .py，返回顶层类名列表（不执行代码）。"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=path)
    except (OSError, SyntaxError) as e:
        raise ValueError(f"无法解析 {os.path.basename(path)}：{e}")
    return [n.name for n in tree.body if isinstance(n, ast.ClassDef)]


def _strip_pycache(root: str):
    """递归清理 __pycache__，保持插件目录干净。"""
    for dirpath, dirnames, _ in os.walk(root, topdown=False):
        for d in dirnames:
            if d == "__pycache__":
                shutil.rmtree(os.path.join(dirpath, d), ignore_errors=True)


# ─────────────────────────────────────────────


class TabPlugin(QWidget):
    """插件管理页：导入 / 查看 / 重载 / 卸载本地 tab 插件。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        _ensure_dirs()
        self._build_ui()

    # ──────────────────────────────────────
    #  布局
    # ──────────────────────────────────────
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(C.size("card_spacing"))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("bareScroll")
        outer.addWidget(scroll)

        content = QWidget()
        content.setObjectName("bareSurface")
        self._cl = QVBoxLayout(content)
        self._cl.setContentsMargins(0, 0, 0, 0)
        self._cl.setSpacing(C.size("card_spacing"))
        self._cl.setAlignment(Qt.AlignTop)

        # ---- 页头 ----
        self._cl.addWidget(build_page_header(content, "page_plugin_title", "page_plugin_sub"))

        # ---- 导入表单（两输入：插件文件夹 + 清单 JSON，含实时清单预览）----
        self._cl.addWidget(self._build_import_card())

        # ---- 已安装插件列表 ----
        list_title = QLabel("已安装插件")
        list_title.setObjectName("cardTitle")
        self._cl.addWidget(list_title)

        list_host = QWidget()
        list_host.setObjectName("bareSurface")
        self._list_lay = QVBoxLayout(list_host)
        self._list_lay.setContentsMargins(0, 0, 0, 0)
        self._list_lay.setSpacing(C.size("card_spacing"))
        self._cl.addWidget(list_host)

        self._render_plugins()

        scroll.setWidget(content)

    # ──────────────────────────────────────
    #  导入表单（两输入：插件文件夹 + 清单 JSON）
    # ──────────────────────────────────────
    def _build_import_card(self) -> QFrame:
        """导入卡片：插件文件夹 + 清单 JSON 两输入，含实时清单预览与开始导入。"""
        card = QFrame()
        card.setObjectName("SettingsSection")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(
            C.size("group_padding_h"), C.size("group_padding_v"),
            C.size("group_padding_h"), C.size("group_padding_v"),
        )
        lay.setSpacing(C.size("form_row_spacing"))

        title = QLabel("导入插件")
        title.setObjectName("cardTitle")
        lay.addWidget(title)

        sub = QLabel("选择一个包含 tab_*.py / set_*.py 的插件文件夹，以及对应的清单 JSON。")
        sub.setObjectName("hint")
        sub.setWordWrap(True)
        lay.addWidget(sub)

        # 1. 插件文件夹（必选）
        self.folder_edit = QLineEdit()
        self.folder_edit.setReadOnly(True)
        self.folder_edit.setPlaceholderText("选择插件文件夹（必选，含 tab_*.py / set_*.py）")
        self._add_path_row(lay, "文件夹", self.folder_edit, "浏览…", self._pick_folder)

        # 2. JSON 清单（必选）
        self.json_edit = QLineEdit()
        self.json_edit.setReadOnly(True)
        self.json_edit.setPlaceholderText("选择插件清单 JSON（必选）")
        self._add_path_row(lay, "清单", self.json_edit, "浏览…", self._pick_json)

        # ── 实时清单预览标题 + 开始导入按钮（同一行，按钮在最右侧）──
        toggle_row = QHBoxLayout()
        toggle_row.setSpacing(C.size("form_row_spacing"))

        self._pv_toggle = QToolButton()
        self._pv_toggle.setObjectName("sectionHeader")
        self._pv_toggle.setCheckable(True)
        self._pv_toggle.setChecked(True)
        self._pv_toggle.setText(self._pv_toggle_text(True))
        self._pv_toggle.toggled.connect(self._toggle_preview)
        toggle_row.addWidget(self._pv_toggle)

        toggle_row.addStretch(1)

        import_btn = QPushButton("开始导入")
        import_btn.setObjectName("ghost")
        import_btn.clicked.connect(self._start_import)
        toggle_row.addWidget(import_btn)

        lay.addLayout(toggle_row)

        # ── 预览内容宿主（可折叠）──
        self._pv_host = QWidget()
        self._pv_host.setObjectName("bareSurface")
        self._pv_lay = QVBoxLayout(self._pv_host)
        self._pv_lay.setContentsMargins(0, 0, 0, 0)
        self._pv_lay.setSpacing(C.size("form_row_spacing"))
        lay.addWidget(self._pv_host)

        self._pv_status = QLabel("")
        self._pv_status.setObjectName("badge")
        self._pv_status.setProperty("ok", "0")
        self._pv_status.style().polish(self._pv_status)
        lay.addWidget(self._pv_status)

        self._update_preview()

        return card

    def _add_path_row(self, lay: QVBoxLayout, label_text: str,
                      edit: QWidget, btn_text: str, slot):
        row = QHBoxLayout()
        row.setSpacing(C.size("form_row_spacing"))
        label = QLabel(label_text)
        label.setFixedWidth(C.size("form_width_90"))
        label.setObjectName("formLabel")
        row.addWidget(label)
        row.addWidget(edit, 1)
        browse_btn = QPushButton(btn_text)
        browse_btn.setObjectName("ghost")
        browse_btn.clicked.connect(slot)
        row.addWidget(browse_btn)
        lay.addLayout(row)

    def _pick_folder(self):
        path = QFileDialog.getExistingDirectory(
            self, "选择插件文件夹（必选，含 tab_*.py / set_*.py）", "")
        if path:
            self.folder_edit.setText(path)
            self._update_preview()

    def _pick_json(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择插件清单 JSON（必选）", "", "JSON 文件 (*.json)")
        if path:
            self.json_edit.setText(path)
            self._update_preview()

    # ──────────────────────────────────────
    #  导入清单预览（tab / set / 其他 分类）
    # ──────────────────────────────────────
    def _scan_plugin_folder(self, folder: str):
        """扫描插件文件夹，分类返回 (tab_*.py, set_*.py, 其他文件)。"""
        tab_files, set_files, other_files = [], [], []
        if not folder or not os.path.isdir(folder):
            return tab_files, set_files, other_files
        for fn in sorted(os.listdir(folder)):
            fp = os.path.join(folder, fn)
            if not os.path.isfile(fp):
                continue
            if fn.startswith("tab_") and fn.endswith(".py"):
                tab_files.append(fn)
            elif fn.startswith("set_") and fn.endswith(".py"):
                set_files.append(fn)
            else:
                other_files.append(fn)
        return tab_files, set_files, other_files

    def _resolve_main_tab_file(self, folder: str, class_name: str):
        """在文件夹中定位含 class_name 的 tab_*.py；无 class_name 时取唯一 tab_*.py。"""
        if not folder or not os.path.isdir(folder):
            return None
        tab_files = [f for f in os.listdir(folder)
                     if f.startswith("tab_") and f.endswith(".py")]
        if class_name:
            for fn in tab_files:
                try:
                    if class_name in _top_level_classes(os.path.join(folder, fn)):
                        return fn
                except ValueError:
                    pass
            # 退一步：在任何 .py 中查找
            for fn in sorted(os.listdir(folder)):
                if not fn.endswith(".py"):
                    continue
                try:
                    if class_name in _top_level_classes(os.path.join(folder, fn)):
                        return fn
                except ValueError:
                    pass
            return None
        if len(tab_files) == 1:
            return tab_files[0]
        return None

    def _update_preview(self):
        """根据已选文件夹 + JSON 重绘导入清单预览（tab / set / 其他 / 校验）。"""
        while self._pv_lay.count():
            it = self._pv_lay.takeAt(0)
            w = it.widget()
            if w is not None:
                w.deleteLater()

        folder = self.folder_edit.text().strip()
        json_path = self.json_edit.text().strip()

        if not folder and not json_path:
            hint = QLabel("选择文件夹与 JSON 后，这里会列出 tab 主文件、set 文件与其他文件。")
            hint.setObjectName("hint")
            hint.setWordWrap(True)
            self._pv_lay.addWidget(hint)
            self._set_pv_status(False, "待选择")
            return

        # ── 读取 JSON ──
        jdata = None
        jerr = ""
        if json_path and os.path.isfile(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    jdata = json.load(f)
                if not isinstance(jdata, dict):
                    jerr = "JSON 顶层必须是对象 {}"
            except (OSError, ValueError) as e:
                jerr = f"JSON 解析失败：{e}"
        elif json_path:
            jerr = "清单文件不存在"

        class_name = (str(jdata.get("class_name", "")).strip()
                      if isinstance(jdata, dict) else "")

        # ── 扫描文件夹分类 ──
        tab_files, set_files, other_files = self._scan_plugin_folder(folder)

        main_file = self._resolve_main_tab_file(folder, class_name) if folder else None
        main_class = ""
        if main_file:
            try:
                classes = _top_level_classes(os.path.join(folder, main_file))
                main_class = class_name if class_name in classes else (
                    classes[0] if classes else "")
            except ValueError:
                main_class = ""

        name = ""
        if main_file:
            base = main_file[:-3]
            if base.startswith("tab_"):
                base = base[4:]
            name = re.sub(r"[^A-Za-z0-9_]", "_", base).strip("_")

        # ── 渲染清单行 ──
        self._info_row(self._pv_lay, "主类 (tab)",
                       f"{main_file or '（未找到）'}  →  class {main_class or '?'}")
        self._info_row(self._pv_lay, "set 设置",
                       ", ".join(set_files) if set_files else "（无）")
        self._info_row(self._pv_lay, "其他文件",
                       ", ".join(other_files) if other_files else "（无）")
        if isinstance(jdata, dict):
            self._info_row(self._pv_lay, "插件名",
                           str(jdata.get("name", "")) or name or "（自动推导）")
            settings = jdata.get("settings")
            scount = len(settings) if isinstance(settings, list) else 0
            self._info_row(self._pv_lay, "设置项",
                           f"{scount} 个（在设置页生成按钮）")

        # ── 校验状态 ──
        if jerr:
            self._set_pv_status(False, jerr)
        elif not folder:
            self._set_pv_status(False, "请选择插件文件夹")
        elif not main_file:
            if class_name:
                self._set_pv_status(False, "未找到含 class_name 的 tab_*.py")
            else:
                self._set_pv_status(False, "文件夹需有且仅有一个 tab_*.py")
        elif not name:
            self._set_pv_status(False, "无法从文件名推导插件名")
        else:
            self._set_pv_status(True, "✔ 可导入")

    def _set_pv_status(self, ok: bool, text: str):
        self._pv_status.setText(text)
        self._pv_status.setProperty("ok", "1" if ok else "0")
        self._pv_status.style().polish(self._pv_status)

    @staticmethod
    def _pv_toggle_text(expanded: bool) -> str:
        return f"导入清单预览 {'▾' if expanded else '▸'}"

    def _toggle_preview(self, expanded: bool):
        self._pv_host.setVisible(expanded)
        self._pv_status.setVisible(expanded)
        self._pv_toggle.setText(self._pv_toggle_text(expanded))

    def _render_plugins(self):
        """清空列表区并重绘已安装插件卡片。"""
        while self._list_lay.count():
            item = self._list_lay.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        installed = self._list_installed()
        if not installed:
            hint = QLabel("暂无已导入的插件。填写上方表单并点击「开始导入」后，"
                          "即可在左侧导航栏看到新 tab。")
            hint.setWordWrap(True)
            hint.setObjectName("hint")
            self._list_lay.addWidget(hint)
            return
        for mf in installed:
            self._list_lay.addWidget(self._plugin_card(mf))

    # ──────────────────────────────────────
    #  已安装插件渲染
    # ──────────────────────────────────────
    def _list_installed(self) -> list:
        """扫描 manifests/plugins/*.json，返回插件清单数据。"""
        out = []
        if not os.path.isdir(PLUGIN_MANIFESTS_DIR()):
            return out
        for fname in sorted(os.listdir(PLUGIN_MANIFESTS_DIR())):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(PLUGIN_MANIFESTS_DIR(), fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (OSError, ValueError):
                continue
            if not isinstance(data, dict) or not data.get("class_name"):
                continue
            data.setdefault("plugin_key", fname[:-5])
            out.append(data)
        return out

    def _plugin_card(self, mf: dict) -> QFrame:
        """单个插件的信息卡片（名称 + 状态徽章 + 操作按钮 + 展开/收起详情）。"""
        card = QFrame()
        card.setObjectName("SettingsSection")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(
            C.size("group_padding_h"), C.size("group_padding_v"),
            C.size("group_padding_h"), C.size("group_padding_v"),
        )
        lay.setSpacing(C.size("form_row_spacing"))

        # 先创建详情容器（因为按钮 lambda 需要引用它）
        details = QWidget()
        details.setObjectName("bareSurface")
        dlay = QVBoxLayout(details)
        dlay.setContentsMargins(0, 0, 0, 0)
        dlay.setSpacing(C.size("form_row_spacing"))

        self._info_row(dlay, "类名", mf.get("class_name", ""))
        self._info_row(dlay, "模块", mf.get("module_path", ""))
        ok, err = self._load_status(mf)
        if err:
            self._info_row(dlay, "原因", err)

        files = mf.get("files") or {}
        self._info_row(dlay, "主类 (tab)",
                    ", ".join(files.get("tab", [])) or "（无）")
        self._info_row(dlay, "set 设置",
                    ", ".join(files.get("set", [])) or "（无）")
        self._info_row(dlay, "其他文件",
                    ", ".join(files.get("other", [])) or "（无）")
        details.setVisible(False)

        # 标题行：插件名 + 状态徽章 + 三个操作按钮（靠右对齐）
        head = QHBoxLayout()
        head.setSpacing(C.size("form_row_spacing"))

        name_label = QLabel(mf.get("name", mf.get("plugin_key", "")))
        name_label.setObjectName("cardTitle")
        head.addWidget(name_label)

        head.addStretch(1)

        badge = QLabel("已加载" if ok else "加载失败")
        badge.setObjectName("badge")
        badge.setProperty("ok", "1" if ok else "0")
        badge.style().polish(badge)
        head.addWidget(badge)

        # 重新加载按钮
        reload_btn = QPushButton("重新加载")
        reload_btn.setObjectName("ghost")
        reload_btn.clicked.connect(
            lambda _=False, k=mf["plugin_key"]: self._on_reload(k))
        head.addWidget(reload_btn)

        # 卸载按钮
        uninstall_btn = QPushButton("卸载")
        uninstall_btn.setObjectName("ghost")
        uninstall_btn.clicked.connect(
            lambda _=False, k=mf["plugin_key"],
                n=mf.get("name", mf.get("plugin_key", "")):
                self._on_uninstall(k, n))
        head.addWidget(uninstall_btn)

        # 查看详情 / 收起详情按钮
        toggle_btn = QPushButton()
        toggle_btn.setObjectName("ghost")
        toggle_btn.setCheckable(True)
        toggle_btn.setChecked(False)
        toggle_btn.setCursor(Qt.PointingHandCursor)
        toggle_btn.clicked.connect(
            lambda checked, b=toggle_btn, d=details:
                self._toggle_card_details(b, d, checked))
        self._set_toggle_state(toggle_btn, False)
        head.addWidget(toggle_btn)

        lay.addLayout(head)
        lay.addWidget(details)

        return card

    # ── 展开 / 收起详情 ──
    def _set_toggle_state(self, btn: QPushButton, expanded: bool):
        """更新展开/收起按钮的文案与箭头图标。"""
        btn.setText("收起详情" if expanded else "查看详情")
        btn.setIcon(icon_res.colored_icon(
            "chevron-up" if expanded else "chevron-down",
            C.color("text_light"), C.size("icon_small")))
        btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))

    def _toggle_card_details(self, btn: QPushButton,
                             details: QWidget, expanded: bool):
        details.setVisible(expanded)
        self._set_toggle_state(btn, expanded)

    def _info_row(self, lay: QVBoxLayout, key: str, value: str):
        row = QHBoxLayout()
        row.setSpacing(C.size("form_row_spacing"))
        label = QLabel(key)
        label.setFixedWidth(C.size("form_width_90"))
        label.setObjectName("formLabel")
        row.addWidget(label)
        value_label = QLabel(value)
        value_label.setWordWrap(True)
        value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        row.addWidget(value_label, 1)
        lay.addLayout(row)

    @staticmethod
    def _load_status(mf: dict):
        """尝试导入并实例化插件类，返回 (ok, err)。"""
        try:
            module = importlib.import_module(mf.get("module_path", ""))
            cls = getattr(module, mf.get("class_name", ""))
            cls()
            return True, ""
        except Exception as e:  # noqa: BLE001 - 状态检查需捕获一切导入异常
            return False, f"{type(e).__name__}: {e}"

    # ──────────────────────────────────────
    #  导入插件
    # ──────────────────────────────────────
    def _start_import(self):
        """读取两输入（文件夹 + JSON），校验后执行安装。"""
        folder = self.folder_edit.text().strip()
        json_path = self.json_edit.text().strip()

        if not folder:
            QMessageBox.warning(self, "导入插件", "请先选择插件文件夹（必选）。")
            return
        if not json_path:
            QMessageBox.warning(self, "导入插件", "请先选择插件清单 JSON（必选）。")
            return
        if not os.path.isdir(folder):
            QMessageBox.warning(self, "导入插件", f"文件夹不存在：{folder}")
            return
        if not os.path.isfile(json_path):
            QMessageBox.warning(self, "导入插件", f"清单文件不存在：{json_path}")
            return

        if self._install_plugin(folder, json_path):
            self.folder_edit.clear()
            self.json_edit.clear()
            self._update_preview()

    def _install_plugin(self, folder: str, json_path: str) -> bool:
        """安装插件并写入清单；成功返回 True（失败已在内部提示）。"""
        # ── 校验清单 JSON ──
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError) as e:
            QMessageBox.warning(self, "导入插件", f"JSON 解析失败：{e}")
            return False
        if not isinstance(data, dict):
            QMessageBox.warning(self, "导入插件", "JSON 顶层必须是对象（{}）。")
            return False

        class_name = str(data.get("class_name", "")).strip()

        # ── 解析主 tab 文件 ──
        main_file = self._resolve_main_tab_file(folder, class_name)
        if not main_file:
            if class_name:
                QMessageBox.warning(
                    self, "导入插件",
                    f"清单声明的类名 {class_name} 在文件夹中未找到对应 tab_*.py。")
            else:
                QMessageBox.warning(
                    self, "导入插件",
                    "文件夹中需有且仅有一个 tab_*.py（或清单声明 class_name）。")
            return False

        base = main_file[:-3]
        name = re.sub(r"[^A-Za-z0-9_]", "_",
                      base[4:] if base.startswith("tab_") else base).strip("_")
        if not name:
            QMessageBox.warning(self, "导入插件", f"无法从文件名 {main_file} 推导插件名。")
            return False

        # ── 校验主文件含 class_name ──
        try:
            module_classes = _top_level_classes(os.path.join(folder, main_file))
        except ValueError as e:
            QMessageBox.warning(self, "导入插件", str(e))
            return False
        if class_name:
            if class_name not in module_classes:
                QMessageBox.warning(
                    self, "导入插件",
                    f"JSON 声明的类名 {class_name} 在 {main_file} 中不存在。\n"
                    f"当前文件中包含的类：{', '.join(module_classes)}")
                return False
        else:
            if len(module_classes) != 1:
                QMessageBox.warning(
                    self, "导入插件",
                    "JSON 未声明 class_name，且主文件中类不唯一，无法自动推断。\n"
                    f"当前文件中包含的类：{', '.join(module_classes)}")
                return False
            class_name = module_classes[0]

        display_name = str(data.get("name", "")).strip() or name

        # ── 覆盖确认 ──
        plugin_dir = os.path.join(PLUGINS_DIR(), name)
        dest_manifest = os.path.join(PLUGIN_MANIFESTS_DIR(), f"{name}.json")
        if os.path.isdir(plugin_dir) or os.path.exists(dest_manifest):
            ret = QMessageBox.question(
                self, "导入插件", f"插件「{name}」已存在，是否覆盖安装？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            if ret != QMessageBox.StandardButton.Yes:
                return False

        # ── 安装：复制整个文件夹内容 ──
        _purge_plugin_modules(name)
        _ensure_dirs()
        if os.path.isdir(plugin_dir):
            shutil.rmtree(plugin_dir, ignore_errors=True)
        os.makedirs(plugin_dir, exist_ok=True)
        shutil.copytree(
            folder, plugin_dir, dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        _strip_pycache(plugin_dir)
        init = os.path.join(plugin_dir, "__init__.py")
        if not os.path.exists(init):
            with open(init, "w", encoding="utf-8") as f:
                f.write(f'"""octool 插件包：{name}"""\n')

        # ── 写入清单（含文件清单，供已安装卡片展示）──
        settings = data.get("settings")
        settings = settings if isinstance(settings, list) else []
        order = data.get("order", 100)
        try:
            order = int(order)
        except (TypeError, ValueError):
            order = 100
        tab_files, set_files, other_files = self._scan_plugin_folder(plugin_dir)
        manifest = {
            "name": display_name,
            "class_name": class_name,
            "module_path": f"{_module_prefix(name)}.{main_file[:-3]}",
            "order": order,
            "settings_count": len(settings),
            "settings": settings,
            "files": {"tab": tab_files, "set": set_files, "other": other_files},
        }
        with open(dest_manifest, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=4)

        # ── 加载验证 ──
        try:
            module = importlib.import_module(manifest["module_path"])
            getattr(module, class_name)
        except Exception as e:  # noqa: BLE001 - 安装后提示真实加载错误
            QMessageBox.warning(
                self, "导入插件", f"插件「{display_name}」已安装，但暂时无法加载：{e}")
        else:
            QMessageBox.information(
                self, "导入插件", f"插件「{display_name}」导入成功，已加入左侧导航。")
        self._refresh()
        return True

    # ──────────────────────────────────────
    #  重载 / 卸载 / 刷新
    # ──────────────────────────────────────
    def _on_reload(self, plugin_key: str):
        _purge_plugin_modules(plugin_key)
        self._refresh()

    def _on_uninstall(self, plugin_key: str, display: str):
        ret = QMessageBox.question(
            self, "卸载插件", f"确定卸载插件「{display}」？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if ret != QMessageBox.StandardButton.Yes:
            return
        _purge_plugin_modules(plugin_key)
        shutil.rmtree(os.path.join(PLUGINS_DIR(), plugin_key), ignore_errors=True)
        manifest = os.path.join(PLUGIN_MANIFESTS_DIR(), f"{plugin_key}.json")
        if os.path.exists(manifest):
            try:
                os.remove(manifest)
            except OSError:
                pass
        self._refresh()

    def _refresh(self):
        """重绘列表，并广播主题事件触发左侧导航重建。"""
        self._render_plugins()
        THEME_BUS.changed.emit(C.theme())