# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, r"d:\Project\PythonProject\OCTools")
os.chdir(r"d:\Project\PythonProject\OCTools")
from PySide6.QtWidgets import QApplication
app = QApplication([])

print("=== overlay demo ===")
from ui.ui_component.overlay import FloatingOverlay
ov = FloatingOverlay(buttons=["retry", "copy", "pin", "close"], title="", bg_color=None, font_size=14)
ov.show()
ov.set_result("Hello", "你好")
app.processEvents()
ov.grab()
print("overlay done")

print("=== TestWindow (split_titlebar) ===")
from ui.ui_component.split_titlebar import TestWindow
w = TestWindow()
w.show()
app.processEvents()
w.grab()
print("testwindow done")
