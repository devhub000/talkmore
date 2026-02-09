# Fast Installation Script for Windows
# For Windows, sherpa-onnx can be installed from PyPI

Write-Host "`n==================================================" -ForegroundColor Cyan
Write-Host "STT Setup - Fast Installation (Windows)" -ForegroundColor Cyan
Write-Host "==================================================`n" -ForegroundColor Cyan

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.10" -ForegroundColor Red
    exit 1
}

Write-Host "`n[1/2] Installing dependencies..." -ForegroundColor Yellow
pip install sentencepiece huggingface-hub "numpy<2"

Write-Host "`n[2/2] Installing Sherpa-ONNX..." -ForegroundColor Yellow
pip install "sherpa-onnx>=1.12.6"

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nError: Installation failed!" -ForegroundColor Red
    exit 1
}

Write-Host "`n==================================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "==================================================`n" -ForegroundColor Cyan

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Download models: python download_stt_models.py" -ForegroundColor Gray
Write-Host "  2. Test STT: python stt_simple_example.py" -ForegroundColor Gray
