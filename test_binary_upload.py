#!/usr/bin/env python3
import requests
import json

api_url = 'http://localhost:8080/transcribe-raw'

print("Testing raw binary upload (bypass multipart)...")
with open("01MX00894434.wav", 'rb') as f:
    file_data = f.read()

print(f"File size: {len(file_data) / (1024*1024):.1f}MB")

# Gửi raw binary body
try:
    headers = {'Content-Type': 'application/octet-stream'}
    response = requests.post(api_url, data=file_data, headers=headers, timeout=300)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Success!")
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Failed: {e}")
