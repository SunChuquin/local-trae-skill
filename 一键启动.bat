@echo off
chcp 65001 > nul
echo ============================================
echo 个人私有文档 Skill 系统 - 一键启动
echo ============================================
echo.

echo [步骤 1/4] 启动后端服务...
echo 提示：请保持此窗口打开，后端服务将在新窗口中运行
start "后端服务 - 个人私有文档 Skill" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo.
echo [步骤 2/4] 等待后端启动 (5秒)...
timeout /t 5 /nobreak > nul

echo.
echo [步骤 3/4] 启动前端服务...
start "前端服务 - 个人私有文档 Skill" cmd /k "cd /d %~dp0frontend && npm install && npm run dev"

echo.
echo [步骤 4/4] 启动完成！
echo.

echo ============================================
echo 服务地址：
echo   - 前端界面: http://localhost:3000
echo   - 后端服务: http://127.0.0.1:8000
echo   - API 文档: http://127.0.0.1:8000/docs
echo ============================================
echo.
echo 提示：
echo   - 首次运行需要下载 BGE 嵌入模型（约 1.2GB）
echo   - 请确保网络连接正常
echo   - 关闭时请关闭两个服务窗口
echo.
pause
