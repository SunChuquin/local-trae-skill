@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ============================================
echo  任务终端 - 文档处理进度监控
echo  显示进度条与任务步骤指导，Ctrl+C 退出
echo ============================================
echo.

if exist ".venv310\Scripts\python.exe" (
    ".venv310\Scripts\python.exe" task_terminal.py %*
) else if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" task_terminal.py %*
) else (
    python task_terminal.py %*
)

if errorlevel 1 (
    echo.
    echo 运行结束。若提示无法连接后端，请先运行 start.bat 启动服务。
    pause
)
