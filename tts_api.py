"""
FastAPI wrapper for Vietnamese TTS & STT service
Provides REST API for text-to-speech and speech-to-text conversion
"""
from fastapi import FastAPI, HTTPException, Query, UploadFile, File, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
import tempfile
import time
from pathlib import Path
import wave
import numpy as np
import json
import base64
import io
import asyncio
import threading

# Import TTS client
from tts_client_api import synthesize_speech
import tritonclient.http as httpclient

# Import STT client (optional)
try:
    import sherpa_onnx
    STT_AVAILABLE = True
    _stt_recognizer = None
    _stt_lock = threading.Lock()  # Lock for thread-safe model loading
    
    # STT model paths (cached for reuse)
    _stt_model_paths = None
except ImportError:
    STT_AVAILABLE = False
    _stt_recognizer = None
    _stt_lock = None
    _stt_model_paths = None

# Configure FastAPI for large uploads
app = FastAPI(
    title="Vietnamese Voice AI API",
    description="Text-to-Speech & Speech-to-Text API for Vietnamese language",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Available voices configuration
VOICES = {
    # Female voices
    "banmai": {"gender": "female", "description": "Ban Mai - Natural female voice"},
    "chieuthanh": {"gender": "female", "description": "Chiều Thanh - Mature female voice"},
    "lacphi": {"gender": "female", "description": "Lạc Phi - Gentle female voice"},
    "maiphuong": {"gender": "female", "description": "Mai Phương - Professional female voice"},
    "ngochuyen": {"gender": "female", "description": "Ngọc Huyền - Soft female voice"},
    "phuongtrang": {"gender": "female", "description": "Phương Trang - Clear female voice"},
    "thientam": {"gender": "female", "description": "Thiên Tâm - Sweet female voice"},
    "calmwoman3688": {"gender": "female", "description": "Calm Woman - Calm female voice"},
    "mytam2": {"gender": "female", "description": "My Tam - Bright female voice"},
    "mytam2794": {"gender": "female", "description": "My Tam Alt - Alternative female voice"},
    "ngocngan3701": {"gender": "female", "description": "Ngọc Ngân - Elegant female voice"},
    "taian2": {"gender": "female", "description": "Tái An - Young female voice"},
    "taian4": {"gender": "female", "description": "Tái An Alt - Alternative young female voice"},
    "thanhphuong2": {"gender": "female", "description": "Thanh Phương - Professional female voice"},
    
    # Male voices
    "deepman3909": {"gender": "male", "description": "Deep Man - Deep male voice"},
    "manhdung": {"gender": "male", "description": "Mạnh Dũng - Strong male voice"},
    "minhkhang": {"gender": "male", "description": "Minh Khang - Clear male voice"},
    "minhquang": {"gender": "male", "description": "Minh Quang - Bright male voice"},
    "mattheo": {"gender": "male", "description": "Mattheo - Natural male voice"},
    "mattheo1": {"gender": "male", "description": "Mattheo Alt - Alternative male voice"},
    "tranthanh3870": {"gender": "male", "description": "Trấn Thành - Professional male voice"},
    "vietthao3886": {"gender": "male", "description": "Việt Thảo - Smooth male voice"},
    "duyoryx3175": {"gender": "male", "description": "Duy Ory - Young male voice"},
    
    # Other
    "indo": {"gender": "other", "description": "Indonesian accent voice"},
}

class TTSRequest(BaseModel):
    text: str
    voice: str = "banmai"
    speed: float = 1.5
    noise_scale: float = 0.667
    noise_w: float = 0.8

class TranscriptionResponse(BaseModel):
    text: str
    duration: float
    sample_rate: int
    model: str

def get_stt_model_paths():
    """Get STT model paths (thread-safe caching)"""
    global _stt_model_paths
    
    if not STT_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="STT not available. Install with: pip install -r requirements-stt.txt && python download_stt_models.py"
        )
    
    # Cache model paths to avoid repeated file system checks
    with _stt_lock:
        if _stt_model_paths is None:
            # Try Docker path first, then local path
            docker_stt_path = Path("/app/models_/stt")
            local_stt_path = Path(__file__).parent / "models_" / "stt"
            
            models_dir = docker_stt_path if docker_stt_path.exists() else local_stt_path
            int8_dir = models_dir / "sherpa-onnx-zipformer-vi-int8"
            
            if not int8_dir.exists():
                raise HTTPException(
                    status_code=503,
                    detail=f"STT models not found at {int8_dir}. Run: python download_stt_models.py"
                )
            
            _stt_model_paths = {
                "encoder": str(int8_dir / "encoder-epoch-20-avg-10.int8.onnx"),
                "decoder": str(int8_dir / "decoder-epoch-20-avg-10.int8.onnx"),
                "joiner": str(int8_dir / "joiner-epoch-20-avg-10.int8.onnx"),
                "tokens": str(int8_dir / "config.json"),
            }
    
    return _stt_model_paths

def create_stt_recognizer():
    """Create a new STT recognizer instance (no sharing between requests)"""
    paths = get_stt_model_paths()
    
    return sherpa_onnx.OfflineRecognizer.from_transducer(
        tokens=paths["tokens"],
        encoder=paths["encoder"],
        decoder=paths["decoder"],
        joiner=paths["joiner"],
        num_threads=2,
        sample_rate=16000,
        feature_dim=80,
        decoding_method="greedy_search",
    )

def convert_to_wav(input_path: str, output_path: str) -> bool:
    """Convert any audio format to WAV chuẩn (16-bit PCM, 22050Hz, stereo)
    
    Supports: MP3, M4A, AAC, OGG, FLAC, WAV (any format)
    Returns: True if success
    """
    import subprocess
    try:
        # ffmpeg convert về WAV chuẩn
        cmd = [
            'ffmpeg', '-i', input_path,
            '-ar', '22050',          # Sample rate 22050Hz
            '-ac', '2',              # Stereo (hoặc mono tùy file)
            '-sample_fmt', 's16',    # 16-bit PCM
            '-y',                    # Overwrite
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=60)
        return result.returncode == 0
    except Exception as e:
        print(f"[CONVERT] Error: {e}")
        return False

def split_audio_to_chunks(wav_path: str, chunk_duration: int = 30) -> list:
    """Chia file audio lớn thành chunks nhỏ
    
    Args:
        wav_path: Path to WAV file
        chunk_duration: Duration per chunk in seconds (default 30s)
    
    Returns:
        List of (chunk_path, start_time, duration) tuples
    """
    import subprocess
    chunks = []
    
    try:
        # Get total duration
        with wave.open(wav_path, 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            total_duration = frames / rate
        
        print(f"[SPLIT] Total duration: {total_duration:.1f}s, splitting to {chunk_duration}s chunks")
        
        # Split into chunks using ffmpeg
        chunk_start = 0
        chunk_idx = 0
        
        while chunk_start < total_duration:
            chunk_path = tempfile.mktemp(suffix=f"_chunk{chunk_idx}.wav")
            
            # ffmpeg split
            cmd = [
                'ffmpeg', '-i', wav_path,
                '-ss', str(chunk_start),
                '-t', str(chunk_duration),
                '-c', 'copy',
                '-y',
                chunk_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            if result.returncode == 0:
                # Get actual chunk duration
                with wave.open(chunk_path, 'rb') as wf:
                    chunk_frames = wf.getnframes()
                    chunk_rate = wf.getframerate()
                    actual_duration = chunk_frames / chunk_rate
                
                chunks.append((chunk_path, chunk_start, actual_duration))
                print(f"[SPLIT] Chunk {chunk_idx}: {chunk_start:.1f}s - {chunk_start + actual_duration:.1f}s")
            
            chunk_start += chunk_duration
            chunk_idx += 1
        
        print(f"[SPLIT] Created {len(chunks)} chunks")
        return chunks
        
    except Exception as e:
        print(f"[SPLIT] Error: {e}")
        # Cleanup partial chunks
        for chunk_path, _, _ in chunks:
            if os.path.exists(chunk_path):
                os.remove(chunk_path)
        return []

class TTSResponse(BaseModel):
    audio_url: str
    duration: float
    sample_rate: int
    voice: str
    text: str

@app.get("/")
async def root():
    """API root - Welcome message"""
    return {
        "service": "Vietnamese TTS API",
        "version": "1.0.0",
        "powered_by": "Triton Inference Server + Piper TTS",
        "endpoints": {
            "health": "/health",
            "voices": "/voices",
            "synthesize_get": "/synthesize?text=...&voice=...&speed=...",
            "synthesize_post": "/synthesize (POST with JSON body)",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Triton connection
        triton_client = httpclient.InferenceServerClient(url="triton:8000")
        is_live = triton_client.is_server_live()
        is_ready = triton_client.is_server_ready()
        
        if not is_live or not is_ready:
            raise HTTPException(status_code=503, detail="Triton server not ready")
        
        return {
            "status": "healthy",
            "triton_live": is_live,
            "triton_ready": is_ready,
            "available_voices": len(VOICES)
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/voices")
async def list_voices():
    """List all available voices"""
    try:
        # Get loaded models from Triton
        triton_client = httpclient.InferenceServerClient(url="triton:8000")
        models = triton_client.get_model_repository_index()
        
        loaded_voices = []
        for model in models:
            if model['name'].startswith('voice_'):
                voice_id = model['name'].replace('voice_', '')
                if voice_id in VOICES:
                    loaded_voices.append({
                        "id": voice_id,
                        "name": model['name'],
                        "status": model['state'],
                        **VOICES[voice_id]
                    })
        
        return {
            "total": len(loaded_voices),
            "voices": loaded_voices
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list voices: {str(e)}")

@app.get("/synthesize")
async def synthesize_get(
    text: str = Query(..., description="Text to synthesize", min_length=1, max_length=1000),
    voice: str = Query("banmai", description="Voice ID"),
    speed: float = Query(1.5, description="Speech speed (0.5-3.0, higher=slower)", ge=0.5, le=3.0)
):
    """Synthesize speech from text (GET method)"""
    return await synthesize_speech_internal(text, voice, speed)

@app.post("/synthesize")
async def synthesize_post(request: TTSRequest):
    """Synthesize speech from text (POST method)"""
    return await synthesize_speech_internal(
        request.text, 
        request.voice, 
        request.speed,
        request.noise_scale,
        request.noise_w
    )

async def synthesize_speech_internal(
    text: str,
    voice: str = "banmai",
    speed: float = 1.5,
    noise_scale: float = 0.667,
    noise_w: float = 0.8
):
    """Internal function to handle TTS synthesis"""
    
    # Validate voice
    if voice not in VOICES:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid voice '{voice}'. Available voices: {list(VOICES.keys())}"
        )
    
    # Validate text length
    if len(text) > 1000:
        raise HTTPException(status_code=400, detail="Text too long (max 1000 characters)")
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            output_path = tmp_file.name
        
        # Synthesize speech
        start_time = time.time()
        voice_model = f"voice_{voice}"
        
        synthesize_speech(
            text=text,
            output_file=output_path,
            voice_model=voice_model,
            espeak_voice='vi',
            length_scale=speed,
            noise_scale=noise_scale,
            noise_w=noise_w
        )
        
        duration = time.time() - start_time
        
        # Return audio file
        return FileResponse(
            output_path,
            media_type="audio/wav",
            filename=f"tts_{voice}_{int(time.time())}.wav",
            headers={
                "X-Processing-Time": str(duration),
                "X-Voice": voice,
                "X-Speed": str(speed)
            }
        )
        
    except Exception as e:
        # Clean up temp file if exists
        if os.path.exists(output_path):
            os.remove(output_path)
        
        raise HTTPException(
            status_code=500, 
            detail=f"TTS synthesis failed: {str(e)}"
        )

@app.get("/info")
async def service_info():
    """Get service information"""
    return {
        "service": "Vietnamese TTS API",
        "version": "1.0.0",
        "models": {
            "total_voices": len(VOICES),
            "female_voices": sum(1 for v in VOICES.values() if v["gender"] == "female"),
            "male_voices": sum(1 for v in VOICES.values() if v["gender"] == "male"),
        },
        "features": {
            "languages": ["Vietnamese"],
            "sample_rate": "22050 Hz",
            "output_format": "WAV (16-bit PCM)",
            "max_text_length": 1000,
            "speed_range": "0.5-3.0",
        },
        "license": {
            "triton": "BSD-3-Clause",
            "models": "Apache-2.0",
            "commercial_use": "Allowed"
        }
    }

@app.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...)
):
    """
    Speech-to-Text endpoint - Chunked processing cho file lớn
    
    Upload WAV/MP3/M4A/AAC file (multipart/form-data)
    Xử lý file lớn 4-5 phút bằng cách chia chunks
    """
    if not STT_AVAILABLE:
        raise HTTPException(503, "STT service not available")
    
    start_time = time.time()
    temp_input = None
    temp_path = None
    chunk_files = []
    
    try:
        # Stream file từ upload vào disk
        temp_input = tempfile.mktemp(suffix=os.path.splitext(audio.filename)[1] if audio.filename else '.tmp')
        print(f"[STT] Receiving file...")
        
        file_size = 0
        with open(temp_input, "wb") as f:
            while True:
                chunk = await audio.read(65536)  # 64KB chunks
                if not chunk:
                    break
                f.write(chunk)
                file_size += len(chunk)
        
        print(f"[STT] Saved: {file_size / (1024*1024):.1f}MB")
        
        # Convert về WAV chuẩn
        temp_path = tempfile.mktemp(suffix=".wav")
        print(f"[STT] Converting to WAV...")
        if not convert_to_wav(temp_input, temp_path):
            os.remove(temp_input)
            raise HTTPException(400, "Cannot convert audio to WAV format")
        
        os.remove(temp_input)
        temp_input = None
        print(f"[STT] Converted")
        
        # Get WAV info
        with wave.open(temp_path, 'rb') as wf:
            sample_rate = wf.getframerate()
            num_channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            duration = wf.getnframes() / sample_rate
            
            print(f"[STT] WAV: {sample_rate}Hz, {num_channels}ch, {duration:.1f}s")
            
            if sample_width != 2:
                raise HTTPException(400, "Expected 16-bit PCM audio")
            if num_channels not in [1, 2]:
                raise HTTPException(400, "Expected mono/stereo")
        
        # Process: chunk if large, whole if small
        if duration > 60:
            print(f"[STT] Large file, splitting into 30s chunks...")
            chunk_files = split_audio_to_chunks(temp_path, chunk_duration=30)
            
            if not chunk_files:
                raise HTTPException(500, "Failed to split audio")
            
            # Process each chunk
            full_text = []
            recognizer = create_stt_recognizer()
            
            for idx, (chunk_path, start_time_chunk, chunk_dur) in enumerate(chunk_files):
                print(f"[STT] Processing chunk {idx+1}/{len(chunk_files)}...")
                
                stream = recognizer.create_stream()
                
                with wave.open(chunk_path, 'rb') as wf:
                    while True:
                        audio_chunk = wf.readframes(32768)
                        if not audio_chunk:
                            break
                        audio_array = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0
                        if num_channels == 2:
                            audio_array = audio_array.reshape(-1, 2).mean(axis=1)
                        stream.accept_waveform(sample_rate, audio_array)
                
                recognizer.decode_stream(stream)
                chunk_text = stream.result.text
                if chunk_text.strip():
                    full_text.append(chunk_text.strip())
                
                # Cleanup chunk immediately
                os.remove(chunk_path)
            
            text = " ".join(full_text)
            print(f"[STT] Processed {len(chunk_files)} chunks")
            
        else:
            # Small file - process whole
            print(f"[STT] Processing small file...")
            recognizer = create_stt_recognizer()
            stream = recognizer.create_stream()
            
            with wave.open(temp_path, 'rb') as wf:
                while True:
                    audio_chunk = wf.readframes(32768)
                    if not audio_chunk:
                        break
                    audio_array = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0
                    if num_channels == 2:
                        audio_array = audio_array.reshape(-1, 2).mean(axis=1)
                    stream.accept_waveform(sample_rate, audio_array)
            
            recognizer.decode_stream(stream)
            text = stream.result.text
        
        elapsed = time.time() - start_time
        print(f"[STT] ✅ Done: {elapsed:.1f}s")
        
        return {
            "text": text,
            "duration": duration,
            "file_size_mb": file_size / (1024*1024),
            "processing_time": elapsed,
            "model": "sherpa-onnx-zipformer-vi-int8",
            "chunks_processed": len(chunk_files) if chunk_files else 1
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[STT] Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"Transcription failed: {str(e)}")
    finally:
        # Cleanup all temp files
        for path in [temp_input, temp_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass
        
        # Cleanup any remaining chunks
        for chunk_path, _, _ in chunk_files:
            if os.path.exists(chunk_path):
                try:
                    os.remove(chunk_path)
                except:
                    pass

@app.post("/transcribe-raw")
async def transcribe_raw(request: Request):
    """Raw binary upload - Chunked processing cho file lớn"""
    if not STT_AVAILABLE:
        raise HTTPException(503, "STT not available")
    
    start_time = time.time()
    temp_input = None
    temp_path = None
    chunk_files = []
    
    try:
        # Stream body to disk
        temp_input = tempfile.mktemp(suffix=".tmp")
        file_size = 0
        
        print(f"[STT-RAW] Streaming body...")
        with open(temp_input, 'wb') as f:
            async for chunk in request.stream():
                f.write(chunk)
                file_size += len(chunk)
        
        print(f"[STT-RAW] Received: {file_size / (1024*1024):.1f}MB")
        
        # Convert to WAV
        temp_path = tempfile.mktemp(suffix=".wav")
        print(f"[STT-RAW] Converting...")
        if not convert_to_wav(temp_input, temp_path):
            raise HTTPException(400, "Cannot convert")
        
        os.remove(temp_input)
        temp_input = None
        
        # Get duration
        with wave.open(temp_path, 'rb') as wf:
            sample_rate = wf.getframerate()
            num_channels = wf.getnchannels()
            duration = wf.getnframes() / sample_rate
        
        print(f"[STT-RAW] Duration: {duration:.1f}s")
        
        # Split into chunks if large (> 60s)
        if duration > 60:
            print(f"[STT-RAW] Large file, splitting into 30s chunks...")
            chunk_files = split_audio_to_chunks(temp_path, chunk_duration=30)
            
            if not chunk_files:
                raise HTTPException(500, "Failed to split audio")
            
            # Process each chunk
            full_text = []
            recognizer = create_stt_recognizer()
            
            for idx, (chunk_path, start_time_chunk, chunk_dur) in enumerate(chunk_files):
                print(f"[STT-RAW] Processing chunk {idx+1}/{len(chunk_files)}...")
                
                stream = recognizer.create_stream()
                
                with wave.open(chunk_path, 'rb') as wf:
                    while True:
                        audio_chunk = wf.readframes(32768)
                        if not audio_chunk:
                            break
                        audio_array = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0
                        if num_channels == 2:
                            audio_array = audio_array.reshape(-1, 2).mean(axis=1)
                        stream.accept_waveform(sample_rate, audio_array)
                
                recognizer.decode_stream(stream)
                chunk_text = stream.result.text
                if chunk_text.strip():
                    full_text.append(chunk_text.strip())
                
                # Cleanup chunk immediately
                os.remove(chunk_path)
            
            text = " ".join(full_text)
            print(f"[STT-RAW] Processed {len(chunk_files)} chunks")
            
        else:
            # Small file - process whole
            print(f"[STT-RAW] Processing small file...")
            recognizer = create_stt_recognizer()
            stream = recognizer.create_stream()
            
            with wave.open(temp_path, 'rb') as wf:
                while True:
                    audio_chunk = wf.readframes(32768)
                    if not audio_chunk:
                        break
                    audio_array = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0
                    if num_channels == 2:
                        audio_array = audio_array.reshape(-1, 2).mean(axis=1)
                    stream.accept_waveform(sample_rate, audio_array)
            
            recognizer.decode_stream(stream)
            text = stream.result.text
        
        elapsed = time.time() - start_time
        print(f"[STT-RAW] ✅ Done: {elapsed:.1f}s")
        
        return {
            "text": text,
            "duration": duration,
            "file_size_mb": file_size / (1024*1024),
            "processing_time": elapsed,
            "chunks_processed": len(chunk_files) if chunk_files else 1
        }
        
    except Exception as e:
        print(f"[STT-RAW] Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, str(e))
    finally:
        # Cleanup all temp files
        for path in [temp_input, temp_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass
        
        # Cleanup any remaining chunks
        for chunk_path, _, _ in chunk_files:
            if os.path.exists(chunk_path):
                try:
                    os.remove(chunk_path)
                except:
                    pass

# ==================== WebSocket Streaming Endpoints ====================

@app.websocket("/ws/tts")
async def websocket_tts_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time TTS streaming
    
    Client sends: {"text": "...", "voice": "...", "speed": 1.5}
    Server responds: {"audio": "base64_encoded_audio_chunk", "duration": ...}
    """
    await websocket.accept()
    try:
        while True:
            # Receive request from client
            data = await websocket.receive_text()
            request = json.loads(data)
            
            text = request.get("text", "")
            voice = request.get("voice", "banmai")
            speed = float(request.get("speed", 1.5))
            noise_scale = float(request.get("noise_scale", 0.667))
            noise_w = float(request.get("noise_w", 0.8))
            
            # Validate
            if not text or len(text) == 0:
                await websocket.send_json({"error": "Text cannot be empty"})
                continue
            
            if voice not in VOICES:
                await websocket.send_json({"error": f"Invalid voice: {voice}"})
                continue
            
            try:
                # Synthesize
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                    output_path = tmp.name
                
                start_time = time.time()
                voice_model = f"voice_{voice}"
                
                synthesize_speech(
                    text=text,
                    output_file=output_path,
                    voice_model=voice_model,
                    espeak_voice='vi',
                    length_scale=speed,
                    noise_scale=noise_scale,
                    noise_w=noise_w
                )
                
                duration = time.time() - start_time
                
                # Read audio file
                with open(output_path, 'rb') as f:
                    audio_bytes = f.read()
                
                # Encode to base64
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                
                # Send response
                await websocket.send_json({
                    "success": True,
                    "audio": audio_base64,
                    "duration": duration,
                    "voice": voice,
                    "sample_rate": 22050
                })
                
                # Cleanup
                os.remove(output_path)
                
            except Exception as e:
                await websocket.send_json({"error": f"TTS failed: {str(e)}"})
    
    except WebSocketDisconnect:
        print("TTS WebSocket client disconnected")
    except Exception as e:
        print(f"TTS WebSocket error: {e}")

@app.websocket("/ws/stt")
async def websocket_stt_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time STT streaming
    
    Client sends: {"audio": "base64_encoded_audio", "format": "wav"}
    Server responds: {"text": "...", "duration": ...}
    """
    if not STT_AVAILABLE:
        await websocket.close(code=1008, reason="STT not available")
        return
    
    await websocket.accept()
    try:
        while True:
            # Receive audio from client
            data = await websocket.receive_text()
            request = json.loads(data)
            
            audio_base64 = request.get("audio", "")
            sample_rate = int(request.get("sample_rate", 16000))
            
            if not audio_base64:
                await websocket.send_json({"error": "Audio data required"})
                continue
            
            try:
                # Decode base64 audio
                audio_bytes = base64.b64decode(audio_base64)
                
                # Save to temp file
                temp_path = tempfile.mktemp(suffix=".wav")
                with open(temp_path, "wb") as f:
                    f.write(audio_bytes)
                
                start_time = time.time()
                
                # Read audio
                with wave.open(temp_path, 'rb') as wf:
                    actual_sample_rate = wf.getframerate()
                    num_channels = wf.getnchannels()
                    sample_width = wf.getsampwidth()
                    num_samples = wf.getnframes()
                    duration = num_samples / actual_sample_rate
                    
                    audio_data = wf.readframes(num_samples)
                    
                    if sample_width == 2:
                        audio_array = np.frombuffer(audio_data, dtype=np.int16)
                        audio_array = audio_array.astype(np.float32) / 32768.0
                    else:
                        await websocket.send_json({"error": "Unsupported audio format"})
                        os.remove(temp_path)
                        continue
                    
                    # Convert to mono
                    if num_channels == 2:
                        audio_array = audio_array.reshape(-1, 2).mean(axis=1)
                    elif num_channels != 1:
                        await websocket.send_json({"error": f"Unsupported channels: {num_channels}"})
                        os.remove(temp_path)
                        continue
                
                # Create new recognizer instance for this request (no contention)
                recognizer = create_stt_recognizer()
                stream = recognizer.create_stream()
                
                # Audio processing (can be parallelized per instance)
                stream.accept_waveform(actual_sample_rate, audio_array)
                recognizer.decode_stream(stream)
                text = stream.result.text
                
                processing_time = time.time() - start_time
                
                # Send response
                await websocket.send_json({
                    "success": True,
                    "text": text,
                    "duration": duration,
                    "processing_time": processing_time,
                    "model": "sherpa-onnx-zipformer-vi-int8"
                })
                
                # Cleanup
                os.remove(temp_path)
                
            except Exception as e:
                await websocket.send_json({"error": f"STT failed: {str(e)}"})
    
    except WebSocketDisconnect:
        print("STT WebSocket client disconnected")
    except Exception as e:
        print(f"STT WebSocket error: {e}")

if __name__ == "__main__":
    import asyncio
    from uvicorn import Config, Server
    
    # Custom Uvicorn config for large uploads
    config = Config(
        app=app,
        host="0.0.0.0",
        port=8080,
        timeout_keep_alive=600,
        timeout_notify=1800,
        limit_request_line=32768,
        limit_request_fields=256, 
        limit_request_field_size=16384,
        ws_max_size=16 * 1024 * 1024,  # 16MB for WebSocket
    )
    server = Server(config)
    asyncio.run(server.serve())
