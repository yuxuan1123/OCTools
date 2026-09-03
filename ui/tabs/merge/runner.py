"""
OCTools/ui/tabs/merge/runner.py
─────────────────────────────
拼接执行：单文件 / 多文件（合并为单个文件），后台线程调用
services.merge.concat.concat（多文件）或 services.conversion.convert（单文件）。
所有日志通过 page.log（_LogBridge 跨线程桥）安全落盘，完成后复位按钮。
"""

import threading

from PySide6.QtWidgets import QMessageBox

from ui.tabs.merge.registry import (
    C, batch_api, concat_files, get_format_from_path,
)


def pick_config(page, src_fmt, dst_fmt):
    """按目标/源类型挑选对应的配置对象"""
    if dst_fmt in C.AUDIO_FORMATS and src_fmt in ("txt", "md"):
        return page.tts_config          # TtsConfig 实例
    if dst_fmt == "txt" and src_fmt in C.AUDIO_FORMATS:
        return page.stt_config          # SttConfig 实例
    if src_fmt in C.IMAGE_FORMATS and dst_fmt == "docx":
        return page.image_docx_config   # ImageDocxConfig 实例
    return page.current_config          # FormatConfig 实例（docx 等）


def run_concat(page):
    """开始拼接：校验输入后按「单文件 / 多文件」分发到后台线程"""
    folder = page.folder_path.strip()
    file_ = page.input_path.strip()
    src = folder or file_
    fmt = page.selected_format

    if not src:
        QMessageBox.warning(page, "提示", "请先选择源文件或源文件夹")
        return
    if not fmt:
        QMessageBox.warning(page, "提示", "请选择目标格式")
        return

    if folder:
        src_fmt = page.src_format
        if not src_fmt:
            QMessageBox.warning(page, "提示", "请选择「源文件格式」（文件夹内文件的格式）")
            return
        if not batch_api.can_concat(src_fmt, fmt):
            QMessageBox.warning(
                page, "提示", f"「{src_fmt} → {fmt}」不支持拼接模式（目标格式无法合并）。")
            return
    else:
        src_fmt = get_format_from_path(file_)

    out_file = page.output_entry.text().strip()
    if not out_file:
        QMessageBox.warning(page, "提示", "请选择「输出文件」（拼接后的单个文件）")
        return

    config = pick_config(page, src_fmt, fmt)

    page.convert_btn.setEnabled(False)
    page.convert_btn.setText("拼接中…")
    page.clear_log()
    page.log(f"🚀 开始拼接: {src_fmt or '文件夹'} → {fmt}")
    page.log(f"📁 输出文件: {out_file}")

    def worker():
        try:
            if folder:
                ok = concat_files(folder, src_fmt, fmt, out_file,
                                  log=page.log, config=config)
            else:
                ok = C.convert(file_, out_file, log=page.log,
                               config=config, target=fmt)
            if ok:
                page.log(f"✅ 拼接成功，已保存到:\n{out_file}")
            else:
                page.log("❌ 拼接失败，请查看日志")
        except Exception as e:
            page.log(f"❌ 异常: {e}")
        finally:
            page.convert_btn.setEnabled(True)
            page.convert_btn.setText("开始拼接")

    threading.Thread(target=worker, daemon=True).start()
