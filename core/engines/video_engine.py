"""
OCTools/core/engines/video_engine.py
───────────────────────────────────────────────
视频引擎（核心引擎层）：视频格式转换与封装（ffmpeg）

覆盖：
  - 视频 → 视频（含 视频 → 动态 GIF，调色板优化）
  - 视频 → 图像（取首帧）
  - 图像 → 视频（静图循环成视频）

设计原则（与音频/图像引擎一致）：
  - 每个转换函数签名统一为 (input_path, output_path, log) -> bool
  - 先尝试「流拷贝」加速（不重新编码），失败再完整转码
"""

import os

from core.engines.ffmpeg_utils import (
    VIDEO_CODECS,
    VIDEO_FORMATS,
    PIL_FORMATS,
    _ffmpeg_summary,
    _log_done,
    _norm_ext,
    _run_ffmpeg,
    ensure_outdir,
)
from core.utils.file_handler import file_exists


# ════════════════════════════════════════════
#  视频 → 视频
# ════════════════════════════════════════════

def video_to_video(input_path, output_path, log):
    """视频 → 视频（含 视频 → 动态 GIF）"""
    if not file_exists(input_path, log): return False
    dst = _norm_ext(output_path)
    if dst not in VIDEO_FORMATS:
        log(f"❌ 不支持的目标视频格式: {dst}")
        return False
    log(f"🎬 视频转换: {os.path.basename(input_path)} → {os.path.basename(output_path)}")
    ensure_outdir(output_path)

    if dst == "gif":
        return _to_animated_gif(input_path, output_path, log)

    # 快路径：流拷贝（不重新编码）
    if _try_stream_copy(input_path, output_path, log):
        return True

    # 慢路径：完整转码
    log("   ⚙️ 流拷贝不可用，改为完整转码…")
    return _transcode_video(input_path, output_path, log, dst)


def _try_stream_copy(input_path, output_path, log):
    """尝试 ffmpeg -c copy 直接封装（最快）"""
    log("   ⚡ 尝试流拷贝（不重新编码）…")
    ok, _ = _run_ffmpeg(["-i", input_path, "-c", "copy", output_path], log, quiet=True)
    if ok and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        _log_done(output_path, log, kind="视频")
        return True
    if os.path.exists(output_path):
        try: os.remove(output_path)
        except OSError: pass
    return False


def _transcode_video(input_path, output_path, log, dst):
    """按目标容器选择编码器完整转码"""
    prof = VIDEO_CODECS.get(dst, VIDEO_CODECS["mp4"])
    args = ["-i", input_path,
            "-c:v", prof["v"], "-c:a", prof["a"]] + list(prof.get("extra", []))
    args += [output_path]
    ok, err = _run_ffmpeg(args, log)
    if ok and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        dur, _ = _ffmpeg_summary(err, output_path)
        _log_done(output_path, log, dur=dur, kind="视频")
        return True
    return False


def _to_animated_gif(input_path, output_path, log):
    """视频 → 动态 GIF（调色板优化，宽高 ≤480 等比缩放，无限循环）"""
    vf = ("fps=10,scale='min(480\\,iw)':-2:flags=lanczos,"
          "split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse")
    ok, err = _run_ffmpeg(["-i", input_path, "-an", "-vf", vf, "-loop", "0", output_path], log)
    if ok and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        _log_done(output_path, log, kind="GIF")
        return True
    return False


# ════════════════════════════════════════════
#  视频 → 图像（取首帧）
# ════════════════════════════════════════════

def video_to_image(input_path, output_path, log):
    """视频 → 图像（抽取第 1 帧作为缩略图）"""
    if not file_exists(input_path, log): return False
    dst = _norm_ext(output_path)
    if dst not in PIL_FORMATS or dst in ("heic", "svg"):
        log(f"❌ 不支持从视频导出为 {dst}")
        return False
    log(f"🖼️ 抽取首帧: {os.path.basename(input_path)} → {os.path.basename(output_path)}")
    ensure_outdir(output_path)
    ok, err = _run_ffmpeg(["-i", input_path, "-frames:v", "1", "-q:v", "2", output_path], log)
    if ok and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        _log_done(output_path, log, kind="图像")
        return True
    return False


# ════════════════════════════════════════════
#  图像 → 视频（静图循环）
# ════════════════════════════════════════════

def image_to_video(input_path, output_path, log, duration=5):
    """图像 → 视频（单张图片循环成 duration 秒的视频）"""
    if not file_exists(input_path, log): return False
    dst = _norm_ext(output_path)
    prof = VIDEO_CODECS.get(dst)
    if not prof or prof.get("gif"):
        log(f"❌ 暂不支持图片 → {dst}（动图请走图像互转）")
        return False
    log(f"🎬 图片 → 视频: {os.path.basename(input_path)} → {os.path.basename(output_path)}"
        f"（静图循环 {duration}s）")
    ensure_outdir(output_path)

    from core.engines.image_engine import image_to_image
    src = input_path
    tmp = None
    # SVG / HEIC / GIF 需要先转成 PNG 再交给 ffmpeg：
    # （gif 的 demuxer 不支持 -loop 输入选项，会报 "Option loop not found"）
    if _norm_ext(input_path) in ("svg", "heic", "gif"):
        tmp = output_path + ".tmp.png"
        if not image_to_image(input_path, tmp, log):
            return False
        src = tmp
    try:
        # 图片 → 视频：统一转 yuv420p（透明 RGBA 帧若无显式像素格式，
        # 3gp(baseline) / webm(vp9) 等编码器会直接报 Invalid argument）
        args = ["-loop", "1", "-i", src, "-t", str(duration), "-r", "25",
                "-c:v", prof["v"], "-pix_fmt", "yuv420p"] + list(prof.get("extra", [])) + [output_path]
        ok, err = _run_ffmpeg(args, log)
        if ok and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            _log_done(output_path, log, kind="视频")
            return True
        return False
    finally:
        if tmp and os.path.exists(tmp):
            try: os.remove(tmp)
            except OSError: pass
