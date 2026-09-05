# -*- coding: utf-8 -*-
"""
OCTools 插件 demo_tk：window 模式示例。
───────────────────────────────────────────────
window：插件不使用 PySide6（此处为 tkinter），在子进程内自建独立窗口，
主进程仅通过 IPC 管理生命周期。manifest 显式声明 ui_mode=window，
无 pip 依赖（tkinter 为 Python 标准库）。
"""


class TabTk:
    """window 模式：主进程仅管理子进程生命周期，窗口完全由本插件绘制。"""

    def show(self):
        import tkinter as tk
        root = tk.Tk()
        root.title("OCTools 插件 · window 模式（tkinter）")
        root.geometry("380x200")
        tk.Label(
            root,
            text="window 模式示例：非 PySide6 UI（tkinter）\n子进程自建独立窗口",
            font=("Microsoft YaHei", 11),
        ).pack(pady=34)
        tk.Button(root, text="关闭", width=14, command=root.destroy).pack()
        root.mainloop()
