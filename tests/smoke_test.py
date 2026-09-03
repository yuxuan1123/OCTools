"""
octool/tests/smoke_test.py
───────────────────────────────────────────────
一键回归冒烟测试（无窗口 / offscreen 平台）

验证：
  1. main.py 启动链路：MainApp + LeftSidebar 扫描 manifests
  2. 4 个 tab（转换 / 合并 / 翻译 / 设置）可导入并实例化
  3. 7 个参数设置弹窗可导入并实例化
  4. 核心 config 模块可正常导入

用法：
  python tests/smoke_test.py
退出码 0 = 全部通过；非 0 = 有失败。
"""

import os
import sys

# 项目根目录（本文件位于 <root>/tests/ 下）
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
    except Exception as e:  # noqa: BLE001 - 冒烟测试需捕获一切异常
        _FAIL += 1
        print(f"FAIL  {name}: {type(e).__name__}: {e}")


def main() -> int:
    from PySide6.QtWidgets import QApplication

    from ui.theme import APP_STYLESHEET
    app = QApplication([])
    app.setStyleSheet(APP_STYLESHEET)

    print("[1/3] tab 动态注册 + 实例化")
    from ui.main_window import MainApp
    mw = MainApp()
    for info in mw.sidebar.tab_infos:
        def _inst(info=info):
            w = mw._get_or_create_widget(info["class_name"], info.get("module_path"))
            assert type(w).__name__ == info["class_name"]
        _check(info["name"], _inst)

    print("[2/3] 参数设置弹窗实例化")
    from config.stt_config import default_config as stt_cfg
    from config.tts_config import default_config as tts_cfg
    from config.translator_config import default_config as tr_cfg
    from config.pdf_docx_config import default_config as pdf_cfg
    from config.screen_region_config import default_config as sr_cfg
    from config.image_docx_config import ImageDocxConfig

    from ui.options import (
        set_stt, set_tts, set_translator, set_image_docx,
        set_screen_region, set_pdf_docx, set_ui,
    )
    for name, dlg in (
        ("翻译引擎参数", set_translator.SetTranslator(tr_cfg())),
        ("语音识别参数", set_stt.SetStt(stt_cfg())),
        ("语音合成参数", set_tts.SetTts(tts_cfg())),
        ("图片排版参数", set_image_docx.SetImageDocx(ImageDocxConfig())),
        ("截图区域参数", set_screen_region.SetScreenRegion(sr_cfg())),
        ("PDF→DOCX 方式", set_pdf_docx.SetPdfDocx(pdf_cfg())),
        ("全局 UI 风格", set_ui.Setui()),
    ):
        def _open(_dlg=dlg):
            assert _dlg is not None and _dlg.windowTitle() != ""
        _check(name, _open)

    print("[3/3] 关键 config / engine 模块导入")
    for name, mod in (
        ("config.ui_config", "config.ui_config"),
        ("config.presets", "config.presets"),
        ("core.engines.screenshot_engine", "core.engines.screenshot_engine"),
        ("core.engines.audio_capture_engine", "core.engines.audio_capture_engine"),
        ("core.engines.translation_engine", "core.engines.translation_engine"),
    ):
        def _import(_mod=mod):
            __import__(_mod, fromlist=[None])
        _check(name, _import)

    print(f"\n结果: {_PASS} 通过, {_FAIL} 失败")
    return 1 if _FAIL else 0


if __name__ == "__main__":
    sys.exit(main())