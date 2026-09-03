@echo off
chcp 65001 > nul
echo ========================================
echo         正在关闭服务...
echo ========================================
echo.

:: 关闭后端 (端口8000)
echo [1/2] 正在关闭后端服务...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo 找到进程 PID: %%a
    taskkill /F /PID %%a 2>nul
    if errorlevel 1 (
        echo 关闭失败，尝试强制关闭...
        taskkill /F /PID %%a
    )
)

:: 关闭前端 (端口3000，如果不是请修改)
echo.
echo [2/2] 正在关闭前端服务...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') do (
    echo 找到进程 PID: %%a
    taskkill /F /PID %%a 2>nul
    if errorlevel 1 (
        echo 关闭失败，尝试强制关闭...
        taskkill /F /PID %%a
    )
)

echo.
echo ========================================
echo         所有服务已关闭！
echo ========================================
timeout /t 2 /nobreak > nul