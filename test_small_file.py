#!/usr/bin/env python3
import requests
import subprocess
import time

# Generate a small 5-second WAV file
print("Generating small test WAV (5s)...")
subprocess.run([
    "ffmpeg", "-f", "lavfi", "-i", "sine=f=1000:d=5",
    "-acodec", "pcm_s16le", "-ar", "22050",
    "test_small.wav", "-y"
], capture_output=True)

api_url = 'http://localhost:8080/transcribe'

print("Uploading small file...")
with open("test_small.wav", 'rb') as f:
    files = {'audio': f}
    try:
        response = requests.post(api_url, files=files, timeout=60)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json() if response.status_code == 200 else response.text}")
    except Exception as e:
        print(f"Error: {e}")
