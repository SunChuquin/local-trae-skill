# 项目提示词

## 项目概述

这是一个全栈的私有文档Skill系统，名为"MySkills"。系统允许用户上传和管理私有文档（支持MD、TXT、PDF、DOCX、Excel格式），通过向量检索技术构建知识库，并提供AI对话功能，使AI能够基于用户的私有文档回答问题。系统还包含智能体模板管理、调试面板等功能。

## 技术栈

### 后端
- **框架**: Python FastAPI
- **向量数据库**: ChromaDB
- **嵌入模型**: BAAI/bge-large-zh-v1.5（通过HuggingFaceEmbedding）
- **ORM**: SQLAlchemy + Alembic（数据库迁移）
- **数据库**: SQLite（默认，可通过配置更改）
- **文件解析**: 支持MD、TXT、PDF、DOCX、Excel（使用python-docx、pdfplumber、openpyxl等）
- **异步处理**: 使用FastAPI的异步支持
- **日志**: loguru
- **环境配置**: Pydantic Settings
- **CORS**: 支持跨域请求
- **API文档**: 自动生成OpenAPI文档（Swagger UI）

### 前端
- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **UI组件库**: shadcn/ui + Tailwind CSS
- **路由**: React Router DOM
- **HTTP客户端**: Axios
- **图标**: Lucide React
- **状态管理**: React Hooks（useState, useEffect）
- **代码质量**: ESLint + Prettier

### 基础设施
- **容器化**: Docker + Docker Compose
- **环境变量**: 使用.env文件管理配置
- **部署**: 支持单机Docker部署

## 目录结构

```
myskills/
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI应用入口
│   │   ├── config.py          # 配置管理（Pydantic Settings）
│   │   ├── database.py        # 数据库连接和会话管理
│   │   ├── models/            # SQLAlchemy数据模型
│   │   │   ├── __init__.py
│   │   │   ├── knowledge_base.py
│   │   │   ├── document.py
│   │   │   ├── vector.py
│   │   │   ├── excel_document.py
│   │   │   └── agent_template.py
│   │   ├── schemas/           # Pydantic模型（请求/响应）
│   │   ├── routers/           # API路由
│   │   │   ├── __init__.py
│   │   │   ├── knowledge_base.py
│   │   │   ├── document.py
│   │   │   ├── vector.py
│   │   │   ├── excel_document.py
│   │   │   ├── skill.py
│   │   │   ├── chat.py
│   │   │   ├── agent.py
│   │   │   ├── agent_template.py
│   │   │   └── system.py
│   │   ├── services/          # 业务逻辑服务
│   │   │   ├── __init__.py
│   │   │   ├── knowledge_base.py
│   │   │   ├── document.py
│   │   │   ├── vector.py
│   │   │   ├── excel_document.py
│   │   │   ├── skill.py
│   │   │   ├── chat.py
│   │   │   ├── agent.py
│   │   │   ├── embedding.py   # 嵌入模型服务
│   │   │   └── vector_utils.py # 向量工具函数
│   │   └── utils/             # 工具函数
│   │       ├── __init__.py
│   │       ├── file_parser.py # 文件解析工具
│   │       └── text_utils.py  # 文本处理工具
│   ├── alembic/               # 数据库迁移
│   │   ├── versions/
│   │   └── env.py
│   ├── requirements.txt       # Python依赖
│   ├── Dockerfile             # 后端Docker镜像
│   └── .env.example           # 环境变量示例
├── frontend/                  # 前端代码
│   ├── src/
│   │   ├── main.tsx          # 应用入口
│   │   ├── App.tsx           # 主应用组件
│   │   ├── index.css         # 全局样式
│   │   ├── lib/              # 工具库
│   │   │   └── utils.ts      # 工具函数
│   │   ├── components/       # 可复用组件
│   │   │   ├── ui/           # shadcn/ui组件
│   │   │   │   ├── button.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── input.tsx
│   │   │   │   └── ...
│   │   │   └── layout/       # 布局组件
│   │   ├── pages/            # 页面组件
│   │   │   ├── Dashboard.tsx
│   │   │   ├── KnowledgeBases.tsx
│   │   │   ├── Documents.tsx
│   │   │   ├── Chat.tsx
│   │   │   ├── ExcelDocuments.tsx
│   │   │   ├── VectorManagement.tsx
│   │   │   ├── SkillConfig.tsx
│   │   │   ├── DebugPanel.tsx
│   │   │   └── AgentTemplates.tsx
│   │   ├── services/         # API服务
│   │   │   ├── api.ts        # Axios实例
│   │   │   ├── knowledgeBase.ts
│   │   │   ├── document.ts
│   │   │   ├── vector.ts
│   │   │   ├── excelDoc.ts
│   │   │   ├── skill.ts
│   │   │   ├── chat.ts
│   │   │   ├── agent.ts
│   │   │   └── agentTemplate.ts
│   │   ├── types/            # TypeScript类型定义
│   │   │   ├── knowledge_base.ts
│   │   │   ├── document.ts
│   │   │   ├── excel_document.ts
│   │   │   ├── chat.ts
│   │   │   └── index.ts
│   │   └── hooks/            # 自定义Hooks
│   │       └── useChat.ts    # 聊天Hook
│   ├── public/               # 静态资源
│   ├── index.html            # HTML入口
│   ├── package.json          # 前端依赖
│   ├── tsconfig.json         # TypeScript配置
│   ├── vite.config.ts        # Vite配置
│   ├── tailwind.config.js    # Tailwind配置
│   ├── components.json       # shadcn/ui配置
│   └── Dockerfile            # 前端Docker镜像
├── docker-compose.yml        # Docker Compose配置
├── Dockerfile                # 整体Docker配置（如需要）
├── .env                      # 环境变量（实际文件，不应提交）
├── .env.example              # 环境变量示例
├── README.md                 # 项目说明
├── SETUP.md                  # 安装设置指南
├── PROJECT_SUMMARY.md        # 项目概要
├── PROJECT_RECONSTRUCTION_PROMPT.md # 本文件
└── .gitignore                # Git忽略文件
```

## 核心功能模块

### 1. 知识库管理
- 创建、编辑、删除知识库
- 知识库摘要生成（基于文档内容自动生成）
- 批量生成摘要
- 查看知识库统计信息（文档数量、向量数量）

### 2. 文档管理
- 支持上传多种格式文档：MD、TXT、PDF、DOCX
- 支持直接创建Markdown文档
- 文档分块处理（自动将文档分割为文本块）
- 查看文档详情和向量信息
- 删除文档

### 3. Excel文档管理
- 专门处理Excel文件（.xlsx, .xls）
- 支持两种分块模式：
  - 行级分块：每行作为一个独立块（适合结构化明细表）
  - 主题语义分块：基于语义相似度合并行（适合半结构化文档）
- 可配置语义阈值和是否包含表头上下文
- 分块预览功能

### 4. 向量管理
- 向量检索测试：输入查询测试检索效果
- 向量索引重建：重新生成知识库的向量索引
- 查看文档向量详情
- 向量相似度计算

### 5. AI对话
- 支持两种模式：
  - 通用模式：使用大模型的通用知识回答
  - 私有文档Skill模式：基于用户私有文档回答
- 流式响应：实时显示AI回复
- 知识库选择器：AI推荐相关知识库，用户确认选择
- LLM API配置：支持OpenAI兼容API
- 对话历史管理

### 6. Skill配置
- Function Calling配置：定义Skill的描述和参数
- 配置检索参数：top_k（返回结果数量）、相似度阈值
- 自动生成Function Calling JSON供大模型使用

### 7. 调试面板
- 在线测试Skill调用效果
- 查看检索结果和相似度分数
- 调用日志（开发中）

### 8. 智能体管理
- 查看系统内置智能体（选择器、助手、分析器）
- 管理智能体提示词模板
- 模板变量管理和版本控制

### 9. 系统健康监控
- 系统状态检查
- 向量数据库连接检查
- 嵌入模型状态检查

## API端点

### 知识库相关
- `GET /api/knowledge-bases` - 获取知识库列表
- `POST /api/knowledge-bases` - 创建知识库
- `GET /api/knowledge-bases/{kb_id}` - 获取知识库详情
- `PUT /api/knowledge-bases/{kb_id}` - 更新知识库
- `DELETE /api/knowledge-bases/{kb_id}` - 删除知识库
- `POST /api/knowledge-bases/{kb_id}/generate-summary` - 生成知识库摘要
- `GET /api/knowledge-bases/{kb_id}/summary` - 获取知识库摘要
- `POST /api/knowledge-bases/regenerate-all-summaries` - 批量重新生成摘要

### 文档相关
- `GET /api/knowledge-bases/{kb_id}/documents` - 获取文档列表
- `POST /api/knowledge-bases/{kb_id}/documents` - 创建文档（文本）
- `POST /api/knowledge-bases/{kb_id}/documents/upload` - 上传文档文件
- `GET /api/documents/{doc_id}` - 获取文档详情
- `DELETE /api/documents/{doc_id}` - 删除文档

### Excel文档相关
- `GET /api/knowledge-bases/{kb_id}/excel-documents` - 获取Excel文档列表
- `POST /api/knowledge-bases/{kb_id}/excel-documents/upload` - 上传Excel文档
- `POST /api/excel-documents/{doc_id}/chunk-and-store` - 分块并存储Excel文档
- `POST /api/excel-documents/chunk-preview` - 预览分块效果
- `DELETE /api/excel-documents/{doc_id}` - 删除Excel文档

### 向量相关
- `GET /api/knowledge-bases/{kb_id}/vectors` - 获取向量列表
- `POST /api/knowledge-bases/{kb_id}/vectors/rebuild` - 重建向量索引
- `GET /api/knowledge-bases/{kb_id}/documents/{doc_id}/vectors` - 获取文档向量详情
- `POST /api/vectors/retrieve` - 向量检索

### Skill相关
- `GET /api/skill/config` - 获取Skill配置
- `PUT /api/skill/config` - 更新Skill配置
- `GET /api/skill/metadata` - 获取Function Calling元数据
- `POST /api/skill/test` - 测试Skill调用

### 聊天相关
- `GET /api/chat/config` - 获取聊天配置
- `PUT /api/chat/config` - 更新聊天配置
- `POST /api/chat` - 发送聊天消息（非流式）
- `POST /api/chat/stream` - 流式聊天

### 智能体相关
- `POST /api/agent/select-knowledge-bases` - 选择知识库（智能体推荐）
- `GET /api/agent-templates` - 获取智能体模板列表
- `GET /api/agent-templates/{agent_id}` - 获取智能体模板详情

### 系统相关
- `GET /api/system/health` - 系统健康检查
- `GET /api/system/info` - 系统信息

## 数据库模型

### KnowledgeBase（知识库）
- `id`: UUID主键
- `name`: 名称
- `description`: 描述
- `document_count`: 文档数量
- `vector_count`: 向量数量
- `summary`: 知识库摘要
- `summary_updated_at`: 摘要更新时间
- `created_at`: 创建时间
- `updated_at`: 更新时间

### Document（文档）
- `id`: UUID主键
- `knowledge_base_id`: 外键，关联知识库
- `name`: 文档名称
- `document_type`: 文档类型（md、txt、pdf、docx）
- `file_path`: 文件存储路径
- `size`: 文件大小（字节）
- `content`: 文档内容（文本格式）
- `chunk_count`: 分块数量
- `vector_count`: 向量数量
- `created_at`: 创建时间
- `updated_at`: 更新时间

### ExcelDocument（Excel文档）
- `id`: UUID主键
- `knowledge_base_id`: 外键，关联知识库
- `name`: 文档名称
- `file_path`: 文件存储路径
- `size`: 文件大小（字节）
- `sheet_count`: Sheet数量
- `chunk_mode`: 分块模式（row_level, topic_semantic）
- `chunk_count`: 分块数量
- `vector_count`: 向量数量
- `created_at`: 创建时间
- `updated_at`: 更新时间

### Vector（向量）
- `id`: UUID主键
- `knowledge_base_id`: 外键，关联知识库
- `document_id`: 外键，关联文档
- `chunk_id`: 分块ID
- `content`: 文本内容
- `embedding`: 向量嵌入（JSON数组）
- `embedding_dimension`: 向量维度
- `metadata`: 元数据（JSON）
- `created_at`: 创建时间

### AgentTemplate（智能体模板）
- `id`: UUID主键
- `name`: 智能体名称
- `type`: 智能体类型（selector, assistant, analyzer）
- `description`: 描述
- `status`: 状态（active, inactive）
- `templates`: 模板列表（JSON数组）
- `created_at`: 创建时间
- `updated_at`: 更新时间

## 配置说明

### 后端配置（.env）
```env
# 应用配置
APP_NAME=MySkills Backend
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=true

# 数据库配置
DATABASE_URL=sqlite:///./app.db
# 或使用PostgreSQL: postgresql://user:password@localhost/myskills

# 向量数据库配置
CHROMA_HOST=chromadb
CHROMA_PORT=8000
CHROMA_COLLECTION=myskills_collection

# 嵌入模型配置
EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5
EMBEDDING_DEVICE=cpu  # 或 cuda

# 文件存储
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=104857600  # 100MB

# CORS配置
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# LLM配置（可选，用于聊天功能）
LLM_API_URL=https://api.openai.com/v1/chat/completions
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini
```

### 前端配置（环境变量）
```env
VITE_API_BASE_URL=/api
VITE_APP_NAME=MySkills
VITE_APP_VERSION=1.0.0
```

## 依赖列表

### 后端依赖（requirements.txt）
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
chromadb==0.4.22
sentence-transformers==2.2.2
llama-index-embeddings-huggingface==0.1.2
llama-index==0.10.0
loguru==0.7.2
python-docx==1.1.0
pdfplumber==0.10.3
openpyxl==3.1.2
pandas==2.1.4
numpy==1.24.3
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
httpx==0.25.2
aiofiles==23.2.1
```

### 前端依赖（package.json）
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.1",
    "axios": "^1.6.2",
    "lucide-react": "^0.309.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0",
    "tailwindcss-animate": "^1.0.7"
  },
  "devDependencies": {
    "@types/react": "^18.2.45",
    "@types/react-dom": "^18.2.18",
    "@typescript-eslint/eslint-plugin": "^6.14.0",
    "@typescript-eslint/parser": "^6.14.0",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.16",
    "eslint": "^8.55.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.5",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.3.6",
    "typescript": "^5.2.2",
    "vite": "^5.0.8"
  }
}
```

## 启动和运行

### 开发环境

#### 后端启动
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端启动
```bash
cd frontend
npm install
npm run dev
```

### Docker Compose启动
```bash
# 复制环境变量文件
cp .env.example .env
# 编辑.env文件，配置必要的参数

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### Docker Compose配置（docker-compose.yml）
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./app.db
      - CHROMA_HOST=chromadb
      - CHROMA_PORT=8000
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/app.db:/app/app.db
    depends_on:
      - chromadb
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000/api
    depends_on:
      - backend
    restart: unless-stopped

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/chroma
    restart: unless-stopped

volumes:
  chroma_data:
```

## 关键代码片段

### 后端FastAPI应用入口（app/main.py）
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import (
    knowledge_base, document, vector, excel_document,
    skill, chat, agent, agent_template, system
)
from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(knowledge_base.router, prefix="/api/knowledge-bases", tags=["knowledge-bases"])
app.include_router(document.router, prefix="/api/documents", tags=["documents"])
app.include_router(vector.router, prefix="/api/vectors", tags=["vectors"])
app.include_router(excel_document.router, prefix="/api/excel-documents", tags=["excel-documents"])
app.include_router(skill.router, prefix="/api/skill", tags=["skill"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])
app.include_router(agent_template.router, prefix="/api/agent-templates", tags=["agent-templates"])
app.include_router(system.router, prefix="/api/system", tags=["system"])

@app.get("/")
async def root():
    return {"message": "MySkills API", "version": settings.APP_VERSION}

@app.get("/api/health")
async def health():
    return {"status": "healthy"}
```

### 前端API服务示例（src/services/api.ts）
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json; charset=utf-8',
  },
});

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export default api;
```

### 嵌入模型服务（app/services/embedding.py）
```python
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

from typing import List, Optional
import numpy as np
from loguru import logger
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from app.config import settings
from app.services.vector_utils import vector_utils

class EmbeddingService:
    def __init__(self):
        self.model: Optional[HuggingFaceEmbedding] = None
        self._initialize_model()
    
    def _initialize_model(self):
        try:
            logger.info(f"正在加载嵌入模型: {settings.embedding_model}")
            self.model = HuggingFaceEmbedding(
                model_name=settings.embedding_model,
                device=settings.embedding_device,
            )
            logger.info("嵌入模型加载成功")
        except Exception as e:
            logger.error(f"嵌入模型加载失败: {str(e)}")
            raise
    
    def get_embedding(self, text: str, text_type: str = "chunk") -> List[float]:
        if not self.model:
            raise RuntimeError("嵌入模型未初始化")
        
        try:
            processed_text = vector_utils.preprocess_for_chunk(text)
            embedding = self.model.get_text_embedding(processed_text)
            return self._normalize(embedding)
        except Exception as e:
            logger.error(f"生成嵌入向量失败: {str(e)}")
            raise
    
    @staticmethod
    def _normalize(vector: List[float]) -> List[float]:
        arr = np.array(vector, dtype=np.float32)
        norm = np.linalg.norm(arr)
        if norm > 0:
            arr = arr / norm
        return arr.tolist()

embedding_service = EmbeddingService()
```

### 前端主应用组件（src/App.tsx）
```typescript
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Button } from './components/ui/button';
import { BookOpen, FileText, Database, Settings, Bug, BarChart3, MessageSquare, File, Brain } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import KnowledgeBases from './pages/KnowledgeBases';
import Documents from './pages/Documents';
import Chat from './pages/Chat';
import ExcelDocuments from './pages/ExcelDocuments';
import VectorManagement from './pages/VectorManagement';
import SkillConfig from './pages/SkillConfig';
import DebugPanel from './pages/DebugPanel';
import AgentTemplates from './pages/AgentTemplates';

function App() {
  const location = useLocation();
  
  return (
    <div className="min-h-screen bg-background">
      <div className="flex">
        <aside className="w-64 border-r bg-card h-screen fixed left-0 top-0">
          <div className="p-6 border-b">
            <h2 className="text-xl font-bold">📚 私有文档 Skill</h2>
          </div>
          <nav className="p-4 space-y-2">
            <Link to="/">
              <Button variant={location.pathname === '/' ? 'secondary' : 'ghost'} className="w-full justify-start">
                <BarChart3 className="mr-2 h-4 w-4" />仪表盘
              </Button>
            </Link>
            {/* 其他导航链接 */}
          </nav>
        </aside>
        
        <main className="flex-1 ml-64 p-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/knowledge-bases" element={<KnowledgeBases />} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/excel-documents" element={<ExcelDocuments />} />
            <Route path="/vector" element={<VectorManagement />} />
            <Route path="/skill" element={<SkillConfig />} />
            <Route path="/debug" element={<DebugPanel />} />
            <Route path="/agent-templates" element={<AgentTemplates />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;
```

## 部署说明

### 生产环境部署建议
1. **数据库**: 将SQLite替换为PostgreSQL或MySQL以提高并发性能
2. **向量数据库**: ChromaDB可配置持久化存储
3. **文件存储**: 考虑使用云存储（如AWS S3、阿里云OSS）替代本地存储
4. **缓存**: 添加Redis缓存层提高检索性能
5. **负载均衡**: 使用Nginx作为反向代理和负载均衡器
6. **监控**: 集成Prometheus和Grafana进行系统监控
7. **日志**: 使用ELK栈（Elasticsearch, Logstash, Kibana）集中日志管理
8. **安全**: 配置HTTPS、API密钥认证、请求限流

### 扩展性考虑
1. **微服务架构**: 可将文档解析、向量生成、检索服务拆分为独立微服务
2. **异步任务**: 使用Celery或RQ处理耗时的文档解析和向量生成任务
3. **分布式向量数据库**: 考虑使用Weaviate或Qdrant替代ChromaDB以支持分布式部署
4. **多租户**: 添加多租户支持，使多个团队或用户共享系统

## 测试和验证

### 单元测试
```bash
# 后端测试
cd backend
pytest tests/ -v

# 前端测试
cd frontend
npm test
```

### API测试
```bash
# 使用curl测试API
curl -X GET http://localhost:8000/api/health
curl -X GET http://localhost:8000/api/knowledge-bases
```

### 集成测试
1. 上传测试文档
2. 创建知识库并关联文档
3. 测试向量检索
4. 测试AI对话功能
5. 验证Excel文档处理

## 故障排除

### 常见问题
1. **嵌入模型下载失败**: 检查网络连接，配置HF_ENDPOINT镜像
2. **向量检索效果差**: 调整分块大小、重叠参数，或更换嵌入模型
3. **内存不足**: 减少批量处理大小，使用GPU加速
4. **文件上传失败**: 检查文件大小限制和文件格式支持
5. **数据库连接失败**: 检查数据库URL配置和网络连接

### 日志查看
```bash
# 查看后端日志
docker-compose logs backend

# 查看前端日志
docker-compose logs frontend

# 查看向量数据库日志
docker-compose logs chromadb
```

## 后续开发建议

### 功能增强
1. **多语言支持**: 添加英文界面和文档处理
2. **文档版本控制**: 支持文档版本管理和回滚
3. **协作功能**: 添加团队协作和权限管理
4. **API密钥管理**: 为外部集成提供API密钥管理
5. **插件系统**: 支持自定义文档解析器和向量模型插件

### 性能优化
1. **向量索引优化**: 使用HNSW或IVF索引提高检索速度
2. **缓存策略**: 实现查询结果缓存和热点数据缓存
3. **批量处理优化**: 优化文档批量上传和处理流程
4. **前端性能**: 代码分割、懒加载、图片优化

### 用户体验改进
1. **移动端适配**: 优化移动端界面
2. **快捷键支持**: 添加键盘快捷键提高操作效率
3. **主题切换**: 支持深色/浅色主题
4. **教程和引导**: 添加新用户引导和操作教程

---

## 使用此提示词重建项目的指导

1. **环境准备**: 确保具备Python 3.9+、Node.js 18+、Docker环境
2. **项目初始化**: 按照目录结构创建项目骨架
3. **依赖安装**: 安装前后端依赖包
4. **配置设置**: 复制环境变量文件并配置必要参数
5. **数据库初始化**: 运行数据库迁移创建表结构
6. **服务启动**: 启动后端、前端和向量数据库服务
7. **功能验证**: 按照测试和验证步骤检查各功能模块
8. **部署上线**: 根据部署说明配置生产环境
