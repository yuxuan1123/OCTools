"""
OCTools/ui/tabs/translation/apps/screen_subtitle_app.py
─────────────────────────────────────────────────────
最终应用 · 屏幕字幕 = 内置语音识别 + 悬浮显示框

按钮：暂停 / 复制 / 固定 / 关闭（未选择的按钮自动隐藏）
流程：后台采集系统内置声音 → 定时语音识别 → 悬浮显示框更新纯文本字幕。
点击「暂停」停止定时识别（录音继续缓冲）；「复制」复制当前字幕；
「固定」锁定窗口位置与大小（固定后不可拖动/缩放，解锁恢复）。
悬浮窗背景 / 字号沿用「语音字幕」独立参数（voice_sub_bg_color / voice_sub_font_size）。
"""

from ui.tabs.translation.apps.app_base import TranslateAppBase
from services.recipes.builtin_speech_recognize import BuiltinSpeechRecognize

DEFAULT_INTERVAL_MS = 3000


class ScreenSubtitleApp(TranslateAppBase):
    """屏幕字幕应用：录音 + 语音识别 → 纯文本字幕悬浮窗"""

    NAME = "屏幕字幕"
    BUTTONS = ["pause", "copy", "pin", "close"]
    SHOW_ORIG = False

    def __init__(self, app, parent=None):
        super().__init__(app, parent)
        self._voice = None   # BuiltinSpeechRecognize

    # ── 悬浮窗视觉：沿用语音字幕独立参数 ──

    def _overlay_params(self) -> dict:
        p = super()._overlay_params()
        cfg = self.config()
        if cfg is None:
            return p
        p["bg_color"] = str(getattr(cfg, "voice_sub_bg_color", p["bg_color"])
                            or p["bg_color"])
        try:
            p["font_size"] = int(getattr(cfg, "voice_sub_font_size", p["font_size"])
                                 or p["font_size"])
        except (TypeError, ValueError):
            pass
        return p

    def start(self):
        if self.is_running():
            return
        self._overlay = self._create_overlay()
        self._overlay.pause_toggled.connect(self._on_pause)

        self._voice = BuiltinSpeechRecognize(
            mode="loopback", interval_ms=DEFAULT_INTERVAL_MS,
            stt_config=self.stt_config())
        self._voice.result_ready.connect(self._bridge.text_ready)
        self._voice.status.connect(self._bridge.status)
        self._voice.error.connect(self._on_error)

        self._overlay.show()
        self._overlay.set_status("⏳ 正在加载语音识别模型…（首次约 30 秒）")
        self.log(f"🎙️ 屏幕字幕已启动（系统内置声音，"
                f"每 {DEFAULT_INTERVAL_MS // 1000}s 刷新）")
        self._voice.start()

    def _on_pause(self, paused):
        if self._voice is not None:
            self._voice.set_paused(paused)

    def _on_error(self, err):
        self._bridge.status.emit(f"❌ {err}")
        self.log(f"❌ {self.NAME}: {err}")

    def stop(self):
        try:
            if self._voice is not None:
                self._voice.stop()
                self._voice = None
        finally:
            # 无论语音引擎停止是否异常，都确保悬浮窗关闭并复位按钮
            self._close_overlay()