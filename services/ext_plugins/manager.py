"""
OCTools/services/ext_plugins/manager.py
───────────────────────────────────────────────
外部插件核心管理器：状态机 + 生命周期 + 心跳监控 + 闲置回收。

状态常量：MISSING / NEEDS_INSTALL / INSTALLING / INSTALL_FAILED /
          READY / STARTING / RUNNING / STOPPING / CRASHED / DISABLED

职责：
  - 扫描插件源、读取 config.json、计算各插件状态；
  - 串行安装缺失依赖（InstallWorker 位于独立 QThread）；
  - 按加载模式启动/停止子进程（always 常驻 / lazy 懒加载 / auto_recycle 闲置回收）；
  - 5s 心跳检测，12s 无响应判定卡死 → 强制终止并重启（≤3 次）；
  - 崩溃自动重启（间隔 2s，存活 >60s 重置计数）；
  - 退出时向全部子进程发送 shutdown 并兜底强杀。

单例：PluginManager.instance()（主线程创建，供 UI 共用）。
"""

import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime

from PySide6.QtCore import QObject, QThread, QTimer, Signal

from services.ext_plugins import config_store, detection, log_store, paths
from services.ext_plugins.installer import InstallWorker
from services.ext_plugins.process import PluginProcess

# 统一子进程运行时（替代各插件自带的 main.py）
HOST_PY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "host.py")

# 状态常量
MISSING        = "MISSING"
NEEDS_INSTALL  = "NEEDS_INSTALL"
INSTALLING     = "INSTALLING"
INSTALL_FAILED = "INSTALL_FAILED"
READY          = "READY"
STARTING       = "STARTING"
RUNNING        = "RUNNING"
STOPPING       = "STOPPING"
CRASHED        = "CRASHED"
DISABLED       = "DISABLED"

HEARTBEAT_INTERVAL_S = 5.0
HEARTBEAT_TIMEOUT_S  = 12.0     # 连续两次心跳无响应
RESTART_MAX          = 3
RESTART_DELAY_S      = 2.0
RESTART_RESET_S      = 60.0     # 存活超过该时长后重置重试计数
SHUTDOWN_GRACE_S     = 3.0
EXIT_SHUTDOWN_S      = 5.0


@dataclass
class PluginInfo:
    """单个插件的状态快照（供 UI 渲染）。"""
    plugin_id: str
    dir: str = ""
    main_py: str = ""
    requirements: str = ""
    deps_dir: str = ""
    has_deps: bool = False
    has_requirements: bool = False
    ui_mode: str = detection.UI_DIRECT   # direct / desc / window
    module_path: str = ""
    class_name: str = ""
    enabled: bool = True
    load_mode: str = "lazy"
    state: str = ""
    last_log: str = ""


class PluginManager(QObject):
    """外部插件管理器（主线程 QObject，单例）。"""

    plugins_scanned      = Signal(dict)            # {plugin_id: PluginInfo}
    plugin_state_changed = Signal(str, str)        # (plugin_id, state)
    install_progress     = Signal(str, int, str)   # (plugin_id, percent, line)
    install_finished     = Signal(str, bool, str)  # (plugin_id, ok, message)
    call_result          = Signal(str, bool, str)  # (plugin_id, ok, message)
    call_response        = Signal(str, bool, object)  # (plugin_id, ok, result) 结构化数据
    log_updated          = Signal(str, str)        # (plugin_id, kind: run/install/crash)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._started = False
        self._python_exe = ""
        self._uv = None
        self._cfg = config_store.load_config()

        self._sources: dict[str, detection.PluginSource] = {}
        self._infos: dict[str, PluginInfo] = {}
        self._processes: dict[str, PluginProcess] = {}
        self._stopping: dict[str, str] = {}        # plugin_id -> 停止后状态
        self._retries: dict[str, int] = {}
        self._alive_since: dict[str, float] = {}
        self._pending_calls: dict[str, tuple] = {} # plugin_id -> (method, params)
        self._requests: dict[int, str] = {}        # req_id -> plugin_id
        self._call_meta: dict[int, tuple] = {}     # req_id -> (plugin_id, method)

        self._install_queue: list[str] = []
        self._install_busy = False
        self._installing: str | None = None
        self._install_thread: QThread | None = None
        self._install_worker: InstallWorker | None = None

        self._hb_timer: QTimer | None = None
        self._idle_timer: QTimer | None = None

    # ── 单例 ──────────────────────────────
    @classmethod
    def instance(cls) -> "PluginManager":
        if not hasattr(cls, "_singleton") or cls._singleton is None:
            cls._singleton = cls()
        return cls._singleton

    # ── 启动 / 关闭 ───────────────────────
    def start(self):
        """初始化并启动（幂等）：扫描 → 安装缺失依赖 → 按模式启动进程。"""
        if self._started:
            return
        self._started = True
        paths.ensure_dirs()
        self._python_exe = detection.find_python()
        self._uv = detection.find_uv()
        if not self._python_exe:
            log_store.app_logger().warning("未找到嵌入式 Python 运行时")
        if self._uv is None:
            log_store.app_logger().warning(
                "未找到 uv，依赖安装将回退 pip（仅开发/无随附环境）")

        self.scan()

        # 安装工作线程（串行队列）
        self._install_thread = QThread(self)
        self._install_worker = InstallWorker(self._python_exe, self._uv)
        self._install_worker.moveToThread(self._install_thread)
        self._install_worker.install_requested.connect(
            self._install_worker._do_install)
        self._install_worker.progress.connect(self.install_progress)
        self._install_worker.finished.connect(self._on_install_finished)
        self._install_thread.start()

        # 心跳 / 闲置回收定时器
        self._hb_timer = QTimer(self)
        self._hb_timer.setInterval(int(HEARTBEAT_INTERVAL_S * 1000))
        self._hb_timer.timeout.connect(self._heartbeat_tick)
        self._hb_timer.start()

        self._idle_timer = QTimer(self)
        self._idle_timer.setInterval(60_000)
        self._idle_timer.timeout.connect(self._idle_tick)
        self._idle_timer.start()

        # 初始调度
        for pid, info in list(self._infos.items()):
            if not info.enabled:
                continue
            if info.state == NEEDS_INSTALL:
                self._install_queue.append(pid)
            elif info.state == READY and info.load_mode in ("always", "auto_recycle"):
                self._start_process(pid)
        self._pump_install_queue()

    def shutdown(self):
        """关闭所有子进程、停止定时器与安装线程（阻塞，≤5s）。"""
        if not self._started:
            return
        self._started = False
        if self._hb_timer is not None:
            self._hb_timer.stop()
        if self._idle_timer is not None:
            self._idle_timer.stop()
        if self._install_thread is not None:
            self._install_thread.quit()
            self._install_thread.wait(2000)

        for proc in list(self._processes.values()):
            if proc.alive():
                proc.shutdown()
        deadline = time.monotonic() + EXIT_SHUTDOWN_S
        while time.monotonic() < deadline:
            if not any(p.alive() for p in self._processes.values()):
                break
            time.sleep(0.1)
        for pid, proc in list(self._processes.items()):
            if proc.alive():
                log_store.append_line(paths.crash_log(pid),
                                      "主程序退出：强制终止残留进程")
                proc.kill_tree()
        self._processes.clear()
        self._stopping.clear()

    # ── 扫描 ──────────────────────────────
    def scan(self) -> dict[str, PluginInfo]:
        """扫描插件源并合并配置，返回状态快照。"""
        self._sources = detection.scan_plugins()
        cfg = self._cfg
        ids = set(self._sources) | set(cfg.get("plugins", {}))
        infos: dict[str, PluginInfo] = {}
        for pid in sorted(ids):
            src = self._sources.get(pid)
            if src is None:
                infos[pid] = PluginInfo(
                    plugin_id=pid,
                    enabled=bool(config_store.plugin_entry(cfg, pid).get("enabled", True)),
                    load_mode=config_store.plugin_entry(cfg, pid).get("load_mode", "lazy"),
                    state=MISSING,
                )
                continue
            entry = config_store.plugin_entry(cfg, pid)
            enabled = bool(entry.get("enabled", True))
            mode = entry.get("load_mode", "lazy")
            ui_mode = src.ui_mode
            # direct 模式无需依赖安装、不启动子进程
            if ui_mode == detection.UI_DIRECT:
                has_deps = True
            else:
                has_deps = detection.has_deps(pid) if src.has_requirements else True
            if not enabled:
                state = DISABLED
            elif ui_mode == detection.UI_DIRECT:
                state = READY
            elif entry.get("install_failed"):
                state = INSTALL_FAILED
            elif not has_deps:
                state = NEEDS_INSTALL
            else:
                state = READY
            infos[pid] = PluginInfo(
                plugin_id=pid,
                dir=src.dir,
                main_py=src.main_py,
                requirements=src.requirements,
                deps_dir=paths.plugin_deps_dir(pid),
                has_deps=has_deps,
                has_requirements=src.has_requirements,
                ui_mode=ui_mode,
                module_path=src.module_path,
                class_name=src.class_name,
                enabled=enabled,
                load_mode=mode,
                state=state,
            )
        # 保留运行中的动态状态
        for pid, info in infos.items():
            old = self._infos.get(pid)
            if old and old.state in (INSTALLING, STARTING, RUNNING,
                                     STOPPING, CRASHED, INSTALL_FAILED):
                info.state = old.state
                info.last_log = old.last_log
            proc = self._processes.get(pid)
            if proc is not None and proc.alive():
                info.state = RUNNING
        self._infos = infos
        self.plugins_scanned.emit(dict(infos))
        return dict(infos)

    def info(self, plugin_id: str) -> PluginInfo | None:
        return self._infos.get(plugin_id)

    # ── 状态 ──────────────────────────────
    def _set_state(self, plugin_id: str, state: str):
        info = self._infos.get(plugin_id)
        if info is None or info.state == state:
            return
        info.state = state
        self.plugin_state_changed.emit(plugin_id, state)

    # ── 依赖安装 ──────────────────────────
    def install(self, plugin_id: str):
        """把插件依赖安装请求加入队列（串行执行）。"""
        info = self._infos.get(plugin_id)
        if info is None or self._installing == plugin_id:
            return
        if plugin_id in self._install_queue:
            return
        entry = config_store.plugin_entry(self._cfg, plugin_id)
        entry.pop("install_failed", None)
        self._cfg["plugins"][plugin_id] = entry
        config_store.save_config(self._cfg)
        self._install_queue.append(plugin_id)
        self._pump_install_queue()

    def _pump_install_queue(self):
        if self._install_busy or not self._install_queue:
            return
        if self._install_worker is None:
            return
        pid = self._install_queue.pop(0)
        self._install_busy = True
        self._installing = pid
        self._set_state(pid, INSTALLING)
        self._install_worker.install_requested.emit(pid)

    def _on_install_finished(self, plugin_id: str, ok: bool, message: str):
        self._install_busy = False
        self._installing = None
        self.install_finished.emit(plugin_id, ok, message)
        info = self._infos.get(plugin_id)
        if info is None:
            self._pump_install_queue()
            return
        if ok:
            info.has_deps = True
            self._set_state(plugin_id, READY)
            if info.enabled and (
                    info.load_mode in ("always", "auto_recycle")
                    or plugin_id in self._pending_calls):
                self._start_process(plugin_id)
        else:
            self._set_state(plugin_id, INSTALL_FAILED)
            entry = config_store.plugin_entry(self._cfg, plugin_id)
            entry["install_failed"] = True
            self._cfg["plugins"][plugin_id] = entry
            config_store.save_config(self._cfg)
        self._pump_install_queue()

    # ── 启用 / 禁用 ───────────────────────
    def enable(self, plugin_id: str):
        """启用插件；依赖缺失先安装（装完自动按模式启动）。"""
        entry = config_store.plugin_entry(self._cfg, plugin_id)
        entry["enabled"] = True
        self._cfg["plugins"][plugin_id] = entry
        config_store.save_config(self._cfg)
        info = self._infos.get(plugin_id)
        if info is None:
            return
        info.enabled = True
        if info.state == MISSING:
            self.call_result.emit(plugin_id, False, "插件目录无效（缺 main.py 或 requirements.txt）")
            return
        if not info.has_deps or info.state == INSTALL_FAILED:
            self.install(plugin_id)
        elif info.load_mode in ("always", "auto_recycle"):
            self._start_process(plugin_id)
        else:
            self._set_state(plugin_id, READY)

    def disable(self, plugin_id: str):
        """禁用插件；停止子进程（先 shutdown，3s 后兜底强杀）。"""
        entry = config_store.plugin_entry(self._cfg, plugin_id)
        entry["enabled"] = False
        self._cfg["plugins"][plugin_id] = entry
        config_store.save_config(self._cfg)
        info = self._infos.get(plugin_id)
        if info is not None:
            info.enabled = False
        proc = self._processes.get(plugin_id)
        if proc is not None and proc.alive():
            self._stop_process(plugin_id, DISABLED)
        else:
            self._set_state(plugin_id, DISABLED)

    # ── 加载模式 ──────────────────────────
    def set_load_mode(self, plugin_id: str, mode: str):
        """切换加载模式（立即生效）。"""
        if mode not in config_store.LOAD_MODES:
            return
        config_store.set_load_mode(self._cfg, plugin_id, mode)
        info = self._infos.get(plugin_id)
        if info is None:
            return
        old = info.load_mode
        info.load_mode = mode
        if old in ("always", "auto_recycle") and mode == "lazy":
            proc = self._processes.get(plugin_id)
            if proc is not None and proc.alive():
                self._stop_process(plugin_id, READY)
            else:
                self._set_state(plugin_id, READY)
        elif old == "lazy" and mode in ("always", "auto_recycle"):
            if info.enabled and info.has_deps:
                self._start_process(plugin_id)
        # always <-> auto_recycle：保留进程，回收逻辑按模式动态判断

    # ── 子进程 ────────────────────────────
    def _start_process(self, plugin_id: str) -> bool:
        if not self._started:
            return False
        info = self._infos.get(plugin_id)
        if info is None or not info.enabled or not info.has_deps:
            return False
        existing = self._processes.get(plugin_id)
        if existing is not None and existing.alive():
            return True
        if not self._python_exe:
            log_store.append_line(
                paths.crash_log(plugin_id),
                "无法启动：未找到嵌入式 Python 运行时")
            self._set_state(plugin_id, CRASHED)
            return False
        self._set_state(plugin_id, STARTING)
        proc = PluginProcess(plugin_id)
        proc.ipc_event.connect(
            lambda kind, msg, p=plugin_id: self._on_ipc_event(p, kind, msg))
        proc.exited.connect(self._on_process_exited)
        proc.log_line.connect(self._on_log_line)
        ok = proc.start(self._python_exe, HOST_PY, info.deps_dir,
                        info.dir, paths.app_root())
        if not ok:
            self._set_state(plugin_id, CRASHED)
            return False
        self._processes[plugin_id] = proc
        self._alive_since[plugin_id] = time.monotonic()
        self._set_state(plugin_id, RUNNING)
        pending = self._pending_calls.pop(plugin_id, None)
        if pending:
            self._send_call(plugin_id, pending[0], pending[1])
        return True

    def _stop_process(self, plugin_id: str, to_state: str):
        """发送 shutdown，3s 后仍存活则强杀；退出后状态置为 to_state。"""
        self._set_state(plugin_id, STOPPING)
        proc = self._processes.get(plugin_id)
        if proc is None or not proc.alive():
            self._stopping.pop(plugin_id, None)
            self._set_state(plugin_id, to_state)
            return
        self._stopping[plugin_id] = to_state
        proc.shutdown()
        QTimer.singleShot(int(SHUTDOWN_GRACE_S * 1000),
                          lambda p=plugin_id: self._force_kill(p))

    def _force_kill(self, plugin_id: str):
        proc = self._processes.get(plugin_id)
        if proc is not None and proc.alive():
            proc.kill_tree()

    def _on_process_exited(self, plugin_id: str, code: int, proc=None):
        # 仅处理当前登记的进程退出；旧进程（已被替换）的退出事件忽略
        if proc is not None and self._processes.get(plugin_id) is not proc:
            return
        tracked = self._processes.get(plugin_id)
        alive_dur = time.monotonic() - self._alive_since.get(plugin_id, 0.0)
        if tracked is not None:
            self._processes.pop(plugin_id, None)
        self._alive_since.pop(plugin_id, None)

        if plugin_id in self._stopping:
            to_state = self._stopping.pop(plugin_id)
            self._set_state(plugin_id, to_state)
            return

        # 崩溃路径
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_store.append_line(paths.crash_log(plugin_id),
                              f"[{ts}] 进程意外退出 exit_code={code}")
        self.log_updated.emit(plugin_id, "crash")
        info = self._infos.get(plugin_id)
        if info is None or not info.enabled:
            self._set_state(plugin_id, DISABLED if (info and not info.enabled) else READY)
            return
        mode = info.load_mode
        if mode in ("always", "auto_recycle"):
            if alive_dur > RESTART_RESET_S:
                self._retries[plugin_id] = 0
            retries = self._retries.get(plugin_id, 0)
            if retries < RESTART_MAX:
                self._retries[plugin_id] = retries + 1
                self._set_state(plugin_id, STARTING)
                QTimer.singleShot(int(RESTART_DELAY_S * 1000),
                                  lambda p=plugin_id: self._start_process(p))
            else:
                self._set_state(plugin_id, CRASHED)
                log_store.append_line(
                    paths.crash_log(plugin_id),
                    f"[{ts}] 达到最大重启次数（{RESTART_MAX}），停止自动重启")
        else:
            # lazy 模式：进程退出后回到就绪，下次调用再启动
            self._set_state(plugin_id, READY)

    # ── 调用 ──────────────────────────────
    def _guard_callable(self, plugin_id: str):
        """校验插件可调用；不可用则经 call_response 发失败消息并返回 None。"""
        info = self._infos.get(plugin_id)
        if info is None or info.state == MISSING:
            self.call_response.emit(plugin_id, False, "插件无效或不存在")
            return None
        if not info.enabled:
            self.call_response.emit(plugin_id, False, "插件已禁用，请先启用")
            return None
        if info.state == INSTALL_FAILED:
            self.call_response.emit(plugin_id, False, "插件依赖安装失败，无法调用")
            return None
        if not info.has_deps:
            self.call_response.emit(plugin_id, False, "插件依赖未安装，请先安装")
            return None
        if info.ui_mode == detection.UI_DIRECT:
            self.call_response.emit(plugin_id, False, "直载插件由主进程加载，无需子进程调用")
            return None
        return info

    def call(self, plugin_id: str, method: str, params=None):
        """调用插件方法；进程未运行时按需启动（lazy/auto_recycle）。"""
        if self._guard_callable(plugin_id) is None:
            return
        self._send_call(plugin_id, method, params)

    def invoke_action(self, plugin_id: str, action: str, params=None):
        """desc 模式：触发插件动作，响应经 call_response 回渲染器刷新。"""
        if self._guard_callable(plugin_id) is None:
            return
        self._send_call(plugin_id, "invoke_action",
                        {"action": action, "params": params or {}})

    def activate(self, plugin_id: str):
        """window 模式：点击入口时确保子进程启动（独立窗口由子进程自建）。"""
        info = self._guard_callable(plugin_id)
        if info is None or info.ui_mode != detection.UI_WINDOW:
            return
        self._start_process(plugin_id)

    def test_crash(self, plugin_id: str):
        """演示崩溃恢复：调用插件 crash 方法使其退出。"""
        self.call(plugin_id, "crash")

    def _send_call(self, plugin_id: str, method: str, params=None):
        proc = self._processes.get(plugin_id)
        if proc is None or not proc.alive():
            self._pending_calls[plugin_id] = (method, params)
            self._start_process(plugin_id)
            return
        req_id = proc.send_request(method, params)
        if req_id == -1:
            self.call_result.emit(plugin_id, False, "请求发送失败（进程已退出）")
            return
        self._requests[req_id] = plugin_id
        self._call_meta[req_id] = (plugin_id, method)

    # ── IPC 事件 ──────────────────────────
    def _on_ipc_event(self, plugin_id: str, kind: str, msg: dict):
        if kind == "response":
            self._handle_response(plugin_id, msg)
        elif kind == "event":
            ev = msg.get("event")
            data = msg.get("data")
            if ev == "log":
                text = data.get("text", "") if isinstance(data, dict) else str(data)
                if text:
                    log_store.append_line(paths.plugin_log(plugin_id), str(text))
                    self.log_updated.emit(plugin_id, "run")
            else:
                log_store.append_line(
                    paths.plugin_log(plugin_id),
                    f"[event {ev}] {json.dumps(data, ensure_ascii=False) if data is not None else ''}")
                self.log_updated.emit(plugin_id, "run")

    def _handle_response(self, plugin_id: str, msg: dict):
        req_id = msg.get("id")
        meta = self._call_meta.pop(req_id, None)
        self._requests.pop(req_id, None)
        if meta is None:
            return
        pid, method = meta
        if "error" in msg:
            err = msg.get("error") or {}
            message = err.get("message", "未知错误")
            message = f"[{method}] {message}"
            self.call_result.emit(pid, False, message)
            self.call_response.emit(pid, False, message)
        else:
            result = msg.get("result")
            try:
                text = json.dumps(result, ensure_ascii=False)
            except (TypeError, ValueError):
                text = str(result)
            message = f"[{method}] {text}"
            self.call_result.emit(pid, True, message)
            # 结构化结果（控件树 / update 增量）供 desc 渲染器使用
            self.call_response.emit(pid, True, result)
        log_store.append_line(paths.plugin_log(pid), message)
        self.log_updated.emit(pid, "run")

    def _on_log_line(self, plugin_id: str, line: str):
        log_store.append_line(paths.plugin_log(plugin_id), line)
        self.log_updated.emit(plugin_id, "run")

    # ── 定时任务 ──────────────────────────
    def _heartbeat_tick(self):
        """每 5s 向运行中的进程发送 ping；12s 无响应判定卡死并强制重启。"""
        if not self._started:
            return
        now = time.monotonic()
        for pid, proc in list(self._processes.items()):
            if not proc.alive():
                continue
            proc.ping()
            if now - proc.last_pong > HEARTBEAT_TIMEOUT_S:
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_store.append_line(paths.crash_log(pid),
                                      f"[{ts}] 心跳超时（> {HEARTBEAT_TIMEOUT_S}s），强制终止")
                self.log_updated.emit(pid, "crash")
                proc.kill_tree()      # wait 线程随后触发 exited → 崩溃重启流程

    def _idle_tick(self):
        """每 1 分钟检查 auto_recycle 插件，闲置超阈值则回收。"""
        if not self._started:
            return
        timeout_s = float(self._cfg.get("settings", {}).get("idle_timeout_min", 10)) * 60
        now = time.monotonic()
        for pid, info in list(self._infos.items()):
            if info.state != RUNNING or info.load_mode != "auto_recycle":
                continue
            proc = self._processes.get(pid)
            if proc is None or not proc.alive():
                continue
            if now - proc.last_active > timeout_s:
                log_store.append_line(paths.plugin_log(pid),
                                      "闲置超时，自动回收进程")
                self._stopping[pid] = READY
                proc.shutdown()
                QTimer.singleShot(int(SHUTDOWN_GRACE_S * 1000),
                                  lambda p=pid: self._force_kill(p))
