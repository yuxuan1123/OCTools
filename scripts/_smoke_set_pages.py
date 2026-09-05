# -*- coding: utf-8 -*-
"""设置弹窗统一化冒烟测试：
实例化所有 set_*.py 弹窗（offscreen），验证：
  1. 继承 OptionsDialogBase
  2. 统一尺寸策略已生效（调用了 fit_size，窗口尺寸在合理区间）
  3. 页面可正常构建（无异常）
  4. 底部按钮条存在（build_buttons 产物）
"""
import importlib.util
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from PySide6.QtWidgets import QApplication, QPushButton

app = QApplication.instance() or QApplication(sys.argv)

from ui.options._base import OptionsDialogBase

CASES = [
    # (文件路径, 配置工厂)
    (r"plugins\translation\set_screen_region.py", "config.screen_region_config:ScreenRegionConfig"),
    (r"plugins\translation\set_translator.py", "config.translator_config:TranslatorConfig"),
    (r"plugins\_shared\set_pdf_docx.py", "config.pdf_docx_config:PdfDocxConfig"),
    (r"plugins\_shared\set_image_docx.py", "config.image_docx_config:ImageDocxConfig"),
    (r"plugins\_shared\set_stt.py", "config.stt_config:SttConfig"),
    (r"plugins\_shared\set_tts.py", "config.tts_config:TtsConfig"),
    (r"plugins\tree\set_tts.py", "config.tts_config:TtsConfig"),
    (r"ui\tabs\tab_component\set_format.py", "config.format_config:FormatConfig"),
    (r"ui\options\set_ui.py", None),
]


def load_module(path):
    full = os.path.join(ROOT, path)
    mod_name = "smoke_set_" + os.path.basename(path).replace(".py", "").replace("-", "_")
    spec = importlib.util.spec_from_file_location(mod_name, full)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_config(spec):
    if not spec:
        return None
    mod_name, cls_name = spec.split(":")
    m = __import__(mod_name, fromlist=[cls_name])
    return getattr(m, cls_name)()


def find_dialog_cls(mod):
    for name in dir(mod):
        obj = getattr(mod, name)
        if isinstance(obj, type) and issubclass(obj, OptionsDialogBase) and obj is not OptionsDialogBase:
            return obj
    return None


failures = []
for path, cfg_spec in CASES:
    tag = path
    try:
        mod = load_module(path)
        cls = find_dialog_cls(mod)
        cfg = make_config(cfg_spec)
        dlg = cls(cfg) if cfg is not None else cls()
        w, h = dlg.size().width(), dlg.size().height()
        # 底部按钮条：主布局里最后一个 QWidget 含「确定」按钮
        btns = dlg.findChildren(QPushButton)
        ok_btns = [b for b in btns if b.text() in ("确定", "完成", "保存")]
        assert ok_btns, "未找到确定/完成/保存按钮"
        assert w >= 480 and h >= 360, f"尺寸过小: {w}x{h}"
        assert w <= 1600 and h <= 1600, f"尺寸异常: {w}x{h}"
        print(f"[PASS] {tag:55s} {w}x{h}  按钮条✓")
        dlg.deleteLater()
    except Exception as e:
        failures.append((tag, repr(e)))
        print(f"[FAIL] {tag:55s} {e!r}")
    app.processEvents()

print()
if failures:
    print(f"共 {len(CASES)} 个弹窗，失败 {len(failures)} 个：")
    for tag, err in failures:
        print(f"  - {tag}: {err}")
    sys.exit(1)
print(f"全部 {len(CASES)} 个设置弹窗统一化验证通过。")
