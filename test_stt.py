"""
Test Speech-to-Text functionality
"""
import wave
import numpy as np
from pathlib import Path
from stt_client import STTClient

def create_test_audio():
    """Create a simple test audio file (silence for testing structure)"""
    sample_rate = 16000
    duration = 3  # seconds
    
    # Generate test signal (silence for now, in production use real audio)
    samples = np.zeros(sample_rate * duration, dtype=np.float32)
    
    # Convert to int16
    audio_int16 = (samples * 32767).astype(np.int16)
    
    # Save
    output_file = "test_stt_audio.wav"
    with wave.open(output_file, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())
    
    return output_file

def test_stt():
    """Test STT models"""
    print("\n" + "="*70)
    print("Speech-to-Text Test")
    print("="*70)
    
    # Check if models exist
    models_dir = Path(__file__).parent / "models" / "stt"
    
    int8_model = models_dir / "sherpa-onnx-zipformer-vi-int8"
    full_model = models_dir / "sherpa-onnx-zipformer-vi"
    
    if not int8_model.exists() and not full_model.exists():
        print("\n⚠ STT models not found!")
        print(f"Expected location: {models_dir}")
        print("\nPlease run: python download_stt_models.py")
        return
    
    # List available test audio files
    test_files = list(Path(__file__).parent.glob("*.wav"))
    
    if not test_files:
        print("\n⚠ No WAV files found for testing")
        print("\nTo test STT, you need audio files. You can:")
        print("  1. Record audio using Windows Voice Recorder (save as WAV)")
        print("  2. Use the TTS API to generate test audio")
        print("  3. Download Vietnamese audio samples")
        print("\nGenerating test audio structure...")
        test_file = create_test_audio()
        print(f"✓ Created: {test_file} (silence, for testing only)")
        test_files = [Path(test_file)]
    
    print(f"\nFound {len(test_files)} audio file(s) to test:")
    for f in test_files:
        size = f.stat().st_size
        print(f"  - {f.name} ({size:,} bytes)")
    
    # Test each model
    for use_int8, model_name in [(True, "INT8"), (False, "Full Precision")]:
        model_dir = int8_model if use_int8 else full_model
        
        if not model_dir.exists():
            print(f"\n⚠ Skipping {model_name} model (not downloaded)")
            continue
        
        print(f"\n{'='*70}")
        print(f"Testing {model_name} Model")
        print(f"{'='*70}")
        
        try:
            client = STTClient(use_int8=use_int8)
            
            for audio_file in test_files[:3]:  # Test first 3 files
                print(f"\nTranscribing: {audio_file.name}")
                print("-"*70)
                
                # Get audio info
                with wave.open(str(audio_file), 'rb') as wf:
                    duration = wf.getnframes() / wf.getframerate()
                    print(f"Duration: {duration:.2f}s")
                
                # Transcribe
                text = client.transcribe_file(str(audio_file))
                
                print(f"Result: '{text}'")
                
                if not text:
                    print("⚠ No transcription (silence or not recognized)")
                else:
                    print(f"✓ Transcribed {len(text)} characters")
        
        except Exception as e:
            print(f"✗ Error testing {model_name} model: {e}")
    
    print("\n" + "="*70)
    print("Test completed!")
    print("="*70)
    
    print("\nNext steps:")
    print("  1. Test with real Vietnamese audio recordings")
    print("  2. Compare INT8 vs Full Precision accuracy")
    print("  3. Integrate STT into your pipeline")
    print("  4. Add STT endpoint to FastAPI (tts_api.py)")

if __name__ == "__main__":
    test_stt()
