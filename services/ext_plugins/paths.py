"""
OCTools/services/ext_plugins/paths.py
───────────────────────────────────────────────
外部插件系统的路径解析（源码 / 打包环境统一）。

路径规则：
  - 源码运行时：根目录 = 项目根（OCTools/）；
  - 打包后（sys.frozen）：根目录 = 可执行文件所在目录（可写、持久）。

约定目录：
  <root>/plugins/<plugin_id>/   插件源代码（main.py + requirements.txt）
  <root>/deps/<plugin_id>/      插件依赖安装目标
  <root>/logs/                  统一日志目录
  <root>/config.json            插件配置
  <root>/embedded_python/       嵌入式 Python 运行时（仅打包环境）
  <root>/uv.exe                 依赖安装工具（仅打包环境）
"""

import os
import sys


def app_root() -> str:
    """主程序根目录：打包后为 exe 所在目录，源码为项目根。"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def plugins_dir() -> str:
    """外部插件源代码根目录。"""
    return os.path.join(app_root(), "plugins")


def deps_dir() -> str:
    """插件依赖安装根目录。"""
    return os.path.join(app_root(), "deps")


def logs_dir() -> str:
    """日志目录。"""
    return os.path.join(app_root(), "logs")


def config_file() -> str:
    """插件配置 JSON 路径。"""
    return os.path.join(app_root(), "config.json")


def plugin_source_dir(plugin_id: str) -> str:
    return os.path.join(plugins_dir(), plugin_id)


def plugin_deps_dir(plugin_id: str) -> str:
    return os.path.join(deps_dir(), plugin_id)


def embedded_python_dir() -> str:
    """嵌入式 Python 运行时目录（打包后随 exe 分发）。"""
    return os.path.join(app_root(), "embedded_python")


def uv_exe() -> str:
    """随主程序分发的 uv 可执行文件（Windows 为 uv.exe）。"""
    name = "uv.exe" if os.name == "nt" else "uv"
    return os.path.join(app_root(), name)


def app_log_file() -> str:
    return os.path.join(logs_dir(), "app.log")


def install_log(plugin_id: str) -> str:
    return os.path.join(logs_dir(), f"install_{plugin_id}.log")


def crash_log(plugin_id: str) -> str:
    return os.path.join(logs_dir(), f"crash_{plugin_id}.log")


def plugin_log(plugin_id: str) -> str:
    return os.path.join(logs_dir(), f"plugin_{plugin_id}.log")


def ensure_dirs():
    """确保 plugins / deps / logs 目录存在。"""
    for d in (plugins_dir(), deps_dir(), logs_dir()):
        os.makedirs(d, exist_ok=True)
