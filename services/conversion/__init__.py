"""
OCTools/services/conversion/
───────────────────────────────────────────────
格式转换业务层：星型 + 直接转换调度。

模块：
  - direct_table.py        直达转换表（引擎函数 → (源,目标) 路由表）
  - registry.py            转换注册表（ConversionSpec + Registry）
  - planner.py             可达性规划（can_batch / can_concat / reachable_targets）
  - pipeline.py            统一转换入口（直达 → 星型保底）
  - batch.py               多文件批量转换
  - base_converter.py      抽象基类：统一 convert() 接口
  - category_converters/   星型架构转换器（按类别，枢纽 + 成员）
  - direct_converters/     高质量直接转换（docx↔pdf / md↔html / txt↔audio 等）
  - cross_category.py      跨类转换调度
  - converter_factory.py   工厂：自动选择直接 or 星型转换
  - star/                  星型保底（hubs / router / runner）

公共 API（本包聚合导出，供 UI / 测试 / 脚本直接使用）：
  convert()                统一转换入口
  CONVERSION_TABLE         直达转换表（(源,目标) → 函数）
  REGISTRY / Registry / ConversionSpec / build_registry
  planner / router / STAR / run_path / HUBS
  格式与媒体常量（FORMAT_ALIASES / MEDIA_EXTENSIONS / 各格式列表）
"""

from services.conversion.registry import (  # noqa: F401
    REGISTRY,
    Registry,
    ConversionSpec,
    build_registry,
)
from services.conversion.pipeline import convert  # noqa: F401
from services.conversion.planner import (  # noqa: F401
    is_reachable,
    path_of,
    reachable_from,
    can_batch,
    can_concat,
    reachable_targets,
)
from services.conversion.direct_table import (  # noqa: F401
    CONVERSION_TABLE,
    FORMAT_ALIASES,
    TXT_OCR_SRC_EXTS,
    TXT_OCR_SOURCES,
    AUDIO_TARGET_EXTS,
    STT_SOURCE_EXTS,
    _IMAGE_TO_DOCX_EXTS,
    _infer_source_format,
)
from services.conversion.star.hubs import HUBS, hub_of, hub_star_edges  # noqa: F401
from services.conversion.star.router import StarRouter, router as STAR  # noqa: F401
from services.conversion.star.runner import run_path  # noqa: F401
from services.conversion.converter_factory import ConverterFactory, factory  # noqa: F401
from services.conversion.cross_category import (  # noqa: F401
    is_cross_category,
    cross_path,
    cross_reachable,
    cross_targets_from,
)

# 格式与媒体常量（媒体引擎侧）
from core.engines.ffmpeg_utils import (  # noqa: F401
    VIDEO_FORMATS,
    AUDIO_FORMATS,
    IMAGE_FORMATS,
    MEDIA_EXTENSIONS,
    SOURCE_ONLY_FORMATS as MEDIA_SOURCE_ONLY_FORMATS,
)
from core.engines.media_engine import (  # noqa: F401
    MEDIA_TARGETS,
    supported_targets,
    is_media_format,
    convert as media_convert,
)

__all__ = [
    "REGISTRY", "Registry", "ConversionSpec", "build_registry",
    "convert", "is_reachable", "path_of", "reachable_from",
    "can_batch", "can_concat", "reachable_targets",
    "CONVERSION_TABLE", "FORMAT_ALIASES", "TXT_OCR_SRC_EXTS", "TXT_OCR_SOURCES",
    "AUDIO_TARGET_EXTS", "STT_SOURCE_EXTS", "_IMAGE_TO_DOCX_EXTS",
    "_infer_source_format",
    "HUBS", "hub_of", "hub_star_edges", "StarRouter", "STAR", "run_path",
    "ConverterFactory", "factory", "is_cross_category", "cross_path",
    "cross_reachable", "cross_targets_from",
    "VIDEO_FORMATS", "AUDIO_FORMATS", "IMAGE_FORMATS", "MEDIA_EXTENSIONS",
    "MEDIA_SOURCE_ONLY_FORMATS", "MEDIA_TARGETS", "supported_targets",
    "is_media_format", "media_convert",
]
