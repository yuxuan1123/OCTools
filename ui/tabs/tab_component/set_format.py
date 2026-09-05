"""
OCTools/ui/tabs/tab_component/set_format.py
───────────────────────────────────────────────
MD → DOCX 格式控制面板（PySide6 版）

折叠式面板设计，包含 5 个分组：
  1. 预设管理 (Presets)
  2. 页面设置 (Page Setup)
  3. 字体排版 (Typography)
  4. 内容样式 (Content Styles)
  5. 高级特性 (Advanced)

用法:
  panel = FormatPanel(parent, config=FormatConfig.default_chinese())
  # 读取用户修改后的配置:
  updated_config = panel.get_config()
  # 弹窗用法:
  dlg = SetFormat(config, parent)
  dlg.exec()
  config = dlg.get_config()
"""

import sys

from PySide6.QtCore import Qt, QSize
from ui import icon_res
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QComboBox, QLineEdit, QDoubleSpinBox, QCheckBox, QRadioButton,
    QButtonGroup, QToolButton, QScrollArea, QFrame, QPushButton,
    QFileDialog, QMessageBox, QInputDialog, QColorDialog, QSizePolicy,
)

from ui.options._base import OptionsDialogBase
from config.format_config import FormatConfig
from config.enums import PaperSize, Orientation, LineSpacingMode, Alignment
from config import presets

from ui.theme import THEME as T
from config.ui_config import CONFIG as C


# 可用中文字体列表
CN_FONTS = [
    "宋体", "黑体", "微软雅黑", "楷体", "仿宋",
    "华文宋体", "华文黑体", "华文楷体", "华文仿宋",
    "思源宋体", "思源黑体", "方正书宋", "方正黑体",
]

EN_FONTS = [
    "Times New Roman", "Arial", "Calibri", "Cambria",
    "Georgia", "Consolas", "Courier New", "Helvetica",
    "Segoe UI", "Verdana", "Tahoma", "Trebuchet MS",
]

CODE_FONTS = [
    "Consolas", "Courier New", "Fira Code", "JetBrains Mono",
    "Source Code Pro", "Monaco", "Menlo", "DejaVu Sans Mono",
]

ALIGNMENTS = {
    "两端对齐": Alignment.JUSTIFY,
    "左对齐": Alignment.LEFT,
    "居中": Alignment.CENTER,
    "右对齐": Alignment.RIGHT,
}
ALIGN_REVERSE = {v: k for k, v in ALIGNMENTS.items()}


# ════════════════════════════════════════════
#  辅助控件
# ════════════════════════════════════════════

def _spin(parent, lo, hi, step=1.0, value=None, suffix="", decimals=None):
    """标准 QDoubleSpinBox"""
    sb = QDoubleSpinBox(parent)
    sb.setRange(lo, hi)
    sb.setSingleStep(step)
    if decimals is None:
        decimals = max(0, len(str(step).split(".")[1]) if "." in str(step) else 0)
    sb.setDecimals(decimals)
    if suffix:
        sb.setSuffix(suffix)
    if value is not None:
        sb.setValue(float(value))
    return sb


def _combo(parent, values, current=None, editable=False):
    """标准 QComboBox；current 不在列表中时自动补入以保证显示"""
    cb = QComboBox(parent)
    cb.setEditable(editable)
    vals = list(values)
    if current and current not in vals:
        vals.append(current)
    cb.addItems(vals)
    if current:
        cb.setCurrentText(current)
    elif vals:
        cb.setCurrentIndex(0)
    return cb


class ColorField(QWidget):
    """颜色输入框 + 选色按钮"""

    def __init__(self, color=None, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(C.size("widget_row_spacing"))
        self._edit = QLineEdit(self)
        self._edit.setFixedWidth(C.size("input_min_w"))
        self._edit.setText(color or C.color("colorpicker_default"))
        btn = QPushButton("选色", self)
        btn.setObjectName("ghost")
        btn.setFixedWidth(C.size("color_btn_w"))
        btn.clicked.connect(self._pick)
        lay.addWidget(self._edit)
        lay.addWidget(btn)

    def _pick(self):
        cur = self._edit.text().strip()
        initial = (QColor(cur) if QColor(cur).isValid()
                   else QColor(C.color("colorpicker_default")))
        color = QColorDialog.getColor(initial, self, "选择颜色")
        if color.isValid():
            self._edit.setText(color.name().upper())

    def text(self):
        return self._edit.text().strip()

    def setText(self, s):
        self._edit.setText(s or C.color("colorpicker_default"))


def _form(parent):
    """标准表单布局（label 列固定宽度）"""
    form = QFormLayout()
    form.setContentsMargins(12, 8, 12, 10)
    form.setHorizontalSpacing(12)
    form.setVerticalSpacing(8)
    form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
    return form


def _hbox(*widgets, spacing=None):
    """横向容器"""
    if spacing is None:
        spacing = C.size("header_row_spacing")
    w = QWidget()
    lay = QHBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(spacing)
    for x in widgets:
        lay.addWidget(x)
    return w


# ════════════════════════════════════════════
#  折叠面板组件
# ════════════════════════════════════════════

class CollapsibleSection(QWidget):
    """可折叠的分组面板"""

    def __init__(self, parent, title: str, icon: str = "", expanded: bool = True):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 6)
        lay.setSpacing(4)

        self.toggle_btn = QToolButton(self)
        self.toggle_btn.setText(title)
        if icon:
            self.toggle_btn.setIcon(icon_res.colored_icon(
                icon, C.color("icon_default"), C.size("icon_medium")))
            self.toggle_btn.setIconSize(
                QSize(C.size("icon_medium"), C.size("icon_medium")))
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(expanded)
        self.toggle_btn.setToolButtonStyle(
            Qt.ToolButtonTextBesideIcon if icon else Qt.ToolButtonTextOnly)
        self.toggle_btn.setArrowType(Qt.DownArrow if expanded else Qt.RightArrow)
        self.toggle_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.toggle_btn.setObjectName("sectionHeader")
        self.toggle_btn.toggled.connect(self._on_toggled)
        lay.addWidget(self.toggle_btn)

        self.content = QWidget(self)
        self.content.setVisible(expanded)
        lay.addWidget(self.content)

    def _on_toggled(self, checked: bool):
        self.toggle_btn.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)
        self.content.setVisible(checked)


# ════════════════════════════════════════════
#  各分组面板
# ════════════════════════════════════════════

class PageSetupSection(CollapsibleSection):
    """页面设置分组"""

    def __init__(self, parent, config: FormatConfig, **kwargs):
        super().__init__(parent, "页面设置", "layout", **kwargs)
        self._config = config
        self._build()

    def _build(self):
        c = self.content
        form = _form(c)
        c.setLayout(form)

        # 纸张大小
        paper_items = [(f"{p.value} - {PaperSize.labels().get(p, p.value)}", p)
                       for p in PaperSize]
        self._paper_combo = QComboBox(c)
        for text, p in paper_items:
            self._paper_combo.addItem(text, p)
        cur_paper = self._config.page.paper_size
        idx = next((i for i, (_, p) in enumerate(paper_items) if p == cur_paper), 0)
        self._paper_combo.setCurrentIndex(idx)
        form.addRow("纸张大小:", self._paper_combo)

        # 页面方向
        self._orientation_group = QButtonGroup(c)
        orient_row = QWidget(c)
        o_lay = QHBoxLayout(orient_row)
        o_lay.setContentsMargins(0, 0, 0, 0)
        o_lay.setSpacing(16)
        self._rb_portrait = QRadioButton("纵向", orient_row)
        self._rb_landscape = QRadioButton("横向", orient_row)
        self._orientation_group.addButton(self._rb_portrait)
        self._orientation_group.addButton(self._rb_landscape)
        o_lay.addWidget(self._rb_portrait)
        o_lay.addWidget(self._rb_landscape)
        if self._config.page.orientation == Orientation.LANDSCAPE:
            self._rb_landscape.setChecked(True)
        else:
            self._rb_portrait.setChecked(True)
        form.addRow("页面方向:", orient_row)

        # 页边距
        margins_row = QWidget(c)
        m_lay = QHBoxLayout(margins_row)
        m_lay.setContentsMargins(0, 0, 0, 0)
        m_lay.setSpacing(8)
        self._margin_top = _spin(c, 0, 10, 0.1, self._config.page.margin_top, " cm")
        self._margin_bottom = _spin(c, 0, 10, 0.1, self._config.page.margin_bottom, " cm")
        self._margin_left = _spin(c, 0, 10, 0.1, self._config.page.margin_left, " cm")
        self._margin_right = _spin(c, 0, 10, 0.1, self._config.page.margin_right, " cm")
        for lbl, sb in (("上", self._margin_top), ("下", self._margin_bottom),
                        ("左", self._margin_left), ("右", self._margin_right)):
            box = QWidget(margins_row)
            b_lay = QVBoxLayout(box)
            b_lay.setContentsMargins(0, 0, 0, 0)
            b_lay.setSpacing(2)
            lab = QLabel(lbl, box)
            lab.setObjectName("hint")
            b_lay.addWidget(lab)
            b_lay.addWidget(sb)
            m_lay.addWidget(box)
        m_lay.addStretch(1)
        form.addRow("页边距 (cm):", margins_row)

        # 装订线
        self._gutter = _spin(c, 0, 5, 0.1, self._config.page.gutter, " cm")
        form.addRow("装订线 (cm):", self._gutter)

    def apply_to(self, config: FormatConfig):
        data = self._paper_combo.currentData()
        config.page.paper_size = PaperSize(data) if data else PaperSize.A4
        config.page.orientation = (Orientation.LANDSCAPE if self._rb_landscape.isChecked()
                                   else Orientation.PORTRAIT)
        config.page.margin_top = self._margin_top.value()
        config.page.margin_bottom = self._margin_bottom.value()
        config.page.margin_left = self._margin_left.value()
        config.page.margin_right = self._margin_right.value()
        config.page.gutter = self._gutter.value()


class TypographySection(CollapsibleSection):
    """字体排版分组"""

    def __init__(self, parent, config: FormatConfig, **kwargs):
        super().__init__(parent, "字体排版", "typography", **kwargs)
        self._config = config
        self._build()

    def _build(self):
        c = self.content
        form = _form(c)
        c.setLayout(form)
        t = self._config.typography

        def section_label(text):
            lab = QLabel(text, c)
            lab.setObjectName("sectionTitle")
            return lab

        # ── 正文字体 ──
        form.addRow(section_label("── 正文字体 ──"))

        self._body_font_cn = _combo(c, CN_FONTS, t.body_font_cn)
        form.addRow("中文字体:", self._body_font_cn)
        self._body_font_en = _combo(c, EN_FONTS, t.body_font_en)
        form.addRow("西文字体:", self._body_font_en)
        self._body_size = _spin(c, 6, 72, 0.5, t.body_font_size, " pt")
        form.addRow("字号 (pt):", self._body_size)
        self._body_color = ColorField(t.body_color, c)
        form.addRow("字体颜色:", self._body_color)

        # ── 段落格式 ──
        form.addRow(section_label("── 段落格式 ──"))

        self._line_group = QButtonGroup(c)
        line_mode_row = QWidget(c)
        lm_lay = QHBoxLayout(line_mode_row)
        lm_lay.setContentsMargins(0, 0, 0, 0)
        lm_lay.setSpacing(16)
        self._rb_multiple = QRadioButton("倍数", line_mode_row)
        self._rb_fixed = QRadioButton("固定值", line_mode_row)
        self._line_group.addButton(self._rb_multiple)
        self._line_group.addButton(self._rb_fixed)
        lm_lay.addWidget(self._rb_multiple)
        lm_lay.addWidget(self._rb_fixed)
        is_fixed = (t.line_spacing_mode == LineSpacingMode.FIXED)
        self._rb_fixed.setChecked(is_fixed)
        self._rb_multiple.setChecked(not is_fixed)
        form.addRow("行距模式:", line_mode_row)

        # 行距值（倍数 / 固定值 切换显示）
        self._line_spacing = _spin(c, 0.5, 5, 0.1, t.line_spacing, " 倍")
        self._line_fixed = _spin(c, 8, 60, 1, t.line_spacing_fixed, " pt")
        self._line_stack = QWidget(c)
        self._line_stack_lay = QHBoxLayout(self._line_stack)
        self._line_stack_lay.setContentsMargins(0, 0, 0, 0)
        self._line_stack_lay.setSpacing(8)
        self._line_stack_lay.addWidget(self._line_spacing)
        self._line_stack_lay.addWidget(self._line_fixed)
        self._line_stack_lay.addStretch(1)
        form.addRow("行距设置:", self._line_stack)
        self._update_line_mode_ui()
        self._rb_multiple.toggled.connect(lambda _: self._update_line_mode_ui())

        # 段间距
        sp_row = QWidget(c)
        sp_lay = QHBoxLayout(sp_row)
        sp_lay.setContentsMargins(0, 0, 0, 0)
        sp_lay.setSpacing(8)
        self._space_before = _spin(c, 0, 100, 1, t.para_space_before, " pt")
        self._space_after = _spin(c, 0, 100, 1, t.para_space_after, " pt")
        sp_lay.addWidget(QLabel("段前", sp_row))
        sp_lay.addWidget(self._space_before)
        sp_lay.addSpacing(8)
        sp_lay.addWidget(QLabel("段后", sp_row))
        sp_lay.addWidget(self._space_after)
        sp_lay.addStretch(1)
        form.addRow("段间距 (pt):", sp_row)

        self._indent_chars = _spin(c, 0, 8, 0.5, t.first_line_indent_chars, " 字符")
        form.addRow("首行缩进(字符):", self._indent_chars)

        self._alignment = _combo(c, list(ALIGNMENTS.keys()),
                                 ALIGN_REVERSE.get(t.alignment, "左对齐"))
        form.addRow("对齐方式:", self._alignment)

        # ── 标题样式 ──
        form.addRow(section_label("── 标题样式 ──"))

        self._heading_widgets = {}
        for level in ("h1", "h2", "h3"):
            hs = t.headings.get(level)
            if hs is None:
                continue
            label_text = {"h1": "H1 一级标题", "h2": "H2 二级标题", "h3": "H3 三级标题"}[level]
            lab = QLabel(label_text, c)
            lab.setObjectName("sectionTitle")
            form.addRow(lab)

            font_row = _hbox(
                _combo(c, CN_FONTS, hs.font_cn),
                _combo(c, EN_FONTS, hs.font_en),
                spacing=C.size("widget_row_spacing"))
            form.addRow("  字体:", font_row)

            size_bold_row = _hbox(
                _spin(c, 8, 48, 1, hs.font_size, " pt"),
                _checkbox("加粗", hs.bold), spacing=C.size("card_spacing"))
            form.addRow("  字号/加粗:", size_bold_row)

            color_field = ColorField(hs.color, c)
            form.addRow("  颜色:", color_field)

            self._heading_widgets[level] = {
                "font_cn": font_row.layout().itemAt(0).widget(),
                "font_en": font_row.layout().itemAt(1).widget(),
                "size": size_bold_row.layout().itemAt(0).widget(),
                "bold": size_bold_row.layout().itemAt(1).widget(),
                "color": color_field,
            }

    def _update_line_mode_ui(self):
        fixed = self._rb_fixed.isChecked()
        self._line_fixed.setVisible(fixed)
        self._line_spacing.setVisible(not fixed)

    def apply_to(self, config: FormatConfig):
        t = config.typography
        t.body_font_cn = self._body_font_cn.currentText()
        t.body_font_en = self._body_font_en.currentText()
        t.body_font_size = self._body_size.value()
        t.body_color = self._body_color.text() or "#000000"
        t.line_spacing_mode = (LineSpacingMode.FIXED if self._rb_fixed.isChecked()
                               else LineSpacingMode.MULTIPLE)
        t.line_spacing = self._line_spacing.value()
        t.line_spacing_fixed = self._line_fixed.value()
        t.para_space_before = self._space_before.value()
        t.para_space_after = self._space_after.value()
        t.first_line_indent_chars = self._indent_chars.value()
        t.alignment = ALIGNMENTS.get(self._alignment.currentText(), Alignment.LEFT)

        for level, w in self._heading_widgets.items():
            hs = t.headings.get(level)
            if hs is None:
                continue
            hs.font_cn = w["font_cn"].currentText()
            hs.font_en = w["font_en"].currentText()
            hs.font_size = w["size"].value()
            hs.bold = w["bold"].isChecked()
            hs.color = w["color"].text() or "#000000"


def _checkbox(text, checked=False, parent=None):
    cb = QCheckBox(text, parent)
    cb.setChecked(bool(checked))
    return cb


class ContentStylesSection(CollapsibleSection):
    """内容样式分组"""

    def __init__(self, parent, config: FormatConfig, **kwargs):
        super().__init__(parent, "内容样式", "paint", **kwargs)
        self._config = config
        self._build()

    def _build(self):
        c = self.content
        form = _form(c)
        c.setLayout(form)
        conf = self._config.content

        def section_label(text):
            lab = QLabel(text, c)
            lab.setObjectName("sectionTitle")
            return lab

        # 列表
        self._bullet = QLineEdit(conf.list_bullet_char, c)
        self._bullet.setFixedWidth(56)
        self._bullet.setMaxLength(4)
        form.addRow("无序列表符号:", self._bullet)

        # 引用块
        form.addRow(section_label("── 引用块 ──"))
        self._blockquote_bar = ColorField(conf.blockquote_bar_color, c)
        form.addRow("竖线颜色:", self._blockquote_bar)
        self._blockquote_bg = ColorField(conf.blockquote_bg_color, c)
        form.addRow("背景色:", self._blockquote_bg)
        self._blockquote_indent = _spin(c, 0, 5, 0.1, conf.blockquote_left_indent, " cm")
        form.addRow("左缩进 (cm):", self._blockquote_indent)

        # 代码块
        form.addRow(section_label("── 代码块 ──"))
        self._code_font = _combo(c, CODE_FONTS, conf.code_font)
        form.addRow("代码字体:", self._code_font)
        self._code_size = _spin(c, 6, 18, 0.5, conf.code_font_size, " pt")
        form.addRow("字号 (pt):", self._code_size)
        self._code_bg = ColorField(conf.code_bg_color, c)
        form.addRow("背景色:", self._code_bg)
        self._code_border = _checkbox("显示边框", conf.code_border)
        form.addRow("边框:", self._code_border)

        # 表格
        form.addRow(section_label("── 表格 ──"))
        self._table_header = ColorField(conf.table_header_bg, c)
        form.addRow("表头背景色:", self._table_header)
        self._table_border = _checkbox("显示表格边框", conf.table_border)
        form.addRow("表格边框:", self._table_border)

        # 图片
        form.addRow(section_label("── 图片 ──"))
        self._img_width = _spin(c, 10, 100, 5, conf.image_max_width_pct, " %")
        form.addRow("最大宽度 (%):", self._img_width)
        self._img_center = _checkbox("图片居中", conf.image_center)
        form.addRow("图片居中:", self._img_center)

        # 超链接
        form.addRow(section_label("── 超链接 ──"))
        self._link_color = ColorField(conf.link_color, c)
        form.addRow("链接颜色:", self._link_color)
        self._link_underline = _checkbox("显示下划线", conf.link_underline)
        form.addRow("显示下划线:", self._link_underline)

    def apply_to(self, config: FormatConfig):
        c = config.content
        c.list_bullet_char = self._bullet.text() or "•"
        c.blockquote_bar_color = self._blockquote_bar.text() or "#000000"
        c.blockquote_bg_color = self._blockquote_bg.text() or "#FFFFFF"
        c.blockquote_left_indent = self._blockquote_indent.value()
        c.code_font = self._code_font.currentText()
        c.code_font_size = self._code_size.value()
        c.code_bg_color = self._code_bg.text() or "#F3F4F6"
        c.code_border = self._code_border.isChecked()
        c.table_header_bg = self._table_header.text() or "#E5E7EB"
        c.table_border = self._table_border.isChecked()
        c.image_max_width_pct = self._img_width.value()
        c.image_center = self._img_center.isChecked()
        c.link_color = self._link_color.text() or "#3B82F6"
        c.link_underline = self._link_underline.isChecked()


class AdvancedSection(CollapsibleSection):
    """高级特性分组"""

    def __init__(self, parent, config: FormatConfig, **kwargs):
        super().__init__(parent, "高级特性", "settings", **kwargs)
        self._config = config
        self._build()

    def _build(self):
        c = self.content
        form = _form(c)
        c.setLayout(form)
        adv = self._config.advanced

        def section_label(text):
            lab = QLabel(text, c)
            lab.setObjectName("sectionTitle")
            return lab

        # 标题编号
        self._heading_num = _checkbox("自动标题编号", adv.heading_numbering)
        form.addRow("", self._heading_num)
        self._heading_num_fmt = _combo(c, ["1.", "1)", "第1章"], adv.heading_numbering_format)
        form.addRow("编号格式:", self._heading_num_fmt)

        # 目录
        self._toc = _checkbox("自动生成目录", adv.auto_toc)
        form.addRow("", self._toc)
        self._toc_depth = _spin(c, 1, 6, 1, adv.toc_depth, " 级")
        form.addRow("目录深度:", self._toc_depth)

        # 页眉页脚
        form.addRow(section_label("── 页眉页脚 ──"))
        self._header = QLineEdit(adv.header_text, c)
        form.addRow("页眉文字:", self._header)
        self._footer = QLineEdit(adv.footer_text, c)
        form.addRow("页脚文字:", self._footer)

        # 封面
        form.addRow(section_label("── 封面页 ──"))
        self._cover = _checkbox("启用封面", adv.cover_enabled)
        form.addRow("", self._cover)
        self._cover_title = QLineEdit(adv.cover_title, c)
        form.addRow("文档标题:", self._cover_title)
        self._cover_author = QLineEdit(adv.cover_author, c)
        form.addRow("作者:", self._cover_author)
        self._cover_date = QLineEdit(adv.cover_date, c)
        form.addRow("日期 (空=今天):", self._cover_date)

        # 水印
        form.addRow(section_label("── 水印 ──"))
        self._wm_text = QLineEdit(adv.watermark_text, c)
        form.addRow("水印文字:", self._wm_text)
        self._wm_size = _spin(c, 8, 200, 1, adv.watermark_font_size, " pt")
        form.addRow("水印字号 (pt):", self._wm_size)
        self._wm_opacity = _spin(c, 0, 1, 0.05, adv.watermark_opacity, "", decimals=2)
        form.addRow("透明度 (0-1):", self._wm_opacity)

    def apply_to(self, config: FormatConfig):
        adv = config.advanced
        adv.heading_numbering = self._heading_num.isChecked()
        adv.heading_numbering_format = self._heading_num_fmt.currentText()
        adv.auto_toc = self._toc.isChecked()
        adv.toc_depth = int(self._toc_depth.value())
        adv.header_text = self._header.text()
        adv.footer_text = self._footer.text()
        adv.cover_enabled = self._cover.isChecked()
        adv.cover_title = self._cover_title.text()
        adv.cover_author = self._cover_author.text()
        adv.cover_date = self._cover_date.text()
        adv.watermark_text = self._wm_text.text()
        adv.watermark_font_size = self._wm_size.value()
        adv.watermark_opacity = self._wm_opacity.value()


class PresetsSection(CollapsibleSection):
    """预设管理分组"""

    def __init__(self, parent, config: FormatConfig, on_load=None, on_sync=None, **kwargs):
        super().__init__(parent, "预设管理", "bookmark", **kwargs)
        self._config = config
        self._on_load = on_load
        self._on_sync = on_sync
        self._build()
        self._refresh_list()

    def _build(self):
        c = self.content
        form = _form(c)
        c.setLayout(form)

        # 选择预设 + 按钮
        self._preset_combo = QComboBox(c)
        form.addRow("选择预设:", self._preset_combo)

        btn_row = _hbox()
        for text, ic, cmd, obj in (
                ("加载", "file-import", self._do_load, "primary"),
                ("保存", "file-export", self._do_save, "primary"),
                ("删除", "trash", self._do_delete, "danger")):
            b = QPushButton(text, c)
            b.setIcon(icon_res.colored_icon(ic, size=C.size("icon_small")))
            b.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
            b.setObjectName(obj)
            b.clicked.connect(cmd)
            btn_row.layout().addWidget(b)
        btn_row.layout().addStretch(1)
        form.addRow("", btn_row)

        # 另存为
        save_row = _hbox()
        self._preset_name = QLineEdit(c)
        self._preset_name.setPlaceholderText("输入预设名称…")
        save_btn = QPushButton("保存", c)
        save_btn.setIcon(icon_res.colored_icon(
            "file-export", size=C.size("icon_small")))
        save_btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
        save_btn.setObjectName("primary")
        save_btn.clicked.connect(self._do_save_as)
        save_row.layout().addWidget(self._preset_name, 1)
        save_row.layout().addWidget(save_btn)
        form.addRow("另存为:", save_row)

        # 导入导出 + 恢复默认（同一行：左侧导入/导出，右侧恢复默认）
        ie_row = _hbox()
        for text, ic, cmd in (("导入预设", "download", self._do_import),
                              ("导出当前", "upload", self._do_export)):
            b = QPushButton(text, c)
            b.setIcon(icon_res.colored_icon(ic, size=C.size("icon_small")))
            b.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
            b.setObjectName("ghost")
            b.clicked.connect(cmd)
            ie_row.layout().addWidget(b)
        ie_row.layout().addStretch(1)
        reset_btn = QPushButton("恢复默认配置", c)
        reset_btn.setIcon(icon_res.colored_icon("refresh"))
        reset_btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
        reset_btn.setObjectName("danger")
        reset_btn.clicked.connect(self._do_reset)
        ie_row.layout().addWidget(reset_btn)
        form.addRow("", ie_row)

    def _refresh_list(self):
        names = presets.list_presets()
        self._preset_combo.clear()
        self._preset_combo.addItems(names)
        cur = getattr(self._config, "name", "")
        if cur in names:
            self._preset_combo.setCurrentText(cur)

    def _selected(self) -> str:
        return self._preset_combo.currentText().strip()

    def _do_load(self):
        name = self._selected()
        if not name:
            QMessageBox.warning(self, "提示", "请先选择一个预设")
            return
        cfg = presets.load_preset(name)
        if cfg:
            if self._on_load:
                self._on_load(cfg)
            QMessageBox.information(self, "成功", f"已加载预设: {name}")
        else:
            QMessageBox.critical(self, "失败", f"无法加载预设: {name}")

    def _do_save(self):
        name = self._selected()
        if not name:
            QMessageBox.warning(self, "提示", "请先选择一个预设")
            return
        cfg = self._on_sync() if self._on_sync else self._config
        presets.save_preset(cfg, name)
        self._refresh_list()
        QMessageBox.information(self, "成功", f"已保存预设: {name}")

    def _do_save_as(self):
        name = self._preset_name.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "请输入预设名称")
            return
        cfg = self._on_sync() if self._on_sync else self._config
        presets.save_preset(cfg, name)
        self._refresh_list()
        self._preset_name.clear()
        QMessageBox.information(self, "成功", f"已保存为新预设: {name}")

    def _do_delete(self):
        name = self._selected()
        if not name:
            QMessageBox.warning(self, "提示", "请先选择一个预设")
            return
        ret = QMessageBox.question(
            self, "确认", f"确定要删除预设「{name}」吗？\n（内置预设不可删除）")
        if ret != QMessageBox.Yes:
            return
        if presets.delete_preset(name):
            self._refresh_list()
            QMessageBox.information(self, "成功", f"已删除预设: {name}")
        else:
            QMessageBox.critical(self, "失败", f"无法删除预设「{name}」（可能是内置预设）")

    def _do_import(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "导入预设", "", "JSON 文件 (*.json);;所有文件 (*.*)")
        if not path:
            return
        cfg = presets.import_preset(path)
        if cfg:
            if self._on_load:
                self._on_load(cfg)
            QMessageBox.information(self, "成功", f"已导入预设: {cfg.name}")
        else:
            QMessageBox.critical(self, "失败", "无法读取预设文件")

    def _do_export(self):
        cfg = self._on_sync() if self._on_sync else self._config
        path, _ = QFileDialog.getSaveFileName(
            self, "导出预设", "", "JSON 文件 (*.json)")
        if not path:
            return
        presets.export_preset(cfg, path)
        QMessageBox.information(self, "成功", f"已导出预设到:\n{path}")

    def _do_reset(self):
        ret = QMessageBox.question(
            self, "确认", "确定要恢复到默认配置吗？\n当前未保存的修改将丢失。")
        if ret != QMessageBox.Yes:
            return
        cfg = presets.reset_to_default()
        if self._on_load:
            self._on_load(cfg)
        QMessageBox.information(self, "成功", "已恢复默认配置")


# ════════════════════════════════════════════
#  主面板
# ════════════════════════════════════════════

class FormatPanel(QWidget):
    """MD → DOCX 格式控制总面板（可嵌入任意容器）"""

    def __init__(self, parent, config: FormatConfig = None, **kwargs):
        super().__init__(parent, **kwargs)
        if config is None:
            config = FormatConfig.default_chinese()
        self._config = config
        self._sections = {}

        # 可滚动容器
        self._scroll = QScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._inner = QWidget()
        self._inner.setObjectName("scrollInner")
        self._inner_lay = QVBoxLayout(self._inner)
        self._inner_lay.setContentsMargins(4, 4, 8, 4)
        self._inner_lay.setSpacing(4)
        self._scroll.setWidget(self._inner)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._scroll)

        self._build_sections()

    def _build_sections(self):
        inner = self._inner
        lay = self._inner_lay
        cfg = self._config

        self._presets_section = PresetsSection(
            inner, cfg, on_load=self._on_preset_loaded, on_sync=self.get_config)
        self._page_section = PageSetupSection(inner, cfg)
        self._typo_section = TypographySection(inner, cfg)
        self._content_section = ContentStylesSection(inner, cfg)
        self._advanced_section = AdvancedSection(inner, cfg)

        for s in (self._presets_section, self._page_section,
                  self._typo_section, self._content_section,
                  self._advanced_section):
            lay.addWidget(s)
        lay.addStretch(1)

    def _on_preset_loaded(self, new_config: FormatConfig):
        """预设加载回调：更新内部配置并重建 UI"""
        self._config = new_config
        self.load_config(new_config)

    def load_config(self, config: FormatConfig):
        """从外部加载配置并刷新 UI"""
        self._config = config
        # 销毁旧分组并重建
        while self._inner_lay.count():
            item = self._inner_lay.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        self._build_sections()

    def get_config(self) -> FormatConfig:
        """从 UI 读取最新配置值"""
        self._page_section.apply_to(self._config)
        self._typo_section.apply_to(self._config)
        self._content_section.apply_to(self._config)
        self._advanced_section.apply_to(self._config)
        return self._config


# ════════════════════════════════════════════
#  弹窗封装
# ════════════════════════════════════════════

class SetFormat(OptionsDialogBase):
    """「格式选项 - MD → DOCX」独立窗口"""

    def __init__(self, config: FormatConfig = None, parent=None):
        super().__init__("格式选项 - MD → DOCX", parent)
        self.fit_size(640, 720, min_w=560, min_h=560)

        # 顶栏
        self.build_header("格式选项（仅 MD → DOCX 生效）")

        # 面板
        self.panel = FormatPanel(self, config)
        self._lay.addWidget(self.panel, 1)

        # 底部按钮
        self._lay.addWidget(self.build_buttons(
            ok_text="完成", ok_icon="check", ok_min_width=120,
            on_ok=self.accept, margins=(16, 10, 16, 14)))

    def get_config(self) -> FormatConfig:
        return self.panel.get_config()


# ════════════════════════════════════════════
#  独立测试
# ════════════════════════════════════════════

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    from ui.theme import APP_STYLESHEET

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLESHEET)

    cfg = FormatConfig.default_chinese()
    dlg = SetFormat(cfg)
    dlg.show()
    app.exec()
    updated = dlg.get_config()
    print(updated.to_json())
