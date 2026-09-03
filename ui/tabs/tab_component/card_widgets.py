"""
OCTools/ui/tabs/tab_component/card_widgets.py
────────────────────────────────────────────────────
通用卡片构建小工具：
  - make_card(parent)       创建一张标准卡片（QFrame#card + QVBoxLayout）
  - make_title_row(...)     图标 + 标题行（含可选右侧提示）
  - make_icon_label(...)    表单行带小图标的标签（<图标> 文字）

用法与原文 _build_ui 保持一致（icon_res.card_icon / C.size("card_header_icon") 等）。
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget

from ui import icon_res
from config.ui_config import CONFIG as C


def make_card(parent):
    """创建一张标准卡片（QFrame#card + QVBoxLayout），返回 (card, layout)。

    布局间距与原文卡片一致：垂直/水平内边距 card_padding_v/h，控件间距 header_row_spacing。
    """
    card = QFrame(parent)
    card.setObjectName("card")
    layout = QVBoxLayout(card)
    layout.setContentsMargins(
        C.size("card_padding_h"), C.size("card_padding_v"),
        C.size("card_padding_h"), C.size("card_padding_v"))
    layout.setSpacing(C.size("header_row_spacing"))
    return card, layout


def make_title_row(card, icon_key, title, layout, hint=None):
    """卡片标题行：图标 + 标题（cardTitle）+ 可选提示文本，右侧撑开。

    hint 传给 QLabel 并设 objectName="hint"（与原文语音卡片右侧提示一致）。
    """
    row = QWidget(card)
    t_lay = QHBoxLayout(row)
    t_lay.setContentsMargins(0, 0, 0, 0)
    t_lay.setSpacing(C.size("header_row_spacing"))
    icon = QLabel(row)
    icon.setPixmap(icon_res.card_icon(icon_key))
    icon.setFixedSize(C.size("card_header_icon"), C.size("card_header_icon"))
    t_lay.addWidget(icon)
    title_lab = QLabel(title, row)
    title_lab.setObjectName("cardTitle")
    t_lay.addWidget(title_lab)
    if hint:
        h = QLabel(hint, row)
        h.setObjectName("hint")
        t_lay.addWidget(h)
    t_lay.addStretch(1)
    layout.addWidget(row)


def make_icon_label(text: str, icon: str, parent: QWidget):
    """表单行带小图标的标签：<图标> 文字（图标取 outline 线性着色）。

    用于卡片内表单字段前的行标签（如「源文件」「输出文件夹」等）。
    """
    w = QWidget(parent)
    lay = QHBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(C.size("icon_label_spacing"))
    ic = QLabel(w)
    ic.setPixmap(icon_res.colored_pixmap(icon, C.color("icon_default"), C.size("icon_medium")))
    ic.setFixedSize(C.size("icon_medium"), C.size("icon_medium"))
    lay.addWidget(ic)
    lab = QLabel(text, w)
    lay.addWidget(lab)
    lay.addStretch(1)
    return w