"""
OCTools/ui/options/set_ui.py
───────────────────────────────────────────────
全局 UI 风格设置窗口（Setui）

包含：
  1. 主题方案（浅色 / 深色，默认两套，用户可各自覆盖）
  2. 字体族（从 config/ui_config.json fonts.families 读取候选）
  3. 颜色（主色 / 页面背景 / 卡片背景 / 正文 / 次要文字 / 边框）
  4. 尺寸（全局缩放、基础字号、边框粗细、滚动条宽度、卡片/按钮圆角、输入框/按钮高度）

行为：
  - 调整立即生效并自动保存（config/presets.py 的应用设置），点「确定」仅关闭；
  - 「恢复默认」清空全部自定义覆盖与缩放，仅保留主题选择。
"""

import copy

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QComboBox,
    QSlider, QSpinBox, QPushButton, QWidget, QFrame, QColorDialog,
    QApplication,
)

from config import presets
from config.ui_config import CONFIG as C
from ui.theme import apply_theme as _apply_theme
from ui.theme import theme_names as _theme_names

from ui.options._base import OptionsDialogBase
from ui.style_hook import StyleHookMixin


# 可自定义的颜色（说明文字, colors 段 key）
_COLOR_ROWS = [
    ("主色调", "primary"),
    ("页面背景", "bg"),
    ("卡片背景", "card"),
    ("正文文字", "text"),
    ("次要文字", "text_light"),
    ("边框颜色", "border"),
]

# 可自定义的数字参数：段, key, 标签, 最小值, 最大值, 单位
_NUM_ROWS = [
    ("fonts", "body", "基础字号", 9, 26, "px"),
    ("sizes", "border_w", "边框粗细", 1, 4, "px"),
    ("sizes", "scroll_w", "滚动条宽度", 6, 20, "px"),
    ("sizes", "radius_card", "卡片圆角", 0, 28, "px"),
    ("sizes", "radius_btn", "按钮圆角", 0, 24, "px"),
    ("sizes", "input_min_h", "输入框高度", 20, 48, "px"),
    ("sizes", "btn_h", "按钮高度", 24, 48, "px"),
    ("sizes", "cta_h", "主操作按钮高度", 36, 64, "px"),
]


class _Group(StyleHookMixin, QFrame):
    """弹窗内的分组卡片（全局 QSS 的 QFrame#card 样式）。"""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(
            C.size("group_padding_h"), C.size("group_padding_v"),
            C.size("group_padding_h"), C.size("group_padding_v"))
        lay.setSpacing(C.size("form_row_spacing"))
        self._title_label = QLabel(title)
        lay.addWidget(self._title_label)
        self.form = QFormLayout()
        self.form.setHorizontalSpacing(C.size("form_spacing"))
        self.form.setVerticalSpacing(C.size("form_spacing"))
        self.form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        lay.addLayout(self.form)
        self._apply_inline_style()

    def _apply_inline_style(self):
        """主题切换时由 StyleHookMixin 调用：重刷分组标题配色（随主题变）。"""
        self._title_label.setStyleSheet(
            f"color: {C.color('text')}; font-size: {C.font('group_header')}px;"
            f" font-weight: {C.font('group_header_weight')};")


class Setui(StyleHookMixin, OptionsDialogBase):
    """全局 UI 风格设置窗口"""

    def __init__(self, config=None, parent=None):
        super().__init__("全局 UI 风格", parent)
        self._config = config      # 预留，保持弹窗构造签名兼容
        self.resize(640, 560)
        self.setMinimumSize(600, 460)
        self._unit_labels = []

        self._settings = presets.load_app_settings() or {}
        self._apply_timer = QTimer(self)
        self._apply_timer.setSingleShot(True)
        self._apply_timer.setInterval(250)
        self._apply_timer.timeout.connect(self._commit_theme)

        self.build_header("全局 UI 风格")
        body, b_lay = self.build_scroll_body(margins=(20, 16, 20, 14))

        # ── 主题与字体 ──
        group1, f1 = self._make_group("主题与字体")
        self._build_theme_font_form(f1)
        b_lay.addWidget(group1)

        # ── 颜色 ──
        group2, f2 = self._make_group("颜色")
        self._build_colors_form(f2)
        b_lay.addWidget(group2)

        # ── 尺寸 ──
        group3, f3 = self._make_group("尺寸")
        self._build_sizes_form(f3)
        b_lay.addWidget(group3)

        hint = QLabel("调整立即生效并自动保存；「恢复默认」清空全部自定义，仅保留主题选择。")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        b_lay.addWidget(hint)

        b_lay.addStretch(1)
        b_lay.addWidget(self.build_buttons(
            left_text="恢复默认", left_on_click=self._reset_theme,
            ok_text="确定", ok_icon="check", on_ok=self._ok,
            margins=(0, 6, 0, 0)))
        self._apply_inline_style()

    # ──────────────────────────────────────
    #  构建
    # ──────────────────────────────────────

    def _apply_inline_style(self):
        """主题切换时由 StyleHookMixin 调用：重刷缩放值、单位、颜色按钮配色。"""
        if getattr(self, "_scale_label", None) is not None:
            self._scale_label.setStyleSheet(
                f"color: {C.color('primary')}; font-size: {C.font('hint')}px;"
                f" font-weight: {C.font('checked_weight')};")
        for unit_label in getattr(self, "_unit_labels", []):
            unit_label.setStyleSheet(
                f"color: {C.color('text_light')}; font-size: {C.font('hint')}px;")
        for btn in getattr(self, "_color_btns", {}).values():
            self._paint_color_btn(btn)
    def _make_group(self, title: str):
        group = _Group(title, self)
        return group, group.form

    def _build_theme_font_form(self, form: QFormLayout):
        settings = self._settings
        current_overrides = settings.get("ui_overrides") or {}

        # 主题方案
        theme_combo = QComboBox(self)
        theme_combo.setMinimumWidth(C.size("combo_min_w_small"))
        for key, disp in (_theme_names() or {"light": "浅色"}).items():
            theme_combo.addItem(disp, key)
        idx = theme_combo.findData(settings.get("ui_theme") or C.theme())
        theme_combo.setCurrentIndex(idx if idx >= 0 else 0)

        # 字体族
        fam_choices = C.raw("fonts", "families") or ["Microsoft YaHei UI"]
        fam_combo = QComboBox(self)
        fam_combo.setMinimumWidth(C.size("combo_min_w_small"))
        for fam in fam_choices:
            fam_combo.addItem(fam, fam)
        cur_fam = (current_overrides.get("fonts") or {}).get("family") \
            or C._raw_no_override("fonts", "family") or "Microsoft YaHei UI"
        fam_idx = fam_combo.findData(cur_fam)
        fam_combo.setCurrentIndex(fam_idx if fam_idx >= 0 else 0)

        form.addRow("主题方案:", theme_combo)
        form.addRow("字体族:", fam_combo)

        self._theme_combo = theme_combo
        self._fam_combo = fam_combo

        theme_combo.currentIndexChanged.connect(
            lambda _i: self._schedule_theme_apply())
        fam_combo.currentIndexChanged.connect(
            lambda _i: self._dirty_family_change())

    def _build_colors_form(self, form: QFormLayout):
        current_overrides = self._settings.get("ui_overrides") or {}
        color_btns = {}
        for _label, key in _COLOR_ROWS:
            btn = QPushButton(self)
            btn.setFixedSize(44, 24)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setProperty("hex", (current_overrides.get("colors") or {}).get(key)
                            or C._raw_no_override("colors", key) or C.color(key))
            self._paint_color_btn(btn)
            row = QWidget(self)
            rl = QHBoxLayout(row)
            rl.setContentsMargins(0, 0, 0, 0)
            rl.setSpacing(C.size("form_row_spacing"))
            rl.addWidget(btn)
            rl.addWidget(QLabel(_label, row))
            rl.addStretch(1)
            form.addRow("", row)
            color_btns[key] = btn
        self._color_btns = color_btns
        for key, btn in color_btns.items():
            btn.clicked.connect(lambda _=False, k=key: self._pick_color(k))

    def _build_sizes_form(self, form: QFormLayout):
        settings = self._settings

        # 全局缩放
        scale_val = settings.get("ui_scale", 1.0)
        try:
            pct = int(round(float(scale_val) * 100))
        except (TypeError, ValueError):
            pct = 100
        scale_slider = QSlider(Qt.Horizontal, self)
        scale_slider.setRange(80, 140)
        scale_slider.setValue(pct)
        scale_label = QLabel(f"×{pct / 100:.2f}")
        scale_label.setMinimumWidth(46)
        scale_label.setAlignment(Qt.AlignRight)
        self._scale_label = scale_label
        scale_row = QWidget(self)
        sl = QHBoxLayout(scale_row)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(C.size("form_row_spacing"))
        sl.addWidget(scale_slider, 1)
        sl.addWidget(scale_label)
        form.addRow("全局缩放:", scale_row)

        # 数字参数
        num_spins = {}
        for sec_name, key, label, lo, hi, unit in _NUM_ROWS:
            spin = QSpinBox(self)
            spin.setRange(lo, hi)
            val = C.font(key) if sec_name == "fonts" else C.size(key)
            spin.setValue(val)
            spin.setMinimumWidth(C.size("min_width_96"))
            row = QWidget(self)
            rl = QHBoxLayout(row)
            rl.setContentsMargins(0, 0, 0, 0)
            rl.setSpacing(C.size("form_row_spacing"))
            rl.addWidget(spin)
            unit_label = QLabel(unit, row)
            self._unit_labels.append(unit_label)
            rl.addWidget(unit_label)
            rl.addStretch(1)
            form.addRow(f"{label}:", row)
            num_spins[(sec_name, key)] = spin

        self._scale_slider = scale_slider
        self._scale_label = scale_label
        self._num_spins = num_spins

        scale_slider.valueChanged.connect(self._on_scale_changed)
        for (s, k), sp in num_spins.items():
            sp.valueChanged.connect(lambda _v, t=(s, k): self._on_num_changed(t))

        self._initial_nums = {(s, k): sp.value() for (s, k), sp in num_spins.items()}
        self._initial_family = self._fam_combo.currentData()
        self._initial_colors = {k: btn.property("hex") for k, btn in self._color_btns.items()}
        self._dirty_colors = set()
        self._dirty_nums = set()
        self._dirty_family = False

    # ──────────────────────────────────────
    #  控件回调
    # ──────────────────────────────────────
    def _paint_color_btn(self, btn: QPushButton):
        color = btn.property("hex") or C.color("primary")
        btn.setStyleSheet(
            f"QPushButton {{ background: {color};"
            f" border: 1px solid {C.color('border')};"
            f" border-radius: {C.size('radius_btn')}px; }}")

    def _pick_color(self, key: str):
        btn = self._color_btns[key]
        color = QColorDialog.getColor(
            QColor(btn.property("hex")), self, f"选择颜色：{key}")
        if color.isValid():
            btn.setProperty("hex", color.name())
            self._paint_color_btn(btn)
            self._dirty_colors.add(key)
            self._schedule_theme_apply()

    def _on_scale_changed(self, value: int):
        self._scale_label.setText(f"×{value / 100:.2f}")
        self._schedule_theme_apply()

    def _dirty_family_change(self):
        self._dirty_family = True
        self._schedule_theme_apply()

    def _on_num_changed(self, key):
        self._dirty_nums.add(key)
        self._schedule_theme_apply()

    def _schedule_theme_apply(self):
        """合并多次连续调整，250ms 去抖后再统一应用（重建由主窗口完成）。"""
        self._apply_timer.start()

    # ──────────────────────────────────────
    #  收集 / 提交
    # ──────────────────────────────────────
    def _gather_theme(self):
        """从控件收集主题/缩放/覆盖到 self._settings。

        覆盖写入策略：
          - 以当前生效的覆盖（C.theme_settings）为基底，保留未改动的既有覆盖；
          - 仅处理用户动过的控件；若其值回到主题默认，则从覆盖中移除；
          - 因此仅拖动缩放/切换主题不会把默认值误锁为自定义覆盖。
        """
        self._settings["ui_theme"] = self._theme_combo.currentData()
        pct = self._scale_slider.value()
        scale = round(pct / 100.0, 3)
        self._settings["ui_scale"] = scale

        overrides = copy.deepcopy(C.theme_settings().get("ui_overrides") or {})

        # 颜色
        colors = overrides.get("colors", {})
        for key, btn in self._color_btns.items():
            if key not in self._dirty_colors:
                continue
            curr = btn.property("hex") or ""
            default = C._raw_no_override("colors", key) or ""
            if curr.lower() == default.lower():
                colors.pop(key, None)
            else:
                colors[key] = curr
        if colors:
            overrides["colors"] = colors
        elif "colors" in overrides:
            del overrides["colors"]

        # 数字参数与字体
        fonts = overrides.get("fonts", {})
        sizes = overrides.get("sizes", {})
        for (sec_name, key), spin in self._num_spins.items():
            if key not in self._dirty_nums:
                continue
            value = spin.value()
            if value == C.effective_if_unoverridden(sec_name, key, scale):
                (fonts if sec_name == "fonts" else sizes).pop(key, None)
            else:
                (fonts if sec_name == "fonts" else sizes)[key] = value
        if self._dirty_family:
            fam = self._fam_combo.currentData()
            if fam and fam == (C._raw_no_override("fonts", "family") or ""):
                fonts.pop("family", None)
            elif fam:
                fonts["family"] = fam
        if fonts:
            overrides["fonts"] = fonts
        elif "fonts" in overrides:
            del overrides["fonts"]
        if sizes:
            overrides["sizes"] = sizes
        elif "sizes" in overrides:
            del overrides["sizes"]

        self._settings["ui_overrides"] = overrides

    def _commit_theme(self, gather: bool = True):
        if gather:
            self._gather_theme()
        presets.save_app_settings(self._settings)
        app = QApplication.instance()
        if app is not None:
            _apply_theme(app, self._settings)

    def _reset_theme(self):
        """清空自定义覆盖与缩放（保留主题选择），立即生效。"""
        self._settings["ui_overrides"] = {}
        self._settings["ui_scale"] = 1.0
        self._commit_theme(gather=False)

    def _ok(self):
        self.accept()