#!/usr/bin/env python3
"""
Simple STT Example - Based on sherpa-onnx official examples
"""
import wave
import numpy as np
import sherpa_onnx
from pathlib import Path

def read_wave(wav_file):
    """Read WAV file and return samples as float32 array"""
    with wave.open(wav_file, 'rb') as f:
        assert f.getnchannels() == 1, f"Expected mono audio, got {f.getnchannels()} channels"
        assert f.getsampwidth() == 2, f"Expected 16-bit audio, got {f.getsampwidth()} bytes"
        
        num_samples = f.getnframes()
        samples = f.readframes(num_samples)
        samples_int16 = np.frombuffer(samples, dtype=np.int16)
        samples_float32 = samples_int16.astype(np.float32) / 32768.0
        
        return samples_float32, f.getframerate()

def create_recognizer(model_dir, use_int8=True):
    """Create offline recognizer"""
    model_dir = Path(model_dir)
    
    # Find model files
    if use_int8:
        encoder = str(model_dir / "encoder-epoch-20-avg-10.int8.onnx")
        decoder = str(model_dir / "decoder-epoch-20-avg-10.int8.onnx")
        joiner = str(model_dir / "joiner-epoch-20-avg-10.int8.onnx")
    else:
        encoder = str(model_dir / "encoder-epoch-20-avg-10.onnx")
        decoder = str(model_dir / "decoder-epoch-20-avg-10.onnx")
        joiner = str(model_dir / "joiner-epoch-20-avg-10.onnx")
    
    tokens = str(model_dir / "config.json")
    
    print(f"Loading model from: {model_dir}")
    print(f"  Encoder: {Path(encoder).name}")
    print(f"  Decoder: {Path(decoder).name}")
    print(f"  Joiner: {Path(joiner).name}")
    print(f"  Tokens: {Path(tokens).name}")
    
    # Create recognizer
    recognizer = sherpa_onnx.OfflineRecognizer.from_transducer(
        tokens=tokens,
        encoder=encoder,
        decoder=decoder,
        joiner=joiner,
        num_threads=2,
        sample_rate=16000,
        feature_dim=80,
        decoding_method="greedy_search",
    )
    
    print("✓ Model loaded successfully\n")
    return recognizer

def transcribe(recognizer, wav_file):
    """Transcribe audio file"""
    print(f"Transcribing: {wav_file}")
    
    # Read audio
    samples, sample_rate = read_wave(wav_file)
    duration = len(samples) / sample_rate
    print(f"  Duration: {duration:.2f}s, Sample rate: {sample_rate}Hz")
    
    # Create stream and decode
    stream = recognizer.create_stream()
    stream.accept_waveform(sample_rate, samples)
    recognizer.decode_stream(stream)
    
    # Get result
    text = stream.result.text
    print(f"  Result: '{text}'")
    
    return text

def main():
    """Main function"""
    print("\n" + "="*70)
    print("Simple Speech-to-Text Example")
    print("="*70 + "\n")
    
    # Model paths
    base_dir = Path(__file__).parent / "models" / "stt"
    int8_dir = base_dir / "sherpa-onnx-zipformer-vi-int8"
    full_dir = base_dir / "sherpa-onnx-zipformer-vi"
    
    # Check if models exist
    if not int8_dir.exists() and not full_dir.exists():
        print("⚠ Models not found!")
        print(f"Expected location: {base_dir}")
        print("\nPlease run: python download_stt_models.py")
        return
    
    # Use INT8 model if available
    model_dir = int8_dir if int8_dir.exists() else full_dir
    use_int8 = int8_dir.exists()
    
    # Create recognizer
    recognizer = create_recognizer(model_dir, use_int8=use_int8)
    
    # Find WAV files to test
    wav_files = list(Path.cwd().glob("*.wav"))
    
    if not wav_files:
        print("⚠ No WAV files found in current directory")
        print("\nTo test, you can:")
        print("  1. Record audio with Windows Voice Recorder (save as WAV)")
        print("  2. Generate audio with TTS: python -c \"from tts_client_api import synthesize_speech; synthesize_speech('Xin chào Việt Nam', output_file='test.wav', triton_url='localhost:8000')\"")
        return
    
    print(f"Found {len(wav_files)} WAV file(s):\n")
    
    # Transcribe each file
    for wav_file in wav_files[:5]:  # Test first 5 files
        try:
            transcribe(recognizer, str(wav_file))
            print()
        except Exception as e:
            print(f"  ✗ Error: {e}\n")
    
    print("="*70)
    print("Transcription completed!")
    print("="*70)

if __name__ == "__main__":
    main()
