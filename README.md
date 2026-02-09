# DevHub Vietnamese Voice AI - TTS & STT API

🎙️ **Professional Vietnamese Text-to-Speech & Speech-to-Text API** powered by Triton Inference Server, Piper TTS, and Sherpa-ONNX ASR.

## ✨ Features

### Text-to-Speech (TTS)
- 🇻🇳 **24 Vietnamese Voices** (14 female, 9 male, 1 other)
- ⚡ **High Performance** with GPU acceleration via Triton
- 🎛️ **Adjustable Speech Speed** (0.5x - 2.0x)
- 🔊 **High Quality Audio** (22.05kHz, 16-bit PCM WAV)
- 📝 **IPA Phonemization** - Accurate Vietnamese pronunciation

### Speech-to-Text (STT)
- 🎤 **Vietnamese ASR** - Automatic Speech Recognition
- 📊 **Two Model Options** - INT8 (fast) & Full Precision (accurate)
- 🔄 **Real-time Processing** - Low latency transcription
- 📁 **Multiple Input Formats** - WAV, audio data streams

### Infrastructure
- 🐳 **Docker Ready** - One-command deployment
- 🌐 **REST API** - Easy integration with any platform
- 💼 **Commercial License** - Ready for business use

## 🚀 Quick Start

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 8GB RAM minimum (16GB recommended)
- 4 CPU cores minimum (8 cores recommended)

### Installation

1. **Clone or extract the package:**
```bash
cd devhub_text_to_voice
```

2. **Download voice models:**
```powershell
# Windows - TTS voices
.\setup_models.ps1

# Optional: Add Speech-to-Text (STT) support
# Fast installation (recommended):
.\setup_stt_fast_windows.ps1

# Or manual installation:
pip install -r requirements-stt.txt
python download_stt_models.py
```
```bash
# Linux/macOS - TTS voices
chmod +x setup_models.sh
./setup_models.sh

# Optional: STT support
# Fast installation (Linux only):
chmod +x setup_stt_fast_linux.sh
./setup_stt_fast_linux.sh

# Or manual installation:
pip install -r requirements-stt.txt
python download_stt_models.py
```

3. **Start the TTS service:**
```bash
docker-compose up -d
```

4. **Verify installation:**
```bash
curl http://localhost:8080/health
```

## 📖 API Documentation

### Base URL
```
http://localhost:8080
```

### Endpoints

#### 1. Health Check
```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "triton_live": true,
  "triton_ready": true,
  "available_voices": 24
}
```

#### 2. List Available Voices
```bash
GET /voices
```

Response:
```json
{
  "total": 24,
  "voices": {
    "banmai": {
      "gender": "female",
      "description": "Ban Mai - Natural female voice"
    },
    "lacphi": {
      "gender": "female",
      "description": "Lạc Phi - Gentle female voice"
    },
    ...
  }
}
```

#### 3. Synthesize Speech (GET)
```bash
GET /synthesize?text=Xin chào&voice=banmai&speed=1.0
```

Parameters:
- `text` (required): Text to synthesize (Vietnamese)
- `voice` (optional): Voice name (default: "banmai")
- `speed` (optional): Speech speed 0.5-2.0 (default: 1.0, higher = slower)

Returns: WAV audio file

#### 4. Synthesize Speech (POST)
```bash
POST /synthesize
Content-Type: application/json

{
  "text": "Xin chào Việt Nam",
  "voice": "banmai",
  "speed": 1.5
}
```

Returns: WAV audio file

### Example Usage

**PowerShell (Windows):**
```powershell
# Simple GET request
Invoke-WebRequest -Uri "http://localhost:8080/synthesize?text=Xin chào&voice=banmai&speed=1.0" -OutFile output.wav

# POST request with JSON
$body = @{text="Xin chào Việt Nam"; voice="lacphi"; speed=1.5} | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8080/synthesize -Method POST -ContentType "application/json" -Body $body -OutFile output.wav
```

**curl (Linux/macOS):**
```bash
# Simple GET request
curl "http://localhost:8080/synthesize?text=Xin%20chào&voice=banmai&speed=1.0" -o output.wav

# POST request with JSON
curl -X POST http://localhost:8080/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text":"Xin chào Việt Nam","voice":"lacphi","speed":1.5}' \
  -o output.wav
```

**Python:**
```python
import requests

# Simple request
response = requests.get(
    "http://localhost:8080/synthesize",
    params={
        "text": "Xin chào Việt Nam",
        "voice": "banmai",
        "speed": 1.5
    }
)

with open("output.wav", "wb") as f:
    f.write(response.content)
```

**JavaScript/Node.js:**
```javascript
const fs = require('fs');

fetch('http://localhost:8080/synthesize', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    text: 'Xin chào Việt Nam',
    voice: 'banmai',
    speed: 1.5
  })
})
.then(res => res.arrayBuffer())
.then(buffer => fs.writeFileSync('output.wav', Buffer.from(buffer)));
```

## 🎭 Available Voices

### Female Voices (14)
- `banmai` - Ban Mai - Natural female voice
- `chieuthanh` - Chiều Thanh - Mature female voice
- `lacphi` - Lạc Phi - Gentle female voice
- `maiphuong` - Mai Phương - Professional female voice
- `ngochuyen` - Ngọc Huyền - Soft female voice
- `phuongtrang` - Phương Trang - Clear female voice
- `thientam` - Thiên Tâm - Sweet female voice
- `calmwoman3688` - Calm Woman - Calm female voice
- `mytam2` - My Tam - Bright female voice
- `mytam2794` - My Tam Alt - Alternative female voice
- `ngocngan3701` - Ngọc Ngân - Elegant female voice
- `taian2` - Tái An - Young female voice
- `taian4` - Tái An Alt - Alternative young female voice
- `thanhphuong2` - Thanh Phương - Professional female voice

### Male Voices (9)
- `deepman3909` - Deep Man - Deep male voice
- `duyoryx3175` - Duy Oryx - Natural male voice
- `manhdung` - Mạnh Dũng - Strong male voice
- `mattheo` - Mattheo - Young male voice
- `mattheo1` - Mattheo Alt - Alternative young male voice
- `minhkhang` - Minh Khang - Professional male voice
- `minhquang` - Minh Quang - Clear male voice
- `tranthanh3870` - Trấn Thanh - Mature male voice
- `vietthao3886` - Việt Thảo - Gentle male voice

### Other (1)
- `indo` - Indonesian accent

## ⚙️ Configuration

### Docker Compose Options

Edit `docker-compose.yml` to customize:

```yaml
services:
  triton:
    deploy:
      resources:
        limits:
          cpus: '4'        # CPU limit
          memory: 8G       # Memory limit
        reservations:
          cpus: '2'
          memory: 4G

  tts-api:
    environment:
      - TRITON_URL=triton:8000
      - MAX_WORKERS=4    # API worker processes
```

### Speech Speed Guidelines

- `0.5` - Very fast (2x speed)
- `1.0` - Normal speed (recommended)
- `1.5` - Slower, more clear
- `2.0` - Very slow

**Note:** Higher `speed` value = slower speech (parameter is actually `length_scale`)

## 🛠️ Management Commands

### Start services:
```bash
docker-compose up -d
```

### Stop services:
```bash
docker-compose down
```

### View logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f tts-api
docker-compose logs -f triton
```

### Restart services:
```bash
docker-compose restart
```

### Check status:
```bash
docker-compose ps
```

## 📊 Performance

Typical performance on 4-core CPU, 8GB RAM:

- **Latency**: 200-500ms per request
- **Throughput**: 10-20 requests/second
- **Audio Quality**: 22.05kHz, 16-bit PCM
- **Concurrent Requests**: Up to 50 (with queuing)

## 🔒 Security

For production deployment:

1. **Add API Authentication:**
   - Implement API keys
   - Use OAuth 2.0
   - Rate limiting

2. **Network Security:**
   - Use HTTPS/TLS
   - Firewall rules
   - VPN/private network

3. **Resource Limits:**
   - CPU/memory limits
   - Request rate limiting
   - Text length limits

## 📝 License

This software is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

### Third-Party Components

This product includes:
- **Triton Inference Server** (BSD-3-Clause)
- **Piper TTS Models** (Apache-2.0)
- **phonemizer** (GPL-3.0) - used as separate process
- **espeak-ng** (GPL-3.0) - used as separate process

See LICENSE file for complete third-party license information.

## 🆘 Support

For technical support and commercial inquiries:
- Email: support@devhub.vn
- Website: https://devhub.vn
- Documentation: https://docs.devhub.vn/tts

## 🔄 Updates

Check for updates:
```bash
docker pull devhub/tts-api:latest
docker pull nvcr.io/nvidia/tritonserver:23.10-py3
```

## � Speech-to-Text (STT) Add-on

### Installation

```powershell
# Windows
.\setup_stt.ps1
```

```bash
# Linux/macOS
pip install -r requirements-stt.txt
python download_stt_models.py
```

### Usage

```python
from stt_client import STTClient

# Initialize (INT8 for speed, False for accuracy)
client = STTClient(use_int8=True)

# Transcribe audio file
text = client.transcribe_file("recording.wav")
print(f"Transcribed: {text}")
```

### Models

| Model | Size | Speed | Best For |
|-------|------|-------|----------|
| INT8 | ~50MB | Fast ⚡ | Real-time, production |
| Full | ~180MB | Accurate 🎯 | Batch, high quality |

### Complete Pipeline

```python
# Voice Assistant Pipeline
from stt_client import STTClient
from tts_client_api import synthesize_speech

# 1. User speaks -> STT
stt = STTClient()
user_text = stt.transcribe_file("user_input.wav")

# 2. Process (AI response, translation, etc.)
response = process_request(user_text)

# 3. TTS -> Speak back
synthesize_speech(
    text=response,
    voice_model="voice_banmai",
    output_file="response.wav",
    triton_url="localhost:8000"
)
```

### Use Cases with STT

- 🤖 **Voice Assistants** - Full conversational AI
- 🎓 **Language Learning** - Pronunciation practice + feedback
- 📝 **Meeting Transcription** - Voice to text + TTS summaries
- 📞 **IVR Systems** - Interactive voice response
- ♿ **Accessibility** - Voice control + text-to-speech
- 🎙️ **Podcast Tools** - Transcription + automated narration

## �🏢 Commercial Use

This software is ready for commercial deployment including:
- ✅ SaaS platforms
- ✅ Mobile applications
- ✅ Web applications
- ✅ Voice assistants
- ✅ E-learning platforms
- ✅ Accessibility tools

No additional licensing fees required beyond standard software license.

---

**© 2026 DevHub. All rights reserved.**
