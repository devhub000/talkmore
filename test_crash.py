#!/usr/bin/env python3
import requests
import time

print("Testing large file upload...")
try:
    with open("01MX00894434.wav", 'rb') as f:
        files = {'audio': f}
        response = requests.post('http://localhost:8080/transcribe', files=files, timeout=300)
        print(f"Response: {response.status_code}")
        if response.status_code == 200:
            print("✅ Success!")
            data = response.json()
            print(f"Duration: {data.get('duration')}s")
            print(f"Processing: {data.get('processing_time')}s")
        else:
            print(f"Error: {response.text[:200]}")
except Exception as e:
    print(f"Request failed: {e}")

print("\nChecking if API is still alive...")
time.sleep(1)
try:
    r = requests.get('http://localhost:8080/health', timeout=5)
    print(f"Health check: {r.status_code}")
except Exception as e:
    print(f"Health check failed: {e}")
