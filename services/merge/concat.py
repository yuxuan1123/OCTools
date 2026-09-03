"""
octool/services/merger/concat.py
───────────────────────────────────────────────
多文件「拼接」编排（业务逻辑层）：把文件夹内所有文件合并为单个目标文件

支持三种拼接（符合 要求.md 板块二）：
  1) 图片 → 文档类（pdf/docx/md/txt/txt-ocr）：天然单文件（每个文件一页/一张），直接合并
  2) 自我拼接 src == dst：同格式合并（全互通架构：docx→docx / pdf→pdf / xlsx→xlsx …）
  3) 格式转换拼接 src != dst：先逐个转换到目标格式，再合并
     （星型架构：mp3→wav→wav 合并→flac）

"""

import os
import shutil
import tempfile

from core import formats as FMT
from core.utils.file_handler import safe_name
from services.conversion.batch import list_files, _norm_fmt, DOC_FORMATS, MERGEABLE_FORMATS
from services.conversion.pipeline import convert as _convert
from services.merge.same_format_merger import merge_files

# 图像格式（含 gif/svg）
IMAGE_FORMATS = set(FMT.media_image_ids())


def concat(folder: str, src_fmt: str, dst_fmt: str, output: str,
           log=lambda m: print(m), config=None) -> bool:
    """把文件夹内所有 src_fmt 文件合并为单个 dst_fmt 文件。"""
    files = list_files(folder, src_fmt)
    if not files:
        log(f"❌ 文件夹中没有 .{_norm_fmt(src_fmt)} 文件: {folder}")
        return False
    if len(files) == 1:
        # 单文件「拼接」= 普通转换
        return _convert(files[0], output, log=log, config=config, target=dst_fmt)

    src = _norm_fmt(src_fmt)
    dst = _norm_fmt(dst_fmt)
    os.makedirs(os.path.dirname(os.path.abspath(output)) or ".", exist_ok=True)
    log(f"🧩 拼接 {len(files)} 个 .{src} 文件 → 单个 .{dst} 文件")

    # ── 1) 图片 → 文档类：直接合并（每个文件一页/一张，天然单文件）──
    if src in IMAGE_FORMATS and dst in DOC_FORMATS:
        log(f"🔄 图片 → {dst.upper()}（{len(files)} 张合并为单文件）")
        from core.engines.document_engine import (
            images_to_pdf,
            images_to_docx,
            images_to_md,
            images_to_txt,
            images_to_txt_ocr,
        )
        if dst == "pdf":
            return images_to_pdf(folder, output, log)
        if dst == "docx":
            return images_to_docx(folder, output, log, image_config=config)
        if dst == "md":
            return images_to_md(folder, output, log)
        if dst == "txt":
            return images_to_txt(folder, output, log)
        if dst == "txt-ocr":
            return images_to_txt_ocr(folder, output, log)

    # ── 2) 图片 → 动态 GIF（动画拼接）──
    if src in IMAGE_FORMATS and dst == "gif":
        from services.merge.image_merger import merge_gif_animated
        return merge_gif_animated(files, output, log)

    # ── 3) 自我拼接：src == dst ──
    if src == dst:
        return merge_files(files, dst, output, log, src_fmt=src)

    # ── 4) 格式转换拼接：先逐个转换，再合并 ──
    if dst not in MERGEABLE_FORMATS:
        log(f"❌ 目标格式 {dst.upper()} 不支持拼接合并")
        return False
    tmpdir = tempfile.mkdtemp(prefix="concat_")
    converted = []
    try:
        for i, f in enumerate(files):
            tmp = os.path.join(tmpdir, f"{i:04d}.{dst}")
            log(f"── 转换 {os.path.basename(f)} → 临时 {dst.upper()}")
            try:
                if _convert(f, tmp, log=log, config=config, target=dst):
                    converted.append(tmp)
                else:
                    log(f"⚠ 跳过 {os.path.basename(f)}（转换失败）")
            except Exception as e:
                log(f"⚠ 跳过 {os.path.basename(f)}: {e}")
        if not converted:
            log("❌ 没有任何文件转换成功，无法拼接")
            return False
        log(f"🧩 合并 {len(converted)} 个 {dst.upper()} 文件 → 单文件")
        return merge_files(converted, dst, output, log, src_fmt=dst)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
