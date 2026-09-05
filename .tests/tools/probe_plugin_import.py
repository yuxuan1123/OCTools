"""端到端验证 tab_plugin 重构：卸载按钮可见性 + 两输入导入 + 清单分类。

不污染真实插件目录：用临时目录 monkeypatch PLUGINS_DIR / PLUGIN_MANIFESTS_DIR，
并把 QMessageBox 替换为非阻塞桩。
"""
import os
import sys
import json
import tempfile
import shutil

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication, QPushButton, QMessageBox  # noqa: E402

from config.ui_config import CONFIG as C  # noqa: E402


def main():
    app = QApplication(sys.argv)

    import ui.tabs.tab_plugin as tp
    from config import presets
    from ui.theme import apply_theme
    st = presets.load_app_settings() or {}
    apply_theme(app, st, notify=False)

    tmp = tempfile.mkdtemp(prefix="OCTools_probe_")
    tmp_plugins = os.path.join(tmp, "plugins")
    tmp_manifests = os.path.join(tmp_plugins, "manifests")
    os.makedirs(tmp_manifests, exist_ok=True)

    # monkeypatch 目录 + 安全桩
    tp.PLUGINS_DIR = lambda: tmp_plugins
    tp.PLUGIN_MANIFESTS_DIR = lambda: tmp_manifests
    tp._ensure_dirs = lambda: None
    tp._purge_plugin_modules = lambda name: None

    class _FakeMB:
        @staticmethod
        def question(*a, **k):
            from PySide6.QtWidgets import QMessageBox
            return QMessageBox.StandardButton.Yes
        @staticmethod
        def warning(*a, **k):
            return QMessageBox.StandardButton.Ok
        @staticmethod
        def information(*a, **k):
            return QMessageBox.StandardButton.Ok
    tp.QMessageBox = _FakeMB

    tab = tp.TabPlugin()
    tab.show()
    app.processEvents()

    print("══ A. 真实列表卸载按钮可见性 ══")
    real = [b for b in tab.findChildren(QPushButton) if b.text() == "卸载"]
    print(f"  真实列表「卸载」按钮数: {len(real)}")
    for b in real:
        print(f"    visible={b.isVisible()} hidden={b.isHidden()} "
              f"geom={b.geometry().width()}x{b.geometry().height()} "
              f"objectName={b.objectName()!r}")

    print("\n══ B. 文件夹扫描分类 ══")
    src = os.path.join(tmp, "src")
    os.makedirs(src, exist_ok=True)
    open(os.path.join(src, "tab_demo.py"), "w", encoding="utf-8").write(
        "from PySide6.QtWidgets import QWidget\nclass DemoTab(QWidget):\n    pass\n")
    open(os.path.join(src, "set_demo.py"), "w", encoding="utf-8").write(
        "class SetDemo:\n    pass\n")
    open(os.path.join(src, "helper.py"), "w", encoding="utf-8").write("# helper\n")
    open(os.path.join(src, "readme.md"), "w", encoding="utf-8").write("note\n")

    tf, sf, of = tab._scan_plugin_folder(src)
    print(f"  tab_*.py = {tf}")
    print(f"  set_*.py = {sf}")
    print(f"  other    = {of}")
    assert tf == ["tab_demo.py"], tf
    assert sf == ["set_demo.py"], sf
    assert of == ["helper.py", "readme.md"], of

    print("\n══ C. 主 tab 文件解析 ══")
    m1 = tab._resolve_main_tab_file(src, "DemoTab")
    m2 = tab._resolve_main_tab_file(src, "")
    print(f"  按 class_name=DemoTab -> {m1}")
    print(f"  无 class_name（唯一 tab_*.py）-> {m2}")
    assert m1 == "tab_demo.py" and m2 == "tab_demo.py"

    print("\n══ D. 导入清单预览 ══")
    json_path = os.path.join(tmp, "demo.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"name": "演示插件", "class_name": "DemoTab",
                   "order": 7, "settings": [{"x": 1}]}, f, ensure_ascii=False)
    tab.folder_edit.setText(src)
    tab.json_edit.setText(json_path)
    tab._update_preview()
    app.processEvents()
    # 收集预览区文本
    pv_texts = []
    for lbl in tab._pv_host.findChildren(__import__("PySide6.QtWidgets", fromlist=["QLabel"]).QLabel):
        if lbl.text():
            pv_texts.append(lbl.text())
    print("  预览内容行:")
    for t in pv_texts:
        print(f"    - {t}")
    assert any("tab_demo.py" in t for t in pv_texts), "预览未显示主类"
    assert any("set_demo.py" in t for t in pv_texts), "预览未显示 set"
    assert tab._pv_status.property("ok") == "1", f"状态应为可导入, 实际={tab._pv_status.text()}"

    print("\n══ E. 执行导入并校验清单 ══")
    ok = tab._install_plugin(src, json_path)
    print(f"  _install_plugin 返回: {ok}")
    dest = os.path.join(tmp_manifests, "demo.json")
    assert os.path.isfile(dest), "清单未写出"
    with open(dest, "r", encoding="utf-8") as f:
        man = json.load(f)
    print(f"  写出的清单: name={man['name']!r} class={man['class_name']!r} "
          f"module={man['module_path']!r}")
    print(f"  files = {man['files']}")
    assert man["files"]["tab"] == ["tab_demo.py"]
    assert man["files"]["set"] == ["set_demo.py"]
    assert "helper.py" in man["files"]["other"]

    print("\n══ F. 已安装卡片显示文件清单 + 卸载按钮 ══")
    tab._render_plugins()
    app.processEvents()
    # 找刚安装的卡片：含「演示插件」标题
    from PySide6.QtWidgets import QLabel
    names = [l.text() for l in tab.findChildren(QLabel) if l.text() == "演示插件"]
    print(f"  已安装卡片标题出现次数: {len(names)}")
    uninstall_btns = [b for b in tab.findChildren(QPushButton) if b.text() == "卸载"]
    print(f"  卸载按钮总数: {len(uninstall_btns)} (含真实 tree 插件 + 本次 demo)")
    for b in uninstall_btns:
        print(f"    visible={b.isVisible()} geom={b.geometry().width()}x{b.geometry().height()} "
              f"objectName={b.objectName()!r}")

    # 清理
    shutil.rmtree(tmp, ignore_errors=True)
    print("\n══ G. 导入清单预览可收缩 ══")
    tab._toggle_preview(False)
    app.processEvents()
    print(f"  折叠后 _pv_host.visible={tab._pv_host.isVisible()} "
          f"_pv_status.visible={tab._pv_status.isVisible()} "
          f"toggle_text={tab._pv_toggle.text()!r}")
    assert tab._pv_host.isVisible() is False
    assert tab._pv_status.isVisible() is False
    assert "▸" in tab._pv_toggle.text()
    tab._toggle_preview(True)
    app.processEvents()
    print(f"  展开后 _pv_host.visible={tab._pv_host.isVisible()} "
          f"toggle_text={tab._pv_toggle.text()!r}")
    assert tab._pv_host.isVisible() is True
    assert "▾" in tab._pv_toggle.text()

    print("\nALL_CHECKS_PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
