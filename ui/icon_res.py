"""
OCTools/ui/icon_res.py
───────────────────────────────────────────────
SVG 图标资源 + 着色工具（全局图标化）。

设计要点：
  - assets/using 下的 SVG 线性图标统一加载（所有图标先复制到 using 再引用）
  - 图标目录 / 尺寸 / 默认颜色 / 图标名映射 全部来自 ui/ui_config.json
  - colored_icon / colored_pixmap 用 QSvgRenderer 渲染后以
    CompositionMode_SourceIn 重新着色 → 同一图标可染任意颜色
    （导航选中白、未选中灰、卡片标题主色），不依赖 -selected 变体文件
  - 文件缺失 / 加载失败一律回退空图标，绝不抛异常、绝不影响功能
"""

import os

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

from config.ui_config import CONFIG as C
from ui.theme import THEME

# 资源根目录
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_DIR = C.icon_dir()          # assets/icons（logo 原图）
USING_DIR = C.using_dir()        # assets/using（在用图标统一源）
MEDIA_DIR = C.media_dir()        # assets/media

# 全局字号 / 图标尺寸（由 JSON 配置）
NAV_ICON_SIZE = C.size("icon_nav")
CARD_ICON_SIZE = C.size("icon_card")


def _svg_path(name: str) -> str:
    """按名称解析到 assets/using 下的 svg 文件路径（允许省略扩展名）"""
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
    """加载 SVG 图标并着色，返回 QPixmap（失败返回透明空图，绝不抛异常）

    media=True 时从 assets/media 目录读取（media 文件名为 hash 风格）。
    size 缺省时使用 JSON 中的卡片图标尺寸 icon_card。
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
    """着色图标 → QIcon（供 QPushButton.setIcon 使用）"""
    return QIcon(colored_pixmap(name, color, size, media))


def tray_pixmap(color=None, size: int = None) -> QPixmap:
    """「放到托盘」图标：arrow-bar-down（向下收起进托盘）着色"""
    color = color or C.color("icon_default")
    if size is None:
        size = NAV_ICON_SIZE
    return colored_pixmap(C.icon("tray"), color, size)


def tray_icon(color=C.color("icon_default"), size: int = None) -> QIcon:
    """「放到托盘」按钮图标 → QIcon"""
    return QIcon(tray_pixmap(color, size))


# ── 语义化图标映射（统一来源 assets/using，outline 优先）──────
NAV_ICON_NAMES = {
    "转换":   C.icon("nav_convert"),    # file（outline 文档）
    "合并":   C.icon("nav_merge"),      # stack（outline 堆叠）
    "翻译":   C.icon("nav_translate"),  # message（outline 气泡）
    "目录树":   C.icon("nav_tree"),       # binary-tree
    "样式实验室": C.icon("nav_style_lab"), # flask-circle
    "插件":   C.icon("nav_plugin"),     # layout-grid-add
    "设置":   C.icon("nav_settings"),   # settings（using 副本）
}

# 卡片标题（主色）
CARD_ICON_NAMES = {
    "input":     C.icon("card_input"),     # cloud 输入
    "target":    C.icon("card_target"),    # flag-2 目标格式
    "output":    C.icon("card_output"),    # box 输出
    "log":       C.icon("card_log"),       # terminal 日志
    "translate": C.icon("card_translate"), # globe 翻译方向
    "source":    C.icon("card_source"),    # message 原文
    "result":    C.icon("card_result"),    # check 译文
    "ocr":       C.icon("card_ocr"),       # bolt 单词翻译
    "live":      C.icon("card_live"),      # bulb 屏幕实时翻译
    "audio":     C.icon("card_audio"),     # music 语音翻译
}

# 导航按钮是否来自 media 目录（现在统一走 using，置为 False）
_NAV_MEDIA = {}

# 常用配色（由 JSON 配置）
GRAY = C.color("icon_default")
GRAY_LIGHT = C.color("text_light")
WHITE = C.color("white")


def nav_icon(name: str, active: bool) -> QIcon:
    """导航项图标：选中用激活前景色（与选中文字同色，深浅主题均可见）/ 未选中用默认灰。

    注意：选中态背景是浅色（nav_active_bg），不能用白色——白图标落近白底会看不见。
    选中图标色必须与 #navBtn:checked 的文字色 nav_active_fg 一致。
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
    """应用品牌 logo（resources/icons/logo128.png，PNG 不参与 SVG 染色）。"""
    if size is None:
        size = NAV_ICON_SIZE
    pm = QPixmap(os.path.join(ICON_DIR, C.icon("app_logo")))
    if pm.isNull():
        return pm
    return pm.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)