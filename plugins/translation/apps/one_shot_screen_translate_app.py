"""
OCTools/ui/tabs/translation/apps/one_shot_screen_translate_app.py
────────────────────────────────────────────────────────────
最终应用 · 一次性屏幕翻译应用 = 一次性屏幕翻译 + 悬浮显示框

按钮：双语 / 再次执行 / 复制 / 固定 / 关闭（未选择的按钮自动隐藏）
流程：框选区域（固定截图框优先）→ 截图 → OCR → 翻译 → 双语悬浮窗。
再次执行按钮：按同一区域重新截屏识别翻译；固定按钮：锁定/解锁窗口位置与大小；关闭即停止。

类 v_st 骨架（基类 TranslateAppBase 统一 `start()` 与 `stop()`）：

  按钮 = [mode, retry, copy, pin, close]，SHOW_ORIG = True（双语）。
  REQUIRES_REGION = True（截图类），USE_TRANSLATE = True（识别 + 翻译）。

子类只声明差异 + 提供 4 个钩子方法：
  - _install_overlay_signals  → retry_clicked → 基类 _run_once
  - _kick_off                 → 启动后立即 _run_once 一次（首轮）
  - _initial_status / _log_started

worker = None（一次性动作直接走基类 _run_once → _thread_ocr → _process_ocr_once）。
"""

from plugins.translation.apps.app_base import TranslateAppBase


class OneShotScreenTranslateApp(TranslateAppBase):
    """一次性屏幕翻译应用：截图 + 图像识别 + 文字翻译 → 双语悬浮窗"""

    NAME = "屏幕翻译"
    BUTTONS = ["mode", "retry", "copy", "pin", "close"]
    SHOW_ORIG = True
    REQUIRES_REGION = True
    USE_TRANSLATE = True      # 识别 + 翻译

    def _install_overlay_signals(self, overlay):
        """retry 按钮 → 基类 _run_once（截图→后台 OCR→翻译）"""
        return {"retry_clicked": self._run_once}

    def _kick_off(self):
        """启动首轮识别+翻译（复用基类 _run_once）"""
        self._run_once()

    def _initial_status(self) -> str:
        return "⏳ 正在加载 OCR / 翻译模型（首次约 30 秒）…"

    def _log_started(self, rect):
        self.log(f"🌐 {self.NAME}已启动（区域 {rect.width()}×{rect.height()}）")
