"""
OCTools/core/engines/media_engine.py
───────────────────────────────────────────────
媒体引擎门面（核心引擎层）：视频 / 音频 / 图像 统一调度

把三个子引擎（video_engine / audio_engine / image_engine）组合为
旧 media_converters 的等价 API：
  - MEDIA_TARGETS / supported_targets / is_media_format  供 UI 与注册表使用
  - convert()  统一媒体转换入口（按源/目标扩展名自动派发）

旧路径 src/media_converters.py 保留为兼容 shim（re-export 本模块
与各子引擎的全部符号）。
"""

import os

from core.engines import audio_engine, image_engine, video_engine
from core.engines.ffmpeg_utils import (
    AUDIO_FORMATS,
    FORMAT_ALIASES,
    IMAGE_FORMATS,
    MEDIA_EXTENSIONS,
    SOURCE_ONLY_FORMATS,
    VIDEO_FORMATS,
    get_ffmpeg_path,
)
from core.utils.file_handler import file_exists


# ════════════════════════════════════════════
#  统一调度
# ════════════════════════════════════════════

# 源格式 → 可达目标格式集合（供 UI 动态启用/禁用按钮）
MEDIA_TARGETS = {}


def _build_targets():
    """构建「源格式 → 支持的目标格式」映射"""
    # 视频源：视频（含动图 gif）+ 全部音频（抽音轨）+ 图像（取首帧，heic/svg 除外）
    for v in VIDEO_FORMATS:
        targets = {v2 for v2 in VIDEO_FORMATS if v2 != v}
        targets |= set(AUDIO_FORMATS)
        targets |= {im for im in IMAGE_FORMATS if im not in ("gif", "heic", "svg")}
        MEDIA_TARGETS[v] = targets
    # 音频源：仅音频互转（音频→视频无意义，暂不支持）
    for a in AUDIO_FORMATS:
        MEDIA_TARGETS[a] = {a2 for a2 in AUDIO_FORMATS if a2 != a}
    # 图像源：图像互转（含 位图→SVG 输出）+ 视频（静图循环，gif 静态走图像互转）
    for im in IMAGE_FORMATS:
        targets = {im2 for im2 in IMAGE_FORMATS if im2 != im}
        targets |= {v for v in VIDEO_FORMATS if v != "gif"}
        MEDIA_TARGETS[im] = targets


_build_targets()


def supported_targets(src_fmt):
    """返回从 src_fmt 出发支持的目标格式列表（供 UI 使用）"""
    src_fmt = FORMAT_ALIASES.get(src_fmt, src_fmt)
    return sorted(MEDIA_TARGETS.get(src_fmt, []))


def is_media_format(fmt):
    """判断某格式是否属于媒体（视频/音频/图像）"""
    return fmt in MEDIA_EXTENSIONS


def convert(input_path, output_path, log):
    """媒体统一转换入口：按源/目标扩展名自动派发。

    优先级：图像互转 → 视频（含动图）→ 音频（抽音轨）→ 图像（取首帧）。
    """
    if not file_exists(input_path, log): return False
    src = _norm_ext(input_path)
    dst = _norm_ext(output_path)

    # 图像源
    if src in IMAGE_FORMATS:
        if dst in IMAGE_FORMATS:
            return image_engine.image_to_image(input_path, output_path, log)
        if dst in VIDEO_FORMATS:
            return video_engine.image_to_video(input_path, output_path, log)
    # 视频源
    if src in VIDEO_FORMATS:
        if dst in VIDEO_FORMATS:
            return video_engine.video_to_video(input_path, output_path, log)
        if dst in AUDIO_FORMATS:
            return audio_engine.video_to_audio(input_path, output_path, log)
        if dst in IMAGE_FORMATS:
            return video_engine.video_to_image(input_path, output_path, log)
    # 音频源
    if src in AUDIO_FORMATS:
        if dst in AUDIO_FORMATS:
            return audio_engine.audio_to_audio(input_path, output_path, log)

    log(f"❌ 不支持的媒体转换: {src} → {dst}")
    return False


def _norm_ext(path):
    """归一化扩展名（无点号小写；别名归一到规范格式）"""
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    return FORMAT_ALIASES.get(ext, ext)


# ════════════════════════════════════════════
#  兼容导出（旧 media_converters 的全部公开符号）
# ════════════════════════════════════════════

# 子引擎函数直接透出（保持旧调用方 C.video_to_video 等可用）
video_to_video = video_engine.video_to_video
video_to_audio = audio_engine.video_to_audio
audio_to_audio = audio_engine.audio_to_audio
video_to_image = video_engine.video_to_image
image_to_image = image_engine.image_to_image
svg_to_png = image_engine.svg_to_png
image_to_video = video_engine.image_to_video
