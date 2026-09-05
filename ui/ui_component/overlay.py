"""
OCTools/ui/ui_component/overlay.py
─────────────────────────────────
小号版 `vertical_split_titlebar.py` + 自定义业务按钮。

布局（参考 vertical_split_titlebar.VerticalWindow，缩窗 + 自定义按钮）：
  ┌─────────────────────────────────────┐
  │ CustomTitleBar（标题 + 自定义按钮）    │ ← 来自 vertical_split_titlebar
  ├─────────────────────────────────────┤
  │ QSplitter(Vertical)                 │ ← 来自 vertical_split_titlebar
  │   ├─ upper_pane：原文                │
  │   └─ lower_pane：译文 + 状态行        │
  └─────────────────────────────────────┘

差异（与 vertical_split_titlebar.VerticalWindow）：
  - 基类 QWidget（非 QMainWindow）；flags 加 StaysOnTopHint + Tool +
    WA_TranslucentBackground（任务栏外的小窗）
  - 外层边距 + panel 圆角/边框（营造悬浮质感）
  - 标题栏含自定义按钮（mode/pause/manual/retry/copy/pin/close），
    通过 CustomTitleBar.register_custom_action 注册，对齐 v_st 的折叠按钮注册方式
  - upper_pane 可由 mode 按钮折叠（双语 ↔ 仅译文），需要 upper_visible / 上次尺寸缓存
  - 无 Win32 任务栏图标（悬浮窗，不上任务栏）
  - 自动适配内容尺寸 + 屏幕边界保持（auto-fit + clamp）
  - 内容 API（set_result/set_text/set_status/set_dual_mode/...）

按钮（恒定排版，未选自动隐藏）：见 _BTN_ORDER。
主题样式由 StyleHookMixin 接入（QEvent.StyleChange 自动重刷）。
所有 UI 参数（颜色/字号/尺寸/图标）均来自 config/ui_config.json，通过
config.ui_config.CONFIG 加载，代码中不出现硬编码魔法值。

直接运行（项目根目录）:
    python ui/ui_component/overlay.py
"""

# ── Bootstrap（直跑支持）──
# overlay 用绝对 import（`from config.ui_config import CONFIG as C` 等），文件位于
# `ui/ui_component/` 子目录，直跑时 `python ui/ui_component/overlay.py` 触发
# `ModuleNotFoundError: No module named 'config'`。解法：在顶部把项目根加入
# sys.path。`__name__ == "__main__"` 时执行；被 `import` 时跳过，不影响正常导入。
import os
import sys

if __name__ == "__main__":
    _PROJ_ROOT = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
    )
    if _PROJ_ROOT not in sys.path:
        sys.path.insert(0, _PROJ_ROOT)


from PySide6.QtCore import QRect, Qt, Signal
from PySide6.QtGui import QColor, QGuiApplication, QPainter
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsDropShadowEffect,
    QLabel,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from config.ui_config import CONFIG as C
from ui.style_hook import StyleHookMixin
from ui.ui_component.button_component import load_icon_for_button
from ui.ui_component.split_window import _Pane
from ui.ui_component.titlebar_component import CustomTitleBar, load_titlebar_icon
from ui.ui_component.window_resizer import attach_resizer

# 按钮恒定排版顺序：按此顺序排列，未选中的按钮自动隐藏（不占用空间）
_BTN_ORDER = ("mode", "pause", "manual", "retry", "copy", "pin", "close")

# 按钮 → 图标文件（相对 resources 根） / 提示键
_BTN_ICON = {
    "pause": "resources/icons/player-pause.svg",
    "manual": "resources/icons/refresh.svg",
    "retry": "resources/icons/refresh.svg",
    "copy": "resources/icons/copy.svg",
    "pin": "resources/icons/pin.svg",
    "close": "resources/icons/x.svg",
}
_BTN_TOOLTIP = {
    "mode": "overlay_mode_both_tooltip",
    "pause": "overlay_pause_tooltip",
    "manual": "overlay_refresh_tooltip",
    "retry": "overlay_refresh_tooltip",
    "copy": "overlay_copy_tooltip",
    "pin": "overlay_pin_tooltip",
    "close": "overlay_close_tooltip",
}

# 允许的按钮 id
_BTN_ALL = set(_BTN_ORDER)


def _overlay_logo_cfg() -> dict:
    """悬浮框标题栏 logo 配置：复用主窗口 titlebar.top.logo（JSON 驱动）。"""
    logo = (C.section("titlebar").get("top", {}) or {}).get("logo", {}) or {}
    return {
        "image": logo.get("image") or "resources/icons/yin-yang.svg",
        "width": logo.get("width", 24),
        "height": logo.get("height", 24),
        "margin_left": logo.get("margin_left", 8),
        "margin_right": logo.get("margin_right", 6),
    }


class FloatingOverlay(StyleHookMixin, QWidget):
    """通用参数化置顶悬浮显示框（复用 CustomTitleBar + _Pane + window_resizer）。

    小号版的 vertical_split_titlebar.VerticalWindow：单标题栏 + 上下两栏 +
    WindowResizer，再加自定义按钮（mode/pause/manual/retry/copy/pin/close）。

    参数：
      buttons       需要显示的按钮 id 列表（子集，如 ["copy", "close"]）
      title         标题文本（None 使用默认标题）
      show_orig     是否显示原文行（双语应用 True；纯文本应用 False）
      show_status   是否显示状态行（默认 True）
      bg_color      背景：None/空=默认浅色（JSON overlay_default_bg_light）；
                     "transparent"=透明+文字阴影；"#RRGGBB"=纯色填充
      font_size     正文字号（px）
      movable       是否可拖动（默认 True）
      resizable     是否可缩放（默认 True）
      pinned_default是否默认固定（锁定位置与大小）
    """

    close_clicked = Signal()
    copy_clicked = Signal()
    retry_clicked = Signal()
    manual_clicked = Signal()
    pause_toggled = Signal(bool)   # True=暂停 / False=恢复
    mode_changed = Signal(bool)    # True=双语 / False=仅译文

    def __init__(self, buttons=None, title=None, show_orig=True, show_status=True,
                 bg_color=None, font_size=None, movable=True, resizable=True,
                 pinned_default=False, parent=None):
        super().__init__(parent,
                         Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        # 工具窗口关闭不应退出整个程序
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # ── 状态 ──
        self._buttons = self._validate_buttons(buttons)
        self._title_text = title if title is not None else C.text("overlay_title_full")
        # 默认浅色（JSON 驱动）；显式传 "transparent" 或 #RRGGBB 时按原值
        self._bg_color = str(bg_color) if bg_color \
            else (C.color("overlay_default_bg_light") or "#FFFFFF")
        self._font_size = max(8, min(24, int(font_size or C.font("body"))))
        self._movable = bool(movable)
        self._resizable = bool(resizable)
        self._pinned = bool(pinned_default)
        self._paused = False
        self._show_orig = bool(show_orig)
        self._show_status = bool(show_status)
        self._mode = "both"   # both=双语 / trans=仅译文
        self._region_box = None
        self.upper_visible = True     # 上分区当前是否可见（mode 折叠状态）
        self._upper_sizes = None      # 收缩前保存的分栏尺寸（展开时恢复）
        # 用户是否手动调整过窗口大小：True 后内容刷新不再 auto-fit 覆盖尺寸
        self._user_sized = False
        self._auto_sizing = False     # 程序化 resize 期间置位（避免误判为手动缩放）
        self._last_geo_size = None
        self._close_emitted = False   # closeEvent 只发一次 close_clicked
        # 样式缓存键：背景/字号变化才重建样式表
        self._visual_key = None

        # 最大宽度 = 所在屏幕宽度的一半左右
        screen = QGuiApplication.primaryScreen()
        sw = screen.geometry().width() if screen else 1920
        self._max_w = max(C.size("overlay_max_w_min"),
                          min(C.size("overlay_max_w_max"), sw // C.size("overlay_screen_half_div")))
        self._default_h = C.size("overlay_default_h") or 240

        # ── 构建 + 主题首次应用（步骤对齐 vertical_split_titlebar）──
        self._build_ui()        # 1) 标题栏  2) 上下两栏  3) resizer
        self._refresh_theme()   # 4) 主题样式首次落地
        self._apply_mode()      # 根据 mode 决定上栏显隐
        if self._pinned:
            self.set_pinned(True)
        self._apply_default_position()

    # ── 构建设置 ──

    @staticmethod
    def _validate_buttons(buttons):
        """过滤非法按钮 id，按恒定顺序排列（未选择的自动隐藏）"""
        if not buttons:
            return []
        return [b for b in _BTN_ORDER if b in buttons]

    def _build_ui(self):
        # ── 外层布局：边距用于 translucency（overlay 专属）──
        outer = QVBoxLayout(self)
        outer.setContentsMargins(C.size("overlay_margin_l"), C.size("overlay_margin_t"),
                                 C.size("overlay_margin_r"), C.size("overlay_margin_b"))
        outer.setSpacing(0)

        # panel：圆角/边框/纯色面板的载体（overlay 专属）
        self._panel = QWidget(self)
        self._panel.setObjectName("overlay_panel")
        outer.addWidget(self._panel)
        lay = QVBoxLayout(self._panel)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # ── 1) 顶部标题栏（窗口控制 + 自定义动作注册）──
        self._title_bar = CustomTitleBar(config=self._titlebar_config(), parent=self._panel)
        self._title_bar.attach_window(self)
        for bid, handler in self._custom_handlers():
            self._title_bar.register_custom_action(bid, handler)
        lay.addWidget(self._title_bar)

        # ── 2) 上下两栏分割区域（upper_pane / lower_pane，对齐 v_st 命名）──
        scfg = C.section("split").get("splitter", {})
        self._splitter = QSplitter(Qt.Vertical, self._panel)
        self._splitter.setChildrenCollapsible(False)
        self._splitter.setHandleWidth(C.size("overlay_split_handle") or 2)

        # 上分区：原文
        self.upper_pane = _Pane({"background": "transparent"})
        self._orig_label = QLabel("（等待识别…）")
        self._orig_label.setObjectName("overlay_orig")
        self.upper_pane.set_body(self._orig_label)
        self._splitter.addWidget(self.upper_pane)

        # 下分区：译文 + 状态行
        self.lower_pane = _Pane({"background": "transparent"})
        low_body = QWidget()
        vb = QVBoxLayout(low_body)
        vb.setContentsMargins(0, 0, 0, 0)
        vb.setSpacing(0)
        self._trans_label = QLabel("…")
        self._trans_label.setObjectName("overlay_trans")
        self._status_label = QLabel("")
        self._status_label.setObjectName("overlay_status")
        vb.addWidget(self._trans_label, 1)
        vb.addWidget(self._status_label)
        self.lower_pane.set_body(low_body)
        self._splitter.addWidget(self.lower_pane)

        # 上 / 下均分伸缩：overlay 不像 v_st 那样上分区写死高度（悬浮窗内容自适应）
        self._splitter.setSizes([C.size("overlay_split_upper") or 140,
                                 C.size("overlay_split_lower") or 160])
        self._splitter.setStretchFactor(0, 1)
        self._splitter.setStretchFactor(1, 1)
        lay.addWidget(self._splitter, 1)

        # ── 3) 无边框边缘/角落缩放（overlay 专属：margin 默认 8 可由 JSON 覆盖）──
        self._resizer = None
        if self._resizable:
            self._resizer = attach_resizer(
                self, margin=C.size("overlay_resize_margin") or 8,
                min_width=C.size("overlay_min_w") or 160,
                min_height=C.size("overlay_min_h") or 60)
            # 让标题栏在顶边热区把按下事件让给 resizer（实现顶边缩放）
            self._title_bar.set_resizer(self._resizer)

    # ── 标题栏配置（JSON 驱动，复用 CustomTitleBar）──

    def _titlebar_config(self) -> dict:
        info = self._bg_info()
        fg = self._fg_color()
        family = C.raw("fonts", "family") or "Microsoft YaHei UI"
        icons = {"mode": C.text("overlay_mode_both_text")}
        btns = []
        for b in self._buttons:
            item = {"id": b, "tooltip": C.text(_BTN_TOOLTIP.get(b, "")),
                    "enabled": True, "icon_key": b}
            if b == "mode":
                item.update(action="mode", danger=False)
            elif b == "close":
                # 复用 CustomTitleBar 内置关闭（危险红悬停 + window.close）
                item.update(action="close", danger=True)
                icons[b] = _BTN_ICON[b]
            else:
                item.update(action=b, danger=False)
                icons[b] = _BTN_ICON.get(b, "")
            btns.append(item)

        return {
            "window": {"title": self._title_text, "frameless": True},
            # 标题栏左侧品牌标识：复用主窗口 logo（yin-yang.svg），
            # 悬浮框无标题文字时由 logo 承载品牌，避免左侧空白失衡。
            "logo": _overlay_logo_cfg(),
            "titlebar": {
                "height": C.size("overlay_titlebar_h") or 34,
                "background": self._titlebar_bg(),
                "foreground": fg,
                "title_align": "left",
                "padding": [0, 0, 0, 0],
                "draggable": self._movable,
                # 顶边让位 = 0：标题栏不再 e.ignore 让位缩放，按钮上方整条（y 0 到按钮顶）都可拖。
                # 代价：顶部缩放完全失效（标题栏覆盖窗口顶部并截走事件，WindowResizer 收不到
                # 顶部 MouseButtonPress）。左/右/下边缘缩放（overlay_resize_margin=14）保留。
                "top_resize_margin": 0,
                # 按钮图标尺寸：跟随按钮高度自动缩（按钮高 22 → 图标 14，留 4px×2 内边距）。
                "button_icon_size": max((C.size("overlay_btn_h") or 26) - 8, 12),
            },
            "font": {
                "family": family,
                "size": max(self._font_size - 2, 9),
                "title_size": max(self._font_size - 1, 9),
                "button_size": max(self._font_size - 2, 9),
            },
            "icons": icons,
            "icons_tint": fg,   # 悬浮框按钮图标统一用自身前景色，避开主窗口全局染色
            "buttons": btns,
            "button_size": {"width": C.size("overlay_btn_w") or 34,
                            "height": C.size("overlay_btn_h") or 26},
            "colors": {
                "button_normal": "transparent",
                "button_hover": "#F1F4F9",
                "button_press": "#D8DFEA",
                "close_hover": "#FEE2E2",
                "close_press": "#FECACA",
                "content_bg": self._titlebar_bg(),
            },
            "tray": {"enabled": False},
        }

    def _titlebar_bg(self) -> str:
        """标题栏背景：透明模式用默认深灰，纯色模式与面板同色"""
        info = self._bg_info()
        if info["transparent"]:
            return C.color("overlay_default_bg") or "#1F2937"
        return info["panel_bg"]

    def _fg_color(self) -> str:
        """标题栏前景色（标题文字 / 按钮图标染色）"""
        info = self._bg_info()
        if info["transparent"]:
            return C.color("overlay_light_title") or "#E5E7EB"
        return (C.color("overlay_dark_title") or "#374151") if info["dark_text"] \
            else (C.color("overlay_light_title") or "#E5E7EB")

    def _custom_handlers(self):
        """自定义按钮 id → 处理器（close 为内置动作，不在此列）"""
        m = {
            "mode": self._toggle_mode,
            "pause": self._toggle_pause,
            "manual": self._manual_once,
            "retry": self._retry_once,
            "copy": self._copy_content,
            "pin": self._toggle_pin,
        }
        return [(b, m[b]) for b in self._buttons if b in m]

    def _find_btn(self, bid):
        """按 id 查找标题栏按钮（CustomTitleBar objectName = Btn_<id>）"""
        return self.findChild(QPushButton, f"Btn_{bid}")

    # ── 样式（透明/纯色背景，字号/配色全部来自 JSON）──

    def _bg_info(self):
        """返回背景信息：panel_bg / border / dark_text（文字用深色还是浅色）"""
        frame_w = int(C.size("overlay_frame_width"))
        if frame_w > 0:
            border = f"{frame_w}px solid {C.color('overlay_frame_color')}"
        else:
            border = "none"
        bg = self._bg_color
        if bg and bg != "transparent":
            c = QColor(str(bg))
            if not c.isValid():
                c = QColor(C.color("overlay_default_bg"))
            lum = 0.299 * c.red() + 0.587 * c.green() + 0.114 * c.blue()
            return dict(
                panel_bg=f"rgba({c.red()}, {c.green()}, {c.blue()}, 235)",
                border=border,       # 纯色背景：可见边框框体
                dark_text=lum > 150,
                transparent=False,
            )
        return dict(panel_bg="transparent", border=border,
                    dark_text=False, transparent=True)

    def _refresh_theme(self, force: bool = False):
        """主题刷新（步骤对齐 vertical_split_titlebar._refresh_theme）：

        Step 1) 自定义按钮图标染色 + panel/labels 样式表（仅在参数变化或 force=True）
        Step 2) 分栏面板背景（CustomTitleBar 自身配色由其 StyleHookMixin 接管）
        Step 3) overlay 专属：panel + labels + splitter handle 内联样式（参数化）
        Step 4) overlay 专属：透明模式的文字阴影

        `_apply_visuals(force=...)` 别名用于兼容（保留旧调用点；新代码请用
        `_refresh_theme`）。StyleHookMixin 在 StyleChange 时会调
        `_apply_inline_style()` → `_refresh_theme(force=True)`，与 v_st 的
        `THEME_BUS.changed → _refresh_theme()` 在效果上等价。
        """
        # ── Step 1: 缓存键 + 早退（参数未变且非 force）──
        info = self._bg_info()
        fs = self._font_size
        key = (self._bg_color, fs)
        if not force and key == self._visual_key:
            return
        self._visual_key = key

        # 调色：深色文字 vs 浅色文字
        if info["dark_text"]:
            pal = dict(orig=C.color("overlay_dark_orig"), trans=C.color("overlay_dark_trans"),
                       hint=C.color("overlay_dark_hint"))
        else:
            pal = dict(orig=C.color("overlay_light_orig"), trans=C.color("overlay_light_trans"),
                       hint=C.color("overlay_light_hint"))

        # ── Step 2: overlay 专属 panel + labels 内联样式（与 v_st 的 set_pane_style 对仗）──
        radius = C.size("overlay_panel_radius")
        self._panel.setStyleSheet(f"""
            #overlay_panel {{ background: {info['panel_bg']}; border: {info['border']};
                              border-radius: {radius}px; }}
        """)
        self._orig_label.setStyleSheet(
            f"color:{pal['orig']}; font-size:{max(fs - 1, 9)}px; background:transparent;")
        self._trans_label.setStyleSheet(
            f"color:{pal['trans']}; font-size:{fs}px; font-weight:600; background:transparent;")
        self._status_label.setStyleSheet(
            f"color:{pal['hint']}; font-size:{max(fs - 3, 8)}px; background:transparent;")

        # ── Step 3: splitter handle 配色（透明模式用半透明白细线，纯色模式用边框色）──
        if info["transparent"]:
            hc = "rgba(255,255,255,45)"
        else:
            hc = C.color("overlay_frame_color") or "#60A5FA"
        self._splitter.setStyleSheet(f"QSplitter::handle{{background:{hc};}}")

        # ── Step 4: 文字阴影（仅透明背景）──
        self._apply_shadows(info["transparent"])

    def _apply_inline_style(self):
        """StyleHookMixin 在主题切换时调用：强制重刷浮层配色（跳过脏检查）。

        对齐 vertical_split_titlebar._refresh_theme：换主题时重建样式表。
        """
        self._refresh_theme(force=True)

    # 兼容旧调用（保留 `_apply_visuals` 别名，新代码请用 `_refresh_theme`）
    def _apply_visuals(self, force: bool = False):
        """DEPRECATED 别名：见 ` _refresh_theme `。"""
        self._refresh_theme(force=force)

    def paintEvent(self, e):
        """纯色背景时铺满整个窗口（含外边距），保证全窗可命中。

        悬浮窗是分层窗口（WA_TranslucentBackground）：未绘制区域 alpha=0，
        Windows 上这些像素点击会穿透到下层窗口（主窗口）。当背景为纯色时，
        用与面板一致的颜色铺满整窗（圆角矩形保留圆角）：
          - 消除「可见框」外的透明缝隙；
          - 让拖动/缩放区（含外边距）全部落在本窗口上，
            不再误触发主窗口缩放。
        """
        info = self._bg_info()
        if not info["transparent"]:
            c = QColor(str(self._bg_color))
            if not c.isValid():
                c = QColor(C.color("overlay_default_bg"))
            c.setAlpha(235)
            p = QPainter(self)
            try:
                p.setRenderHint(QPainter.Antialiasing)
                p.setPen(Qt.NoPen)
                p.setBrush(c)
                radius = C.size("overlay_panel_radius")
                p.drawRoundedRect(self.rect(), radius, radius)
            finally:
                p.end()
        super().paintEvent(e)

    def _apply_shadows(self, enabled: bool):
        """文字阴影：仅透明背景需要"""
        for w in (self._orig_label, self._trans_label, self._status_label):
            if enabled:
                if w.graphicsEffect() is None:
                    eff = QGraphicsDropShadowEffect(w)
                    eff.setBlurRadius(6)
                    eff.setOffset(1, 1)
                    eff.setColor(QColor(0, 0, 0, 230))
                    w.setGraphicsEffect(eff)
            else:
                w.setGraphicsEffect(None)

    # ── 显示模式（双语 / 仅译文 / 纯文本）──

    def _apply_mode(self):
        """双语切换 = 收缩/展开上栏（原文）；仅译文/纯文本时上栏隐藏"""
        both = self._mode == "both"
        show_upper = both and self._show_orig
        if self.upper_visible != show_upper:
            if show_upper:
                self.upper_pane.show()
                if self._upper_sizes:
                    self._splitter.setSizes(self._upper_sizes)
            else:
                self._upper_sizes = self._splitter.sizes()
                self.upper_pane.hide()
            self.upper_visible = show_upper
        self._status_label.setVisible(self._show_status)
        btn = self._find_btn("mode")
        if btn is not None:
            txt = C.text("overlay_mode_both_text") if both else C.text("overlay_mode_trans_text")
            load_icon_for_button(btn, txt)
            btn.setToolTip(C.text("overlay_mode_both_tooltip") if both
                           else C.text("overlay_mode_trans_tooltip"))

    def _toggle_mode(self):
        self._mode = "trans" if self._mode == "both" else "both"
        self._apply_mode()
        self._fit_to_content()
        self.mode_changed.emit(self._mode == "both")

    def set_dual_mode(self, enabled: bool):
        """外部设置显示模式（True=双语 / False=仅译文）"""
        self._mode = "both" if enabled else "trans"
        self._apply_mode()
        self._fit_to_content()

    def set_show_orig(self, show: bool):
        """运行中切换是否显示原文行（上栏）"""
        self._show_orig = bool(show)
        self._apply_mode()
        self._fit_to_content()

    # ── 公共 API（与 vertical_split_titlebar 对齐）──
    def set_upper_content(self, widget):
        """替换上分区 body（对齐 v_st.set_upper_content）。"""
        self.upper_pane.set_body(widget)

    def set_lower_content(self, widget):
        """替换下分区 body（对齐 v_st.set_lower_content）。"""
        self.lower_pane.set_body(widget)

    # ── 按钮行为 ──

    def _copy_content(self):
        text = self._trans_label.text() or ""
        if text and text != "…":
            QApplication.clipboard().setText(text)
            self.set_status("内容已复制")
        else:
            self.set_status("暂无内容可复制")

    def _manual_once(self):
        self.set_status("识别中…")
        self.manual_clicked.emit()

    def _retry_once(self):
        self.set_status("执行中…")
        self.retry_clicked.emit()

    def _toggle_pause(self):
        self.set_paused(not self._paused)

    def set_paused(self, paused: bool):
        """设置暂停状态；True 停止实时触发，False 恢复"""
        paused = bool(paused)
        if paused == self._paused:
            return
        self._paused = paused
        btn = self._find_btn("pause")
        if btn is not None:
            load_titlebar_icon(btn,
                               "resources/icons/player-play.svg" if paused
                               else "resources/icons/player-pause.svg",
                               icon_size=20, tint=self._fg_color())
            btn.setToolTip(C.text("overlay_play_tooltip" if paused
                                  else "overlay_pause_tooltip"))
        self.pause_toggled.emit(self._paused)

    def is_paused(self) -> bool:
        return self._paused

    # ── 固定 / 锁定 ──

    def set_pinned(self, pinned: bool):
        """固定状态：True 锁定位置与大小（禁用拖动/缩放）"""
        self._pinned = bool(pinned)
        if self._resizer is not None:
            self._resizer.set_enabled(not self._pinned)
        if self._title_bar is not None:
            self._title_bar.cfg["titlebar"]["draggable"] = not self._pinned
        self._refresh_pin_btn()
        if self._pinned:
            self._user_sized = True
        else:
            # 解锁后恢复内容自适应（清除手动尺寸标记）
            self._user_sized = False
            self._fit_to_content()

    def is_pinned(self) -> bool:
        return self._pinned

    def _toggle_pin(self):
        self.set_pinned(not self._pinned)

    def _refresh_pin_btn(self):
        """按固定状态刷新固定按钮的高亮（来自 JSON 配置）"""
        btn = self._find_btn("pin")
        if btn is None:
            return
        btn.setToolTip(C.text("overlay_pinned_tooltip") if self._pinned
                       else C.text("overlay_pin_tooltip"))
        if self._pinned:
            btn.setStyleSheet(
                f"background: {C.color('overlay_pin_active_bg')}; "
                f"border-radius: {C.size('overlay_pin_border_radius')}px;")
        else:
            btn.setStyleSheet("")

    # ── 定位 / 尺寸自适应 ──

    def _apply_size(self, w: int, h: int):
        """程序化 resize（置位 _auto_sizing，避免误判为手动缩放）"""
        self._auto_sizing = True
        try:
            self.resize(w, h)
        finally:
            self._auto_sizing = False

    def resizeEvent(self, e):
        super().resizeEvent(e)
        prev = self._last_geo_size
        cur = (self.width(), self.height())
        self._last_geo_size = cur
        if not self._auto_sizing and not self._pinned \
                and prev is not None and prev != cur:
            # 用户手动缩放（resizer 拖拽）→ 记录，后续内容刷新不再覆盖尺寸
            self._user_sized = True

    def _apply_default_position(self):
        screen = QGuiApplication.primaryScreen()
        geo = screen.geometry() if screen else QRect(0, 0, 1920, 1080)
        w = C.size("overlay_default_w") or 420
        h = self._default_h
        self._apply_size(w, h)
        self.move(geo.right() - w - C.size("overlay_offset_gap"),
                  geo.top() + C.size("overlay_offset_gap"))

    def show_near(self, rect):
        """放置在给定区域下方（放不下则上方），尽量落在该区域内"""
        self._fit_to_content()
        screen = QGuiApplication.screenAt(rect.center()) or QGuiApplication.primaryScreen()
        geo = screen.geometry()
        x = rect.left()
        y = rect.bottom() + 8
        if y + self.height() > geo.bottom() - 8:
            y = rect.top() - self.height() - 8
        if y < geo.top() + 8:
            y = geo.top() + 8
        x = max(geo.left() + 8, min(x, geo.right() - self.width() - 8))
        self.move(x, y)

    def _clamp_on_screen(self):
        screen = QGuiApplication.screenAt(self.frameGeometry().center()) \
            or QGuiApplication.primaryScreen()
        geo = screen.geometry()
        x = min(self.x(), geo.right() - self.width() - 8)
        y = min(self.y(), geo.bottom() - self.height() - 8)
        self.move(max(x, geo.left() + 8), max(y, geo.top() + 8))

    def _set_labels_wrap(self, wrap: bool):
        for w in (self._orig_label, self._trans_label, self._status_label):
            w.setWordWrap(wrap)

    def _fit_to_content(self):
        """按内容自适应宽度；保持位置在屏幕内（固定状态除外）"""
        if self._pinned:
            return
        if self._user_sized:
            # 用户已手动调整过窗口大小：保持尺寸，仅确保换行
            self._set_labels_wrap(True)
            self._clamp_on_screen()
            return
        fm = self._trans_label.fontMetrics()
        text_w = max(
            fm.horizontalAdvance(self._trans_label.text()),
            self._orig_label.fontMetrics().horizontalAdvance(self._orig_label.text()),
            self._status_label.fontMetrics().horizontalAdvance(self._status_label.text()),
        )
        pad = C.size("overlay_margin_l") + C.size("overlay_margin_r")
        wrap = text_w > self._max_w - pad
        self._set_labels_wrap(wrap)
        if wrap:
            w = self._max_w
        else:
            w = max(C.size("overlay_min_w") or 160,
                    text_w + pad + (C.size("overlay_fit_gap") or 24))
        self._apply_size(w, max(self._default_h, self.height()))
        self._clamp_on_screen()

    def showEvent(self, e):
        """显示时主动置顶，避免被主窗口（激活后）盖在下面导致点击落空"""
        super().showEvent(e)
        self.raise_()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(e)

    def closeEvent(self, e):
        """关闭：通知应用停止（close_clicked → stop），并确保窗口一定关闭。

        标题栏内置关闭 / ESC / 应用 stop 都会走到这里；_close_emitted 保证
        每次生命周期内 close_clicked 只发出一次，避免递归 stop。
        """
        try:
            if not self._close_emitted:
                self._close_emitted = True
                self.close_clicked.emit()
        finally:
            super().closeEvent(e)

    # ── 内容更新 ──

    def set_result(self, orig: str, trans: str):
        """双语/翻译结果：显示原文（上栏）+ 译文（下栏）"""
        import datetime
        orig = (orig or "").strip()
        trans = (trans or "").strip()
        if orig:
            self._orig_label.setText(orig[:300])
        else:
            self._orig_label.setText("（未检测到文字）")
        self._trans_label.setText(trans if trans else "…")
        now = datetime.datetime.now().strftime("%H:%M:%S")
        if orig and trans:
            self._status_label.setText(now)
        elif orig:
            self._status_label.setText(f"识别到文字但翻译为空 · {now}")
        else:
            self._status_label.setText(f"（区域暂无文字）{now}")
        self._orig_label.setToolTip(orig)
        self._trans_label.setToolTip(trans)
        self._fit_to_content()

    def set_text(self, text: str):
        """纯文本结果（屏幕OCR / 屏幕字幕）"""
        import datetime
        text = (text or "").strip()
        self._orig_label.setText("")
        self._trans_label.setText(text if text else "…")
        self._status_label.setText(
            datetime.datetime.now().strftime("%H:%M:%S") if text else "（暂无内容）")
        self._trans_label.setToolTip(text)
        self._fit_to_content()

    def set_status(self, text: str):
        self._status_label.setText(text or "")

    # ── 区域框联动（可选）──

    def set_region_box(self, region_box):
        """绑定实时识别区域调整框（可选；有 region 按钮时可切换显示）"""
        self._region_box = region_box

    def toggle_region_box(self):
        box = self._region_box
        if box is None:
            return
        if box.isVisible():
            box.hide()
            self.set_status("区域调整框已隐藏")
        else:
            box.show()
            box.raise_()
            self.set_status("拖动框移动 · 拖四角/边缩放区域")


# --------------------------------------------------------------------------- #
#  主程序（直接运行本文件即可预览悬浮窗）
# --------------------------------------------------------------------------- #
def main():
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)

    ov = FloatingOverlay(
        buttons=["mode", "pause", "manual", "retry", "copy", "pin", "close"],
        title="悬浮窗演示",
        bg_color=None,   # 默认浅色；可试 "transparent"（透明）或 "#1F2937"（深蓝黑）
        font_size=14,
    )
    # 演示信号（业务应用中与各应用联动）
    ov.close_clicked.connect(lambda: print("[demo] close"))
    ov.copy_clicked.connect(lambda: print("[demo] copy"))
    ov.pause_toggled.connect(lambda p: print(f"[demo] pause={p}"))
    ov.mode_changed.connect(lambda b: print(f"[demo] mode_dual={b}"))
    ov.manual_clicked.connect(lambda: print("[demo] manual"))
    ov.retry_clicked.connect(lambda: print("[demo] retry"))

    # 填充示例内容（双语：上栏原文 / 下栏译文）
    ov.set_result(
        "Hello world! This is a sample sentence to demo the floating overlay.",
        "你好，世界！这是一条用于演示悬浮窗的示例译文。",
    )
    ov.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
