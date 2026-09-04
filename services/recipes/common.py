"""
OCTools/services/recipes/common.py
──────────────────────────────────────
拼接配方层共享工具（非 UI）：

  capture_excluded(widgets, rect)
    截取指定区域前临时隐藏给定窗口（悬浮框 / 区域框等），
    等待桌面合成器刷新后截图，完成后恢复显示。避免把自己拍进截图。
"""

import time

from core.engines.screenshot_engine import CAPTURE_EXCLUDE_DELAY, grab_region


def capture_excluded(widgets, rect):
    """隐藏给定窗口 → 等待刷新 → 截图 → 恢复显示；返回 PIL Image"""
    vis = [w for w in (widgets or []) if w is not None and w.isVisible()]
    for w in vis:
        w.hide()
    try:
        if vis:
            # 强制刷新事件循环，确保 hide() 生效
            from PySide6.QtWidgets import QApplication
            for _ in range(3):
                QApplication.processEvents()
            # 额外等待一小段时间（针对 Windows DWM）
            import time
            time.sleep(CAPTURE_EXCLUDE_DELAY)  # 建议值 0.05
        return grab_region(rect)
    finally:
        for w in vis:
            w.show()