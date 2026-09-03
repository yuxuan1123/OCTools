"""
OCTools/core/engines/ffmpeg_utils.py
───────────────────────────────────────────────
FFmpeg 公共工具（核心引擎层）

被 video_engine / audio_engine / image_engine 共用：
  - 格式清单与别名（VIDEO_FORMATS / AUDIO_FORMATS / IMAGE_FORMATS / MEDIA_EXTENSIONS）
  - 编解码参数表（VIDEO_CODECS / AUDIO_CODECS / AUDIO_EXTRA / PIL_FORMATS）
  - ffmpeg 定位（ui_config.json 的 paths.ffmpeg → 环境变量 → PATH → 常见安装位置）
  - 执行与日志（_run_ffmpeg / _log_done / _ffmpeg_summary）
  - 探测媒体信息（_probe_ffmpeg_info）
"""

import os
import shutil
import subprocess

from config.ui_config import CONFIG as _C


# ════════════════════════════════════════════
#  格式清单
# ════════════════════════════════════════════

# 视频封装格式（gif 视为动态图/视频输出）
VIDEO_FORMATS = ["mp4", "avi", "mkv", "mov", "webm", "flv", "wmv", "3gp", "ogv", "gif"]

# 音频格式
AUDIO_FORMATS = ["mp3", "aac", "wav", "flac", "ogg", "opus", "wma", "m4a", "amr", "ac3", "aiff"]

# 图像格式（svg 仅支持作为输入；heic 需要 pillow-heif）
IMAGE_FORMATS = ["jpg", "png", "gif", "bmp", "webp", "tiff", "heic", "svg", "ppm", "pgm"]

# 全部媒体扩展名（无点号）
MEDIA_EXTENSIONS = set(VIDEO_FORMATS) | set(AUDIO_FORMATS) | set(IMAGE_FORMATS)

# 别名归一化
FORMAT_ALIASES = {
    "jpeg": "jpg", "tif": "tiff", "m4v": "mp4", "oga": "ogg", "mka": "mkv",
}

# 仅能作为输入的格式（svg 已支持双向：位图 → SVG 输出；SVG → 位图输入）
SOURCE_ONLY_FORMATS = {}


def _norm_ext(path):
    """归一化扩展名（无点号小写）"""
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    return FORMAT_ALIASES.get(ext, ext)


# ════════════════════════════════════════════
#  FFmpeg 定位
# ════════════════════════════════════════════

_FFMPEG_CACHE = None


def get_ffmpeg_path():
    """查找 ffmpeg 可执行文件路径（ui_config.json → 环境变量 → PATH → 常见安装位置）"""
    global _FFMPEG_CACHE
    if _FFMPEG_CACHE:
        return _FFMPEG_CACHE
    # 1) 统一配置（config/ui_config.json 的 paths.ffmpeg，允许外置/覆盖）
    cfg = _C.path("ffmpeg")
    if cfg and os.path.exists(cfg):
        _FFMPEG_CACHE = cfg
        return cfg
    # 2) 环境变量
    for key in ("FFMPEG_BIN", "FFMPEG"):
        env = os.environ.get(key)
        if env and os.path.exists(env):
            _FFMPEG_CACHE = env
            return env
    # 3) PATH
    p = shutil.which("ffmpeg")
    if p:
        _FFMPEG_CACHE = p
        return p
    # 4) 常见安装位置（盘符由环境变量推导，不写死字面量）
    sys_drive = os.environ.get("SystemDrive", "C:") + os.sep
    program_files = os.environ.get("ProgramFiles", sys_drive + "Program Files")
    candidates = [
        os.path.join(sys_drive, "ffmpeg", "bin", "ffmpeg.exe"),
        os.path.join(program_files, "ffmpeg", "bin", "ffmpeg.exe"),
        "/usr/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
        "/opt/homebrew/bin/ffmpeg",
    ]
    for c in candidates:
        if os.path.exists(c):
            _FFMPEG_CACHE = c
            return c
    return "ffmpeg"  # 最后交给系统 PATH 尝试


# ════════════════════════════════════════════
#  编码参数表
# ════════════════════════════════════════════

# 视频容器 → 默认编码器（v=视频编码器, a=音频编码器, extra=附加参数）
VIDEO_CODECS = {
    "mp4":  {"v": "libx264",   "a": "aac",      "extra": ["-movflags", "+faststart", "-pix_fmt", "yuv420p"]},
    "avi":  {"v": "mpeg4",     "a": "libmp3lame"},
    "mkv":  {"v": "libx264",   "a": "aac"},
    "mov":  {"v": "libx264",   "a": "aac"},
    "webm": {"v": "libvpx-vp9", "a": "libopus", "extra": ["-b:v", "0", "-crf", "33", "-deadline", "good", "-cpu-used", "4"]},
    "flv":  {"v": "libx264",   "a": "aac"},
    "wmv":  {"v": "wmv2",      "a": "wmav2"},
    "3gp":  {"v": "libx264",   "a": "aac",      "extra": ["-profile:v", "baseline"]},
    "ogv":  {"v": "libtheora", "a": "libvorbis"},
    "gif":  {"gif": True},   # 动图走调色板流程
}

# 音频格式 → 编码器
AUDIO_CODECS = {
    "mp3":  "libmp3lame",
    "aac":  "aac",
    "wav":  "pcm_s16le",
    "flac": "flac",
    "ogg":  "libvorbis",
    "opus": "libopus",
    "wma":  "wmav2",
    "m4a":  "aac",
    "amr":  "libopencore_amrnb",
    "ac3":  "ac3",
    "aiff": "pcm_s16be",
}

# 音频格式 → 附加参数（无损格式不设码率）
AUDIO_EXTRA = {
    "amr":  ["-ac", "1", "-ar", "8000"],   # AMR 仅支持单声道 8kHz
    "mp3":  ["-b:a", "192k"],
    "aac":  ["-b:a", "192k"],
    "ogg":  ["-q:a", "4"],   # libvorbis 用质量参数（-b:a 在新版 ffmpeg 下报 Invalid argument）
    "opus": ["-b:a", "128k"],
    "wma":  ["-b:a", "192k"],
    "m4a":  ["-b:a", "192k"],
    "ac3":  ["-b:a", "384k"],
}

# 图像格式 → Pillow 格式名
PIL_FORMATS = {
    "jpg":  "JPEG",
    "png":  "PNG",
    "gif":  "GIF",
    "bmp":  "BMP",
    "webp": "WEBP",
    "tiff": "TIFF",
    "ppm":  "PPM",
    "pgm":  "PGM",
    "heic": "HEIF",
}


# ════════════════════════════════════════════
#  公共工具
# ════════════════════════════════════════════

def ensure_outdir(output_path):
    """确保输出文件所在目录存在"""
    d = os.path.dirname(os.path.abspath(output_path))
    if d:
        os.makedirs(d, exist_ok=True)


def _run_ffmpeg(args, log, quiet=False):
    """执行 ffmpeg，返回 (ok, stderr 文本)。

    quiet=True 时不打印错误日志（用于先尝试、失败再回退的场景），
    由调用方决定如何处理失败。
    """
    ff = get_ffmpeg_path()
    cmd = [ff, "-hide_banner", "-y"] + args
    log(f"   $ ffmpeg {' '.join(_compact_args(args))}")
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True,
            encoding="utf-8", errors="replace"
        )
    except FileNotFoundError:
        log("❌ 未找到 ffmpeg。请安装 FFmpeg 并加入 PATH，"
            "或设置环境变量 FFMPEG_BIN 指向 ffmpeg 可执行文件。")
        return False, ""
    except OSError as e:
        log(f"❌ ffmpeg 启动失败: {e}")
        return False, ""
    if proc.returncode != 0:
        if not quiet:
            lines = (proc.stderr or "").strip().splitlines()
            log("❌ ffmpeg 执行失败：")
            for line in lines[-4:]:
                log(f"   {line}")
        return False, proc.stderr or ""
    return True, proc.stderr or ""


def _compact_args(args):
    """把命令行参数压缩成适合日志展示的形态"""
    out = []
    for a in args:
        if len(a) > 120:
            a = a[:60] + "…" + a[-50:]
        out.append(a)
    return out


def _ffmpeg_summary(stderr, output_path):
    """从 ffmpeg stderr 中提取时长，返回 (时长文本, 大小字节)"""
    dur = ""
    for line in (stderr or "").splitlines():
        if "Duration:" in line and not dur:
            dur = line.split("Duration:")[1].split(",")[0].strip()
    size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
    return dur, size


def _log_done(output_path, log, dur="", kind="媒体"):
    size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
    extra = f"，时长 {dur}" if dur else ""
    log(f"✅ 完成 → {output_path}（{size / 1024:.1f} KB{extra}）")


def _probe_ffmpeg_info(input_path):
    """探测媒体信息，返回 (是否有音轨, 时长文本)。

    通过 `ffmpeg -i` 的输出解析（无输出文件时 ffmpeg 返回码非 0 属正常）。
    """
    ff = get_ffmpeg_path()
    try:
        proc = subprocess.run(
            [ff, "-hide_banner", "-i", input_path],
            capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
    except OSError:
        return False, ""
    stderr = proc.stderr or ""
    has_audio = "Audio:" in stderr
    dur = ""
    for line in stderr.splitlines():
        if "Duration:" in line:
            dur = line.split("Duration:")[1].split(",")[0].strip()
            break
    return has_audio, dur


def ensure_heif():
    """注册 pillow-heif 支持（HEIC 读写）"""
    try:
        import pillow_heif
        pillow_heif.register_heif_opener()
        return True
    except ImportError:
        return False


def ensure_cairosvg():
    """返回 cairosvg 模块（SVG 渲染）或 None"""
    try:
        import cairosvg
        return cairosvg
    except ImportError:
        return None
