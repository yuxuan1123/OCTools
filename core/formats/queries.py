"""
octool/core/formats/queries.py
───────────────────────────────────────────────
格式查询 API（最小功能单元）

基于 registry 提供各种查询：
  - get / resolve      格式解析与归一化
  - all_ids / source_ids / target_ids / categories
  - 能力集合：doc / mergeable / media_image / bitmap / vector / ocr_target / tts_source / image_to_doc
"""

from typing import Dict, List, Optional, Tuple

from core.formats.capabilities import (
    CAP_MEDIA_IMAGE,
    CAP_MERGE,
    CAP_IMAGE_TO_DOC,
    CAP_OCR_TARGET,
    CAP_SOURCE,
    CAP_TARGET,
    CAP_TTS_SOURCE,
    CAP_VECTOR,
)
from core.formats.model import FAMILY_META, Format
from core.formats.registry import ALIAS_MAP, BY_ID, FORMATS


def get(fmt: str) -> Optional[Format]:
    """按 id 查询格式；带别名或点号也能解析"""
    fmt = str(fmt or "").strip().lower().lstrip(".")
    if fmt in BY_ID:
        return BY_ID[fmt]
    return BY_ID.get(ALIAS_MAP.get(fmt, ""))


def resolve(fmt: str) -> str:
    """归一化格式 id（别名 → 规范 id；未知原样返回）"""
    f = get(fmt)
    return f.id if f else str(fmt or "").strip().lower().lstrip(".")


def all_ids() -> List[str]:
    return [f.id for f in FORMATS]


def source_ids() -> List[str]:
    """可作为源的格式（pptx-img 仅目标）"""
    return [f.id for f in FORMATS if CAP_SOURCE in f.capabilities]


def target_ids() -> List[str]:
    return [f.id for f in FORMATS if CAP_TARGET in f.capabilities]


def family_of(fmt: str) -> str:
    f = get(fmt)
    return f.family if f else ""


def display(fmt: str) -> str:
    f = get(fmt)
    return f.display if f else str(fmt).upper()


def icon(fmt: str) -> str:
    f = get(fmt)
    return f.icon if f else "📦"


def filter_of(fmt: str) -> Tuple[str, str]:
    f = get(fmt)
    return f.filter() if f else ("所有文件", "*.*")


def categories() -> List[Tuple[str, str, List[str]]]:
    """[(分类名, 图标, [格式id...])] —— 按家族分组、保持注册表顺序"""
    return [(title, ico, [f.id for f in FORMATS if f.family == fam])
            for fam, title, ico in FAMILY_META]


def alias_map() -> Dict[str, str]:
    return dict(ALIAS_MAP)


# ── 能力集合（供 planner / batch / star 使用）──

def _with_cap(cap: str) -> List[str]:
    return [f.id for f in FORMATS if cap in f.capabilities]


def doc_ids() -> List[str]:
    return [f.id for f in FORMATS if f.family == "doc"]


def mergeable_ids() -> List[str]:
    return _with_cap(CAP_MERGE)


def media_image_ids() -> List[str]:
    """媒体引擎里的图像族（含 gif / svg）"""
    return _with_cap(CAP_MEDIA_IMAGE)


def bitmap_ids() -> List[str]:
    """位图（不含 svg）"""
    return [f.id for f in FORMATS if CAP_MEDIA_IMAGE in f.capabilities
            and CAP_VECTOR not in f.capabilities]


def vector_ids() -> List[str]:
    return _with_cap(CAP_VECTOR)


def ocr_target_ids() -> List[str]:
    return _with_cap(CAP_OCR_TARGET)


def tts_source_ids() -> List[str]:
    return _with_cap(CAP_TTS_SOURCE)


def image_to_doc_ids() -> List[str]:
    """可走 图片→DOCX 的源格式"""
    return _with_cap(CAP_IMAGE_TO_DOC)
