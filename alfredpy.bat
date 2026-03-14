@echo off
REM AlfredPy Windows 启动脚本

setlocal
set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

echo.
echo 🚀 AlfredPy - 正在启动...
echo.

REM 检查虚拟环境
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
    echo ✅ 使用虚拟环境
) else (
    echo ⚠️  未找到虚拟环境，使用系统 Python
)

REM 解析参数
set MODE=gui
if "%1"=="gui" set MODE=gui
if "%1"=="tui" set MODE=tui
if "%1"=="hotkey" set MODE=hotkey
if "%1"=="list" set MODE=list

REM 执行对应模式
if "%MODE%"=="gui" (
    python -m alfredpy --gui %2 %3
) else if "%MODE%"=="tui" (
    python -m alfredpy %2 %3
) else if "%MODE%"=="hotkey" (
    python -m alfredpy.gui.hotkey
) else if "%MODE%"=="list" (
    python -m alfredpy --list %2 %3
)

endlocal
