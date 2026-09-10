@echo off
title Auto Setup: Shutdown A+B + Open Feishu Docs

:: 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Please run as administrator!
    pause
    exit /b
)

echo ============================================
echo  Auto Setup: Shutdown Tasks + Feishu Docs
echo  (No input required, running automatically)
echo ============================================

:: -------- 1. 安装场景A ----------
echo [Step 1/3] Installing Scenario A (11:55 confirm, 12:00 shutdown)...
call :createReminderScript "12" "11:55" "12:00"
schtasks /create /tn "ShutdownConfirmPrompt" /tr "\"%~dp0reminder_12.bat\"" /sc once /st 11:55 /f >nul 2>&1
if %errorLevel% equ 0 (
    echo   Scenario A installed successfully.
) else (
    echo   Scenario A installation FAILED.
)

:: -------- 2. 安装场景B ----------
echo [Step 2/3] Installing Scenario B (17:55 remind, 18:00 shutdown)...
call :createReminderScript "18" "17:55" "17:58"
schtasks /create /tn "ShutdownReminder" /tr "\"%~dp0reminder_18.bat\"" /sc once /st 17:55 /f >nul 2>&1
schtasks /create /tn "OneTimeShutdown" /tr "shutdown /s /f /t 120" /sc once /st 17:58 /f >nul 2>&1
if %errorLevel% equ 0 (
    echo   Scenario B installed successfully.
) else (
    echo   Scenario B installation FAILED.
)

:: -------- 3. 打开飞书文档 ----------
echo [Step 3/3] Opening Feishu docs in default browser...
call :openFeishuDocs

echo ============================================
echo  All steps completed.
echo  - Scenarios A and B installed.
echo  - Three Feishu docs opened in browser.
echo ============================================
pause
exit /b

:: -------------------------------------------------
:: 子程序：生成 reminder 脚本
:: -------------------------------------------------
:createReminderScript
setlocal
set "TIME_LABEL=%~1"
set "PROMPT_TIME=%~2"
set "SHUTDOWN_TIME=%~3"
set "SCRIPT_PATH=%~dp0reminder_%TIME_LABEL%.bat"
(
echo @echo off
echo title Shutdown Confirmation %TIME_LABEL%
echo cd /d "%~dp0"
echo powershell -NoProfile -STA -Command "exit ^([System.Windows.Forms.MessageBox]::Show('Shut down the computer at %SHUTDOWN_TIME% ?','Shutdown Confirmation',4,32,0,331776^)^)"
echo if not "%%errorlevel%%"=="6" exit /b
echo schtasks /create /tn "ShutdownAt%TIME_LABEL%" /tr "shutdown /s /f /t 60" /sc once /st %SHUTDOWN_TIME% /f
echo if "%%errorlevel%%"=="0" ^(
echo     powershell -NoProfile -STA -Command "[System.Windows.Forms.MessageBox]::Show('Shutdown scheduled at %SHUTDOWN_TIME%. To cancel run: shutdown /a','Shutdown Scheduled',0,331776]"
echo ^) else ^(
echo     powershell -NoProfile -STA -Command "[System.Windows.Forms.MessageBox]::Show('Failed to schedule shutdown.','Error',0,331776]"
echo ^)
echo exit /b
) > "%SCRIPT_PATH%"
exit /b

:: -------------------------------------------------
:: 子程序：无条件打开三个飞书文档
:: 说明：走浏览器 HTTP，不依赖飞书客户端，
::       飞书进程检测已移除，三个网页必定尝试打开。
:: -------------------------------------------------
:openFeishuDocs
set "CHROME="
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" set "CHROME=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
if not defined CHROME if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" set "CHROME=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
if not defined CHROME if exist "%LocalAppData%\Google\Chrome\Application\chrome.exe" set "CHROME=%LocalAppData%\Google\Chrome\Application\chrome.exe"

:: 注册表兜底（部分绿色/自定义安装）
if not defined CHROME (
  for /f "tokens=2,*" %%A in ('reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" /ve 2^>nul ^| find "REG_"') do set "CHROME=%%B"
)
if not defined CHROME (
  for /f "tokens=2,*" %%A in ('reg query "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" /ve 2^>nul ^| find "REG_"') do set "CHROME=%%B"
)

if not defined CHROME (
  echo   Chrome not found, open with default browser instead.
  start "" "https://dej4esdop1.feishu.cn/wiki/WEpJwuaZditGJAkDJG6cGB4knQQ"
  start "" "https://dej4esdop1.feishu.cn/sheets/shtcnj4YBiK5miobFJmXzf6wNcf?sheet=VE8X5A"
  start "" "https://dej4esdop1.feishu.cn/wiki/RXTcw0iDXiYKDyk6yZZcVIN1nid?table=tbl8UVBA5oiQDvIX&view=vewH6RqXnd"
  exit /b
)

start "" "%CHROME%" --new-window ^
  "https://dej4esdop1.feishu.cn/wiki/WEpJwuaZditGJAkDJG6cGB4knQQ" ^
  "https://dej4esdop1.feishu.cn/sheets/shtcnj4YBiK5miobFJmXzf6wNcf?sheet=VE8X5A" ^
  "https://dej4esdop1.feishu.cn/wiki/RXTcw0iDXiYKDyk6yZZcVIN1nid?table=tbl8UVBA5oiQDvIX&view=vewH6RqXnd"
echo   Three Feishu docs opened in Chrome (one window, three tabs).
exit /b