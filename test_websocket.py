#!/usr/bin/env python3
"""
WebSocket client for testing TTS and STT streaming
"""
import asyncio
import websockets
import json
import base64
import sys
from pathlib import Path

async def test_tts():
    """Test TTS WebSocket streaming"""
    print("\n" + "="*60)
    print("Testing TTS WebSocket Stream")
    print("="*60)
    
    try:
        async with websockets.connect('ws://localhost:8080/ws/tts') as websocket:
            print("✓ Connected to TTS WebSocket\n")
            
            # Test request
            request = {
                "text": "Xin chào bạn. Đây là test âm thanh.",
                "voice": "banmai",
                "speed": 1.5,
                "noise_scale": 0.667,
                "noise_w": 0.8
            }
            
            print(f"→ Sending request:")
            print(f"  Text: {request['text']}")
            print(f"  Voice: {request['voice']}")
            print(f"  Speed: {request['speed']}\n")
            
            await websocket.send(json.dumps(request))
            
            # Receive response
            response_text = await websocket.recv()
            response = json.loads(response_text)
            
            if response.get('error'):
                print(f"✗ Error: {response['error']}")
            else:
                print(f"✓ Response received:")
                print(f"  Duration: {response['duration']:.3f}s")
                print(f"  Sample rate: {response['sample_rate']} Hz")
                print(f"  Audio data size: {len(response['audio'])} bytes (base64)")
                
                # Decode and save audio
                audio_bytes = base64.b64decode(response['audio'])
                output_file = Path('tts_websocket_output.wav')
                output_file.write_bytes(audio_bytes)
                print(f"  ✓ Audio saved to: {output_file}")
    
    except Exception as e:
        print(f"✗ Error: {e}")

async def test_stt():
    """Test STT WebSocket streaming"""
    print("\n" + "="*60)
    print("Testing STT WebSocket Stream")
    print("="*60)
    
    audio_file = Path('test_stt_audio.wav')
    if not audio_file.exists():
        print(f"⚠ Audio file not found: {audio_file}")
        print("  Skipping STT test")
        return
    
    try:
        async with websockets.connect('ws://localhost:8080/ws/stt') as websocket:
            print("✓ Connected to STT WebSocket\n")
            
            # Read audio file
            audio_bytes = audio_file.read_bytes()
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            # Test request
            request = {
                "audio": audio_base64,
                "sample_rate": 16000
            }
            
            print(f"→ Sending request:")
            print(f"  Audio file: {audio_file.name}")
            print(f"  Audio size: {len(audio_bytes)} bytes")
            print(f"  Sample rate: {request['sample_rate']} Hz\n")
            
            await websocket.send(json.dumps(request))
            
            # Receive response
            response_text = await websocket.recv()
            response = json.loads(response_text)
            
            if response.get('error'):
                print(f"✗ Error: {response['error']}")
            else:
                print(f"✓ Response received:")
                print(f"  Text: \"{response['text']}\"")
                print(f"  Duration: {response['duration']:.3f}s")
                print(f"  Processing time: {response['processing_time']:.3f}s")
                print(f"  Model: {response['model']}")
    
    except Exception as e:
        print(f"✗ Error: {e}")

async def main():
    """Run all tests"""
    print("\n🎤 WebSocket Streaming Test Suite")
    print(f"Server: ws://localhost:8080")
    
    await test_tts()
    await test_stt()
    
    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
