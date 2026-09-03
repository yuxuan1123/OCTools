"""
tab_terminal.py — 嵌入式终端模拟器（支持 cmd / PowerShell）
"""
import sys
import os

from PySide6.QtCore import Qt, QTimer, QProcess, QTranslator, QLibraryInfo
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QComboBox, QPlainTextEdit, QGroupBox, QFrame,
    QCheckBox, QMessageBox,
)


class TabTerminal(QWidget):
    """可嵌入的终端模拟器，支持 cmd / PowerShell 交互。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = None                 # QProcess 实例
        self._tooltip_label = None          # 右下角提示标签
        self._install_translators()
        self._build_ui()

    def _install_translators(self):
        """加载 Qt 中文翻译（同原示例）"""
        app = QApplication.instance()
        if app is None:
            return
        official = QTranslator(self)
        official.load("qt_zh_CN", QLibraryInfo.path(QLibraryInfo.TranslationsPath))
        app.installTranslator(official)
        extra = QTranslator(self)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        qm_path = os.path.join(script_dir, "my_zh_CN.qm")
        if os.path.exists(qm_path):
            extra.load(qm_path)
            app.installTranslator(extra)
        self._translators = [official, extra]

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(12)

        # ── 标题 ──
        title = QLabel("终端模拟器")
        title.setObjectName("pageTitle")
        main_layout.addWidget(title)

        # ── Shell 选择与控制区 ──
        control_layout = QHBoxLayout()
        self.shell_combo = QComboBox()
        self.shell_combo.addItems(["cmd", "PowerShell"])
        self.shell_combo.setObjectName("shellCombo")
        self.shell_combo.setFixedWidth(140)

        self.start_btn = QPushButton("启动终端")
        self.start_btn.setObjectName("startBtn")
        self.start_btn.setFixedWidth(120)
        self.start_btn.clicked.connect(self._start_shell)

        self.stop_btn = QPushButton("停止终端")
        self.stop_btn.setObjectName("stopBtn")
        self.stop_btn.setFixedWidth(120)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_shell)

        self.clear_btn = QPushButton("清屏")
        self.clear_btn.setObjectName("clearBtn")
        self.clear_btn.setFixedWidth(80)
        self.clear_btn.clicked.connect(self._clear_output)

        control_layout.addWidget(self.shell_combo)
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(self.clear_btn)
        control_layout.addStretch()
        main_layout.addLayout(control_layout)

        # ── 输出区域 ──
        output_group = QGroupBox("命令输出")
        output_group.setObjectName("outputGroup")
        out_layout = QVBoxLayout(output_group)
        self.output_area = QPlainTextEdit()
        self.output_area.setObjectName("terminalOutput")
        self.output_area.setReadOnly(True)
        self.output_area.setFont(QFont("Consolas", 10))
        self.output_area.setLineWrapMode(QPlainTextEdit.NoWrap)
        out_layout.addWidget(self.output_area)
        main_layout.addWidget(output_group)

        # ── 输入区域 ──
        input_label = QLabel("输入命令（按 Enter 执行）：")
        input_label.setObjectName("formLabel")
        main_layout.addWidget(input_label)

        input_row = QHBoxLayout()
        self.input_line = QLineEdit()
        self.input_line.setObjectName("commandInput")
        self.input_line.setPlaceholderText("在此输入命令...")
        self.input_line.returnPressed.connect(self._execute_command)
        self.send_btn = QPushButton("发送")
        self.send_btn.setObjectName("sendBtn")
        self.send_btn.setFixedWidth(70)
        self.send_btn.clicked.connect(self._execute_command)
        input_row.addWidget(self.input_line, 1)
        input_row.addWidget(self.send_btn)
        main_layout.addLayout(input_row)

        # ── 状态指示 ──
        status_layout = QHBoxLayout()
        self.status_label = QLabel("终端状态：未启动")
        self.status_label.setObjectName("statusLabel")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        main_layout.addLayout(status_layout)

        # 初始禁用输入
        self._set_input_enabled(False)

    # ── 内部辅助 ──
    def _set_input_enabled(self, enabled: bool):
        self.input_line.setEnabled(enabled)
        self.send_btn.setEnabled(enabled)

    def _start_shell(self):
        """启动所选 shell 进程"""
        if self.process and self.process.state() == QProcess.Running:
            QMessageBox.information(self, "提示", "终端已在运行中。")
            return

        shell = self.shell_combo.currentText()
        if shell == "cmd":
            program = "cmd.exe"
            args = ["/Q"]                     # /Q 关闭回显，减少冗余输出
        else:
            program = "powershell.exe"
            args = ["-NoLogo", "-NoExit"]     # 不显示 logo，不退出

        self.process = QProcess(self)
        self.process.setProgram(program)
        self.process.setArguments(args)
        self.process.setProcessChannelMode(QProcess.MergedChannels)  # 合并 stdout/stderr

        # 连接信号
        self.process.readyReadStandardOutput.connect(self._read_output)
        self.process.started.connect(self._on_started)
        self.process.finished.connect(self._on_finished)
        self.process.errorOccurred.connect(self._on_error)

        # 设置工作目录为当前脚本所在目录（可选）
        self.process.setWorkingDirectory(os.getcwd())

        self.process.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("终端状态：正在启动...")
        self._append_output(f"[启动] 正在启动 {shell} ...\n")

    def _stop_shell(self):
        """终止当前 shell 进程"""
        if self.process and self.process.state() == QProcess.Running:
            self.process.kill()               # 强制结束
            self.process.waitForFinished(2000)
        self._reset_ui()

    def _reset_ui(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self._set_input_enabled(False)
        self.status_label.setText("终端状态：已停止")
        self._append_output("[终端] 进程已终止。\n")

    def _on_started(self):
        self._set_input_enabled(True)
        self.status_label.setText("终端状态：运行中")
        self._append_output("[终端] 就绪，请输入命令。\n")

    def _on_finished(self, exit_code, exit_status):
        self._reset_ui()
        self._append_output(f"[终端] 进程退出，代码 {exit_code}\n")

    def _on_error(self, error):
        err_msg = self.process.errorString()
        self._append_output(f"[错误] {err_msg}\n")
        self._reset_ui()

    def _read_output(self):
        data = self.process.readAllStandardOutput()
        text = bytes(data).decode("utf-8", errors="replace")
        self._append_output(text)

    def _execute_command(self):
        """将输入行中的命令写入进程标准输入"""
        if not self.process or self.process.state() != QProcess.Running:
            self._append_output("[警告] 终端未运行，请先启动。\n")
            return

        cmd = self.input_line.text().strip()
        if not cmd:
            return
        # 写入命令并追加换行符
        self.process.write((cmd + "\n").encode("utf-8"))
        self.input_line.clear()
        # 将命令本身回显到输出区域（因为 cmd /Q 模式下不会回显）
        self._append_output(f"> {cmd}\n")

    def _append_output(self, text: str):
        """向输出区域追加文本，并滚动到底部"""
        self.output_area.moveCursor(QTextCursor.End)
        self.output_area.insertPlainText(text)
        scrollbar = self.output_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _clear_output(self):
        self.output_area.clear()

    # ── 复制功能（右下角提示） ──
    def _copy_selected(self):
        """复制选中的文本（可由外部按钮或快捷键调用）"""
        cursor = self.output_area.textCursor()
        if cursor.hasSelection():
            selected = cursor.selectedText()
            QApplication.clipboard().setText(selected)
            self._show_tooltip("复制成功")
        else:
            self._show_tooltip("未选中任何文本")

    def _show_tooltip(self, message: str):
        """右下角浮动提示（同原示例）"""
        if self._tooltip_label is not None:
            self._tooltip_label.deleteLater()
            self._tooltip_label = None

        label = QLabel(message, self)
        label.setObjectName("copyTooltip")
        label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 180);
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 13px;
            }
        """)
        label.adjustSize()
        parent_rect = self.rect()
        x = parent_rect.width() - label.width() - 20
        y = parent_rect.height() - label.height() - 20
        label.move(x, y)
        label.show()
        label.raise_()
        self._tooltip_label = label

        QTimer.singleShot(1500, label.deleteLater)
        QTimer.singleShot(1500, lambda: setattr(self, '_tooltip_label', None))

    # ── 析构时清理进程 ──
    def closeEvent(self, event):
        if self.process and self.process.state() == QProcess.Running:
            self.process.kill()
            self.process.waitForFinished(1000)
        super().closeEvent(event)


# ── 独立测试 ──
if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        from ui.theme import APP_STYLESHEET
        if APP_STYLESHEET:
            app.setStyleSheet(APP_STYLESHEET)
    except ImportError:
        pass
    w = TabTerminal()
    w.setWindowTitle("终端模拟器")
    w.resize(700, 500)
    w.show()
    sys.exit(app.exec())