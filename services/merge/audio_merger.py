"""
octool/services/merger/audio_merger.py
───────────────────────────────────────────────
音频合并器（业务逻辑层）：星型架构 —— 统一为 wav 后合并

流程（符合 要求.md 星型合并示例，如 两个mp3合并为FLAC）：
  1. 每个音频先转为 16k/44.1k WAV（wav 为音频枢纽格式）
  2. 用 ffmpeg concat 把 WAV 合并为单个 WAV
  3. 按目标格式把 WAV 转码为输出

若所有文件已是目标格式，直接走 ffmpeg concat（流拷贝优先，秒级）。
"""

import os
import tempfile
import shutil

from core.engines.audio_engine import _audio_encode
from core.engines.ffmpeg_utils import AUDIO_FORMATS, _run_ffmpeg
from services.merge.base_merger import BaseMerger


class AudioMerger(BaseMerger):
    """音频合并器（经 wav 枢纽）"""

    supported_formats = AUDIO_FORMATS

    def merge(self, files, output, log=lambda m: print(m)):
        dst = os.path.splitext(output)[1].lstrip(".").lower()
        return merge_audio(files, dst, output, log)


def merge_audio(files, dst: str, output, log=lambda m: print(m)) -> bool:
    """把音频文件合并为单个 dst 格式文件"""
    if not files:
        log("❌ 没有可合并的音频文件")
        return False

    dst = dst.lstrip(".").lower()
    all_same = all(os.path.splitext(f)[1].lstrip(".").lower() == dst for f in files)

    # 快路径：全部已是目标格式 → 直接 ffmpeg concat（流拷贝优先）
    if all_same:
        from services.merge.media_merger import merge_media
        return merge_media(files, output, log)

    # 星型路径：统一转 wav → concat → 转目标格式
    tmpdir = tempfile.mkdtemp(prefix="audio_merge_")
    wavs = []
    try:
        for i, f in enumerate(files):
            tmp = os.path.join(tmpdir, f"a{i:03d}.wav")
            log(f"── 转换 {os.path.basename(f)} → wav 枢纽")
            if not _audio_encode(f, tmp, log, src_is_video=False):
                log(f"⚠ 跳过 {os.path.basename(f)}（转 wav 失败）")
                continue
            wavs.append(tmp)
        if not wavs:
            log("❌ 没有任何音频转换成功，无法合并")
            return False
        merged_wav = os.path.join(tmpdir, "merged.wav")
        if not _concat_wavs(wavs, merged_wav, log):
            return False
        os.makedirs(os.path.dirname(os.path.abspath(output)) or ".", exist_ok=True)
        if dst in ("", "wav"):
            shutil.move(merged_wav, output)
            log(f"✅ 完成 → {output}")
            return True
        return _audio_encode(merged_wav, output, log, src_is_video=False)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def _concat_wavs(wavs, output, log):
    """把 WAV 列表用 ffmpeg concat 合并（同格式可流拷贝）"""
    listfile = os.path.join(os.path.dirname(output), "list.txt")
    with open(listfile, "w", encoding="utf-8") as fh:
        for p in wavs:
            p2 = os.path.abspath(p).replace("\\", "/")
            fh.write(f"file '{p2}'\n")
    base = ["-f", "concat", "-safe", "0", "-i", listfile]
    ok, _ = _run_ffmpeg(base + ["-c", "copy", output], log, quiet=True)
    if ok and os.path.exists(output) and os.path.getsize(output) > 0:
        return True
    ok, _ = _run_ffmpeg(base + ["-c:a", "pcm_s16le", output], log)
    return ok and os.path.exists(output) and os.path.getsize(output) > 0
