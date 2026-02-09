# WebSocket Streaming API Documentation

## Overview

WebSocket endpoints cho phép streaming real-time cho TTS (Text-to-Speech) và STT (Speech-to-Text).

### API Endpoints

#### 1. TTS WebSocket Stream
**URL:** `ws://localhost:8080/ws/tts`

**Purpose:** Tổng hợp tiếng nói từ text theo thời gian thực

**Request Format:**
```json
{
  "text": "Xin chào bạn",
  "voice": "banmai",
  "speed": 1.5,
  "noise_scale": 0.667,
  "noise_w": 0.8
}
```

**Response Format:**
```json
{
  "success": true,
  "audio": "base64_encoded_audio_data",
  "duration": 0.175,
  "voice": "banmai",
  "sample_rate": 22050
}
```

**Parameters:**
- `text` (string): Văn bản tiếng Việt cần tổng hợp
- `voice` (string): Giọng nói (mặc định: "banmai")
  - Giọng nữ: banmai, chieuthanh, lacphi, maiphuong, ngochuyen, phuongtrang, thientam, ...
  - Giọng nam: deepman3909, manhdung, minhkhang, mattheo, ...
- `speed` (float): Tốc độ nói (0.5-3.0, mặc định: 1.5)
- `noise_scale` (float): Mức độ nhiễu (mặc định: 0.667)
- `noise_w` (float): Trọng số nhiễu (mặc định: 0.8)

**Example JavaScript:**
```javascript
const ws = new WebSocket('ws://localhost:8080/ws/tts');

ws.onopen = () => {
  const request = {
    text: "Xin chào bạn",
    voice: "banmai",
    speed: 1.5
  };
  ws.send(JSON.stringify(request));
};

ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  if (response.success) {
    // Decode audio từ base64
    const audioData = Uint8Array.from(
      atob(response.audio), 
      c => c.charCodeAt(0)
    );
    const blob = new Blob([audioData], { type: 'audio/wav' });
    const url = URL.createObjectURL(blob);
    
    // Phát audio
    const audio = new Audio(url);
    audio.play();
  }
};
```

**Example Python:**
```python
import asyncio
import websockets
import json
import base64

async def test_tts():
    async with websockets.connect('ws://localhost:8080/ws/tts') as ws:
        request = {
            "text": "Xin chào bạn",
            "voice": "banmai",
            "speed": 1.5
        }
        await ws.send(json.dumps(request))
        response = json.loads(await ws.recv())
        
        if response['success']:
            audio_bytes = base64.b64decode(response['audio'])
            with open('output.wav', 'wb') as f:
                f.write(audio_bytes)

asyncio.run(test_tts())
```

---

#### 2. STT WebSocket Stream
**URL:** `ws://localhost:8080/ws/stt`

**Purpose:** Chuyển đổi âm thanh thành text theo thời gian thực

**Request Format:**
```json
{
  "audio": "base64_encoded_audio",
  "sample_rate": 16000
}
```

**Response Format:**
```json
{
  "success": true,
  "text": "Xin chào bạn",
  "duration": 1.234,
  "processing_time": 0.456,
  "model": "sherpa-onnx-zipformer-vi-int8"
}
```

**Parameters:**
- `audio` (string): Audio data encoded as base64
- `sample_rate` (int): Sample rate của audio (mặc định: 16000 Hz)

**Example JavaScript:**
```javascript
const ws = new WebSocket('ws://localhost:8080/ws/stt');

ws.onopen = () => {
  // Đọc file audio
  const fileInput = document.getElementById('audioFile');
  const file = fileInput.files[0];
  const reader = new FileReader();
  
  reader.onload = async (e) => {
    const arrayBuffer = e.target.result;
    const uint8Array = new Uint8Array(arrayBuffer);
    const base64 = btoa(String.fromCharCode.apply(null, uint8Array));
    
    const request = {
      audio: base64,
      sample_rate: 16000
    };
    ws.send(JSON.stringify(request));
  };
  
  reader.readAsArrayBuffer(file);
};

ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  if (response.success) {
    console.log('Transcribed text:', response.text);
    console.log('Duration:', response.duration, 's');
    console.log('Processing time:', response.processing_time, 's');
  }
};
```

**Example Python:**
```python
import asyncio
import websockets
import json
import base64

async def test_stt(audio_file):
    async with websockets.connect('ws://localhost:8080/ws/stt') as ws:
        # Đọc audio file
        with open(audio_file, 'rb') as f:
            audio_bytes = f.read()
        
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        request = {
            "audio": audio_base64,
            "sample_rate": 16000
        }
        
        await ws.send(json.dumps(request))
        response = json.loads(await ws.recv())
        
        if response['success']:
            print(f"Text: {response['text']}")
            print(f"Duration: {response['duration']}s")
            print(f"Processing time: {response['processing_time']}s")

asyncio.run(test_stt('audio.wav'))
```

---

## Testing

### 1. Test với HTML Client
Mở file `websocket_client.html` trong trình duyệt:
```bash
# Option 1: Dùng Python simple HTTP server
python -m http.server 8000

# Option 2: Mở trực tiếp file HTML
start websocket_client.html  # Windows
open websocket_client.html   # macOS
xdg-open websocket_client.html  # Linux
```

Truy cập `http://localhost:8000/websocket_client.html`

### 2. Test với Python Script
```bash
python test_websocket.py
```

---

## Lưu ý Quan trọng

1. **CORS:** WebSocket không tuân theo CORS, nhưng REST API tuân theo. Nếu frontend khác domain cần CORS setup.

2. **Connection Timeout:** WebSocket giữ kết nối mở. Nên close khi không sử dụng.

3. **Audio Format:**
   - TTS output: WAV 22050Hz PCM 16-bit mono
   - STT input: WAV format, bất kỳ sample rate nào (khuyến nghị 16000Hz)

4. **Base64 Encoding:**
   - Luôn encode/decode audio thành base64 khi truyền qua JSON
   - JavaScript: `btoa()` để encode, `atob()` để decode
   - Python: `base64.b64encode()` / `base64.b64decode()`

5. **Error Handling:**
   ```json
   {
     "error": "Invalid voice: unknown_voice"
   }
   ```

---

## Advanced Usage

### Real-time Streaming (Continuous)
Bạn có thể gửi nhiều request liên tiếp qua cùng một WebSocket connection:

```javascript
const ws = new WebSocket('ws://localhost:8080/ws/tts');

ws.onopen = () => {
  // Gửi request 1
  ws.send(JSON.stringify({
    text: "Xin chào",
    voice: "banmai"
  }));
  
  // Gửi request 2
  setTimeout(() => {
    ws.send(JSON.stringify({
      text: "Đây là test 2",
      voice: "mattheo"
    }));
  }, 1000);
};

ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  if (response.success) {
    console.log("Response received");
  }
};
```

### Microphone Input (Web Audio API)
```javascript
const ws = new WebSocket('ws://localhost:8080/ws/stt');

navigator.mediaDevices.getUserMedia({ audio: true })
  .then(stream => {
    const mediaRecorder = new MediaRecorder(stream);
    
    mediaRecorder.ondataavailable = async (event) => {
      const arrayBuffer = await event.data.arrayBuffer();
      const uint8Array = new Uint8Array(arrayBuffer);
      const base64 = btoa(String.fromCharCode.apply(null, uint8Array));
      
      ws.send(JSON.stringify({
        audio: base64,
        sample_rate: 16000
      }));
    };
    
    mediaRecorder.start(1000); // Record in 1-second chunks
  });
```

---

## Performance Tips

1. **Connection Reuse:** Mở 1 connection và tái sử dụng thay vì mở nhiều connections
2. **Batch Processing:** Ghi âm nhiều giây rồi gửi 1 lần thay vì streaming từng frame
3. **Compression:** Nếu network bị chậm, xem xét compress audio trước khi gửi

---

## Troubleshooting

### "Connection Refused"
- Kiểm tra Docker container đang chạy: `docker ps`
- Kiểm tra port 8080: `netstat -tuln | grep 8080` (Linux/Mac) hoặc `netstat -ano | findstr 8080` (Windows)

### "WebSocket closed unexpectedly"
- Check Docker logs: `docker logs tts-api`
- Xem request/response có error không

### "Audio quality poor"
- Tăng `speed` parameter (values > 1.5) để nghe chậm hơn
- Giảm `noise_scale` để ít đầu ra thêm

---

## API Compatibility

| Endpoint | Method | Status |
|----------|--------|--------|
| `/ws/tts` | WebSocket | ✓ Working |
| `/ws/stt` | WebSocket | ✓ Working |
| `/synthesize` (GET/POST) | REST | ✓ Working |
| `/transcribe` | REST | ✓ Working |
| `/health` | REST | ✓ Working |
| `/voices` | REST | ✓ Working |

