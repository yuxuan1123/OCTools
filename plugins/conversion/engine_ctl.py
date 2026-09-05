"""
OCTools/ui/tabs/conversion/engine_ctl.py
────────────────────────────────────────
TTS 语音引擎下拉控制（txt/md → 音频）：
  - refresh_tts_engine_combo(page)   按当前配置刷新「语音引擎」下拉
  - on_tts_engine_selected(page, i)  下拉选择 → 更新配置并持久化 + 刷新设置摘要
"""

from config import presets

from plugins.conversion.registry import TTS_ENGINE_LABELS, TTS_ENGINE_ORDER


def refresh_tts_engine_combo(page):
    """刷新「语音引擎」下拉，显示当前配置的引擎"""
    if page.tts_engine_combo is None:
        return
    page.tts_engine_combo.blockSignals(True)
    labels = [TTS_ENGINE_LABELS[e] for e in TTS_ENGINE_ORDER]
    page.tts_engine_combo.clear()
    page.tts_engine_combo.addItems(labels)
    eng = page.tts_config.engine
    if eng in TTS_ENGINE_ORDER:
        page.tts_engine_combo.setCurrentIndex(TTS_ENGINE_ORDER.index(eng))
    else:
        page.tts_engine_combo.setCurrentIndex(0)
    page.tts_engine_combo.blockSignals(False)


def on_tts_engine_selected(page, index):
    """语音引擎下拉选择 → 更新配置并持久化"""
    if 0 <= index < len(TTS_ENGINE_ORDER):
        page.tts_config.engine = TTS_ENGINE_ORDER[index]
        presets.save_last_tts_config(page.tts_config)
        page.log(f"🎙️ 语音引擎: {TTS_ENGINE_LABELS[page.tts_config.engine]}")
        page.refresh_settings_summaries()
