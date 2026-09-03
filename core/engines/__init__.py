"""
OCTools/core/engines/__init__.py
───────────────────────────────────────────────
核心引擎层：各类格式与算法的底层能力封装。

按能力拆分的引擎文件：
  - image_engine.py          图像格式互转（Pillow / cairosvg）
  - audio_engine.py          音频解码、编码、重采样（ffmpeg）
  - video_engine.py          视频格式转换与封装（ffmpeg）
  - document_engine.py       文本类文档处理（docx / pdf / md / txt / rtf / wps）
  - spreadsheet_engine.py    表格类文件读写（xlsx / csv / json / yaml）
  - presentation_engine.py   演示文稿处理（pptx / html / odp）
  - ocr_engine.py            OCR 文字识别（PaddleOCR）
  - speech_engine.py         语音识别 ASR（SenseVoice / Whisper）
  - tts_engine.py            文本转语音（edge-tts / kokoro / moss）
  - translation_engine.py    机器翻译接口（hy-mt / opus-mt）

原子能力引擎（互不依赖，供业务层 recipes 直接组合）：
  - screenshot_engine.py     屏幕截图（区域 → PIL Image）
  - audio_capture_engine.py  录音采集（WASAPI 回环 / 麦克风 → PCM 帧）
"""
