"""
OCTools/ui/tabs/conversion/actions.py
────────────────────────────────────
转换页的交互动作与状态联动：
  - 浏览源文件 / 源文件夹 / 输出文件夹
  - 源路径手动编辑 / 源文件格式选择
  - 输出状态联动 / 自动填充输出路径
  - 选项弹窗（格式面板 / TTS / STT / 图片→docx 预设）

各函数第一个参数为 page（TabConversion），供回调传入 self。
跨模块联动统一通过 page 的委托方法（如 page._refresh_target_combo()）进行，
避免 actions 与本模块产生循环导入。
"""

import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog

from config import presets

from ui.tabs.conversion.registry import (
    C, ALL_SOURCE_FORMATS, _filters_str, get_format_from_path, get_known_src_formats,
)
from ui.options.set_tts import show_tts_options
from ui.options.set_stt import show_stt_options
from ui.options.set_image_docx import show_image_docx_options
from ui.options.set_pdf_docx import show_pdf_docx_options


def effective_source(page):
    """返回 (源路径, 源格式)：优先「源文件夹」，其次「源文件」"""
    if page.folder_path.strip():
        return page.folder_path, page.src_format
    f = page.input_path.strip()
    return f, (get_format_from_path(f) if f else "")


def infer_folder_format(page, folder):
    """扫描文件夹，返回第一个受支持文件的格式；找不到返回 None"""
    try:
        known_src = get_known_src_formats()
        for name in sorted(os.listdir(folder)):
            p = os.path.join(folder, name)
            if not os.path.isfile(p):
                continue
            fmt = get_format_from_path(p)
            if not fmt:
                continue
            if fmt in known_src or fmt in C.IMAGE_FORMATS or fmt in C.MEDIA_EXTENSIONS:
                return fmt
    except Exception:
        pass
    return None


def browse_folder(page):
    """浏览并选择「源文件夹」：多文件逐个转换"""
    folder = QFileDialog.getExistingDirectory(
        page, "选择源文件夹（多文件：逐个转换）")
    if not folder:
        return
    page.folder_entry.setText(folder)
    page.input_entry.clear()
    page.output_folder_entry.clear()
    fmt = infer_folder_format(page, folder)
    page.src_format = fmt or ""
    page.source_picker.select(fmt, emit=False)
    if fmt:
        page.log(f"📂 已选择文件夹: {os.path.basename(folder)}（识别为 {fmt} 格式）")
    else:
        page.log(f"⚠ 文件夹中没有找到支持的格式，请手动选择「源文件格式」: {folder}")
    page._update_output_state()
    page._refresh_target_combo()
    page._update_preset_area(fmt or "", page.selected_format)
    page._auto_fill_output()


def browse_input(page):
    """浏览并选择「源文件」：单文件转换"""
    path, _ = QFileDialog.getOpenFileName(
        page, "选择源文件", "", _filters_str(ALL_SOURCE_FORMATS))
    if not path:
        return
    page.input_entry.setText(path)
    page.folder_entry.clear()
    page.output_folder_entry.clear()

    src_fmt = get_format_from_path(path)
    page.log(f"📂 已选择: {os.path.basename(path)} ({src_fmt})")

    page._refresh_target_combo()
    page._update_preset_area(src_fmt, page.selected_format)
    page._update_output_state()


def browse_output_folder(page):
    """浏览并选择「输出文件夹」"""
    initial = (page.output_folder_path.strip()
               or os.path.dirname(page.folder_path.strip()) or "")
    folder = QFileDialog.getExistingDirectory(
        page, "选择输出文件夹（每个源文件单独转换后输出到此）", initial)
    if folder:
        page.output_folder_entry.setText(folder)


def on_folder_fmt_selected(page, fmt):
    """用户手动选择「源文件格式」"""
    fmt = (fmt or "").strip()
    if not fmt:
        return
    page.src_format = fmt
    page.log(f"🗂️ 源文件格式: {fmt}")
    page._refresh_target_combo()
    page._update_preset_area(fmt, page.selected_format)
    page._auto_fill_output()


def on_source_edited(page):
    """源文件/源文件夹被手动编辑时，同步界面状态"""
    try:
        page.folder_path = page.folder_entry.text().strip()
        page.input_path = page.input_entry.text().strip()
        page.output_folder_path = page.output_folder_entry.text().strip()
        page.src_format = page.source_picker.current_format()
        page._update_output_state()
        folder = page.folder_path
        if folder:
            page._update_preset_area(page.src_format, page.selected_format)
        else:
            f = page.input_path
            page._update_preset_area(get_format_from_path(f) if f else "",
                                     page.selected_format)
    except Exception:
        pass


def update_output_state(page):
    """根据源（文件/文件夹）启用/禁用输出文件夹"""
    folder = page.folder_path.strip()
    # 转换模式始终使用输出文件夹
    page.output_folder_entry.setEnabled(True)
    page.output_folder_browse_btn.setEnabled(True)
    # 源文件格式选择器：仅源文件夹模式显示
    page._src_fmt_widget.setVisible(bool(folder))
    page.source_picker.setEnabled(bool(folder))


def auto_fill_output(page):
    """按源 + 目标格式自动填充输出文件夹路径（仅当输出为空时）"""
    folder = page.folder_path.strip()
    fmt = page.selected_format
    if not fmt:
        return
    try:
        if folder:
            base = os.path.basename(folder.rstrip("/\\"))
            parent = os.path.dirname(folder.rstrip("/\\"))
            if not page.output_folder_path.strip() and parent:
                page.output_folder_entry.setText(
                    os.path.join(parent, f"{base}_转换_{fmt}"))
    except Exception:
        pass


# ──────────────────────────────────────
#  选项弹窗
# ──────────────────────────────────────

def show_format_panel(page):
    """打开格式选项对话框"""
    from ui.tabs.tab_component.set_format import SetFormat
    dlg = SetFormat(page.current_config, page)
    dlg.setAttribute(Qt.WA_DeleteOnClose)
    dlg.finished.connect(lambda result: on_format_panel_finished(page, dlg))
    dlg.show()


def on_format_panel_finished(page, dlg):
    """格式选项对话框关闭回调：保存配置"""
    try:
        page.current_config = dlg.get_config()
    except RuntimeError:
        pass
    presets.save_last_config(page.current_config)


def open_tts_options(page):
    """打开 TTS 语音参数弹窗"""
    show_tts_options(page, page.tts_config, on_close=lambda: tts_options_closed(page))


def tts_options_closed(page):
    """TTS 弹窗关闭：持久化 + 刷新引擎下拉"""
    presets.save_last_tts_config(page.tts_config)
    page._refresh_tts_engine_combo()


def open_stt_options(page):
    """打开 STT 语音识别参数弹窗"""
    show_stt_options(page, page.stt_config, on_close=lambda: stt_options_closed(page))


def stt_options_closed(page):
    """STT 弹窗关闭：持久化 + 刷新识别摘要"""
    presets.save_last_stt_config(page.stt_config)
    page._refresh_stt_summary()


def open_image_docx_options(page):
    """打开「图片 → docx」排版预设弹窗"""
    show_image_docx_options(page, page.image_docx_config,
                            on_close=lambda: image_options_closed(page))


def image_options_closed(page):
    """图片排版弹窗关闭：持久化 + 刷新预设下拉"""
    presets.save_last_image_config(page.image_docx_config)
    page._refresh_img_preset_combo()


def open_pdf_docx_options(page):
    """打开「PDF → DOCX」转换方式弹窗"""
    show_pdf_docx_options(page, page.pdf_docx_config,
                          on_close=lambda: pdf_docx_options_closed(page))


def pdf_docx_options_closed(page):
    """PDF→DOCX 弹窗关闭：持久化 + 刷新转换方式摘要"""
    presets.save_last_pdf_docx_config(page.pdf_docx_config)
    page._refresh_pdf_docx_summary()
