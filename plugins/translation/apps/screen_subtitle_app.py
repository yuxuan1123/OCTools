"""
OCTools/ui/tabs/translation/apps/screen_subtitle_app.py
─────────────────────────────────────────────────────
最终应用 · 屏幕字幕 = 内置语音识别 + 悬浮显示框

按钮：暂停 / 复制 / 固定 / 关闭（未选择的按钮自动隐藏）
流程：后台采集系统内置声音 → 定时语音识别 → 悬浮显示框更新纯文本字幕。
点击「暂停」停止定时识别（录音继续缓冲）；「复制」复制当前字幕；
「固定」锁定窗口位置与大小（固定后不可拖动/缩放，解锁恢复）。

类 v_st 骨架（基类 TranslateAppBase 统一 `start()` 与 `stop()`）：

  按钮 = [pause, copy, pin, close]，SHOW_ORIG = False（仅纯文本字幕）。
  REQUIRES_REGION = False（语音类，无需截图识别区域）。
  视觉覆写：_overlay_params 沿用「语音字幕」独立参数
            voice_sub_bg_color / voice_sub_font_size（CONFIG 已完备）。

子类声明差异 + 提供 3 个钩子方法：
  - _make_worker(rect)              → 返回 BuiltinSpeechRecognize
                                       （连 result_ready/status/error → bridge）
  - _install_overlay_signals        → pause_toggled → worker.set_paused
  - _initial_status / _log_started
"""

from plugins.translation.apps.app_base import TranslateAppBase
from services.recipes.builtin_speech_recognize import BuiltinSpeechRecognize

DEFAULT_INTERVAL_MS = 3000


class ScreenSubtitleApp(TranslateAppBase):
    """屏幕字幕应用：录音 + 语音识别 → 纯文本字幕悬浮窗"""

    NAME = "屏幕字幕"
    BUTTONS = ["pause", "copy", "pin", "close"]
    SHOW_ORIG = False
    REQUIRES_REGION = False      # 语音类：没有截图区域
    USE_TRANSLATE = False        # 仅识别不翻译

    # ── 钩子方法（基类 start() 依次调）──

    def _install_overlay_signals(self, overlay):
        """pause 按钮 → _on_pause（控制 worker）"""
        return {"pause_toggled": self._on_pause}

    def _make_worker(self, rect):
        """worker = BuiltinSpeechRecognize（loopback 模式采系统内置声音，3s 一轮）"""
        voice = BuiltinSpeechRecognize(
            mode="loopback", interval_ms=DEFAULT_INTERVAL_MS,
            stt_config=self.stt_config())
        voice.result_ready.connect(self._bridge.text_ready)
        voice.status.connect(self._bridge.status)
        voice.error.connect(self._on_error)
        return voice

    def _initial_status(self) -> str:
        return "⏳ 正在加载语音识别模型…（首次约 30 秒）"

    def _log_started(self, rect):
        self.log(f"🎙️ {self.NAME}已启动（系统内置声音，"
                f"每 {DEFAULT_INTERVAL_MS // 1000}s 刷新）")

    # ── 回调（worker 由基类调度）──

    def _on_pause(self, paused: bool):
        if self._worker is not None:
            self._worker.set_paused(paused)

    def _on_error(self, err):
        # 基类默认行为：广播到悬浮框 + 写日志；子类直接 super() 复用
        super()._on_error(err)
