"""
OCTools/ui/icon_res.py
───────────────────────
SVG 图标资源 + 着色工具（全局图标化）。

设计要点：
  - 所有图标统一从 using/plugin_ui 加载
  - 图标目录/尺寸/默认颜色/名称映射来自 ui/ui_config.json
  - colored_icon/colored_pixmap 使用 QSvgRenderer 渲染后以 SourceIn 着色
  - 失败时返回空图标，不抛异常
"""

import os

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

from config.ui_config import CONFIG as C
from ui.theme import THEME

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_DIR = C.icon_dir()          # assets/icons（logo 原图）
USING_DIR = C.using_dir()        # assets/using（在用图标统一源）
MEDIA_DIR = C.media_dir()        # assets/media

NAV_ICON_SIZE = C.size("icon_nav")
CARD_ICON_SIZE = C.size("icon_card")


def _svg_path(name: str) -> str:
    """返回 assets/using 下 svg 文件路径（自动补 .svg）"""
    base = name if name.endswith(".svg") else name + ".svg"
    return os.path.join(USING_DIR, base)


def _renderer(path: str):
    try:
        r = QSvgRenderer(path)
        return r if r.isValid() else None
    except Exception:
        return None


def colored_pixmap(name: str, color=C.color("icon_default"), size: int = None,
                   media: bool = False) -> QPixmap:
    """加载 SVG 并着色为 QPixmap；失败返回透明空图。

    media=True 时从 assets/media 读取。size 缺省使用 icon_card。
    """
    color = color or GRAY
    if size is None:
        size = CARD_ICON_SIZE
    path = os.path.join(MEDIA_DIR, name) if media else _svg_path(name)
    r = _renderer(path)
    if r is None:
        return QPixmap()
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    try:
        r.render(p, QRectF(0, 0, size, size))
        p.setCompositionMode(QPainter.CompositionMode_SourceIn)
        p.fillRect(pix.rect(), QColor(color))
    finally:
        p.end()
    return pix


def colored_icon(name: str, color=C.color("icon_default"), size: int = None,
                 media: bool = False) -> QIcon:
    """着色图标 → QIcon（供 setIcon 使用）"""
    return QIcon(colored_pixmap(name, color, size, media))


def tray_pixmap(color=None, size: int = None) -> QPixmap:
    """「放到托盘」图标（arrow-bar-down）着色"""
    color = color or C.color("icon_default")
    if size is None:
        size = NAV_ICON_SIZE
    return colored_pixmap(C.icon("tray"), color, size)


def tray_icon(color=C.color("icon_default"), size: int = None) -> QIcon:
    """「放到托盘」按钮图标 → QIcon"""
    return QIcon(tray_pixmap(color, size))


# ── 语义化图标映射（来源 assets/using，outline 优先）──────
NAV_ICON_NAMES = {
    "转换":   C.icon("nav_convert"),
    "合并":   C.icon("nav_merge"),
    "翻译":   C.icon("nav_translate"),
    "目录树":   C.icon("nav_tree"),
    "样式实验室": C.icon("nav_style_lab"),
    "插件":   C.icon("nav_plugin"),
    "设置":   C.icon("nav_settings"),
}

CARD_ICON_NAMES = {
    "input":     C.icon("card_input"),
    "target":    C.icon("card_target"),
    "output":    C.icon("card_output"),
    "log":       C.icon("card_log"),
    "translate": C.icon("card_translate"),
    "source":    C.icon("card_source"),
    "result":    C.icon("card_result"),
    "ocr":       C.icon("card_ocr"),
    "live":      C.icon("card_live"),
    "audio":     C.icon("card_audio"),
}

_NAV_MEDIA = {}

GRAY = C.color("icon_default")
GRAY_LIGHT = C.color("text_light")
WHITE = C.color("white")


def nav_icon(name: str, active: bool) -> QIcon:
    """导航项图标：选中用 nav_active_fg 色，未选中用 icon_default。

    选中态背景为浅色，故图标色须与文字色 nav_active_fg 一致。
    """
    color = C.color("nav_active_fg") if active else C.color("icon_default")
    svg = NAV_ICON_NAMES.get(name, "office")
    return colored_icon(svg, color, NAV_ICON_SIZE,
                        media=_NAV_MEDIA.get(name, False))


def card_icon(name: str, color: str = None) -> QPixmap:
    """卡片标题图标（默认主色）"""
    svg = CARD_ICON_NAMES.get(name, "box")
    return colored_pixmap(svg, color or THEME["primary"], CARD_ICON_SIZE)


def brand_pixmap(size: int = None) -> QPixmap:
    """应用品牌 logo（PNG，不参与染色）"""
    if size is None:
        size = NAV_ICON_SIZE
    pm = QPixmap(os.path.join(ICON_DIR, C.icon("app_logo")))
    if pm.isNull():
        return pm
    return pm.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)