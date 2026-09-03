"""
OCTools/ui/tabs/translation/apps/worker_bridge.py
──────────────────────────────────────────────
最终应用 · 工作线程 → 主线程 信号桥

从原项目单拎出来，供 ui/tabs/translation/apps/app_base.py（TranslateAppBase）复用。
"""

from PySide6.QtCore import QObject, Signal


class _WorkerBridge(QObject):
    """工作线程 → 主线程 信号桥（跨线程 emit 自动 QueuedConnection）"""

    text_ready = Signal(str)            # 单文本结果（屏幕OCR / 屏幕字幕）
    result_ready = Signal(str, str)     # 双语结果（原文, 译文）
    status = Signal(str)
    log_line = Signal(str)