"""
octool/services/merger/video_merger.py
───────────────────────────────────────────────
视频合并器（业务逻辑层）：星型架构 —— 统一为 mp4 后合并

流程（符合 要求.md 星型合并示例）：
  1. 每个视频先转为 MP4（mp4 为视频枢纽格式）
  2. 用 ffmpeg concat 把 MP4 合并为单个 MP4
  3. 按目标格式把 MP4 封装/转码为输出

若所有文件已是目标格式，直接走 ffmpeg concat（流拷贝优先，秒级）。
"""

import os
import tempfile
import shutil

from core.engines.ffmpeg_utils import (
    VIDEO_CODECS,
    _run_ffmpeg,
)
from core.engines.video_engine import video_to_video
from services.merge.base_merger import BaseMerger


class VideoMerger(BaseMerger):
    """视频合并器（经 mp4 枢纽）"""

    supported_formats = ["mp4", "avi", "mkv", "mov", "webm", "flv", "wmv", "3gp", "ogv"]

    def merge(self, files, output, log=lambda m: print(m)):
        dst = os.path.splitext(output)[1].lstrip(".").lower()
        return merge_video(files, dst, output, log)


def merge_video(files, dst: str, output, log=lambda m: print(m)) -> bool:
    """把视频文件合并为单个 dst 格式文件"""
    if not files:
        log("❌ 没有可合并的视频文件")
        return False

    dst = dst.lstrip(".").lower()
    all_same = all(os.path.splitext(f)[1].lstrip(".").lower() == dst for f in files)

    # 快路径：全部已是目标格式 → 直接 ffmpeg concat（流拷贝优先）
    if all_same:
        from services.merge.media_merger import merge_media
        return merge_media(files, output, log)

    # 星型路径：统一转 mp4 → concat → 转目标格式
    tmpdir = tempfile.mkdtemp(prefix="video_merge_")
    mp4s = []
    try:
        for i, f in enumerate(files):
            tmp = os.path.join(tmpdir, f"v{i:03d}.mp4")
            log(f"── 转换 {os.path.basename(f)} → mp4 枢纽")
            if not video_to_video(f, tmp, log):
                log(f"⚠ 跳过 {os.path.basename(f)}（转 mp4 失败）")
                continue
            mp4s.append(tmp)
        if not mp4s:
            log("❌ 没有任何视频转换成功，无法合并")
            return False
        merged_mp4 = os.path.join(tmpdir, "merged.mp4")
        if not _concat_mp4s(mp4s, merged_mp4, log):
            return False
        os.makedirs(os.path.dirname(os.path.abspath(output)) or ".", exist_ok=True)
        if dst in ("", "mp4"):
            shutil.move(merged_mp4, output)
            log(f"✅ 完成 → {output}")
            return True
        return video_to_video(merged_mp4, output, log)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def _concat_mp4s(mp4s, output, log):
    """把 MP4 列表用 ffmpeg concat 合并（流拷贝优先，失败统一重编码）"""
    listfile = os.path.join(os.path.dirname(output), "list.txt")
    with open(listfile, "w", encoding="utf-8") as fh:
        for p in mp4s:
            p2 = os.path.abspath(p).replace("\\", "/")
            fh.write(f"file '{p2}'\n")
    base = ["-f", "concat", "-safe", "0", "-i", listfile]
    ok, _ = _run_ffmpeg(base + ["-c", "copy", output], log, quiet=True)
    if ok and os.path.exists(output) and os.path.getsize(output) > 0:
        return True
    prof = VIDEO_CODECS["mp4"]
    ok, _ = _run_ffmpeg(base + ["-c:v", prof["v"], "-c:a", prof["a"]]
                        + list(prof.get("extra", [])) + [output], log)
    return ok and os.path.exists(output) and os.path.getsize(output) > 0
