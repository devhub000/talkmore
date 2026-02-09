#!/bin/bash
# Quick Start Guide for Vietnamese TTS & STT WebSocket API

echo "================================"
echo "🎤 Vietnamese TTS & STT WebSocket"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠ Docker not found. Please install Docker first.${NC}"
    exit 1
fi

echo -e "${BLUE}1. Starting Docker containers...${NC}"
docker-compose up -d

# Wait for Triton to be healthy
echo -e "${BLUE}2. Waiting for Triton server to be ready...${NC}"
sleep 10

# Check if containers are running
TRITON=$(docker inspect -f '{{.State.Health.Status}}' tritonserver 2>/dev/null)
API=$(docker inspect -f '{{.State.Status}}' tts-api 2>/dev/null)

if [ "$TRITON" == "healthy" ] && [ "$API" == "running" ]; then
    echo -e "${GREEN}✓ Containers are running${NC}"
    echo ""
    
    echo -e "${BLUE}Available Services:${NC}"
    echo ""
    echo "📺 Web UI (Interactive)"
    echo "   Open: websocket_client.html in your browser"
    echo "   Or: python -m http.server 8000 && open http://localhost:8000/websocket_client.html"
    echo ""
    
    echo "🐍 Python Test Client"
    echo "   Command: python test_websocket.py"
    echo ""
    
    echo "📡 REST API"
    echo "   TTS: http://localhost:8080/synthesize?text=...&voice=..."
    echo "   STT: curl -X POST -F audio=@file.wav http://localhost:8080/transcribe"
    echo ""
    
    echo "📚 API Documentation"
    echo "   WebSocket: Read WEBSOCKET_API.md"
    echo "   Structure: Read STRUCTURE_GUIDE.md"
    echo ""
    
    echo -e "${BLUE}Test Commands:${NC}"
    echo ""
    echo "# Test TTS (REST)"
    echo "curl 'http://localhost:8080/synthesize?text=Xin+chào&voice=banmai' -o output.wav"
    echo ""
    
    echo "# List voices"
    echo "curl http://localhost:8080/voices"
    echo ""
    
    echo "# Health check"
    echo "curl http://localhost:8080/health"
    echo ""
    
    echo -e "${GREEN}✓ All services ready!${NC}"
else
    echo -e "${YELLOW}⚠ Containers not ready yet. Check logs:${NC}"
    echo "   docker logs tritonserver"
    echo "   docker logs tts-api"
fi
