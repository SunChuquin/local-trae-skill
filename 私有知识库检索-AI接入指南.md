# 本地私有知识库检索 — AI 会话接入指南

> 本文档供**任意 AI 会话（TRAE / Claude / ChatGPT / 其他）**阅读后，学会如何从我本地的文档向量化服务中检索文档内容，并基于检索到的内容回答用户问题。
>
> 面向对象：AI 模型（你）。如果你是人类读者，请直接看「快速上手」。

---

## 一、这是什么

在本地运行着一个**个人私有知识库检索服务**（FastAPI + Chroma + BGE 嵌入模型，100% 本地、数据不出机器）。用户可以事先把 PDF / MD / TXT / DOCX 文档上传进去，系统自动完成：

```
文档 → 解析 → 切块(chunk) → 向量化(bge-base-zh-v1.5, 768维) → 存入 Chroma 向量库
```

之后，**AI 会话可以通过一个 HTTP 接口，把用户的提问向量化、在向量库中检索最相关的文档片段**，再基于这些片段（而不是通用知识）来回答。

**核心价值**：让 AI 的回答基于用户私有文档的原文，可溯源、可核对。

---

## 二、服务地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 后端 API | `http://127.0.0.1:8000` | 检索服务本体 |
| 前端管理界面 | `http://localhost:3000` | 浏览器里管理知识库/上传文档（人用） |
| 后端健康检查 | `http://127.0.0.1:8000/api/system/health` | 返回 `{"status":"healthy"}` 即正常 |

> **前置条件（AI 自行负责）**：后端服务必须在运行。**若调不通，由 AI 会话自己启动后端服务**，不要推给用户（启动命令见「二·补充：AI 自行启动后端」）。

### 二·补充：AI 自行启动后端（不依赖用户）

当调用检索接口失败 / 连接被拒时，AI 会话按以下顺序自查并自启动，全程不打扰用户：

**第 1 步：确认端口是否已被占用**

```powershell
# 查看 8000 端口是否已有进程监听
netstat -ano | findstr ":8000" | findstr LISTENING
```

- 若**有输出**（有 PID 在监听）→ 服务可能仍在启动/加载模型中，等 10~30 秒后重试健康检查。
- 若**无输出** → 进入第 2 步启动。

**第 2 步：启动后端服务（后台运行）**

```powershell
cd c:\Users\sunck\home\projects\doc\local-trae-skill\backend
c:\Users\sunck\home\projects\doc\local-trae-skill\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

> 说明：项目依赖装在根目录 `.venv`，所以用绝对路径的 venv Python。若该路径不存在，回退到 `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`。
> 首次启动会加载 bge-base-zh-v1.5 模型，可能需要 10~60 秒，属正常现象。

**第 3 步：等待并验证健康**

```powershell
# 轮询健康检查，直到返回 healthy
(Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/system/health" -Method Get)
```

看到 `"status": "healthy"`（或 code 200）即启动成功，之后即可正常调用检索接口。

**原则**：把「启动服务」视为 AI 自己的工作职责，只有真的无法自行启动（如缺依赖、端口冲突且无法解决）时才向用户说明情况。

---

## 三、检索接口（AI 会话最常用的核心接口）

### 接口定义

```
GET http://127.0.0.1:8000/api/vectors/retrieve
```

| 参数 | 必填 | 说明 |
|------|------|------|
| `query` | **是** | 用户的问题（原话即可，无需改写） |
| `knowledge_base_name` | 否 | 指定只检索某个知识库；**留空则检索全部知识库** |
| `top_k` | 否 | 返回结果数，默认 5 |
| `content_length` | 否 | 每条结果的 `content` 最大字符数，默认 500。**传 `0` 表示不截断** |

### 返回结构

```json
{
  "code": 200,
  "message": "检索成功",
  "data": [
    {
      "document_name": "ISO_IEC 7816-3-2006.pdf",
      "document_id": "040227f7-...",
      "content": "检索到的原文片段……",
      "similarity": 0.776,
      "metadata": { "chunk_index": 156, "total_chunks": 343 }
    }
  ],
  "total": 3
}
```

关键字段：
- `content`：命中的**文档原文片段**（回答的依据）
- `document_name`：来源文档名（回答时必须标注）
- `similarity`：相似度 0~1，越高越相关（低于 0.5 会被阈值过滤掉）
- `metadata.chunk_index`：该片段在文档中的块编号（可用于定位原文）

### 调用示例（curl）

```bash
# 全库检索，不截断原文
curl -s -G "http://127.0.0.1:8000/api/vectors/retrieve" \
  --data-urlencode "query=ATR Answer to Reset 是什么" \
  --data-urlencode "top_k=5" \
  --data-urlencode "content_length=0"

# 指定知识库检索
curl -s -G "http://127.0.0.1:8000/api/vectors/retrieve" \
  --data-urlencode "query=PPS 什么情况下会被停用" \
  --data-urlencode "knowledge_base_name=ISO7816标准库" \
  --data-urlencode "top_k=5" \
  --data-urlencode "content_length=0"
```

> **Windows PowerShell 注意**：不要直接用 `Invoke-RestMethod -Body` 传中文，容易乱码。推荐用 `curl.exe`（Windows 自带）+ `--data-urlencode`，可正确编码中文。

---

## 四、AI 会话的使用规范（重要）

当用户的问题**涉及本地私有文档内容**时，请按以下流程执行：

1. **判断是否需要检索**：若用户问的是私有文档里的内容（标准、规范、项目文档、业务规则等），调用检索接口；通用知识问答不要调用。
2. **调用接口**：`GET /api/vectors/retrieve`，`query` 用用户的原话。
3. **基于原文回答**：只基于 `content` 字段的内容回答，**不要编造**。
4. **标注来源**：回答末尾用如下格式标注每个来源：
   ```
   根据《ISO_IEC 7816-3-2006.pdf》（相似度 77.6%）：
   [原文片段内容]
   ```
5. **无结果处理**：若 `data` 为空（`total: 0`），如实告诉用户「知识库中没有找到相关内容」，**不要用通用知识硬答**。
6. **相似度阈值**：系统已内置 0.5 阈值过滤，返回的都是过阈值的片段。

### 可选：先查有哪些知识库

```
GET http://127.0.0.1:8000/api/knowledge-bases
```

返回 `data` 数组，每个元素含 `id`、`name`。当前已有知识库（示例）：

| name | 内容 |
|------|------|
| `ISO7816标准库` | ISO/IEC 7816-3-2006 智能卡标准（343 块） |

---

## 五、当前知识库与文档状态

（此表为文档创建时快照，实际以 `GET /api/knowledge-bases` 返回为准）

- 知识库：`ISO7816标准库`（ID 以接口返回为准）
- 文档：`ISO_IEC 7816-3-2006.pdf`，343 个向量块

---

## 六、其他可用接口（管理用，AI 一般不需要）

| 用途 | 接口 |
|------|------|
| 知识库列表 | `GET /api/knowledge-bases` |
| 创建知识库 | `POST /api/knowledge-bases` |
| 上传文档 | `POST /api/documents/upload`（multipart：`knowledge_base_id` + `file`） |
| 上传进度 | `GET /api/documents/upload-progress/{task_id}` |
| 文档列表 | `GET /api/documents/knowledge-base/{kb_id}` |
| Skill 元数据（Function Calling 定义） | `GET /api/skill/metadata` |
| Skill 检索（POST 版，供 Function Calling 用） | `POST /api/skill/retrieve` |
| 系统健康 | `GET /api/system/health` |

---

## 七、技术背景（可选了解）

- **嵌入模型**：`bge-base-zh-v1.5`（本地，768 维），配置在 `backend/.env` 的 `EMBEDDING_MODEL`
- **向量库**：Chroma，持久化在 `backend/data/chroma`
- **分块**：`CHUNK_SIZE=500`、`CHUNK_OVERLAP=50`，含父子块增强
- **检索流程**：提问 → 向量化 → 余弦相似度计算 → 阈值(0.5)过滤 → 取 top-k
- **为什么能溯源**：回答时把 `content` 原文逐字引用 + 标注 `document_name` + `similarity`，用户即可打开 PDF 核对

---

## 八、启动服务（人类用户手动方式，AI 会话请看「二·补充」）

人类用户可以双击 `start.bat` 一键启动前后端；或分两个终端手动启动：

```bash
# 后端（在 backend 目录下）
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
# 或直接 .\启动后端.bat

# 前端（在 frontend 目录下）
npm run dev
```

> **AI 会话注意**：后端未运行时应由 AI 自行启动，不要依赖人类用户手动执行——具体步骤见「二·补充：AI 自行启动后端」。

验证：浏览器访问 `http://127.0.0.1:8000/api/system/health`，返回 `healthy` 即成功。

---

## 九、常见问题

| 现象 | 原因 / 解决 |
|------|------|
| 检索返回 `total: 0` | ①问题不在知识库范围内；②知识库为空或文档未向量化完成；③中文经旧工具乱码（用 `curl.exe --data-urlencode`） |
| 后端连不上 | 后端没启动 → **AI 自行启动**（见「二·补充」，不要推给用户） |
| 上传大 PDF 很慢 | 异步处理中，轮询 `upload-progress` 接口看进度 |
| 需要换模型 | 改 `.env` 的 `EMBEDDING_MODEL`，但换模型需重建向量库并重新上传文档（维度不兼容） |

---

*文档路径：`c:\Users\sunck\home\projects\doc\local-trae-skill\私有知识库检索-AI接入指南.md`*
