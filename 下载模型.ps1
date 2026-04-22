[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "=========================================="
Write-Host "BGE Model Download Script"
Write-Host "=========================================="
Write-Host ""

$MODEL_DIR = Join-Path $PSScriptRoot "models\bge-large-zh-v1.5"
Write-Host "Download to: $MODEL_DIR"
Write-Host ""

if (-not (Test-Path $MODEL_DIR)) {
    New-Item -ItemType Directory -Path $MODEL_DIR -Force | Out-Null
}

Write-Host "Downloading model files..."
Write-Host ""

$files = @(
    @{Name="config.json"; Url="https://hf-mirror.com/BAAI/bge-large-zh-v1.5/resolve/main/config.json"},
    @{Name="config_sentence_transformers.json"; Url="https://hf-mirror.com/BAAI/bge-large-zh-v1.5/resolve/main/config_sentence_transformers.json"},
    @{Name="pytorch_model.bin"; Url="https://hf-mirror.com/BAAI/bge-large-zh-v1.5/resolve/main/pytorch_model.bin"},
    @{Name="tokenizer.json"; Url="https://hf-mirror.com/BAAI/bge-large-zh-v1.5/resolve/main/tokenizer.json"},
    @{Name="tokenizer_config.json"; Url="https://hf-mirror.com/BAAI/bge-large-zh-v1.5/resolve/main/tokenizer_config.json"},
    @{Name="special_tokens_map.json"; Url="https://hf-mirror.com/BAAI/bge-large-zh-v1.5/resolve/main/special_tokens_map.json"},
    @{Name="vocab.txt"; Url="https://hf-mirror.com/BAAI/bge-large-zh-v1.5/resolve/main/vocab.txt"},
    @{Name="modeling.py"; Url="https://hf-mirror.com/BAAI/bge-large-zh-v1.5/resolve/main/modeling.py"},
    @{Name=" SentenceTransformerCandidates.json"; Url="https://hf-mirror.com/BAAI/bge-large-zh-v1.5/resolve/main/%20SentenceTransformerCandidates.json"}
)

$total = $files.Count
$current = 0

foreach ($file in $files) {
    $current++
    $outputPath = Join-Path $MODEL_DIR $file.Name

    if ($file.Name -eq "pytorch_model.bin") {
        Write-Host "[$current/$total] Downloading $($file.Name) (about 1.2GB, please wait)..." -ForegroundColor Cyan
    } else {
        Write-Host "[$current/$total] Downloading $($file.Name)..." -ForegroundColor Cyan
    }

    try {
        Invoke-WebRequest -Uri $file.Url -OutFile $outputPath -TimeoutSec 600
        Write-Host "  Done" -ForegroundColor Green
    } catch {
        Write-Host "  Failed: $($_.Exception.Message)" -ForegroundColor Red
    }

    Write-Host ""
}

Write-Host "=========================================="
Write-Host "Download Complete!"
Write-Host "=========================================="
Write-Host ""
Write-Host "Check downloaded files:"
Get-ChildItem $MODEL_DIR | Format-Table Name, @{N="Size(MB)";E={[math]::Round($_.Length/1MB,2)}} -AutoSize
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Modify .env: EMBEDDING_MODEL=./models/bge-large-zh-v1.5"
Write-Host "2. Restart backend service"
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
