# DevHub Vietnamese TTS - Quick Start Guide

## 📋 Prerequisites Check

Before starting, verify you have:

- [ ] Docker Engine 20.10+ installed
- [ ] Docker Compose 2.0+ installed  
- [ ] 8GB+ RAM available
- [ ] 4+ CPU cores
- [ ] 20GB+ free disk space
- [ ] Internet connection (for model download)

## 🚀 Installation Steps

### Step 1: Extract Package

```bash
# Extract to desired location
cd /path/to/devhub_text_to_voice
```

### Step 2: Download Models

**Windows:**
```powershell
.\setup_models.ps1
```

**Linux/macOS:**
```bash
chmod +x setup_models.sh
./setup_models.sh
```

This will download 24 Vietnamese voice models (~500MB total).

### Step 3: Start Services

```bash
docker-compose up -d
```

Wait 30-60 seconds for services to start.

### Step 4: Verify Installation

```bash
# Check health
curl http://localhost:8080/health

# Expected response:
# {"status":"healthy","triton_live":true,"triton_ready":true,"available_voices":24}
```

### Step 5: Test Synthesis

**Windows PowerShell:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8080/synthesize?text=Xin chào&voice=banmai&speed=1.0" -OutFile test.wav
```

**Linux/macOS:**
```bash
curl "http://localhost:8080/synthesize?text=Xin%20chào&voice=banmai&speed=1.0" -o test.wav
```

Play `test.wav` - you should hear "Xin chào" in Vietnamese!

## ✅ Success Indicators

- ✓ Both containers running: `docker-compose ps`
- ✓ Health check returns 200 OK
- ✓ API accessible on http://localhost:8080
- ✓ Test audio file generated successfully

## 🐛 Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs

# Common issues:
# 1. Port 8080 already in use - change in docker-compose.yml
# 2. Not enough memory - increase Docker memory limit
# 3. Models not downloaded - run setup_models script
```

### "Service Unavailable" error

```bash
# Wait longer (Triton needs 30-60s to load models)
sleep 60

# Check Triton specifically
docker-compose logs triton
```

### Audio quality issues

- Try different voices: `voice=lacphi`, `voice=deepman3909`
- Adjust speed: `speed=1.5` (slower, clearer)
- Check input text encoding (must be UTF-8)

## 📚 Next Steps

1. Read [README.md](README.md) for full API documentation
2. See [COMMERCIAL_GUIDE.md](COMMERCIAL_GUIDE.md) for business usage
3. Check [LICENSE](LICENSE) for legal information

## 🆘 Support

- Email: support@devhub.vn
- GitHub Issues: Report bugs and request features

---

**Installation complete! 🎉**
