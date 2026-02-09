# API Integration Examples

Complete code examples for integrating DevHub Vietnamese TTS API.

## Table of Contents

- [Python](#python)
- [JavaScript/Node.js](#javascriptnodejs)
- [PHP](#php)
- [Java](#java)
- [C#/.NET](#cnet)
- [Go](#go)
- [Ruby](#ruby)
- [cURL](#curl)

---

## Python

### Simple GET Request

```python
import requests

# Simple synthesis
response = requests.get(
    "http://localhost:8080/synthesize",
    params={
        "text": "Xin chào Việt Nam",
        "voice": "banmai",
        "speed": 1.5
    }
)

# Save audio
with open("output.wav", "wb") as f:
    f.write(response.content)

print("Audio saved to output.wav")
```

### POST Request with Error Handling

```python
import requests
from pathlib import Path

class TTSClient:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
    
    def synthesize(self, text, voice="banmai", speed=1.0, output_file="output.wav"):
        """Synthesize speech from text"""
        try:
            response = requests.post(
                f"{self.base_url}/synthesize",
                json={
                    "text": text,
                    "voice": voice,
                    "speed": speed
                },
                timeout=30
            )
            response.raise_for_status()
            
            # Save audio
            with open(output_file, "wb") as f:
                f.write(response.content)
            
            file_size = len(response.content)
            print(f"✓ Generated: {output_file} ({file_size:,} bytes)")
            return output_file
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error: {e}")
            return None
    
    def get_voices(self):
        """Get list of available voices"""
        response = requests.get(f"{self.base_url}/voices")
        return response.json()
    
    def health_check(self):
        """Check service health"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()

# Usage
client = TTSClient()

# Check health
health = client.health_check()
print(f"Service health: {health['status']}")
print(f"Available voices: {health['available_voices']}")

# Get voices
voices = client.get_voices()
print(f"\nVoices: {list(voices['voices'].keys())}")

# Synthesize speech
client.synthesize(
    text="Chào mừng bạn đến với DevHub TTS",
    voice="lacphi",
    speed=1.5,
    output_file="welcome.wav"
)
```

### Async Python (FastAPI Integration)

```python
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

app = FastAPI()
TTS_API = "http://localhost:8080"

@app.get("/text-to-speech")
async def text_to_speech(text: str, voice: str = "banmai", speed: float = 1.0):
    """Convert text to speech and return audio file"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{TTS_API}/synthesize",
                json={"text": text, "voice": voice, "speed": speed},
                timeout=30.0
            )
            response.raise_for_status()
            
            # Save temporary file
            temp_file = f"temp_{hash(text)}.wav"
            with open(temp_file, "wb") as f:
                f.write(response.content)
            
            return FileResponse(
                temp_file,
                media_type="audio/wav",
                filename="speech.wav"
            )
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=str(e))
```

---

## JavaScript/Node.js

### Using fetch (Node.js 18+)

```javascript
const fs = require('fs');

async function synthesizeSpeech(text, voice = 'banmai', speed = 1.0) {
  try {
    const response = await fetch('http://localhost:8080/synthesize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text, voice, speed }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const arrayBuffer = await response.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    
    fs.writeFileSync('output.wav', buffer);
    console.log(`✓ Audio saved: output.wav (${buffer.length} bytes)`);
    
    return 'output.wav';
  } catch (error) {
    console.error('✗ Error:', error.message);
    return null;
  }
}

// Usage
synthesizeSpeech('Xin chào Việt Nam', 'banmai', 1.5);
```

### Using axios (Node.js)

```javascript
const axios = require('axios');
const fs = require('fs');

class TTSClient {
  constructor(baseUrl = 'http://localhost:8080') {
    this.baseUrl = baseUrl;
  }

  async synthesize(text, voice = 'banmai', speed = 1.0, outputFile = 'output.wav') {
    try {
      const response = await axios.post(
        `${this.baseUrl}/synthesize`,
        { text, voice, speed },
        { responseType: 'arraybuffer', timeout: 30000 }
      );

      fs.writeFileSync(outputFile, response.data);
      console.log(`✓ Generated: ${outputFile} (${response.data.length} bytes)`);
      return outputFile;
    } catch (error) {
      console.error('✗ Error:', error.message);
      return null;
    }
  }

  async getVoices() {
    const response = await axios.get(`${this.baseUrl}/voices`);
    return response.data;
  }

  async healthCheck() {
    const response = await axios.get(`${this.baseUrl}/health`);
    return response.data;
  }
}

// Usage
const client = new TTSClient();

(async () => {
  // Health check
  const health = await client.healthCheck();
  console.log('Service status:', health.status);

  // Synthesize
  await client.synthesize(
    'Chào mừng bạn đến với DevHub TTS',
    'lacphi',
    1.5,
    'welcome.wav'
  );
})();
```

### Browser JavaScript

```html
<!DOCTYPE html>
<html>
<head>
    <title>Vietnamese TTS Demo</title>
</head>
<body>
    <h1>Vietnamese Text-to-Speech</h1>
    
    <textarea id="text" rows="4" cols="50" placeholder="Enter Vietnamese text...">
Xin chào Việt Nam
    </textarea><br>
    
    <select id="voice">
        <option value="banmai">Ban Mai (Female)</option>
        <option value="lacphi">Lạc Phi (Female)</option>
        <option value="deepman3909">Deep Man (Male)</option>
    </select>
    
    <input type="range" id="speed" min="0.5" max="2.0" step="0.1" value="1.0">
    <span id="speedLabel">Speed: 1.0x</span><br>
    
    <button onclick="synthesize()">Generate Speech</button>
    
    <div id="status"></div>
    <audio id="player" controls></audio>

    <script>
        const speedSlider = document.getElementById('speed');
        const speedLabel = document.getElementById('speedLabel');
        
        speedSlider.addEventListener('input', function() {
            speedLabel.textContent = `Speed: ${this.value}x`;
        });

        async function synthesize() {
            const text = document.getElementById('text').value;
            const voice = document.getElementById('voice').value;
            const speed = parseFloat(document.getElementById('speed').value);
            const status = document.getElementById('status');
            const player = document.getElementById('player');

            status.textContent = 'Generating...';

            try {
                const response = await fetch('http://localhost:8080/synthesize', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text, voice, speed })
                });

                if (!response.ok) throw new Error(`HTTP ${response.status}`);

                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                
                player.src = url;
                status.textContent = '✓ Generated successfully!';
                player.play();
            } catch (error) {
                status.textContent = `✗ Error: ${error.message}`;
            }
        }
    </script>
</body>
</html>
```

---

## PHP

### Simple cURL Request

```php
<?php

function synthesizeSpeech($text, $voice = 'banmai', $speed = 1.0, $outputFile = 'output.wav') {
    $url = 'http://localhost:8080/synthesize';
    
    $data = json_encode([
        'text' => $text,
        'voice' => $voice,
        'speed' => $speed
    ]);
    
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($httpCode == 200 && $response !== false) {
        file_put_contents($outputFile, $response);
        echo "✓ Audio saved: $outputFile (" . strlen($response) . " bytes)\n";
        return $outputFile;
    } else {
        echo "✗ Error: HTTP $httpCode\n";
        return null;
    }
}

// Usage
synthesizeSpeech('Xin chào Việt Nam', 'banmai', 1.5, 'output.wav');

?>
```

### PHP Class with Error Handling

```php
<?php

class TTSClient {
    private $baseUrl;
    
    public function __construct($baseUrl = 'http://localhost:8080') {
        $this->baseUrl = $baseUrl;
    }
    
    public function synthesize($text, $voice = 'banmai', $speed = 1.0, $outputFile = 'output.wav') {
        $url = $this->baseUrl . '/synthesize';
        
        $data = json_encode([
            'text' => $text,
            'voice' => $voice,
            'speed' => $speed
        ]);
        
        $ch = curl_init($url);
        curl_setopt_array($ch, [
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => $data,
            CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 30
        ]);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $error = curl_error($ch);
        curl_close($ch);
        
        if ($httpCode == 200 && $response !== false) {
            file_put_contents($outputFile, $response);
            return [
                'success' => true,
                'file' => $outputFile,
                'size' => strlen($response)
            ];
        } else {
            return [
                'success' => false,
                'error' => $error ?: "HTTP $httpCode"
            ];
        }
    }
    
    public function getVoices() {
        $ch = curl_init($this->baseUrl . '/voices');
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        $response = curl_exec($ch);
        curl_close($ch);
        
        return json_decode($response, true);
    }
    
    public function healthCheck() {
        $ch = curl_init($this->baseUrl . '/health');
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        $response = curl_exec($ch);
        curl_close($ch);
        
        return json_decode($response, true);
    }
}

// Usage
$client = new TTSClient();

$health = $client->healthCheck();
echo "Service status: " . $health['status'] . "\n";

$result = $client->synthesize('Chào mừng bạn', 'lacphi', 1.5, 'welcome.wav');
if ($result['success']) {
    echo "✓ Generated: {$result['file']} ({$result['size']} bytes)\n";
} else {
    echo "✗ Error: {$result['error']}\n";
}

?>
```

---

## Java

### Using HttpURLConnection

```java
import java.io.*;
import java.net.*;
import java.nio.file.*;

public class TTSClient {
    private final String baseUrl;
    
    public TTSClient(String baseUrl) {
        this.baseUrl = baseUrl;
    }
    
    public String synthesize(String text, String voice, double speed, String outputFile) 
            throws IOException {
        URL url = new URL(baseUrl + "/synthesize");
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        
        try {
            // Setup request
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Content-Type", "application/json");
            conn.setDoOutput(true);
            conn.setConnectTimeout(30000);
            conn.setReadTimeout(30000);
            
            // Send JSON
            String json = String.format(
                "{\"text\":\"%s\",\"voice\":\"%s\",\"speed\":%.1f}",
                text, voice, speed
            );
            
            try (OutputStream os = conn.getOutputStream()) {
                os.write(json.getBytes("UTF-8"));
            }
            
            // Read response
            if (conn.getResponseCode() == 200) {
                try (InputStream is = conn.getInputStream()) {
                    Files.copy(is, Paths.get(outputFile), StandardCopyOption.REPLACE_EXISTING);
                }
                
                long fileSize = Files.size(Paths.get(outputFile));
                System.out.println("✓ Generated: " + outputFile + " (" + fileSize + " bytes)");
                return outputFile;
            } else {
                throw new IOException("HTTP " + conn.getResponseCode());
            }
        } finally {
            conn.disconnect();
        }
    }
    
    public static void main(String[] args) {
        try {
            TTSClient client = new TTSClient("http://localhost:8080");
            client.synthesize("Xin chào Việt Nam", "banmai", 1.5, "output.wav");
        } catch (IOException e) {
            System.err.println("✗ Error: " + e.getMessage());
        }
    }
}
```

---

## C#/.NET

### Using HttpClient

```csharp
using System;
using System.IO;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

public class TTSClient
{
    private readonly HttpClient _httpClient;
    private readonly string _baseUrl;
    
    public TTSClient(string baseUrl = "http://localhost:8080")
    {
        _baseUrl = baseUrl;
        _httpClient = new HttpClient { Timeout = TimeSpan.FromSeconds(30) };
    }
    
    public async Task<string> SynthesizeAsync(string text, string voice = "banmai", 
                                              double speed = 1.0, string outputFile = "output.wav")
    {
        try
        {
            var request = new
            {
                text = text,
                voice = voice,
                speed = speed
            };
            
            var json = JsonSerializer.Serialize(request);
            var content = new StringContent(json, Encoding.UTF8, "application/json");
            
            var response = await _httpClient.PostAsync($"{_baseUrl}/synthesize", content);
            response.EnsureSuccessStatusCode();
            
            var audioData = await response.Content.ReadAsByteArrayAsync();
            await File.WriteAllBytesAsync(outputFile, audioData);
            
            Console.WriteLine($"✓ Generated: {outputFile} ({audioData.Length:N0} bytes)");
            return outputFile;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"✗ Error: {ex.Message}");
            return null;
        }
    }
    
    public static async Task Main(string[] args)
    {
        var client = new TTSClient();
        await client.SynthesizeAsync("Xin chào Việt Nam", "banmai", 1.5, "output.wav");
    }
}
```

---

## Go

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io"
    "net/http"
    "os"
    "time"
)

type TTSRequest struct {
    Text  string  `json:"text"`
    Voice string  `json:"voice"`
    Speed float64 `json:"speed"`
}

type TTSClient struct {
    BaseURL string
    Client  *http.Client
}

func NewTTSClient(baseURL string) *TTSClient {
    return &TTSClient{
        BaseURL: baseURL,
        Client:  &http.Client{Timeout: 30 * time.Second},
    }
}

func (c *TTSClient) Synthesize(text, voice string, speed float64, outputFile string) error {
    request := TTSRequest{
        Text:  text,
        Voice: voice,
        Speed: speed,
    }
    
    jsonData, err := json.Marshal(request)
    if err != nil {
        return err
    }
    
    resp, err := c.Client.Post(
        c.BaseURL+"/synthesize",
        "application/json",
        bytes.NewBuffer(jsonData),
    )
    if err != nil {
        return err
    }
    defer resp.Body.Close()
    
    if resp.StatusCode != http.StatusOK {
        return fmt.Errorf("HTTP %d", resp.StatusCode)
    }
    
    file, err := os.Create(outputFile)
    if err != nil {
        return err
    }
    defer file.Close()
    
    size, err := io.Copy(file, resp.Body)
    if err != nil {
        return err
    }
    
    fmt.Printf("✓ Generated: %s (%d bytes)\n", outputFile, size)
    return nil
}

func main() {
    client := NewTTSClient("http://localhost:8080")
    
    err := client.Synthesize("Xin chào Việt Nam", "banmai", 1.5, "output.wav")
    if err != nil {
        fmt.Printf("✗ Error: %v\n", err)
    }
}
```

---

## Ruby

```ruby
require 'net/http'
require 'json'
require 'uri'

class TTSClient
  def initialize(base_url = 'http://localhost:8080')
    @base_url = base_url
  end
  
  def synthesize(text, voice: 'banmai', speed: 1.0, output_file: 'output.wav')
    uri = URI("#{@base_url}/synthesize")
    
    request = Net::HTTP::Post.new(uri)
    request['Content-Type'] = 'application/json'
    request.body = {
      text: text,
      voice: voice,
      speed: speed
    }.to_json
    
    response = Net::HTTP.start(uri.hostname, uri.port, read_timeout: 30) do |http|
      http.request(request)
    end
    
    if response.code == '200'
      File.binwrite(output_file, response.body)
      puts "✓ Generated: #{output_file} (#{response.body.length} bytes)"
      output_file
    else
      puts "✗ Error: HTTP #{response.code}"
      nil
    end
  rescue StandardError => e
    puts "✗ Error: #{e.message}"
    nil
  end
end

# Usage
client = TTSClient.new
client.synthesize('Xin chào Việt Nam', voice: 'banmai', speed: 1.5, output_file: 'output.wav')
```

---

## cURL

### Simple GET Request

```bash
curl "http://localhost:8080/synthesize?text=Xin%20chào&voice=banmai&speed=1.0" \
  -o output.wav
```

### POST Request with JSON

```bash
curl -X POST http://localhost:8080/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text":"Xin chào Việt Nam","voice":"banmai","speed":1.5}' \
  -o output.wav
```

### Health Check

```bash
curl http://localhost:8080/health
```

### Get Available Voices

```bash
curl http://localhost:8080/voices | jq
```

### Complete Script

```bash
#!/bin/bash

API_URL="http://localhost:8080"

# Health check
echo "Checking service health..."
health=$(curl -s "$API_URL/health")
echo "$health" | jq

# Get voices
echo -e "\nAvailable voices:"
curl -s "$API_URL/voices" | jq -r '.voices | keys[]'

# Synthesize speech
echo -e "\nGenerating speech..."
curl -X POST "$API_URL/synthesize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Chào mừng bạn đến với DevHub Vietnamese TTS",
    "voice": "banmai",
    "speed": 1.5
  }' \
  -o welcome.wav

if [ -f welcome.wav ]; then
  size=$(stat -f%z welcome.wav 2>/dev/null || stat -c%s welcome.wav)
  echo "✓ Generated: welcome.wav ($size bytes)"
else
  echo "✗ Failed to generate audio"
fi
```

---

## Error Handling Best Practices

All clients should handle:

1. **Network Errors**: Connection timeouts, DNS failures
2. **HTTP Errors**: 4xx (client errors), 5xx (server errors)
3. **Timeouts**: Long synthesis times for large text
4. **File I/O Errors**: Disk space, permissions

Example error handling pattern:

```python
try:
    result = client.synthesize(text, voice, speed)
    if result:
        # Success
        play_audio(result)
except requests.exceptions.Timeout:
    print("Request timed out - try shorter text or increase timeout")
except requests.exceptions.ConnectionError:
    print("Cannot connect to TTS service - is it running?")
except requests.exceptions.HTTPError as e:
    print(f"HTTP error: {e.response.status_code}")
except IOError as e:
    print(f"File error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Rate Limiting

For production use, implement client-side rate limiting:

```python
import time
from collections import deque

class RateLimitedTTSClient:
    def __init__(self, max_requests=10, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
    
    def synthesize(self, text, voice='banmai', speed=1.0):
        # Remove old requests outside time window
        now = time.time()
        while self.requests and now - self.requests[0] > self.time_window:
            self.requests.popleft()
        
        # Check rate limit
        if len(self.requests) >= self.max_requests:
            wait_time = self.time_window - (now - self.requests[0])
            raise Exception(f"Rate limit exceeded. Wait {wait_time:.1f}s")
        
        # Make request
        self.requests.append(now)
        # ... actual synthesis code ...
```

---

For more examples and support, visit:
- GitHub: https://github.com/devhub/vietnamese-tts
- Documentation: https://docs.devhub.ai.vn/tts
- Support: support@devhub.ai.vn
