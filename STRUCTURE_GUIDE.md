# 📁 Project Structure After Organization

## Cấu trúc Thư mục

```
devhub_text_to_voice/
├── models/
│   └── text_to_speech/           # TTS Models cho Triton (24 voices)
│       ├── voice_banmai/
│       ├── voice_chieuthanh/
│       ├── voice_deepman3909/
│       └── ... (21 more voices)
│
├── models_/
│   └── stt/                       # STT Models (không qua Triton)
│       ├── sherpa-onnx-zipformer-vi-int8/
│       └── sherpa-onnx-zipformer-vi-full/
│
├── docker-compose.yml             # Docker configuration
├── Dockerfile.api                 # FastAPI container
├── tts_api.py                     # FastAPI application (TTS + STT + WebSocket)
├── tts_client_api.py              # TTS inference client
├── websocket_client.html          # Web UI for testing
├── test_websocket.py              # Python test client
├── WEBSOCKET_API.md               # API documentation
└── ...
```

## Cấu hình Docker

### Triton Server
- **Mount:** `./models/text_to_speech:/models` (read-only)
- **Port:** 8000 (HTTP), 8001 (gRPC)
- **Models:** 24 voice models cho TTS

### FastAPI Server
- **Mount:** 
  - `./models/text_to_speech:/app/models/text_to_speech` (TTS)
  - `./models_/stt:/app/models_/stt` (STT)
- **Port:** 8080 (HTTP + WebSocket)
- **Features:** REST API + WebSocket Streaming

## Endpoints

### REST API
| URL | Method | Purpose |
|-----|--------|---------|
| `/` | GET | API root |
| `/health` | GET | Health check |
| `/voices` | GET | List all voices |
| `/synthesize` | GET/POST | TTS synthesis |
| `/transcribe` | POST | STT transcription |
| `/info` | GET | Service info |

### WebSocket API
| URL | Purpose |
|-----|---------|
| `ws://localhost:8080/ws/tts` | Real-time TTS streaming |
| `ws://localhost:8080/ws/stt` | Real-time STT streaming |

## Quick Start

### 1. Start Docker
```bash
cd devhub_text_to_voice
docker-compose up -d
```

### 2. Test TTS (REST)
```bash
curl "http://localhost:8080/synthesize?text=Xin+chào&voice=banmai" -o output.wav
```

### 3. Test WebSocket
```bash
python test_websocket.py
```

### 4. Web Interface
- Open `websocket_client.html` in browser
- Click "Synthesize" or "Transcribe"
- Real-time audio streaming

## Configuration

### Voice Selection
**Female Voices:**
- banmai, chieuthanh, lacphi, maiphuong, ngochuyen, phuongtrang, thientam
- calmwoman3688, mytam2, mytam2794, ngocngan3701, taian2, taian4, thanhphuong2

**Male Voices:**
- deepman3909, manhdung, minhkhang, minhquang, mattheo, mattheo1
- tranthanh3870, vietthao3886, duyoryx3175

### TTS Parameters
```json
{
  "text": "Input text",
  "voice": "banmai",
  "speed": 1.5,        // 0.5-3.0 (higher = slower)
  "noise_scale": 0.667,
  "noise_w": 0.8
}
```

### STT Support
- Input: WAV format, any sample rate (16000 Hz recommended)
- Output: Vietnamese text transcription
- Model: sherpa-onnx-zipformer-vi-int8

## Troubleshooting

### Container Issues
```bash
# Check logs
docker logs tritonserver
docker logs tts-api

# Restart
docker-compose down
docker-compose up -d
```

### Port Already in Use
```bash
# Find process using port 8080
lsof -i :8080              # Linux/Mac
netstat -ano | findstr 8080 # Windows

# Change port in docker-compose.yml
# Ports: "8081:8080"
```

### WebSocket Connection Failed
- Ensure containers are running: `docker ps`
- Check firewall settings
- Verify CORS settings if using from different origin

## Performance Notes

- **TTS:** ~100-500ms per synthesis (depends on text length)
- **STT:** Real-time processing (faster than audio duration)
- **GPU:** Uses CPU by default. Can enable GPU in docker-compose.yml

## File Changes Summary

### Moved
- `models/voice_* → models/text_to_speech/voice_*` (24 folders)

### Updated
- `docker-compose.yml`: Changed volume mounts for new structure
- `tts_client_api.py`: Updated config path detection
- `tts_api.py`: Added WebSocket endpoints + imports

### Created
- `websocket_client.html`: Interactive web UI
- `test_websocket.py`: Python test client
- `WEBSOCKET_API.md`: Complete API documentation

## Next Steps

1. ✅ Move models to correct directories
2. ✅ Configure Docker mounts
3. ✅ Add WebSocket streaming
4. ✅ Create testing tools
5. 📋 (Optional) Add SSL/TLS for production
6. 📋 (Optional) Add authentication
7. 📋 (Optional) Add load balancing

