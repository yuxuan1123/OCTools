"""
OCTools/ui/tabs/translation/apps/speech_translate_app.py
──────────────────────────────────────────────────────
最终应用 · 语音翻译应用 = 实时语音翻译 + 悬浮显示框

按钮：双语 / 暂停 / 复制 / 固定 / 关闭（未选择的按钮自动隐藏）
流程：后台采集系统内置声音 → 定时语音识别 → 翻译为中文 →
悬浮显示框展示 原文 + 译文（双语可切换为仅译文）。
点击「暂停」停止定时识别（录音继续缓冲）；「固定」锁定窗口位置与大小
（固定后不可拖动/缩放，解锁恢复）；关闭即停止。

类 v_st 骨架（基类 TranslateAppBase 统一 `start()` 与 `stop()`）：

  按钮 = [mode, pause, copy, pin, close]，SHOW_ORIG = True（默认双语）。
  REQUIRES_REGION = False（语音类）。
  视觉覆写：_overlay_params 用 voice_sub_bg_color/font_size
  显示覆写：_apply_overlay_extra 用 voice_sub_show_orig 配置

子类声明差异 + 提供 3 个钩子方法：
  - _make_worker(rect)              → 返回 RealtimeSpeechTranslate
  - _install_overlay_signals        → pause_toggled → worker.set_paused
  - _initial_status / _log_started
"""

from ui.tabs.translation.apps.app_base import TranslateAppBase
from services.recipes.realtime_speech_translate import RealtimeSpeechTranslate

DEFAULT_INTERVAL_MS = 3000


class SpeechTranslateApp(TranslateAppBase):
    """语音翻译应用：录音 + 语音识别 + 文字翻译 → 双语字幕悬浮窗"""

    NAME = "语音翻译"
    BUTTONS = ["mode", "pause", "copy", "pin", "close"]
    SHOW_ORIG = True
    REQUIRES_REGION = False      # 语音类：没有截图区域
    USE_TRANSLATE = True         # 语音识别 + 翻译（识别 = 内置，翻译 = 服务）

    # ── 钩子方法（基类 start() 依次调）──

    def _install_overlay_signals(self, overlay):
        """pause 按钮 → _on_pause（控制 worker）"""
        return {"pause_toggled": self._on_pause}

    def _make_worker(self, rect):
        """worker = RealtimeSpeechTranslate（loopback 采内置声音，3s 一轮，识别+翻译）"""
        speech = RealtimeSpeechTranslate(
            direction=self.direction,
            interval_ms=DEFAULT_INTERVAL_MS,
            config=self.config(),
            stt_config=self.stt_config())
        speech.result_ready.connect(self._bridge.result_ready)
        speech.status.connect(self._bridge.status)
        speech.error.connect(self._on_error)
        return speech

    def _initial_status(self) -> str:
        return "⏳ 正在采集系统声音 / 加载模型…（首次约 30 秒）"

    def _log_started(self, rect):
        self.log(f"🎙️ {self.NAME}已启动（系统内置声音 → 中文字幕，"
                f"每 {DEFAULT_INTERVAL_MS // 1000}s 刷新）")

    # ── 回调（worker 由基类调度）──

    def _on_pause(self, paused: bool):
        if self._worker is not None:
            self._worker.set_paused(paused)

    def _on_error(self, err):
        # 基类默认行为：广播到悬浮框 + 写日志；子类直接 super() 复用
        super()._on_error(err)
