"""
octool/ui/tabs/tab_component/page_header.py
───────────────────────────────────────────────
通用页头部件：标题 + 副标题。

用于各标签页顶部，提供页面层级标识。
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

from config.ui_config import CONFIG as C


def build_page_header(parent, title_key: str, subtitle_key: str = None):
    """构建页头，返回 QWidget。

    Args:
        parent: 父控件
        title_key: 标题文案键（ui_config.json text 段）
        subtitle_key: 副标题文案键（可选）
    """
    header = QWidget(parent)
    lay = QVBoxLayout(header)
    lay.setContentsMargins(0, 0, 0, C.size("header_margin_bottom"))
    lay.setSpacing(4)

    title = QLabel(C.text(title_key) or title_key, header)
    title.setObjectName("pageTitle")
    lay.addWidget(title)

    if subtitle_key:
        sub = QLabel(C.text(subtitle_key) or subtitle_key, header)
        sub.setObjectName("pageSubtitle")
        sub.setWordWrap(True)
        lay.addWidget(sub)

    return header
