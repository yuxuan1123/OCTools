"""
OCTools/config/__init__.py
───────────────────────────────────────────────
配置层（最小功能单元拆分）

  - enums.py              全部枚举（PaperSize/Orientation/LineSpacingMode/Alignment）
  - page_layout.py        页面布局配置 PageLayout
  - heading.py            标题样式 HeadingStyle
  - typography.py         字体与排版 Typography
  - content.py            内容样式 ContentStyles
  - advanced.py           高级特性 AdvancedFeatures
  - format_config.py      MD→DOCX 完整配置 FormatConfig（聚合四类子配置）
  - image_docx_config.py  图片→DOCX 排版配置 ImageDocxConfig
  - presets.py            预设 / 上次配置管理器
  - paths.py              配置存储路径常量
  - pdf_docx_config.py    PDF→DOCX 转换方式配置 PdfDocxConfig
  - ui_config.py          UI 配置加载器（JSON 驱动）
  - ui_config.json        UI 参数数据文件
"""

from config.enums import PaperSize, Orientation, LineSpacingMode, Alignment  # noqa: F401
from config.page_layout import PageLayout  # noqa: F401
from config.heading import HeadingStyle  # noqa: F401
from config.typography import Typography  # noqa: F401
from config.content import ContentStyles  # noqa: F401
from config.advanced import AdvancedFeatures  # noqa: F401
from config.format_config import FormatConfig  # noqa: F401
from config.image_docx_config import ImageDocxConfig  # noqa: F401
from config.presets import (  # noqa: F401
    list_presets,
    load_preset,
    save_preset,
    delete_preset,
    export_preset,
    import_preset,
    reset_to_default,
    save_last_config,
    load_last_config,
    list_image_presets,
    save_image_preset,
    load_image_preset,
    delete_image_preset,
    save_last_image_config,
    load_last_image_config,
    save_last_tts_config,
    load_last_tts_config,
    save_last_stt_config,
    load_last_stt_config,
    save_last_pdf_docx_config,
    load_last_pdf_docx_config,
    list_tts_presets,
    save_tts_preset,
    load_tts_preset,
    delete_tts_preset,
    export_tts_preset,
    import_tts_preset,
)
from config.pdf_docx_config import PdfDocxConfig  # noqa: F401
from config.ui_config import CONFIG as C  # noqa: F401

__all__ = [
    "PaperSize",
    "Orientation",
    "LineSpacingMode",
    "Alignment",
    "PageLayout",
    "HeadingStyle",
    "Typography",
    "ContentStyles",
    "AdvancedFeatures",
    "FormatConfig",
    "ImageDocxConfig",
    "PdfDocxConfig",
    "C",
]
