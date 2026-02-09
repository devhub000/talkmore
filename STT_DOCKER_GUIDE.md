# Enabling Speech-to-Text (STT) in Docker

This guide explains how to add STT support to your TTS Docker deployment.

## Architecture Overview

- **TTS (Text-to-Speech)**: Uses Triton Inference Server for model serving
  - Models: 24 Vietnamese voices in `models/voice_*/`
  - Inference: GPU-accelerated via Triton
  
- **STT (Speech-to-Text)**: Uses Sherpa-ONNX directly in Python
  - Models: Vietnamese zipformer in `models/stt/`
  - Inference: CPU-based, runs in API container

## Enable STT in Docker

### Step 1: Download STT Models

```bash
# Download models to models/stt/
python download_stt_models.py
```

This will download:
- `models/stt/sherpa-onnx-zipformer-vi-int8/` (~30MB, faster)
- `models/stt/sherpa-onnx-zipformer-vi/` (~100MB, more accurate)

### Step 2: Enable STT in Dockerfile

Edit `Dockerfile.api` and uncomment the STT section:

```dockerfile
# OPTIONAL: Uncomment to enable Speech-to-Text (STT) support
# This adds ~50MB to image and requires models/stt volume mount
COPY requirements-stt.txt .
RUN pip install --no-cache-dir -r requirements-stt.txt
```

### Step 3: Mount STT Models in Docker Compose

Edit `docker-compose.yml` and uncomment the STT volume:

```yaml
volumes:
  - ./models:/models:ro  # TTS voice models (read-only)
  # Uncomment to enable STT support:
  - ./models/stt:/app/models/stt:ro  # STT models (read-only)
```

### Step 4: Rebuild and Restart

```bash
# Rebuild API container
docker-compose build tts-api --no-cache

# Restart services
docker-compose up -d
```

## Test STT Endpoint

### Upload Audio File

```bash
curl -X POST http://localhost:8080/transcribe \
  -F "audio=@recording.wav"
```

### Response

```json
{
  "text": "xin chào việt nam",
  "duration": 2.5,
  "sample_rate": 22050,
  "model": "sherpa-onnx-zipformer-vi-int8",
  "processing_time": 0.34,
  "original_filename": "recording.wav"
}
```

## Check STT Status

```bash
curl http://localhost:8080/
```

Look for `"stt": {"available": true}` in the response.

## Why STT Doesn't Use Triton?

1. **Different Architecture**: 
   - TTS models (Piper/VITS) are optimized for Triton
   - STT models (Sherpa-ONNX) have their own runtime

2. **Simplicity**:
   - Running sherpa-onnx directly avoids complex Triton configuration
   - Fewer dependencies and easier deployment

3. **Performance**:
   - STT INT8 model is already very fast on CPU
   - Triton overhead not needed for this use case

## Optional: Deploy STT to Triton

If you want to use Triton for STT (for consistency or GPU acceleration):

1. Create `models/stt_triton/` directory
2. Add `config.pbtxt` for each ONNX model
3. Configure Triton model repository
4. Update API to use Triton client for STT

This is more complex and not recommended unless you have specific GPU requirements.

## Resource Requirements

### With TTS Only
- CPU: 4 cores
- RAM: 4GB
- Disk: 2GB (models)

### With TTS + STT
- CPU: 4 cores (STT uses 2 threads)
- RAM: 6GB (+2GB for STT models and runtime)
- Disk: 2.2GB (+200MB for STT models)

## Troubleshooting

### "STT not available" Error

Check if sherpa-onnx is installed:
```bash
docker exec tts-api python -c "import sherpa_onnx; print('OK')"
```

If not installed, rebuild with STT enabled (Step 2).

### "STT models not found" Error

Check if models are mounted:
```bash
docker exec tts-api ls -la /app/models/stt/
```

If empty, check volume mount (Step 3) and restart.

### Poor Transcription Quality

- Use full precision model instead of INT8
- Ensure audio is clear (16kHz, mono recommended)
- Check audio format is supported (WAV preferred)

## Production Considerations

1. **Scaling**: STT is CPU-bound, scale horizontally
2. **Caching**: Cache common transcriptions
3. **Rate Limiting**: Add rate limits to prevent abuse
4. **Authentication**: Add API keys for production
5. **Monitoring**: Track transcription accuracy and performance
