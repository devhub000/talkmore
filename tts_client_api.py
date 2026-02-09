"""
TTS Client functions for API use - Lazy loading version
"""
import sys
import os
import numpy as np
import json
from pathlib import Path
import re
import unicodedata
import wave
from phonemizer import phonemize
import tritonclient.http as httpclient

# Global cache for config
_voice_config = None
_phoneme_id_map = None

def _load_config():
    """Lazy load voice config"""
    global _voice_config, _phoneme_id_map
    if _voice_config is None:
        # Try Docker path first, then local path
        docker_path = Path("/app/models/text_to_speech/voice_banmai/1/model.onnx.json")
        local_path = Path(__file__).parent / "models" / "text_to_speech" / "voice_banmai" / "1" / "model.onnx.json"
        
        config_path = docker_path if docker_path.exists() else local_path
        
        if not config_path.exists():
            raise FileNotFoundError(f"Voice config not found at {docker_path} or {local_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            _voice_config = json.load(f)
        _phoneme_id_map = _voice_config['phoneme_id_map']
    return _voice_config, _phoneme_id_map

def text_to_phonemes(text, voice='vi'):
    """Convert text to phonemes using phonemizer library"""
    try:
        phonemes_text = phonemize(
            text,
            language=voice,
            backend='espeak',
            strip=True,
            preserve_punctuation=True,
            with_stress=True
        )
        phonemes_text = re.sub(r'\([^)]*\)', '', phonemes_text)
        phonemes_text = unicodedata.normalize('NFD', phonemes_text)
        phonemes = list(phonemes_text)
        return phonemes
    except Exception as e:
        print(f"⚠ Phonemization error: {e}")
        return list(unicodedata.normalize('NFD', text))
def phonemes_to_ids(phonemes, add_padding=True):
    """Convert phoneme list to phoneme IDs with optional extra padding"""
    _, phoneme_id_map = _load_config()
    BOS = phoneme_id_map['^'][0]
    PAD = phoneme_id_map['_'][0]
    EOS = phoneme_id_map['$'][0]
    
    # Thêm nhiều PAD hơn ở đầu
    phoneme_ids = [BOS]
    if add_padding:
        phoneme_ids.extend([PAD] * 3)  # Thêm 3 PAD thay vì 1
    else:
        phoneme_ids.append(PAD)
    
    for phoneme in phonemes:
        if phoneme in phoneme_id_map:
            phoneme_ids.append(phoneme_id_map[phoneme][0])
            phoneme_ids.append(PAD)
        else:
            if phoneme.strip():
                print(f"⚠ Unknown phoneme: '{phoneme}' (skipping)")
    
    # Thêm nhiều PAD hơn ở cuối
    if add_padding:
        phoneme_ids.extend([PAD] * 3)
    phoneme_ids.append(EOS)
    
    return phoneme_ids

def synthesize_speech(
    text,
    output_file="output.wav",
    voice_model='voice_banmai',
    espeak_voice='vi',
    length_scale=1.5,  # Tăng lên 1.5-2.0 để âm thanh chậm hơn
    noise_scale=0.667,
    noise_w=0.8,
    triton_url="triton:8000",
    add_silence_duration=0.2  # Thêm tham số này
):
    """Synthesize speech from text using Triton TTS model"""
    voice_config, _ = _load_config()
    
    # Text to phonemes
    phonemes = text_to_phonemes(text, espeak_voice)
    
    # Phonemes to IDs (với padding thêm)
    phoneme_ids = phonemes_to_ids(phonemes, add_padding=True)
    
    # Run inference
    triton_client = httpclient.InferenceServerClient(url=triton_url)
    
    input_data = np.array([phoneme_ids], dtype=np.int64)
    input_lengths = np.array([len(phoneme_ids)], dtype=np.int64)
    scales = np.array([noise_scale, length_scale, noise_w], dtype=np.float32)
    
    inputs = [
        httpclient.InferInput("input", input_data.shape, "INT64"),
        httpclient.InferInput("input_lengths", input_lengths.shape, "INT64"),
        httpclient.InferInput("scales", scales.shape, "FP32"),
    ]
    
    inputs[0].set_data_from_numpy(input_data)
    inputs[1].set_data_from_numpy(input_lengths)
    inputs[2].set_data_from_numpy(scales)
    
    outputs = [httpclient.InferRequestedOutput("output")]
    
    response = triton_client.infer(
        model_name=voice_model,
        inputs=inputs,
        outputs=outputs
    )
    
    audio_output = response.as_numpy("output")
    
    # Save audio
    print(f"Audio output shape: {audio_output.shape}")
    
    if len(audio_output.shape) == 4:
        audio_data = audio_output.squeeze()
        if audio_data.ndim > 1:
            audio_data = audio_data.flatten()
    elif len(audio_output.shape) == 3:
        audio_data = audio_output.squeeze()
    else:
        audio_data = audio_output.squeeze()
    
    print(f"Audio data length: {len(audio_data)} samples")
    print(f"Audio data range: [{audio_data.min():.4f}, {audio_data.max():.4f}]")
    
    # Normalize
    max_val = np.abs(audio_data).max()
    if max_val > 0:
        audio_data = audio_data / max_val
    
    # THÊM SILENCE Ở ĐẦU VÀ CUỐI
    sample_rate = voice_config['audio']['sample_rate']
    silence_samples = int(add_silence_duration * sample_rate)
    silence = np.zeros(silence_samples, dtype=audio_data.dtype)
    
    # Ghép: silence + audio + silence
    audio_data = np.concatenate([silence, audio_data, silence])
    
    audio_int16 = (audio_data * 32767).astype(np.int16)
    
    with wave.open(output_file, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_int16.tobytes())
    
    return output_file