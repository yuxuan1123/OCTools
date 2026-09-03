"""
octool/main.py  ─  应用启动入口
──────────────────────────────── ㄧ
创建 QApplication 后全局安装滚轮阻断（no_wheel_filter），
然后启动主窗口。
"""

import sys
import os

# 确保项目根目录在 sys.path 中，便于 ui.import 生效
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
    app = QApplication(sys.argv)

    # 全局屏蔽 ComboBox/SpinBox/Slider 等的悬浮滚轮误操作
    no_wheel_filter.install()

    # 应用已保存的全局 UI 风格（主题/缩放/自定义），启动不广播避免页面提前重建
    apply_theme(app, presets.load_app_settings() or {}, notify=False)

    # 设置全局任务栏图标（yin-yang.svg），染色为前景色保证可见
    icon_path = os.path.join(project_root, "resources", "icons", "yin-yang.svg")
    if os.path.exists(icon_path):
        icon = _tinted_svg_icon(icon_path, "#1F2430", 32)
        if not icon.isNull():
            app.setWindowIcon(icon)

    # 复用现有主窗口
    from ui.main_window import MainApp
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()



