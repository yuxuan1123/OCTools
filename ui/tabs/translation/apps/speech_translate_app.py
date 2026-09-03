"""
octool/ui/tabs/translation/apps/speech_translate_app.py
──────────────────────────────────────────────────────
最终应用 · 语音翻译应用 = 实时语音翻译 + 悬浮显示框

按钮：双语 / 暂停 / 复制 / 固定 / 关闭（未选择的按钮自动隐藏）
流程：后台采集系统内置声音 → 定时语音识别 → 翻译为中文 →
悬浮显示框展示 原文 + 译文（双语可切换为仅译文）。
点击「暂停」停止定时识别（录音继续缓冲）；「固定」锁定窗口位置与大小
（固定后不可拖动/缩放，解锁恢复）；关闭即停止。
悬浮窗背景 / 字号沿用「语音字幕」独立参数（voice_sub_bg_color / voice_sub_font_size），
是否显示原文沿用 voice_sub_show_orig。
"""

from ui.tabs.translation.apps.app_base import TranslateAppBase
from services.recipes.realtime_speech_translate import RealtimeSpeechTranslate

DEFAULT_INTERVAL_MS = 3000


class SpeechTranslateApp(TranslateAppBase):
    """语音翻译应用：录音 + 语音识别 + 文字翻译 → 双语字幕悬浮窗"""

    NAME = "语音翻译"
    BUTTONS = ["mode", "pause", "copy", "pin", "close"]
    SHOW_ORIG = True

    def __init__(self, app, parent=None):
        super().__init__(app, parent)
        self._speech = None   # RealtimeSpeechTranslate

    # ── 悬浮窗视觉 / 内容：沿用语音字幕独立参数 ──

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

    def _apply_overlay_extra(self, overlay):
        cfg = self.config()
        if cfg is None:
            return
        try:
            show_orig = bool(getattr(cfg, "voice_sub_show_orig", self.SHOW_ORIG))
        except Exception:
            show_orig = self.SHOW_ORIG
        overlay.set_show_orig(show_orig)

    def start(self):
        if self.is_running():
            return
        self._overlay = self._create_overlay()
        self._overlay.pause_toggled.connect(self._on_pause)

        self._speech = RealtimeSpeechTranslate(
            direction=self.direction,
            interval_ms=DEFAULT_INTERVAL_MS,
            config=self.config(),
            stt_config=self.stt_config())
        self._speech.result_ready.connect(self._bridge.result_ready)
        self._speech.status.connect(self._bridge.status)
        self._speech.error.connect(self._on_error)

        self._overlay.show()
        self._overlay.set_status("⏳ 正在采集系统声音 / 加载模型…（首次约 30 秒）")
        self.log(f"🎙️ 语音翻译已启动（系统内置声音 → 中文字幕，"
                f"每 {DEFAULT_INTERVAL_MS // 1000}s 刷新）")
        self._speech.start()

    def _on_pause(self, paused):
        if self._speech is not None:
            self._speech.set_paused(paused)

    def _on_error(self, err):
        self._bridge.status.emit(f"❌ {err}")
        self.log(f"❌ {self.NAME}: {err}")

    def stop(self):
        try:
            if self._speech is not None:
                self._speech.stop()
                self._speech = None
        finally:
            # 无论语音引擎停止是否异常，都确保悬浮窗关闭并复位按钮
            self._close_overlay()