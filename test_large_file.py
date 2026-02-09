#!/usr/bin/env python3
"""
Test large audio file transcription via REST API
Tests ability to handle 4-5 minute audio files (20-30MB)
"""
import requests
import os
from pathlib import Path
import time

API_URL = "http://localhost:8080"

def test_large_audio_file():
    """Test uploading and transcribing large audio file"""
    audio_file = Path("test_stt_audio.wav")
    
    if not audio_file.exists():
        print(f"❌ Audio file not found: {audio_file}")
        return False
    
    file_size_mb = audio_file.stat().st_size / (1024 * 1024)
    print(f"\n{'='*70}")
    print(f"🎤 Large Audio File Transcription Test")
    print(f"{'='*70}")
    print(f"File: {audio_file.name}")
    print(f"Size: {file_size_mb:.2f} MB")
    print(f"API: {API_URL}/transcribe")
    print()
    
    try:
        print("📤 Uploading audio file...")
        upload_start = time.time()
        
        with open(audio_file, 'rb') as f:
            files = {'audio': f}
            response = requests.post(
                f"{API_URL}/transcribe",
                files=files,
                timeout=600  # 10 minutes timeout for very long audio
            )
        
        upload_time = time.time() - upload_start
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Upload completed in {upload_time:.1f}s")
            print()
            print(f"📊 Results:")
            print(f"  Duration: {result['duration']:.1f}s ({result['duration']/60:.1f} minutes)")
            print(f"  File size: {result['file_size_mb']:.2f} MB")
            print(f"  Processing time: {result['processing_time']:.1f}s")
            print(f"  Model: {result['model']}")
            print()
            print(f"📝 Transcribed text ({len(result['text'])} chars):")
            print(f"  {result['text'][:100]}..." if len(result['text']) > 100 else f"  {result['text']}")
            print()
            print(f"{'='*70}")
            print(f"✅ Test PASSED - Large file handled successfully!")
            print(f"{'='*70}\n")
            return True
        
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Details: {response.text}")
            return False
    
    except requests.exceptions.Timeout:
        print(f"❌ Request timeout - file too large or processing took too long")
        return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_api_limits():
    """Test API configuration for large files"""
    print(f"\n{'='*70}")
    print(f"🔍 API Configuration Check")
    print(f"{'='*70}")
    
    try:
        response = requests.get(f"{API_URL}/info", timeout=5)
        if response.status_code == 200:
            info = response.json()
            print("✅ API is responding")
            print(f"  Service: {info['service']}")
            print(f"  Version: {info['version']}")
            
            # Check if STT is available
            health = requests.get(f"{API_URL}/health", timeout=5).json()
            print(f"  STT Status: Available ✓" if health.get('status') == 'healthy' else f"  STT Status: Not available")
            return True
        else:
            print(f"❌ API not responding properly")
            return False
    
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

if __name__ == "__main__":
    print("\n🧪 Large Audio File Test Suite\n")
    
    # Check API first
    if not test_api_limits():
        print("⚠ API not ready. Make sure Docker containers are running.")
        exit(1)
    
    # Test large file
    success = test_large_audio_file()
    
    exit(0 if success else 1)
