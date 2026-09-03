"""
OCTools/ui/tabs/conversion/registry.py
──────────────────────────────────────
转换页的常量注册表与共享引用：
  - 格式相关常量（ALL_FORMATS / ALL_SOURCE_FORMATS / 预设项 / _actual_ext 等）
  - 语音引擎常量（TTS / STT）
  - 共享辅助函数（build_format_list / get_known_src_formats）
"""

from services import conversion as C
from services.conversion import batch as batch_api
from config.format_config import FormatConfig
from config.image_docx_config import ImageDocxConfig
from config.tts_config import TtsConfig, \
    ENGINE_LABELS as TTS_ENGINE_LABELS, ENGINE_ORDER as TTS_ENGINE_ORDER
from config.stt_config import SttConfig, STT_LANGUAGE_LABELS
from ui.widgets.format_select_widget import (
    FormatPicker,
    ALL_FORMATS,
    ALL_SOURCE_FORMATS,
    PRESET_NEW_OPTION,
    IMG_PRESET_DEFAULT_OPTION,
    _actual_ext,
    get_format_from_path,
    _filters_str,
    _categories_for,
)


def build_format_list():
    """转换模式可用的目标格式（排除仅作为媒体源的格式）"""
    return [f for f in ALL_FORMATS if f not in C.MEDIA_SOURCE_ONLY_FORMATS]


def get_known_src_formats():
    """所有可转换的已知源格式集合"""
    return {k[0].lstrip(".") for k in C.CONVERSION_TABLE}
