# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, r"d:\Project\PythonProject\OCTools")
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QPixmap
app = QApplication([])

print("=== 1) QIcon(绝对路径, 不存在) ===")
QIcon(r"d:\Project\PythonProject\OCTools\resources\icons\nonexist.svg")
print("done")

print("=== 2) QPixmap(绝对路径, 不存在) ===")
QPixmap(r"d:\Project\PythonProject\OCTools\resources\icons\nonexist.svg")
print("done")

print("=== 3) QIcon(相对路径, 不存在, cwd=OCTools) ===")
os.chdir(r"d:\Project\PythonProject\OCTools")
QIcon("resources/icons/nonexist.svg")
print("done")

print("=== 4) QIcon(路径含\\x00) ===")
QIcon("d:\\Project\\PythonProject\\OCTools\\\x00")
print("done")

print("=== 5) QPixmap(路径末尾单字符?) ===")
QPixmap("d:\\Project\\PythonProject\\OCTools\\" + "?")
print("done")

print("=== 6) QIcon(单字符?) ===")
QIcon("?")
print("done")
