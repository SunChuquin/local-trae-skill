#!/bin/bash

echo "============================================"
echo "个人私有文档 Skill 系统 - 一键启动"
echo "============================================"
echo ""

echo "[步骤 1/4] 启动后端服务..."
cd "$(dirname "$0")/backend"
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

echo "后端服务 PID: $BACKEND_PID"
echo "[步骤 2/4] 等待后端启动 (5秒)..."
sleep 5

echo ""
echo "[步骤 3/4] 启动前端服务..."
cd "$(dirname "$0")/frontend"
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi
npm run dev &
FRONTEND_PID=$!

echo "前端服务 PID: $FRONTEND_PID"
echo "[步骤 4/4] 启动完成！"
echo ""

echo "============================================"
echo "服务地址："
echo "  - 前端界面: http://localhost:3000"
echo "  - 后端服务: http://127.0.0.1:8000"
echo "  - API 文档: http://127.0.0.1:8000/docs"
echo "============================================"
echo ""
echo "提示："
echo "  - 首次运行需要下载 BGE 嵌入模型（约 1.2GB）"
echo "  - 请确保网络连接正常"
echo "  - 关闭时请按 Ctrl+C"
echo ""

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
