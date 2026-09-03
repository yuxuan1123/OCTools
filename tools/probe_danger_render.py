"""量取「卸载」按钮在不同 Qt 风格下的真实渲染像素，确认白底白字根因。

用法：
  STYLE=Windows      python tools/probe_danger_render.py
  STYLE=WindowsVista python tools/probe_danger_render.py
  (无 STYLE)         用默认风格（本机 offscreen 默认 Fusion）
"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication, QPushButton  # noqa: E402

from config.ui_config import CONFIG as C  # noqa: E402


def main():
    style = os.environ.get("STYLE", "")
    app = QApplication(sys.argv)
    if style:
        ok = app.setStyle(style)
        print(f"setStyle({style!r}) -> {ok}, 实际风格={app.style().objectName()}")
    else:
        print(f"默认风格={app.style().objectName()}")

    from config import presets
    from ui.theme import apply_theme
    st = presets.load_app_settings() or {}
    apply_theme(app, st, notify=False)

    btn = QPushButton("卸载")
    btn.setObjectName("danger")
    btn.show()
    app.processEvents()

    pix = btn.grab().toImage()
    cx, cy = pix.width() // 2, pix.height() // 2
    center = pix.pixelColor(cx, cy)
    # 采样按钮中心 5x5 平均，避免落在字上
    import struct
    rs = gs = bs = n = 0
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            x, y = cx + dx, cy + dy
            if 0 <= x < pix.width() and 0 <= y < pix.height():
                c = pix.pixelColor(x, y)
                rs += c.red(); gs += c.green(); bs += c.blue(); n += 1
    avg = (rs // n, gs // n, bs // n)
    print(f"按钮尺寸={btn.width()}x{btn.height()}  中心像素={center.name()}  "
          f"中心5x5均值=({avg[0]},{avg[1]},{avg[2]})")
    print(f"  danger 配置色: {C.color('danger')}  white: {C.color('white')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
