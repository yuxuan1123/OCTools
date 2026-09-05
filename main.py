"""
OCTools/main.py  ─  应用启动入口
──────────────────────────────── ㄧ
以管理员身份启动
创建 QApplication 后全局安装滚轮阻断（no_wheel_filter），
然后启动主窗口。
"""

import sys
import os

# 确保项目根目录在 sys.path 中
current_path = os.path.abspath(__file__)
project_root = os.path.dirname(current_path)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtWidgets import QApplication  # noqa: E402
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor  # noqa: E402
from PySide6.QtCore import Qt, QRectF  # noqa: E402
from PySide6.QtSvg import QSvgRenderer  # noqa: E402

from config import presets  # noqa: E402
from ui.widgets import no_wheel_filter  # noqa: E402
from ui.theme import apply_theme


def _tinted_svg_icon(path: str, color: str, size: int = 32) -> QIcon:
    """用指定颜色渲染 SVG → QIcon（解决 currentColor 在任务栏不可见）。"""
    try:
        r = QSvgRenderer(path)
    except Exception:
        return QIcon()
    if not r.isValid():
        return QIcon()
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    r.render(p, QRectF(0, 0, size, size))
    p.setCompositionMode(QPainter.CompositionMode_SourceIn)
    p.fillRect(pix.rect(), QColor(color))
    p.end()
    return QIcon(pix)


def main():
    import ctypes
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except AttributeError:
        is_admin = False  # 非 Windows 系统忽略
    if not is_admin:
        # 重新以管理员身份启动当前脚本
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()
    app = QApplication(sys.argv)

    # 全局屏蔽 ComboBox/SpinBox/Slider 等的悬浮滚轮误操作
    no_wheel_filter.install()

    # 全局 UI 风格（主题/缩放/自定义），启动不广播避免页面提前重建
    apply_theme(app, presets.load_app_settings() or {}, notify=False)

    # 设置全局任务栏图标（yin-yang.svg）
    icon_path = os.path.join(project_root, "resources", "icons", "yin-yang.svg")
    if os.path.exists(icon_path):
        icon = _tinted_svg_icon(icon_path, "#1F2430", 32)
        if not icon.isNull():
            app.setWindowIcon(icon)

    # 外部插件管理器：启动扫描/安装/子进程调度，退出时清理所有子进程
    from services.ext_plugins.manager import PluginManager
    _plugin_mgr = PluginManager.instance()
    app.aboutToQuit.connect(_plugin_mgr.shutdown)
    _plugin_mgr.start()

    # 复用现有主窗口
    from ui.main_window import MainApp
    main_app = MainApp()
    main_app.show()

    # 主程序 UI 已显示：按翻译设置后台预加载 OCR / 翻译模型（失败静默，不阻塞启动）
    try:
        from plugins.translation.preload import start_preload
        start_preload(presets.load_last_translator_config(), timing="startup")
    except Exception:
        pass

    sys.exit(app.exec())


if __name__ == "__main__":
    main()



