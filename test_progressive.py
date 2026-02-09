#!/usr/bin/env python3
import requests

test_files = [
    ("test_output.wav", 51988),
    ("test_stt_audio.wav", 610580),
    ("tts_websocket_output.wav", 102676),
    ("01MX00894434.wav", 8167502),
]

api_url = 'http://localhost:8080/transcribe'

for filename, size in test_files:
    print(f"\n{'='*60}")
    print(f"Testing: {filename} ({size/1024:.1f}KB)")
    print('='*60)
    try:
        with open(filename, 'rb') as f:
            files = {'audio': f}
            response = requests.post(api_url, files=files, timeout=120)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"  Duration: {data.get('duration'):.1f}s")
            print(f"  Processing: {data.get('processing_time'):.1f}s")
            text = data.get('text', '')[:100]
            print(f"  Text: {text}...")
        else:
            print(f"❌ Error: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Exception: {e}")
