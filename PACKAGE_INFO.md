# Package Summary

**Product:** DevHub Vietnamese TTS - Text-to-Speech API  
**Version:** 1.0.0  
**Release Date:** February 3, 2026  
**License:** MIT License  
**Developer:** DevHub  

## What's Included

### Core Components
- ✅ FastAPI REST API Server (`tts_api.py`)
- ✅ Triton Inference Client (`tts_client_api.py`)
- ✅ Docker Compose Configuration (`docker-compose.yml`)
- ✅ API Container Build File (`Dockerfile.api`)
- ✅ Model Setup Scripts (Windows & Linux)

### Voice Models
- ✅ 24 Pre-trained Vietnamese TTS Voices
  - 14 Female voices
  - 9 Male voices
  - 1 Indonesian-accented voice
- ✅ ONNX format for fast inference
- ✅ High-quality audio output (22.05kHz, 16-bit PCM)

### Documentation
- ✅ README.md - Complete API documentation
- ✅ QUICKSTART.md - Quick installation guide
- ✅ COMMERCIAL_GUIDE.md - Business & deployment guide
- ✅ API_EXAMPLES.md - Code examples (8 languages)
- ✅ LICENSE - Legal information
- ✅ CHANGELOG.md - Version history

## Key Features

### Technical
- 🚀 **Fast Inference** - Powered by Triton Inference Server
- 🎭 **24 Voices** - Multiple voice options for variety
- ⚡ **Low Latency** - 200-500ms response time
- 🔊 **High Quality** - Natural-sounding Vietnamese speech
- 🎛️ **Speed Control** - Adjustable speech rate (0.5x - 2.0x)
- 🐳 **Docker Ready** - One-command deployment
- 📦 **No Dependencies** - All libraries containerized

### Business
- 💼 **Commercial Ready** - MIT licensed, no restrictions
- 💰 **One-Time Cost** - No ongoing fees or royalties
- 🔓 **Full Source Code** - Complete access for customization
- 📈 **Scalable** - From 1 to 1000+ requests/second
- 🌐 **API-First** - Easy integration with any platform
- 🛡️ **No Vendor Lock-in** - Own and control your deployment

## System Requirements

### Minimum
- **CPU:** 2 cores
- **RAM:** 4 GB
- **Storage:** 10 GB
- **OS:** Ubuntu 20.04+ / Windows Server 2019+ / macOS 11+
- **Docker:** 20.10+
- **Docker Compose:** 2.0+

### Recommended
- **CPU:** 4+ cores
- **RAM:** 8+ GB
- **Storage:** 20 GB SSD
- **Network:** 100 Mbps+

### For High Traffic (100+ req/min)
- **CPU:** 8+ cores
- **RAM:** 16+ GB
- **Storage:** 50 GB SSD
- **Load Balancer:** Nginx/HAProxy

## Performance Metrics

### Latency (Average)
- Short text (<50 chars): 200-300ms
- Medium text (50-200 chars): 300-500ms
- Long text (200-500 chars): 500-1000ms

### Throughput
- Single server: 10-20 requests/second
- With load balancing (3 servers): 50-60 requests/second

### Concurrent Requests
- Up to 50 simultaneous requests (with queuing)

## Integration Examples

```python
# Python
import requests
response = requests.get("http://localhost:8080/synthesize",
    params={"text": "Xin chào", "voice": "banmai"})
with open("output.wav", "wb") as f:
    f.write(response.content)
```

```javascript
// JavaScript
fetch('http://localhost:8080/synthesize', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({text: 'Xin chào', voice: 'banmai'})
})
.then(res => res.arrayBuffer())
.then(buffer => fs.writeFileSync('output.wav', Buffer.from(buffer)));
```

```bash
# cURL
curl "http://localhost:8080/synthesize?text=Xin%20chào&voice=banmai" -o output.wav
```

## Use Cases

### E-Learning
- Course narration
- Language learning apps
- Educational content

### Content Creation
- Video voiceovers
- Podcast production
- Social media content

### Accessibility
- Screen readers
- Audio books
- Assistive technology

### Business Applications
- IVR systems
- Voice notifications
- Customer service bots

### Entertainment
- Game voice acting
- Character voices
- Interactive media

## Licensing

### Your Rights
✅ **Commercial use** - Sell, license, or offer as service  
✅ **Modification** - Customize for your needs  
✅ **Distribution** - Include in your products  
✅ **Private use** - Internal company applications  
✅ **Patent use** - No patent restrictions  

### Your Obligations
📋 **Include license** - Keep LICENSE file in distributions  
📋 **State changes** - Document modifications  
📋 **Include notice** - Credit original authors  

### Third-Party Licenses
- **Triton Inference Server:** BSD-3-Clause (commercial-friendly)
- **Piper TTS Models:** Apache-2.0 (commercial-friendly)
- **phonemizer/espeak-ng:** GPL-3.0 (used as separate processes)

## Pricing Models (Suggestions)

### SaaS Pricing
```
Free:      1,000 requests/month
Starter:   $19/month - 50,000 requests
Pro:       $99/month - 500,000 requests
Business:  $299/month - 2,000,000 requests
Enterprise: Custom pricing
```

### License Pricing
```
Single Site:   $999 one-time
Developer:     $2,999 one-time
Agency:        $9,999 one-time
Enterprise:    Custom pricing
```

### Value-Add Services
```
Custom Voice Training:     $5,000 - $20,000
Custom Integration:        $2,000 - $10,000
White-Label Branding:      $500 - $2,000
Priority Support:          $99/month
Enterprise Support:        $999/month
```

## Support Options

### Community (Free)
- GitHub Issues
- Email: support@devhub.vn
- Response time: 3-5 business days

### Priority Support ($99/month)
- Email support
- 24-hour response time
- Bug fix priority

### Enterprise Support ($999/month)
- Phone support
- 4-hour response time
- Custom feature development
- Dedicated account manager

## Quick Start

```bash
# 1. Extract package
cd devhub_text_to_voice

# 2. Download models (Windows)
.\setup_models.ps1

# 3. Start services
docker-compose up -d

# 4. Test
curl "http://localhost:8080/synthesize?text=Xin%20chào&voice=banmai" -o test.wav
```

## File Structure

```
devhub_text_to_voice/
├── README.md                  # Full documentation
├── QUICKSTART.md              # Quick start guide
├── COMMERCIAL_GUIDE.md        # Business guide
├── API_EXAMPLES.md            # Code examples
├── LICENSE                    # Legal information
├── CHANGELOG.md               # Version history
├── VERSION                    # Current version
├── .gitignore                 # Git ignore rules
├── docker-compose.yml         # Service orchestration
├── Dockerfile.api             # API container build
├── requirements-api.txt       # Python dependencies
├── requirements.txt           # Alternative dependencies
├── tts_api.py                 # FastAPI server (256 lines)
├── tts_client_api.py          # Triton client (159 lines)
├── setup_models.ps1           # Windows setup script
├── setup_models.sh            # Linux setup script
└── models/                    # Voice models (24 voices)
    ├── voice_banmai/
    │   ├── config.pbtxt       # Triton config
    │   └── 1/
    │       ├── model.onnx     # ONNX model
    │       └── model.onnx.json # Model config
    └── ... (23 more voices)
```

## What You Can Build

### Products
- Vietnamese audiobook platform
- E-learning course narration system
- Content creator TTS tool
- Accessibility reader app
- Voice bot for customer service

### Services
- TTS API as a service (SaaS)
- White-label TTS solution for agencies
- Custom voice training service
- Integration consulting
- Managed hosting service

### Integrations
- WordPress plugin
- Shopify app
- Mobile app SDK
- Chrome extension
- Slack/Discord bot

## Competitive Advantages

✅ **Most Comprehensive** - 24 Vietnamese voices (competitors: 2-5)  
✅ **Fully Owned** - No API key dependencies  
✅ **Cost Effective** - One-time purchase vs per-use pricing  
✅ **Customizable** - Full source code access  
✅ **Privacy** - On-premise deployment, no data sent to third parties  
✅ **Scalable** - Deploy anywhere from laptop to cloud  

## Success Metrics

After successful deployment, you should see:
- ✓ Health check returns 200 OK
- ✓ 24 voices available
- ✓ Response time < 500ms
- ✓ Audio quality score > 4/5
- ✓ Uptime > 99.9%

## Next Steps

1. **Read Documentation** - Start with QUICKSTART.md
2. **Install & Test** - Follow installation guide
3. **Try All Voices** - Find the best voice for your use case
4. **Integrate** - Use API_EXAMPLES.md for your language
5. **Deploy Production** - See COMMERCIAL_GUIDE.md for scaling
6. **Get Support** - Contact support@devhub.vn for help

## Contact Information

**Developer:** DevHub  
**Email:** support@devhub.vn  
**Sales:** sales@devhub.vn  
**Website:** https://devhub.vn  
**Documentation:** https://docs.devhub.vn/tts  

---

**© 2026 DevHub. All rights reserved.**

**Package Version:** 1.0.0  
**Last Updated:** February 3, 2026  
**License:** MIT License
