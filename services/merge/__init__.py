"""
OCTools/services/merge/__init__.py
───────────────────────────────────────────────
文件合并业务层（全互通 + 星型并存）：
  - base_merger.py        合并抽象接口
  - same_format_merger.py 同格式合并（全互通架构）
  - image_merger.py       图像拼合成大图 / 动图（网格布局）
  - audio_merger.py       音频统一为 wav 后合并（星型）
  - video_merger.py       视频统一为 mp4 后合并（星型）
  - media_merger.py       ffmpeg concat 媒体合并原语
  - picture_in_doc.py     图片以表格形式插入 docx / pdf
  - concat.py             多文件拼接编排（调度以上合并器）
"""

from services.merge.base_merger import BaseMerger, MergeError  # noqa: F401
from services.merge.concat import concat  # noqa: F401
from services.merge.same_format_merger import merge_files  # noqa: F401

__all__ = ["BaseMerger", "MergeError", "concat", "merge_files"]
