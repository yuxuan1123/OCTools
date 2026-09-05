"""
OCTools/ui/tabs/plugins/tree/card_output.py
───────────────────────────────────────────────
目录树 tab 的「生成 + 输出」卡片。

包含：
  - 生成按钮（主色，点击后按选项构建目录树）；
  - 目录树文本显示区（等宽字体、只读、可选中复制）；
  - 生成统计行（共 N 行，含失败/跳过提示）。

所有视觉/布局参数统从 config/ui_config.json 读取（CONFIG 单例）。
"""

from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QHBoxLayout, \
    QLabel, QPushButton, QPlainTextEdit
from PySide6.QtGui import QTextOption

from config.ui_config import CONFIG as C

# 插件模式下被平铺复制到插件目录，MVP 独立运行时为 tree 子包，相对导入均可用。
from .card_options import (
    card_style, title_style, label_style, primary_btn_style,
)


def build_output_card(parent: QWidget, page) -> QFrame:
    """构建生成 + 输出卡片，控件引用挂到 page 上。"""
    card = QFrame(parent)
    card.setObjectName("SettingsSection")
    card.setStyleSheet(card_style())
    lay = QVBoxLayout(card)
    lay.setContentsMargins(
        C.size("group_padding_h"), C.size("group_padding_v"),
        C.size("group_padding_h"), C.size("group_padding_v"),
    )
    lay.setSpacing(C.size("form_row_spacing"))

    # 标题行：标题 + 生成按钮
    head = QHBoxLayout()
    head.setSpacing(C.size("form_row_spacing"))
    title = QLabel("目录树")
    title.setStyleSheet(title_style())
    head.addWidget(title)
    head.addStretch(1)

    page.generate_btn = QPushButton("生成目录树", card)
    page.generate_btn.setStyleSheet(primary_btn_style())
    page.generate_btn.clicked.connect(lambda _=False: page._generate())
    head.addWidget(page.generate_btn)
    lay.addLayout(head)

    # 生成统计行
    page.stat_label = QLabel("尚未生成。", card)
    page.stat_label.setStyleSheet(label_style())
    lay.addWidget(page.stat_label)

    # 树文本显示区（等宽字体）
    page.tree_text = QPlainTextEdit(card)
    page.tree_text.setReadOnly(True)
    page.tree_text.setWordWrapMode(QTextOption.NoWrap)
    page.tree_text.setMinimumHeight(C.size("txn_log_min_h"))
    mono_family = C.raw("fonts", "family_log") or "Consolas"
    page.tree_text.setStyleSheet(
        f"QPlainTextEdit {{ background: {C.color('card')};"
        f" border: 1px solid {C.color('input_border')};"
        f" border-radius: {C.size('radius_card')}px;"
        f" color: {C.color('nav_text')};"
        f" font-family: {mono_family};"
        f" font-size: {C.font('log')}px; }}"
    )
    lay.addWidget(page.tree_text, 1)

    return card