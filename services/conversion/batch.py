"""
octool/services/converter/batch.py
───────────────────────────────────────────────
多文件「批量转换」引擎（业务逻辑层）

功能：
  - list_files(folder, src_fmt)  列出文件夹内指定格式的文件
  - can_batch / can_concat       供 UI 判断某 (源格式 → 目标格式) 是否支持对应模式
  - batch_convert(folder, src, dst, out_dir)  多文件「转换」：
       文件夹内每个文件单独转换为目标格式，输出到输出文件夹。

拼接（concat / merge_files）逻辑见 services/merger/。

设计原则：
  - log 是 callable(msg)，线程安全由调用方保证
  - 单个文件失败不影响其他文件（跳过并计数）

旧路径 src/batch.py 保留为兼容 shim（re-export 本模块 + services.merge）。
"""

import os

from core import formats as FMT
from core.utils.file_handler import read_text, write_text, safe_name
from services.conversion import planner



# 文档类格式（图片 → 文档类 一律视为拼接；txt-ocr 输出仍是 txt）
DOC_FORMATS = set(FMT.doc_ids())

# 支持「合并为单个文件」的目标格式
MERGEABLE_FORMATS = set(FMT.mergeable_ids())

# 需要 ffmpeg 合并的媒体格式
from core.engines.ffmpeg_utils import (  # noqa: E402
    VIDEO_FORMATS,
    AUDIO_FORMATS,
    AUDIO_CODECS,
    AUDIO_EXTRA,
    VIDEO_CODECS,
    _run_ffmpeg,
)
MEDIA_MERGE_EXTS = {f".{x}" for x in VIDEO_FORMATS + AUDIO_FORMATS}
# 图像（不含 gif/svg）—— 自我拼接为「联系表」单图
IMAGE_CONTACT_EXTS = {f".{x}" for x in FMT.media_image_ids() if x not in ("gif", "svg")}


def _norm_fmt(fmt):
    """归一化格式名（pptx-img 实际产物仍是 pptx）"""
    fmt = fmt.lstrip(".").lower()
    return "pptx" if fmt == "pptx-img" else fmt


# ════════════════════════════════════════════
#  文件收集
# ════════════════════════════════════════════

def list_files(folder: str, src_fmt: str) -> list:
    """列出文件夹内指定格式的文件（按文件名排序，含别名归一化）"""
    fmt = _norm_fmt(src_fmt)
    files = []
    try:
        names = sorted(os.listdir(folder))
    except OSError:
        return files
    for name in names:
        p = os.path.join(folder, name)
        if not os.path.isfile(p):
            continue
        if FMT.resolve(os.path.splitext(p)[1].lstrip(".")) == fmt:
            files.append(p)
    return files


# ════════════════════════════════════════════
#  模式可用性判断（供 UI 使用；判断逻辑统一在 services/converter/planner.py）
# ════════════════════════════════════════════

def can_batch(src_fmt: str, dst_fmt: str) -> bool:
    """多文件「转换」模式是否可用：每个文件单独转换为目标格式。
    例外：图片 → 文档类格式 应合并为单文件，视为拼接，不允许逐个转换。"""
    return planner.can_batch(_norm_fmt(src_fmt), _norm_fmt(dst_fmt))


def can_concat(src_fmt: str, dst_fmt: str) -> bool:
    """多文件「拼接」模式是否可用：合并为单个目标文件。

    规则：
      1) 图片 → 文档类格式：直接合并（每个文件一页/一张），恒可用；
      2) 自我拼接 src == dst：目标格式需支持合并；
      3) 格式转换拼接：目标格式需支持合并，且存在（直达或星型）转换路径。
    """
    dst_raw = dst_fmt.lstrip(".").lower()
    if dst_raw == "pptx-img":
        return False   # 图片版PPT 不支持拼接合并
    return planner.can_concat(_norm_fmt(src_fmt), _norm_fmt(dst_raw))


# ════════════════════════════════════════════
#  多文件「转换」：逐个转换
# ════════════════════════════════════════════

def batch_convert(folder: str, src_fmt: str, dst_fmt: str, out_dir: str,
                  log=lambda m: print(m), config=None) -> bool:
    """文件夹内每个文件单独转换为目标格式，输出到 out_dir。"""
    from services.conversion.pipeline import convert as _convert
    files = list_files(folder, src_fmt)
    if not files:
        log(f"❌ 文件夹中没有 .{_norm_fmt(src_fmt)} 文件: {folder}")
        return False
    os.makedirs(out_dir, exist_ok=True)

    actual_ext = {"pptx-img": "pptx", "txt-ocr": "txt", "txt_ocr": "txt"}.get(dst_fmt, dst_fmt)
    ok_cnt = fail_cnt = 0
    for f in files:
        base = safe_name(f)
        name = (f"{base}_稳定版.{actual_ext}" if dst_fmt == "pptx-img"
                else f"{base}.{actual_ext}")
        out = os.path.join(out_dir, name)
        log(f"── 转换 {os.path.basename(f)} → {name}")
        try:
            if _convert(f, out, log=log, config=config, target=dst_fmt):
                ok_cnt += 1
            else:
                fail_cnt += 1
        except Exception as e:
            log(f"❌ {e}")
            fail_cnt += 1
    log(f"📊 批量转换完成: 成功 {ok_cnt}，失败 {fail_cnt} → {out_dir}")
    return ok_cnt > 0
