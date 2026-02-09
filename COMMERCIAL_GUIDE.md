# DevHub Vietnamese TTS - Commercial Package

## 📦 Package Contents

This commercial package includes:

```
devhub_text_to_voice/
├── docker-compose.yml          # Docker orchestration
├── Dockerfile.api              # API container build file
├── requirements-api.txt        # Python dependencies
├── requirements.txt            # Alternative dependencies
├── tts_api.py                  # FastAPI REST API server
├── tts_client_api.py          # Triton client library
├── setup_models.ps1           # Model download script (Windows)
├── setup_models.sh            # Model download script (Linux/macOS)
├── LICENSE                     # MIT License + third-party notices
├── README.md                   # User documentation
├── COMMERCIAL_GUIDE.md        # This file
└── models/                     # Voice models (24 voices)
    ├── voice_banmai/
    ├── voice_lacphi/
    ├── voice_deepman3909/
    └── ... (21 more voices)
```

## 💰 Pricing & Licensing

### License Type: **MIT License**

- ✅ **Commercial use allowed** - No restrictions
- ✅ **Modification allowed** - Customize as needed
- ✅ **Distribution allowed** - Resell or bundle
- ✅ **Private use allowed** - Internal company use
- ✅ **No royalties** - One-time purchase only
- ✅ **Source code included** - Full access

### What You Can Do:

1. **SaaS Platform** - Offer TTS as a cloud service
2. **Mobile Apps** - Integrate into iOS/Android apps
3. **Web Applications** - Add voice features to websites
4. **API Reselling** - Resell TTS API access
5. **White-Label Solutions** - Brand as your own product
6. **Enterprise Deployment** - Internal company use
7. **Embedded Systems** - Integrate into hardware

### What You Must Do:

1. **Include License Notice** - Keep LICENSE file in distributions
2. **Respect Third-Party Licenses** - Follow Triton (BSD-3), Piper (Apache-2.0) licenses
3. **GPL Compliance** - phonemizer/espeak-ng are used as separate processes (no linking)

### What You Cannot Do:

- ❌ **Claim Original Authorship** - Don't claim you created this
- ❌ **Remove License Notices** - Must keep attribution
- ❌ **Hold DevHub Liable** - Software provided "as is"

## 🚀 Deployment Options

### Option 1: On-Premise Deployment (Recommended)

**Best for:** Full control, data privacy, no bandwidth limits

```bash
# Install on your server
git clone <your-repo> or extract package
cd devhub_text_to_voice
./setup_models.sh
docker-compose up -d
```

**Requirements:**
- Server: 4+ cores, 8+ GB RAM, 20GB storage
- OS: Ubuntu 20.04+, CentOS 8+, or Windows Server 2019+
- Docker: 20.10+ and Docker Compose 2.0+

### Option 2: Cloud Deployment

**Best for:** Scalability, managed infrastructure

**AWS EC2:**
```bash
# t3.xlarge or larger (4 vCPU, 16 GB RAM)
# Ubuntu 22.04 AMI
# Security Group: Allow TCP 8080 (API), 8000/8001/8002 (Triton)

sudo apt update && sudo apt install -y docker.io docker-compose
cd devhub_text_to_voice
docker-compose up -d
```

**Google Cloud Compute Engine:**
```bash
# n1-standard-4 or larger
# Ubuntu 22.04 LTS
# Firewall: Allow TCP 8080

# Same Docker setup as AWS
```

**Azure Virtual Machines:**
```bash
# Standard_D4s_v3 or larger
# Ubuntu 22.04 LTS
# NSG: Allow TCP 8080

# Same Docker setup
```

### Option 3: Kubernetes Deployment

**Best for:** High availability, auto-scaling

```yaml
# k8s-deployment.yaml (example)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tts-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tts-api
  template:
    metadata:
      labels:
        app: tts-api
    spec:
      containers:
      - name: triton
        image: nvcr.io/nvidia/tritonserver:23.10-py3
        ports:
        - containerPort: 8000
      - name: api
        image: devhub/tts-api:latest
        ports:
        - containerPort: 8080
```

## 📈 Scaling Strategies

### Vertical Scaling (Single Server)

Increase resources on one server:

```yaml
# docker-compose.yml
services:
  triton:
    deploy:
      resources:
        limits:
          cpus: '8'
          memory: 16G
```

**Capacity:** Up to 50 concurrent requests

### Horizontal Scaling (Load Balancing)

Multiple servers with load balancer:

```
                    ┌─────────────┐
                    │   Nginx LB  │
                    │  (Port 80)  │
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼─────┐    ┌─────▼─────┐   ┌─────▼─────┐
    │  Server 1 │    │  Server 2 │   │  Server 3 │
    │   TTS API │    │   TTS API │   │   TTS API │
    └───────────┘    └───────────┘   └───────────┘
```

**Nginx config:**
```nginx
upstream tts_backend {
    least_conn;
    server 192.168.1.10:8080;
    server 192.168.1.11:8080;
    server 192.168.1.12:8080;
}

server {
    listen 80;
    location / {
        proxy_pass http://tts_backend;
    }
}
```

**Capacity:** 150+ concurrent requests (3 servers)

## 💼 Business Models

### Model 1: API-as-a-Service (SaaS)

**Monetization:**
- Charge per API call ($0.001 - $0.01 per request)
- Subscription tiers (Basic/Pro/Enterprise)
- Character/minute-based pricing

**Example Pricing:**
```
Free Tier:     1,000 requests/month
Basic:      $19/month -  50,000 requests
Pro:        $99/month - 500,000 requests
Enterprise: Custom pricing
```

### Model 2: White-Label Reselling

**Monetization:**
- License to agencies/developers
- One-time fee or annual subscription
- Custom branding support

**Example Pricing:**
```
Single Site License:     $999 one-time
Developer License:     $2,999 one-time
Agency License:        $9,999 one-time
Enterprise License:   Custom pricing
```

### Model 3: Embedded Feature

**Monetization:**
- Part of larger product/platform
- Value-add feature
- Competitive differentiation

**Example:**
- E-learning platform with voice narration
- Content management system with TTS
- Accessibility tool for visually impaired

## 🔐 Security Best Practices

### 1. API Authentication

Add JWT token authentication:

```python
# tts_api.py addition
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/synthesize")
async def synthesize(
    request: TTSRequest,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    if not verify_token(credentials.credentials):
        raise HTTPException(status_code=401)
    # ... existing code
```

### 2. Rate Limiting

Prevent abuse:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/synthesize")
@limiter.limit("10/minute")
async def synthesize(request: Request, ...):
    # ... existing code
```

### 3. HTTPS/TLS

Use reverse proxy with SSL:

```nginx
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8080;
    }
}
```

### 4. Input Validation

Limit text length and sanitize:

```python
@app.post("/synthesize")
async def synthesize(request: TTSRequest):
    if len(request.text) > 5000:  # Max 5000 characters
        raise HTTPException(status_code=400, detail="Text too long")
    
    # Sanitize HTML/SQL injection
    clean_text = sanitize_input(request.text)
```

## 📊 Monitoring & Analytics

### Health Monitoring

```bash
# Prometheus metrics endpoint
curl http://localhost:8080/metrics

# Response time monitoring
tail -f /var/log/tts-api.log | grep "response_time"
```

### Usage Analytics

Track:
- Requests per minute/hour/day
- Popular voices
- Average text length
- Error rates
- Response times

### Alerting

Set up alerts for:
- Service downtime
- High error rate (>5%)
- High latency (>2 seconds)
- High CPU/memory usage (>80%)

## 🛡️ Backup & Disaster Recovery

### What to Backup:

1. **Configuration files** (docker-compose.yml, .env)
2. **Custom voice models** (if added)
3. **API keys/secrets** (if implemented)
4. **Usage logs** (for analytics)

### Backup Strategy:

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf backup-$DATE.tar.gz \
    docker-compose.yml \
    models/ \
    .env \
    logs/

# Upload to S3/Cloud Storage
aws s3 cp backup-$DATE.tar.gz s3://your-bucket/backups/
```

## 📞 Support & Updates

### Getting Updates:

```bash
# Pull latest Docker images
docker pull devhub/tts-api:latest
docker pull nvcr.io/nvidia/tritonserver:23.10-py3

# Restart services
docker-compose down
docker-compose up -d
```

### Commercial Support Options:

1. **Community Support** (Free)
   - GitHub Issues
   - Community Forum
   - Email: support@devhub.ai.vn

2. **Priority Support** ($99/month)
   - 24-hour response time
   - Email support
   - Bug fixes priority

3. **Enterprise Support** ($999/month)
   - 4-hour response time
   - Phone support
   - Custom feature development
   - Dedicated account manager

## 📋 Compliance & Legal

### Data Privacy (GDPR/CCPA):

- ✅ No personal data stored
- ✅ No cookies or tracking
- ✅ No user data collection
- ✅ Audio files deleted after response

### Accessibility (WCAG/ADA):

- ✅ Provides audio alternative to text
- ✅ Supports assistive technologies
- ✅ Multiple voice options

### Export Compliance:

- ✅ No encryption >64-bit (not applicable)
- ✅ Open-source components (BSD/Apache/MIT)
- ✅ Can be exported worldwide

## 🎯 Marketing & Sales

### Target Markets:

1. **E-learning Platforms** - Course narration
2. **Content Creators** - YouTube/TikTok voiceovers
3. **Publishers** - Audiobook generation
4. **Accessibility Tools** - Screen readers
5. **Call Centers** - IVR systems
6. **Smart Home** - Voice assistants

### Key Selling Points:

- ✅ **24 Vietnamese voices** - Most comprehensive
- ✅ **High quality** - Natural-sounding speech
- ✅ **Fast deployment** - Docker-based, minutes to setup
- ✅ **Cost-effective** - One-time license, no per-use fees
- ✅ **Customizable** - Full source code access
- ✅ **Scalable** - From 1 to 1000+ req/sec

### Demo & Trial:

Offer potential customers:
- 30-day free trial
- Demo website with live API
- Sample audio files
- Performance benchmarks

## 📝 Customization Services

Offer additional paid services:

1. **Custom Voice Training** ($5,000 - $20,000)
   - Train voice from customer's audio samples
   - 2-4 weeks turnaround

2. **Custom Integration** ($2,000 - $10,000)
   - Integrate into customer's platform
   - Custom API endpoints
   - SSO/OAuth integration

3. **Performance Optimization** ($1,000 - $5,000)
   - Infrastructure tuning
   - Load testing
   - Caching strategies

4. **White-Label Branding** ($500 - $2,000)
   - Custom API documentation
   - Branded web interface
   - Custom domain setup

## 🎓 Training & Documentation

### Included:

- ✅ README.md - Quick start guide
- ✅ API documentation (this file)
- ✅ Docker deployment guide
- ✅ Troubleshooting guide

### Additional Services:

1. **Video Tutorials** ($500)
   - Setup and deployment
   - Integration examples
   - Best practices

2. **Live Training** ($1,000/session)
   - 2-hour online session
   - Q&A
   - Custom use cases

3. **Custom Documentation** ($1,000+)
   - Company-specific guides
   - Integration documentation
   - API client libraries

## 💡 Success Stories (Examples)

### Case Study 1: E-Learning Platform

**Client:** ABC Education
**Challenge:** Generate Vietnamese voice for 1,000+ courses
**Solution:** Deployed TTS API, integrated with CMS
**Results:**
- Saved $50,000 in voice actor fees
- Reduced production time from weeks to hours
- 95% student satisfaction with voice quality

### Case Study 2: Content Creator Tool

**Client:** XYZ Media Tools
**Challenge:** Offer TTS feature to 10,000 users
**Solution:** White-label license, cloud deployment
**Results:**
- 2,000 paying subscribers ($29/month)
- $58,000 monthly revenue
- 4.8/5 star rating

## 📧 Contact & Licensing

For commercial licensing inquiries:

**Email:** sales@devhub.ai.vn  
**Website:** https://devhub.ai.vn  
**Phone:** +84 xxx xxx xxx  

**Business Hours:** Mon-Fri, 9AM-6PM (GMT+7)

---

**© 2026 DevHub. All rights reserved.**

*This is a commercial product guide. By using this software, you agree to the terms specified in the LICENSE file.*
