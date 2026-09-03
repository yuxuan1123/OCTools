"""
octool/ui/tabs/translation/runner.py
───────────────────────────────────────────────
翻译执行：后台线程调用 TRANSLATOR.translate，完成后通过 page 的信号发回主线程。

  - run_translation(page)            开始翻译（读取输入 → 清空日志 → 置 busy → 起线程）
  - on_translation_finished(page,...) 完成回调（成功写入译文 + toast；失败弹框）
  - on_translation_error(page, err)   异常回调
  - reset_busy(page)                 恢复按钮可点击状态
"""

import threading

from PySide6.QtWidgets import QMessageBox

from core.engines import translation_engine as TRANSLATOR
from ui.toast import show_toast


def run_translation(page):
    """读取输入文本/方向，清空日志与输出，置 busy 并起后台线程翻译。"""
    text = page.input_edit.toPlainText().strip()
    if not text:
        QMessageBox.warning(page, "提示", "请先输入要翻译的文本（或载入文件）")
        return
    idx = page.direction_combo.currentIndex()
    direction = (TRANSLATOR.DIRECTION_ORDER[idx]
                 if 0 <= idx < len(TRANSLATOR.DIRECTION_ORDER) else "auto")

    page.clear_log()
    page.output_edit.clear()
    page.log(f"🌐 开始翻译（{TRANSLATOR.DIRECTION_LABELS.get(direction, direction)}，{len(text)} 字符）")

    page._busy = True
    page.translate_btn.setEnabled(False)
    page.translate_btn.setText("翻译中…")

    def worker():
        try:
            out = TRANSLATOR.translate(text, direction, log=page.log,
                                       config=page.translator_config)
            if out.strip():
                page.translation_finished.emit(page, True, out)
            else:
                page.translation_finished.emit(page, False, "翻译结果为空")
        except Exception as e:
            page.translation_error.emit(page, str(e))

    threading.Thread(target=worker, daemon=True).start()


def on_translation_finished(page, ok, result):
    """主线程完成回调：成功写译文 + 右下角轻提示；失败弹框。"""
    reset_busy(page)
    if ok:
        page.output_edit.setPlainText(result)
        page.log(f"✅ 翻译完成（{len(result)} 字符）")
        # 右下角轻提示，1.5 秒后自动关闭（不再弹模态框）
        show_toast(page, f"翻译完成（{len(result)} 字符）", duration_ms=1500)
    else:
        page.log("❌ 翻译失败")
        QMessageBox.critical(page, "失败", result)


def on_translation_error(page, err):
    """主线程异常回调：复位 busy 并弹错。"""
    reset_busy(page)
    page.log(f"❌ 异常: {err}")
    QMessageBox.critical(page, "错误", err)


def reset_busy(page):
    """恢复「开始翻译」按钮为可点击、文案复原。"""
    page._busy = False
    if page.translate_btn is not None:
        page.translate_btn.setEnabled(True)
        page.translate_btn.setText("开始翻译")