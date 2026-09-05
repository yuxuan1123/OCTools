"""
OCTools/ui/ui_component/vertical_split_titlebar.py
───────────────────────────────────────────────
组合窗口（单标题栏 + 垂直分割版）：
- 顶部标题栏：窗口名称、最小化、最大化/还原、关闭（无托盘）
- 下方：上下两栏分割窗口（reuse `_Pane`，上深 / 下浅配色）
- 窗口缩放：通过 window_resizer.WindowResizer 提供无边框边缘/角落拖拽拉伸

与 split_titlebar.py 的关系：
  - splitter orientation 不同：本文件 Qt.Vertical（上下两栏），split_titlebar.py
    Qt.Horizontal（左右两栏）
  - 仅顶部一个标题栏（无底部折叠按钮）

所有布局/颜色/尺寸参数统一从 config/ui_config.json 的 titlebar/split 段读取
（CONFIG 单例）。

直接运行（项目根目录）:
    python -m ui.ui_component.vertical_split_titlebar
"""

from __future__ import annotations

if __name__ == "__main__":
    # Bootstrap：让 `python ui/ui_component/vertical_split_titlebar.py` 直跑也能工作。
    # 文件内 `from .split_window import _Pane` 等相对 import 要求模块必须以
    # `ui.ui_component.vertical_split_titlebar` 身份加载（有包上下文）。直跑时无包
    # 上下文会立即报 `ImportError: attempted relative import with no known
    # parent package`。解法：在文件最早处检测 `__name__`；若为 "__main__" 则用
    # importlib 以包成员身份重新加载本文件，再调用 `main()`。
    import os, sys, importlib.util
    _PROJ_ROOT = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
    )
    if _PROJ_ROOT not in sys.path:
        sys.path.insert(0, _PROJ_ROOT)
    _SPEC = importlib.util.spec_from_file_location(
        "ui.ui_component.vertical_split_titlebar",
        os.path.abspath(__file__),
    )
    _MOD = importlib.util.module_from_spec(_SPEC)
    sys.modules["ui.ui_component.vertical_split_titlebar"] = _MOD
    _SPEC.loader.exec_module(_MOD)
    sys.exit(_MOD.main())


import sys
import os


from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSplitter,
    QMainWindow, QPushButton, QSizePolicy
)

# 复用已有组件
from .split_window import _Pane
from .titlebar_component import (
    CustomTitleBar,
    set_titlebar_icon_tint as _set_tint,
    load_titlebar_icon as _load_tb_icon,
)

# 独立、可复用的无边框窗口拉伸组件
from .window_resizer import attach_resizer

# 统一 UI 参数（JSON 驱动）
from config.ui_config import CONFIG as C

# 全局 UI 风格变化广播（框架配色随主题联动）
from ui.theme import THEME_BUS

# 项目根目录（用于把相对路径解析为绝对路径）
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.normpath(os.path.join(_HERE, "..", ".."))


def _resolve(path: str) -> str:
    """相对项目根的路径 -> 绝对路径（绝对路径原样返回）。"""
    if not path:
        return path
    return path if os.path.isabs(path) else os.path.normpath(os.path.join(_PROJECT_ROOT, path))


def _resolve_icons(cfg: dict) -> dict:
    """把配置里的图标路径解析为绝对路径，便于 QPixmap 直接加载。"""
    cfg = dict(cfg)
    if isinstance(cfg.get("icons"), dict):
        cfg["icons"] = {k: _resolve(v) for k, v in cfg["icons"].items()}
    if isinstance(cfg.get("logo"), dict) and cfg["logo"].get("image"):
        cfg["logo"] = dict(cfg["logo"])
        cfg["logo"]["image"] = _resolve(cfg["logo"]["image"])
    return cfg


class VerticalWindow(QMainWindow):
    """单标题栏 + 上下两栏分割的组合窗口。

    与 TestWindow（split_titlebar.py，水平双标题栏）的差异：
      - 仅顶部一个标题栏（无底部折叠条 / 无折叠按钮）
      - splitter 为 Qt.Vertical（上下两栏），而非水平（左右两栏）
      - 命名 upper / lower 对应 split.panes.upper / lower（缺失时回退 left / right 兼容）
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("组合窗口（单标题栏 + 上下两栏）")
        _lay = C.section("layout")
        self.resize(_lay.get("window_w", 1120), _lay.get("window_h", 820))

        # 无边框（由顶部标题栏控制拖拽）
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

        # 缓存顶部标题栏配置中的 logo 路径，用于 showEvent 重设任务栏图标
        self._icon_path_for_taskbar = None
        top_cfg_for_icon = _resolve_icons(C.section("titlebar").get("top", {}))
        logo_cfg = top_cfg_for_icon.get("logo", {})
        self._icon_path_for_taskbar = (logo_cfg.get("image")
                                       or top_cfg_for_icon.get("icons", {}).get("tray_icon"))

        # ---------- 中心部件 ----------
        central = QWidget()
        central.setObjectName("CentralWidget")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---------- 1. 顶部标题栏（窗口控制，无托盘） ----------
        top_cfg = _resolve_icons(C.section("titlebar").get("top", {}))
        if not top_cfg.get("window"):
            top_cfg["window"] = {"title": "OCTools", "frameless": True}

        self.top_bar = CustomTitleBar(config=top_cfg)
        self.top_bar.attach_window(self)
        main_layout.addWidget(self.top_bar)

        # ---------- 2. 上下两栏分割区域 ----------
        split_cfg = C.section("split")
        scfg = split_cfg.get("splitter", {})
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(int(scfg.get("handle_width", 4)))
        splitter.setChildrenCollapsible(False)
        self._splitter = splitter

        # 上分区
        upper_cfg = split_cfg.get("panes", {}).get("upper",
                    split_cfg.get("panes", {}).get("left", {}))
        upper_cfg["background"] = C.color("sidebar_bg")
        self.upper_pane = _Pane(upper_cfg)
        self._upper_cfg = upper_cfg
        self.upper_pane.set_body(QLabel("上分区内容区\n（业务树/导航/列表等）"))
        self.upper_pane.setMinimumHeight(40)
        self.upper_pane.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Ignored)

        # 下分区
        lower_cfg = split_cfg.get("panes", {}).get("lower",
                    split_cfg.get("panes", {}).get("right", {}))
        lower_cfg["background"] = C.color("bg")
        self.lower_pane = _Pane(lower_cfg)
        self._lower_cfg = lower_cfg
        self.lower_pane.set_body(QLabel("下分区内容区\n（编辑器/详情/控制台等）"))

        splitter.addWidget(self.upper_pane)
        splitter.addWidget(self.lower_pane)

        # 上分区高度以 layout.sidebar_h 为唯一真源；split.sizes 仅提供回退比例。
        # stretch [0, 1] 让上分区保持固定高度，伸缩只作用于下分区内容区。
        sizes = list(scfg.get("sizes") or [200, 560])
        sidebar_h = C.section("layout").get("sidebar_h")
        if sidebar_h:
            sizes[0] = sidebar_h
        for i, s in enumerate(scfg.get("stretch") or [0, 1]):
            splitter.setStretchFactor(i, s)
        splitter.setSizes(sizes)

        # 底缘让出「滚动条外侧的缩放区」：滚动条不再紧贴窗口底缘，
        # 最外侧露出中央面板背景条（坐标即窗口坐标，缩放可正常触发），
        # 避免 tab 滚动条与底缘 6px 缩放区重合。
        gutter = C.size("scrollbar_edge_gutter")
        splitter_row = QWidget()
        sr = QHBoxLayout(splitter_row)
        sr.setContentsMargins(0, 0, 0, gutter)        # ← 底缘让位（与 split_titlebar 的右缘让位对称）
        sr.setSpacing(0)
        sr.addWidget(splitter)

        main_layout.addWidget(splitter_row, 1)

        # ---------- 3. 绑定无边框窗口边缘拉伸（独立组件，便于复用） ----------
        lay_cfg = C.section("layout")
        _min_w = lay_cfg.get("window_min_w", 980)
        _min_h = lay_cfg.get("window_min_h", 660)
        self.setMinimumSize(_min_w, _min_h)
        self.resizer = attach_resizer(self, margin=6,
                                      min_width=_min_w, min_height=_min_h)

        # ---------- 4. 主题联动：框架配色/图标/背景随全局 UI 风格刷新 ----------
        THEME_BUS.changed.connect(lambda _t: self._refresh_theme())
        self._refresh_theme()   # 启动即按当前主题着色

    # -------------------------- 主题联动 -------------------------- #
    def _refresh_theme(self):
        """主题变化：刷新顶部标题栏配色/图标 与 分割面板背景（不动业务内容）。

        注意：CustomTitleBar 内部对传入 config 做了深合并（load_config），
        self.top_bar.cfg 与构造时传入的 top_cfg 并非同一对象。因此必须直接改
        bar.cfg，bar._apply_inline_style() 才能读到新配色。
        """
        _set_tint(C.color("title_fg"))
        bar = self.top_bar
        cfg = bar.cfg
        tb = cfg.setdefault("titlebar", {})
        tb["background"] = C.color("sidebar_bg")
        tb["foreground"] = C.color("text")
        colors = cfg.setdefault("colors", {})
        colors["button_hover"] = C.color("hover")
        colors["button_press"] = C.color("pressed")
        colors["close_hover"] = C.color("danger")
        colors["close_press"] = C.color("danger_dark")
        bar._apply_inline_style()
        for btn in bar.findChildren(QPushButton):
            action = btn.property("action") or ""
            icon_key = action
            for b in cfg.get("buttons", []):
                if b.get("action") == action:
                    icon_key = b.get("icon_key") or action
                    break
            path = cfg.get("icons", {}).get(icon_key, "")
            if path:
                _load_tb_icon(btn, path, 20)
        # 分割面板背景
        self._upper_cfg["background"] = C.color("sidebar_bg")
        self._lower_cfg["background"] = C.color("bg")
        self.upper_pane.set_pane_style(self.upper_pane, {"background": self._upper_cfg["background"]})
        self.upper_pane.set_pane_style(self.upper_pane._body, {"background": self._upper_cfg["background"]})
        self.lower_pane.set_pane_style(self.lower_pane, {"background": self._lower_cfg["background"]})
        self.lower_pane.set_pane_style(self.lower_pane._body, {"background": self._lower_cfg["background"]})

    # -------------------------- 公共 API -------------------------- #
    def set_upper_content(self, widget: QWidget):
        self.upper_pane.set_body(widget)

    def set_lower_content(self, widget: QWidget):
        self.lower_pane.set_body(widget)

    # -------------------------- 窗口事件 -------------------------- #
    def showEvent(self, event):
        """窗口显示后强制设置任务栏图标（FramelessWindowHint 在 Windows
        show 之后可能擦除 Qt 的 setWindowIcon）。用 Windows API 直接
        发送 WM_SETICON + 修改窗口类图标。"""
        super().showEvent(event)
        if self._icon_path_for_taskbar:
            import tempfile
            import ctypes
            from ctypes import wintypes
            from PySide6.QtGui import QPixmap, QPainter, QColor, QIcon
            from PySide6.QtCore import QRectF
            from PySide6.QtSvg import QSvgRenderer

            fg = self.top_bar.cfg.get("titlebar", {}).get("foreground", "#1F2430")
            try:
                r = QSvgRenderer(self._icon_path_for_taskbar)
            except Exception:
                r = None
            if not r or not r.isValid():
                return

            # 渲染 SVG 并染色 → 32×32 彩色 pixmap
            px = QPixmap(32, 32)
            px.fill(Qt.transparent)
            p = QPainter(px)
            r.render(p, QRectF(0, 0, 32, 32))
            p.setCompositionMode(QPainter.CompositionMode_SourceIn)
            p.fillRect(px.rect(), QColor(fg))
            p.end()

            # 存为临时 .ico 文件（Windows 任务栏对 .ico 支持最好）
            ico_path = os.path.join(tempfile.gettempdir(),
                                    "OCTools_taskbar_icon.ico")
            px.toImage().save(ico_path, "ICO")

            # --- 方法 1: Qt 标准方法 ---
            ico = QIcon(ico_path)
            self.setWindowIcon(ico)
            wnd = self.windowHandle()
            if wnd:
                wnd.setIcon(ico)
            app = QApplication.instance()
            if app:
                app.setWindowIcon(ico)

            # --- 方法 2: Windows API 直接设任务栏图标 ---
            try:
                hwnd_val = int(self.winId())
                if hwnd_val > 0:
                    user32 = ctypes.windll.user32
                    user32.LoadImageW.restype = wintypes.HANDLE
                    user32.SetClassLongPtrW.restype = wintypes.HANDLE
                    hwnd = wintypes.HWND(hwnd_val)

                    hicon = user32.LoadImageW(
                        None, ico_path, 1, 32, 32, 0x0010
                    )
                    if hicon:
                        WM_SETICON = 0x0080
                        user32.SendMessageW(hwnd, WM_SETICON, 0, hicon)
                        user32.SendMessageW(hwnd, WM_SETICON, 1, hicon)
                        user32.SetClassLongPtrW(hwnd, -14, hicon)
                        user32.SetClassLongPtrW(hwnd, -34, hicon)
            except Exception:
                pass  # 非 Windows 或不支持时静默忽略


def main():
    app = QApplication(sys.argv)
    window = VerticalWindow()
    window.show()
    sys.exit(app.exec())
