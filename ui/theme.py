"""
OCTools/ui/theme.py
───────────────────────────────────────────────
PySide6 全局主题：从 ui/ui_config.json 读取所有 UI 参数并生成全局 QSS 样式表。

设计语言（2026 重构版）：
  - 清爽现代蓝：浅灰蓝页面背景 + 白色卡片 + 靛蓝主色
  - 统一控件高度与圆角，减少视觉噪音，强调留白与层级
  - 左侧导航激活态带主色指示条；卡片统一 12px 圆角 + 细边框

所有颜色 / 字体字号 / 圆角 / 内边距 / 最小高度 / 图标尺寸 等 UI 参数
都在 ui_config.json 中声明，此处仅负责按名字取用并拼接 QSS。

用法:
  from ui.theme import APP_STYLESHEET, THEME
  app.setStyleSheet(APP_STYLESHEET)
"""

import os

from config.ui_config import CONFIG as C


class _LiveTheme(dict):
    """THEME['key'] 实时读取当前主题色彩。
    切换主题 / 覆盖后无需重建该对象，取值始终与 CONFIG 一致。
    """

    def __getitem__(self, key):
        return C.color(key)

    def get(self, key, default=None):
        v = C.color(key)
        return v if v else default


# ── 配色常量（实时取自 JSON 当前主题，兼容旧代码 THEME['key'] 访问）────
THEME = _LiveTheme()

T = THEME  # 简短别名

# ── 便捷读取（复用 JSON 配置）──────────────────
def _c(key):
    return C.color(key)


def _s(key):
    return C.size(key)


def _f(key):
    return C.font(key)


def _nav_align() -> str:
    """侧栏导航按钮文字对齐，取自 sidebar.button.alignment。"""
    return C.section("sidebar").get("button", {}).get("alignment", "left")


def _tinted_icon(name: str, color: str) -> str:
    """把 currentColor SVG 模板着色后写入 ui/styles/_gen/，返回绝对路径。

    QSS 的 image:url() 不支持 currentColor（会渲染成黑色，深色主题下不可见），
    因此按当前主题色生成着色副本再引用。失败时回退原文件路径。
    """
    src = os.path.join(C.using_dir(), name)
    try:
        with open(src, "r", encoding="utf-8") as f:
            content = f.read()
        tinted = content.replace("currentColor", color)
    except Exception:
        return src.replace("\\", "/")
    gen_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "styles", "_gen")
    out = os.path.join(gen_dir, name.replace(".svg", ".tinted.svg"))
    try:
        os.makedirs(gen_dir, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(tinted)
        return out.replace("\\", "/")
    except Exception:
        return src.replace("\\", "/")


def _qss() -> str:
    """根据 JSON 配置构建全局样式表"""
    monofam = f"{C.raw('fonts', 'mono_family')}, {C.raw('fonts', 'mono_fallback')}, monospace"
    fam = f"{C.raw('fonts', 'family')}, {C.raw('fonts', 'fallback_family')}, sans-serif"
    check_icon = os.path.join(C.using_dir(), "square-check.svg").replace("\\", "/")
    radio_icon = os.path.join(C.using_dir(), "square-rounded-check.svg").replace("\\", "/")
    square_icon = os.path.join(C.using_dir(), "square.svg").replace("\\", "/")
    square_rounded_icon = os.path.join(C.using_dir(), "square-rounded.svg").replace("\\", "/")
    # 下拉箭头：主题色 chevron（收起向下 / 展开向上）
    chevron_down = _tinted_icon("chevron-down.svg", _c('text_light'))
    chevron_up = _tinted_icon("chevron-up.svg", _c('text_light'))
    return f"""
/* ══════════ 全局 ══════════ */
* {{
    font-family: {fam};
}}
QMainWindow, QDialog {{
    background: {_c('bg')};
}}
QWidget {{
    color: {_c('text')};
    font-size: {_f('body')}px;
}}

/* ══════════ 标签层级 ══════════ */
QLabel {{
    background: transparent;
    color: {_c('text')};
}}
QLabel#hint {{
    color: {_c('text_light')};
    font-size: {_f('hint')}px;
}}
QLabel#formLabel {{
    color: {_c('text_light')};
    font-size: {_f('form_label')}px;
}}
QLabel#fieldLabel {{
    color: {_c('text')};
    font-size: {_f('body')}px;
    font-weight: {_f('field_label_weight')};
}}
/* 无边框滚动区：与主题无关的结构性样式，供滚动容器复用 */
QScrollArea#bareScroll {{
    border: none;
    background: transparent;
}}
/* 透明承载面：仅去掉自身底色，不参与主题配色 */
QWidget#bareSurface {{
    background: transparent;
}}
QLabel#pageTitle {{
    font-size: {_f('page_title')}px;
    font-weight: {_f('page_title_weight')};
    color: {_c('text')};
}}
QLabel#pageSubtitle {{
    font-size: {_f('page_subtitle')}px;
    color: {_c('text_light')};
}}
QLabel#cardTitle {{
    font-size: {_f('card_title')}px;
    font-weight: {_f('card_title_weight')};
    color: {_c('text')};
}}
QLabel#sectionTitle {{
    font-size: {_f('section_title')}px;
    font-weight: {_f('section_title_weight')};
    color: {_c('primary')};
}}
QLabel#summary {{
    font-size: {_f('summary')}px;
    color: {_c('text_light')};
}}

/* ══════════ 卡片 ══════════ */
QFrame#card {{
    background: {_c('card')};
    border: {_s('border_w')}px solid {_c('border')};
    border-radius: {_s('radius_card')}px;
}}

/* ══════════ 弹窗顶栏 ══════════ */
QFrame#header {{
    background: {_c('card')};
    border-bottom: {_s('border_w')}px solid {_c('border')};
    border-top-left-radius: {_s('radius_card')}px;
    border-top-right-radius: {_s('radius_card')}px;
}}
QLabel#headerTitle {{
    font-size: {_f('page_title')}px;
    font-weight: {_f('page_title_weight')};
    color: {_c('text')};
}}

/* ══════════ 设置分组 ══════════ */
QFrame#SettingsSection {{
    background: {_c('card')};
    border: {_s('border_w')}px solid {_c('border')};
    border-radius: {_s('radius_card')}px;
}}

/* ══════════ 普通按钮 ══════════ */
QPushButton {{
    background: {_c('hover')};
    border: {_s('border_w')}px solid {_c('border')};
    border-radius: {_s('radius_btn')}px;
    padding: 0px {_s('btn_padding_h')}px;
    min-height: {_s('btn_h') - 2 * _s('border_w')}px;
    color: {_c('text')};
    font-weight: {_f('btn_weight')};
}}
QPushButton:hover {{
    background: {_c('border')};
}}
QPushButton:pressed {{
    background: {_c('pressed')};
}}
QPushButton:disabled {{
    background: {_c('disabled_bg')};
    color: {_c('disabled_fg')};
    border-color: {_c('disabled_border')};
}}

QPushButton#primary {{
    background: {_c('primary')};
    color: {_c('white')};
    border: none;
    min-height: {_s('btn_h')}px;
}}
QPushButton#primary:hover {{
    background: {_c('primary_dark')};
}}
QPushButton#primary:pressed {{
    background: {_c('primary_dark')};
}}
QPushButton#primary:disabled {{
    background: {_c('primary_btn_disabled_bg')};
    color: {_c('primary_btn_disabled_fg')};
}}

QPushButton#secondary {{
    background: {_c('secondary')};
    color: {_c('white')};
    border: none;
    min-height: {_s('btn_h')}px;
}}
QPushButton#secondary:hover {{
    background: {_c('secondary_dark')};
}}

QPushButton#danger {{
    background: {_c('danger')};
    color: {_c('white')};
    border: none;
    min-height: {_s('btn_h')}px;
}}
QPushButton#danger:hover {{
    background: {_c('danger_dark')};
}}

QPushButton#ghost {{
    background: {_c('hover')};
    border: {_s('border_w')}px solid {_c('border')};
    color: {_c('text')};
}}
QPushButton#ghost:hover {{
    background: {_c('pressed')};
    color: {_c('text')};
}}

/* 设置弹窗内按钮统一用主题文字色（黑字），避免白字在部分系统上渲染不可见 */
QDialog QPushButton#primary,
QDialog QPushButton#secondary,
QDialog QPushButton#danger {{
    color: {_c('text')};
}}

/* ══════════ 侧栏导航按钮 ══════════ */
QPushButton#navBtn {{
    background: transparent;
    border: none;
    border-radius: {_s('radius_btn')}px;
    padding: 0px {_s('nav_padding_h')}px;
    min-height: {_s('btn_h')}px;
    color: {_c('nav_text')};
    font-size: {_f('nav')}px;
    font-weight: {_f('nav_weight')};
    text-align: {_nav_align()};
}}
QPushButton#navBtn:hover {{
    background: {_c('hover')};
    color: {_c('nav_text_hover')};
}}
QPushButton#navBtn:checked {{
    background: {_c('nav_active_bg')};
    color: {_c('nav_active_fg')};
}}
QPushButton#navBtn:pressed {{
    background: {_c('pressed')};
}}

QPushButton#convertBtn {{
    background: {_c('primary_btn_bg')};
    color: {_c('text')};
    border: none;
    border-radius: {_s('convert_radius')}px;
    font-size: {_f('convert')}px;
    font-weight: {_f('convert_weight')};
    letter-spacing: {_f('convert_letter_spacing')}px;
    padding: 0px {_s('convert_padding_h')}px;
    min-height: {_s('cta_h')}px;
}}
QPushButton#convertBtn:hover {{
    background: {_c('primary_btn_hover')};
}}
QPushButton#convertBtn:pressed {{
    background: {_c('primary_btn_pressed')};
}}
QPushButton#convertBtn:disabled {{
    background: {_c('primary_btn_disabled_bg')};
    color: {_c('primary_btn_disabled_fg')};
}}

/* ══════════ 输入控件 ══════════ */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QDateTimeEdit, QDateEdit {{
    background: {_c('card')};
    border: {_s('border_w')}px solid {_c('input_border')};
    border-radius: {_s('radius_input')}px;
    padding: {_s('input_padding_v')}px {_s('input_padding_h')}px;
    min-height: {_s('input_min_h')}px;
    selection-background-color: {_c('primary')};
}}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus,
QDateTimeEdit:focus, QDateEdit:focus {{
    border: 1px solid {_c('primary')};
    background: {_c('card_focus')};
}}
QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled, QComboBox:disabled {{
    background: {_c('disabled_bg')};
    color: {_c('disabled_input_fg')};
}}
QComboBox::drop-down {{
    border: none;
    width: {_s('combo_dropdown_w')}px;
}}
QComboBox::down-arrow {{
    image: url({chevron_down});
    width: {_s('combo_arrow_size')}px;
    height: {_s('combo_arrow_size')}px;
    margin-right: {_s('combo_arrow_margin_r')}px;
}}
QComboBox::down-arrow:on {{
    image: url({chevron_up});
}}
QComboBox QAbstractItemView {{
    background: {_c('card')};
    border: 1px solid {_c('border')};
    border-radius: {_s('radius_input')}px;
    padding: 4px;
    selection-background-color: {_c('primary_light')};
    selection-color: {_c('text')};
    outline: none;
}}
QSpinBox::up-button, QDoubleSpinBox::up-button {{
    border: none;
    width: {_s('spin_btn_w')}px;
}}
QSpinBox::down-button, QDoubleSpinBox::down-button {{
    border: none;
    width: {_s('spin_btn_w')}px;
}}

/* ══════════ 勾选 / 单选 ══════════ */
QCheckBox, QRadioButton {{
    spacing: {_s('check_spacing')}px;
    background: transparent;
}}
QCheckBox::indicator, QRadioButton::indicator {{
    width: {_s('indicator_size')}px;
    height: {_s('indicator_size')}px;
}}
QCheckBox::indicator {{
    image: url({square_icon});
}}
QCheckBox::indicator:checked {{
    background: {_c('card')};
    image: url({check_icon});
}}
QRadioButton::indicator {{
    image: url({square_rounded_icon});
}}
QRadioButton::indicator:checked {{
    background: {_c('card')};
    image: url({radio_icon});
}}

/* ══════════ 滑块（全局缩放等）══════════ */
QSlider::groove:horizontal {{
    height: 4px;
    background: {_c('hover')};
    border: 1px solid {_c('border')};
    border-radius: 2px;
}}
QSlider::sub-page:horizontal {{
    background: {_c('primary')};
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    width: 14px;
    height: 14px;
    margin: -6px 0;
    background: {_c('card')};
    border: 1px solid {_c('primary')};
    border-radius: 7px;
}}
QSlider::handle:horizontal:hover {{
    background: {_c('primary_light')};
}}
QSlider::handle:horizontal:pressed {{
    background: {_c('primary')};
}}

/* ══════════ 折叠面板 ══════════ */
QToolButton#sectionHeader {{
    background: {_c('section_header')};
    border: 1px solid {_c('border')};
    border-radius: {_s('radius_section')}px;
    padding: {_s('section_padding_v')}px {_s('section_padding_h')}px;
    font-size: {_f('section_header')}px;
    font-weight: {_f('section_header_weight')};
    color: {_c('text')};
    text-align: left;
}}
QToolButton#sectionHeader:hover {{
    background: {_c('hover_deep')};
}}
QToolButton#sectionHeader::menu-indicator {{
    image: none;
}}

/* ══════════ 日志区 ══════════ */
QTextEdit#log {{
    background-color: {_c('log_bg')};
    color: {_c('log_fg')};
    font-family: {monofam};
    font-size: {_f('log')}px;
    border: none;
    border-radius: {_s('radius_log')}px;
    padding: {_s('log_padding')}px;
    selection-background-color: {_c('primary')};
}}

/* ══════════ 滚动区域 / 滚动条 ══════════ */
QScrollArea {{
    background: transparent;
    border: none;
}}
QScrollArea > QWidget > QWidget {{
    background: transparent;
}}
QScrollBar:vertical {{
    background: transparent;
    width: {_s('scroll_w')}px;
    margin: {_s('scroll_margin')}px;
}}
QScrollBar::handle:vertical {{
    background: {_c('scroll_handle')};
    border-radius: {_s('scroll_handle_radius')}px;
    min-height: {_s('scroll_handle_min')}px;
}}
QScrollBar::handle:vertical:hover {{
    background: {_c('scroll_handle_hover')};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: {_s('scroll_h')}px;
    margin: {_s('scroll_margin')}px;
}}
QScrollBar::handle:horizontal {{
    background: {_c('scroll_handle')};
    border-radius: {_s('scroll_handle_radius')}px;
    min-width: {_s('scroll_handle_min')}px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {_c('scroll_handle_hover')};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* ══════════ 消息框 ══════════ */
QMessageBox {{
    background: {_c('card')};
}}
QMessageBox QLabel {{
    font-size: {_f('msgbox')}px;
    color: {_c('text')};
}}

/* ══════════ 格式二级选择器 ══════════ */
QPushButton#catBtn {{
    background: transparent;
    border: none;
    border-radius: {_s('radius_cat')}px;
    padding: 0px {_s('cat_padding_h')}px;
    min-height: {_s('btn_h')}px;
    color: {_c('text_light')};
    font-weight: {_f('btn_weight')};
}}
QPushButton#catBtn:hover {{
    background: {_c('hover')};
    color: {_c('text')};
}}
QPushButton#catBtn:checked {{
    background: {_c('primary_light')};
    color: {_c('primary_dark')};
    font-weight: {_f('checked_weight')};
}}
QPushButton#catBtn:disabled {{
    color: {_c('cat_disabled')};
}}

QPushButton#chip {{
    background: {_c('card')};
    border: {_s('border_w')}px solid {_c('border')};
    border-radius: {_s('radius_chip')}px;
    padding: 0px {_s('chip_padding_h')}px;
    min-height: {_s('btn_h') - 2 * _s('border_w')}px;
    color: {_c('chip_text')};
}}
QPushButton#chip:hover {{
    border-color: {_c('primary')};
    color: {_c('primary_dark')};
    background: {_c('primary_light')};
}}
QPushButton#chip:checked {{
    background: {_c('primary_light')};
    border-color: {_c('primary')};
    color: {_c('primary_dark')};
    font-weight: {_f('checked_weight')};
}}
QPushButton#chip:disabled {{
    background: {_c('chip_disabled_bg')};
    color: {_c('chip_disabled_fg')};
    border-color: {_c('disabled_border')};
}}
QLabel#pickerHint {{
    color: {_c('text_light')};
    font-size: {_f('picker_hint')}px;
    padding: {_s('chip_picker_padding_v')}px {_s('chip_picker_padding_h')}px;
}}

/* ══════════ MD→DOCX 排版卡片 ══════════ */
QFrame#docxFormatCard {{
    background: {_c('card')};
    border: {_s('border_w')}px solid {_c('border')};
    border-radius: {_s('radius_card')}px;
}}
QFrame#dxfHeader {{
    background: {_c('subtle_bg')};
    border-top-left-radius: {_s('radius_card')}px;
    border-top-right-radius: {_s('radius_card')}px;
}}
QLabel#dxfTitle {{
    color: {_c('text')};
    font-weight: {_f('card_title_weight')};
    font-size: {_f('card_title')}px;
}}
QLineEdit#dxfPresetEdit {{
    background: {_c('card')};
    border: {_s('border_w')}px solid {_c('border')};
    border-radius: {_s('radius_dxf')}px;
    padding: {_s('dxf_preset_padding_v')}px {_s('dxf_preset_padding_h')}px;
    font-size: {_f('dxf')}px;
    color: {_c('text')};
}}
QLineEdit#dxfPresetEdit:focus {{
    border-color: {_c('primary')};
    background: {_c('card_focus')};
}}
QToolButton#dxfToggleBtn {{
    background: {_c('primary')};
    color: {_c('white')};
    border: none;
    border-radius: {_s('radius_dxf_btn')}px;
    padding: {_s('dxf_btn_padding_v')}px {_s('dxf_btn_padding_h')}px;
    font-size: {_f('dxf')}px;
    font-weight: {_f('dxf_weight')};
}}
QToolButton#dxfToggleBtn:hover {{
    background: {_c('primary_dark')};
}}
QToolButton#dxfToggleBtn:checked {{
    background: {_c('primary_dark')};
}}
QFrame#dxfSeparator {{
    color: {_c('border')};
    max-height: 1px;
    margin: 0;
}}
QFrame#dxfBtnBar {{
    background: {_c('subtle_bg')};
    border-top: 1px solid {_c('border')};
    border-bottom-left-radius: {_s('radius_card')}px;
    border-bottom-right-radius: {_s('radius_card')}px;
}}

/* ══════════ 区块标题（set_format 内的 section_label / 标题样式标签） ══════════ */
QLabel#sectionTitle {{
    color: {_c('title_fg')};
    font-weight: 700;
}}

/* ══════════ 插件加载状态徽章（tab_plugin） ══════════ */
QLabel#badge[ok="1"] {{
    color: {_c('white')};
    background: {_c('success')};
    border-radius: {_s('radius_btn')}px;
    padding: {_s('badge_padding_v')}px {_s('badge_padding_h')}px;
}}
QLabel#badge[ok="0"] {{
    color: {_c('white')};
    background: {_c('danger')};
    border-radius: {_s('radius_btn')}px;
    padding: {_s('badge_padding_v')}px {_s('badge_padding_h')}px;
}}
QLabel#badge[ok="2"] {{
    color: {_c('white')};
    background: {_c('text_light')};
    border-radius: {_s('radius_btn')}px;
    padding: {_s('badge_padding_v')}px {_s('badge_padding_h')}px;
}}

/* 插件 UI 加载模式徽章（plugin_ext / tab_plugin）：direct 灰 / desc 蓝 / window 紫 */
QLabel#badge[mode="direct"] {{
    color: {_c('white')};
    background: {_c('text_light')};
    border-radius: {_s('radius_btn')}px;
    padding: {_s('badge_padding_v')}px {_s('badge_padding_h')}px;
}}
QLabel#badge[mode="desc"] {{
    color: {_c('white')};
    background: {_c('card_icon_blue')};
    border-radius: {_s('radius_btn')}px;
    padding: {_s('badge_padding_v')}px {_s('badge_padding_h')}px;
}}
QLabel#badge[mode="window"] {{
    color: {_c('white')};
    background: {_c('purple')};
    border-radius: {_s('radius_btn')}px;
    padding: {_s('badge_padding_v')}px {_s('badge_padding_h')}px;
}}


/* ══════════ 轻提示 toast（ui/toast.py） ══════════ */
QLabel#toast_success {{
    background: {_c('toast_success')};
    color: {_c('toast_text')};
    border-radius: {_s('radius_toast')}px;
    padding: {_s('toast_padding_v')}px {_s('toast_padding_h')}px;
    font-size: {_f('toast_font')}px;
    font-weight: 600;
}}
QLabel#toast_info {{
    background: {_c('toast_info')};
    color: {_c('toast_text')};
    border-radius: {_s('radius_toast')}px;
    padding: {_s('toast_padding_v')}px {_s('toast_padding_h')}px;
    font-size: {_f('toast_font')}px;
    font-weight: 600;
}}
QLabel#toast_warning {{
    background: {_c('toast_warning')};
    color: {_c('toast_text')};
    border-radius: {_s('radius_toast')}px;
    padding: {_s('toast_padding_v')}px {_s('toast_padding_h')}px;
    font-size: {_f('toast_font')}px;
    font-weight: 600;
}}

"""


APP_STYLESHEET = _qss()


def _sync_style_file() -> str:
    """把 QSS 同步写入 ui/styles/style.qss（静态样式文件，便于统一维护与查看）。

    返回样式文件路径；写入失败返回 ""（不影响运行）。
    """
    try:
        import os
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "styles", "style.qss")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(APP_STYLESHEET)
        return path
    except Exception:
        return ""


STYLE_FILE = _sync_style_file()

#  主题切换（全局 UI 风格）

from PySide6.QtCore import QObject, Signal  # noqa: E402


class _ThemeBus(QObject):
    """主题切换广播：所有监听方（如主窗口重建页面）连接 changed 即可。"""

    changed = Signal(str)   # 参数：当前主题名


THEME_BUS = _ThemeBus()


def rebuild_stylesheet() -> str:
    """按当前 CONFIG（主题/覆盖/缩放）重建全局 QSS 并同步静态文件。"""
    global APP_STYLESHEET
    APP_STYLESHEET = _qss()
    _sync_style_file()
    return APP_STYLESHEET


def apply_theme(app, settings: dict = None, notify: bool = True) -> str:
    """应用保存的全局 UI 风格。

    流程：加载设置 → 重建 QSS → app.setStyleSheet → 广播主题变化。
    返回新样式表字符串。notify=False 时不广播（启动期使用，避免页面提前重建）。
    """
    if settings:
        C.apply_theme_settings(settings)
    if app.style().objectName() != "fusion":
        app.setStyle("Fusion")
    rebuild_stylesheet()
    app.setStyleSheet(APP_STYLESHEET)
    if notify:
        THEME_BUS.changed.emit(C.theme())
    return APP_STYLESHEET


def current_theme() -> str:
    """当前生效主题名（light/dark…）。"""
    return C.theme()


def theme_names() -> dict:
    """{主题key: 显示名} 映射，供设置页下拉与开关使用。"""
    return C.theme_names()