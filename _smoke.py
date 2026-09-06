# -*- coding: utf-8 -*-
"""临时冒烟测试：QComboBox→Combo 迁移后关键页面可正常实例化"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication

from ui.ui_component.combo_component import Combo, DescComboBox
from config import presets

app = QApplication([])

ok = []

# 1) Combo 兼容原生写法
w = Combo()                      # QComboBox()
w2 = Combo(None)                 # QComboBox(None)
from PySide6.QtWidgets import QWidget
host = QWidget()
w3 = Combo(host)                 # QComboBox(parent) 位置参数
assert w3.parent() is host
w4 = Combo(["a", "b"], default="a", parent=host)
assert w4.parent() is host and w4.currentText() == "a"
# 类属性常量继承（项目代码均为类访问，如 Combo.NoInsert）
from PySide6.QtWidgets import QComboBox
assert Combo.NoInsert == QComboBox.NoInsert
ok.append("Combo 兼容构造")

# 2) 终端可视化参数
from PySide6.QtCore import Qt
from plugins.terminal.visual_dialog import VisualParamDialog
dlg = VisualParamDialog()
dlg.show()
items = dlg.type_list.findItems("git", Qt.MatchFlag.MatchStartsWith)
dlg.type_list.setCurrentItem(items[0])
assert dlg.subcmd_combo.currentText() == "clone"
dlg.subcmd_combo.setCurrentText("commit")
assert dlg.output_area.toPlainText().startswith("git commit")
ok.append("visual_dialog 子命令")

# 3) 终端 Tab
from plugins.terminal.tab_terminal import TabTerminal
t = TabTerminal()
assert t.shell_combo is not None
ok.append("tab_terminal")

# 4) 插件页
from ui.tabs.tab_plugin import TabPlugin
TabPlugin()
ok.append("tab_plugin")

# 5) TTS 设置页（含 Combo(preset_row) 位置参数）
from config.tts_config import TtsConfig
from plugins._shared.set_tts import SetTts
SetTts(config=TtsConfig())
ok.append("set_tts")

# 6) 翻译设置页
from config.translator_config import TranslatorConfig
from plugins.translation.set_translator import SetTranslator
SetTranslator(config=TranslatorConfig())
ok.append("set_translator")

# 7) 格式设置页
from ui.tabs.tab_component.set_format import SetFormat
SetFormat()
ok.append("set_format")

# 8) UI 设置页
from ui.options.set_ui import Setui
Setui(config=None)
ok.append("set_ui")

# 9) 卡片选项（import 级验证；实例化需完整 page 上下文，位置参数兼容已由 set_tts 覆盖）
import importlib
importlib.import_module("plugins.merge.card_target")
importlib.import_module("plugins.conversion.card_target")
importlib.import_module("plugins.tree.card_options")
importlib.import_module("ui.tabs.tab_component.docx_format_card")
ok.append("card_target(merge/conversion)")

# 10) 其余设置页
from plugins._shared.set_stt import SetStt
SetStt(config={})
from plugins._shared.set_pdf_docx import SetPdfDocx
SetPdfDocx(config={})
from plugins._shared.set_image_docx import SetImageDocx
SetImageDocx(config={})
from plugins.translation.set_screen_region import SetScreenRegion
SetScreenRegion(config={})
from plugins.translation.card_direction import CardDirection
CardDirection(config={})
ok.append("其余设置页")

for item in ok:
    print("PASS:", item)
print("ALL OK")
