# 快速启动指南

## 环境要求
- Python 3.10+
- Node.js 18+
- 网络连接（用于下载模型）

## 第一步：安装后端依赖

```bash
cd backend
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

如果遇到网络问题，可以使用 ModelScope：

```bash
pip install -r requirements.txt -i https://modelscope.cn/simple
```

## 第二步：下载 BGE 嵌入模型

首次启动后端服务时，系统会自动从 huggingface.co 下载模型。

如果网络不通，可以：
1. 配置 VPN/代理
2. 手动下载模型
3. 使用 ModelScope 镜像

## 第三步：启动后端服务

```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

等待看到以下信息表示启动成功：
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

## 第四步：启动前端服务

新开一个终端：

```bash
cd frontend
npm install
npm run dev
```

## 第五步：访问应用

- 前端界面：http://localhost:3000
- API 文档：http://127.0.0.1:8000/docs

## 一键启动（Windows）

双击运行 `start.bat`

## 一键启动（Mac/Linux）

```bash
chmod +x start.sh
./start.sh
```

## 验证安装

在浏览器中访问 http://127.0.0.1:8000/api/system/health

应该返回：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    ...
  }
}
```

## 常见问题

### 1. 模型下载失败
**问题**：无法连接到 huggingface.co
**解决**：
- 配置网络代理
- 使用国内镜像
- 手动下载模型到本地

### 2. 端口被占用
**问题**：8000 或 3000 端口被占用
**解决**：
- 修改 `.env` 文件中的端口配置
- 或关闭占用端口的程序

### 3. 依赖安装失败
**问题**：pip 安装依赖报错
**解决**：
- 使用国内镜像源
- 检查 Python 版本
- 更新 pip：`python -m pip install --upgrade pip`

### 4. 前端无法连接后端
**问题**：浏览器无法访问 API
**解决**：
- 检查后端服务是否启动
- 检查 CORS 配置
- 检查防火墙设置

## 快速测试

### 创建知识库
```bash
curl -X POST http://127.0.0.1:8000/api/knowledge-bases \
  -H "Content-Type: application/json" \
  -d '{"name": "测试知识库", "description": "这是一个测试知识库"}'
```

### 获取 Skill 元数据
```bash
curl http://127.0.0.1:8000/api/skill/metadata
```

### 系统健康检查
```bash
curl http://127.0.0.1:8000/api/system/health
```

## 下一步

1. 在前端界面创建知识库
2. 上传文档（MD/TXT/PDF/DOCX）
3. 配置 Skill 参数
4. 通过 Function Calling 接口调用

详细文档请参考：
- `README.md` - 项目说明
- `SETUP.md` - 环境配置说明
- `PROJECT_SUMMARY.md` - 开发总结
