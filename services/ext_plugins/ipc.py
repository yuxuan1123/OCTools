"""
OCTools/services/ext_plugins/ipc.py
───────────────────────────────────────────────
JSON Lines IPC 协议（主进程侧）。

传输约定：
  - 每行一条 JSON，末尾带换行符；双方均使用 stdin.readline() / print(..., flush=True)。
  - 插件 stdout 仅承载协议数据；stderr 走独立管道（避免污染协议流）。

消息类型：
  请求   {"id": N, "method": "...", "params": {...}}
  响应   {"id": N, "result": {...}}  |  {"id": N, "error": {"code": -1, "message": "..."}}
  事件   {"event": "...", "data": {...}}
  心跳   {"ping": true}              →  {"pong": true}
  关闭   {"shutdown": true}
"""

import itertools
import json
import threading


class JsonLinesIpc:
    """读写子进程 stdin/stdout 的 JSON Lines 协议封装（线程安全）。"""

    def __init__(self, proc, on_response=None, on_event=None,
                 on_pong=None, on_eof=None):
        """
        Args:
            proc:      已启动的 subprocess.Popen（stdin/stdout 为管道）
            on_response: 回调(id, msg) —— 收到请求响应
            on_event:    回调(msg)   —— 收到插件事件推送
            on_pong:     回调()      —— 收到心跳响应
            on_eof:      回调()      —— stdout 关闭（进程退出）
        """
        self._proc = proc
        self._on_response = on_response
        self._on_event = on_event
        self._on_pong = on_pong
        self._on_eof = on_eof
        self._write_lock = threading.Lock()
        self._pending = {}          # id -> (deadline, callback)
        self._seq = itertools.count(1)
        self._broken = False

    # ── 发送 ──────────────────────────────
    def _write(self, obj) -> bool:
        """写一行 JSON；管道已关闭/失败返回 False 并标记 broken。"""
        if self._broken:
            return False
        try:
            line = json.dumps(obj, ensure_ascii=False)
            with self._write_lock:
                self._proc.stdin.write(line + "\n")
                self._proc.stdin.flush()
            return True
        except (OSError, ValueError, BrokenPipeError):
            self._broken = True
            return False

    def send_request(self, method, params=None, callback=None,
                     timeout=30.0) -> int:
        """发送请求，返回请求 id。响应到达时回调(result 或 {"error": ...})。"""
        req_id = next(self._seq)
        deadline = None
        if timeout:
            import time
            deadline = time.monotonic() + timeout
        self._pending[req_id] = (deadline, callback)
        msg = {"id": req_id, "method": method}
        if params is not None:
            msg["params"] = params
        if not self._write(msg):
            self._pending.pop(req_id, None)
            return -1
        return req_id

    def send_event(self, event, data=None):
        msg = {"event": event}
        if data is not None:
            msg["data"] = data
        self._write(msg)

    def send_ping(self):
        self._write({"ping": True})

    def send_shutdown(self):
        self._write({"shutdown": True})

    # ── 读取循环（读线程目标）──────────────
    def read_loop(self):
        """阻塞读取 stdout 直至 EOF，逐行解析并分发。"""
        try:
            for raw in self._proc.stdout:
                line = raw.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(msg, dict):
                    continue
                self._dispatch(msg)
        except (OSError, ValueError):
            pass
        finally:
            if self._on_eof is not None:
                try:
                    self._on_eof()
                except Exception:
                    pass

    def _dispatch(self, msg: dict):
        if msg.get("pong") is True and self._on_pong is not None:
            try:
                self._on_pong()
            except Exception:
                pass
            return
        if "event" in msg and self._on_event is not None:
            try:
                self._on_event(msg)
            except Exception:
                pass
            return
        req_id = msg.get("id")
        if req_id is None:
            return
        if self._on_response is not None:
            try:
                self._on_response(req_id, msg)
            except Exception:
                pass
        entry = self._pending.pop(req_id, None)
        if entry is None:
            return
        deadline, callback = entry
        if callback is None:
            return
        if deadline is not None:
            import time
            if time.monotonic() > deadline:
                return          # 已过期，丢弃
        try:
            callback(msg)
        except Exception:
            pass
