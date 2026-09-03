import os
import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton

from config.ui_config import CONFIG as C


def _project_root() -> str:
    """项目根目录：源码 = 仓库根；打包后 = _internal（内建只读资源所在）。

    打包后模块在 PYZ 内，__file__ 指向 _internal/...，取 sys._MEIPASS 更稳妥。
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
    """相对项目根的路径 → 绝对路径（绝对路径原样返回）。

    打包后项目根 = _internal（内建 resources/ 等数据随其分发）；
    各调用方均使用 "resources/icons/..." 形式，故整体按项目根解析。
    """
    if not path:
        return path
    if os.path.isabs(path):
        return path
    return os.path.normpath(os.path.join(_project_root(), path))


def load_icon_for_button(btn: QPushButton, symbol: str, icon_size: int = 20):
    """给按钮设置图标（文件路径）或文字（符号）。"""
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
    """
    明确设置按钮图标（不设文本）。
    如果文件不存在，则清空图标和文本。
    """
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

    外观全部由全局 QSS 的 QPushButton#navBtn 规则承载（含 hover / checked /
    pressed 三态），此处只负责尺寸、光标与信号连接，保证主题切换即时生效。

    fixed_width <= 0 时宽度交给布局自适应（侧栏变宽后按钮随之填满）。
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