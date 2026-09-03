"""
OCTools/ui/tabs/merge/target_ctl.py
─────────────────────────────────
目标格式（二级选择器）与预设区联动控制（拼接模式）：
  - reachable_targets / batch_reachable_targets / update_picker_available /
    select_format / refresh_target_combo
  - update_preset_area（md→docx / 图片→docx / TTS / STT / 占位 显隐）
  - 图片预设下拉 / 语音识别摘要 / docx 排版卡刷新

各函数第一个参数为 page（TabMerge），供回调传入 self。
跨模块联动统一通过 page 的委托方法（如 page._auto_fill_output()）进行，
避免 actions 与本模块产生循环导入。
"""

import os

from PySide6.QtWidgets import QMessageBox

from config import presets
from config.image_docx_config import ImageDocxConfig

from ui.tabs.merge.registry import (
    C, batch_api, _actual_ext, get_format_from_path,
    PRESET_NEW_OPTION, IMG_PRESET_DEFAULT_OPTION, STT_LANGUAGE_LABELS,
)


def reachable_targets(page, src_fmt):
    """按源格式返回可达的目标格式（拼接模式：合并为单个文件）"""
    available = []
    for f in page._format_list:
        if f == "pptx-img":
            continue                      # 图片版PPT 不支持拼接合并
        if f == "txt-ocr":
            if src_fmt in C.TXT_OCR_SOURCES:
                available.append(f)
            continue
        if batch_api.can_concat(src_fmt, f):
            available.append(f)
    return available


def batch_reachable_targets(page, src_fmt):
    """按源格式返回可达的目标格式（单文件：转换与拼接效果相同 → 按转换可达性过滤）"""
    available = []
    for f in page._format_list:
        if f == "pptx-img":
            if src_fmt == "pptx":
                available.append(f)
            continue
        if f == "txt-ocr":
            if src_fmt in C.TXT_OCR_SOURCES:
                available.append(f)
            continue
        if batch_api.can_batch(src_fmt, f):
            available.append(f)
    return available


def update_picker_available(page, formats):
    """更新二级选择器的可选格式；当前选中项不可用时清空选择"""
    page._available_list = list(formats)
    page.format_picker.set_available(formats)
    cur = page.selected_format
    if cur and cur in formats:
        page.format_picker.select(cur, emit=False)
    else:
        page.selected_format = ""
        page.format_picker.clear()


def select_format(page, fmt):
    """选中目标格式，并自动更新输出路径的扩展名"""
    page.selected_format = fmt
    page.format_picker.select(fmt, emit=False)

    src, src_fmt = page._effective_source()
    update_preset_area(page, src_fmt if src else "", fmt)

    # 多文件（源文件夹）：自动填充输出文件
    if page.folder_path.strip():
        page._auto_fill_output()
        return

    # ── 单文件模式：维持原有输出路径联动逻辑 ──
    out = page.output_entry.text().strip()

    # 文档（PDF/DOCX）→ 图片：按页输出到文件夹
    if src and src_fmt in ("pdf", "docx") and fmt in ("jpg", "jpeg", "png"):
        base = os.path.splitext(src)[0]
        folder_name = os.path.basename(base) + "_图片"
        if out and os.path.dirname(out):
            new_path = os.path.join(os.path.dirname(out), folder_name)
        else:
            new_path = base + "_图片"
        page.output_entry.setText(new_path)
        return

    actual_ext = _actual_ext(fmt)

    if src:
        base = os.path.splitext(src)[0]
        if not out:
            page.output_entry.setText(f"{base}.{actual_ext}")
        else:
            out_dir = os.path.dirname(out)
            out_name = os.path.basename(out)
            out_base = os.path.splitext(out_name)[0]
            new_name = f"{out_base}.{actual_ext}"
            new_path = os.path.join(out_dir, new_name) if out_dir else new_name
            page.output_entry.setText(new_path)


def refresh_target_combo(page):
    """按源（文件/文件夹）刷新「目标格式」的可选项"""
    folder = page.folder_path.strip()
    if folder:
        src_fmt = page.src_format
        if not src_fmt:
            update_picker_available(page, list(page._format_list))
            return
        avail = reachable_targets(page, src_fmt)
        update_picker_available(page, avail)
    else:
        f = page.input_path.strip()
        if not f:
            update_picker_available(page, list(page._format_list))
            return
        src_fmt = get_format_from_path(f)
        # 单文件：转换与拼接效果相同 → 按转换可达性过滤
        avail = batch_reachable_targets(page, src_fmt)
        update_picker_available(page, avail)


def update_preset_area(page, src_fmt, dst_fmt):
    """根据源格式 + 目标格式切换「预设选择」区"""
    show_tts = src_fmt in ("txt", "md") and (not dst_fmt or dst_fmt in C.AUDIO_FORMATS)
    show_preset = src_fmt == "md" and dst_fmt == "docx"
    show_img = src_fmt in C.IMAGE_FORMATS and dst_fmt == "docx"
    show_stt = src_fmt in C.AUDIO_FORMATS and dst_fmt == "txt"
    page.docx_card.setVisible(show_preset)
    page._img_row_w.setVisible(show_img)
    page._tts_row_w.setVisible(show_tts)
    page._stt_row_w.setVisible(show_stt)
    page._preset_none_label.setVisible(not (show_preset or show_img or show_tts or show_stt))
    if show_stt:
        refresh_stt_summary(page)


def refresh_stt_summary(page):
    """刷新「语音识别」行的当前配置摘要"""
    if page._stt_summary is None:
        return
    cfg = page.stt_config
    if cfg is None:
        return
    lang = dict(STT_LANGUAGE_LABELS).get(cfg.language, cfg.language)
    page._stt_summary.setText(
        f"模型: {os.path.basename(cfg.model_dir)} | 语言: {lang} | 设备: {cfg.device}")


def refresh_preset_combo(page):
    """刷新 MD→DOCX 排版卡片的配置同步"""
    if page.docx_card is None:
        return
    page.docx_card.set_config(page.current_config)


def on_docx_card_config_changed(page, config):
    """排版卡片配置变更回调：同步到全局 + 持久化 + 刷新"""
    page.current_config = config
    presets.save_last_config(config)
    page.refresh_settings_summaries()


def refresh_img_preset_combo(page):
    """刷新「图片预设」下拉：默认 + 全部图片预设名 + 「新增预设」入口"""
    names = presets.list_image_presets()
    page._img_preset_names = names
    if page.img_preset_combo is None:
        return
    page.img_preset_combo.blockSignals(True)
    page.img_preset_combo.clear()
    page.img_preset_combo.addItems([IMG_PRESET_DEFAULT_OPTION] + names + [PRESET_NEW_OPTION])
    page.img_preset_combo.setCurrentIndex(-1)
    page.img_preset_combo.blockSignals(False)


def on_img_preset_selected(page, index):
    """「图片预设」下拉回调"""
    if index < 0:
        return
    if index == 0:
        page.image_docx_config = ImageDocxConfig()
        presets.save_last_image_config(page.image_docx_config)
        page.log("💾 已恢复默认图片排版")
        page.img_preset_combo.blockSignals(True)
        page.img_preset_combo.setCurrentText(IMG_PRESET_DEFAULT_OPTION)
        page.img_preset_combo.blockSignals(False)
        page.refresh_settings_summaries()
        return
    if index == len(page._img_preset_names) + 1:
        page._open_image_docx_options()
        reset_img_preset_combo(page)
        return
    name = page._img_preset_names[index - 1]
    cfg = presets.load_image_preset(name)
    if cfg is None:
        QMessageBox.critical(page, "失败", f"无法加载图片预设: {name}")
        reset_img_preset_combo(page)
        return
    page.image_docx_config = cfg
    presets.save_last_image_config(cfg)
    page.log(f"💾 已加载图片预设: {name}")
    page.img_preset_combo.blockSignals(True)
    page.img_preset_combo.setCurrentText(name)
    page.img_preset_combo.blockSignals(False)
    page.refresh_settings_summaries()


def reset_img_preset_combo(page):
    """将「图片预设」下拉复位为未选择状态"""
    if page.img_preset_combo is None:
        return
    page.img_preset_combo.blockSignals(True)
    page.img_preset_combo.setCurrentIndex(-1)
    page.img_preset_combo.blockSignals(False)
