"""
color_pick.py — 颜色选择与多格式转换（带一键复制 + 右下角提示）
"""
import sys
import os
import re

from PySide6.QtCore import Qt, QTranslator, QLibraryInfo
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QColorDialog, QGridLayout, QGroupBox, QFrame,
)

# ── 引入统一 toast 组件 ──
from ui.toast import show_toast


# ── 颜色转换工具函数（保持不变） ──
def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    h = hex_str.lstrip("#")
    if len(h) != 6:
        raise ValueError
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hsl(r: int, g: int, b: int) -> tuple[float, float, float]:
    r_, g_, b_ = r / 255.0, g / 255.0, b / 255.0
    mx, mn = max(r_, g_, b_), min(r_, g_, b_)
    l = (mx + mn) / 2.0
    if mx == mn:
        h = s = 0.0
    else:
        d = mx - mn
        s = d / (1 - abs(2*l - 1))
        if mx == r_:
            h = ((g_ - b_) / d) % 6
        elif mx == g_:
            h = (b_ - r_) / d + 2
        else:
            h = (r_ - g_) / d + 4
        h *= 60
        if h < 0:
            h += 360
    return (round(h), round(s*100), round(l*100))

def rgb_to_hsv(r: int, g: int, b: int) -> tuple[float, float, float]:
    r_, g_, b_ = r / 255.0, g / 255.0, b / 255.0
    mx, mn = max(r_, g_, b_), min(r_, g_, b_)
    v = mx
    delta = mx - mn
    if mx == 0:
        s = 0.0
    else:
        s = delta / mx
    if delta == 0:
        h = 0.0
    elif mx == r_:
        h = ((g_ - b_) / delta) % 6
    elif mx == g_:
        h = (b_ - r_) / delta + 2
    else:
        h = (r_ - g_) / delta + 4
    h *= 60
    if h < 0:
        h += 360
    return (round(h), round(s*100), round(v*100))

def rgb_to_cmyk(r: int, g: int, b: int) -> tuple[float, float, float, float]:
    if r == 0 and g == 0 and b == 0:
        return (0, 0, 0, 100)
    c = 1 - r / 255.0
    m = 1 - g / 255.0
    y = 1 - b / 255.0
    k = min(c, m, y)
    if k == 1:
        return (0, 0, 0, 100)
    c = (c - k) / (1 - k) * 100
    m = (m - k) / (1 - k) * 100
    y = (y - k) / (1 - k) * 100
    k = k * 100
    return (round(c), round(m), round(y), round(k))


class TabColorPick(QWidget):
    """颜色选择与多格式转换页面（自包含翻译 + 右下角复制提示）。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_color = "#3498DB"
        self._install_translators()
        self._build_ui()

    def _install_translators(self):
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
        title = QLabel("选择颜色")
        title.setObjectName("pageTitle")
        main_layout.addWidget(title)

        # ── 颜色选择按钮 + 当前颜色预览 ──
        color_row = QHBoxLayout()
        self.color_btn = QPushButton("点击选择颜色")
        self.color_btn.setObjectName("colorPickBtn")
        self.color_btn.setFixedSize(160, 40)
        self.color_btn.setCursor(Qt.PointingHandCursor)
        self.color_btn.clicked.connect(self._pick_color)
        self._apply_button_color(self.selected_color)

        self.color_preview = QLabel()
        self.color_preview.setObjectName("colorPreview")
        self.color_preview.setFixedSize(60, 30)
        self.color_preview.setStyleSheet(f"background-color: {self.selected_color}; border: 1px solid #888; border-radius: 4px;")

        self.current_label = QLabel("当前颜色：")
        self.current_label.setObjectName("formLabel")

        color_row.addWidget(self.color_btn)
        color_row.addSpacing(10)
        color_row.addWidget(self.current_label)
        color_row.addWidget(self.color_preview)
        color_row.addStretch()
        main_layout.addLayout(color_row)

        # ── 颜色格式列表（带复制按钮） ──
        formats_group = QGroupBox("颜色格式（点击右侧按钮复制）")
        formats_group.setObjectName("formatsGroup")
        grid = QGridLayout(formats_group)
        grid.setSpacing(8)

        self.format_defs = [
            ("十六进制 (Hex)",  lambda qc: qc.name().upper()),
            ("RGB",             lambda qc: f"rgb({qc.red()}, {qc.green()}, {qc.blue()})"),
            ("HSL",             lambda qc: f"hsl({rgb_to_hsl(qc.red(), qc.green(), qc.blue())[0]}°, {rgb_to_hsl(qc.red(), qc.green(), qc.blue())[1]}%, {rgb_to_hsl(qc.red(), qc.green(), qc.blue())[2]}%)"),
            ("HSV",             lambda qc: f"hsv({rgb_to_hsv(qc.red(), qc.green(), qc.blue())[0]}°, {rgb_to_hsv(qc.red(), qc.green(), qc.blue())[1]}%, {rgb_to_hsv(qc.red(), qc.green(), qc.blue())[2]}%)"),
            ("CMYK",            lambda qc: f"cmyk({rgb_to_cmyk(qc.red(), qc.green(), qc.blue())[0]}%, {rgb_to_cmyk(qc.red(), qc.green(), qc.blue())[1]}%, {rgb_to_cmyk(qc.red(), qc.green(), qc.blue())[2]}%, {rgb_to_cmyk(qc.red(), qc.green(), qc.blue())[3]}%)"),
        ]

        self.format_lines = []
        for row_idx, (label_text, func) in enumerate(self.format_defs):
            lbl = QLabel(label_text)
            lbl.setObjectName("formatLabel")
            line = QLineEdit()
            line.setReadOnly(True)
            line.setObjectName("formatValue")
            line.setPlaceholderText(label_text.split("(")[0].strip())
            copy_btn = QPushButton("复制")
            copy_btn.setObjectName("copyBtn")
            copy_btn.setFixedWidth(60)
            # 注意：使用 lambda 捕获当前 line
            copy_btn.clicked.connect(lambda checked, le=line: self._copy_to_clipboard(le))
            grid.addWidget(lbl, row_idx, 0)
            grid.addWidget(line, row_idx, 1)
            grid.addWidget(copy_btn, row_idx, 2)
            self.format_lines.append((line, func))

        main_layout.addWidget(formats_group)

        # ── 手动输入转换（可选） ──
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setObjectName("separator")
        main_layout.addWidget(sep)

        input_label = QLabel("手动输入颜色值（Hex 或 rgb()）并转换：")
        input_label.setObjectName("formLabel")
        main_layout.addWidget(input_label)

        input_row = QHBoxLayout()
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("例如 #FF6600 或 rgb(255,102,0)")
        self.input_line.setObjectName("colorInput")
        convert_btn = QPushButton("转换并更新")
        convert_btn.setObjectName("convertBtnSmall")
        convert_btn.clicked.connect(self._convert_from_input)
        input_row.addWidget(self.input_line, 1)
        input_row.addWidget(convert_btn)
        main_layout.addLayout(input_row)

        main_layout.addStretch(1)

        # 初始化显示
        self._update_formats(QColor(self.selected_color))

    # ── 内部方法 ──
    def _apply_button_color(self, hex_color: str):
        text_color = "white" if self._is_dark(hex_color) else "black"
        self.color_btn.setStyleSheet(
            f"QPushButton#colorPickBtn {{ background-color: {hex_color}; color: {text_color}; }}"
        )

    @staticmethod
    def _is_dark(hex_color: str) -> bool:
        col = QColor(hex_color)
        luminance = 0.299 * col.red() + 0.587 * col.green() + 0.114 * col.blue()
        return luminance < 128

    def _pick_color(self):
        initial = QColor(self.selected_color)
        color = QColorDialog.getColor(initial, self, "选择颜色",
                                      options=QColorDialog.DontUseNativeDialog)
        if color.isValid():
            self.selected_color = color.name().upper()
            self._apply_button_color(self.selected_color)
            self.color_preview.setStyleSheet(
                f"background-color: {self.selected_color}; border: 1px solid #888; border-radius: 4px;"
            )
            self._update_formats(color)

    def _update_formats(self, qc: QColor):
        for line, func in self.format_lines:
            line.setText(func(qc))

    def _convert_from_input(self):
        text = self.input_line.text().strip()
        if not text:
            return
        qc = self._parse_color(text)
        if qc is None:
            show_toast(self, "无法识别，请使用 #RRGGBB 或 rgb(R,G,B)", kind="warn")
            return
        self.selected_color = qc.name().upper()
        self._apply_button_color(self.selected_color)
        self.color_preview.setStyleSheet(
            f"background-color: {self.selected_color}; border: 1px solid #888; border-radius: 4px;"
        )
        self._update_formats(qc)

    @staticmethod
    def _parse_color(text: str) -> QColor | None:
        text = text.strip()
        match = re.match(r'^#?([0-9a-fA-F]{6})$', text)
        if match:
            try:
                r, g, b = hex_to_rgb(match.group(1))
                return QColor(r, g, b)
            except ValueError:
                return None
        match = re.match(r'rgb\s*\(\s*(\d{1,3})\s*[, ]\s*(\d{1,3})\s*[, ]\s*(\d{1,3})\s*\)', text)
        if match:
            try:
                r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
                if all(0 <= x <= 255 for x in (r, g, b)):
                    return QColor(r, g, b)
            except ValueError:
                pass
        return None

    # ── 复制到剪贴板 + 右下角提示 ──
    def _copy_to_clipboard(self, line_edit: QLineEdit):
        clipboard = QApplication.clipboard()
        clipboard.setText(line_edit.text())
        show_toast(self, f"已复制 {line_edit.text()}", kind="success")


# ── 独立测试 ──
if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        from ui.theme import APP_STYLESHEET
        if APP_STYLESHEET:
            app.setStyleSheet(APP_STYLESHEET)
    except ImportError:
        pass
    w = TabColorPick()
    w.setWindowTitle("颜色选择")
    w.resize(580, 460)
    w.show()
    sys.exit(app.exec())