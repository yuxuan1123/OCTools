# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, r"d:\Project\PythonProject\OCTools")
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
app = QApplication([])
os.chdir(r"d:\Project\PythonProject\OCTools")

print("=== 1) QIcon(不存在svg) + 强制渲染 ===")
ic = QIcon(r"d:\Project\PythonProject\OCTools\resources\icons\nonexist.svg")
ic.pixmap(20, 20)
print("done")

print("=== 2) QIcon(相对路径, cwd改到translation) ===")
os.chdir(r"d:\Project\PythonProject\OCTools\plugins\translation")
ic = QIcon("resources/icons/yin-yang.svg")
ic.pixmap(20, 20)
print("done")

print("=== 3) QIcon(resource_path 拼出的正常绝对路径) ===")
from ui.ui_component.button_component import resource_path
p = resource_path("resources/icons/refresh.svg")
print("path:", p)
ic = QIcon(p)
ic.pixmap(20, 20)
print("done")

print("=== 4) QIcon(资源不存在但路径正常) ===")
os.chdir(r"d:\Project\PythonProject\OCTools")
p = resource_path("resources/icons/no-such-icon.svg")
print("path:", p)
ic = QIcon(p)
ic.pixmap(20, 20)
print("done")
