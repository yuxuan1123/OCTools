"""按钮高度诊断：定位 QPushButton 高度不一致的具体来源。

对主窗口内所有可见 QPushButton 逐个输出：
  objectName / 文本 / 实际高 / sizeHint高 / min高 / max高 / 垂直 sizePolicy / 父链

用于判断高度是被 setFixedHeight、QSS padding、还是 sizePolicy 撑开的。
"""
import os
import sys
from collections import defaultdict

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (  # noqa: E402
    QApplication, QPushButton, QSizePolicy,
)
from PySide6.QtGui import QFontDatabase, QFont  # noqa: E402

from config.ui_config import CONFIG as C  # noqa: E402


def _load_font(app):
    for p in (r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf"):
        if os.path.exists(p):
            fid = QFontDatabase.addApplicationFont(p)
            if fid >= 0:
                fams = QFontDatabase.applicationFontFamilies(fid)
                if fams:
                    app.setFont(QFont(fams[0], 10))
                    return fams[0]
    return ""


def visible(w):
    while w is not None:
        if w.isHidden() or (hasattr(w, "isVisible") and not w.isVisible()):
            return False
        w = w.parent()
    return True


def parent_chain(w, depth=3):
    parts = []
    p = w.parent()
    for _ in range(depth):
        if p is None:
            break
        name = p.objectName() or type(p).__name__
        parts.append(name)
        p = p.parent()
    return "/".join(parts) if parts else "(top)"


def main():
    app = QApplication(sys.argv)
    _load_font(app)

    from config import presets
    from ui.theme import apply_theme
    st = presets.load_app_settings() or {}
    apply_theme(app, st, notify=False)

    from ui.main_window import MainApp
    m = MainApp()
    m.window.resize(1100, 760)
    m.window.show()
    app.processEvents()

    rows = defaultdict(list)
    for info in m.sidebar.tab_infos:
        m._switch_to(info["name"], info["class_name"], info.get("module_path"))
        app.processEvents()
        w = m._right_widgets.get(info["class_name"])
        if w is None:
            continue
        for b in w.findChildren(QPushButton):
            if not visible(b):
                continue
            pol = b.sizePolicy().verticalPolicy()
            pol_name = {
                QSizePolicy.Fixed: "Fixed", QSizePolicy.Minimum: "Minimum",
                QSizePolicy.Maximum: "Maximum", QSizePolicy.Preferred: "Preferred",
                QSizePolicy.Expanding: "Expanding",
                QSizePolicy.MinimumExpanding: "MinExpanding",
                QSizePolicy.Ignored: "Ignored",
            }.get(pol, str(pol))
            rec = (
                b.height(), b.sizeHint().height(), b.minimumHeight(),
                b.maximumHeight(), pol_name, b.text()[:18],
                parent_chain(b), info["name"],
                "内联" if b.styleSheet() else "",
            )
            rows[(b.objectName() or "(匿名)", b.height())].append(rec)

    print(f"{'objectName':16} {'高':>4} {'hint':>5} {'min':>4} {'max':>5} "
          f"{'策略':12} {'文本':20} 父链")
    print("-" * 118)
    for (name, h) in sorted(rows, key=lambda k: (k[1], k[0])):
        recs = rows[(name, h)]
        r = recs[0]
        inline = sum(1 for x in recs if x[8])
        tail = f" ×{len(recs)}" if len(recs) > 1 else ""
        warn = f" [内联×{inline}]" if inline else ""
        print(f"#{name:15} {r[0]:>4} {r[1]:>5} {r[2]:>4} {r[3]:>5} "
              f"{r[4]:12} {r[6]:20} {r[7]}/{r[6+0]}{tail}{warn}")

    print("\n── 明细（同组只列前 2 条）──")
    for (name, h) in sorted(rows, key=lambda k: (k[1], k[0])):
        for r in rows[(name, h)][:2]:
            print(f"  #{name:14} h={r[0]:3} hint={r[1]:3} min={r[2]:3} max={r[3]:4} "
                  f"{r[4]:11} '{r[5]}' ← {r[6]} [{r[7]}]")

    print(f"\n全局 QPushButton: btn_h={C.size('btn_h')} "
          f"cta_h={C.size('cta_h')} "
          f"sidebar.button.fixed_height="
          f"{C.section('sidebar').get('button', {}).get('fixed_height')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
