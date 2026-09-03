"""
octool/services/recipes/realtime_speech_translate.py
────────────────────────────────────────────────────────
拼接配方 · 实时语音翻译 = 录音 + 语音识别 + 文字翻译

纯逻辑拼接，不可增减功能：
  1. 录音（core/engines/audio_capture）持续采集系统内置声音
  2. 语音识别（core/engines/speech_engine）把音频转换为文本
  3. 文字翻译（core/engines/translation_engine）翻译识别文本

录音 + 定时缓冲识别逻辑复用 内置语音识别（builtin_speech_recognize），
仅追加文字翻译，不增减功能。

输出：result_ready(原文, 译文)，status 阶段反馈，error 异常。
运行中可暂停（set_paused）。不含任何 UI 控件。
"""

from PySide6.QtCore import Signal

from core.engines.speech_engine import transcribe_pcm16k
from core.engines.translation_engine import DIRECTION_LABELS, translate
from services.recipes.builtin_speech_recognize import (
    BuiltinSpeechRecognize,
    DEFAULT_INTERVAL_MS,
)


class RealtimeSpeechTranslate(BuiltinSpeechRecognize):
    """定时循环：后台录音 → 语音识别 → 翻译为中文"""

    # 覆盖父类 result_ready(str)：识别 + 翻译两段内容
    result_ready = Signal(str, str)

    def __init__(self, direction: str = "en2zh", interval_ms: int = DEFAULT_INTERVAL_MS,
                 config=None, stt_config=None, parent=None):
        super().__init__(mode="loopback", interval_ms=interval_ms,
                         stt_config=stt_config, parent=parent)
        if direction not in DIRECTION_LABELS:
            direction = "en2zh"
        self._direction = direction
        self._trans_config = config

    def set_direction(self, direction: str):
        """运行前/运行中切换翻译方向"""
        if direction in DIRECTION_LABELS:
            self._direction = direction

    # ── 覆盖：识别后追加翻译 ──

    def _process(self, data):
        """工作线程：语音识别 → 翻译 → 信号回传（不碰任何 Qt 控件）"""
        try:
            self.status.emit("⏳ 正在加载语音识别模型（首次约 20-30 秒）…")
            text = transcribe_pcm16k(
                data, log=lambda m: None, config=self._stt_config)
            if self._stopped:
                return
            if not text:
                self.status.emit("（未识别到有效语音）")
                return
            self.status.emit("⏳ 正在翻译…")
            trans = translate(text, self._direction,
                              config=self._trans_config) if text else ""
            if not self._stopped:
                self.result_ready.emit(text, trans)
        except RuntimeError:
            pass   # 控制器已被销毁（退出中），忽略跨线程回传
        except Exception as e:
            if not self._stopped:
                self.error.emit(str(e))
        finally:
            self._busy = False