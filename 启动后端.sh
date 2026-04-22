#!/bin/bash

echo "============================================"
echo "个人私有文档 Skill 系统 - 后端启动脚本"
echo "============================================"
echo ""

cd "$(dirname "$0")/backend"

echo "[1/3] 检查 Python 环境..."
python3 --version
if [ $? -ne 0 ]; then
    echo "[错误] 未找到 Python，请先安装 Python 3.10+"
    exit 1
fi

echo ""
echo "[2/3] 检查依赖是否安装..."
if ! pip3 show fastapi > /dev/null 2>&1; then
    echo "[提示] 依赖未安装，开始安装..."
    pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    if [ $? -ne 0 ]; then
        echo "[错误] 依赖安装失败"
        exit 1
    fi
fi

echo ""
echo "[3/3] 启动后端服务..."
echo ""
echo "服务地址: http://127.0.0.1:8000"
echo "API 文档: http://127.0.0.1:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
