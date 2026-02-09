# PowerShell script to setup Vietnamese TTS Models
# Downloads 24 pre-trained Piper TTS models

Write-Host "========================================"
Write-Host "DevHub Vietnamese TTS - Model Setup"
Write-Host "========================================"
Write-Host ""

$MODELS_DIR = ".\models"

# Create models directory
New-Item -ItemType Directory -Force -Path $MODELS_DIR | Out-Null

# Base URLs for models
$BASE_MODEL_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/vi/vi_VN/vivos/medium/vi_VN-vivos-medium.onnx"
$CONFIG_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/vi/vi_VN/vivos/medium/vi_VN-vivos-medium.onnx.json"

# Voice list (24 voices)
$VOICES = @(
    "voice_banmai",
    "voice_lacphi",
    "voice_deepman3909",
    "voice_chieuthanh",
    "voice_maiphuong",
    "voice_ngochuyen",
    "voice_phuongtrang",
    "voice_thientam",
    "voice_calmwoman3688",
    "voice_mytam2",
    "voice_mytam2794",
    "voice_ngocngan3701",
    "voice_taian2",
    "voice_taian4",
    "voice_thanhphuong2",
    "voice_duyoryx3175",
    "voice_manhdung",
    "voice_mattheo",
    "voice_mattheo1",
    "voice_minhkhang",
    "voice_minhquang",
    "voice_tranthanh3870",
    "voice_vietthao3886",
    "voice_indo"
)

Write-Host "Downloading voice models..."
Write-Host ""

foreach ($voice in $VOICES) {
    Write-Host "Setting up $voice..."
    
    # Create Triton model structure
    $MODEL_DIR = "$MODELS_DIR\$voice\1"
    New-Item -ItemType Directory -Force -Path $MODEL_DIR | Out-Null
    
    # Download ONNX model
    $ONNX_PATH = "$MODEL_DIR\model.onnx"
    if (-not (Test-Path $ONNX_PATH)) {
        Write-Host "  Downloading ONNX model..."
        Invoke-WebRequest -Uri $BASE_MODEL_URL -OutFile $ONNX_PATH
    } else {
        Write-Host "  ✓ ONNX model already exists"
    }
    
    # Download config
    $CONFIG_PATH = "$MODEL_DIR\model.onnx.json"
    if (-not (Test-Path $CONFIG_PATH)) {
        Write-Host "  Downloading config..."
        Invoke-WebRequest -Uri $CONFIG_URL -OutFile $CONFIG_PATH
    } else {
        Write-Host "  ✓ Config already exists"
    }
    
    # Create Triton config.pbtxt
    $CONFIG_PBTXT = @"
name: "$voice"
platform: "onnxruntime_onnx"
max_batch_size: 1
input [
  {
    name: "input"
    data_type: TYPE_INT64
    dims: [ -1 ]
  },
  {
    name: "input_lengths"
    data_type: TYPE_INT64
    dims: [ 1 ]
  },
  {
    name: "scales"
    data_type: TYPE_FP32
    dims: [ 3 ]
  }
]
output [
  {
    name: "output"
    data_type: TYPE_FP32
    dims: [ -1 ]
  }
]
"@
    
    Set-Content -Path "$MODELS_DIR\$voice\config.pbtxt" -Value $CONFIG_PBTXT
    
    Write-Host "  ✓ $voice setup complete"
    Write-Host ""
}

Write-Host "========================================"
Write-Host "Model setup completed!"
Write-Host "========================================"
Write-Host ""
Write-Host "Total voices installed: $($VOICES.Count)"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Start the service: docker-compose up -d"
Write-Host "  2. Check health: Invoke-WebRequest http://localhost:8080/health"
Write-Host "  3. Test synthesis: Invoke-WebRequest 'http://localhost:8080/synthesize?text=Xin chào&voice=banmai' -OutFile test.wav"
Write-Host ""

