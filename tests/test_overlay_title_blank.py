"""
OCTools/tests/test_overlay_title_blank.py
───────────────────────────────────────────────
悬浮窗左上角标题应为空白（屏幕OCR / 屏幕翻译 / 屏幕实时翻译 / 屏幕字幕 / 语音翻译）。

需求：五个最终应用的悬浮窗左上角不显示任何文字。
实现：TranslateAppBase.OVERLAY_TITLE 默认 ""，`_create_overlay` 缺省用它；
NAME 仅作内部名（日志 / 可访问性），不再渲染到标题栏。

验证：
  1. 五个 app 创建 overlay 后 `overlay._title_text == ""`；
  2. 标题栏实际 QLabel 文本为空（不会回退成旧名称 / "None"）；
  3. NAME 内部名仍非空（日志依赖）。

用法：
  python tests/test_overlay_title_blank.py
退出码 0 = 全部通过；非 0 = 有失败。
"""

import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_PASS = 0
_FAIL = 0


def _check(name, fn):
    global _PASS, _FAIL
    try:
        fn()
        _PASS += 1
        print(f"  OK  {name}")
    except Exception as e:  # noqa: BLE001 - 回归测试需捕获一切异常
        _FAIL += 1
        print(f"FAIL  {name}: {type(e).__name__}: {e}")


def main() -> int:
    from PySide6.QtWidgets import QApplication

    app = QApplication([])

    from plugins.translation.tab_translation import TabTranslation
    from plugins.translation.registry import _APP_ROWS

    page = TabTranslation()
    page.show()
    app.processEvents()

    def _all_blank():
        for key, (cls, label, *_rest) in _APP_ROWS.items():
            a = cls(page, parent=page)
            ov = a._create_overlay()
            tl = ov._title_bar._title_label.text()
            assert ov._title_text == "", f"{key}: overlay 标题未清空（{ov._title_text!r}）"
            assert tl == "", f"{key}: 标题栏仍显示文字 {tl!r}"
            assert label, f"{key}: 内部名 NAME 不应为空（日志依赖）"

    _check("五个悬浮窗左上角标题均为空", _all_blank)

    print(f"\n结果: {_PASS} 通过, {_FAIL} 失败")
    return 1 if _FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
