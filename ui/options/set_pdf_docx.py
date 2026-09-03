"""
OCTools/ui/options/set_pdf_docx.py
───────────────────────────────────────────────
PDF → DOCX 转换方式选项窗口

在两种方式中选择并持久化（PdfDocxConfig）：
  - libreoffice : LibreOffice 直转（推荐，失败自动回退文本提取）
  - text        : 文本提取 + python-docx 重建（仅文字，无需 LibreOffice）
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QComboBox,
    QPushButton, QWidget,
)

from config.pdf_docx_config import PdfDocxConfig, MODE_LABELS
from ui.theme import THEME as T
from config.ui_config import CONFIG as C


class SetPdfDocx(QDialog):
    """PDF → DOCX 转换方式选项窗口"""

    def __init__(self, config: PdfDocxConfig, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PDF → DOCX 转换方式")
        self.setMinimumWidth(520)
        self._config = config

        lay = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(C.size("form_row_spacing"))

        tip = QLabel(
            "选择 PDF 转 DOCX 的实现方式。\n"
            "· LibreOffice 直转：保留更多版式（字体/表格/段落结构），需要安装 LibreOffice；"
            "失败时自动回退到文本提取。\n"
            "· 文本提取重建：pdfplumber 提取文字 + python-docx 逐段重建，仅保留文字，不依赖外部程序。",
            self)
        tip.setObjectName("hint")
        tip.setWordWrap(True)
        form.addRow(tip)

        self._method_combo = QComboBox(self)
        for key, label in MODE_LABELS.items():
            self._method_combo.addItem(label, key)
        cur = config.method if config.method in MODE_LABELS else "libreoffice"
        self._method_combo.setCurrentIndex(
            list(MODE_LABELS.keys()).index(cur))
        form.addRow("转换方式:", self._method_combo)

        self._summary = QLabel("", self)
        self._summary.setObjectName("summary")
        form.addRow(self._summary)
        lay.addLayout(form)

        btns = QWidget(self)
        b_lay = QHBoxLayout(btns)
        b_lay.setContentsMargins(0, 8, 0, 0)
        b_lay.addStretch(1)
        cancel = QPushButton("取消", btns)
        cancel.clicked.connect(self.reject)
        ok = QPushButton("保存", btns)
        ok.setObjectName("primary")
        ok.clicked.connect(self._ok)
        b_lay.addWidget(cancel)
        b_lay.addWidget(ok)
        lay.addWidget(btns)

        self._method_combo.currentIndexChanged.connect(self._refresh_summary)
        self._refresh_summary()

    def _refresh_summary(self):
        key = self._method_combo.currentData()
        self._summary.setText(f"当前选择：{MODE_LABELS.get(key, key)}")

    def _ok(self):
        self._config.method = self._method_combo.currentData()
        self.accept()

    def get_config(self) -> PdfDocxConfig:
        return self._config


def show_pdf_docx_options(parent, config: PdfDocxConfig, on_close=None):
    """打开 PDF→DOCX 选项窗口（非模态，关闭时回调）"""
    from PySide6.QtCore import Qt
    dlg = SetPdfDocx(config, parent)
    dlg.setAttribute(Qt.WA_DeleteOnClose)
    if on_close is not None:
        dlg.finished.connect(lambda _r: on_close())
    dlg.show()
    dlg.raise_()
    dlg.activateWindow()
    return dlg
