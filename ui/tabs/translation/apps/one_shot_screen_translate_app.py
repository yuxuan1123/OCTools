"""
octool/ui/tabs/translation/apps/one_shot_screen_translate_app.py
────────────────────────────────────────────────────────────
最终应用 · 一次性屏幕翻译应用 = 一次性屏幕翻译 + 悬浮显示框

按钮：双语 / 再次执行 / 复制 / 固定 / 关闭（未选择的按钮自动隐藏）
流程：框选区域（固定截图框优先）→ 截图 → OCR → 翻译 → 双语悬浮窗。
再次执行按钮：按同一区域重新截屏识别翻译；固定按钮：锁定/解锁窗口位置与大小；关闭即停止。
"""

from ui.tabs.translation.apps.app_base import TranslateAppBase


class OneShotScreenTranslateApp(TranslateAppBase):
    """一次性屏幕翻译应用：截图 + 图像识别 + 文字翻译 → 双语悬浮窗"""

    NAME = "屏幕翻译"
    BUTTONS = ["mode", "retry", "copy", "pin", "close"]
    SHOW_ORIG = True

    def start(self):
        if self.is_running():
            return
        rect = self._resolve_region("屏幕翻译")
        if rect is None:
            return
        self._region = rect
        self._overlay = self._create_overlay()
        self._overlay.retry_clicked.connect(self._run_once)
        self._overlay.show()
        self._overlay.show_near(rect)
        self._overlay.set_status("⏳ 正在加载 OCR / 翻译模型（首次约 30 秒）…")
        self.log(f"🌐 屏幕翻译已启动（区域 {rect.width()}×{rect.height()}）")
        self._run_once()

    def _run_once(self, *_args):
        """主线程：截图 → 后台 识别+翻译（上一轮未完成则跳过）"""
        if self._busy:
            if self._overlay is not None:
                self._overlay.set_status("处理中…")
            return
        img = self._capture_excluding()
        if img is None:
            if self._overlay is not None:
                self._overlay.set_status("❌ 截图失败")
            return
        self._thread_ocr(img, use_translate=True)

    def stop(self):
        self._busy = False
        self._close_overlay()