# Speech-to-Text Setup Script
# Automates installation and model download

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "Speech-to-Text Setup - Vietnamese ASR Models" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Check Python
Write-Host "[1/4] Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.10 or higher" -ForegroundColor Red
    exit 1
}
Write-Host "  $pythonVersion" -ForegroundColor Green

# Install dependencies
Write-Host "`n[2/4] Installing STT dependencies..." -ForegroundColor Yellow
Write-Host "  Installing from requirements-stt.txt..." -ForegroundColor Gray
pip install -r requirements-stt.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to install dependencies!" -ForegroundColor Red
    exit 1
}
Write-Host "  Dependencies installed successfully" -ForegroundColor Green

# Create models directory
Write-Host "`n[3/4] Creating models directory..." -ForegroundColor Yellow
$modelsDir = "models\stt"
if (-not (Test-Path $modelsDir)) {
    New-Item -ItemType Directory -Path $modelsDir -Force | Out-Null
    Write-Host "  Created: $modelsDir" -ForegroundColor Green
} else {
    Write-Host "  Directory exists: $modelsDir" -ForegroundColor Green
}

# Download models
Write-Host "`n[4/4] Downloading STT models from HuggingFace..." -ForegroundColor Yellow
Write-Host "  This will download ~230MB of model files" -ForegroundColor Gray
Write-Host "  Models:" -ForegroundColor Gray
Write-Host "    - sherpa-onnx-zipformer-vi-int8 (~50MB, faster)" -ForegroundColor Gray
Write-Host "    - sherpa-onnx-zipformer-vi (~180MB, more accurate)" -ForegroundColor Gray

$response = Read-Host "`n  Continue? (Y/n)"
if ($response -eq "n" -or $response -eq "N") {
    Write-Host "`nSetup cancelled." -ForegroundColor Yellow
    exit 0
}

python download_stt_models.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nError: Model download failed!" -ForegroundColor Red
    Write-Host "Please check your internet connection and try again" -ForegroundColor Red
    exit 1
}

# Test installation
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "Testing STT Installation" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "Running test script..." -ForegroundColor Yellow
python test_stt.py

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Test with your own audio files:" -ForegroundColor Gray
Write-Host "     python stt_client.py your_audio.wav" -ForegroundColor Gray
Write-Host "`n  2. Integrate into your application:" -ForegroundColor Gray
Write-Host "     from stt_client import STTClient" -ForegroundColor Gray
Write-Host "     client = STTClient()" -ForegroundColor Gray
Write-Host "     text = client.transcribe_file('audio.wav')" -ForegroundColor Gray
Write-Host "`n  3. Use with TTS for full voice pipeline:" -ForegroundColor Gray
Write-Host "     Audio -> STT -> Text Processing -> TTS -> Audio" -ForegroundColor Gray
