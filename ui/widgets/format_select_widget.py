"""
OCTools/ui/widgets/format_select_widget.py
───────────────────────────────────────────────
格式选择控件（可复用自定义控件）

内容：
  - 格式元数据（ICONS / FORMAT_DISPLAY / FILE_FILTERS / FORMAT_CATEGORIES …）
    全部派生自 core/formats.py（单一真相源）
  - FormatPicker：两级格式选择器（一级 = 分类按钮；二级 = 格式芯片按钮）

"""

import os

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget,
    QButtonGroup,
)

from core import formats as FMT
from config.ui_config import CONFIG as C
from ui import icon_res


# ── 格式元数据：全部派生自 core/formats.py（单一真相源）──
# 格式 id → SVG 图标名（assets/using，outline 线性风格）
FORMAT_ICON_NAMES = {
    # 文档类
    "md": "file-text", "docx": "file-text", "pdf": "file",
    "txt": "file-text", "txt-ocr": "scan",
    # 图像类
    "png": "photo", "jpg": "photo", "jpeg": "photo", "bmp": "photo",
    "gif": "photo", "webp": "photo", "tiff": "photo", "heic": "photo",
    "ppm": "photo", "pgm": "photo", "svg": "photo",
    # 表格类
    "xlsx": "table", "xls": "table", "csv": "table", "json": "braces",
    # 演示类
    "html": "world", "pptx": "presentation", "pptx-img": "presentation",
    # 视频类
    "mp4": "video", "avi": "video", "mkv": "video", "mov": "video",
    "webm": "video", "flv": "video", "wmv": "video", "3gp": "video",
    "ogv": "video",
    # 音频类
    "mp3": "music", "aac": "music", "wav": "music", "flac": "music",
    "ogg": "music", "opus": "music", "wma": "music", "m4a": "music",
    "amr": "music", "ac3": "music", "aiff": "music",
}
DEFAULT_FORMAT_ICON = "file"

# 分类（family）→ SVG 图标名
CATEGORY_ICON_NAMES = {
    "doc": "file-text", "table": "table", "presentation": "presentation",
    "video": "video", "audio": "music", "image": "photo",
}

# 选择器图标统一着色（灰，与 catBtn / chip 文字一致）
_ICON_COLOR = C.color("icon_default")

FORMAT_DISPLAY = {f.id: f.display for f in FMT.FORMATS}

# 「预设选择」下拉中的特殊选项：点击后打开原先的格式选项页面
PRESET_NEW_OPTION = "新增预设…"
# 「图片预设」下拉中的特殊选项：恢复默认图片排版
IMG_PRESET_DEFAULT_OPTION = "默认"

# 统一格式表（源格式驱动一切）
ALL_FORMATS = FMT.all_ids()
# 可作为源的格式（pptx-img 仅目标）
ALL_SOURCE_FORMATS = FMT.source_ids()

# ── 格式 → 文件过滤器 ──
FILE_FILTERS = {f.id: [f.filter()] for f in FMT.FORMATS}

# ── 格式分类（二级选择器一级选项；每个格式只归属一个分类）──
FORMAT_CATEGORIES = FMT.categories()


def get_icon(fmt):
    """格式 → SVG 图标名（用于 setIcon，缺省回退文件图标）"""
    return FORMAT_ICON_NAMES.get(str(fmt).lower().strip("."), DEFAULT_FORMAT_ICON)


def _cat_icon_name(fmts):
    """分类图标：由该分类首个格式的家族推断"""
    fam = FMT.family_of(fmts[0]) if fmts else ""
    return CATEGORY_ICON_NAMES.get(fam, DEFAULT_FORMAT_ICON)


def get_filter(fmt):
    return FILE_FILTERS.get(str(fmt).lower().strip("."), [("所有文件", "*.*")])


def _actual_ext(fmt):
    """伪目标格式 → 实际输出文件扩展名（txt-ocr 输出仍是 .txt，pptx-img 输出是 .pptx）"""
    fmt = str(fmt).lower()
    if fmt == "pptx-img":
        return "pptx"
    if fmt in ("txt-ocr", "txt_ocr"):
        return "txt"
    return fmt


def get_format_from_path(path):
    """从文件路径推断格式（别名归一化）"""
    ext = os.path.splitext(path)[1].lower().strip(".")
    return FMT.resolve(ext)


def _filters_str(formats):
    """格式列表 → QFileDialog 过滤器字符串"""
    parts = ["所有文件 (*.*)"]
    seen = set()
    for fmt in formats:
        for desc, pat in get_filter(fmt):
            key = (desc, pat)
            if key not in seen:
                seen.add(key)
                parts.append(f"{desc} ({pat})")
    return ";;".join(parts)


def _categories_for(allowed_formats):
    """按允许的格式集合裁剪分类（如源格式不含 pptx-img）"""
    cats = []
    for title, icon, fmts in FORMAT_CATEGORIES:
        kept = [f for f in fmts if f in allowed_formats]
        if kept:
            cats.append((title, icon, kept))
    return cats


# ════════════════════════════════════════════
#  格式二级选择器（分类按钮 + 格式芯片，点击选择）
# ════════════════════════════════════════════

class FormatPicker(QWidget):
    """两级格式选择：一级 = 分类按钮；二级 = 格式芯片按钮。

    - 芯片为可点选按钮，悬停 / 滚轮不会改变选择，避免误修改。
    - set_available() 控制哪些格式可选；select() 程序化选中。
    """

    format_selected = Signal(str)

    _CHIPS_PER_ROW = 6

    def __init__(self, categories, parent=None):
        super().__init__(parent)
        self._cat_buttons = []      # (btn, stack_index)
        self._cat_fmts = []         # index -> [fmt, ...]
        self._chips = {}            # fmt -> btn
        self._fmt_of_chip = {}      # btn -> fmt

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        # ── 一级：分类按钮行 ──
        cat_row = QWidget(self)
        cat_lay = QHBoxLayout(cat_row)
        cat_lay.setContentsMargins(0, 0, 0, 0)
        cat_lay.setSpacing(6)
        self._cat_group = QButtonGroup(self)
        self._cat_group.setExclusive(True)

        self._stack = QStackedWidget(self)
        for idx, (title, icon, fmts) in enumerate(categories):
            btn = QPushButton(title, cat_row)
            btn.setIcon(icon_res.colored_icon(
                _cat_icon_name(fmts), _ICON_COLOR, C.size("icon_medium")))
            btn.setIconSize(QSize(C.size("icon_medium"), C.size("icon_medium")))
            btn.setObjectName("catBtn")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            self._cat_group.addButton(btn, idx)
            cat_lay.addWidget(btn)
            self._cat_buttons.append(btn)
            self._cat_fmts.append(list(fmts))

            # ── 二级：该分类的格式芯片 ──
            page = QWidget(self._stack)
            page_lay = QVBoxLayout(page)
            page_lay.setContentsMargins(0, 0, 0, 0)
            page_lay.setSpacing(6)
            rows = []
            for i, fmt in enumerate(fmts):
                if i % self._CHIPS_PER_ROW == 0:
                    row = QWidget(page)
                    row_lay = QHBoxLayout(row)
                    row_lay.setContentsMargins(0, 0, 0, 0)
                    row_lay.setSpacing(6)
                    row_lay.addStretch(1)
                    page_lay.addWidget(row)
                    rows.append(row_lay)
                chip = QPushButton(
                    FORMAT_DISPLAY.get(fmt, fmt.upper()), page)
                chip.setIcon(icon_res.colored_icon(
                    get_icon(fmt), _ICON_COLOR, C.size("icon_medium")))
                chip.setIconSize(QSize(C.size("icon_medium"), C.size("icon_medium")))
                chip.setObjectName("chip")
                chip.setCheckable(True)
                chip.setCursor(Qt.PointingHandCursor)
                self._chips[fmt] = chip
                self._fmt_of_chip[chip] = fmt
                rows[-1].insertWidget(rows[-1].count() - 1, chip)
            self._stack.addWidget(page)
        cat_lay.addStretch(1)
        lay.addWidget(cat_row)
        lay.addWidget(self._stack, 1)

        # ── 空状态提示 ──
        self._empty_label = QLabel("当前源没有可选的目标格式", self)
        self._empty_label.setObjectName("pickerHint")
        self._empty_label.setVisible(False)
        lay.addWidget(self._empty_label)

        # 芯片互斥（手动管理：Qt 互斥组不允许程序化取消勾选）
        self._chip_group = None
        for chip in self._chips.values():
            chip.clicked.connect(self._on_chip_clicked)
        self._cat_group.idClicked.connect(self._on_cat_clicked)

        # 初始显示第一个分类
        if self._cat_buttons:
            self._cat_buttons[0].setChecked(True)
            self._stack.setCurrentIndex(0)

    # ── 信号处理 ──

    def _on_cat_clicked(self, idx):
        if 0 <= idx < self._stack.count():
            self._stack.setCurrentIndex(idx)

    def _on_chip_clicked(self):
        btn = self.sender()
        fmt = self._fmt_of_chip.get(btn)
        if not fmt:
            return
        # 手动互斥：只保留当前芯片选中
        for chip in self._chips.values():
            chip.setChecked(chip is btn)
        self.format_selected.emit(fmt)

    # ── 对外接口 ──

    def count(self):
        """芯片总数"""
        return len(self._chips)

    def current_format(self):
        """当前选中的格式；未选中返回 ''"""
        for fmt, chip in self._chips.items():
            if chip.isChecked():
                return fmt
        return ""

    def select(self, fmt, emit=False):
        """程序化选中格式（自动切到所在分类）；fmt 为空则取消选中"""
        if not fmt:
            self.clear()
            return
        chip = self._chips.get(fmt)
        if chip is None:
            return
        if not chip.isEnabled():
            return
        for c in self._chips.values():
            c.setChecked(c is chip)
        # 切到该格式所在分类
        for idx, fmts in enumerate(self._cat_fmts):
            if fmt in fmts:
                self._cat_buttons[idx].setChecked(True)
                self._stack.setCurrentIndex(idx)
                break
        if emit:
            self.format_selected.emit(fmt)

    def clear(self):
        for chip in self._chips.values():
            chip.setChecked(False)

    def set_available(self, formats):
        """更新可选格式；当前选中项不可用时自动清除并跳到首个可用分类"""
        avail = set(formats)
        for fmt, chip in self._chips.items():
            chip.setEnabled(fmt in avail)
        any_available = False
        for idx, btn in enumerate(self._cat_buttons):
            enabled = any(f in avail for f in self._cat_fmts[idx])
            btn.setEnabled(enabled)
            any_available = any_available or enabled

        self._empty_label.setVisible(not any_available)

        cur = self.current_format()
        if cur and cur not in avail:
            self.clear()

        # 当前分类不可用时，跳到第一个可用分类
        cur_idx = self._stack.currentIndex()
        if cur_idx < len(self._cat_buttons) and not self._cat_buttons[cur_idx].isEnabled():
            for idx, btn in enumerate(self._cat_buttons):
                if btn.isEnabled():
                    btn.setChecked(True)
                    self._stack.setCurrentIndex(idx)
                    break
