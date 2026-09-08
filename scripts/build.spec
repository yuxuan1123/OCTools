# -*- mode: python ; coding: utf-8 -*-
"""OCTools PyInstaller 规范文件（onedir 模式）。

排除 mvp/ 与 plugins/，打包 resources/、config/ui_config.json、ui/tabs/manifests/。
playwright Python 包通过 collect_submodules 收集；浏览器二进制由 runtime hook
指向 exe 同目录的 ms-playwright/（build.bat 创建空占位）。

用法（项目根执行）：
    .venv\Scripts\python.exe -m PyInstaller scripts\build.spec --noconfirm ^
        --distpath D:\pyex --workpath build
产物：D:\pyex\OCTools\OCTools.exe
"""

import os
from PyInstaller.utils.hooks import collect_submodules

# 项目根目录（spec 文件在 scripts/ 下，上跳一层）
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(SPEC)))


def _walk_pkg_modules(pkg_dir: str) -> list:
    """直接从文件系统枚举包内全部模块。

    不用 collect_submodules：它枚举时会真实 import 各子包，
    任何一个子包导入失败（如 ui.tabs 链上引用了被排除的 plugins.*）
    都会导致整棵子树被静默跳过，打包后运行时插件 import 报
    No module named 'ui.tabs.tab_component.card_widgets' 之类错误。
    """
    mods = []
    base = os.path.dirname(pkg_dir)
    for dirpath, dirnames, filenames in os.walk(pkg_dir):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), base)
            mod = os.path.splitext(rel)[0].replace(os.sep, ".").replace("/", ".")
            if mod.endswith(".__init__"):
                mod = mod[: -len(".__init__")]
            mods.append(mod)
    return mods


# 应用内包全量收集（插件 plugins/ 仍排除：运行时以 exe 同目录源码包加载）
_APP_MODULES = []
for _pkg in ("ui", "core", "services", "config"):
    _d = os.path.join(_ROOT, _pkg)
    if os.path.isdir(_d):
        _APP_MODULES += _walk_pkg_modules(_d)

block_cipher = None

a = Analysis(
    [os.path.join(_ROOT, 'main.py')],
    pathex=[_ROOT],
    binaries=[],
    datas=[
        (os.path.join(_ROOT, 'resources'), 'resources'),
        (os.path.join(_ROOT, 'config', 'ui_config.json'), 'config'),
        (os.path.join(_ROOT, 'ui', 'tabs', 'manifests'), os.path.join('ui', 'tabs', 'manifests')),
        # 插件子进程宿主脚本：manager.HOST_PY 用 __file__ 推导路径，
        # embedded python 需要真实源文件（不能在 PYZ 里）
        (os.path.join(_ROOT, 'services', 'ext_plugins', 'host.py'), os.path.join('services', 'ext_plugins')),
    ],
    hiddenimports=[
        'PySide6.QtSvg',
        'PySide6.QtSvgWidgets',
        'PySide6.QtPrintSupport',
        'PySide6.QtMultimedia',
    ] + collect_submodules('playwright')
      # 项目内包全量模块：动态导入的 tab / 插件运行时依赖的 app 模块
      # （main_window 按 manifest 用 importlib.import_module 加载，
      #   插件源码也 import ui.* / config.* / core.*，静态分析覆盖不到）
      + _APP_MODULES,
    hookspath=[],
    runtimehooks=[os.path.join(_ROOT, 'scripts', 'pyi_rt_hook.py')],
    excludes=['mvp', 'plugins', 'tests', 'pytest', 'unittest'],
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz, a.scripts, [],
    name='OCTools',
    debug=False,
    strip=False,
    upx=False,              # UPX 与 PySide6 不兼容
    console=False,           # GUI 应用，无控制台
    icon=os.path.join(_ROOT, 'resources', 'icons', 'logo128.png'),
)

coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    name='OCTools',
)
