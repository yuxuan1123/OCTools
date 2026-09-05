"""
OCTools/ui/tabs/conversion/runner.py
────────────────────────────────────
转换执行：单文件 / 多文件（逐个转换），后台线程调用 services.conversion.convert。
所有日志通过 page.log（_LogBridge 跨线程桥）安全落盘，完成后复位按钮。
"""

import os
import threading

from PySide6.QtWidgets import QMessageBox

from plugins.conversion.registry import (
    C, batch_api, _actual_ext, get_format_from_path,
)


def run_conversion(page):
    """开始转换：校验输入后按「单文件 / 多文件」分发到后台线程"""
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

    out_dir = None
    if folder:
        src_fmt = page.src_format
        if not src_fmt:
            QMessageBox.warning(page, "提示", "请选择「源文件格式」（文件夹内文件的格式）")
            return
        out_dir = page.output_folder_entry.text().strip()
        if not out_dir:
            QMessageBox.warning(page, "提示", "请选择「输出文件夹」")
            return
        if not batch_api.can_batch(src_fmt, fmt):
            QMessageBox.warning(
                page, "提示",
                f"「{src_fmt} → {fmt}」不支持逐个转换模式。\n"
                f"图片 → 文档类格式（pdf/docx/md/txt/TXT(OCR)）应合并为单个文件，请改用「拼接」模式。")
            return
    else:
        src_fmt = get_format_from_path(file_)
        out_dir = page.output_folder_entry.text().strip()
        if not out_dir:
            # 单文件模式：自动生成输出路径（如果未指定）
            base = os.path.splitext(file_)[0]
            ext = _actual_ext(fmt)
            out_dir = f"{base}.{ext}"
            page.output_folder_entry.setText(out_dir)

    # 开始转换（异步，后台线程执行）
    page.convert_btn.setEnabled(False)
    page.convert_btn.setText("转换中...")
    page.clear_log()
    page.log(f"🚀 开始转换: {src} → {fmt}")
    page.log(f"📁 输出目录: {out_dir}")

    if folder:
        threading.Thread(
            target=batch_convert,
            args=(page, folder, src_fmt, fmt, out_dir),
            daemon=True
        ).start()
    else:
        threading.Thread(
            target=single_convert,
            args=(page, file_, src_fmt, fmt, out_dir),
            daemon=True
        ).start()


def pick_config(page, src_fmt, dst_fmt):
    """按目标/源类型挑选对应的配置对象"""
    if dst_fmt in C.AUDIO_FORMATS:
        return page.tts_config          # TtsConfig 实例
    if dst_fmt == "txt" and src_fmt in C.AUDIO_FORMATS:
        return page.stt_config          # SttConfig 实例
    if dst_fmt == "docx" and src_fmt == "pdf":
        return page.pdf_docx_config     # PdfDocxConfig 实例
    return page.current_config          # FormatConfig 实例（docx 等）


def single_convert(page, src_path, src_fmt, dst_fmt, output_path):
    """单文件转换（在线程中执行）"""
    try:
        from services.conversion import convert
        config = pick_config(page, src_fmt, dst_fmt)
        success = convert(
            input_path=src_path,
            output_path=output_path,
            log=page.log,
            config=config,
        )
        if success:
            page.log(f"✅ 转换成功: {os.path.basename(src_path)} → {output_path}")
        else:
            page.log("❌ 转换失败（详情见上方日志）")
    except Exception as e:
        page.log(f"❌ 异常: {str(e)}")
    finally:
        page.convert_btn.setEnabled(True)
        page.convert_btn.setText("开始转换")


def batch_convert(page, folder, src_fmt, dst_fmt, output_dir):
    """多文件逐个转换（在线程中执行）"""
    try:
        from services.conversion import convert

        files = []
        for name in sorted(os.listdir(folder)):
            full_path = os.path.join(folder, name)
            if not os.path.isfile(full_path):
                continue
            ext = os.path.splitext(name)[1].lstrip(".").lower()
            if ext == src_fmt:
                files.append(full_path)

        if not files:
            page.log(f"⚠ 文件夹中没有找到 .{src_fmt} 文件")
            return

        total = len(files)
        success_count = 0
        fail_count = 0

        for idx, src_path in enumerate(files, start=1):
            base_name = os.path.splitext(os.path.basename(src_path))[0]
            out_path = os.path.join(output_dir, f"{base_name}.{_actual_ext(dst_fmt)}")
            page.log(f"[{idx}/{total}] 转换: {os.path.basename(src_path)}")

            try:
                config = pick_config(page, src_fmt, dst_fmt)
                success = convert(
                    input_path=src_path,
                    output_path=out_path,
                    log=page.log,
                    config=config,
                )
                if success:
                    success_count += 1
                    page.log(f"  ✅ 成功 -> {os.path.basename(out_path)}")
                else:
                    fail_count += 1
                    page.log("  ❌ 失败（详情见上方日志）")
            except Exception as e:
                fail_count += 1
                page.log(f"  ❌ 异常: {str(e)}")

        page.log(f"📊 批量转换完成: 成功 {success_count}, 失败 {fail_count}")
    except Exception as e:
        page.log(f"❌ 批量转换异常: {str(e)}")
    finally:
        page.convert_btn.setEnabled(True)
        page.convert_btn.setText("开始转换")
