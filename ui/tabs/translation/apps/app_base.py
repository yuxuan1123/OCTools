"""
OCTools/ui/tabs/translation/apps/app_base.py
──────────────────────────────────────────
最终应用 · 公共基类（挂载 UI）

各最终应用 = 拼接配方（services/recipes）+ 悬浮显示框
（ui/ui_component/overlay，**小号版 vertical_split_titlebar.VerticalWindow +
自定义按钮**）+ 区域框选（ui/ui_component/region_box，按需）。
本基类实现：
  - 区域选择（固定截图框优先，否则全屏框选；结果写回配置）
  - 悬浮显示框创建（`_create_overlay`：§ 1) 构造 → § 2) 接通用信号 →
    § 3) 应用已保存模式 → § 4) 钩子覆写）
  - 启动骨架 `start()`（对齐 vertical_split_titlebar.VerticalWindow 的"基类
    固定 4 步骨架，子类只填差异"模型）：
        §1) 防重入
        §2) 解析识别区域（语音类 REQUIRES_REGION=False 时跳过）
        §3) 创建悬浮框（委托 _create_overlay，§1-§4 内部步骤）
        §4) 接应用专属信号（子类 `_install_overlay_signals` 返回映射）
        §5) 创建额外非悬浮组件（子类 `_install_extra_widgets`，如 LiveRegionBox）
        §6) 创建 worker（子类 `_make_worker` 工厂）
        §7) 启动 worker
        §8) 立即触发（子类 `_kick_off`，一次性图像类的首次识别）
        §9) 显示 + 定位 + 初始状态 + 日志
  - 通用停止 `stop()`：停 worker → 关闭 extras → 关闭悬浮框
  - 实时识别区域调整框（LiveRegionBox）
  - 工作线程 → 主线程 的信号桥（OCR / 翻译等慢操作不卡 UI）
  - 通用停止 / 清理

业务逻辑本身在 services/recipes（纯逻辑），本层只做 UI 挂载与编排。

子类接口（按需提供 / 覆写，详见各 `apps/*.py`）：
  类属性：
    REQUIRES_REGION  bool  默认 True。语音字幕/语音翻译设为 False（无截图区）。
    USE_TRANSLATE    bool  默认 True。纯 OCR 应用（屏幕 OCR）设为 False。
    BUTTONS          list  按钮子集（驱动 _install_overlay_signals 的覆盖范围）
    SHOW_ORIG        bool  是否显示原文行（双语应用 True / 纯文本应用 False）
    OVERLAY_TITLE    str   悬浮窗左上角标题文本（默认空 = 不显示）
  方法：
    _make_worker(rect)                  工厂：返回 QObject worker（必须实现，
                                         默认 None = 不创建任何 worker，
                                         常见于"只在 _kick_off 触发一次性动作"的
                                         应用，如屏幕 OCR / 一次性屏幕翻译的
                                         直接调试场景）。
    _install_overlay_signals(overlay)   返回 {signal_attr_name: callback}
                                         映射，基类按映射逐个 connect。
                                         默认返回空 dict。
    _install_extra_widgets(rect)        返回 [widget, ...]，基类 show/raise_ 并
                                         在 stop() 时统一关闭。默认返回 []。
    _kick_off()                        worker 启动后的首轮动作（一次性图像类
                                         调 _run_once；其他应用默认空）。
    _initial_status()                  启动后悬浮框的初始状态文本。
    _log_started(rect)                启动后日志。

注：基类不约束 worker 类型 —— duck typing。worker 必须实现 `start(rect)` /
`stop()`；worker 与 bridge 的信号连接（result_ready / text_ready / status /
error）在子类的 `_make_worker` 内部完成（因为不同 worker 信号约定不同：
AutoRegionCapture 是 `frame(rect, img)`，语音类是 `result_ready/text_ready
+ status + error`）。
"""

import threading

from PySide6.QtCore import QObject, Signal

from ui.tabs.translation.apps.worker_bridge import _WorkerBridge
from ui.ui_component import window_ctl

from services.recipes.common import capture_excluded
from services.recipes.image_translate import recognize, recognize_translate


class TranslateAppBase(QObject):
    """翻译类最终应用基类。

    每个最终应用是"小号 vertical_split_titlebar.py + 自定义按钮"：复用
    `FloatingOverlay`（单标题栏 + 上下两栏 + WindowResizer + 自定义按钮 ID 子集）。
    子类通过 `BUTTONS` / `OVERLAY_TITLE` / `SHOW_ORIG` / `REQUIRES_REGION` /
    `USE_TRANSLATE` 类属性 + 5 个钩子方法控制外观和行为。
    """

    # 悬浮窗被关闭（用户点「关闭」或调用 stop）后发出，供页面行控制器复位按钮
    stopped = Signal()

    # ── 子类声明（按需覆写）──
    NAME = ""               # 悬浮窗内部名（日志 / 可访问性），不显示给用户
    OVERLAY_TITLE = ""      # 悬浮窗左上角标题文本：留空 → 不显示任何文字
    BUTTONS = []            # 悬浮窗按钮子集（由 `services/components/overlay` 恒定顺序排版）
    SHOW_ORIG = True        # 是否显示原文行（双语应用 True / 纯文本应用 False）
    REQUIRES_REGION = True  # 是否需要截图识别区域。语音类（subtitle / speech_translate）False
    USE_TRANSLATE = True    # 一次性图像应用相关。屏幕 OCR 设为 False（仅识别）

    def __init__(self, app, parent=None):
        super().__init__(parent)
        self._app = app
        self._overlay = None
        self._worker = None       # 子类 _make_worker() 返回的对象
        self._region_box = None   # _install_extra_widgets() 创建的额外组件代表
        self._extras = []         # 所有额外组件列表（stop 时统一关闭）
        self._region = None
        self._busy = False
        self._bridge = _WorkerBridge(self)
        self._bridge.text_ready.connect(self._on_text_ready)
        self._bridge.result_ready.connect(self._on_result_ready)
        self._bridge.status.connect(self._on_status)
        self._bridge.log_line.connect(self.log)

    # ════════════════════════════════════════════════════════════════════════════
    # 公共 API（应用控制器 / 按钮 / 热键 / 托盘菜单统一入口）
    # ════════════════════════════════════════════════════════════════════════════

    # ── 通用 ──

    def log(self, msg):
        try:
            self._app.log(msg)
        except Exception:
            print(msg)

    def config(self):
        """翻译配置（TranslatorConfig，含悬浮窗显示参数）"""
        return getattr(self._app, "translator_config", None)

    def stt_config(self):
        """语音识别配置（SttConfig）"""
        return getattr(self._app, "stt_config", None)

    def is_running(self) -> bool:
        return self._overlay is not None

    @property
    def direction(self) -> str:
        """翻译方向（与旧实现一致，默认 英 → 中；应用可覆写）"""
        return "en2zh"

    def start(self):
        """启动骨架（对齐 vertical_split_titlebar.VerticalWindow.__init__：
        基类固定步骤 + 子类 5 个钩子）。

          §1) 防重入：若已有悬浮框运行，直接返回
          §2) 解析识别区域（语音类 REQUIRES_REGION=False 跳过）
          §3) 创建悬浮显示框（构造 → 通用信号 → 模式持久化 → 钩子覆写）
          §4) 接应用专属 overlay 信号（子类 _install_overlay_signals 返回映射）
          §5) 创建额外非悬浮组件（子类 _install_extra_widgets，如 LiveRegionBox）
          §6) 创建 worker（子类 _make_worker 工厂，可选）
          §7) 启动 worker.start(rect)
          §8) 立即触发（子类 _kick_off：一次性图像类首次识别）
          §9) 显示 + 定位（识别区域附近）+ 初始状态 + 日志
        """
        # ── §1) 防重入 ──
        if self.is_running():
            return

        # ── §2) 解析识别区域（语音类跳过） ──
        rect = None
        if self.REQUIRES_REGION:
            rect = self._resolve_region(self.NAME)
            if rect is None:
                return
            self._region = rect

        # ── §3) 创建悬浮显示框（基类内部 § 1-§ 4：构造 → 信号 → 模式 → 钩子） ──
        self._overlay = self._create_overlay()

        # ── §4) 接应用专属 overlay 信号（子类 _install_overlay_signals 返回映射） ──
        try:
            hooks = self._install_overlay_signals(self._overlay) or {}
        except Exception as e:
            self.log(f"❌ {self.NAME}._install_overlay_signals 失败: {e}")
            hooks = {}
        for sig_attr, callback in hooks.items():
            sig = getattr(self._overlay, sig_attr, None)
            if sig is None or callback is None:
                continue
            try:
                sig.connect(callback)
            except Exception as e:
                self.log(f"❌ {self.NAME} 接 overlay.{sig_attr} 失败: {e}")

        # ── §5) 创建额外非悬浮组件（如实时翻译类的区域调整框） ──
        try:
            extras = self._install_extra_widgets(rect) or []
        except Exception as e:
            self.log(f"❌ {self.NAME}._install_extra_widgets 失败: {e}")
            extras = []
        self._extras = list(extras)

        # ── §5b) 显示额外组件（如实时翻译的区域调整框：置顶、可拖动/缩放） ──
        for w in self._extras:
            try:
                w.show()
                w.raise_()
            except Exception:
                pass

        # ── §6) 创建 worker（子类 _make_worker 工厂，可选） ──
        self._worker = self._make_worker(rect)

        # ── §7) 启动 worker ──
        if self._worker is not None and hasattr(self._worker, "start"):
            try:
                self._worker.start(rect)
            except Exception as e:
                self.log(f"❌ {self.NAME} worker.start 失败: {e}")
                self._cleanup()
                return

        # ── §8) 立即触发（子类 _kick_off：一次性图像类的首次识别） ──
        try:
            self._kick_off()
        except Exception as e:
            self.log(f"❌ {self.NAME}._kick_off 失败: {e}")

        # ── §9) 显示 + 定位 + 初始状态 + 日志 ──
        self._overlay.show()
        if rect is not None and hasattr(self._overlay, "show_near"):
            self._overlay.show_near(rect)
        self._overlay.set_status(self._initial_status())
        self._log_started(rect)

    def stop(self):
        """反向清理：停止 worker → 关闭 extras → 关闭悬浮框。

        骨架由基类统一负责；子类无需实现。
        幂等：未启动或已停止时调用为 no-op。"""
        if not self.is_running():
            # 已被 stop() 清理过（或 start() 中途失败）→ 安全返回
            if self._worker is not None:
                # 兜底：极端情况下 _worker 还在（如 start() §7 worker.start 抛错）
                try:
                    if hasattr(self._worker, "stop"):
                        self._worker.stop()
                except Exception:
                    pass
                self._worker = None
            return
        self._busy = False
        if self._worker is not None:
            try:
                if hasattr(self._worker, "stop"):
                    self._worker.stop()
            except Exception:
                pass
            self._worker = None
        if self._overlay is not None and hasattr(self._overlay, "set_region_box"):
            try:
                self._overlay.set_region_box(None)
            except Exception:
                pass
        self._region_box = None
        for w in self._extras:
            if w is None:
                continue
            try:
                w.close()
                w.deleteLater()
            except RuntimeError:
                pass
        self._extras = []
        self._close_overlay()

    # ════════════════════════════════════════════════════════════════════════════
    # 子类钩子（按需覆写；默认实现为安全空操作）
    # ════════════════════════════════════════════════════════════════════════════

    def _make_worker(self, rect):
        """工厂：返回 worker 对象（基类调 `worker.start(rect)` + `worker.stop()`）。

        worker 类型无约束（duck typing）：
          - 一次性图像类（screen_ocr / one_shot）默认不创建 worker → 返回 None
          - 实时图像类（realtime）返回 AutoRegionCapture 实例
          - 语音类（subtitle / speech_translate）返回语音引擎实例

        worker 与 bridge 的信号连接（result_ready / text_ready / status / error
        等）由子类在自己的实现中处理 —— 因为不同 worker 信号约定不同。
        """
        return None

    def _install_overlay_signals(self, overlay):
        """返回 overlay 信号 → 回调 方法的映射。

        例:
            return {
                "retry_clicked": self._on_retry,
                "pause_toggled": self._on_pause,
                "manual_clicked": self._on_manual,
            }

        基类按映射逐个 connect。默认返回空 dict（无应用专属信号）。
        """
        return {}

    def _install_extra_widgets(self, rect):
        """返回额外非悬浮组件列表（基类会 .show() / .raise_() 并在 stop 时统一关闭）。

        典型用例：实时翻译类的 LiveRegionBox（区域调整框）。

        默认返回 []。
        """
        return []

    def _kick_off(self):
        """worker 启动后的首轮动作（基类在 §8 调）。默认空操作。

        一次性图像类覆写：调 `self._run_once()` 触发首次截图+识别。
        """
        return None

    def _initial_status(self) -> str:
        """启动后悬浮框状态条首屏文本（基类在 §9 调）。默认通用提示。"""
        return f"⏳ 启动{self.NAME}…"

    def _log_started(self, rect):
        """启动后日志（基类在 §9 调）。默认格式。"""
        if rect is not None:
            self.log(f"▶ {self.NAME}已启动（区域 {rect.width()}×{rect.height()}）")
        else:
            self.log(f"▶ {self.NAME}已启动")

    # ════════════════════════════════════════════════════════════════════════════
    # 子类可覆写：一次性图像类的 _run_once（基类 _thread_ocr → _process_ocr_once）
    # ════════════════════════════════════════════════════════════════════════════

    # 兼容保留：供 ScreenOcrApp / OneShotScreenTranslateApp 的 _run_once 调用
    def _thread_ocr(self, img, use_translate: bool):
        """主线程调用：占用 _busy 并启动工作线程（不可重入）"""
        if self._busy:
            return
        self._busy = True
        threading.Thread(target=self._process_ocr_once,
                         args=(img, use_translate), daemon=True).start()

    def _process_ocr_once(self, img, use_translate: bool):
        """工作线程：屏幕OCR / 一次性屏幕翻译 的慢处理"""
        try:
            if not use_translate:
                self._bridge.status.emit("⏳ 正在加载 OCR 模型（首次约 20 秒）…")
                text = recognize(img)
                self._busy = False
                if self.is_running():
                    self._bridge.text_ready.emit(text)
                return
            self._bridge.status.emit("⏳ 正在加载 OCR / 翻译模型（首次约 30 秒）…")
            orig, trans = recognize_translate(img, self.direction,
                                              config=self.config())
            self._busy = False
            if self.is_running():
                self._bridge.result_ready.emit(orig, trans)
        except RuntimeError:
            self._busy = False
        except Exception as e:
            self._busy = False
            self._bridge.status.emit(f"❌ {e}")
            self.log(f"❌ {self.NAME}: {e}")

    # ════════════════════════════════════════════════════════════════════════════
    # 一次性图像类的 _run_once（基类提供复用实现，子类直接继承）
    # ════════════════════════════════════════════════════════════════════════════

    def _run_once(self, *_args):
        """一次性图像类：截图 → 后台识别+翻译（基类通用实现）。

        子类（如 ScreenOcrApp / OneShotScreenTranslateApp）的 _install_overlay_signals
        将 retry_clicked 连到这里。`use_translate` 来自子类的 `USE_TRANSLATE` 类属性。
        """
        if self._busy:
            if self._overlay is not None:
                self._overlay.set_status("处理中…")
            return
        img = self._capture_excluding()
        if img is None:
            if self._overlay is not None:
                self._overlay.set_status("❌ 截图失败")
            return
        self._thread_ocr(img, use_translate=self.USE_TRANSLATE)

    # ════════════════════════════════════════════════════════════════════════════
    # 区域选择 / 区域调整框
    # ════════════════════════════════════════════════════════════════════════════

    def _resolve_region(self, log_hint: str):
        """解析识别区域：固定截图框优先；否则全屏框选并写回配置。
        框选前最小化主窗口，之后永不恢复。"""
        from PySide6.QtCore import QRect

        # ★ 无论是否固定，先最小化主窗口（永不恢复）
        #   宿主是页面子控件，必须经 window_ctl 取顶层窗口；start_app 已调过一次，
        #   这里是直接调用 start() 时的兜底（已最小化则返回 False，不重复操作）。
        window_ctl.minimize_host(self._app)

        region = getattr(self._app, "screen_region_config", None)
        if region is not None and region.fixed and region.has_rect():
            x, y, w, h = region.rect_tuple()
            rect = QRect(x, y, w, h)
            self.log(f"📌 {log_hint}：使用固定截图框 ({x}, {y}) {w}×{h}")
            return rect   # 主窗口已最小化，直接返回

        from config.ui_config import CONFIG as C
        from ui.ui_component.region_box import RegionSelectDialog
        from PySide6.QtWidgets import QDialog

        border = region.border_color if region is not None else C.color("screen_border")
        dlg = RegionSelectDialog(border_color=border)
        self._app._region_dialog = dlg

        try:
            if dlg.exec() != QDialog.Accepted or dlg.selected_rect is None:
                self.log("⏹ 已取消区域选择")
                return None

            rect = dlg.selected_rect
            if region is not None:
                region.set_rect(rect.x(), rect.y(), rect.width(), rect.height())
                from config import presets
                presets.save_last_screen_region_config(region)
            return rect
        finally:
            if getattr(self._app, "_region_dialog", None) is dlg:
                self._app._region_dialog = None
            # ★ 绝不恢复主窗口
            # （用户需手动点击任务栏图标恢复）

    def _make_region_box(self, rect):
        """创建实时识别区域调整框（可拖动/缩放，变化经回调更新区域）"""
        from ui.ui_component.region_box import LiveRegionBox
        from config.screen_region_config import DEFAULT_BORDER_COLOR
        region = getattr(self._app, "screen_region_config", None)
        border = getattr(region, "border_color", DEFAULT_BORDER_COLOR) or DEFAULT_BORDER_COLOR
        return LiveRegionBox(rect, border_color=border)

    # ════════════════════════════════════════════════════════════════════════════
    # 悬浮显示框（构造 + 通用信号 + 模式持久化）
    # ════════════════════════════════════════════════════════════════════════════

    def _overlay_params(self) -> dict:
        """悬浮框参数：背景 / 字号 / 可拖动 / 可缩放 / 默认固定，来自翻译配置。
        背景默认 None → 由 FloatingOverlay 回落为 JSON 浅色默认；配置显式指定
        "transparent" 或 #RRGGBB 时按原值。"""
        cfg = self.config()
        params = dict(bg_color=None, font_size=14,
                      movable=True, resizable=True, pinned_default=False)
        if cfg is not None:
            bg = getattr(cfg, "overlay_bg_color", None)
            params["bg_color"] = str(bg) if bg else None
            try:
                params["font_size"] = int(getattr(cfg, "overlay_font_size", 14) or 14)
            except (TypeError, ValueError):
                params["font_size"] = 14
            params["movable"] = bool(getattr(cfg, "overlay_movable", True))
            params["resizable"] = bool(getattr(cfg, "overlay_resizable", True))
            params["pinned_default"] = bool(getattr(cfg, "overlay_pin_default", False))
        params["font_size"] = max(8, min(24, params["font_size"]))
        return params

    def _create_overlay(self, title: str = None):
        """创建悬浮显示框并接通通用信号（关闭 / 复制 / 模式切换持久化）

        步骤对齐 `FloatingOverlay._build_ui` 与 `vertical_split_titlebar.VerticalWindow.__init__`：
          §1) 构造悬浮框（参数来自 `_overlay_params()` + 类属性
              `BUTTONS` / `SHOW_ORIG` / `OVERLAY_TITLE`）
          §2) 接通用信号（close → `self.stop`；mode_changed → `_on_mode_changed`）
          §3) 应用已保存的显示模式（双语 / 仅译文），与 v_st 启动即按当前主题着色对称
          §4) 应用可覆写钩子（`_apply_overlay_extra`，子类自定义视觉/内容）

        title 缺省用 `self.OVERLAY_TITLE`（默认空字符串）→ 悬浮窗标题栏不显示
        文字，左侧由 logo（_titlebar_config 注入）承载品牌标识。
        """
        # ── §1) 构造悬浮框（参数：_overlay_params 解析配置 + 类属性提供内容/外观形态）──
        from ui.ui_component.overlay import FloatingOverlay
        p = self._overlay_params()
        overlay = FloatingOverlay(
            buttons=list(self.BUTTONS),
            title=title if title is not None else self.OVERLAY_TITLE,
            show_orig=self.SHOW_ORIG,
            show_status=True,
            bg_color=p["bg_color"],
            font_size=p["font_size"],
            movable=p["movable"],
            resizable=p["resizable"],
            pinned_default=p["pinned_default"],
        )

        # ── §2) 接通用信号（关闭 → 触发本应用 stop；模式切换 → 持久化翻译配置）──
        overlay.close_clicked.connect(self.stop)
        overlay.mode_changed.connect(self._on_mode_changed)

        # ── §3) 应用已保存的显示模式（双语 / 仅译文），与 v_st 的『启动即着色』对称 ──
        cfg = self.config()
        if cfg is not None and hasattr(cfg, "overlay_mode"):
            try:
                overlay.set_dual_mode(getattr(cfg, "overlay_mode", "both") != "trans")
            except Exception:
                pass

        # ── §4) 应用可覆写钩子（子类追加应用专属视觉/内容参数，留空则跳过）──
        self._apply_overlay_extra(overlay)
        return overlay

    def _apply_overlay_extra(self, overlay):
        """应用可覆写：悬浮窗创建后追加应用专属视觉/内容参数"""

    def _on_mode_changed(self, both: bool):
        """悬浮窗上切换 双语/仅译文 → 持久化翻译配置"""
        cfg = self.config()
        if cfg is None:
            return
        try:
            cfg.overlay_mode = "both" if both else "trans"
            from config import presets
            presets.save_last_translator_config(cfg)
        except Exception:
            pass
        self.log(f"🖥️ {self.NAME} 显示模式: {'双语（原文+译文）' if both else '仅译文'}")

    # ════════════════════════════════════════════════════════════════════════════
    # 信号桥 → 界面（主线程）
    # ════════════════════════════════════════════════════════════════════════════

    def _on_text_ready(self, text):
        if self._overlay is not None:
            self._overlay.set_text(text)

    def _on_result_ready(self, orig, trans):
        if self._overlay is not None:
            self._overlay.set_result(orig, trans)

    def _on_status(self, text):
        if self._overlay is not None:
            self._overlay.set_status(text)

    def _on_error(self, err):
        """默认错误处理：广播到悬浮框 + 写日志。
        语音类（subtitle / speech_translate）用此默认实现，不再各自重复。"""
        if self._overlay is not None:
            self._overlay.set_status(f"❌ {err}")
        self.log(f"❌ {self.NAME}: {err}")

    # ════════════════════════════════════════════════════════════════════════════
    # 清理
    # ════════════════════════════════════════════════════════════════════════════

    def _cleanup(self):
        """启动失败时的兜底清理：仅清空 self，关联资源由 stop() / GC 回收"""
        self._worker = None
        self._extras = []
        self._region = None
        self._overlay = None

    def _close_overlay(self):
        """关闭悬浮框并清理引用。

        注意：**不要**调 `self._overlay.close()`，因为 `FloatingOverlay.closeEvent`
        会 emit `close_clicked` → 又触发 `self.stop()` 同步递归。直接 deleteLater
        清理即可。`closeEvent` 仍正常 emit → 应用层 stop() 会触发同样的清理。
        """
        if self._overlay is None:
            return
        ov = self._overlay
        self._overlay = None
        try:
            ov.deleteLater()
        except RuntimeError:
            pass
        try:
            self.stopped.emit()   # 悬浮窗已关闭（用户点✕ / 调用 stop）
        except RuntimeError:
            pass

    def _close_region_box(self):
        """保留兼容名（实时翻译类仍可能单独调用）；新代码用 stop() 统一清理"""
        if self._region_box is not None:
            try:
                self._region_box.close()
                self._region_box.deleteLater()
            except RuntimeError:
                pass
            self._region_box = None

    def _capture_excluding(self):
        """截图前隐藏悬浮框/区域框，返回 PIL Image（主窗口已在框选时最小化）"""
        from PySide6.QtCore import QTimer, QEventLoop
        from PySide6.QtWidgets import QApplication
        from core.engines.screenshot_engine import grab_region

        # 兜底：确认主窗口真的缩下去了，否则会把自己拍进截图里
        window_ctl.ensure_minimized(self._app)

        # 隐藏子组件（悬浮框、区域框、额外组件）
        exclude_widgets = [self._overlay, self._region_box, *self._extras]
        vis = [w for w in exclude_widgets if w is not None and w.isVisible()]
        for w in vis:
            w.hide()
        QApplication.processEvents()

        result = [None]
        loop = QEventLoop()

        def _grab():
            img = grab_region(self._region)
            result[0] = img
            # 仅恢复子组件，主窗口保持最小化
            for w in vis:
                w.show()
            loop.quit()

        QTimer.singleShot(window_ctl.capture_delay_ms(), _grab)
        loop.exec()
        return result[0]
