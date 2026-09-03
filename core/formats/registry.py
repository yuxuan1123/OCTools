"""
OCTools/core/formats/registry.py
───────────────────────────────────────────────
格式注册表本体（最小功能单元）

  - FORMATS  格式元组（顺序即 UI 展示顺序）
  - FAMILY_META 家族展示元信息
  - ALIAS_MAP 别名 → 规范 id
  - BY_ID     id → Format 索引
"""

from typing import Dict, Tuple

from core.formats.capabilities import (
    CAP_MERGE,
    CAP_MEDIA_IMAGE,
    CAP_IMAGE_TO_DOC,
    CAP_OCR_TARGET,
    CAP_SOURCE,
    CAP_TARGET,
    CAP_TTS_SOURCE,
    CAP_VECTOR,
)
from core.formats.model import Format

# 常用能力组合
_DOC_CAPS = frozenset({CAP_SOURCE, CAP_TARGET, CAP_MERGE})
_DOCX_CAPS = frozenset({CAP_SOURCE, CAP_TARGET, CAP_MERGE, CAP_IMAGE_TO_DOC})
_IMG_CAPS = frozenset({CAP_SOURCE, CAP_TARGET, CAP_MERGE, CAP_IMAGE_TO_DOC})
_BMP_CAPS = frozenset({CAP_SOURCE, CAP_TARGET, CAP_MERGE, CAP_IMAGE_TO_DOC})
_MEDIA_IMG_CAPS = frozenset({CAP_SOURCE, CAP_TARGET, CAP_MERGE,
                             CAP_MEDIA_IMAGE, CAP_IMAGE_TO_DOC})

FORMATS: Tuple[Format, ...] = (
    # ── 文档类 ──
    Format("md", "Markdown 文件", ("*.md", "*.markdown", "*.mdown"), "doc",
           icon="📝", aliases=("markdown", "mdown"),
           capabilities=_DOC_CAPS | {CAP_TTS_SOURCE}),
    Format("docx", "Word 文档", ("*.docx", "*.doc"), "doc", icon="📄",
           capabilities=_DOC_CAPS),
    Format("pdf", "PDF 文件", ("*.pdf",), "doc", icon="📕",
           capabilities=_DOC_CAPS),
    Format("txt", "文本文件", ("*.txt",), "doc", icon="📃",
           capabilities=_DOC_CAPS | {CAP_TTS_SOURCE}),
    Format("txt-ocr", "文本文件（OCR 识别）", ("*.txt",), "doc", icon="🔤",
           label="TXT(OCR)", capabilities=frozenset(
               {CAP_TARGET, CAP_MERGE, CAP_OCR_TARGET})),

    # ── 图像类（位图 + 矢量 svg）──
    Format("png", "PNG 图片", ("*.png",), "image", icon="🖼️", capabilities=_IMG_CAPS | _MEDIA_IMG_CAPS),
    Format("jpg", "JPEG 图片", ("*.jpg", "*.jpeg"), "image", icon="🖼️",
           label="JPG", aliases=("jpeg",), capabilities=_IMG_CAPS | _MEDIA_IMG_CAPS),
    Format("bmp", "BMP 图片", ("*.bmp",), "image", icon="🖼️", capabilities=_BMP_CAPS | _MEDIA_IMG_CAPS),
    Format("gif", "GIF 图片", ("*.gif",), "video", icon="🖼️",
           capabilities=_MEDIA_IMG_CAPS | frozenset({CAP_MERGE})),
    Format("webp", "WebP 图片", ("*.webp",), "image", icon="🖼️",
           capabilities=_IMG_CAPS | _MEDIA_IMG_CAPS),
    Format("tiff", "TIFF 图片", ("*.tiff", "*.tif"), "image", icon="🖼️",
           aliases=("tif",), capabilities=_IMG_CAPS | _MEDIA_IMG_CAPS),
    Format("heic", "HEIC 图片", ("*.heic", "*.heif"), "image", icon="🖼️",
           label="HEIC", aliases=("heif",), capabilities=_IMG_CAPS | _MEDIA_IMG_CAPS),
    Format("ppm", "PPM 图像", ("*.ppm",), "image", icon="🖼️", capabilities=_MEDIA_IMG_CAPS),
    Format("pgm", "PGM 图像", ("*.pgm",), "image", icon="🖼️", capabilities=_MEDIA_IMG_CAPS),
    Format("svg", "SVG 矢量图", ("*.svg",), "image", icon="✒️",
           capabilities=frozenset({CAP_SOURCE, CAP_TARGET, CAP_MEDIA_IMAGE,
                                   CAP_VECTOR, CAP_IMAGE_TO_DOC})),

    # ── 表格类 ──
    Format("xlsx", "Excel 文件", ("*.xlsx", "*.xls"), "table", icon="📊",
           aliases=("xls",), capabilities=_DOC_CAPS),
    Format("csv", "CSV 文件", ("*.csv",), "table", icon="📊", capabilities=_DOC_CAPS),
    Format("json", "JSON 文件", ("*.json",), "table", icon="📊", capabilities=_DOC_CAPS),

    # ── 演示类 ──
    Format("html", "HTML 文件", ("*.html", "*.htm"), "presentation", icon="🌐",
           aliases=("htm",), capabilities=frozenset({CAP_SOURCE, CAP_TARGET, CAP_MERGE})),
    Format("pptx", "PPT 文件", ("*.pptx",), "presentation", icon="🌐",
           capabilities=frozenset({CAP_SOURCE, CAP_TARGET, CAP_MERGE})),
    Format("pptx-img", "PPT 文件", ("*.pptx",), "presentation", icon="🌐",
           label="PPT图片版", capabilities=frozenset({CAP_TARGET})),

    # ── 视频类（含动态 gif）──
    Format("mp4", "MP4 视频", ("*.mp4", "*.m4v"), "video", icon="🎬",
           aliases=("m4v",), capabilities=frozenset({CAP_SOURCE, CAP_TARGET, CAP_MERGE})),
    Format("avi", "AVI 视频", ("*.avi",), "video", icon="🎬", capabilities=frozenset({CAP_SOURCE, CAP_TARGET, CAP_MERGE})),
    Format("mkv", "MKV 视频", ("*.mkv", "*.mka"), "video", icon="🎬",
           aliases=("mka",), capabilities=frozenset({CAP_SOURCE, CAP_TARGET, CAP_MERGE})),
    Format("mov", "MOV 视频", ("*.mov",), "video", icon="🎬", capabilities=frozenset({CAP_SOURCE, CAP_TARGET, CAP_MERGE})),
    Format("webm", "WebM 视频", ("*.webm",), "video", icon="🎬", capabilities=frozenset({CAP_SOURCE, CAP_TARGET, CAP_MERGE})),
    Format("flv", "FLV 视频", ("*.flv",), "video", icon="🎬", capabilities=frozenset({CAP_SOURCE, CAP_TARGET, CAP_MERGE})),
    Format("wmv", "WMV 视频", ("*.wmv",), "video", icon="🎬", capabilities=frozenset({CAP_SOURCE, CAP_TARGET, CAP_MERGE})),
    Format("3gp", "3GP 视频", ("*.3gp", "*.3g2"), "video", icon="🎬", capabilities=frozenset({CAP_SOURCE, CAP_TARGET, CAP_MERGE})),
    Format("ogv", "OGV 视频", ("*.ogv",), "video", icon="🎬", capabilities=frozenset({CAP_SOURCE, CAP_TARGET, CAP_MERGE})),

    # ── 音频类 ──
    Format("mp3", "MP3 音频", ("*.mp3",), "audio", icon="🎵", capabilities=frozenset({CAP_SOURCE, CAP_TARGET, CAP_MERGE})),
    Format("aac", "AAC 音频", ("*.aac",), "audio", icon="🎵", capabilities=frozenset({CAP_SOURCE, CAP_TARGET, CAP_MERGE})),
    Format("wav", "WAV 音频", ("*.wav",), "audio", icon="🎵", capabilities=frozenset({CAP_SOURCE, CAP_TARGET, CAP_MERGE})),
    Format("flac", "FLAC 音频", ("*.flac",), "audio", icon="🎵", capabilities=frozenset({CAP_SOURCE, CAP_TARGET, CAP_MERGE})),
    Format("ogg", "OGG 音频", ("*.ogg", "*.oga"), "audio", icon="🎵",
           aliases=("oga",), capabilities=frozenset({CAP_SOURCE, CAP_TARGET, CAP_MERGE})),
    Format("opus", "Opus 音频", ("*.opus",), "audio", icon="🎵",
           label="Opus", capabilities=frozenset({CAP_SOURCE, CAP_TARGET, CAP_MERGE})),
    Format("wma", "WMA 音频", ("*.wma",), "audio", icon="🎵", capabilities=frozenset({CAP_SOURCE, CAP_TARGET, CAP_MERGE})),
    Format("m4a", "M4A 音频", ("*.m4a",), "audio", icon="🎵", capabilities=frozenset({CAP_SOURCE, CAP_TARGET, CAP_MERGE})),
    Format("amr", "AMR 音频", ("*.amr",), "audio", icon="🎵", capabilities=frozenset({CAP_SOURCE, CAP_TARGET, CAP_MERGE})),
    Format("ac3", "AC3 音频", ("*.ac3",), "audio", icon="🎵", capabilities=frozenset({CAP_SOURCE, CAP_TARGET, CAP_MERGE})),
    Format("aiff", "AIFF 音频", ("*.aiff", "*.aif"), "audio", icon="🎵",
           label="AIFF", capabilities=frozenset({CAP_SOURCE, CAP_TARGET, CAP_MERGE})),
)

# 别名 → 规范格式 id（含历史别名）
ALIAS_MAP: Dict[str, str] = {}
for _f in FORMATS:
    for _a in _f.aliases:
        ALIAS_MAP[_a] = _f.id

BY_ID: Dict[str, Format] = {f.id: f for f in FORMATS}
