"""PyInstaller runtime hook：设置 playwright 浏览器路径。

在主程序 main.py 之前执行，把 PLAYWRIGHT_BROWSERS_PATH 指向 exe 同目录的
ms-playwright/。用户后续把 chromium 内容放进该目录即生效（document_engine 的
MD→图片功能）。

源码运行时（非 frozen）不介入，保持 playwright 默认行为。
"""

import os
import sys

if getattr(sys, "frozen", False):
    _exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(_exe_dir, "ms-playwright")
