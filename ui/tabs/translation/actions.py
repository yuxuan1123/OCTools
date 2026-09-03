"""
octool/ui/tabs/translation/actions.py
────────────────────────────────────────────────
页面交互动作：载入文件 / 清空输入 / 复制译文 / 保存译文。

各函数第一个参数为 page（TabTranslation），供回调传入 self。
"""

import os

from PySide6.QtWidgets import QFileDialog, QMessageBox, QApplication

from core.utils.file_handler import read_text, write_text


def load_file(page):
    """载入文本文件到原文输入框"""
    path, _ = QFileDialog.getOpenFileName(
        page, "选择要翻译的文本文件", "",
        "文本文件 (*.txt *.md *.markdown);;所有文件 (*.*)")
    if not path:
        return
    try:
        text = read_text(path)
        page.input_edit.setPlainText(text)
        page.log(f"📂 已载入: {os.path.basename(path)}（{len(text)} 字符）")
    except Exception as e:
        QMessageBox.critical(page, "错误", f"读取文件失败:\n{e}")


def clear_input(page):
    """清空原文输入框"""
    page.input_edit.clear()


def copy_result(page):
    """复制译文到剪贴板"""
    text = page.output_edit.toPlainText().strip()
    if not text:
        QMessageBox.warning(page, "提示", "暂无译文可复制")
        return
    QApplication.clipboard().setText(text)
    page.log(f"📋 译文已复制到剪贴板（{len(text)} 字符）")


def save_result(page):
    """把译文保存到文件"""
    text = page.output_edit.toPlainText().strip()
    if not text:
        QMessageBox.warning(page, "提示", "暂无译文可保存")
        return
    path, _ = QFileDialog.getSaveFileName(
        page, "保存译文", "译文.txt", "文本文件 (*.txt);;所有文件 (*.*)")
    if not path:
        return
    if not os.path.splitext(path)[1]:
        path += ".txt"
    try:
        write_text(path, text)
        page.log(f"💾 译文已保存到: {path}")
    except Exception as e:
        QMessageBox.critical(page, "错误", f"保存失败:\n{e}")