"""
tab_terminal.py — 嵌入式终端模拟器（命令行模式）

「终端的可视化参数」入口按钮 → 弹出独立窗口 VisualParamDialog
（见同目录 visual_dialog.py，模板数据见 commands.json）。
"""
from ui.ui_component.combo_component import Combo
import locale
import os
import sys

from PySide6.QtCore import Qt, QProcess
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QPlainTextEdit, QGroupBox, QFrame,
)

from plugins.terminal.visual_dialog import VisualParamDialog


class TabTerminal(QWidget):
    """嵌入式终端模拟器（命令行模式）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = None
        self._visual_dlg = None  # 持有可视化参数窗口引用，防止被 GC 回收而闪退
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(12)

        # ── 标题行：标题 + 可视化参数入口 ──
        title_row = QHBoxLayout()
        title = QLabel("终端")
        title.setObjectName("pageTitle")
        title_row.addWidget(title)
        title_row.addStretch(1)
        self.visual_btn = QPushButton("终端的可视化参数")
        self.visual_btn.setObjectName("ghost")
        self.visual_btn.clicked.connect(self._open_visual_dialog)
        title_row.addWidget(self.visual_btn)
        main_layout.addLayout(title_row)

        # ── 命令行模式控件 ──
        control_row = QHBoxLayout()
        shell_label = QLabel("Shell:")
        self.shell_combo = Combo()
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
        main_layout.addLayout(control_row)

        # 命令输入
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("输入命令，例如 dir 或 Get-ChildItem")
        self.cmd_input.returnPressed.connect(self._execute_command)
        main_layout.addWidget(self.cmd_input)

        # ── 输出显示区 ──
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

    # ── 可视化参数窗口 ──
    def _open_visual_dialog(self):
        """弹出「终端的可视化参数」独立窗口"""
        dlg = VisualParamDialog(terminal=self)
        dlg.setAttribute(Qt.WA_DeleteOnClose)
        self._visual_dlg = dlg  # 持有引用，避免局部变量被 GC 导致窗口闪退
        dlg.show()
        dlg.raise_()

    def execute_raw(self, cmd_str):
        """直接执行一条命令（用于可视化参数模式）"""
        self.cmd_input.setText(cmd_str)
        self._execute_command()

    # ── 命令执行 ──
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
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    app = QApplication(sys.argv)
    w = TabTerminal()
    w.setWindowTitle("终端模拟器")
    w.resize(850, 650)
    w.show()
    w.visual_btn.click()  # 直接演示可视化参数窗口
    sys.exit(app.exec())
