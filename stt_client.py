"""
Speech-to-Text Client using Sherpa-ONNX
Vietnamese ASR with zipformer models
"""
import os
from pathlib import Path
import numpy as np
import wave
import sherpa_onnx

class STTClient:
    """Client for Speech-to-Text conversion"""
    
    def __init__(self, model_path=None, use_int8=True):
        """
        Initialize STT client
        
        Args:
            model_path: Path to model directory (auto-detect if None)
            use_int8: Use INT8 quantized model (faster) or full precision (more accurate)
        """
        if model_path is None:
            base_dir = Path(__file__).parent / "models" / "stt"
            model_name = "sherpa-onnx-zipformer-vi-int8" if use_int8 else "sherpa-onnx-zipformer-vi"
            model_path = base_dir / model_name
        
        self.model_path = Path(model_path)
        self.use_int8 = use_int8
        
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {self.model_path}\n"
                f"Please run: python download_stt_models.py"
            )
        
        print(f"Loading STT model from: {self.model_path}")
        self._init_recognizer()
    
    def _init_recognizer(self):
        """Initialize the recognizer"""
        # Find model files
        encoder_path = None
        decoder_path = None
        joiner_path = None
        tokens_path = None
        
        for file in self.model_path.glob("*.onnx"):
            name = file.name.lower()
            if "encoder" in name:
                encoder_path = str(file)
            elif "decoder" in name:
                decoder_path = str(file)
            elif "joiner" in name:
                joiner_path = str(file)
        
        # Check for config.json (contains tokens) or tokens.txt
        config_json = self.model_path / "config.json"
        tokens_txt = self.model_path / "tokens.txt"
        
        if config_json.exists():
            tokens_path = str(config_json)
        elif tokens_txt.exists():
            tokens_path = str(tokens_txt)
        
        if not all([encoder_path, decoder_path, joiner_path, tokens_path]):
            raise FileNotFoundError(
                f"Missing model files in {self.model_path}\n"
                f"Required: encoder.onnx, decoder.onnx, joiner.onnx, tokens (config.json or tokens.txt)"
            )
        
        print(f"  Encoder: {Path(encoder_path).name}")
        print(f"  Decoder: {Path(decoder_path).name}")
        print(f"  Joiner: {Path(joiner_path).name}")
        print(f"  Tokens: {Path(tokens_path).name}")
        
        # Create recognizer config using OfflineRecognizer (not Online)
        recognizer_config = sherpa_onnx.OfflineRecognizerConfig(
            model_config=sherpa_onnx.OfflineModelConfig(
                transducer=sherpa_onnx.OfflineTransducerModelConfig(
                    encoder_filename=encoder_path,
                    decoder_filename=decoder_path,
                    joiner_filename=joiner_path,
                ),
                tokens=tokens_path,
                num_threads=2,
                debug=False,
            )
        )
        
        self.recognizer = sherpa_onnx.OfflineRecognizer(recognizer_config)
        print("✓ STT model loaded successfully")
    
    def transcribe_file(self, audio_file):
        """
        Transcribe audio file to text
        
        Args:
            audio_file: Path to WAV audio file (16kHz recommended)
        
        Returns:
            str: Transcribed text
        """
        audio_file = Path(audio_file)
        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file}")
        
        # Read audio
        with wave.open(str(audio_file), 'rb') as wf:
            sample_rate = wf.getframerate()
            num_channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            
            # Read all frames
            audio_data = wf.readframes(wf.getnframes())
            
            # Convert to float32
            if sample_width == 2:
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                audio_array = audio_array.astype(np.float32) / 32768.0
            else:
                raise ValueError(f"Unsupported sample width: {sample_width}")
            
            # Convert stereo to mono if needed
            if num_channels == 2:
                audio_array = audio_array.reshape(-1, 2).mean(axis=1)
        
        # Create stream and decode
        stream = self.recognizer.create_stream()
        stream.accept_waveform(sample_rate, audio_array)
        
        self.recognizer.decode_stream(stream)
        result = stream.result
        
        return result.text
    
    def transcribe_audio_data(self, audio_data, sample_rate=16000):
        """
        Transcribe audio data (numpy array) to text
        
        Args:
            audio_data: numpy array of audio samples (float32, range -1 to 1)
            sample_rate: Sample rate of audio
        
        Returns:
            str: Transcribed text
        """
        # Create stream and decode
        stream = self.recognizer.create_stream()
        stream.accept_waveform(sample_rate, audio_data)
        
        self.recognizer.decode_stream(stream)
        result = stream.result
        
        return result.text


def transcribe(audio_file, use_int8=True):
    """
    Convenience function to transcribe audio file
    
    Args:
        audio_file: Path to audio file
        use_int8: Use INT8 model (faster) or full precision (more accurate)
    
    Returns:
        str: Transcribed text
    """
    client = STTClient(use_int8=use_int8)
    return client.transcribe_file(audio_file)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python stt_client.py <audio_file.wav>")
        print("\nExample:")
        print("  python stt_client.py test_audio.wav")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    print(f"\nTranscribing: {audio_file}")
    print("="*70)
    
    try:
        # Test with INT8 model (faster)
        print("\n--- Using INT8 model ---")
        text_int8 = transcribe(audio_file, use_int8=True)
        print(f"Result: {text_int8}")
        
        # Test with full precision model (more accurate)
        print("\n--- Using full precision model ---")
        text_full = transcribe(audio_file, use_int8=False)
        print(f"Result: {text_full}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
