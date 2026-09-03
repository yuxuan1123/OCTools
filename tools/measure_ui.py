"""离屏量取主窗口实际布局几何，用于评估 UI 一致性（不依赖看图）。

检查项：
  1. 配置声明值 vs 实际渲染值（layout / sidebar / splitter / titlebar）
  2. 同类控件的真实高度是否统一（输入框 / 按钮 / 下拉框）
  3. 可见控件的裁切与文字溢出
"""
import os
import sys
from collections import Counter, defaultdict

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (  # noqa: E402
    QApplication, QLabel, QPushButton, QLineEdit, QComboBox, QTextEdit,
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
    """Qt 的 isHidden() 只看自身，需向上追溯父级是否可见。"""
    while w is not None:
        if w.isHidden() or (hasattr(w, "isVisible") and not w.isVisible()):
            return False
        w = w.parent()
    return True


def main():
    app = QApplication(sys.argv)
    print(f"font: {_load_font(app)}")

    from config import presets
    from ui.theme import apply_theme
    st = presets.load_app_settings() or {}
    apply_theme(app, st, notify=False)

    from ui.main_window import MainApp
    m = MainApp()
    win = m.window
    win.show()
    app.processEvents()

    lay = C.section("layout")
    sp_cfg = C.section("split").get("splitter", {})
    sb_cfg = C.section("sidebar")
    tb_cfg = C.section("titlebar")

    print("\n──────── A. 配置声明 vs 实际渲染 ────────")
    rows = [
        ("窗口默认尺寸", f"{lay.get('window_w')}x{lay.get('window_h')}",
         f"{win.width()}x{win.height()}", "layout.window_w/h 驱动"),
        ("窗口最小尺寸", f"{lay.get('window_min_w')}x{lay.get('window_min_h')}",
         f"{win.minimumWidth()}x{win.minimumHeight()}",
         "layout.window_min_w/h 驱动"),
        ("侧栏宽度", str(lay.get("sidebar_w")), str(m.sidebar.width()),
         f"layout.sidebar_w 覆盖 splitter.sizes[0]"),
        ("分割比例（左栏固定）", str(sp_cfg.get("sizes", [None])[0]),
         str(m.window._splitter.sizes()[0]), "stretch=[0,1]：左栏固定，右栏自适应"),
        ("顶栏高度", str(tb_cfg.get("top", {}).get("titlebar", {}).get("height")),
         str(m.window.top_bar.height()), "一致"),
        ("底栏高度", str(tb_cfg.get("bottom", {}).get("titlebar", {}).get("height")),
         str(m.window.bottom_bar.height()), "一致"),
        ("导航按钮高", str(sb_cfg.get("button", {}).get("fixed_height")),
         str(m.sidebar.findChildren(QPushButton)[0].height()) if m.sidebar.findChildren(QPushButton) else "?",
         "见下方详情"),
    ]
    for k, cfg, act, note in rows:
        mark = "✔" if cfg == act else "✘"
        print(f"  {mark} {k:12} 配置={cfg:12} 实际={act:12} ({note})")

    b0 = m.sidebar.findChildren(QPushButton)[0]
    print(f"\n  导航按钮详情: geometry={b0.width()}x{b0.height()}  "
          f"sizeHint={b0.sizeHint().width()}x{b0.sizeHint().height()}  "
          f"min={b0.minimumHeight()} max={b0.maximumHeight()}  font={b0.font().pointSize()}px")

    print("\n──────── B. 控件高度一致性（全部 5 个页面，仅可见控件）────────")
    heights = defaultdict(Counter)
    btn_by_name = defaultdict(Counter)
    for info in m.sidebar.tab_infos:
        m._switch_to(info["name"], info["class_name"], info.get("module_path"))
        app.processEvents()
        w = m._right_widgets.get(info["class_name"])
        if w is None:
            continue
        for cls, key in ((QLineEdit, "QLineEdit"), (QPushButton, "QPushButton"),
                         (QComboBox, "QComboBox"), (QTextEdit, "QTextEdit")):
            for ctl in w.findChildren(cls):
                if visible(ctl):
                    heights[key][ctl.height()] += 1
                    if cls is QPushButton:
                        btn_by_name[ctl.objectName() or "(匿名)"][ctl.height()] += 1
    std_h, cta_h = C.size("btn_h"), C.size("cta_h")
    for key in ("QLineEdit", "QPushButton", "QComboBox", "QTextEdit"):
        c = heights.get(key)
        if not c:
            print(f"  {key:12} (无可见实例)")
            continue
        dist = "  ".join(f"{h}px×{n}" for h, n in sorted(c.items()))
        if len(c) == 1:
            verdict = "统一"
        elif key == "QPushButton" and set(c) <= {std_h, cta_h}:
            verdict = f"统一（{std_h}px 标准 + {cta_h}px 主操作 CTA，有意分层）"
        else:
            verdict = f"⚠ {len(c)} 种高度"
        print(f"  {key:12} {dist:44} {verdict}")

    if len(heights.get("QPushButton", {})) > 1:
        print("\n  QPushButton 按 objectName 拆分：")
        for name in sorted(btn_by_name):
            dist = "  ".join(f"{h}px×{n}" for h, n in sorted(btn_by_name[name].items()))
            print(f"    #{name:14} {dist}")

    print("\n──────── C. 可见控件裁切 / 文字溢出 ────────")
    total_clip = total_of = 0
    for info in m.sidebar.tab_infos:
        m._switch_to(info["name"], info["class_name"], info.get("module_path"))
        app.processEvents()
        w = m._right_widgets.get(info["class_name"])
        if w is None:
            continue
        issues = []
        for ctl in w.findChildren(QLabel):
            if not visible(ctl) or not ctl.text() or "\n" in ctl.text() or ctl.wordWrap():
                continue
            need = ctl.fontMetrics().horizontalAdvance(ctl.text())
            if ctl.width() > 0 and need > ctl.width() * 1.02:
                issues.append(f"文字溢出 需{need}>实{ctl.width()} '{ctl.text()[:30]}'")
        for ctl in w.findChildren(QPushButton):
            if not visible(ctl):
                continue
            h = ctl.sizeHint()
            if h.width() > 0 and ctl.width() < h.width() - 1:
                issues.append(f"按钮裁切 {ctl.objectName() or 'QPushButton'} 需{h.width()}>实{ctl.width()} '{ctl.text()[:16]}'")
        total_of += len(issues)
        flag = "✔ 无" if not issues else f"⚠ {len(issues)} 处"
        print(f"  {info['name']:4} {flag}")
        for s in issues[:6]:
            print(f"        - {s}")
    print(f"\n  合计可见控件问题: {total_of}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
