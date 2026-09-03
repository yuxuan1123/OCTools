"""
OCTools/core/engines/audio_engine.py
───────────────────────────────────────────────
音频引擎（核心引擎层）：音频解码、编码、重采样（ffmpeg）

覆盖：
  - 音频 → 音频（转码）
  - 视频 → 音频（抽音轨；无声源自动生成等时长静音）
  - _audio_encode 通用音频编码（供 TTS 引擎等其他模块复用）

设计原则：
  - 每个转换函数签名统一为 (input_path, output_path, log) -> bool
"""

import os

from core.engines.ffmpeg_utils import (
    AUDIO_CODECS,
    AUDIO_EXTRA,
    _log_done,
    _norm_ext,
    _probe_ffmpeg_info,
    _run_ffmpeg,
    ensure_outdir,
)
from core.utils.file_handler import file_exists


def _audio_encode(input_path, output_path, log, src_is_video=False):
    """通用音频编码：-vn 丢弃视频轨，按目标格式选编码器。

    若源是视频且没有音轨，则生成等时长的静音音频，保证转换成功。
    """
    dst = _norm_ext(output_path)
    codec = AUDIO_CODECS.get(dst)
    if not codec:
        log(f"❌ 不支持的目标音频格式: {dst}")
        return False
    ensure_outdir(output_path)
    args = (["-i", input_path, "-vn", "-c:a", codec]
            + list(AUDIO_EXTRA.get(dst, [])) + [output_path])
    ok, err = _run_ffmpeg(args, log, quiet=True)
    if ok and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        _log_done(output_path, log, kind="音频")
        return True

    # 兜底：视频没有音轨 → 生成等时长静音音频
    if src_is_video and os.path.exists(output_path):
        try: os.remove(output_path)
        except OSError: pass
    if src_is_video:
        has_audio, dur = _probe_ffmpeg_info(input_path)
        if not has_audio and dur:
            log(f"   ⚠ 源文件没有音轨，生成等时长（{dur}）静音音频…")
            args2 = (["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                      "-i", input_path, "-t", dur, "-vn", "-c:a", codec]
                     + list(AUDIO_EXTRA.get(dst, [])) + [output_path])
            ok2, _ = _run_ffmpeg(args2, log)
            if ok2 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                _log_done(output_path, log, kind="音频")
                return True

    # 两次尝试都失败：把第一次的 ffmpeg 错误打印出来
    if err:
        lines = err.strip().splitlines()
        log("❌ 音频转换失败：")
        for line in lines[-4:]:
            log(f"   {line}")
    return False


def video_to_audio(input_path, output_path, log):
    """视频 → 音频（抽取音轨）"""
    if not file_exists(input_path, log): return False
    log(f"🎵 抽取音轨: {os.path.basename(input_path)} → {os.path.basename(output_path)}")
    return _audio_encode(input_path, output_path, log, src_is_video=True)


def audio_to_audio(input_path, output_path, log):
    """音频 → 音频（转码）"""
    if not file_exists(input_path, log): return False
    log(f"🎵 音频转换: {os.path.basename(input_path)} → {os.path.basename(output_path)}")
    return _audio_encode(input_path, output_path, log, src_is_video=False)
