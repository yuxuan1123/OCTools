"""
OCTools/core/formats/
───────────────────────────────────────────────
格式注册表（全项目唯一的「格式真相源」）—— 最小功能单元拆分

  - capabilities.py  能力位常量
  - model.py         Format 元数据模型 + 家族展示元信息
  - registry.py      注册表本体（FORMATS / ALIAS_MAP / BY_ID）
  - queries.py       查询 API

对外保持与原单文件等价：from core.formats import Format, get, ...
"""

from core.formats.capabilities import (  # noqa: F401
    CAP_SOURCE,
    CAP_TARGET,
    CAP_MERGE,
    CAP_OCR_TARGET,
    CAP_TTS_SOURCE,
    CAP_VECTOR,
    CAP_MEDIA_IMAGE,
    CAP_IMAGE_TO_DOC,
)
from core.formats.model import Format, FAMILY_META  # noqa: F401
from core.formats.registry import FORMATS, ALIAS_MAP, BY_ID  # noqa: F401
from core.formats.queries import (  # noqa: F401
    get,
    resolve,
    all_ids,
    source_ids,
    target_ids,
    family_of,
    display,
    icon,
    filter_of,
    categories,
    alias_map,
    doc_ids,
    mergeable_ids,
    media_image_ids,
    bitmap_ids,
    vector_ids,
    ocr_target_ids,
    tts_source_ids,
    image_to_doc_ids,
)

__all__ = [
    "CAP_SOURCE",
    "CAP_TARGET",
    "CAP_MERGE",
    "CAP_OCR_TARGET",
    "CAP_TTS_SOURCE",
    "CAP_VECTOR",
    "CAP_MEDIA_IMAGE",
    "CAP_IMAGE_TO_DOC",
    "Format",
    "FAMILY_META",
    "FORMATS",
    "ALIAS_MAP",
    "BY_ID",
    "get",
    "resolve",
    "all_ids",
    "source_ids",
    "target_ids",
    "family_of",
    "display",
    "icon",
    "filter_of",
    "categories",
    "alias_map",
    "doc_ids",
    "mergeable_ids",
    "media_image_ids",
    "bitmap_ids",
    "vector_ids",
    "ocr_target_ids",
    "tts_source_ids",
    "image_to_doc_ids",
]
