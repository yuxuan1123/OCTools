"""
OCTools/ui/tabs/translation/apps/app_base.py
──────────────────────────────────────────
最终应用 · 公共基类（挂载 UI）

各最终应用 = 拼接配方（services/recipes）+ 悬浮显示框
（services/components/overlay）+ 区域框选（services/components/region_box，按需）。
本基类集中实现：
  - 区域选择（固定截图框优先，否则全屏框选；结果写回配置）
  - 悬浮显示框创建（按钮/背景/字号/固定等参数按需传入，读 UI JSON 配置）
  - 实时识别区域调整框（LiveRegionBox）
  - 工作线程 → 主线程 的信号桥（OCR / 翻译等慢操作不卡 UI）
  - 通用停止 / 清理

业务逻辑本身在 services/recipes（纯逻辑），本层只做 UI 挂载与编排。
"""

import threading

from PySide6.QtCore import QObject, Signal

from ui.tabs.translation.apps.worker_bridge import _WorkerBridge

from services.recipes.common import capture_excluded
from services.recipes.image_translate import recognize, recognize_translate


class TranslateAppBase(QObject):
    """翻译类最终应用基类"""

    # 悬浮窗被关闭（用户点「关闭」或调用 stop）后发出，供页面行控制器复位按钮
    stopped = Signal()

    NAME = ""               # 悬浮窗标题
    BUTTONS = []            # 悬浮窗按钮子集（由 `services/components/overlay` 恒定顺序排版）
    SHOW_ORIG = True        # 是否显示原文行（双语应用 True / 纯文本应用 False）

    def __init__(self, app, parent=None):
        super().__init__(parent)
        self._app = app
        self._overlay = None
        self._region_box = None
        self._region = None
        self._busy = False
        self._bridge = _WorkerBridge(self)
        self._bridge.text_ready.connect(self._on_text_ready)
        self._bridge.result_ready.connect(self._on_result_ready)
        self._bridge.status.connect(self._on_status)
        self._bridge.log_line.connect(self.log)

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
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    # ── 区域选择 / 区域框 ──

    def _resolve_region(self, log_hint: str):
        """解析识别区域（QRect 或 None）：
        固定截图框优先；否则全屏框选并写回配置。框选期间隐藏主窗口。"""
        from PySide6.QtCore import QRect
        region = getattr(self._app, "screen_region_config", None)
        if region is not None and region.fixed and region.has_rect():
            x, y, w, h = region.rect_tuple()
            rect = QRect(x, y, w, h)
            self.log(f"📌 {log_hint}：使用固定截图框 ({x}, {y}) {w}×{h}")
            return rect

        from config.ui_config import CONFIG as C
        was_visible = self._app.isVisible()
        if was_visible:
            self._app.hide()
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
            if was_visible:
                self._app.show()

    def _make_region_box(self, rect):
        """创建实时识别区域调整框（可拖动/缩放，变化经回调更新区域）"""
        from ui.ui_component.region_box import LiveRegionBox
        from config.screen_region_config import DEFAULT_BORDER_COLOR
        region = getattr(self._app, "screen_region_config", None)
        border = getattr(region, "border_color", DEFAULT_BORDER_COLOR) or DEFAULT_BORDER_COLOR
        return LiveRegionBox(rect, border_color=border)

    # ── 悬浮显示框 ──

    def _overlay_params(self) -> dict:
        """悬浮框参数：背景 / 字号 / 可拖动 / 可缩放 / 默认固定，来自翻译配置。
        背景默认 None → 由 FloatingOverlay 回落为 JSON 浅色默认；配置显式指定
        "transparent" 或 #RRGGBB 时按原值。"""
        cfg = self.config()
        params = dict(bg_color=None, font_size=12,
                      movable=True, resizable=True, pinned_default=False)
        if cfg is not None:
            bg = getattr(cfg, "overlay_bg_color", None)
            params["bg_color"] = str(bg) if bg else None
            try:
                params["font_size"] = int(getattr(cfg, "overlay_font_size", 12) or 12)
            except (TypeError, ValueError):
                params["font_size"] = 12
            params["movable"] = bool(getattr(cfg, "overlay_movable", True))
            params["resizable"] = bool(getattr(cfg, "overlay_resizable", True))
            params["pinned_default"] = bool(getattr(cfg, "overlay_pin_default", False))
        params["font_size"] = max(8, min(24, params["font_size"]))
        return params

    def _create_overlay(self, title: str = None):
        """创建悬浮显示框并接通通用信号（关闭 / 复制 / 模式切换持久化）"""
        from ui.ui_component.overlay import FloatingOverlay
        p = self._overlay_params()
        overlay = FloatingOverlay(
            buttons=list(self.BUTTONS),
            title=title if title is not None else self.NAME,
            show_orig=self.SHOW_ORIG,
            show_status=True,
            bg_color=p["bg_color"],
            font_size=p["font_size"],
            movable=p["movable"],
            resizable=p["resizable"],
            pinned_default=p["pinned_default"],
        )
        overlay.close_clicked.connect(self.stop)
        overlay.mode_changed.connect(self._on_mode_changed)
        # 应用已保存的显示模式（双语 / 仅译文）
        cfg = self.config()
        if cfg is not None and hasattr(cfg, "overlay_mode"):
            try:
                overlay.set_dual_mode(getattr(cfg, "overlay_mode", "both") != "trans")
            except Exception:
                pass
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

    # ── 信号桥 → 界面（主线程）──

    def _on_text_ready(self, text):
        if self._overlay is not None:
            self._overlay.set_text(text)

    def _on_result_ready(self, orig, trans):
        if self._overlay is not None:
            self._overlay.set_result(orig, trans)

    def _on_status(self, text):
        if self._overlay is not None:
            self._overlay.set_status(text)

    # ── 后台处理（慢操作在工作线程）──

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

    def _thread_ocr(self, img, use_translate: bool):
        """主线程调用：占用 _busy 并启动工作线程（不可重入）"""
        if self._busy:
            return
        self._busy = True
        threading.Thread(target=self._process_ocr_once,
                         args=(img, use_translate), daemon=True).start()

    # ── 清理 ──

    def _close_overlay(self):
        if self._overlay is not None:
            try:
                self._overlay.close()
                self._overlay.deleteLater()
            except RuntimeError:
                pass
            self._overlay = None
            self.stopped.emit()   # 悬浮窗已关闭（用户点✕ / 调用 stop）

    def _close_region_box(self):
        if self._region_box is not None:
            try:
                self._region_box.close()
                self._region_box.deleteLater()
            except RuntimeError:
                pass
            self._region_box = None

    def _capture_excluding(self):
        """截图前隐藏悬浮框与区域框，返回截取的 PIL Image"""
        return capture_excluded([self._overlay, self._region_box], self._region)