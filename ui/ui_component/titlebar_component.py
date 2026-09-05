"""
通用、JSON 驱动的 PySide6 自定义标题栏组件。

特性：
- 所有视觉/布局/符号/按钮均从 JSON 配置加载，改 JSON 不改代码即可换肤、换功能。
- 按钮个数动态化：JSON 的 buttons 数组决定渲染哪些按钮及其顺序。
- 每个按钮可独立开关（enabled）与自定义功能（action: "custom" + 注册回调）。
- 内置动作：tray / minimize / maximize / close；其余 action 视为自定义，需注册回调。
- 可作为独立无边框窗口运行，也可嵌入到其他 QWidget/QMainWindow 的布局中。
- 按钮位置可由外部配置决定：button_align = "right"（默认）| "left" | "split"
    - "right" : 所有按钮集中在标题栏右侧（默认，原行为）。
    - "left"  : 所有按钮集中在标题栏左侧（标题移到右侧）。
    - "split" : 通过按钮项里的 "align":"left"|"right" 分别指定，未指定的按 button_align 兜底（默认右）。

用法：
    from titlebar_component import CustomTitleBar, TitleBarWindow
    # 1) 独立窗口（自动无边框 + 托盘 + 拖拽）
    w = TitleBarWindow(config="my.json")
    w.set_content(QLabel("正文区"))
    w.show()
    # 2) 仅标题栏部件，嵌入别处
    bar = CustomTitleBar(config={"title": "...", "titlebar": {"button_align": "left"}, ...})
    bar.register_custom_action("myact", lambda: print("clicked"))
"""
from __future__ import annotations

import sys
import json
from typing import Callable, Optional

from PySide6.QtCore import Qt, QPoint, QSize, QRectF
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QHBoxLayout, QApplication,
    QSystemTrayIcon, QMenu, QMainWindow, QVBoxLayout,
)

from .button_component import load_icon_for_button, resource_path
from ui.style_hook import StyleHookMixin
from config.ui_config import CONFIG as C


# 标题栏图标统一染色（主题联动）。None = 不染色。
_TITLEBAR_ICON_TINT: Optional[str] = None


def set_titlebar_icon_tint(color: Optional[str]):
    """设置标题栏图标统一颜色（None 恢复原样）。主题切换时由框架调用。"""
    global _TITLEBAR_ICON_TINT
    _TITLEBAR_ICON_TINT = color


def _tinted_svg_pixmap(path: str, color: str, size: int) -> QPixmap:
    """用 QSvgRenderer 渲染 SVG 并统一染色，解决 currentColor → 黑色的问题。

    返回指定大小的 QPixmap（失败返回空 QPixmap）。
    """
    try:
        r = QSvgRenderer(path)
        if not r.isValid():
            return QPixmap()
    except Exception:
        return QPixmap()
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    r.render(p, QRectF(0, 0, size, size))
    p.setCompositionMode(QPainter.CompositionMode_SourceIn)
    p.fillRect(pix.rect(), QColor(color))
    p.end()
    return pix


def _tinted_svg_icon(path: str, color: str, size: int) -> QIcon:
    """染色 SVG → QIcon"""
    return QIcon(_tinted_svg_pixmap(path, color, size))


def load_titlebar_icon(btn: QPushButton, symbol: str, icon_size: int = 20,
                       tint: Optional[str] = None):
    """加载标题栏图标；tint 显式传入时优先，否则用全局统一色调，都不设则原样加载。

    图标路径为相对路径时先解析为绝对路径（QSvgRenderer 按工作目录解析相对路径，
    打包后工作目录不是项目根，必须绝对化）。
    symbol 为纯文本符号（如 mode 按钮的"双"/"译"）时不当作图标路径打开，
    直接回退文本显示，避免 QSvgRenderer 尝试打开 `项目根/<文本>` 触发 Qt 警告。
    """
    if not symbol:
        load_icon_for_button(btn, symbol, icon_size)
        return
    is_image = any(symbol.lower().endswith(ext)
                   for ext in (".svg", ".png", ".ico", ".jpg"))
    color = tint if tint is not None else _TITLEBAR_ICON_TINT
    if is_image and color:
        icon = _tinted_svg_icon(resource_path(symbol), color, icon_size)
        if not icon.isNull():
            btn.setIcon(icon)
            btn.setText("")
            btn.setIconSize(QSize(icon_size, icon_size))
            return
    load_icon_for_button(btn, symbol, icon_size=icon_size)


# --------------------------------------------------------------------------- #
#  配置加载 & 默认值
# --------------------------------------------------------------------------- #
def _default_config() -> dict:
    return {
        "window": {"title": "App", "width": 900, "height": 600,
                   "background": "#F3F5F9", "frameless": True},
        "titlebar": {
            "height": 40, "background": "#FBFCFE", "foreground": "#1F2430",
            "title_align": "left",
            "button_align": "right",
            "padding": [0, 10, 0, 10],
            "draggable": True,
        },
        "font": {"family": "Sans Serif", "size": 13, "title_size": 14, "button_size": 15},
        "icons": {
            "tray": "resources/icons/arrow-bar-down.svg",
            "minimize": "resources/icons/minimize.svg",
            "maximize": "resources/icons/maximize.svg",
            "restore": "resources/icons/restore.svg",
            "close": "resources/icons/x.svg",
        },
        "buttons": [
            {"id": "tray",     "action": "tray",     "tooltip": "托盘",   "enabled": True,  "danger": False},
            {"id": "minimize", "action": "minimize", "tooltip": "最小化", "enabled": True,  "danger": False},
            {"id": "maximize", "action": "maximize", "tooltip": "最大化", "enabled": True,  "danger": False},
            {"id": "close",    "action": "close",    "tooltip": "关闭",   "enabled": True,  "danger": True},
        ],
        "button_size": {"width": 40, "height": 34},
        "colors": {
            "button_normal": "transparent",
            "button_hover":  "#F1F4F9",
            "button_press":  "#D8DFEA",
            "close_hover":   "#FEE2E2",
            "close_press":   "#FECACA",
            "content_bg":    "#F3F5F9",
        },
        "tray": {"enabled": True, "tooltip": "应用已最小化到托盘",
                 "menu": [{"label": "显示窗口", "action": "show"},
                          {"label": "退出",     "action": "quit"}]},
    }


def load_config(config) -> dict:
    """接受 JSON 文件路径(str) 或 dict，返回合并后的配置(dict)。"""
    base = _default_config()
    if config is None:
        return base
    if isinstance(config, str):
        with open(config, "r", encoding="utf-8") as f:
            user = json.load(f)
    elif isinstance(config, dict):
        user = config
    else:
        raise TypeError("config 必须是 JSON 文件路径或 dict")
    _deep_merge(base, user)
    return base


def _deep_merge(base: dict, user: dict):
    for k, v in user.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v


# --------------------------------------------------------------------------- #
#  图标工具：把 JSON 里的符号文字渲染成 QIcon
# --------------------------------------------------------------------------- #
def _symbol_icon(symbol: str, fg: str = "#ffffff", size: int = 64) -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setPen(QColor(fg))
    f = QFont()
    f.setBold(True)
    f.setPointSize(int(size * 0.62))
    p.setFont(f)
    p.drawText(pix.rect(), Qt.AlignCenter, symbol)
    p.end()
    return QIcon(pix)


# --------------------------------------------------------------------------- #
#  自定义标题栏部件（可独立使用）
# --------------------------------------------------------------------------- #
class CustomTitleBar(StyleHookMixin, QWidget):
    """JSON 驱动的自定义标题栏。

    标题栏配色随主题变化，混入 StyleHookMixin 后由 QEvent.StyleChange 自动重刷。
    """
    
    BUILTIN_ACTIONS = {"tray", "minimize", "maximize", "close"}

    def __init__(self, config=None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.cfg = load_config(config)
        self._window = None          # 关联的顶级窗口（拖拽/最大化用）
        self._custom_actions: dict[str, Callable[[], None]] = {}
        self._maximized = False
        self._drag_pos: Optional[QPoint] = None
        self._tray_icon: Optional[QSystemTrayIcon] = None

        # 顶边缩放让位：标题栏顶部 top_resize_margin 像素内不启动拖动，
        # 改由 window 上的 WindowResizer 接管（让事件冒泡）。仅浮窗会注入
        # resizer 并配置该值；主窗口等默认 0 → 行为不变。
        self._top_resize_margin = int(self.cfg.get("titlebar", {})
                                      .get("top_resize_margin", 0))
        self._resizer = None            # 由 window 在创建缩放器后注入

        self.setObjectName("CustomTitleBar")
        self.setMouseTracking(True)  # 确保鼠标移动时能收到 mouseMoveEvent
        self._build_ui()
        self._apply_inline_style()
        self.setAutoFillBackground(True)
        self.setAttribute(Qt.WA_StyledBackground, True)

    # -------------------------- 公共 API -------------------------- #
    def attach_window(self, window: QWidget):
        self._window = window
        window.setWindowTitle(self.cfg["window"].get("title", ""))
        # setWindowFlags 会销毁并重建窗口句柄，所有图标/标题/tooltip 必须在
        # 这里之后设置。frameless 只在独立 TitleBarWindow 里用；
        # split_titlebar.TestWindow 已经在外部设置过 FramelessWindowHint，
        # 再次调用会导致 setWindowIcon 丢失（Windows 回退成 Python 自带图标）。
        if self.cfg["window"].get("frameless") and not (
            window.windowFlags() & Qt.FramelessWindowHint
        ):
            window.setWindowFlags(window.windowFlags() | Qt.FramelessWindowHint)
        # 统一设置窗口图标（任务栏 + 最小化到托盘时显示的图标 = 应用 logo）
        logo_cfg = self.cfg.get("logo", {})
        logo_path = logo_cfg.get("image") or self.cfg.get("icons", {}).get("tray_icon")
        if logo_path:
            fg = self.cfg.get("titlebar", {}).get("foreground", "#1F2430")
            if logo_path.lower().endswith(".svg"):
                icon = _tinted_svg_icon(logo_path, fg, 32)
            else:
                icon = QIcon(logo_path)
            if not icon.isNull():
                window.setWindowIcon(icon)
        if self.cfg["tray"].get("enabled"):
            self._init_tray(window)
        # 【新增】监听窗口状态变化
        if window.windowHandle():
            window.windowHandle().windowStateChanged.connect(self._on_window_state_changed)

    def _on_window_state_changed(self, old_state, new_state):
        """当窗口状态变化时，同步最大化按钮图标"""
        self._maximized = bool(new_state & Qt.WindowMaximized)
        icon_key = "restore" if self._maximized else "maximize"
        icon_path = self.cfg["icons"].get(icon_key, "")
        tooltip = "还原" if self._maximized else "最大化"

        for child in self.findChildren(QPushButton):
            if child.property("action") == "maximize":
                load_titlebar_icon(child, icon_path, icon_size=20,
                                   tint=self.cfg.get("icons_tint"))
                child.setToolTip(tooltip)

    def register_custom_action(self, action_name: str, callback: Callable[[], None]):
        """注册自定义按钮动作。buttons 里 action 为非内置值时调用对应回调。"""
        self._custom_actions[action_name] = callback

    def set_resizer(self, resizer):
        """注入 window 的边缘缩放器（浮窗用）；None 表示本窗口不可缩放。

        顶边缩放让位依赖此引用：顶边热区内按下时，若 resizer 存在且 enabled，
        则把按下事件让给 resizer（缩放），否则照常拖动。
        """
        self._resizer = resizer

    def set_title(self, title: str):
        self.cfg["window"]["title"] = title
        if hasattr(self, "_title_label"):
            self._title_label.setText(title)

    # -------------------------- 构建 UI -------------------------- #
    def _build_ui(self):
        tcfg = self.cfg["titlebar"]
        self.setFixedHeight(tcfg["height"])

        lay = QHBoxLayout(self)
        lay.setContentsMargins(*tcfg["padding"])
        lay.setSpacing(0)
    # ----- 添加 Logo（支持配置） -----
        logo_cfg = self.cfg.get("logo", {})
        if logo_cfg.get("image"):
            ml = logo_cfg.get("margin_left", 0)
            mr = logo_cfg.get("margin_right", 0)
            # 左间距用 spacer，避免 setContentsMargins 裁剪 QLabel 内容区
            if ml > 0:
                spacer = QWidget(self)
                spacer.setFixedWidth(ml)
                spacer.setStyleSheet("background:transparent;")
                lay.addWidget(spacer)
            logo_label = QLabel(self)
            # 图标不拦截鼠标：让鼠标事件穿透到标题栏，实现整窗拖动
            logo_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            w = logo_cfg.get("width", 28)
            h = logo_cfg.get("height", 28)
            # SVG 用染色渲染（解决 currentColor → 黑色），PNG 回退 QPixmap
            if logo_cfg["image"].lower().endswith(".svg"):
                tint_color = self.cfg.get("titlebar", {}).get("foreground", "#1F2430")
                pixmap = _tinted_svg_pixmap(logo_cfg["image"], tint_color, max(w, h))
            else:
                pixmap = QPixmap(logo_cfg["image"])
            if not pixmap.isNull():
                scaled = pixmap.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(scaled)
                logo_label.setFixedSize(w, h)
                lay.addWidget(logo_label)
            # 右间距用 spacer
            if mr > 0:
                spacer = QWidget(self)
                spacer.setFixedWidth(mr)
                spacer.setStyleSheet("background:transparent;")
                lay.addWidget(spacer)
        # 按每个按钮的 align 字段分拣到左侧或右侧
        left_buttons = []
        right_buttons = []
        for b in self.cfg["buttons"]:
            if not b.get("enabled", True):
                continue
            align = b.get("align", "right")   # 默认右侧
            btn = self._make_button(b)
            if align == "left":
                left_buttons.append(btn)
            else:
                right_buttons.append(btn)

        # 左侧按钮
        for btn in left_buttons:
            lay.addWidget(btn)

        # 标题
        self._title_label = QLabel(self.cfg["window"].get("title", ""))
        self._title_label.setObjectName("TitleLabel")
        f = QFont(self.cfg["font"].get("family", "Sans Serif"))
        f.setPointSize(self.cfg["font"].get("title_size", 14))
        self._title_label.setFont(f)
        # 标题文字不拦截鼠标：落在标题上的按下事件穿透到标题栏，
        # 否则 QLabel 默认吞掉事件，标题区无法触发整窗拖动。
        self._title_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        if tcfg.get("title_align") == "center":
            # 标题居中：左右各加一个 stretch
            lay.insertStretch(len(left_buttons), 1)
            lay.addWidget(self._title_label)
            lay.addStretch(1)
        else:
            # 标题靠左：左侧按钮后直接接标题，右侧按钮在 stretch 之后
            lay.addWidget(self._title_label)
            lay.addStretch(1)

        # 右侧按钮
        for btn in right_buttons:
            lay.addWidget(btn)

    def _make_button(self, b: dict) -> QPushButton:
        btn = QPushButton(self)
        action = b.get("action", "")
        icon_key = b.get("icon_key") or action
        symbol = self.cfg["icons"].get(icon_key, "")
        tint = self.cfg.get("icons_tint")
        # 按钮图标尺寸：优先读 cfg（浮窗传 button_icon_size 跟随按钮高度缩放），
        # 默认 20 保持主窗口等未传值的场景不变。
        icon_size = int(self.cfg.get("titlebar", {}).get("button_icon_size", 20))
        load_titlebar_icon(btn, symbol, icon_size=icon_size, tint=tint)

        btn.setObjectName(f"Btn_{b.get('id', action)}")
        btn.setToolTip(b.get("tooltip", ""))
        btn.setProperty("danger", "1" if b.get("danger") else "0")
        btn.setProperty("action", action)

        bs = self.cfg["button_size"]
        btn.setFixedSize(QSize(bs.get("width", 40), bs.get("height", 34)))
        f = QFont(self.cfg["font"].get("family", "Sans Serif"))
        f.setPointSize(self.cfg["font"].get("button_size", 15))
        btn.setFont(f)
        btn.clicked.connect(lambda _=False, a=action, bid=b.get("id", ""): self._on_clicked(a, bid))
        return btn

    def _apply_inline_style(self):
        """重刷标题栏内联样式（样式钩子混入时自动调用，必须幂等）。"""
        c = self.cfg["colors"]; tb = self.cfg["titlebar"]; f = self.cfg["font"]
        self.setStyleSheet(f"""
            #CustomTitleBar {{ background:{tb['background']}; color:{tb['foreground']}; }}
            #TitleLabel {{ color:{tb['foreground']}; background:transparent; border:none; }}
            QPushButton {{
                background:{c.get('button_normal','transparent')}; color:{tb['foreground']};
                border:none; border-radius:0px;
                padding:0px; min-height:0px;
                font-size:{f.get('button_size',15)}px;
            }}
            QPushButton:hover {{ background:{c.get('button_hover','#465c70')}; }}
            QPushButton:pressed {{ background:{c.get('button_press','#5a7590')}; }}
            QPushButton[action="close"]:hover {{ background:{c.get('close_hover','#c0392b')}; }}
            QPushButton[action="close"]:pressed {{ background:{c.get('close_press','#a5281b')}; }}
        """)

    # -------------------------- 点击分发 -------------------------- #
    def _on_clicked(self, action: str, btn_id: str):
        if action in self.BUILTIN_ACTIONS and hasattr(self, f"_act_{action}"):
            getattr(self, f"_act_{action}")()
        else:
            cb = self._custom_actions.get(action) or self._custom_actions.get(btn_id)
            if cb:
                cb()
            else:
                print(f"[TitleBar] 未注册自定义动作: action={action} id={btn_id}")

    # ---- 内置动作 ----
    def _act_tray(self):
        if self._tray_icon and self._window:
            self._window.hide()
            self._tray_icon.showMessage(self.cfg["window"].get("title", "App"),
                                        self.cfg["tray"].get("tooltip", ""),
                                        QSystemTrayIcon.Information, 1500)

    def _act_minimize(self):
        if self._window:
            self._window.showMinimized()

    def _act_maximize(self):
        if not self._window:
            return
        if self._maximized:
            self._window.showNormal()
            self._maximized = False
        else:
            self._window.showMaximized()
            self._maximized = True

        # 确定新图标路径
        icon_key = "restore" if self._maximized else "maximize"
        icon_path = self.cfg["icons"].get(icon_key, "")
        tooltip = "还原" if self._maximized else "最大化"

        # 更新按钮（使用 load_titlebar_icon，随主题染色）
        for child in self.findChildren(QPushButton):
            if child.property("action") == "maximize":
                load_titlebar_icon(child, icon_path, icon_size=20,
                                   tint=self.cfg.get("icons_tint"))
                child.setToolTip(tooltip)

    def _act_close(self):
        # 如果有关联的窗口，只关闭该窗口
        if self._window:
            self._window.close()
        else:
            # 没有关联窗口时才退出应用
            QApplication.quit()
    # -------------------------- 托盘 -------------------------- #
    def _init_tray(self, window: QWidget):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self._tray_icon = QSystemTrayIcon(window)
        # 托盘图标：优先用 icons.tray_icon，回退到 icons.tray，再回退到 logo.image
        tray_path = (self.cfg["icons"].get("tray_icon")
                     or self.cfg["icons"].get("tray")
                     or self.cfg.get("logo", {}).get("image"))
        if tray_path:
            fg = self.cfg.get("titlebar", {}).get("foreground", "#1F2430")
            if tray_path.lower().endswith(".svg"):
                icon = _tinted_svg_icon(tray_path, fg, 32)
            else:
                icon = QIcon(tray_path)
            if not icon.isNull():
                self._tray_icon.setIcon(icon)
        else:
            self._tray_icon.setIcon(_symbol_icon("T", "#1F2430", 64))
        self._tray_icon.setToolTip(self.cfg["window"].get("title", "App"))
        menu = QMenu(window)
        for item in self.cfg["tray"].get("menu", []):
            act_text = item.get("label", "")
            act_key = item.get("action", "")
            qact = menu.addAction(act_text)
            qact.triggered.connect(lambda _=False, k=act_key: self._tray_menu(k))
        self._tray_icon.setContextMenu(menu)
        self._tray_icon.activated.connect(
            lambda reason: self._window.show() if reason == QSystemTrayIcon.Trigger else None)
        self._tray_icon.show()

    def _tray_menu(self, key: str):
        if key == "show":
            if self._window:
                self._window.showNormal(); self._window.raise_(); self._window.activateWindow()
        elif key == "quit":
            QApplication.quit()

    # -------------------------- 拖拽移动 -------------------------- #
    def mousePressEvent(self, e):
        if e.button() != Qt.LeftButton:
            return
        # 顶边热区：交给 window 的缩放器处理（缩放），不启动拖动。
        # 仅当缩放器存在且启用时让位；否则（不可缩放 / 已固定）顶边照常拖动。
        if (self._resizer is not None and self._resizer.is_enabled()
                and self._top_resize_margin > 0
                and e.pos().y() <= self._top_resize_margin):
            e.ignore()      # 让事件冒泡到 window，由 WindowResizer 接管顶边缩放
            return
        if not self.cfg["titlebar"].get("draggable", True):
            return
        if not self._window:
            return
        # 优先用系统原生拖动：startSystemMove() 在 Windows 下由操作系统接管
        # 整个拖动过程，避免 grabMouse()+move() 在无边框窗口上捕获丢失的
        # 已知问题（SetCapture 与 SetWindowPos 冲突导致拖不动/中途失效）。
        wnd = self._window.windowHandle()
        if wnd is not None:
            e.accept()
            wnd.startSystemMove()
            return
        # 回退：窗口句柄不可用时手动拖动
        self._drag_pos = e.globalPosition().toPoint() - self._window.geometry().topLeft()
        e.accept()

    def mouseMoveEvent(self, e):
        if self._drag_pos is None or not self._window:
            return
        if not e.buttons() & Qt.LeftButton:
            self._drag_pos = None
            return
        if self._maximized:
            self._act_maximize()  # 拖拽时还原
        self._window.move(e.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, e):
        self._drag_pos = None


# --------------------------------------------------------------------------- #
#  便捷：带标题栏的完整无边框窗口
# --------------------------------------------------------------------------- #
class TitleBarWindow(QMainWindow):
    """开箱即用的无边框主窗口：顶部标题栏 + 下方内容区。"""

    def __init__(self, config=None, parent=None):
        super().__init__(parent)
        self.cfg = load_config(config)
        self.setWindowTitle(self.cfg["window"].get("title", "App"))
        w = self.cfg["window"]
        self.resize(w.get("width", 900), w.get("height", 600))
        if w.get("frameless"):
            self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

        self._central = QWidget()
        self._central.setLayout(QVBoxLayout())
        self._central.layout().setContentsMargins(0, 0, 0, 0)
        self._central.layout().setSpacing(0)
        self.setCentralWidget(self._central)

        self.title_bar = CustomTitleBar(config=self.cfg)
        self.title_bar.attach_window(self)
        self._central.layout().addWidget(self.title_bar)
        self._content_host = QWidget()
        self._content_host.setLayout(QVBoxLayout())
        self._content_host.layout().setContentsMargins(12, 12, 12, 12)
        self._content_host.setStyleSheet(
            f"background:{C.color('card') or self.cfg['colors'].get('content_bg', '#FFFFFF')};")
        self._central.layout().addWidget(self._content_host, 1)

        if self.cfg["tray"].get("enabled"):
            QApplication.setQuitOnLastWindowClosed(False)

    def set_content(self, widget: QWidget):
        """设置窗口正文内容区部件。"""
        for child in self._content_host.children():
            if isinstance(child, QWidget) and child is not widget:
                child.setParent(None)
        self._content_host.layout().addWidget(widget)

    def register_custom_action(self, name: str, cb: Callable[[], None]):
        self.title_bar.register_custom_action(name, cb)


def main():
    app = QApplication(sys.argv)

    # 演示：通过配置把按钮放到左侧
    config = {
        "titlebar": {"button_align": "left"},
        "window": {"title": "按钮在左侧 - 自定义标题栏"},
    }
    window = TitleBarWindow(config=config)

    label = QLabel("按钮已移到标题栏左侧\n拖拽标题栏移动窗口")
    label.setStyleSheet("font-size: 18px; padding: 30px;")
    window.set_content(label)

    window.resize(500, 360)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()