"""
OCTools/services/ext_plugins/detection.py
───────────────────────────────────────────────
环境检测与插件扫描。

- find_python()：定位插件子进程使用的 Python 解释器。
  优先嵌入式运行时（embedded_python/），缺失时回退当前解释器（开发模式）。
- find_uv()：定位依赖安装工具 uv，缺失返回 None（由 installer 回退 pip）。
- detect_ui_mode()：按 requirements 自动判定插件 UI 加载模式
  （direct：主进程直载 / desc：控件树 JSON + 依赖隔离 / window：独立窗口）。
- scan_plugins()：扫描 plugins/ 下每个子目录，识别统一 tab 插件
  （tab_*.py + manifests/<name>.json），兼容旧 main.py 格式。
"""

import json
import os
import shutil
import sys
from dataclasses import dataclass

from services.ext_plugins import paths

# UI 加载模式
UI_DIRECT = "direct"    # 主进程直接 import，无依赖隔离
UI_DESC   = "desc"      # 子进程隔离 + 控件树 JSON，主进程渲染
UI_WINDOW = "window"    # 子进程隔离 + 独立窗口

# 非 PySide6 的第三方 UI 框架（requirements 中出现即判定为 window 模式）
THIRD_UI = {"pyqt5", "pyqt6", "pyqt", "tkinter", "wxpython", "wx",
            "kivy", "customtkinter", "pysimplegui", "pyside2"}

# PySide6 相关包（主进程已有，仅出现这些仍按 direct 处理）
PYSIDE_PKGS = {"pyside6", "pyside6-essentials", "pyside6-addons", "shiboken6"}


def find_python() -> str:
    """返回插件子进程解释器路径。

    打包环境：embedded_python/python.exe（Linux/macOS 为 bin/python3）；
    源码环境：回退 sys.executable（开发模式，仍按 deps/<id>/ 隔离依赖）。
    """
    ep = paths.embedded_python_dir()
    candidates = []
    if os.name == "nt":
        candidates.append(os.path.join(ep, "python.exe"))
    else:
        candidates.append(os.path.join(ep, "bin", "python3"))
        candidates.append(os.path.join(ep, "bin", "python"))
    for c in candidates:
        if os.path.isfile(c):
            return c
    if getattr(sys, "frozen", False):
        # 打包后仍找不到嵌入式运行时：提示错误由调用方决定是否继续
        return ""
    return sys.executable


def find_uv() -> str | None:
    """返回 uv 可执行文件路径；未找到返回 None。"""
    bundled = paths.uv_exe()
    if os.path.isfile(bundled):
        return bundled
    return shutil.which("uv")


@dataclass
class PluginSource:
    """扫描得到的插件源信息。"""
    plugin_id: str
    dir: str
    main_py: str
    requirements: str
    has_requirements: bool
    ui_mode: str = UI_DIRECT      # direct / desc / window
    module_path: str = ""         # tab 格式：import 模块路径（如 plugins.demo_numpy_a.tab_numpy_a）
    class_name: str = ""          # tab 格式：UI 类名（如 TabNumpyA）


def _parse_package_names(req_text: str) -> list[str]:
    """解析 requirements 文本中的包名（小写，忽略版本号与注释）。"""
    pkgs: list[str] = []
    for raw in req_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        # 去掉版本约束（==/>=/<=/>/</~=/!=）与 extras
        name = line.split("==")[0].split(">=")[0].split("<=")[0]
        name = name.split(">")[0].split("<")[0].split("~=")[0].split("!=")[0]
        name = name.strip().split("[", 1)[0].strip()
        if name:
            pkgs.append(name.lower().replace("_", "-"))
    return pkgs


def detect_ui_mode(req_text: str) -> str:
    """按 requirements 自动判定 UI 加载模式。

    - 无依赖 / 仅 PySide6（主进程已有）→ direct（主进程直接 import）
    - 含第三方 UI 框架（PyQt5/tkinter 等）→ window（独立窗口）
    - 其他依赖（numpy 等，可能为主进程没有/版本不同的库）→ desc（控件树 JSON + 依赖隔离）
    """
    pkgs = _parse_package_names(req_text)
    if not pkgs or set(pkgs) <= PYSIDE_PKGS:
        return UI_DIRECT
    if any(p in THIRD_UI for p in pkgs):
        return UI_WINDOW
    return UI_DESC


def _load_manifest(plugin_id: str) -> dict | None:
    """读取 plugins/manifests/<plugin_id>.json；缺失/损坏返回 None。"""
    mf = os.path.join(paths.plugins_dir(), "manifests", f"{plugin_id}.json")
    if not os.path.isfile(mf):
        return None
    try:
        with open(mf, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else None
    except (OSError, ValueError):
        return None


def _requirements_text(sub: str) -> str:
    """读取插件目录 requirements.txt 内容（缺失返回空串）。"""
    req = os.path.join(sub, "requirements.txt")
    if not os.path.isfile(req):
        return ""
    try:
        with open(req, "r", encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def scan_plugins() -> dict[str, PluginSource]:
    """扫描 plugins/ 下所有合法插件目录。

    统一 tab 格式：目录含 tab_*.py，manifest 位于 plugins/manifests/<name>.json，
    从 manifest 读取 class_name / module_path / ui_mode（ui_mode 缺省时按
    requirements 自动检测）。

    返回 {plugin_id: PluginSource}。
    """
    out: dict[str, PluginSource] = {}
    root = paths.plugins_dir()
    if not os.path.isdir(root):
        return out
    for name in sorted(os.listdir(root)):
        sub = os.path.join(root, name)
        if not os.path.isdir(sub) or name.startswith((".", "_")):
            continue
        if name == "manifests":   # 清单目录不是插件
            continue
        req_text = _requirements_text(sub)
        has_req = bool(req_text.strip())

        manifest = _load_manifest(name)
        if manifest is None:
            print(f"[外部插件] 跳过 {name}：缺少 plugins/manifests/{name}.json")
            continue
        module_path = manifest.get("module_path", "")
        class_name = manifest.get("class_name", "")
        ui_mode = manifest.get("ui_mode") or detect_ui_mode(req_text)
        if not module_path or not class_name:
            print(f"[外部插件] 跳过 {name}：manifest 缺少 module_path/class_name")
            continue
        out[name] = PluginSource(
            plugin_id=name,
            dir=sub,
            main_py="",                      # 统一由 host.py 加载
            requirements=os.path.join(sub, "requirements.txt"),
            has_requirements=has_req,
            ui_mode=ui_mode,
            module_path=module_path,
            class_name=class_name,
        )
    return out


def has_deps(plugin_id: str) -> bool:
    """deps/<plugin_id>/ 是否存在且非空。"""
    d = paths.plugin_deps_dir(plugin_id)
    if not os.path.isdir(d):
        return False
    try:
        return any(True for _ in os.scandir(d))
    except OSError:
        return False
