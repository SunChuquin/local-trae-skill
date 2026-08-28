@echo off
echo ============================================
echo 个人私有文档 Skill 系统启动脚本
echo ============================================

rem 优先使用 .venv310（Python 3.10 环境），否则回退全局 python
set "PY=python"
if exist "%~dp0.venv310\Scripts\python.exe" set "PY=%~dp0.venv310\Scripts\python.exe"

echo.
echo [1/4] 检查 Python 环境...
%PY% --version
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

echo.
echo [2/4] 安装后端依赖...
cd backend
%PY% -m pip install -r requirements.txt
if errorlevel 1 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)
cd ..

echo.
echo [3/4] 启动后端服务...
start "后端服务" cmd /k "cd backend && %PY% -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 5 /nobreak > nul

echo.
echo [4/4] 启动前端服务...
start "前端服务" cmd /k "cd frontend && npm install && npm run dev"

echo.
echo ============================================
echo 启动完成！
echo 后端服务: http://127.0.0.1:8000
echo 前端服务: http://localhost:3000
echo API 文档: http://127.0.0.1:8000/docs
echo ============================================
pause
