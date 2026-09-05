"""
OCTools/services/ext_plugins/installer.py
───────────────────────────────────────────────
插件依赖安装器。

优先使用 uv：
    <uv> pip install --python <python> --target deps/<id> -r plugins/<id>/requirements.txt
无 uv 时回退：
    <python> -m pip install --target deps/<id> -r plugins/<id>/requirements.txt

安装输出逐行转发为 progress 信号（percent=-1 表示不确定进度），
并追加写入 logs/install_<plugin_id>.log。requirements 为空时直接跳过安装。
"""

import os
import subprocess
import sys

from PySide6.QtCore import QObject, Signal

from services.ext_plugins import log_store, paths

# Python 标准库模块名（安装时跳过：tkinter 等随解释器自带，pip 装不了）
_STDLIB = set(getattr(sys, "stdlib_module_names", ()))


def _filter_requirements(req: str) -> str | None:
    """过滤出非标准库依赖；全部为标准库返回 None（无需安装）。"""
    try:
        with open(req, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError:
        return None
    keep: list[str] = []
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        name = line.split("==")[0].split(">=")[0].split("<=")[0]
        name = name.split(">")[0].split("<")[0].split("~=")[0].split("!=")[0]
        name = name.strip().split("[", 1)[0].strip().lower().replace("_", "-")
        if not name:
            continue
        if name in _STDLIB:
            continue
        keep.append(raw)
    return "\n".join(keep) + "\n" if keep else None


class InstallWorker(QObject):
    """安装在独立 QThread 中执行（moveToThread 后由队列串行驱动）。"""

    install_requested = Signal(str)              # (plugin_id)
    progress          = Signal(str, int, str)    # (plugin_id, percent(-1=不确定), line)
    finished          = Signal(str, bool, str)   # (plugin_id, ok, message)

    def __init__(self, python_exe: str, uv: str | None, parent=None):
        super().__init__(parent)
        self._python_exe = python_exe
        self._uv = uv
        self._proc = None

    def abort(self):
        """终止当前正在运行的安装进程（供主程序退出时调用）。"""
        proc = self._proc
        if proc is not None:
            try:
                proc.kill()
            except Exception:
                pass

    # 槽：在工作线程中执行（moveToThread 后经队列连接调用）
    def _do_install(self, plugin_id: str):
        req = os.path.join(paths.plugins_dir(), plugin_id, "requirements.txt")
        if not os.path.isfile(req) or os.path.getsize(req) == 0:
            log_store.append_line(paths.install_log(plugin_id),
                                  "[跳过] 无依赖（requirements.txt 为空）")
            self.finished.emit(plugin_id, True, "无依赖，跳过安装")
            return

        # 过滤标准库依赖（tkinter 等随解释器自带，pip 无法安装）
        filtered = _filter_requirements(req)
        if filtered is None:
            log_store.append_line(
                paths.install_log(plugin_id),
                "[跳过] 依赖均为 Python 标准库，无需安装")
            self.finished.emit(plugin_id, True, "依赖均为标准库，跳过安装")
            return

        deps = paths.plugin_deps_dir(plugin_id)
        os.makedirs(deps, exist_ok=True)
        req_file = req + ".effective"
        try:
            with open(req_file, "w", encoding="utf-8") as f:
                f.write(filtered)
        except OSError as e:
            msg = f"写入有效依赖清单失败：{e}"
            log_store.append_line(paths.install_log(plugin_id), msg)
            self.finished.emit(plugin_id, False, msg)
            return
        if self._uv:
            cmd = [self._uv, "pip", "install",
                   "--python", self._python_exe,
                   "--target", deps,
                   "-r", req_file]
            tool = os.path.basename(self._uv)
        else:
            cmd = [self._python_exe, "-m", "pip", "install",
                   "--disable-pip-version-check",
                   "--target", deps,
                   "-r", req_file]
            tool = "pip"

        log_store.append_line(paths.install_log(plugin_id),
                              f"$ {' '.join(cmd)}")
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
        except OSError as e:
            msg = f"安装进程启动失败：{e}"
            log_store.append_line(paths.install_log(plugin_id), msg)
            self.finished.emit(plugin_id, False, msg)
            return

        for raw in proc.stdout:
            line = raw.rstrip("\n")
            if line:
                log_store.append_line(paths.install_log(plugin_id), line)
                self.progress.emit(plugin_id, -1, line)
        code = proc.wait()

        if code == 0:
            log_store.append_line(paths.install_log(plugin_id),
                                  f"[{tool}] 依赖安装完成")
            self.finished.emit(plugin_id, True, "依赖安装完成")
        else:
            msg = f"依赖安装失败（exit={code}），详情见 logs/install_{plugin_id}.log"
            log_store.append_line(paths.install_log(plugin_id), msg)
            self.finished.emit(plugin_id, False, msg)
