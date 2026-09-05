"""
OCTools/ui/tabs/tab_plugin.py
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
  - 源码运行时插件根为项目根 plugins/（与外部插件系统共用同一目录），
    打包（PyInstaller）后为 exe 同目录 plugins/
    （路径 / 包前缀 / sys.path 挂载统一由 plugin_registry 提供，兼容打包环境）。

UI 加载模式自动判定（写入 manifest 的 ui_mode）：
  - direct：requirements 为空或仅 PySide6 → 主进程直接 import；
  - desc：PySide6 + 其他第三方库 → 子进程依赖隔离 + 控件树 JSON，主进程渲染；
  - window：非 PySide6 UI 库（tkinter/PyQt5 等）→ 子进程独立窗口。
  desc/window 导入时自动把依赖加入 PluginManager 安装队列（deps/<名>/）。

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
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QFileDialog, QScrollArea, QFrame, QMessageBox, QToolButton,
    QComboBox, QProgressBar, QPlainTextEdit,
)

from config.ui_config import CONFIG as C
from ui import icon_res
from ui.theme import THEME_BUS
from ui.tabs.tab_component.page_header import build_page_header
from services.ext_plugins import detection, paths
from services.ext_plugins.manager import (
    PluginManager,
    MISSING, NEEDS_INSTALL, INSTALLING, INSTALL_FAILED,
    READY, STARTING, RUNNING, STOPPING, CRASHED, DISABLED,
)

# 插件路径 / 包前缀 / sys.path 挂载 / 模块清理统一走注册表（兼容打包）。
from ui.tabs.plugin_registry import (
    plugins_dir as PLUGINS_DIR,
    plugin_manifests_dir as PLUGIN_MANIFESTS_DIR,
    module_prefix as _module_prefix,
    purge_plugin_modules as _purge_plugin_modules,
    ensure_plugin_dirs as _ensure_dirs,
)

# ─────────────────────────────────────────────
#  插件卡片共用元数据（与插件状态 / UI 模式徽章）
# ─────────────────────────────────────────────

# 子进程状态 → (文案, 徽章 ok 值: 1 成功绿 / 2 中性灰 / 0 失败红)
STATE_META = {
    MISSING:        ("无效", "0"),
    NEEDS_INSTALL:  ("待安装", "2"),
    INSTALLING:     ("安装中", "1"),
    INSTALL_FAILED: ("安装失败", "0"),
    READY:          ("就绪", "1"),
    STARTING:       ("启动中", "1"),
    RUNNING:        ("运行中", "1"),
    STOPPING:       ("停止中", "2"),
    CRASHED:        ("已崩溃", "0"),
    DISABLED:       ("已禁用", "2"),
}

# UI 加载模式 → (文案, 徽章 mode 值: 直载灰 / 隔离渲染蓝 / 独立窗口紫)
UI_MODE_META = {
    detection.UI_DIRECT: ("直载", "direct"),
    detection.UI_DESC:   ("隔离渲染", "desc"),
    detection.UI_WINDOW: ("独立窗口", "window"),
}

# 加载模式：界面展示顺序 → 配置取值
MODE_ITEMS = [("懒加载", "lazy"), ("常驻", "always"), ("闲置回收", "auto_recycle")]


def _tail(path: str, n: int = 80) -> str:
    """读取文件末尾 n 行；文件不存在返回空字符串。"""
    if not os.path.isfile(path):
        return ""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        return "".join(lines[-n:]).rstrip("\n")
    except OSError:
        return ""


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
        self._mgr = PluginManager.instance()
        self._cards: dict[str, QFrame] = {}
        self._build_ui()
        self._connect_manager()

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

        # ---- 已安装插件列表（含三种 UI 模式的管理控件）----
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
        self._cards.clear()
        installed = self._list_installed()
        if not installed:
            hint = QLabel("暂无已导入的插件。填写下方表单并点击「开始导入」后，"
                          "即可在左侧导航栏看到新 tab。")
            hint.setWordWrap(True)
            hint.setObjectName("hint")
            self._list_lay.addWidget(hint)
            return
        for mf in installed:
            card = self._plugin_card(mf)
            self._cards[mf["plugin_key"]] = card
            self._list_lay.addWidget(card)

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
        """单个插件的信息卡片（三种 UI 模式的管理控件合一）。

        - 标题行：名称 + UI 模式徽章 + 状态徽章 + 重新加载 / 卸载 / 查看详情；
        - direct：直载提示（无子进程生命周期控件）；
        - desc/window：启用 / 禁用、加载模式下拉、安装依赖、调用测试 / 打开窗口、
          崩溃测试，以及安装进度与日志详情。
        """
        key = mf["plugin_key"]
        ui_mode = mf.get("ui_mode", detection.UI_DIRECT)
        is_direct = ui_mode == detection.UI_DIRECT

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
        _, err = self._load_status(mf)
        if err:
            self._info_row(dlay, "原因", err)

        files = mf.get("files") or {}
        self._info_row(dlay, "主类 (tab)",
                       ", ".join(files.get("tab", [])) or "（无）")
        self._info_row(dlay, "set 设置",
                       ", ".join(files.get("set", [])) or "（无）")
        self._info_row(dlay, "其他文件",
                       ", ".join(files.get("other", [])) or "（无）")

        log_edit = None
        if not is_direct:
            log_edit = QPlainTextEdit()
            log_edit.setReadOnly(True)
            log_edit.setMinimumHeight(140)
            fam = C.raw("fonts", "family_log")
            if fam:
                log_edit.setFont(QFont(fam, C.font("log")))
            dlay.addWidget(log_edit)
        details.setVisible(False)

        # 标题行：插件名 + UI 模式徽章 + 状态徽章 + 操作按钮（靠右对齐）
        head = QHBoxLayout()
        head.setSpacing(C.size("form_row_spacing"))

        name_label = QLabel(mf.get("name", key))
        name_label.setObjectName("cardTitle")
        head.addWidget(name_label)

        mode_label, mode_key = UI_MODE_META.get(ui_mode, (ui_mode, "direct"))
        mode_badge = QLabel(mode_label)
        mode_badge.setObjectName("badge")
        mode_badge.setProperty("mode", mode_key)
        mode_badge.style().polish(mode_badge)
        head.addWidget(mode_badge)

        badge = QLabel("")
        badge.setObjectName("badge")
        head.addWidget(badge)

        head.addStretch(1)

        reload_btn = QPushButton("重新加载")
        reload_btn.setObjectName("ghost")
        reload_btn.clicked.connect(
            lambda _=False, k=key: self._on_reload(k))
        head.addWidget(reload_btn)

        uninstall_btn = QPushButton("卸载")
        uninstall_btn.setObjectName("ghost")
        uninstall_btn.clicked.connect(
            lambda _=False, k=key, n=mf.get("name", key):
                self._on_uninstall(k, n))
        head.addWidget(uninstall_btn)

        toggle_btn = QPushButton()
        toggle_btn.setObjectName("ghost")
        toggle_btn.setCheckable(True)
        toggle_btn.setChecked(False)
        toggle_btn.setCursor(Qt.PointingHandCursor)
        toggle_btn.clicked.connect(
            lambda checked, b=toggle_btn, d=details, k=key:
                self._toggle_card_details(b, d, checked, k))
        self._set_toggle_state(toggle_btn, False)
        head.addWidget(toggle_btn)

        lay.addLayout(head)

        # direct：直载提示（替代子进程管理控件）
        if is_direct:
            direct_hint = QLabel(
                "直载模式：由主进程直接加载，无子进程生命周期，可在左侧导航直接使用。")
            direct_hint.setObjectName("hint")
            direct_hint.setWordWrap(True)
            lay.addWidget(direct_hint)

        # desc/window：子进程管理控件
        mode_combo = toggle2 = install_btn = None
        progress = prog_status = call_btn = crash_btn = None
        if not is_direct:
            ctrl = QHBoxLayout()
            ctrl.setSpacing(C.size("form_row_spacing"))

            toggle2 = QPushButton("")
            toggle2.setObjectName("ghost")
            toggle2.clicked.connect(lambda _=False, k=key: self._on_toggle(k))
            ctrl.addWidget(toggle2)

            mode_combo = QComboBox()
            for label, _ in MODE_ITEMS:
                mode_combo.addItem(label)
            mode_combo.currentIndexChanged.connect(
                lambda idx, k=key: self._on_mode_changed(k, idx))
            ctrl.addWidget(mode_combo)

            install_btn = QPushButton("安装依赖")
            install_btn.setObjectName("ghost")
            install_btn.clicked.connect(
                lambda _=False, k=key: self._mgr.install(k))
            ctrl.addWidget(install_btn)

            if ui_mode == detection.UI_WINDOW:
                call_btn = QPushButton("打开窗口")
                call_btn.setObjectName("primary")
                call_btn.clicked.connect(
                    lambda _=False, k=key: self._mgr.activate(k))
            else:
                call_btn = QPushButton("调用测试")
                call_btn.setObjectName("ghost")
                call_btn.clicked.connect(
                    lambda _=False, k=key:
                        self._mgr.call(k, "echo", {"text": "hello"}))
            ctrl.addWidget(call_btn)

            crash_btn = QPushButton("崩溃测试")
            crash_btn.setObjectName("ghost")
            crash_btn.clicked.connect(
                lambda _=False, k=key: self._mgr.test_crash(k))
            ctrl.addWidget(crash_btn)

            ctrl.addStretch(1)
            lay.addLayout(ctrl)

            progress = QProgressBar()
            progress.setRange(0, 0)
            progress.setFixedHeight(C.size("input_min_h"))
            lay.addWidget(progress)
            prog_status = QLabel("")
            prog_status.setObjectName("hint")
            prog_status.setWordWrap(True)
            lay.addWidget(prog_status)

        lay.addWidget(details)

        # 挂引用，供 _refresh_card / 信号槽按需刷新
        card._key = key
        card._ui_mode = ui_mode
        card._badge = badge
        card._mode_combo = mode_combo
        card._toggle_btn = toggle2
        card._install_btn = install_btn
        card._progress = progress
        card._prog_status = prog_status
        card._call_btn = call_btn
        card._crash_btn = crash_btn
        card._log_edit = log_edit
        self._refresh_card(card, mf)
        return card

    def _refresh_card(self, card: QFrame, mf: dict):
        """按 manifest + 管理器快照刷新卡片状态徽章与控件。"""
        key = card._key
        if card._ui_mode == detection.UI_DIRECT:
            ok, _ = self._load_status(mf)
            card._badge.setText("已加载" if ok else "加载失败")
            card._badge.setProperty("ok", "1" if ok else "0")
            card._badge.style().polish(card._badge)
            return
        info = self._mgr.info(key)
        if info is None:
            card._badge.setText("未知")
            card._badge.setProperty("ok", "2")
            card._badge.style().polish(card._badge)
            return
        label, okv = STATE_META.get(info.state, (info.state, "2"))
        card._badge.setText(label)
        card._badge.setProperty("ok", okv)
        card._badge.style().polish(card._badge)
        self._apply_controls(card, info)

    @staticmethod
    def _apply_controls(card: QFrame, info):
        """按 PluginInfo 快照刷新 desc/window 卡片的子进程管理控件。"""
        card._toggle_btn.setText("禁用" if info.enabled else "启用")
        card._mode_combo.blockSignals(True)
        for i, (_, mode) in enumerate(MODE_ITEMS):
            if mode == info.load_mode:
                card._mode_combo.setCurrentIndex(i)
                break
        card._mode_combo.blockSignals(False)

        installing = info.state == INSTALLING
        need_install = info.state in (NEEDS_INSTALL, INSTALL_FAILED)
        card._install_btn.setVisible(need_install or installing)
        card._install_btn.setEnabled(info.enabled and not installing)
        card._progress.setVisible(installing)
        card._prog_status.setVisible(installing)

        callable_ = info.enabled and info.state not in (
            MISSING, NEEDS_INSTALL, INSTALL_FAILED, INSTALLING)
        card._call_btn.setEnabled(callable_)
        card._crash_btn.setEnabled(callable_)

    # ── 展开 / 收起详情 ──
    def _set_toggle_state(self, btn: QPushButton, expanded: bool):
        """更新展开/收起按钮的文案与箭头图标。"""
        btn.setText("收起详情" if expanded else "查看详情")
        btn.setIcon(icon_res.colored_icon(
            "chevron-up" if expanded else "chevron-down",
            C.color("text_light"), C.size("icon_small")))
        btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))

    def _toggle_card_details(self, btn: QPushButton,
                             details: QWidget, expanded: bool, key: str):
        details.setVisible(expanded)
        self._set_toggle_state(btn, expanded)
        if expanded:
            card = self._cards.get(key)
            if card is not None and card._log_edit is not None:
                card._log_edit.setPlainText(
                    _tail(paths.plugin_log(key)) or "（暂无日志）")

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
        """检查插件可加载状态，返回 (ok, err)。

        direct：主进程 import 并实例化类；
        desc/window：由子进程 host.py 加载（依赖隔离），此处仅校验 manifest 完整。
        """
        ui_mode = mf.get("ui_mode", "direct")
        if ui_mode != detection.UI_DIRECT:
            if not mf.get("module_path") or not mf.get("class_name"):
                return False, "manifest 缺少 module_path/class_name"
            return True, ""
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
                f.write(f'"""OCTools 插件包：{name}"""\n')

        # ── requirements → ui_mode 自动检测 ──
        req_path = os.path.join(plugin_dir, "requirements.txt")
        req_text = ""
        if os.path.isfile(req_path):
            try:
                with open(req_path, "r", encoding="utf-8") as f:
                    req_text = f.read()
            except OSError:
                req_text = ""
        ui_mode = detection.detect_ui_mode(req_text)

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
            "ui_mode": ui_mode,
            "order": order,
            "settings_count": len(settings),
            "settings": settings,
            "files": {"tab": tab_files, "set": set_files, "other": other_files},
        }
        with open(dest_manifest, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=4)

        # ── desc/window：依赖加入安装队列（串行安装到 deps/<name>/）──
        if ui_mode in (detection.UI_DESC, detection.UI_WINDOW) and req_text.strip():
            try:
                from services.ext_plugins.manager import PluginManager
                PluginManager.instance().install(name)
            except Exception:  # noqa: BLE001 - 管理器未就绪时静默降级
                pass

        # ── 加载验证（仅 direct：主进程可直接 import；desc/window 在子进程加载）──
        if ui_mode == detection.UI_DIRECT:
            try:
                module = importlib.import_module(manifest["module_path"])
                getattr(module, class_name)
            except Exception as e:  # noqa: BLE001 - 安装后提示真实加载错误
                QMessageBox.warning(
                    self, "导入插件", f"插件「{display_name}」已安装，但暂时无法加载：{e}")
            else:
                QMessageBox.information(
                    self, "导入插件", f"插件「{display_name}」导入成功，已加入左侧导航。")
        else:
            QMessageBox.information(
                self, "导入插件",
                f"插件「{display_name}」导入成功。\n"
                f"UI 模式：{'隔离渲染（desc）' if ui_mode == detection.UI_DESC else '独立窗口（window）'}。"
                f"依赖将安装到 deps/{name}/，完成后即可在左侧导航使用。")
        self._refresh()
        return True

    # ──────────────────────────────────────
    #  PluginManager 信号联动（按插件过滤刷新卡片）
    # ──────────────────────────────────────
    def _connect_manager(self):
        self._mgr.plugin_state_changed.connect(self._on_state)
        self._mgr.install_progress.connect(self._on_install_progress)
        self._mgr.install_finished.connect(self._on_install_finished)
        self._mgr.call_result.connect(self._on_call_result)
        self._mgr.log_updated.connect(self._on_log_updated)

    def _on_state(self, plugin_id: str, state: str):
        card = self._cards.get(plugin_id)
        if card is None:
            return
        info = self._mgr.info(plugin_id)
        if info is None:
            return
        label, okv = STATE_META.get(state, (state, "2"))
        card._badge.setText(label)
        card._badge.setProperty("ok", okv)
        card._badge.style().polish(card._badge)
        self._apply_controls(card, info)

    def _on_install_progress(self, plugin_id: str, percent: int, line: str):
        card = self._cards.get(plugin_id)
        if card is not None and card._prog_status.isVisible():
            card._prog_status.setText(line[-200:])

    def _on_install_finished(self, plugin_id: str, ok: bool, message: str):
        card = self._cards.get(plugin_id)
        if card is not None:
            card._prog_status.setText(message)

    def _on_call_result(self, plugin_id: str, ok: bool, message: str):
        card = self._cards.get(plugin_id)
        if card is not None and card._log_edit is not None:
            card._log_edit.appendPlainText(f"{'✓' if ok else '✗'} {message}")

    def _on_log_updated(self, plugin_id: str, kind: str):
        card = self._cards.get(plugin_id)
        if (card is not None and card._log_edit is not None
                and card._log_edit.isVisible()):
            card._log_edit.setPlainText(
                _tail(paths.plugin_log(plugin_id)) or "（暂无日志）")

    # ── 子进程控件交互 ──
    def _on_toggle(self, key: str):
        info = self._mgr.info(key)
        if info is None:
            return
        if info.enabled:
            self._mgr.disable(key)
        else:
            self._mgr.enable(key)

    def _on_mode_changed(self, key: str, index: int):
        if index < 0:
            return
        mode = MODE_ITEMS[index][1]
        info = self._mgr.info(key)
        if info is not None and info.load_mode != mode:
            self._mgr.set_load_mode(key, mode)

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