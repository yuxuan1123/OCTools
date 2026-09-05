# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, r"d:\Project\PythonProject\OCTools")
from PySide6.QtWidgets import QApplication
from PySide6.QtSvg import QSvgRenderer
app = QApplication([])

print("=== 1) cwd=OCTools, 相对路径 yin-yang.svg ===")
r = QSvgRenderer("resources/icons/yin-yang.svg")
print("valid:", r.isValid())

print("=== 2) 改 cwd 到子目录后, 相对路径 ===")
os.chdir(r"d:\Project\PythonProject\OCTools\plugins\translation")
r = QSvgRenderer("resources/icons/yin-yang.svg")
print("valid:", r.isValid())

print("=== 3) 绝对路径 + 不存在文件 ===")
r = QSvgRenderer(r"d:\Project\PythonProject\OCTools\resources\icons\nonexist.svg")
print("valid:", r.isValid())

print("=== 4) 相对路径 + 不存在文件 ===")
r = QSvgRenderer("resources/icons/nonexist.svg")
print("valid:", r.isValid())

print("=== 5) os.path.join(root, '') ===")
r = QSvgRenderer(os.path.join(r"d:\Project\PythonProject\OCTools", ""))
print("valid:", r.isValid())
