"""
octool/ui/tabs/translation/apps/realtime_screen_translate_app.py
──────────────────────────────────────────────────────────────
最终应用 · 屏幕实时翻译应用 = 图翻译 + 悬浮显示框 + 自动区域截图

按钮：双语 / 暂停 / 手动翻译 / 复制 / 固定 / 关闭（未选择的按钮自动隐藏）
流程：
  1. 自动区域截图每 1 秒输出一帧（范围由用户框选）
  2. 每帧送入图翻译（图像识别 + 文字翻译）处理
  3. 结果推送到悬浮显示框更新显示
  4. 点击「暂停」停止定时触发；「手动翻译」立即执行一轮
  5. 「固定」锁定窗口位置与大小（固定后不可拖动/缩放，解锁恢复）
运行中可拖动 / 缩放区域调整框修改识别范围，修改后立即生效。
"""

import threading

from ui.tabs.translation.apps.app_base import TranslateAppBase
from services.recipes.auto_region_capture import AutoRegionCapture
from services.recipes.image_translate import recognize_translate

DEFAULT_INTERVAL_MS = 1000


class RealtimeScreenTranslateApp(TranslateAppBase):
    """屏幕实时翻译应用：定时自动区域截图 → 图翻译 → 悬浮窗更新"""

    NAME = "屏幕实时翻译"
    BUTTONS = ["mode", "pause", "manual", "copy", "pin", "close"]
    SHOW_ORIG = True

    def __init__(self, app, parent=None):
        super().__init__(app, parent)
        self._capture = None   # AutoRegionCapture

    def start(self):
        if self.is_running():
            return
        rect = self._resolve_region("屏幕实时翻译")
        if rect is None:
            return
        self._region = rect
        self._overlay = self._create_overlay()
        self._overlay.pause_toggled.connect(self._on_pause)
        self._overlay.manual_clicked.connect(self._manual_once)

        # 实时识别区域调整框：运行中可拖动/缩放修改识别范围
        self._region_box = self._make_region_box(rect)
        self._region_box.region_changed.connect(self._on_region_changed)
        self._region_box.show()
        self._region_box.raise_()
        self._overlay.set_region_box(self._region_box)

        # 定时自动区域截图（截图前自动隐藏悬浮框与区域框）
        self._capture = AutoRegionCapture(
            interval_ms=DEFAULT_INTERVAL_MS,
            exclude_widgets=[self._overlay, self._region_box])
        self._capture.frame.connect(self._on_frame)
        self._capture.start(rect)

        self._overlay.show()
        self._overlay.show_near(rect)
        self._overlay.set_status("⏳ 首次识别加载模型中…（约 30 秒，请稍候）")
        self.log(f"📺 屏幕实时翻译已启动（区域 {rect.width()}×{rect.height()}，"
                f"每 {DEFAULT_INTERVAL_MS // 1000}s 刷新）")

    # ── 悬浮窗按钮 ──

    def _on_region_changed(self, rect):
        """区域框变化 → 更新识别区域（定时截图下一帧立即生效）"""
        self._region = rect
        if self._capture is not None:
            self._capture.set_region(rect)

    def _on_pause(self, paused):
        """暂停 / 恢复 定时触发"""
        if self._capture is None:
            return
        if paused:
            self._capture.stop()
        else:
            try:
                self._capture.start()
            except ValueError:
                return
        if self._overlay is not None:
            self._overlay.set_status("⏸ 已暂停（点击 ▶ 继续）" if paused else "⏵ 运行中")

    def _manual_once(self):
        """手动翻译：暂停状态下也可立即执行一轮"""
        if self._capture is None:
            return
        if self._overlay is not None:
            self._overlay.set_status("识别中…")
        self._capture.capture_now()

    # ── 自动区域截图 → 图翻译 ──

    def _on_frame(self, rect, img):
        """主线程：收到定时帧 → 后台 图翻译（上一轮未完成则跳过）"""
        if self._busy:
            return
        self._busy = True
        threading.Thread(target=self._process_frame, args=(img,), daemon=True).start()

    def _process_frame(self, img):
        """工作线程：图像识别 + 文字翻译（不碰任何 Qt 控件）"""
        try:
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

    def stop(self):
        self._busy = False
        if self._capture is not None:
            self._capture.stop()
            self._capture = None
        self._close_region_box()
        self._close_overlay()