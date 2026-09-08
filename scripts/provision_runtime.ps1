# OCTools 打包运行时供给脚本
# ─────────────────────────────────────────────
# 为打包产物（onedir）提供外部插件运行所需的：
#   1. embedded_python\  嵌入式 Python（插件子进程解释器 + 按 requirements 装库的载体）
#   2. uv.exe            依赖安装工具（uv pip install --python ... --target deps/<id>）
#   3. tkinter 支持      window 模式插件用（embeddable 包不含 tkinter，从系统 Python 复制）
#
# 产物布局由 services/ext_plugins/paths.py + detection.py 约定：
#   <dist>/embedded_python/python.exe
#   <dist>/uv.exe
#
# 用法：powershell -ExecutionPolicy Bypass -File scripts\provision_runtime.ps1 [-Dist D:\pyex\OCTools]
# 下载缓存在项目根 .build_cache\，重复构建不重复下载。

param(
    [string]$Dist = "D:\pyex\OCTools",
    [string]$PyVersion = "3.12.8"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot          # 项目根
$Cache = Join-Path $Root ".build_cache"
New-Item $Cache -ItemType Directory -Force | Out-Null

function Get-FileWithFallback {
    param([string[]]$Urls, [string]$OutFile)
    if (Test-Path $OutFile) { Write-Host "  [cache] $OutFile"; return $true }
    foreach ($u in $Urls) {
        try {
            Write-Host "  [download] $u"
            Invoke-WebRequest -Uri $u -OutFile $OutFile -UseBasicParsing -TimeoutSec 300
            return $true
        } catch { Write-Host "  [fallback] $($_.Exception.Message)" }
    }
    return $false
}

# ── 1. uv.exe ────────────────────────────────
$uvDst = Join-Path $Dist "uv.exe"
if (Test-Path $uvDst) {
    Write-Host "[1/5] uv.exe 已存在"
} else {
    Write-Host "[1/5] 获取 uv.exe ..."
    $zip = Join-Path $Cache "uv-win64.zip"
    $ok = Get-FileWithFallback -OutFile $zip -Urls @(
        "https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip",
        "https://ghproxy.cn/https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip",
        "https://gh-proxy.com/https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip"
    )
    if (-not $ok) { throw "uv.exe 下载失败，请检查网络或手动放置 $uvDst" }
    $tmp = Join-Path $Cache "uv_extract"
    if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
    Expand-Archive $zip $tmp -Force
    $uvInner = Get-ChildItem $tmp -Recurse -Filter "uv.exe" | Select-Object -First 1
    Copy-Item $uvInner.FullName $uvDst -Force
    Remove-Item $tmp -Recurse -Force
    Write-Host "  [ok] $uvDst"
}

# ── 2. embedded_python ───────────────────────
$ep = Join-Path $Dist "embedded_python"
$epPy = Join-Path $ep "python.exe"
if (Test-Path $epPy) {
    Write-Host "[2/5] embedded_python 已存在"
} else {
    Write-Host "[2/5] 获取嵌入式 Python $PyVersion ..."
    $zip = Join-Path $Cache "python-$PyVersion-embed-amd64.zip"
    $ok = Get-FileWithFallback -OutFile $zip -Urls @(
        "https://www.python.org/ftp/python/$PyVersion/python-$PyVersion-embed-amd64.zip",
        "https://mirrors.huaweicloud.com/python/$PyVersion/python-$PyVersion-embed-amd64.zip",
        "https://registry.npmmirror.com/-/binary/python/$PyVersion/python-$PyVersion-embed-amd64.zip"
    )
    if (-not $ok) { throw "嵌入式 Python 下载失败，请检查网络或手动放置 $epPy" }
    if (Test-Path $ep) { Remove-Item $ep -Recurse -Force }
    Expand-Archive $zip $ep -Force
    Write-Host "  [ok] $ep"
}

# ── 3. 修补 ._pth（启用 DLLs / Lib / site-packages）──
Write-Host "[3/5] 修补 python ._pth ..."
$pth = Get-ChildItem $ep -Filter "python*._pth" | Select-Object -First 1
if ($pth) {
    # zip 命名规则：python312.zip（主+次版本，无点无补丁号）
    $short = ($PyVersion -replace '\.\d+$', '') -replace '\.', ''
    $zipName = "python$short.zip"
    $actualZip = Get-ChildItem $ep -Filter "python*.zip" | Select-Object -First 1
    if ($actualZip) { $zipName = $actualZip.Name }
    # 注：embeddable 3.12 的 ._pth 不支持 environment 指令（会被当作路径条目），
    # PYTHONPATH 由 host.py 自行读取注入 sys.path（见 host.py main）
    @"
$zipName
.
DLLs
Lib
Lib\site-packages
import site
"@ | Set-Content $pth.FullName -Encoding ascii
    Write-Host "  [ok] $($pth.Name)"
} else {
    Write-Host "  [warn] 未找到 ._pth 文件"
}

# ── 4. tkinter 支持（window 模式插件）────────
Write-Host "[4/5] 补齐 tkinter 支持 ..."
$pycfg = Join-Path $Root ".venv\pyvenv.cfg"
$base = $null
if (Test-Path $pycfg) {
    foreach ($line in Get-Content $pycfg) {
        if ($line -match "^\s*home\s*=\s*(.+)$") { $base = $Matches[1].Trim() }
    }
}
if ($base -and (Test-Path $base)) {
    New-Item (Join-Path $ep "DLLs") -ItemType Directory -Force | Out-Null
    New-Item (Join-Path $ep "Lib") -ItemType Directory -Force | Out-Null
    # tkinter 纯 Python 包
    $srcTk = Join-Path $base "Lib\tkinter"
    if (Test-Path $srcTk) {
        Copy-Item $srcTk (Join-Path $ep "Lib\tkinter") -Recurse -Force
        Write-Host "  [ok] Lib\tkinter"
    }
    # _tkinter.pyd + tcl/tk DLL（可能在 DLLs\ 或根目录）
    foreach ($f in @("_tkinter.pyd", "tcl86t.dll", "tk86t.dll", "zlib1.dll")) {
        $src = @((Join-Path $base "DLLs\$f"), (Join-Path $base $f)) | Where-Object { Test-Path $_ } | Select-Object -First 1
        if ($src) {
            Copy-Item $src (Join-Path $ep "DLLs\$f") -Force
            Write-Host "  [ok] DLLs\$f"
        }
    }
    # tcl 脚本库数据
    $srcTcl = Join-Path $base "tcl"
    if (Test-Path $srcTcl) {
        Copy-Item $srcTcl (Join-Path $ep "tcl") -Recurse -Force
        Write-Host "  [ok] tcl\"
    }
} else {
    Write-Host "  [warn] 未找到基础 Python（$base），tkinter 插件将不可用"
}

# ── 5. 自检 ──────────────────────────────────
Write-Host "[5/5] 自检 ..."
& $epPy -c "import sys; print('  embedded python:', sys.version.split()[0])"
& $epPy -c "import tkinter; print('  tkinter import: ok')" 2>$null
if ($LASTEXITCODE -ne 0) { Write-Host "  [warn] tkinter 导入失败（window 模式插件不可用）" }
& $uvDst --version | ForEach-Object { Write-Host "  uv: $_" }

Write-Host ""
Write-Host "[DONE] 运行时供给完成：$Dist"
