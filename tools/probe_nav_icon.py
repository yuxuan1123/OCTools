"""量取导航图标选中/未选中两态的实际像素颜色，确认选中态不再是白色。"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication  # noqa: E402
from PySide6.QtGui import QPixmap  # noqa: E402

from config.ui_config import CONFIG as C  # noqa: E402
from ui.icon_res import nav_icon, NAV_ICON_SIZE  # noqa: E402


def sample(name, active):
    icon = nav_icon(name, active)
    pm = icon.pixmap(NAV_ICON_SIZE, NAV_ICON_SIZE)
    img = pm.toImage()
    # 取所有非透明像素的平均色（图标为单色 SVG 重染，非透明像素应同色）
    r = g = b = n = 0
    for y in range(img.height()):
        for x in range(img.width()):
            c = img.pixelColor(x, y)
            if c.alpha() > 0:
                r += c.red(); g += c.green(); b += c.blue(); n += 1
    if n == 0:
        return (0, 0, 0)
    return (r // n, g // n, b // n)


def main():
    app = QApplication(sys.argv)
    from config import presets
    from ui.theme import apply_theme
    apply_theme(app, presets.load_app_settings() or {}, notify=False)

    fg = C.color("nav_active_fg")
    inactive = sample("转换", False)
    active = sample("转换", True)
    print(f"主题 nav_active_fg = {fg}")
    print(f"  未选中图标中心像素 ≈ {inactive}  (应是灰色)")
    print(f"  选中图标中心像素   ≈ {active}  (应≈{fg}，且绝不是白色 255,255,255)")
    # 判定：选中态不能接近纯白
    near_white = all(v > 230 for v in active)
    print(f"  选中态接近白色? {near_white}  -> {'❌ 仍看不见' if near_white else '✔ 可见'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
