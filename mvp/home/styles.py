"""样式工厂：所有 QSS 字符串集中在此，UI 模块只负责布局与交互。

依赖 config.ui_config 的 CONFIG（C）读取统一的尺寸 / 字体令牌。
"""

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect

from config.ui_config import CONFIG as C

from home.constants import (
    INK, GRAPHITE, MUTED, FAINT, BORDER, BORDER_HV, SOFT_BG, CARD_BG,
    PAGE_A, PAGE_B,
)


# ──────────────────────────────────────
#  页面
# ──────────────────────────────────────
def page_qss(obj: str = "TabHome") -> str:
    """首页背景渐变。"""
    return (
        f"QWidget#{obj} {{"
        f" background: qlineargradient(x1:0, y1:0, x2:1, y2:1,"
        f" stop:0 {PAGE_A}, stop:1 {PAGE_B});"
        f"}}"
    )


def scroll_qss() -> str:
    """滚动区：透明无边框。"""
    return "QScrollArea { background: transparent; border: none; }"


# ──────────────────────────────────────
#  卡片 / 标题
# ──────────────────────────────────────
def card_qss(obj: str) -> str:
    """通用白卡（hover 描边加深）。"""
    rad = C.size("radius_card") or 20
    return (
        f"QFrame#{obj} {{"
        f" background: {CARD_BG};"
        f" border: 1px solid {BORDER};"
        f" border-radius: {rad}px;"
        f"}}"
        f"QFrame#{obj}:hover {{ border-color: {BORDER_HV}; }}"
    )


def hero_card_qss() -> str:
    """Hero：白 → 浅灰的斜向渐变。"""
    rad = C.size("radius_card") or 22
    return (
        "QFrame#Hero {"
        " background: qlineargradient(x1:0, y1:0, x2:1, y2:1,"
        " stop:0 #FFFFFF, stop:1 #F7F7F9);"
        f" border: 1px solid {BORDER};"
        f" border-radius: {rad}px;"
        "}"
    )


def card_title_style() -> str:
    return (
        f"color: {INK};"
        f" font-size: {C.font('card_title') or 15}px;"
        f" font-weight: {C.font('card_title_weight') or 700};"
        f" background: transparent;"
    )


def dot_style(color: str) -> str:
    """状态小圆点。"""
    return f"background: {color}; border-radius: 4px;"


def status_label_style(color: str) -> str:
    return f"color: {color}; font-size: 11px; font-weight: 700; background: transparent;"


def sub_text_style() -> str:
    return f"color: {MUTED}; font-size: 12px; background: transparent;"


def foot_text_style() -> str:
    return f"color: {FAINT}; font-size: 11px; background: transparent;"


# ──────────────────────────────────────
#  按钮 / 输入
# ──────────────────────────────────────
def primary_btn_qss() -> str:
    rad = C.size("radius_btn") or 12
    return (
        "QPushButton {"
        " color: #FFFFFF; font-size: 14px; font-weight: 700;"
        f" background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
        f" stop:0 {INK}, stop:1 {GRAPHITE});"
        f" border: none; border-radius: {rad}px; padding: 10px 16px;"
        " letter-spacing: 1px;"
        "}"
        f"QPushButton:hover {{ background: {GRAPHITE}; }}"
        f"QPushButton:pressed {{ background: {INK}; }}"
        f"QPushButton:disabled {{ color: {FAINT}; background: {SOFT_BG};"
        f" border: 1px solid {BORDER}; }}"
    )


def outline_btn_qss() -> str:
    rad = C.size("radius_btn") or 12
    return (
        "QPushButton {"
        f" color: {INK}; font-size: 14px; font-weight: 700;"
        f" background: #FFFFFF; border: 1.5px solid {INK};"
        f" border-radius: {rad}px; padding: 10px 16px; letter-spacing: 1px;"
        "}"
        f"QPushButton:hover {{ background: {INK}; color: #FFFFFF; }}"
        f"QPushButton:pressed {{ background: {GRAPHITE}; color: #FFFFFF; }}"
    )


def add_btn_qss() -> str:
    rad = C.size("radius_btn") or 12
    return (
        "QPushButton { color: #FFFFFF; font-size: 18px; font-weight: 700;"
        f" background: {INK}; border: none; border-radius: {rad}px; }}"
        f"QPushButton:hover {{ background: {GRAPHITE}; }}"
        "QPushButton:pressed { background: #000000; }"
    )


def input_qss() -> str:
    return (
        "QLineEdit {"
        " background: #FFFFFF;"
        f" border: 1px solid {BORDER};"
        f" border-radius: {C.size('radius_input') or 12}px;"
        f" padding: {C.size('input_padding_v') or 10}px "
        f"{C.size('input_padding_h') or 14}px;"
        f" color: {INK}; font-size: 13px;"
        "}"
        f"QLineEdit:focus {{ border-color: {INK}; }}"
    )


def del_btn_qss() -> str:
    return (
        f"QPushButton {{ color: {FAINT}; background: transparent;"
        f" border: none; border-radius: 13px; font-size: 12px;}}"
        f"QPushButton:hover {{ color: #EF4444; background: {SOFT_BG};}}"
    )


def count_chip_qss() -> str:
    return (
        f"color: {INK}; font-size: 11px; font-weight: 700;"
        f" background: {SOFT_BG}; border-radius: 8px; padding: 2px 8px;"
    )


# ──────────────────────────────────────
#  阴影
# ──────────────────────────────────────
def add_shadow(widget, color: QColor, blur: int = 18, dy: int = 4):
    """给控件挂一层柔和投影。"""
    eff = QGraphicsDropShadowEffect(widget)
    eff.setBlurRadius(blur)
    eff.setColor(color)
    eff.setOffset(0, dy)
    widget.setGraphicsEffect(eff)


def card_shadow(widget):
    """普通卡片阴影。"""
    add_shadow(widget, QColor(24, 24, 27, 16), blur=28, dy=8)


def hero_shadow(widget):
    """Hero 阴影（更散更远）。"""
    add_shadow(widget, QColor(24, 24, 27, 26), blur=40, dy=12)
