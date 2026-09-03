"""
tab_terminal.py — 嵌入式终端模拟器 + 可视化命令构建器
"""
import json
import os
import sys
import locale

from PySide6.QtCore import Qt, QProcess
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QComboBox, QPlainTextEdit, QGroupBox, QFrame,
    QCheckBox, QFileDialog, QSpinBox, QScrollArea, QFormLayout,
)


class CommandBuilder(QWidget):
    """可视化命令构建器，根据 JSON 模板生成参数表单"""

    def __init__(self, terminal_widget, commands_file="commands.json"):
        super().__init__()
        self.terminal = terminal_widget
        self.commands_file = commands_file
        self.commands_data = {}
        self.param_widgets = {}  # 存储每个参数的控件
        self._load_commands()
        self._build_ui()

    def _load_commands(self):
        """加载命令模板 JSON"""
        if os.path.exists(self.commands_file):
            with open(self.commands_file, "r", encoding="utf-8") as f:
                self.commands_data = json.load(f)
        else:
            # 内置默认模板（至少包含 ffmpeg）
            self.commands_data = {
                "ffmpeg": {
                    "description": "FFmpeg 音视频转换",
                    "executable": "ffmpeg",
                    "parameters": [
                        {"flag": "-i", "label": "输入文件", "type": "file_open", "required": True, "placeholder": "选择输入文件"},
                        {"flag": "-ss", "label": "起始时间", "type": "string", "default": "", "placeholder": "HH:MM:SS"},
                        {"flag": "-t", "label": "持续时间", "type": "string", "default": "", "placeholder": "HH:MM:SS"},
                        {"flag": "-c:v", "label": "视频编码器", "type": "combo", "options": ["libx264","libx265","copy"], "default": "libx264"},
                        {"flag": "-c:a", "label": "音频编码器", "type": "combo", "options": ["aac","mp3","copy"], "default": "aac"},
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

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 命令选择行
        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("命令:"))
        self.cmd_combo = QComboBox()
        self.cmd_combo.addItems(self.commands_data.keys())
        self.cmd_combo.currentTextChanged.connect(self._on_command_changed)
        top_row.addWidget(self.cmd_combo)
        self.desc_label = QLabel("")
        top_row.addWidget(self.desc_label)
        top_row.addStretch()
        layout.addLayout(top_row)

        # 滚动区域放置参数表单
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.form_container = QWidget()
        self.form_layout = QFormLayout(self.form_container)
        self.form_layout.setVerticalSpacing(6)
        scroll.setWidget(self.form_container)
        layout.addWidget(scroll, 1)

        # 执行按钮
        btn_layout = QHBoxLayout()
        self.build_btn = QPushButton("生成并执行")
        self.build_btn.clicked.connect(self._build_and_execute)
        btn_layout.addStretch()
        btn_layout.addWidget(self.build_btn)
        layout.addLayout(btn_layout)

        # 初始化第一个命令的表单
        if self.cmd_combo.count() > 0:
            self._on_command_changed(self.cmd_combo.currentText())

    def _on_command_changed(self, cmd_name):
        """切换命令时重新生成参数表单"""
        # 清除旧控件
        for i in reversed(range(self.form_layout.count())):
            item = self.form_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # 清理布局中的控件
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
                self.form_layout.removeItem(item)
        self.param_widgets.clear()

        cmd_info = self.commands_data.get(cmd_name)
        if not cmd_info:
            return

        self.desc_label.setText(cmd_info.get("description", ""))
        executable = cmd_info.get("executable", cmd_name)

        for param in cmd_info["parameters"]:
            flag = param["flag"]
            label = param["label"]
            ptype = param["type"]
            required = param.get("required", False)
            default = param.get("default", "")
            placeholder = param.get("placeholder", "")
            options = param.get("options", [])

            # 创建控件
            widget = None
            if ptype == "string":
                le = QLineEdit()
                le.setPlaceholderText(placeholder)
                if default:
                    le.setText(str(default))
                widget = le
            elif ptype == "int":
                sp = QSpinBox()
                sp.setRange(0, 99999)
                if default:
                    sp.setValue(int(default))
                widget = sp
            elif ptype == "checkbox":
                cb = QCheckBox(label)
                if default:
                    cb.setChecked(bool(default))
                # checkbox 不需要额外的 label，直接添加
                row = QHBoxLayout()
                row.addWidget(cb)
                self.form_layout.addRow("", row)
                self.param_widgets[flag] = cb
                continue
            elif ptype == "combo":
                cmb = QComboBox()
                cmb.addItems(options)
                if default and default in options:
                    cmb.setCurrentText(default)
                widget = cmb
            elif ptype == "file_open":
                hl = QHBoxLayout()
                le = QLineEdit()
                le.setPlaceholderText(placeholder)
                btn = QPushButton("浏览...")
                btn.clicked.connect(lambda checked, e=le: e.setText(QFileDialog.getOpenFileName()[0]))
                hl.addWidget(le, 1)
                hl.addWidget(btn)
                self.form_layout.addRow(label + ":", hl)
                self.param_widgets[flag] = le
                continue
            elif ptype == "file_save":
                hl = QHBoxLayout()
                le = QLineEdit()
                le.setPlaceholderText(placeholder)
                btn = QPushButton("浏览...")
                btn.clicked.connect(lambda checked, e=le: e.setText(QFileDialog.getSaveFileName()[0]))
                hl.addWidget(le, 1)
                hl.addWidget(btn)
                self.form_layout.addRow(label + ":", hl)
                self.param_widgets[flag] = le
                continue
            else:
                # fallback
                le = QLineEdit()
                le.setPlaceholderText(placeholder)
                widget = le

            if widget:
                label_text = label + (" *" if required else "")
                self.form_layout.addRow(label_text + ":", widget)
                self.param_widgets[flag] = widget

    def _build_and_execute(self):
        """收集参数，生成命令字符串并执行"""
        cmd_name = self.cmd_combo.currentText()
        cmd_info = self.commands_data.get(cmd_name)
        if not cmd_info:
            return

        executable = cmd_info.get("executable", cmd_name)
        parts = [executable]

        for param in cmd_info["parameters"]:
            flag = param["flag"]
            widget = self.param_widgets.get(flag)
            if widget is None:
                continue

            # 获取值
            value = None
            ptype = param["type"]
            if ptype == "string":
                value = widget.text().strip()
            elif ptype == "int":
                value = str(widget.value()) if widget.value() != 0 else ""
            elif ptype == "checkbox":
                if widget.isChecked():
                    parts.append(flag)  # 对于 checkbox，只添加 flag（如 -y）
                continue
            elif ptype == "combo":
                value = widget.currentText()
            elif ptype in ("file_open", "file_save"):
                value = widget.text().strip()
            else:
                value = widget.text().strip()

            # 特殊标记 _output 和 _target 不作为 flag，直接追加
            if flag.startswith("_"):
                if value:
                    parts.append(value)
            else:
                if value:
                    parts.append(flag)
                    parts.append(value)

        # 生成完整命令字符串
        cmd_str = " ".join(parts)
        # 调用 Terminal 执行（假设 terminal 有 execute_raw 方法）
        self.terminal.execute_raw(cmd_str)


class TabTerminal(QWidget):
    """嵌入式终端模拟器（含可视化参数模式）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = None
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(12)

        # ── 标题 ──
        title = QLabel("终端")
        title.setObjectName("pageTitle")
        main_layout.addWidget(title)

        # ── 模式切换 ──
        mode_row = QHBoxLayout()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["命令行模式", "可视化参数模式"])
        self.mode_combo.currentTextChanged.connect(self._on_mode_changed)
        mode_row.addWidget(QLabel("模式:"))
        mode_row.addWidget(self.mode_combo)
        mode_row.addStretch()
        main_layout.addLayout(mode_row)

        # ── 命令行模式控件 ──
        self.cmd_widget = QWidget()
        cmd_layout = QVBoxLayout(self.cmd_widget)
        cmd_layout.setContentsMargins(0, 0, 0, 0)

        # Shell 选择 + 控制按钮
        control_row = QHBoxLayout()
        shell_label = QLabel("Shell:")
        self.shell_combo = QComboBox()
        self.shell_combo.addItems(["CMD", "PowerShell"])
        self.shell_combo.setCurrentIndex(0)
        self.run_btn = QPushButton("执行")
        self.run_btn.setObjectName("runBtn")
        self.run_btn.setFixedWidth(80)
        self.run_btn.setCursor(Qt.PointingHandCursor)
        self.run_btn.clicked.connect(self._execute_command)
        self.clear_btn = QPushButton("清屏")
        self.clear_btn.setFixedWidth(70)
        self.clear_btn.clicked.connect(self._clear_output)
        self.kill_btn = QPushButton("终止")
        self.kill_btn.setFixedWidth(70)
        self.kill_btn.clicked.connect(self._kill_process)
        self.kill_btn.setEnabled(False)
        control_row.addWidget(shell_label)
        control_row.addWidget(self.shell_combo)
        control_row.addSpacing(10)
        control_row.addWidget(self.run_btn)
        control_row.addWidget(self.clear_btn)
        control_row.addWidget(self.kill_btn)
        control_row.addStretch()
        cmd_layout.addLayout(control_row)

        # 命令输入
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("输入命令，例如 dir 或 Get-ChildItem")
        self.cmd_input.returnPressed.connect(self._execute_command)
        cmd_layout.addWidget(self.cmd_input)

        main_layout.addWidget(self.cmd_widget)

        # ── 可视化参数模式控件 ──
        self.builder_widget = CommandBuilder(self)
        self.builder_widget.hide()
        main_layout.addWidget(self.builder_widget)

        # ── 输出显示区（共用） ──
        output_group = QGroupBox("输出")
        output_group.setObjectName("outputGroup")
        group_layout = QVBoxLayout(output_group)
        self.output_area = QPlainTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setFont(QFont("Consolas", 10))
        self.output_area.setStyleSheet("background-color: #1e1e1e; color: #dcdcdc;")
        group_layout.addWidget(self.output_area)
        main_layout.addWidget(output_group)

        # ── 状态栏 ──
        status_frame = QFrame()
        status_frame.setObjectName("statusBar")
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(0, 0, 0, 0)
        self.status_label = QLabel("就绪")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        main_layout.addWidget(status_frame)

    def _on_mode_changed(self, mode):
        if mode == "命令行模式":
            self.cmd_widget.show()
            self.builder_widget.hide()
        else:
            self.cmd_widget.hide()
            self.builder_widget.show()

    def execute_raw(self, cmd_str):
        """直接执行一条命令（用于可视化参数模式）"""
        self.cmd_input.setText(cmd_str)
        self._execute_command()

    # ── 以下方法与之前相同（略作调整） ──

    def _execute_command(self):
        command = self.cmd_input.text().strip()
        if not command:
            return

        shell_type = self.shell_combo.currentText()
        if shell_type == "CMD":
            program = "cmd.exe"
            args = ["/c", command]
        else:
            program = "powershell.exe"
            args = ["-ExecutionPolicy", "Bypass", "-Command", command]

        self._kill_process()
        self.process = QProcess(self)
        self.process.setProgram(program)
        self.process.setArguments(args)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._on_stdout)
        self.process.finished.connect(self._on_finished)
        self.process.started.connect(self._on_started)

        self.cmd_input.returnPressed.disconnect()
        self.cmd_input.returnPressed.connect(self._send_input)

        self.output_area.appendPlainText(f"> {command}")
        self.process.start()

    def _send_input(self):
        if self.process and self.process.state() == QProcess.Running:
            text = self.cmd_input.text() + "\n"
            encoding = locale.getpreferredencoding() or 'utf-8'
            self.process.write(text.encode(encoding, errors='replace'))
            self.cmd_input.clear()

    def _on_stdout(self):
        raw = self.process.readAllStandardOutput().data()
        encoding = locale.getpreferredencoding() or 'utf-8'
        try:
            text = raw.decode(encoding, errors='replace')
        except LookupError:
            text = raw.decode('utf-8', errors='replace')
        self.output_area.appendPlainText(text.rstrip())

    def _on_started(self):
        self.status_label.setText("正在执行...")
        self.run_btn.setEnabled(False)
        self.kill_btn.setEnabled(True)

    def _on_finished(self, exit_code, exit_status):
        self.status_label.setText(f"完成 (退出码 {exit_code})")
        self.run_btn.setEnabled(True)
        self.kill_btn.setEnabled(False)
        self.process = None
        self.cmd_input.returnPressed.disconnect()
        self.cmd_input.returnPressed.connect(self._execute_command)

    def _kill_process(self):
        if self.process and self.process.state() == QProcess.Running:
            self.process.kill()
            self.process.waitForFinished(2000)
            self.output_area.appendPlainText("[INFO] 进程已终止")
        self.process = None
        self.run_btn.setEnabled(True)
        self.kill_btn.setEnabled(False)

    def _clear_output(self):
        self.output_area.clear()
        self.status_label.setText("已清屏")


# ── 独立测试 ──
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = TabTerminal()
    w.setWindowTitle("终端模拟器 + 命令构建器")
    w.resize(850, 650)
    w.show()
    sys.exit(app.exec())