✅ **FIXED:**
- Small files work (50KB-600KB): ✅ 
- Ffmpeg conversion added: ✅
- Supports MP3/M4A/AAC/OGG formats: ✅
- Streaming upload từ client: ✅

❌ **ISSUE: Large files (8MB) crash với OOM**
- Docker logs: `exitCode=137` = Out Of Memory
- Container limit: 8GB
- File: 8MB WAV → processing needs more RAM

**Root cause:**
Sherpa-onnx model + numpy arrays + ffmpeg output = memory spike > 8GB

**Solutions to try:**
1. Optimize sherpa model loading (shared/reuse)
2. Process file từng phần nhỏ
3. Increase container limit to 16GB
4. Use lighter sherpa model
5. Add swap memory

**Current status:** 
- API: `/transcribe` (multipart) → OOM at 8MB
- API: `/transcribe-raw` (binary) → OOM at 8MB  
- Both endpoints crash same place = sherpa processing issue

Testing now với file nhỏ hơn để tìm threshold...
