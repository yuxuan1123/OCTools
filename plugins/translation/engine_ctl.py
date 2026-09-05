"""
OCTools/ui/tabs/translation/engine_ctl.py
───────────────────────────────────────────────────
翻译引擎（预选模型 + 参数）下拉控制：
  - refresh_tr_engine_combo(page)  按当前配置刷新「翻译引擎」下拉
  - on_tr_engine_selected(page,...) 下拉选择 → 更新引擎配置并持久化 + 刷新设置摘要
"""

from config import presets

from plugins.translation.registry import TR_ENGINE_LABELS, TR_ENGINE_ORDER


def refresh_tr_engine_combo(page):
    """刷新「翻译引擎」下拉，显示当前配置的引擎"""
    if page.tr_engine_combo is None:
        return
    cfg = getattr(page, "translator_config", None)
    if cfg is None:
        return
    page.tr_engine_combo.blockSignals(True)
    page.tr_engine_combo.clear()
    page.tr_engine_combo.addItems([TR_ENGINE_LABELS[e] for e in TR_ENGINE_ORDER])
    if cfg.engine in TR_ENGINE_ORDER:
        page.tr_engine_combo.setCurrentIndex(TR_ENGINE_ORDER.index(cfg.engine))
    else:
        page.tr_engine_combo.setCurrentIndex(0)
    page.tr_engine_combo.blockSignals(False)


def on_tr_engine_selected(page, index):
    """翻译引擎下拉选择 → 更新配置并持久化"""
    if 0 <= index < len(TR_ENGINE_ORDER):
        page.translator_config.engine = TR_ENGINE_ORDER[index]
        presets.save_last_translator_config(page.translator_config)
        page.log(f"🌐 翻译引擎: {TR_ENGINE_LABELS[page.translator_config.engine]}")
        page.refresh_settings_summaries()