@echo off
chcp 65001 > nul
echo ============================================
echo BGE 模型下载脚本
echo ============================================
echo.

set MODEL_DIR=%~dp0models\bge-large-zh-v1.5
echo 模型将下载到: %MODEL_DIR%
echo.

if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"

echo 正在下载模型文件...
echo.

echo [1/8] 下载 config.json...
powershell -Command "Invoke-WebRequest -Uri 'https://hf-mirror.com/BAAI/bge-large-zh-v1.5/resolve/main/config.json' -OutFile '%MODEL_DIR%\config.json'"
if %ERRORLEVEL% neq 0 (
    echo [错误] 下载 config.json 失败
)

echo.
echo [2/8] 下载 config_sentence_transformers.json...
powershell -Command "Invoke-WebRequest -Uri 'https://hf-mirror.com/BAAI/bge-large-zh-v1.5/resolve/main/config_sentence_transformers.json' -OutFile '%MODEL_DIR%\config_sentence_transformers.json'"

echo.
echo [3/8] 下载 model.safetensors (约 1.2GB，请耐心等待)...
powershell -Command "Invoke-WebRequest -Uri 'https://hf-mirror.com/BAAI/bge-large-zh-v1.5/resolve/main/model.safetensors' -OutFile '%MODEL_DIR%\model.safetensors'"
if %ERRORLEVEL% neq 0 (
    echo [错误] 下载 model.safetensors 失败
)

echo.
echo [4/8] 下载 tokenizer.json...
powershell -Command "Invoke-WebRequest -Uri 'https://hf-mirror.com/BAAI/bge-large-zh-v1.5/resolve/main/tokenizer.json' -OutFile '%MODEL_DIR%\tokenizer.json'"

echo.
echo [5/8] 下载 tokenizer_config.json...
powershell -Command "Invoke-WebRequest -Uri 'https://hf-mirror.com/BAAI/bge-large-zh-v1.5/resolve/main/tokenizer_config.json' -OutFile '%MODEL_DIR%\tokenizer_config.json'"

echo.
echo [6/8] 下载 special_tokens_map.json...
powershell -Command "Invoke-WebRequest -Uri 'https://hf-mirror.com/BAAI/bge-large-zh-v1.5/resolve/main/special_tokens_map.json' -OutFile '%MODEL_DIR%\special_tokens_map.json'"

echo.
echo [7/8] 下载 vocab.txt...
powershell -Command "Invoke-WebRequest -Uri 'https://hf-mirror.com/BAAI/bge-large-zh-v1.5/resolve/main/vocab.txt' -OutFile '%MODEL_DIR%\vocab.txt'"

echo.
echo [8/8] 下载 modeling.py...
powershell -Command "Invoke-WebRequest -Uri 'https://hf-mirror.com/BAAI/bge-large-zh-v1.5/resolve/main/modeling.py' -OutFile '%MODEL_DIR%\modeling.py'"

echo.
echo ============================================
echo 模型下载完成！
echo ============================================
echo.
echo 检查下载的文件...
dir "%MODEL_DIR%"
echo.
echo 下一步：
echo 1. 修改 .env 中的 EMBEDDING_MODEL 为本地路径
echo 2. 重启后端服务
echo.
pause
