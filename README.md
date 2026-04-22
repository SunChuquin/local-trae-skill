# 个人私有文档 Skill 系统

100% 本地运行的个人私有文档检索系统，为大模型提供专属 Skill 接口。

## 🎯 功能特性

- **本地向量数据库**：使用 Chroma 本地持久化存储
- **本地嵌入模型**：BAAI/bge-large-zh-v1.5，离线可用
- **多格式支持**：Markdown、TXT、PDF、DOCX 文档解析
- **智能分块**：语义切片，自动分块处理
- **标准接口**：OpenAI Function Calling 接口
- **可视化管琌**：浏览器端管理知识库和文档
- **隐私安全**：所有数据仅保存在本地，不上云

## 📋 系统要求

- Python 3.10+
- Node.js 18+
- 8GB+ RAM
- 10GB+ 可用磁盘空间

## 🚀 快速开始

### Windows 系统

1. 双击运行 `start.bat`
2. 等待服务启动完成
3. 访问 http://localhost:3000

### Mac/Linux 系统

```bash
chmod +x start.sh
./start.sh
```

### 手动启动

**后端服务：**

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**前端服务：**

```bash
cd frontend
npm install
npm run dev
```

## 📁 项目结构

```
myskills/
├── backend/                    # Python FastAPI 后端
│   ├── app/
│   │   ├── models/            # 数据模型
│   │   ├── routers/           # API 路由
│   │   ├── services/         # 业务逻辑
│   │   ├── utils/            # 工具类
│   │   ├── config.py         # 配置管理
│   │   └── main.py           # 应用入口
│   ├── data/                  # 数据存储
│   │   ├── chroma/           # 向量数据库
│   │   └── backup/          # 备份文件
│   └── requirements.txt      # Python 依赖
│
├── frontend/                   # React + TypeScript 前端
│   ├── src/
│   │   ├── components/       # React 组件
│   │   ├── pages/           # 页面
│   │   ├── services/        # API 服务
│   │   └── types/           # 类型定义
│   ├── package.json
│   └── vite.config.ts
│
├── .env                       # 环境变量配置
├── start.bat                  # Windows 启动脚本
├── start.sh                  # Mac/Linux 启动脚本
└── README.md
```

## 🔌 API 接口

### 知识库管理

- `GET /api/knowledge-bases` - 获取知识库列表
- `POST /api/knowledge-bases` - 创建知识库
- `GET /api/knowledge-bases/{id}` - 获取知识库详情
- `PUT /api/knowledge-bases/{id}` - 更新知识库
- `DELETE /api/knowledge-bases/{id}` - 删除知识库

### 文档管理

- `GET /api/documents/knowledge-base/{kb_id}` - 获取文档列表
- `POST /api/documents` - 创建文档
- `POST /api/documents/upload` - 上传文档
- `GET /api/documents/{id}` - 获取文档详情
- `PUT /api/documents/{id}` - 更新文档
- `DELETE /api/documents/{id}` - 删除文档

### 向量管理

- `POST /api/vectors/rebuild/{kb_id}` - 重建向量索引
- `POST /api/vectors/retrieve` - 检索向量
- `POST /api/vectors/backup/{kb_id}` - 创建备份
- `GET /api/vectors/backups` - 获取备份列表

### Skill 接口

- `GET /api/skill/metadata` - 获取 Skill 元数据
- `POST /api/skill/retrieve` - 检索文档
- `GET /api/skill/config` - 获取 Skill 配置
- `PUT /api/skill/config` - 更新 Skill 配置

### 系统

- `GET /api/system/health` - 系统健康检查
- `GET /api/system/info` - 系统信息

## 🛠️ 配置说明

编辑 `.env` 文件修改配置：

```env
HOST=127.0.0.1
PORT=8000
DEBUG=true

CHROMA_PERSIST_DIRECTORY=./data/chroma
EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5

CHUNK_SIZE=500
CHUNK_OVERLAP=50

DEFAULT_TOP_K=5
DEFAULT_SIMILARITY_THRESHOLD=0.5
```

## 🐳 Docker 部署

```bash
docker-compose up -d
```

## 📖 使用流程

1. **创建知识库**：在浏览器中创建知识库
2. **上传文档**：上传 MD/TXT/PDF/DOCX 文档
3. **自动向量化**：系统自动进行分块和向量化
4. **配置 Skill**：设置 Skill 描述和检索参数
5. **接入大模型**：通过 Function Calling 接口调用

## 🔧 技术栈

**后端：**
- Python 3.10+
- FastAPI
- Chroma (向量数据库)
- LlamaIndex (RAG 框架)
- BAAI/bge-large-zh-v1.5 (嵌入模型)

**前端：**
- React 18
- TypeScript
- Vite
- TailwindCSS
- shadcn/ui

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
