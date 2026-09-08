# OCTools 打包为 exe 方案

## v2 变更（插件运行时机制，2026-09-08）

> 打包后插件全部以 exe 同目录源码包加载（`D:\pyex\OCTools\plugins\`，从源码复制或由应用内导入），
> 不打进 PYZ。插件缺失依赖由内置运行时按 requirements.txt 自动安装。

### 三个关键修复

1. **PYZ 模块缺失**（报错 `No module named 'ui.tabs.tab_component.card_widgets'`）
   - 原因：`collect_submodules()` 枚举时会真实 import 子包，`ui.tabs` 链上导入失败导致整棵子树被静默跳过
   - 修复：[scripts/build.spec](../../scripts/build.spec) 改用 `_walk_pkg_modules()`（os.walk 文件系统枚举，不 import）收集 `ui/core/services/config` 全部模块
   - 插件子进程宿主 `services/ext_plugins/host.py` 必须以 **datas** 打包（`manager.HOST_PY` 用 `__file__` 推导真实路径，embedded python 无法从 PYZ 读）

2. **内置插件运行时**（desc/window 模式插件按 requirements.txt 自动装库）
   - `services/ext_plugins/paths.py` 约定：`<exe目录>/embedded_python/python.exe` + `<exe目录>/uv.exe`
   - 供给脚本：[scripts/provision_runtime.ps1](../../scripts/provision_runtime.ps1)（下载 uv + Python 3.12.8 embeddable，补 tkinter 支持，修 `._pth`；下载缓存在 `.build_cache/`）
   - [build.bat](../../build.bat) 构建后自动调用；装库流程 `uv pip install --python <embedded> --target deps/<id> -r requirements.txt`，日志见 `logs/install_<id>.log`

3. **构建前必须杀残留进程**：`OCTools.exe` 运行中会锁 `logs\app.log`，导致 PyInstaller 清理产物目录 PermissionError（build.bat 已加 `taskkill`）

### 分发清单

```
D:\pyex\OCTools\
├── OCTools.exe / _internal\      # 主程序（PyInstaller onedir）
├── plugins\                      # 插件源码包（随包分发/应用内导入，运行时可写）
├── embedded_python\              # 嵌入式 Python 3.12.8（含 tkinter 支持）
├── uv.exe                        # 依赖安装工具
├── deps\<plugin_id>\             # 插件依赖自动安装目标（运行时生成）
├── ms-playwright\                # 浏览器占位（MD→图片功能）
└── logs\ config\ config.json     # 运行时生成
```


## Context

用户需要把 OCTools 项目打包成 Windows 可执行文件分发，要求排除 `mvp/`（最小试点，与主项目无关）和 `plugins/`（外部插件目录，运行时按需加载）两个目录。交付物需包含可复用打包脚本（bat/ps1），方便下次增量打包。

项目已有 PyInstaller 兼容设计：`config/paths.py` 区分源码/打包环境（`sys.frozen` 时 ROOT=exe 目录，配置写进 `exe目录/config/presets/`）；`ui/tabs/plugin_registry.py` 区分插件挂载点（打包后用 exe 同目录的 `plugins/`）；`main.py` 的 `from plugins.translation.preload import` 在 try/except 内，排除后静默失败不崩溃。

## 决策（已与用户确认）

- **打包模式**：onedir（生成 `dist/OCTools/` 文件夹），启动快、适合大型项目
- **外部资源**：ffmpeg / AI 模型（D:/AI_Model）不打包，运行时按 `config/ui_config.json` 路径加载（缺失走 except 兜底）；playwright 主项目代码不直接引用（仅在 plugins/ 内），排除 plugins 后不收集，无需处理浏览器
- **脚本**：`build.bat`（最通用，双击即可），内部调用同目录 `build.spec`

## 排除策略

| 目录 | 是否被 main.py 引用 | 处理方式 |
|------|-------------------|---------|
| `mvp/` | 否 | PyInstaller 默认只收集被 import 模块，自动不包含；额外在 spec `excludes` 显式声明 |
| `plugins/` | `main.py` 有 `from plugins.translation.preload import`（在 try/except 内） | spec `excludes=['plugins']`，运行时 import 失败被 `except Exception: pass` 捕获，PluginManager.scan() 扫描不存在目录时基于 `os.path.isdir` 跳过 |

## 数据文件（datas）

打包进 exe 同目录（onedir 模式下 `_internal/` 内镜像项目结构）：

- `resources/` → `resources/`（图标 svg/png，1.1MB，139 文件，main.py 用 yin-yang.svg，ui_config.json 引用 resources/icons/）
- `config/ui_config.json` → `config/ui_config.json`（UI 配置，ui_config.py 的 `_ROOT` 在打包后指向 `_MEIPASS`，能读到）
- `config/*.py` → 自动作为代码模块收集（无需单独 datas）
- `ui/tabs/manifests/*.json` → `ui/tabs/manifests/`（内建 tab 清单，plugin_registry 的 `builtin_manifests_dir()` 读取）

注意：`config/presets/` 不打包（运行时在 exe 目录动态生成，由 `config/paths.py` 的 `ROOT = exe 目录` 处理）。

## Hidden Imports

PySide6 通常能被 PyInstaller 自动收集，但以下需显式声明（main.py 或 ui 代码用到）：

- `PySide6.QtSvg`（main.py 用 `QSvgRenderer` 渲染任务栏图标）
- `PySide6.QtSvgWidgets`
- `PySide6.QtPrintSupport`（文档打印）
- `PySide6.QtMultimedia`（音频播放）
- `playwright` + 子模块（`core/engines/document_engine.py:1034` 函数内延迟导入，PyInstaller 静态分析收集不到，需 `collect_submodules('playwright')`）

## playwright 处理（已确认）

`core/engines/document_engine.py` 的 `_html_to_images_playwright` 用 `from playwright.sync_api import sync_playwright` 做 MD→图片（HTML 截图），失败时退回 reportlab。

- **Python 包**：作为 hidden import 打包（`collect_submodules('playwright')`）
- **浏览器二进制**（chromium）：不在 pip 包内，当前机器未安装（`$env:LOCALAPPDATA\ms-playwright` 不存在）。方案：
  1. 创建 runtime hook `scripts/pyi_rt_hook.py`，启动时设置 `os.environ['PLAYWRIGHT_BROWSERS_PATH'] = <exe目录>/ms-playwright`
  2. `build.bat` 构建后在 `dist/OCTools/` 下创建空 `ms-playwright/` 占位目录
  3. 用户后续把 chromium（运行 `playwright install chromium` 后的目录内容）放进去即生效

runtime hook 内容（`scripts/pyi_rt_hook.py`）：
```python
import os, sys
if getattr(sys, "frozen", False):
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(
        os.path.dirname(sys.executable), "ms-playwright")
```

## 实现步骤

### 1. 创建 `scripts/build.spec`（PyInstaller 规范文件）

关键字段：
```python
# -*- mode: python ; coding: utf-8 -*-
import os, sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources'),
        ('config/ui_config.json', 'config'),
        ('ui/tabs/manifests', 'ui/tabs/manifests'),
    ],
    hiddenimports=[
        'PySide6.QtSvg',
        'PySide6.QtSvgWidgets',
        'PySide6.QtPrintSupport',
        'PySide6.QtMultimedia',
    ] + collect_submodules('playwright'),
    hookspath=[],
    runtimehooks=['scripts/pyi_rt_hook.py'],
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
    upx=False,           # UPX 压缩与 PySide6 不兼容，禁用
    console=False,        # GUI 应用，无控制台
    icon='resources/icons/logo128.png',  # 任务栏图标
)
coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    name='OCTools',
)
```

### 2. 创建 `scripts/pyi_rt_hook.py`（runtime hook）

启动时设置 playwright 浏览器路径指向 exe 同目录的 `ms-playwright/`：
```python
import os, sys
if getattr(sys, "frozen", False):
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(
        os.path.dirname(sys.executable), "ms-playwright")
```

### 3. 创建 `build.bat`（可复用打包脚本，项目根）

逻辑：
1. 切到脚本所在目录（`cd /d "%~dp0"`）
2. 用项目 venv 的 python（`.venv\Scripts\python.exe`）
3. 检查 PyInstaller 是否安装，缺失则 `pip install pyinstaller`
4. 清理旧产物：`D:\pyex\OCTools`（上次输出）
5. 执行 `python -m PyInstaller scripts\build.spec --noconfirm --distpath D:\pyex --workpath build`
6. 构建后在 `D:\pyex\OCTools\` 下创建空 `ms-playwright\` 占位目录
7. 打印 `D:\pyex\OCTools\OCTools.exe` 路径

```bat
@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PY=.venv\Scripts\python.exe
set DIST=D:\pyex
if not exist %PY% ( echo [ERR] 未找到 .venv; exit /b 1 )
%PY% -c "import PyInstaller" 2>nul || %PY% -m pip install pyinstaller
if exist "%DIST%\OCTools" rmdir /s /q "%DIST%\OCTools"
if exist build rmdir /s /q build
%PY% -m PyInstaller scripts\build.spec --noconfirm --distpath "%DIST%" --workpath build
if not exist "%DIST%\OCTools\ms-playwright" mkdir "%DIST%\OCTools\ms-playwright"
echo. & echo [DONE] %DIST%\OCTools\OCTools.exe
pause
```

## 关键文件

- 新建 `scripts/build.spec` — PyInstaller 规范
- 新建 `scripts/pyi_rt_hook.py` — runtime hook（playwright 浏览器路径）
- 新建 `build.bat` — 项目根可复用打包脚本
- 不修改任何现有源码（`config/paths.py`、`plugin_registry.py` 已兼容 PyInstaller）

## 验证

1. 运行 `build.bat`，观察构建日志无 ERROR
2. 进入 `D:\pyex\OCTools\`，双击 `OCTools.exe` 启动
3. 确认：
   - 窗口正常显示，任务栏图标为 logo128.png
   - 左侧导航加载内建 tab（来自 `ui/tabs/manifests/`），无 plugins/mvp 相关报错
   - 首页 Hero 卡片时钟跳动、任务清单可增删
   - exe 同目录生成 `config/presets/`（首次写入配置）
4. 若启动闪退，命令行运行 `D:\pyex\OCTools\OCTools.exe` 看控制台错误（临时改 spec `console=True` 重建调试）

## 已知限制（需告知用户）

- **ffmpeg / AI 模型 / espeak**：不打包，运行时按 `config/ui_config.json` 绝对路径加载；目标机器无对应路径时，相关功能（语音合成、翻译、TTS）不可用但不崩溃（已 except 兜底）。用户需在目标机器配置这些路径或随 exe 分发对应二进制。
- **pandoc / poppler**（pypandoc/pdf2image 外部二进制）：不打包，需用户自行安装。
- **playwright 浏览器**：`D:\pyex\OCTools\ms-playwright\` 为空占位，MD→图片功能初次不可用（退回 reportlab）。用户运行 `playwright install chromium` 后把 `%LOCALAPPDATA%\ms-playwright\chromium-*` 内容复制进去即生效。
- **体积**：含 PySide6 + paddleocr + numpy + pandas + playwright 等，`D:\pyex\OCTools\` 预计 1-1.5GB。
- **首次启动**：exe 目录需可写（写 config/presets），`D:\pyex\OCTools\` 可写满足。
