#!/usr/bin/env python3
"""
Concurrent WebSocket Connection Test
Tests if multiple simultaneous connections return correct data
"""
import asyncio
import websockets
import json
import base64
from pathlib import Path
import random

async def test_single_tts_client(client_id, text, voice):
    """Single TTS client connection"""
    try:
        async with websockets.connect('ws://localhost:8080/ws/tts') as ws:
            request = {
                "text": text,
                "voice": voice,
                "speed": 1.5
            }
            
            print(f"  [Client {client_id}] Sending: {text[:30]}... ({voice})")
            await ws.send(json.dumps(request))
            
            response = json.loads(await ws.recv())
            
            if response.get('success'):
                audio_size = len(response.get('audio', ''))
                print(f"  [Client {client_id}] ✓ Got audio: {audio_size} bytes")
                
                # Verify correct voice was used (match text)
                return {
                    "client_id": client_id,
                    "text": text,
                    "voice": voice,
                    "audio_size": audio_size,
                    "success": True
                }
            else:
                print(f"  [Client {client_id}] ✗ Error: {response.get('error')}")
                return {"client_id": client_id, "success": False}
    
    except Exception as e:
        print(f"  [Client {client_id}] ✗ Exception: {e}")
        return {"client_id": client_id, "success": False}

async def test_single_stt_client(client_id, audio_file):
    """Single STT client connection"""
    audio_file = Path(audio_file)
    if not audio_file.exists():
        print(f"  [STT Client {client_id}] ⚠ Audio file not found")
        return {"client_id": client_id, "success": False}
    
    try:
        audio_bytes = audio_file.read_bytes()
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        async with websockets.connect('ws://localhost:8080/ws/stt') as ws:
            request = {
                "audio": audio_base64,
                "sample_rate": 16000
            }
            
            print(f"  [STT Client {client_id}] Sending audio: {audio_file.name}")
            await ws.send(json.dumps(request))
            
            response = json.loads(await ws.recv())
            
            if response.get('success'):
                text = response.get('text', '')[:50]
                print(f"  [STT Client {client_id}] ✓ Got text: {text}...")
                
                return {
                    "client_id": client_id,
                    "text": response.get('text', ''),
                    "success": True
                }
            else:
                print(f"  [STT Client {client_id}] ✗ Error: {response.get('error')}")
                return {"client_id": client_id, "success": False}
    
    except Exception as e:
        print(f"  [STT Client {client_id}] ✗ Exception: {e}")
        return {"client_id": client_id, "success": False}

async def test_concurrent_tts(num_clients=5):
    """Test multiple concurrent TTS connections"""
    print("\n" + "="*70)
    print("🔄 Testing Concurrent TTS Connections")
    print("="*70)
    print(f"Creating {num_clients} concurrent TTS clients...\n")
    
    voices = ["banmai", "mattheo", "chieuthanh"]
    texts = [
        "Xin chào bạn",
        "Đây là test lần một",
        "Đây là test lần hai",
        "Kiểm tra dữ liệu",
        "Không bị nhầm lẫn"
    ]
    
    tasks = []
    for i in range(num_clients):
        text = texts[i % len(texts)]
        voice = voices[i % len(voices)]
        task = test_single_tts_client(i+1, text, voice)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    
    print(f"\nResults:")
    successful = sum(1 for r in results if r.get('success'))
    print(f"  ✓ Successful: {successful}/{num_clients}")
    print(f"  ✗ Failed: {num_clients - successful}/{num_clients}")
    
    # Check for data mixing
    print(f"\nData Integrity Check:")
    for r in results:
        if r.get('success'):
            print(f"  Client {r['client_id']}: Text='{r['text']}', Voice='{r['voice']}', Size={r['audio_size']} bytes")
    
    return successful == num_clients

async def test_concurrent_stt(num_clients=3):
    """Test multiple concurrent STT connections"""
    print("\n" + "="*70)
    print("🔄 Testing Concurrent STT Connections")
    print("="*70)
    
    audio_file = Path("test_stt_audio.wav")
    if not audio_file.exists():
        print(f"⚠ Audio file not found: {audio_file}")
        return False
    
    print(f"Creating {num_clients} concurrent STT clients...\n")
    
    tasks = []
    for i in range(num_clients):
        task = test_single_stt_client(i+1, audio_file)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    
    print(f"\nResults:")
    successful = sum(1 for r in results if r.get('success'))
    print(f"  ✓ Successful: {successful}/{num_clients}")
    print(f"  ✗ Failed: {num_clients - successful}/{num_clients}")
    
    # Check for consistency
    print(f"\nData Consistency Check:")
    texts = [r.get('text', '') for r in results if r.get('success')]
    if texts:
        first_text = texts[0]
        all_same = all(t == first_text for t in texts)
        if all_same:
            print(f"  ✓ All results are identical (correct)")
            print(f"  Result: '{first_text[:50]}...'")
        else:
            print(f"  ✗ Results differ (data mixing issue!)")
            for i, t in enumerate(texts):
                print(f"    Client {i+1}: '{t[:40]}...'")
    
    return successful == num_clients

async def test_mixed_concurrent():
    """Test concurrent TTS + STT requests"""
    print("\n" + "="*70)
    print("🔄 Testing Mixed Concurrent Connections (TTS + STT)")
    print("="*70)
    print("Creating 3 concurrent TTS + 2 concurrent STT clients...\n")
    
    tasks = []
    
    # Add TTS tasks
    for i in range(3):
        voices = ["banmai", "mattheo", "chieuthanh"]
        texts = ["Xin chào", "Kiểm tra", "Không lỗi"]
        task = test_single_tts_client(f"TTS-{i+1}", texts[i], voices[i])
        tasks.append(task)
    
    # Add STT tasks
    for i in range(2):
        task = test_single_stt_client(f"STT-{i+1}", "test_stt_audio.wav")
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    
    print(f"\nResults:")
    tts_ok = sum(1 for r in results if r.get('client_id', '').startswith('TTS') and r.get('success'))
    stt_ok = sum(1 for r in results if r.get('client_id', '').startswith('STT') and r.get('success'))
    print(f"  ✓ TTS: {tts_ok}/3")
    print(f"  ✓ STT: {stt_ok}/2")
    
    return tts_ok == 3 and stt_ok == 2

async def main():
    print("\n" + "="*70)
    print("🧪 WebSocket Concurrency Test Suite")
    print("="*70)
    
    # Run tests
    tts_ok = await test_concurrent_tts(5)
    stt_ok = await test_concurrent_stt(3)
    mixed_ok = await test_mixed_concurrent()
    
    # Summary
    print("\n" + "="*70)
    print("📊 Summary")
    print("="*70)
    print(f"TTS Concurrent Test: {'✓ PASS' if tts_ok else '✗ FAIL'}")
    print(f"STT Concurrent Test: {'✓ PASS' if stt_ok else '✗ FAIL'}")
    print(f"Mixed Test: {'✓ PASS' if mixed_ok else '✗ FAIL'}")
    print("="*70)
    
    if tts_ok and stt_ok and mixed_ok:
        print("✅ All tests passed! No data mixing detected.")
    else:
        print("❌ Some tests failed!")

if __name__ == "__main__":
    asyncio.run(main())
