"""
OCTools/plugins/_shared
────────────────────────
共享设置弹窗库（非插件，不参与插件扫描）。

被多个插件 manifest 的 settings 段共同引用的弹窗类放在这里：
  - set_tts.py            语音合成（TTS）参数窗口  → SetTts
  - set_stt.py            语音识别参数窗口          → SetStt
  - set_image_docx.py     图片 → DOCX 排版选项窗口   → SetImageDocx
  - set_pdf_docx.py       PDF → DOCX 转换方式窗口    → SetPdfDocx

弹窗基类 OptionsDialogBase 保留在主进程 ui/options/_base.py，
此处各 set_*.py 通过 `from ui.options._base import OptionsDialogBase` 引用。
"""
