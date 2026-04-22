# PowerShell 下载脚本使用说明

## 📥 新增下载脚本

已创建 `下载模型.ps1` PowerShell 脚本文件

## 🚀 使用方法

### 方法一：直接运行（推荐）

1. 右键点击 `下载模型.ps1`
2. 选择 **"使用 PowerShell 运行"**
3. 等待下载完成

### 方法二：通过 PowerShell 终端运行

1. 右键点击 `下载模型.ps1`
2. 选择 **"在终端中打开"**
3. 如果提示执行策略错误，运行：
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser
   ```
4. 然后再次运行脚本

### 方法三：通过命令提示符运行

```cmd
powershell -ExecutionPolicy Bypass -File "C:\Users\hp\Documents\trae_projects\myskills\下载模型.ps1"
```

## 📋 下载内容

脚本会自动下载以下文件到 `models\bge-large-zh-v1.5\` 目录：

- [ ] config.json
- [ ] config_sentence_transformers.json
- [ ] model.safetensors（约 1.2GB，耗时最长）
- [ ] tokenizer.json
- [ ] tokenizer_config.json
- [ ] special_tokens_map.json
- [ ] vocab.txt
- [ ] modeling.py

## ⏱️ 预计时间

- 小文件（约 2MB）：几秒钟
- model.safetensors（约 1.2GB）：取决于网速，通常 5-30 分钟

## ✅ 验证下载

下载完成后，检查文件：

```powershell
Get-ChildItem "C:\Users\hp\Documents\trae_projects\myskills\models\bge-large-zh-v1.5"
```

应该显示 8 个文件。

## ⚠️ 如果下载失败

### 检查网络
```powershell
Test-NetConnection -ComputerName hf-mirror.com -Port 443
```

### 使用代理
如果需要代理，在脚本开头添加：
```powershell
$proxy = "http://127.0.0.1:你的代理端口"
[System.Net.WebRequest]::DefaultWebProxy = New-Object System.Net.WebProxy($proxy)
```

### 单独下载失败的文件
可以单独重试失败的下载：
```powershell
Invoke-WebRequest -Uri "https://hf-mirror.com/BAAI/bge-large-zh-v1.5/resolve/main/文件名" -OutFile "目标路径"
```

## 📝 下一步

1. 确认所有文件下载完成
2. 修改 `.env` 配置：
   ```env
   EMBEDDING_MODEL=./models/bge-large-zh-v1.5
   ```
3. 重启后端服务
4. 访问 http://localhost:3000

## 🔧 常见问题

### Q: 提示"无法加载文件"
**A:** 运行：
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser
```

### Q: 下载很慢
**A:** 
- 检查网络连接
- 尝试使用代理
- 或使用手机热点

### Q: model.safetensors 下载失败
**A:** 这个文件最大，可以单独重试：
```powershell
Invoke-WebRequest -Uri "https://hf-mirror.com/BAAI/bge-large-zh-v1.5/resolve/main/model.safetensors" -OutFile "C:\Users\hp\Documents\trae_projects\myskills\models\bge-large-zh-v1.5\model.safetensors"
```

---

**提示**：如果 PowerShell 脚本也无法运行，可以手动浏览器下载，参考 `手动下载模型.md`
