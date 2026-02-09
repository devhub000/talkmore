#!/usr/bin/env python3
import requests
import time
import sys

file_path = '01MX00894434.wav'
api_url = 'http://localhost:8080/transcribe'

print('='*70)
print('🎤 Upload & Transcribe Test')
print('='*70)

try:
    print(f'📤 Uploading {file_path}...')
    start = time.time()
    
    with open(file_path, 'rb') as f:
        files = {'audio': f}
        try:
            response = requests.post(api_url, files=files, timeout=600)
            elapsed = time.time() - start
            
            print(f'Response status: {response.status_code}')
            print(f'Response time: {elapsed:.1f}s')
            print(f'Response length: {len(response.text)} chars')
            
            if response.status_code == 200:
                result = response.json()
                print(f'✅ Success')
                print()
                print(f'📊 Results:')
                duration = result.get('duration', 0)
                file_size = result.get('file_size_mb', 0)
                proc_time = result.get('processing_time', 0)
                model = result.get('model', 'unknown')
                text = result.get('text', '')
                
                print(f'  Duration: {duration:.1f}s')
                print(f'  File size: {file_size:.2f} MB')
                print(f'  Processing time: {proc_time:.1f}s')
                print(f'  Model: {model}')
                print()
                print(f'📝 Text ({len(text)} chars):')
                preview = text[:200]
                print(f'  {preview}...' if len(text) > 200 else f'  {preview}')
            else:
                print(f'❌ Error {response.status_code}')
                print('Response:')
                print(response.text)
        except requests.exceptions.ConnectionError as e:
            print(f'❌ Connection Error: {e}')
            print('API may have crashed. Check Docker logs.')
        except requests.exceptions.Timeout as e:
            print(f'⏱️ Timeout after 600s: {e}')
        except Exception as e:
            print(f'❌ Request failed: {type(e).__name__}: {e}')
except Exception as e:
    print(f'❌ Failed: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
