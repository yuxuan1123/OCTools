"""
OCTools/ui/ui_component/hotkeys.py
───────────────────────────────────────────────
按钮组件
"""
import os
import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton

from config.ui_config import CONFIG as C


def _project_root() -> str:
    """项目根目录：源码=仓库根；打包后=_internal。

    打包后模块在 PYZ 内，__file__ 指向 _internal/...，用 sys._MEIPASS 更稳妥。
    """
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return os.path.normpath(meipass)
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
    )


def resource_path(path: str) -> str:
    """相对项目根路径→绝对路径（绝对路径原样返回）。

    打包后项目根=_internal，调用方用 "resources/icons/..." 形式。
    """
    if not path:
        return path
    if os.path.isabs(path):
        return path
    return os.path.normpath(os.path.join(_project_root(), path))


def load_icon_for_button(btn: QPushButton, symbol: str, icon_size: int = 20):
    """给按钮设置图标（文件路径）或文字（符号）。

    文件存在则设图标并清空文本，否则设文本并清空图标。
    """
    if symbol and any(symbol.lower().endswith(ext) for ext in ['.svg', '.png', '.ico', '.jpg']):
        fp = resource_path(symbol)
        if os.path.exists(fp):
            btn.setIcon(QIcon(fp))
            btn.setText("")
            btn.setIconSize(QSize(icon_size, icon_size))
            return
    btn.setText(symbol)
    btn.setIcon(QIcon())

def set_button_icon(btn: QPushButton, icon_path: str, icon_size: int = 20):
    """设置按钮图标（不设文本），文件不存在则清空图标和文本。"""
    full_path = resource_path(icon_path)
    if os.path.exists(full_path):
        btn.setIcon(QIcon(full_path))
        btn.setText("")
        btn.setIconSize(QSize(icon_size, icon_size))
    else:
        btn.setIcon(QIcon())
        btn.setText("")


def create_function_entry_button(
    text: str,
    on_click=None,
    fixed_width: int = 110,
    fixed_height: int = None,
    checkable: bool = False,
) -> QPushButton:
    """侧栏功能入口按钮。

    外观由全局 QSS 的 QPushButton#navBtn 承载，此处只设尺寸、光标与信号。
    fixed_width<=0 时宽度自适应。
    """
    btn = QPushButton(text)
    if fixed_height is None:
        fixed_height = C.size("btn_h")
    btn.setObjectName("navBtn")
    if fixed_width and fixed_width > 0:
        btn.setFixedSize(fixed_width, fixed_height)
    else:
        btn.setFixedHeight(fixed_height)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setCheckable(checkable)

    if on_click is not None:
        btn.clicked.connect(on_click)

    return btn