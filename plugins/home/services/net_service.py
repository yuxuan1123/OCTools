"""静默执行网络加速脚本：状态探测 + 开关切换。

所有 subprocess 一律 CREATE_NO_WINDOW / -WindowStyle Hidden，绝不弹窗。
"""

import subprocess
import threading

from home.constants import NET_PS1, NET_STATIC_IP

# PowerShell 探测命令：静态 IP 是否存在
_PROBE_CMD = (
    f"@(Get-NetIPAddress -AddressFamily IPv4 "
    f"-IPAddress {NET_STATIC_IP} -ErrorAction SilentlyContinue).Count"
)


def probe_state(timeout: int = 6) -> str:
    """阻塞探测当前网络加速状态，返回 'on' / 'off' / 'unknown'。

    仅供后台线程调用。
    """
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", _PROBE_CMD],
            capture_output=True, text=True, timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        count = result.stdout.strip()
        return "on" if count and count != "0" else "off"
    except Exception:
        return "unknown"


def probe_state_async(callback, timeout: int = 6):
    """异步探测：callback(state) 在后台线程中被调用（注意线程安全）。"""
    def worker():
        callback(probe_state(timeout))
    threading.Thread(target=worker, daemon=True).start()


def apply_action(turn_on: bool):
    """静默执行 net.ps1 的开关动作，返回 (ok, error)。"""
    action = "on" if turn_on else "off"
    try:
        subprocess.Popen(
            ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-NonInteractive",
             "-ExecutionPolicy", "Bypass",
             "-File", str(NET_PS1), "-Action", action],
            cwd=str(NET_PS1.parent),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        return True, ""
    except Exception as e:
        return False, str(e)


def script_exists() -> bool:
    return NET_PS1.exists()
