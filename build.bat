@echo off
chcp 65001 >nul
REM ============================================
REM  OCTools 打包脚本（可复用）
REM  产物：D:\pyex\OCTools\OCTools.exe
REM  排除：mvp/、plugins/（插件以 exe 同目录源码包运行时加载）
REM  构建 + 运行时供给（embedded_python + uv）一键完成
REM ============================================

cd /d "%~dp0"
set PY=.venv\Scripts\python.exe
set DIST=D:\pyex

if not exist %PY% (
    echo [ERR] 未找到 .venv\Scripts\python.exe
    echo        请先创建虚拟环境并安装依赖
    pause
    exit /b 1
)

echo [0/5] 关闭残留的 OCTools 进程（避免文件占用导致清理失败）...
taskkill /IM OCTools.exe /F >nul 2>&1
timeout /t 2 /nobreak >nul

echo [1/5] 检查 PyInstaller...
%PY% -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo       未安装，正在安装 pyinstaller...
    %PY% -m pip install pyinstaller
)

echo [2/5] 清理旧产物...
if exist "%DIST%\OCTools" rmdir /s /q "%DIST%\OCTools"
if exist build rmdir /s /q build

echo [3/5] 执行 PyInstaller 构建（onedir 模式，约需 3-10 分钟）...
%PY% -m PyInstaller scripts\build.spec --noconfirm --distpath "%DIST%" --workpath build
if errorlevel 1 (
    echo.
    echo [FAIL] 构建失败，请查看上方日志
    pause
    exit /b 1
)

echo [4/5] 供给插件运行时（embedded_python + uv.exe，首次需联网下载）...
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\provision_runtime.ps1 -Dist "%DIST%\OCTools"
if errorlevel 1 (
    echo [WARN] 运行时供给失败，desc/window 模式插件将无法自动装库
)

echo [5/5] 创建 playwright 浏览器目录占位...
if not exist "%DIST%\OCTools\ms-playwright" mkdir "%DIST%\OCTools\ms-playwright"

echo.
echo ============================================
echo  [DONE] 打包完成
echo  exe 路径: %DIST%\OCTools\OCTools.exe
echo  插件运行时: %DIST%\OCTools\embedded_python\ + uv.exe
echo  浏览器目录: %DIST%\OCTools\ms-playwright\ (空，需放入 chromium)
echo ============================================
echo.
pause
