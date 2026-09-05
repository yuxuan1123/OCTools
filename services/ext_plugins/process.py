"""
OCTools/services/ext_plugins/process.py
───────────────────────────────────────────────
插件子进程管理：启动、IPC、心跳、退出检测、进程树终止。

- 环境变量：PYTHONPATH=deps/<plugin_id>、PLUGIN_ID、MYAPP_HOME、
  PYTHONIOENCODING/PYTHONUTF8（保证 UTF-8 协议流）。
- 工作目录：plugins/<plugin_id>/（文件系统隔离的第一步）。
- stdout 仅承载 JSON Lines 协议；stderr 独立管道 → log_line 信号。
"""

import os
import subprocess
import threading
import time

from PySide6.QtCore import QObject, Signal

from services.ext_plugins.ipc import JsonLinesIpc


def _create_no_window_flags():
    if os.name == "nt":
        return getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return 0


class PluginProcess(QObject):
    """单个插件子进程的封装。"""

    # 信号参数均为插件 id + 数据，跨线程发射自动排队到主线程
    ipc_event = Signal(str, object)   # ("response", msg) / ("event", msg)
    exited    = Signal(str, int)      # (plugin_id, exit_code)
    log_line  = Signal(str, str)      # (plugin_id, stderr 文本行)

    def __init__(self, plugin_id: str, parent=None):
        super().__init__(parent)
        self.plugin_id = plugin_id
        self.proc = None
        self.ipc = None
        self._alive = False
        self._last_pong = 0.0
        self._last_active = 0.0
        self._exited_lock = threading.Lock()
        self._emitted_exit = False

    # ── 属性 ──────────────────────────────
    def alive(self) -> bool:
        if self.proc is None:
            return False
        return self.proc.poll() is None

    @property
    def last_pong(self) -> float:
        return self._last_pong

    @property
    def last_active(self) -> float:
        return self._last_active

    def mark_active(self):
        """收到插件任何消息时刷新活跃时间。"""
        self._last_active = time.monotonic()

    def mark_pong(self):
        """收到心跳响应时刷新 pong 时间。"""
        self._last_pong = time.monotonic()
        self.mark_active()

    # ── 生命周期 ──────────────────────────
    def start(self, python_exe: str, main_py: str, deps_dir: str,
              cwd: str, home: str) -> bool:
        """启动子进程；成功返回 True。"""
        if self.proc is not None and self.alive():
            return False
        env = os.environ.copy()
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = (deps_dir + os.pathsep + existing) if existing else deps_dir
        env["PLUGIN_ID"] = self.plugin_id
        env["MYAPP_HOME"] = home
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        try:
            self.proc = subprocess.Popen(
                [python_exe, main_py],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                env=env,
                cwd=cwd,
                creationflags=_create_no_window_flags(),
            )
        except (OSError, ValueError) as e:
            print(f"[外部插件] {self.plugin_id} 启动失败：{e}")
            self.proc = None
            return False

        self._alive = True
        self._emitted_exit = False
        now = time.monotonic()
        self._last_pong = now
        self._last_active = now

        self.ipc = JsonLinesIpc(
            self.proc,
            on_response=self._on_response,
            on_event=self._on_event,
            on_pong=self.mark_pong,
            on_eof=self._on_stdout_eof,
        )
        threading.Thread(target=self.ipc.read_loop, daemon=True,
                         name=f"ipc-{self.plugin_id}").start()
        threading.Thread(target=self._stderr_loop, daemon=True,
                         name=f"stderr-{self.plugin_id}").start()
        threading.Thread(target=self._wait_loop, daemon=True,
                         name=f"wait-{self.plugin_id}").start()
        return True

    def _stderr_loop(self):
        """读取 stderr → log_line 信号。"""
        try:
            for raw in self.proc.stderr:
                line = raw.rstrip("\n")
                if line:
                    self.log_line.emit(self.plugin_id, line)
        except (OSError, ValueError):
            pass

    def _wait_loop(self):
        """等待进程结束 → exited 信号（仅发射一次）。"""
        try:
            code = self.proc.wait()
        except (OSError, ValueError):
            code = -1
        with self._exited_lock:
            already = self._emitted_exit
            self._emitted_exit = True
        if not already:
            self.exited.emit(self.plugin_id, code)

    def _on_response(self, req_id: int, msg: dict):
        self.mark_active()
        self.ipc_event.emit("response", msg)

    def _on_event(self, msg: dict):
        self.mark_active()
        self.ipc_event.emit("event", msg)

    def _on_stdout_eof(self):
        self._alive = False

    # ── IPC 发送 ──────────────────────────
    def send_request(self, method, params=None, callback=None,
                     timeout=30.0) -> int:
        if self.ipc is None:
            return -1
        return self.ipc.send_request(method, params, callback, timeout)

    def send_event(self, event, data=None):
        if self.ipc is not None:
            self.ipc.send_event(event, data)

    def ping(self):
        if self.ipc is not None:
            self.ipc.send_ping()

    def shutdown(self):
        """发送关闭指令（进程应自行退出，exit code 0）。"""
        if self.ipc is not None:
            self.ipc.send_shutdown()

    # ── 终止 ──────────────────────────────
    def kill_tree(self, grace_s: float = 0):
        """终止进程及其子进程。

        grace_s > 0 时先 terminate 等待，随后强制 kill。
        """
        proc = self.proc
        if proc is None:
            return
        pid = proc.pid
        children = []
        try:
            import psutil
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
        except Exception:
            children = []
        if grace_s > 0:
            for c in children:
                try:
                    c.terminate()
                except Exception:
                    pass
            try:
                proc.terminate()
            except Exception:
                pass
            deadline = time.monotonic() + grace_s
            while time.monotonic() < deadline and proc.poll() is None:
                time.sleep(0.05)
        for c in children:
            try:
                c.kill()
            except Exception:
                pass
        try:
            proc.kill()
        except Exception:
            pass
        self._alive = False
