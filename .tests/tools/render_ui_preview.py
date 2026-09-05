"""
OCTools/tools/render_ui_preview.py
───────────────────────────────────────────────
离屏渲染 UI 预览图（无需显示器，用于视觉走查 / 回归对比）

用法：
  python tools/render_ui_preview.py [输出目录]

产出：
  <输出目录>/00_main.png      主窗口（当前默认 tab）
  <输出目录>/NN_<tab>.png     各 tab 页面
"""

import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402
from PySide6.QtCore import Qt, QTimer  # noqa: E402


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        _PROJECT_ROOT, "tools", "ui_preview")
    os.makedirs(out_dir, exist_ok=True)

    from config import presets
    from ui.theme import apply_theme
    from ui.main_window import MainApp

    app = QApplication(sys.argv)
    apply_theme(app, presets.load_app_settings() or {}, notify=False)

    # offscreen 平台下常丢中文，手动加载系统字体文件
    from PySide6.QtGui import QFontDatabase, QFont
    for p in (r"C:\Windows\Fonts\msyh.ttc",
              r"C:\Windows\Fonts\simhei.ttf",
              r"C:\Windows\Fonts\msyhbd.ttc"):
        if os.path.exists(p):
            fid = QFontDatabase.addApplicationFont(p)
            if fid >= 0:
                fams = QFontDatabase.applicationFontFamilies(fid)
                if fams:
                    app.setFont(QFont(fams[0], 10))
                    print(f"  font: {fams[0]} <- {p}")
                    break

    mw = MainApp()
    win = mw.window
    win.resize(1280, 820)
    win.show()
    app.processEvents()

    # 主窗口整体
    win.grab().save(os.path.join(out_dir, "00_main.png"))

    # 逐个 tab 渲染
    for i, info in enumerate(mw.sidebar.tab_infos, start=1):
        name = info["name"]
        try:
            w = mw._get_or_create_widget(
                info["class_name"], info.get("module_path"))
            mw._switch_to(name, info["class_name"], info.get("module_path"))
            app.processEvents()
            win.grab().save(os.path.join(out_dir, f"{i:02d}_{name}.png"))
            print(f"  OK  {name:6s} -> {i:02d}_{name}.png   ({type(w).__name__})")
        except Exception as e:
            print(f"FAIL  {name}: {type(e).__name__}: {e}")

    print(f"\n输出目录: {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
