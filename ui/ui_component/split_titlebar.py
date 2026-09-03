"""
OCTools/ui/ui_component/split_titlebar.py
───────────────────────────────────────────────
组合窗口：两个标题栏 + 两栏分割布局
- 顶部标题栏：窗口名称、最小化、最大化/还原、关闭（无托盘）
- 底部标题栏：复用 CustomTitleBar，仅左侧一个折叠/展开按钮（由 _make_button 构造）
- 下方：两栏分割窗口（左侧深色、右侧浅色）
- 窗口缩放：通过 window_resizer.WindowResizer 提供无边框边缘/角落拖拽拉伸（本文件仅绑定与调用）

所有布局/颜色/尺寸参数统一从 config/ui_config.json 的 titlebar/split 段读取（CONFIG 单例）。
"""

from __future__ import annotations

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


class TestWindow(QMainWindow):
    """两个标题栏 + 两栏分割的组合窗口。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("组合窗口")
        _lay = C.section("layout")
        self.resize(_lay.get("window_w", 1100), _lay.get("window_h", 760))

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

        # ---------- 2. 底部标题栏（折叠按钮，复用 CustomTitleBar） ----------
        bottom_cfg = _resolve_icons(C.section("titlebar").get("bottom", {}))
        if not bottom_cfg.get("window"):
            bottom_cfg["window"] = {"title": "", "frameless": True}

        self.bottom_bar = CustomTitleBar(config=bottom_cfg)
        # 不调用 attach_window，不影响顶层窗口
        main_layout.addWidget(self.bottom_bar)

        # 隐藏底部的空标题标签
        title_label = self.bottom_bar.findChild(QLabel, "TitleLabel")
        if title_label:
            title_label.hide()

        # 获取折叠按钮的引用（由 _make_button 构造，objectName 为 "Btn_collapse"）
        self.collapse_btn = self.bottom_bar.findChild(QPushButton, "Btn_collapse")
        # 注册自定义折叠动作
        self.bottom_bar.register_custom_action("collapse", self._toggle_left_pane)

        # ---------- 3. 两栏分割区域 ----------
        split_cfg = C.section("split")
        scfg = split_cfg.get("splitter", {})
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(int(scfg.get("handle_width", 4)))
        splitter.setChildrenCollapsible(False)
        self._splitter = splitter

        # 左侧面板
        left_cfg = split_cfg.get("panes", {}).get("left", {})
        left_cfg["background"] = C.color("sidebar_bg")
        self.left_pane = _Pane(left_cfg)
        self._left_cfg = left_cfg
        self.left_pane.set_body(QLabel("左侧内容区\n（业务树/导航等）"))
        self.left_pane.setMinimumWidth(10)
        self.left_pane.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)

        # 右侧面板
        right_cfg = split_cfg.get("panes", {}).get("right", {})
        right_cfg["background"] = C.color("bg")
        self.right_pane = _Pane(right_cfg)
        self._right_cfg = right_cfg
        self.right_pane.set_body(QLabel("右侧内容区\n（编辑器/详情等）"))

        splitter.addWidget(self.left_pane)
        splitter.addWidget(self.right_pane)

        # 左栏宽度以 layout.sidebar_w 为唯一真源；split.sizes 仅提供回退比例。
        # stretch [0, 1] 让左栏保持固定宽度，伸缩只作用于右栏内容区。
        sizes = list(scfg.get("sizes") or [60, 760])
        sidebar_w = C.section("layout").get("sidebar_w")
        if sidebar_w:
            sizes[0] = sidebar_w
        for i, s in enumerate(scfg.get("stretch") or [0, 1]):
            splitter.setStretchFactor(i, s)
        splitter.setSizes(sizes)

        # 右缘让出「滚动条外侧的缩放区」：滚动条不再紧贴窗口右缘，
        # 最外侧露出中央面板背景条（坐标即窗口坐标，缩放可正常触发），
        # 避免 tab 滚动条与右缘 6px 缩放区重合。
        gutter = C.size("scrollbar_edge_gutter")
        splitter_row = QWidget()
        sr = QHBoxLayout(splitter_row)
        sr.setContentsMargins(0, 0, gutter, 0)
        sr.setSpacing(0)
        sr.addWidget(splitter)

        main_layout.addWidget(splitter_row, 1)

        # ---------- 折叠状态 ----------
        self._left_visible = True

        # ---------- 4. 绑定无边框窗口边缘拉伸（独立组件，便于复用） ----------
        # 边缘命中阈值 6px；最小尺寸限制避免窗口被拖得过小
        lay_cfg = C.section("layout")
        _min_w = lay_cfg.get("window_min_w", 600)
        _min_h = lay_cfg.get("window_min_h", 400)
        # 双重约束：resizer 限制拖拽，setMinimumSize 限制程序化 setGeometry
        self.setMinimumSize(_min_w, _min_h)
        self.resizer = attach_resizer(self, margin=6,
                                      min_width=_min_w, min_height=_min_h)

        # ---------- 5. 主题联动：框架配色/图标/背景随全局 UI 风格刷新 ----------
        THEME_BUS.changed.connect(lambda _t: self._refresh_theme())
        self._refresh_theme()   # 启动即按当前主题着色

    # -------------------------- 主题联动 -------------------------- #
    def _refresh_theme(self):
        """主题变化：刷新标题栏配色/图标 与 分割面板背景（不动业务内容）。

        注意：CustomTitleBar 内部对传入 config 做了深合并（load_config），
        self.top_bar.cfg 与构造时传入的 top_cfg 并非同一对象。因此必须直接改
        bar.cfg，bar._apply_inline_style() 才能读到新配色。
        """
        _set_tint(C.color("title_fg"))
        for bar in (self.top_bar, self.bottom_bar):
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
        self._left_cfg["background"] = C.color("sidebar_bg")
        self._right_cfg["background"] = C.color("bg")
        self.left_pane.set_pane_style(self.left_pane, {"background": self._left_cfg["background"]})
        self.left_pane.set_pane_style(self.left_pane._body, {"background": self._left_cfg["background"]})
        self.right_pane.set_pane_style(self.right_pane, {"background": self._right_cfg["background"]})
        self.right_pane.set_pane_style(self.right_pane._body, {"background": self._right_cfg["background"]})

    # -------------------------- 折叠逻辑 -------------------------- #
    def _toggle_left_pane(self):
        if self._left_visible:
            self.left_pane.hide()
            if self.collapse_btn:
                icon_path = self.bottom_bar.cfg["icons"]["expand"]
                _load_tb_icon(self.collapse_btn, icon_path, icon_size=20)
                self.collapse_btn.setToolTip("展开左侧面板")
            self._left_visible = False
        else:
            self.left_pane.show()
            if self.collapse_btn:
                icon_path = self.bottom_bar.cfg["icons"]["collapse"]
                _load_tb_icon(self.collapse_btn, icon_path, icon_size=20)
                self.collapse_btn.setToolTip("折叠左侧面板")
            self._left_visible = True

    # -------------------------- 公共 API -------------------------- #
    def set_left_content(self, widget: QWidget):
        self.left_pane.set_body(widget)

    def set_right_content(self, widget: QWidget):
        self.right_pane.set_body(widget)

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
            from PySide6.QtGui import QPixmap, QPainter, QColor, QImage, QIcon
            from PySide6.QtCore import Qt, QRectF, QSize
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
                    # 设置返回类型确保 64 位指针不截断
                    user32.LoadImageW.restype = wintypes.HANDLE
                    user32.SetClassLongPtrW.restype = wintypes.HANDLE
                    hwnd = wintypes.HWND(hwnd_val)

                    # 通过 LoadImageW 加载 .ico → HICON
                    hicon = user32.LoadImageW(
                        None,           # hinst
                        ico_path,       # 文件路径
                        1,              # IMAGE_ICON
                        32, 32,         # 目标尺寸
                        0x0010          # LR_LOADFROMFILE
                    )
                    if hicon:
                        WM_SETICON = 0x0080
                        ICON_SMALL = 0
                        ICON_BIG = 1
                        # 发送 WM_SETICON 设置窗口图标
                        user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon)
                        user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hicon)
                        # 修改窗口类图标（任务栏用）
                        GCL_HICON = -14
                        GCL_HICONSM = -34
                        user32.SetClassLongPtrW(hwnd, GCL_HICON, hicon)
                        user32.SetClassLongPtrW(hwnd, GCL_HICONSM, hicon)
            except Exception:
                pass  # 非 Windows 或不支持时静默忽略


def main():
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
