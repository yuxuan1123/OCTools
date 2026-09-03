"""
OCTools/ui/tabs/plugin_registry.py
───────────────────────────────────────────────
插件注册表：统一提供插件目录 / 清单目录 / 模块前缀 / sys.path 挂载与模块清理。

打包兼容（PyInstaller）：
  - 源码运行时：插件代码 ui/tabs/plugins/<名>/，以 ui.tabs.plugins.<名> 导入；
  - 打包后（sys.frozen 存在）：插件落在可执行文件同目录 plugins/<名>/，
    以普通文件系统包 plugins.<名> 导入——frozen 内置 importer 无法动态加载新模块。
  - 插件清单统一存放在 <插件根>/manifests/<名>.json。

注意：本模块只依赖标准库，避免 UI/配置耦合，供 tab_plugin / left_sidebar 共用。
"""

import os
import sys

# 是否处于打包（PyInstaller）环境
IS_FROZEN = bool(getattr(sys, "frozen", False))

_HERE = os.path.dirname(os.path.abspath(__file__))   # OCTools/ui/tabs


def _mount_dir() -> str:
    """插件挂载点：加入 sys.path 的目录（按此目录解析插件包）。"""
    if IS_FROZEN:
        return os.path.dirname(sys.executable)
    return os.path.normpath(os.path.join(_HERE, "..", ".."))   # OCTools 根目录


def _plugins_pkg() -> str:
    """插件包名空间：ui.tabs.plugins（源码）/ plugins（打包）。"""
    return "plugins" if IS_FROZEN else "ui.tabs.plugins"


def plugins_dir() -> str:
    """插件代码根目录（含 __init__.py，内部按插件名组织子目录）。"""
    if IS_FROZEN:
        return os.path.join(_mount_dir(), "plugins")
    return os.path.join(_HERE, "plugins")


def plugin_manifests_dir() -> str:
    """插件清单目录：<插件根>/manifests。"""
    return os.path.join(plugins_dir(), "manifests")


def builtin_manifests_dir() -> str:
    """内建 tab 清单目录：ui/tabs/manifests（与旧 left_sidebar._resolve_manifests_dir 同源）。"""
    return os.path.join(_HERE, "manifests")


def iter_manifest_dirs():
    """返回所有需要扫描的 manifest 目录（去重、跳过不存在的）。

    供 left_sidebar（左侧导航）与 tab_settings（设置页）统一使用，
    避免两处目录清单不一致导致「插件进了导航却没出现在设置页」之类问题。

    覆盖三类位置：
      - 内建 tab 清单：ui/tabs/manifests
      - 旧版插件子目录（向后兼容）：ui/tabs/manifests/plugins
      - 用户导入插件（打包后挂载目录）：<插件根>/manifests
    """
    candidates = [
        builtin_manifests_dir(),
        os.path.join(builtin_manifests_dir(), "plugins"),
        plugin_manifests_dir(),
    ]
    seen, out = set(), []
    for d in candidates:
        ad = os.path.abspath(d)
        if ad in seen:
            continue
        seen.add(ad)
        if os.path.isdir(ad):
            out.append(ad)
    return out


def mount() -> str:
    """确保插件挂载点已在 sys.path（幂等），返回挂载目录。"""
    d = _mount_dir()
    if d not in sys.path:
        sys.path.insert(0, d)
    return d


def module_prefix(name: str) -> str:
    """插件模块前缀，如 ui.tabs.plugins.tree / plugins.tree。"""
    return f"{_plugins_pkg()}.{name}"


def purge_plugin_modules(name: str):
    """从 sys.modules 移除插件及其子模块，避免卸载/重装后残留旧代码。"""
    prefix = _plugins_pkg()
    for key in list(sys.modules):
        if key == prefix or key.startswith(prefix + "."):
            sys.modules.pop(key, None)


def ensure_plugin_dirs():
    """确保插件根 / 清单目录存在、插件根为可导入包，并完成 sys.path 挂载。

    打包后 exe 位于只读目录（如 Program Files）时可能抛 OSError，调用方自行兜底。
    """
    mount()
    root = plugins_dir()
    os.makedirs(root, exist_ok=True)
    os.makedirs(plugin_manifests_dir(), exist_ok=True)
    init = os.path.join(root, "__init__.py")
    if not os.path.exists(init):
        with open(init, "w", encoding="utf-8") as f:
            f.write('"""OCTools 用户导入的本地 tab 插件包。"""\n')