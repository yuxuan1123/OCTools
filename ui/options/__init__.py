"""
OCTools/ui/options/__init__.py
───────────────────────────────
设置弹窗基类与主进程内置弹窗（命名规范 set_xxx）：
  - _base.py     设置弹窗基类（OptionsDialogBase），供主进程与插件弹窗共用
  - set_ui.py    全局 UI 风格（主题/字体/颜色/尺寸）窗口（设置页核心，不随插件迁移）

已按分类迁出到外部 plugins/ 的弹窗：
  - set_translator.py / set_screen_region.py → plugins/translation/
  - set_tts.py / set_stt.py / set_image_docx.py / set_pdf_docx.py → plugins/_shared/
"""
