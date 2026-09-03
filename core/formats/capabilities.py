"""
OCTools/core/formats/capabilities.py
───────────────────────────────────────────────
能力位常量（最小功能单元）

每种格式用一组能力位描述「能做什么」：
  - CAP_SOURCE      可作为输入源
  - CAP_TARGET      可作为输出目标
  - CAP_MERGE       支持自我拼接合并
  - CAP_OCR_TARGET  OCR 伪目标（txt-ocr，输出仍是 .txt）
  - CAP_TTS_SOURCE  可合成语音的源（txt / md）
  - CAP_VECTOR      矢量图（svg）
  - CAP_MEDIA_IMAGE 媒体引擎里的图像族（含 gif，互转位图/矢量）
  - CAP_IMAGE_TO_DOC 可走 图片→文档 路径
"""

CAP_SOURCE = "source"            # 可作为输入源
CAP_TARGET = "target"            # 可作为输出目标
CAP_MERGE = "merge"              # 支持自我拼接合并
CAP_OCR_TARGET = "ocr_target"    # OCR 伪目标（txt-ocr，输出仍是 .txt）
CAP_TTS_SOURCE = "tts_source"    # 可合成语音的源（txt / md）
CAP_VECTOR = "vector"            # 矢量图（svg）
CAP_MEDIA_IMAGE = "media_image"  # 媒体引擎里的图像族（含 gif，互转位图/矢量）
CAP_IMAGE_TO_DOC = "image_to_doc"  # 可走 图片→文档 路径
