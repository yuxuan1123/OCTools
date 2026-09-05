"""
OCTools/ui/tabs/translation/apps/realtime_screen_translate_app.py
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

类 v_st 骨架（基类 TranslateAppBase 统一 `start()` 与 `stop()`）：

  按钮 = [mode, pause, manual, copy, pin, close]，SHOW_ORIG = True（双语）。
  REQUIRES_REGION = True（截图类）。

子类声明差异 + 提供 5 个钩子方法：
  - _make_worker(rect)              → 返回 AutoRegionCapture（连 frame→_on_frame）
  - _install_extra_widgets(rect)    → 返回 [LiveRegionBox]（连 region_changed→回调）
  - _install_overlay_signals        → pause_toggled / manual_clicked → 回调
  - _initial_status / _log_started

worker = AutoRegionCapture；extras = LiveRegionBox。
"""

import threading

from PySide6.QtCore import QObject, Signal

from ui.tabs.translation.apps.app_base import TranslateAppBase
from services.recipes.auto_region_capture import AutoRegionCapture
from services.recipes.image_translate import recognize_translate

DEFAULT_INTERVAL_MS = 1000


class RealtimeScreenTranslateApp(TranslateAppBase):
    """屏幕实时翻译应用：定时自动区域截图 → 图翻译 → 悬浮窗更新"""

    NAME = "屏幕实时翻译"
    BUTTONS = ["mode", "pause", "manual", "copy", "pin", "close"]
    SHOW_ORIG = True
    REQUIRES_REGION = True
    USE_TRANSLATE = True      # 实时识别 + 翻译

    # ── 钩子方法（基类 start() 依次调：_install_overlay_signals → _install_extra_widgets → _make_worker）──

    def _install_overlay_signals(self, overlay):
        """pause / manual 按钮 → 回调（worker 本身不在此创建）"""
        return {
            "pause_toggled": self._on_pause,
            "manual_clicked": self._on_manual,
        }

    def _install_extra_widgets(self, rect):
        """LiveRegionBox：实时识别区域调整框（运行中可拖动 / 缩放）"""
        box = self._make_region_box(rect)
        box.region_changed.connect(self._on_region_changed)
        # 让悬浮框在「按区域」时同步跟随收放
        self._overlay.set_region_box(box)
        # 基类会保存到 self._extras；stop 时统一关闭
        # 这里同时赋值 self._region_box，_make_worker 用作 exclude_widgets
        self._region_box = box
        return [box]

    def _make_worker(self, rect):
        """worker = AutoRegionCapture；截图前自动隐藏悬浮框与区域框"""
        capture = AutoRegionCapture(
            interval_ms=DEFAULT_INTERVAL_MS,
            exclude_widgets=[self._overlay, self._region_box])
        capture.frame.connect(self._on_frame)
        return capture

    def _initial_status(self) -> str:
        return "⏳ 首次识别加载模型中…（约 30 秒，请稍候）"

    def _log_started(self, rect):
        self.log(f"📺 {self.NAME}已启动（区域 {rect.width()}×{rect.height()}，"
                f"每 {DEFAULT_INTERVAL_MS // 1000}s 刷新）")

    # ── 回调（worker / extras 由基类调度）──

    def _on_pause(self, paused: bool):
        """pause 按钮：暂停 / 恢复 定时触发"""
        if self._worker is None:
            return
        if paused:
            self._worker.stop()
        else:
            try:
                self._worker.start()
            except ValueError:
                return
        if self._overlay is not None:
            self._overlay.set_status("⏸ 已暂停（点击 ▶ 继续）" if paused else "⏵ 运行中")

    def _on_manual(self):
        """manual 按钮：立即触发一帧（暂停状态下也可生效）"""
        if self._worker is None:
            return
        if self._overlay is not None:
            self._overlay.set_status("识别中…")
        self._worker.capture_now()

    def _on_region_changed(self, rect):
        """LiveRegionBox 拖动 / 缩放 → 更新识别区域（worker 下一帧立即生效）"""
        self._region = rect
        if self._worker is not None:
            self._worker.set_region(rect)

    def _on_frame(self, rect, img):
        """主线程：worker 定时帧 → 后台图翻译（上一轮未完成则跳过）"""
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
