"""纯函数工具：时间格式化 · 颜色插值。

不含任何业务判断，方便单测复用。
"""

from PySide6.QtGui import QColor


def hm(sec) -> str:
    """秒 → 'xx小时xx分'（不足 1 小时只显示分）。"""
    sec = max(0, int(sec))
    h, mm = divmod(sec // 60, 60)
    return f"{h}小时{mm:02d}分" if h else f"{mm}分"


def ms(sec) -> str:
    """秒 → 'xx分xx秒'（补卡窗口用）。"""
    sec = max(0, int(sec))
    mm, ss = divmod(sec, 60)
    return f"{mm:02d}分{ss:02d}秒"


def clock_hms(dt) -> str:
    """datetime → 'HH:MM:SS'。"""
    return dt.strftime("%H:%M:%S")


def lerp(a: QColor, b: QColor, t: float) -> QColor:
    """两色按 t∈[0,1] 线性插值。"""
    t = max(0.0, min(1.0, t))
    return QColor(
        int(a.red() + (b.red() - a.red()) * t),
        int(a.green() + (b.green() - a.green()) * t),
        int(a.blue() + (b.blue() - a.blue()) * t),
    )
