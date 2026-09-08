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

# PowerShell 探测命令：物理以太网/wifi 网卡的当前 IPv4（含别名，用 | 分隔 alias|ip）
# 排除 vEthernet (WSL)、Loopback 等虚拟网卡，优先取真实物理网卡
# 通过 stdin 传入，避免嵌套 shell 调用时 $_ 被吞掉
_CURRENT_IP_CMD = (
    '$cs = Get-NetIPConfiguration -ErrorAction SilentlyContinue;'
    '$hit = $cs | Where-Object { $_.InterfaceAlias -notlike "vEthernet*"'
    ' -and $_.InterfaceAlias -notlike "Loopback*" -and $_.IPv4Address }'
    ' | Select-Object -First 1;'
    'if ($hit) { $hit.InterfaceAlias + "|" + $hit.IPv4Address.IPAddress }'
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


def probe_current_ip(timeout: int = 6) -> str:
    """阻塞探测当前物理网卡的 IPv4 地址，失败返回 '—'。"""
    try:
        # 通过 stdin 传命令，避免 $_ 在嵌套 shell 中被吞
        # encoding=gbk：中文 Windows PowerShell 默认输出 GBK
        result = subprocess.run(
            ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", "-"],
            input=_CURRENT_IP_CMD, capture_output=True, timeout=timeout,
            encoding="gbk", errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        raw = result.stdout.strip()
        if not raw:
            return "—"
        # 形如 "以太网|172.17.174.5"，取 IP 部分
        parts = raw.split("|")
        ip = parts[-1].strip() if parts else ""
        return ip or "—"
    except Exception:
        return "—"


def probe_state_async(callback, timeout: int = 6):
    """异步探测：callback(state) 在后台线程中被调用（注意线程安全）。

    state 为字典：{"state": "on"/"off"/"unknown", "ip": "x.x.x.x"}
    """
    def worker():
        callback({
            "state": probe_state(timeout),
            "ip": probe_current_ip(timeout),
        })
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
