"""
octool/services/merger/media_merger.py
───────────────────────────────────────────────
媒体合并器（业务逻辑层）：视频 / 音频 → 合并为单个媒体文件

使用 ffmpeg concat demuxer：
  - 先尝试流拷贝（-c copy，秒级）
  - 失败则统一重新编码拼接（视频按容器选编码器，音频按格式选编码器）

旧逻辑来自 src/batch.py（_merge_media），迁移后 src/batch.py 保留为 shim。
"""

import os
import tempfile
import shutil

from core.engines.ffmpeg_utils import (
    AUDIO_CODECS,
    AUDIO_EXTRA,
    VIDEO_CODECS,
    _run_ffmpeg,
)
from services.merge.base_merger import BaseMerger


class MediaMerger(BaseMerger):
    """媒体（视频/音频）合并器"""

    supported_formats = []  # 由 ffmpeg 支持的全部媒体格式（运行时构造）

    def __init__(self):
        from core.engines.ffmpeg_utils import VIDEO_FORMATS, AUDIO_FORMATS
        self.supported_formats = VIDEO_FORMATS + AUDIO_FORMATS

    def merge(self, files, output, log=lambda m: print(m)):
        return merge_media(files, output, log)


def merge_media(files, output, log=lambda m: print(m)):
    """把同格式媒体文件合并为单个文件（ffmpeg concat demuxer）"""
    tmpdir = tempfile.mkdtemp(prefix="ffconcat_")
    listfile = os.path.join(tmpdir, "list.txt")
    try:
        with open(listfile, "w", encoding="utf-8") as fh:
            for p in files:
                p2 = os.path.abspath(p).replace("\\", "/")
                p2 = p2.replace("'", "'\\''")
                fh.write(f"file '{p2}'\n")
        dst = os.path.splitext(output)[1].lower().lstrip(".")
        base = ["-f", "concat", "-safe", "0", "-i", listfile]
        # 尝试流拷贝（秒级）
        ok, _ = _run_ffmpeg(base + ["-c", "copy", output], log, quiet=True)
        if ok and os.path.exists(output) and os.path.getsize(output) > 0:
            log(f"✅ 完成(流拷贝) → {output}")
            return True
        # 回退：统一重新编码
        if dst in AUDIO_CODECS:
            args = (base + ["-c:a", AUDIO_CODECS[dst]]
                    + list(AUDIO_EXTRA.get(dst, [])) + [output])
        else:
            prof = VIDEO_CODECS.get(dst, VIDEO_CODECS["mp4"])
            args = (base + ["-c:v", prof["v"], "-c:a", prof["a"]]
                    + list(prof.get("extra", [])) + [output])
        log("   ⚙️ 流拷贝不可用，改为统一转码后拼接…")
        ok, _ = _run_ffmpeg(args, log)
        if ok and os.path.exists(output) and os.path.getsize(output) > 0:
            log(f"✅ 完成(转码拼接) → {output}")
            return True
        log("❌ 媒体拼接失败")
        return False
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
