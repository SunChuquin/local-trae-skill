#!/bin/bash

echo "============================================"
echo "个人私有文档 Skill 系统 - 前端启动脚本"
echo "============================================"
echo ""

cd "$(dirname "$0")/frontend"

echo "[1/3] 检查 Node.js 环境..."
node --version
if [ $? -ne 0 ]; then
    echo "[错误] 未找到 Node.js，请先安装 Node.js 18+"
    exit 1
fi

echo ""
echo "[2/3] 检查依赖是否安装..."
if [ ! -d "node_modules" ]; then
    echo "[提示] 依赖未安装，开始安装..."
    npm install
    if [ $? -ne 0 ]; then
        echo "[错误] 依赖安装失败"
        exit 1
    fi
fi

echo ""
echo "[3/3] 启动前端服务..."
echo ""
echo "前端地址: http://localhost:3000"
echo "后端代理: http://localhost:3000/api -> http://127.0.0.1:8000"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

npm run dev
