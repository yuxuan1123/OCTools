"""一键工作模式：静默启动 home.bat（后台执行，不弹控制台）。"""

import subprocess

from home.constants import BAT_FILE

_STARTUPINFO = None  # Windows 下由 CREATE_NO_WINDOW 处理


def start_workmode():
    """静默启动 home.bat，返回 (ok, error)。"""
    try:
        subprocess.Popen(
            ["cmd", "/c", str(BAT_FILE)],
            cwd=str(BAT_FILE.parent),
            creationflags=subprocess.CREATE_NO_WINDOW,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True, ""
    except Exception as e:
        return False, str(e)


def script_exists() -> bool:
    return BAT_FILE.exists()
