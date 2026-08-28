@echo off
chcp 65001 > nul
echo ============================================
echo 个人私有文档 Skill 系统 - 后端启动脚本
echo ============================================
echo.

cd /d "%~dp0backend"

rem 优先使用 .venv310（Python 3.10 环境），否则回退全局 python
set "PY=python"
if exist "%~dp0.venv310\Scripts\python.exe" set "PY=%~dp0.venv310\Scripts\python.exe"

echo [1/3] 检查 Python 环境...
%PY% --version
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

echo.
echo [2/3] 检查依赖是否安装...
%PY% -c "import fastapi, chromadb" > nul 2>&1
if errorlevel 1 (
    echo [提示] 依赖未安装，开始安装...
    %PY% -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)

echo.
echo [3/3] 启动后端服务...
echo.
echo 服务地址: http://127.0.0.1:8000
echo API 文档: http://127.0.0.1:8000/docs
echo.
echo 按 Ctrl+C 停止服务
echo.

%PY% -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
