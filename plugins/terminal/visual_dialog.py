"""
visual_dialog.py — 「终端的可视化参数」独立窗口

按类型（ffmpeg / ping …）可视化配置参数，实时生成命令字符串；
支持「类型搜索」与「指令（参数）搜索」，一键复制 / 交由终端执行。

模板数据来自同目录 commands.json（缺失/损坏时回退内置默认模板）。
"""
import json
import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QDialog, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QPlainTextEdit, QCheckBox, QFileDialog,
    QSpinBox, QScrollArea, QFormLayout, QListWidget, QListWidgetItem,
    QSplitter, QFrame, QTabWidget, QTextBrowser,
)

from ui.ui_component.combo_component import Combo, DescComboBox

_COMMANDS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "commands.json")
_CHEATS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "resources", "CheatSheets",
)


def load_commands(commands_file=_COMMANDS_FILE) -> dict:
    """加载命令模板 JSON；缺失/损坏时回退内置默认模板。"""
    if os.path.exists(commands_file):
        try:
            with open(commands_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and data:
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return _default_templates()


def _default_templates() -> dict:
    """内置默认模板（commands.json 不存在时使用）"""
    return {
        "ffmpeg": {
            "description": "FFmpeg 音视频转换",
            "executable": "ffmpeg",
            "parameters": [
                {"flag": "-i", "label": "输入文件", "type": "file_open", "required": True, "placeholder": "选择输入文件"},
                {"flag": "-ss", "label": "起始时间", "type": "string", "default": "", "placeholder": "HH:MM:SS"},
                {"flag": "-t", "label": "持续时间", "type": "string", "default": "", "placeholder": "HH:MM:SS"},
                {"flag": "-c:v", "label": "视频编码器", "type": "combo", "editable": True, "options": ["libx264", "libx265", "copy"], "default": "libx264"},
                {"flag": "-c:a", "label": "音频编码器", "type": "combo", "editable": True, "options": ["aac", "mp3", "copy"], "default": "aac"},
                {"flag": "-b:v", "label": "视频比特率", "type": "string", "default": "2000k", "placeholder": "如 1000k"},
                {"flag": "-vf", "label": "视频滤镜", "type": "string", "default": "", "placeholder": "如 scale=1280:720"},
                {"flag": "-y", "label": "覆盖输出文件", "type": "checkbox", "default": True},
                {"flag": "_output", "label": "输出文件", "type": "file_save", "required": True, "placeholder": "选择输出路径"}
            ]
        },
        "ping": {
            "description": "Ping 测试",
            "executable": "ping",
            "parameters": [
                {"flag": "_target", "label": "目标地址", "type": "string", "required": True, "placeholder": "IP 或域名"},
                {"flag": "-n", "label": "发送次数", "type": "int", "default": "4", "placeholder": "1-100"},
                {"flag": "-l", "label": "数据包大小", "type": "int", "default": "32", "placeholder": "字节"},
                {"flag": "-t", "label": "持续 ping", "type": "checkbox", "default": False}
            ]
        }
    }


class VisualParamDialog(QDialog):
    """「终端的可视化参数」独立窗口。

    左侧按类型选择模板（顶部搜索框过滤类型），
    右侧按指令（参数）配置选项（顶部搜索框过滤参数），
    底部实时生成命令字符串，支持一键复制 / 交由终端执行。
    """

    def __init__(self, terminal=None, commands_file=_COMMANDS_FILE, parent=None):
        super().__init__(parent)
        self.terminal = terminal
        self.commands_data = load_commands(commands_file)
        self.param_widgets = {}   # flag -> 值控件
        self._row_meta = []       # (flag, row_index, match_text)
        self.form_container = None
        self.form_layout = None
        self.subcmd_row = None    # 子命令选择行（仅含 subcommands 的命令显示）
        self.subcmd_combo = None  # DescComboBox：名称 + 右侧淡色描述
        self._current_cmd = None  # 当前选中命令名
        self._current_sub = None  # 当前选中子命令名

        self.setWindowTitle("可视化参数")
        self.resize(880, 620)
        self._build_ui()

    # ── UI 构建 ───────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_params_tab(), "可视化参数")
        self.tabs.addTab(self._build_cheats_tab(), "速查表")
        root.addWidget(self.tabs, 1)

    def _build_params_tab(self) -> QWidget:
        """可视化参数：左类型列表 + 右参数表单 + 底部命令输出"""
        tab = QWidget()
        root = QVBoxLayout(tab)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(10)

        hint = QLabel("选择命令类型并配置参数，底部将实时生成命令")
        hint.setObjectName("hint")
        root.addWidget(hint)

        # ── 中间：左类型列表 + 右参数表单 ──
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)

        left = QWidget()
        lv = QVBoxLayout(left)
        lv.setContentsMargins(0, 0, 0, 0)
        lv.setSpacing(6)
        lv.addWidget(QLabel("命令类型"))
        self.type_search = QLineEdit()
        self.type_search.setPlaceholderText("搜索类型，如 ffmpeg、ping")
        self.type_search.textChanged.connect(self._filter_types)
        lv.addWidget(self.type_search)
        self.type_list = QListWidget()
        self.type_list.currentItemChanged.connect(self._on_type_changed)
        for name in self.commands_data:
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, name)
            self.type_list.addItem(item)
        lv.addWidget(self.type_list, 1)
        splitter.addWidget(left)

        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(0, 0, 0, 0)
        rv.setSpacing(6)
        rv.addWidget(QLabel("指令（参数）"))
        # 子命令选择行：仅含 subcommands 的命令显示（git/cmd/powershell/linux）
        self.subcmd_row = QWidget()
        sub_layout = QHBoxLayout(self.subcmd_row)
        sub_layout.setContentsMargins(0, 0, 0, 0)
        sub_layout.setSpacing(6)
        sub_label = QLabel("子命令:")
        self.subcmd_combo = DescComboBox()
        self.subcmd_combo.currentTextChanged.connect(self._on_subcommand_changed)
        sub_layout.addWidget(sub_label)
        sub_layout.addWidget(self.subcmd_combo, 1)
        self.subcmd_row.setVisible(False)
        rv.addWidget(self.subcmd_row)
        self.param_search = QLineEdit()
        self.param_search.setPlaceholderText("搜索指令，如 -c:v、输入文件")
        self.param_search.textChanged.connect(self._filter_params)
        rv.addWidget(self.param_search)
        self.param_scroll = QScrollArea()
        self.param_scroll.setWidgetResizable(True)
        self.param_scroll.setFrameShape(QFrame.NoFrame)
        rv.addWidget(self.param_scroll, 1)
        splitter.addWidget(right)

        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 5)
        splitter.setSizes([240, 560])
        root.addWidget(splitter, 1)

        # ── 底部：命令输出 + 按钮 ──
        out_label = QLabel("命令")
        out_label.setObjectName("fieldLabel")
        root.addWidget(out_label)
        self.output_area = QPlainTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setFont(QFont("Consolas", 10))
        self.output_area.setFixedHeight(72)
        self.output_area.setStyleSheet(
            "background-color: #1e1e1e; color: #dcdcdc; border-radius: 6px; padding: 6px;"
        )
        root.addWidget(self.output_area)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        self.copy_btn = QPushButton("复制")
        self.copy_btn.setObjectName("primary")
        self.copy_btn.setFixedWidth(96)
        self.copy_btn.clicked.connect(self._copy_command)
        btn_row.addWidget(self.copy_btn)
        self.exec_btn = QPushButton("生成并执行")
        self.exec_btn.setObjectName("ghost")
        self.exec_btn.setFixedWidth(112)
        self.exec_btn.clicked.connect(self._execute)
        btn_row.addWidget(self.exec_btn)
        root.addLayout(btn_row)

        # 默认选中第一个类型
        if self.type_list.count():
            self.type_list.setCurrentRow(0)
        return tab

    # ── 速查表页 ─────────────────────────────────────────
    def _build_cheats_tab(self) -> QWidget:
        """速查表：CheatSheets 目录下全部 .md，左列表 + 右侧 Markdown 渲染"""
        tab = QWidget()
        root = QVBoxLayout(tab)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        self.cheat_search = QLineEdit()
        self.cheat_search.setPlaceholderText("搜索速查表，如 git、python、docker")
        self.cheat_search.textChanged.connect(self._filter_cheats)
        root.addWidget(self.cheat_search)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        self.cheat_list = QListWidget()
        self.cheat_list.currentItemChanged.connect(self._show_cheat)
        for path in self._cheat_files():
            name = os.path.splitext(os.path.basename(path))[0]
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, path)
            self.cheat_list.addItem(item)
        splitter.addWidget(self.cheat_list)
        self.cheat_view = QTextBrowser()
        self.cheat_view.setOpenExternalLinks(True)
        splitter.addWidget(self.cheat_view)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 5)
        splitter.setSizes([200, 620])
        root.addWidget(splitter, 1)

        if self.cheat_list.count():
            self.cheat_list.setCurrentRow(0)
        return tab

    def _cheat_files(self) -> list:
        """CheatSheets 目录下的全部 .md 文件路径"""
        try:
            names = sorted(f for f in os.listdir(_CHEATS_DIR) if f.lower().endswith(".md"))
        except OSError:
            return []
        return [os.path.join(_CHEATS_DIR, n) for n in names]

    def _filter_cheats(self, text):
        text = text.strip().lower()
        for i in range(self.cheat_list.count()):
            item = self.cheat_list.item(i)
            item.setHidden(bool(text) and text not in item.text().lower())

    def _show_cheat(self, current, _prev=None):
        if current is None:
            return
        path = current.data(Qt.UserRole)
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                md = f.read()
        except OSError:
            md = "（无法读取文件）"
        self.cheat_view.setMarkdown(md)

    # ── 事件：类型 / 子命令 / 参数 ─────────────────────────
    def _on_type_changed(self, current, _prev=None):
        if current is None:
            return
        self._current_cmd = current.data(Qt.UserRole)
        cmd_info = self.commands_data.get(self._current_cmd, {})
        subs = cmd_info.get("subcommands", {})
        if subs:
            # 填充子命令下拉（含描述），并默认选中第一个子命令
            self.subcmd_combo.blockSignals(True)
            self.subcmd_combo.set_desc_items(
                {name: info.get("description", "") for name, info in subs.items()})
            self.subcmd_combo.blockSignals(False)
            self.subcmd_row.setVisible(True)
            self._current_sub = self.subcmd_combo.currentText()
            self._rebuild_form(self._current_cmd, self._current_sub)
        else:
            self.subcmd_row.setVisible(False)
            self._current_sub = None
            self._rebuild_form(self._current_cmd, None)
        self._refresh_command()

    def _on_subcommand_changed(self, text):
        if self._current_cmd is None:
            return
        self._current_sub = text
        self._rebuild_form(self._current_cmd, text)
        self._refresh_command()

    def _filter_types(self, text):
        text = text.strip().lower()
        first_visible = None
        for i in range(self.type_list.count()):
            item = self.type_list.item(i)
            name = item.data(Qt.UserRole) or ""
            info = self.commands_data.get(name, {})
            hay = f"{name} {info.get('description', '')}".lower()
            # 子命令名也可命中搜索
            for sub in (info.get("subcommands") or {}):
                hay += f" {sub}"
            visible = (not text) or text in hay
            item.setHidden(not visible)
            if visible and first_visible is None:
                first_visible = item
        cur = self.type_list.currentItem()
        if cur is None or cur.isHidden():
            if first_visible is not None:
                self.type_list.setCurrentItem(first_visible)

    def _filter_params(self, text):
        text = text.strip().lower()
        for _flag, row, match in self._row_meta:
            self.form_layout.setRowVisible(row, (not text) or text in match)

    # ── 参数表单 ──────────────────────────────────────────
    def _rebuild_form(self, cmd_name, subcmd_name=None):
        self.param_widgets.clear()
        self._row_meta = []
        self.form_container = QWidget()
        self.form_layout = QFormLayout(self.form_container)
        self.form_layout.setContentsMargins(8, 8, 8, 8)
        self.form_layout.setVerticalSpacing(8)
        self.form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.param_scroll.setWidget(self.form_container)  # setWidget 会自动删除旧容器

        cmd_info = self.commands_data.get(cmd_name)
        if not cmd_info:
            return

        # 命中子命令时使用其参数，否则使用命令级参数
        params = cmd_info.get("parameters", [])
        if subcmd_name:
            sub = cmd_info.get("subcommands", {}).get(subcmd_name)
            if sub:
                params = sub.get("parameters", [])

        idx = 0
        for param in params:
            flag = param["flag"]
            label = param["label"]
            ptype = param["type"]
            required = param.get("required", False)
            default = param.get("default", "")
            placeholder = param.get("placeholder", "")
            options = param.get("options", [])
            label_text = label + (" *" if required else "")
            match_text = f"{label} {flag}".lower()

            if ptype == "checkbox":
                cb = QCheckBox(label)
                if default:
                    cb.setChecked(bool(default))
                cb.toggled.connect(self._refresh_command)
                self.form_layout.addRow("", cb)
                self.param_widgets[flag] = cb
            elif ptype in ("file_open", "file_save"):
                hl = QHBoxLayout()
                le = QLineEdit()
                le.setPlaceholderText(placeholder)
                if default:
                    le.setText(str(default))
                le.textChanged.connect(self._refresh_command)
                pick = QPushButton("浏览…")
                pick.setObjectName("ghost")
                if ptype == "file_open":
                    pick.clicked.connect(lambda _=False, e=le: e.setText(QFileDialog.getOpenFileName()[0]))
                else:
                    pick.clicked.connect(lambda _=False, e=le: e.setText(QFileDialog.getSaveFileName()[0]))
                hl.addWidget(le, 1)
                hl.addWidget(pick)
                self.form_layout.addRow(label_text + ":", hl)
                self.param_widgets[flag] = le
            else:
                widget = None
                if ptype == "string":
                    le = QLineEdit()
                    le.setPlaceholderText(placeholder)
                    if default:
                        le.setText(str(default))
                    le.textChanged.connect(self._refresh_command)
                    widget = le
                elif ptype == "int":
                    sp = QSpinBox()
                    sp.setRange(0, 99999)
                    if default:
                        sp.setValue(int(default))
                    sp.valueChanged.connect(self._refresh_command)
                    widget = sp
                elif ptype == "combo":
                    cmb = Combo()
                    cmb.addItems(options)
                    if default and default in options:
                        cmb.setCurrentText(default)
                    if param.get("editable"):
                        # 可手输：选项之外的值也能直接输入，且不自动插入下拉
                        cmb.setEditable(True)
                        cmb.setInsertPolicy(Combo.NoInsert)
                    cmb.currentTextChanged.connect(self._refresh_command)
                    widget = cmb
                else:
                    le = QLineEdit()
                    le.setPlaceholderText(placeholder)
                    if default:
                        le.setText(str(default))
                    le.textChanged.connect(self._refresh_command)
                    widget = le
                self.form_layout.addRow(label_text + ":", widget)
                self.param_widgets[flag] = widget

            self._row_meta.append((flag, idx, match_text))
            idx += 1

    # ── 命令生成 / 复制 / 执行 ────────────────────────────
    def _build_command(self) -> str:
        cur = self.type_list.currentItem()
        if cur is None:
            return ""
        name = cur.data(Qt.UserRole)
        cmd_info = self.commands_data.get(name)
        if not cmd_info:
            return ""
        parts = []
        exe = cmd_info.get("executable", name)
        params = cmd_info.get("parameters", [])
        subcmd = self._current_sub
        if subcmd and subcmd in cmd_info.get("subcommands", {}):
            params = cmd_info["subcommands"][subcmd].get("parameters", [])
        if exe:
            parts.append(exe)
        if subcmd:
            parts.append(subcmd)
        for param in params:
            flag = param["flag"]
            widget = self.param_widgets.get(flag)
            if widget is None:
                continue
            ptype = param["type"]
            if ptype == "checkbox":
                if widget.isChecked():
                    parts.append(flag)
                continue
            if ptype == "int":
                value = str(widget.value()) if widget.value() != 0 else ""
            elif ptype == "combo":
                value = widget.currentText()
            else:
                value = widget.text().strip()
            if flag.startswith("_"):
                if value:
                    parts.append(value)
            else:
                if value:
                    parts.append(flag)
                    parts.append(value)
        return " ".join(parts)

    def _refresh_command(self):
        self.output_area.setPlainText(self._build_command())

    def _copy_command(self):
        cmd = self.output_area.toPlainText()
        if not cmd:
            return
        QApplication.clipboard().setText(cmd)
        try:
            from ui.toast import show_toast
            show_toast(self, "命令已复制到剪贴板", kind="success")
        except Exception:
            pass

    def _execute(self):
        if self.terminal is None:
            return
        cmd = self._build_command()
        if cmd:
            self.terminal.execute_raw(cmd)
