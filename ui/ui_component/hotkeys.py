"""
OCTools/ui/ui_component/hotkeys.py
───────────────────────────────────
全局快捷键绑定（Windows RegisterHotKey + Qt nativeEventFilter）。

功能：
  - bind(spec, callback)：绑定全局快捷键（托盘/窗口隐藏时仍有效）
  - unbind / unbind_all：解绑
  - 绑定失败返回 False，不抛异常

支持组合键：alt / ctrl / shift / win + 字母数字功能键，如 "alt+x"。
非 Windows 平台自动降级（返回 False），由调用方决定提示。
"""

import ctypes
import re
from typing import Callable, Dict, Optional

from PySide6.QtCore import QObject, QAbstractNativeEventFilter

# ── Windows API 常量 ──
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
WM_HOTKEY = 0x0312
VK_FALLBACK = {
    **{chr(c): ord(chr(c)) for c in range(ord("0"), ord("9") + 1)},
    **{chr(c): ord(chr(c)) for c in range(ord("A"), ord("Z") + 1)},
    "F1": 0x70, "F2": 0x71, "F3": 0x72, "F4": 0x73,
    "F5": 0x74, "F6": 0x75, "F7": 0x76, "F8": 0x77,
    "F9": 0x78, "F10": 0x79, "F11": 0x7A, "F12": 0x7B,
    "esc": 0x1B, "tab": 0x09, "space": 0x20, "enter": 0x0D,
    "return": 0x0D, "backspace": 0x08, "delete": 0x2E, "ins": 0x2D,
    "home": 0x24, "end": 0x23, "pgup": 0x21, "pgdn": 0x22,
    "left": 0x25, "right": 0x27, "up": 0x26, "down": 0x28,
    "-": 0xBD, "=": 0xBB, "[": 0xDB, "]": 0xDD, "\\": 0xDC,
    ";": 0xBA, "'": 0xDE, ",": 0xBC, ".": 0xBE, "/": 0xBF,
    "`": 0xC0,
}

# 绑定失败原因（供上层提示）
ERR_OCCUPIED = "occupied"        # 被占用
ERR_INVALID = "invalid"          # 非法格式
ERR_UNAVAILABLE = "unavailable"  # 平台不支持


def _load_user32():
    return ctypes.windll.user32 if hasattr(ctypes, "windll") else None


def parse_hotkey(spec: str) -> Optional[Dict[str, int]]:
    """解析 "alt+x" 为 dict(mods, vk)；非法返回 None"""
    spec = (spec or "").strip().lower().replace(" ", "")
    if not spec:
        return None
    mods = 0
    parts = spec.split("+")
    key = parts[-1]
    for m in parts[:-1]:
        if m in ("alt", "option"):
            mods |= MOD_ALT
        elif m in ("ctrl", "control"):
            mods |= MOD_CONTROL
        elif m in ("shift",):
            mods |= MOD_SHIFT
        elif m in ("win", "meta", "super"):
            mods |= MOD_WIN
        else:
            return None
    if key not in VK_FALLBACK:
        key = key.upper()
        if key not in VK_FALLBACK:
            return None
    return {"mods": mods, "vk": VK_FALLBACK[key]}


class _MSG(ctypes.Structure):
    """Windows MSG 结构（仅解析所需字段）"""
    _fields_ = [
        ("hwnd", ctypes.c_void_p),
        ("message", ctypes.c_uint),
        ("wParam", ctypes.c_size_t),
        ("lParam", ctypes.c_long),
        ("time", ctypes.c_ulong),
        ("pt_x", ctypes.c_long),
        ("pt_y", ctypes.c_long),
    ]


class _NativeHotkeyFilter(QAbstractNativeEventFilter):
    """Qt 原生事件过滤器：捕获 WM_HOTKEY 并分发"""

    def __init__(self, owner: "GlobalHotkeyManager"):
        super().__init__()
        self._owner = owner

    def nativeEventFilter(self, eventType, message):
        try:
            msg = ctypes.cast(int(message), ctypes.POINTER(_MSG)).contents
        except Exception:
            return False
        if msg.message == WM_HOTKEY:
            return self._owner._dispatch(int(msg.wParam))
        return False


class GlobalHotkeyManager(QObject):
    """系统级全局快捷键管理器（Windows）

    用法：
      mgr = GlobalHotkeyManager(app)
      mgr.register("alt+x", callback)
      mgr.unregister("alt+x")
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._user32 = _load_user32()
        self._available = self._user32 is not None
        self._callbacks: Dict[int, Callable] = {}
        self._by_spec: Dict[str, int] = {}
        self._next_id = 1
        self._filter = None
        if self._available:
            from PySide6.QtWidgets import QApplication
            self._filter = _NativeHotkeyFilter(self)
            QApplication.instance().installNativeEventFilter(self._filter)

    @property
    def available(self) -> bool:
        return self._available

    def register(self, spec: str, callback: Callable) -> bool:
        """注册全局快捷键；成功返回 True（占用/非法返回 False）"""
        if not self._available:
            return False
        if not spec or spec in self._by_spec:
            return False
        parsed = parse_hotkey(spec)
        if parsed is None:
            return False
        ok = self._user32.RegisterHotKey(None, self._next_id,
                                         parsed["mods"], parsed["vk"])
        if not ok:
            return False
        self._callbacks[self._next_id] = callback
        self._by_spec[spec.lower()] = self._next_id
        self._next_id += 1
        return True

    def unregister(self, spec: str) -> bool:
        """注销快捷键；成功返回 True"""
        if not self._available:
            return False
        spec = spec.lower()
        hid = self._by_spec.pop(spec, None)
        if hid is None:
            return False
        self._user32.UnregisterHotKey(None, hid)
        self._callbacks.pop(hid, None)
        return True

    def unregister_all(self):
        for spec in list(self._by_spec):
            self.unregister(spec)

    def _dispatch(self, hotkey_id: int) -> bool:
        cb = self._callbacks.get(hotkey_id)
        if cb is None:
            return False
        try:
            cb()
        except Exception:
            pass
        return True

    def __del__(self):
        try:
            self.unregister_all()
        except Exception:
            pass


class HotkeyService(QObject):
    """全局热键绑定服务（Windows）+ 非 Windows 自动降级"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._mgr = GlobalHotkeyManager(parent)
        self._last_error = None

    @property
    def available(self) -> bool:
        return self._mgr.available

    @property
    def last_error(self):
        """最近一次 bind 失败的原因（ERR_* 常量）"""
        return self._last_error

    def bind(self, spec: str, callback) -> bool:
        """绑定全局快捷键；成功返回 True，失败返回 False（见 last_error）"""
        self._last_error = None
        if not self._mgr.available:
            self._last_error = ERR_UNAVAILABLE
            return False
        if parse_hotkey(spec) is None:
            self._last_error = ERR_INVALID
            return False
        if not self._mgr.register(spec, callback):
            self._last_error = ERR_OCCUPIED
            return False
        return True

    def unbind(self, spec: str) -> bool:
        """解绑快捷键；成功返回 True"""
        return self._mgr.unregister(spec)

    def unbind_all(self):
        """解绑全部快捷键"""
        self._mgr.unregister_all()