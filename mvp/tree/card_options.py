"""
OCTools/mvp/tree/card_options.py
───────────────────────────────────────────────
目录树 tab 的「根目录 + 选项」卡片。

包含：
  - 根目录：只读输入框 + 浏览按钮（必选，不存在/非目录会在生成时报错）；
  - 隐藏项：是否显示以 '.' 开头的隐藏项（默认不显示）；
  - 文件过滤：显示所有文件 / 仅显示目录 / 隐藏图片文件；
  - 最大递归深度：0 = 不限；
  - 排除扩展名：逗号分隔（如 .log,.tmp），仅对文件生效；
  - 排除关键词：逗号分隔（如 __pycache__），文件与目录均生效。

所有视觉/布局参数统从 config/ui_config.json 读取（CONFIG 单例）。
"""

from ui.ui_component.combo_component import Combo
from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QSpinBox, QFileDialog,
)

from config.ui_config import CONFIG as C

# ─────────────────────────────────────────
#  通用样式（供本子包卡片共用）
# ─────────────────────────────────────────

FILTER_OPTIONS = [
    "显示所有文件（默认）",
    "仅显示目录",
    "隐藏图片文件",
]


def card_style() -> str:
    return (
        f"QFrame#SettingsSection {{ background: {C.color('card')};"
        f" border: 1px solid {C.color('border')};"
        f" border-radius: {C.size('radius_card')}px; }}"
    )


def title_style() -> str:
    return (
        f"color: {C.color('text')}; font-size: {C.font('group_header')}px;"
        f" font-weight: {C.font('group_header_weight')};"
    )


def label_style() -> str:
    return f"color: {C.color('text_light')}; font-size: {C.font('body')}px;"


def input_style() -> str:
    return (
        f"QLineEdit {{ background: {C.color('card')};"
        f" border: 1px solid {C.color('input_border')};"
        f" border-radius: {C.size('radius_btn')}px;"
        f" padding: {C.size('input_padding_v')}px {C.size('input_padding_h')}px;"
        f" color: {C.color('text')}; }}"
        f" QLineEdit:focus {{ border-color: {C.color('primary')}; }}"
    )


def btn_style() -> str:
    return (
        f"QPushButton {{ background: {C.color('primary_btn_bg')};"
        f" color: {C.color('primary')}; border: none;"
        f" border-radius: {C.size('radius_btn')}px;"
        f" padding: {C.size('btn_padding_v')}px {C.size('btn_padding_h')}px; }}"
        f" QPushButton:hover {{ background: {C.color('primary_btn_hover')}; }}"
        f" QPushButton:pressed {{ background: {C.color('primary_btn_pressed')}; }}"
    )


def primary_btn_style() -> str:
    return (
        f"QPushButton {{ background: {C.color('primary')};"
        f" color: {C.color('white')}; border: none;"
        f" border-radius: {C.size('radius_btn')}px;"
        f" padding: {C.size('btn_padding_v')}px {C.size('btn_padding_h')}px;"
        f" font-weight: {C.font('btn_weight')}; }}"
        f" QPushButton:hover {{ background: {C.color('primary_dark')}; }}"
    )


# ─────────────────────────────────────────
#  卡片
# ─────────────────────────────────────────


def build_options_card(parent: QWidget, page) -> QFrame:
    """构建根目录 + 选项卡片，控件引用挂到 page 上。"""
    card = QFrame(parent)
    card.setObjectName("SettingsSection")
    card.setStyleSheet(card_style())
    lay = QVBoxLayout(card)
    lay.setContentsMargins(
        C.size("group_padding_h"), C.size("group_padding_v"),
        C.size("group_padding_h"), C.size("group_padding_v"),
    )
    lay.setSpacing(C.size("form_row_spacing"))

    # 标题
    title = QLabel("目录树选项")
    title.setStyleSheet(title_style())
    lay.addWidget(title)

    # ── 根目录（必选）──
    root_label = QLabel("根目录")
    root_label.setFixedWidth(C.size("form_width_90"))
    root_label.setStyleSheet(label_style())

    page.root_entry = QLineEdit(card)
    page.root_entry.setReadOnly(True)
    page.root_entry.setPlaceholderText("选择将生成目录树的根目录（必选）")
    page.root_entry.setStyleSheet(input_style())

    browse_btn = QPushButton("浏览…", card)
    browse_btn.setStyleSheet(btn_style())
    browse_btn.clicked.connect(lambda _=False: page._browse_root())

    root_row = QHBoxLayout()
    root_row.setSpacing(C.size("form_row_spacing"))
    root_row.addWidget(root_label)
    root_row.addWidget(page.root_entry, 1)
    root_row.addWidget(browse_btn)
    lay.addLayout(root_row)

    # ── 隐藏项 ──
    page.show_hidden_check = QCheckBox("显示隐藏项（名称以 . 开头的文件夹/文件）", card)
    page.show_hidden_check.setStyleSheet(f"color: {C.color('text')};")
    lay.addWidget(page.show_hidden_check)

    # ── 文件过滤模式 ──
    filter_label = QLabel("文件过滤")
    filter_label.setFixedWidth(C.size("form_width_90"))
    filter_label.setStyleSheet(label_style())

    page.filter_combo = Combo(card)
    page.filter_combo.addItems(FILTER_OPTIONS)
    page.filter_combo.setCurrentIndex(0)
    page.filter_combo.setMinimumWidth(C.size("combo_min_w_large"))

    filter_row = QHBoxLayout()
    filter_row.setSpacing(C.size("form_row_spacing"))
    filter_row.addWidget(filter_label)
    filter_row.addWidget(page.filter_combo)
    filter_row.addStretch(1)
    lay.addLayout(filter_row)

    # ── 最大递归深度 ──
    depth_label = QLabel("最大深度")
    depth_label.setFixedWidth(C.size("form_width_90"))
    depth_label.setStyleSheet(label_style())

    page.max_depth_spin = QSpinBox(card)
    page.max_depth_spin.setRange(0, 99)
    page.max_depth_spin.setValue(0)
    page.max_depth_spin.setToolTip("0 表示不限深度；1 表示仅显示直接子项")

    depth_hint = QLabel("（0 = 不限）")
    depth_hint.setStyleSheet(label_style())

    depth_row = QHBoxLayout()
    depth_row.setSpacing(C.size("form_row_spacing"))
    depth_row.addWidget(depth_label)
    depth_row.addWidget(page.max_depth_spin)
    depth_row.addWidget(depth_hint)
    depth_row.addStretch(1)
    lay.addLayout(depth_row)

    # ── 排除扩展名 ──
    ext_label = QLabel("排除扩展名")
    ext_label.setFixedWidth(C.size("form_width_90"))
    ext_label.setStyleSheet(label_style())

    page.exclude_ext_entry = QLineEdit(card)
    page.exclude_ext_entry.setPlaceholderText("示例：.log,.tmp,md（逗号分隔，自动补点，仅对文件生效）")
    page.exclude_ext_entry.setStyleSheet(input_style())

    ext_row = QHBoxLayout()
    ext_row.setSpacing(C.size("form_row_spacing"))
    ext_row.addWidget(ext_label)
    ext_row.addWidget(page.exclude_ext_entry, 1)
    lay.addLayout(ext_row)

    # ── 排除关键词 ──
    kw_label = QLabel("排除关键词")
    kw_label.setFixedWidth(C.size("form_width_90"))
    kw_label.setStyleSheet(label_style())

    page.exclude_kw_entry = QLineEdit(card)
    page.exclude_kw_entry.setPlaceholderText("示例：__pycache__,node_modules（逗号分隔，名称包含即排除，文件与目录均生效）")
    page.exclude_kw_entry.setStyleSheet(input_style())

    kw_row = QHBoxLayout()
    kw_row.setSpacing(C.size("form_row_spacing"))
    kw_row.addWidget(kw_label)
    kw_row.addWidget(page.exclude_kw_entry, 1)
    lay.addLayout(kw_row)

    return card