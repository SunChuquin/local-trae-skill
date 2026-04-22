# 环境配置说明

## 后端环境配置

### 1. 安装 Python 依赖

推荐使用清华镜像源安装依赖：

```bash
cd backend
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

或者使用阿里云镜像：

```bash
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 2. 下载 BGE 嵌入模型

首次运行后端服务时，系统会自动下载 BAAI/bge-large-zh-v1.5 模型。

模型大小约 1.2GB，请确保网络连接稳定。

### 3. 配置环境变量

编辑项目根目录的 `.env` 文件：

```env
HOST=127.0.0.1
PORT=8000
DEBUG=true

CHROMA_PERSIST_DIRECTORY=./data/chroma
EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5
EMBEDDING_DEVICE=cpu
EMBEDDING_BATCH_SIZE=32

CHUNK_SIZE=500
CHUNK_OVERLAP=50

DEFAULT_TOP_K=5
DEFAULT_SIMILARITY_THRESHOLD=0.5

BACKUP_DIRECTORY=./data/backup
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

### 4. 启动后端服务

```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

服务启动后，访问 http://127.0.0.1:8000/docs 查看 API 文档。

## 前端环境配置

### 1. 安装 Node.js 依赖

```bash
cd frontend
npm install
```

### 2. 启动前端服务

```bash
npm run dev
```

前端服务启动后，访问 http://localhost:3000

## 一键启动

### Windows

双击运行 `start.bat`

### Mac/Linux

```bash
chmod +x start.sh
./start.sh
```

## 常见问题

### 1. 依赖安装失败

- 检查网络连接
- 尝试使用国内镜像源
- 确保 Python 版本 >= 3.10

### 2. 模型下载失败

- 检查网络连接
- 可以手动下载模型到本地目录
- 或者使用其他嵌入模型

### 3. 端口被占用

修改 `.env` 文件中的 `PORT` 配置

### 4. 内存不足

- 减小 `EMBEDDING_BATCH_SIZE`
- 减小 `CHUNK_SIZE`
- 或者使用 GPU 加速（需要 CUDA）

## 验证安装

启动后端服务后，访问以下接口验证：

```bash
# 健康检查
curl http://127.0.0.1:8000/api/system/health

# 获取 Skill 元数据
curl http://127.0.0.1:8000/api/skill/metadata
```

如果返回 JSON 数据，说明安装成功。
