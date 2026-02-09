# Changelog

All notable changes to DevHub Vietnamese TTS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-03

### Added
- Initial commercial release
- 24 Vietnamese TTS voices (14 female, 9 male, 1 other)
- FastAPI REST API with 6 endpoints
- Docker Compose deployment stack
- Triton Inference Server integration
- IPA phonemization with espeak-ng
- Speech speed control (0.5x - 2.0x)
- High-quality audio output (22.05kHz, 16-bit PCM WAV)
- Comprehensive documentation:
  - README.md - Full API documentation
  - COMMERCIAL_GUIDE.md - Business and deployment guide
  - QUICKSTART.md - Quick start guide
  - LICENSE - MIT license with third-party notices
- Automated model setup scripts (Windows PowerShell & Linux Bash)
- Health check endpoints
- CORS support for web applications
- Audio quality improvements:
  - Fixed 4D tensor extraction bug
  - Added silence padding (200ms before/after)
  - Extra phoneme padding for complete speech
  - Proper audio normalization

### Features
- Voice switching via API parameter (no restart needed)
- GET and POST endpoints for synthesis
- JSON and URL parameter input
- Streaming audio response
- Concurrent request handling
- Docker health checks
- Automatic service restart

### Technical
- Python 3.10
- FastAPI 0.104.0
- Triton Inference Server 23.10
- Piper TTS ONNX models
- phonemizer 3.3.0
- espeak-ng 1.52.0
- Docker Compose 3.8

### License
- MIT License for application code
- BSD-3-Clause (Triton Inference Server)
- Apache-2.0 (Piper TTS models)
- GPL-3.0 (phonemizer, espeak-ng) - used as separate processes

### Known Issues
- None

### Security
- No known vulnerabilities
- Recommend implementing API authentication for production
- Recommend rate limiting for public deployments

---

## Version History

- **1.0.0** (2026-02-03) - Initial commercial release
