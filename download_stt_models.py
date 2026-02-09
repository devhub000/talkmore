"""
Download Speech-to-Text models from HuggingFace
Models: sherpa-onnx-zipformer-vi Vietnamese ASR
"""
import os
from pathlib import Path
from huggingface_hub import hf_hub_download

# Model files from HuggingFace Space
# Source: https://huggingface.co/spaces/hynt/k2-automatic-speech-recognition-demo
REPO_ID = "hynt/k2-automatic-speech-recognition-demo"
REPO_TYPE = "space"

# INT8 Model (faster, lower memory)
INT8_FILES = [
    "encoder-epoch-20-avg-10.int8.onnx",
    "decoder-epoch-20-avg-10.int8.onnx",
    "joiner-epoch-20-avg-10.int8.onnx",
    "config.json"  # This contains tokens
]

# Full Precision Model (more accurate)
FULL_FILES = [
    "encoder-epoch-20-avg-10.onnx",
    "decoder-epoch-20-avg-10.onnx",
    "joiner-epoch-20-avg-10.onnx",
    "config.json"
]

MODELS = [
    {
        "name": "sherpa-onnx-zipformer-vi-int8",
        "files": INT8_FILES,
        "description": "Quantized INT8 model for faster inference with lower memory usage",
        "size": "~30MB"
    },
    {
        "name": "sherpa-onnx-zipformer-vi",
        "files": FULL_FILES,
        "description": "Full precision model for best accuracy",
        "size": "~100MB"
    }
]

def download_model_files(model_name, files, local_dir):
    """Download individual model files from HuggingFace Space"""
    print(f"\n{'='*70}")
    print(f"Downloading: {model_name}")
    print(f"Destination: {local_dir}")
    print(f"Files: {len(files)}")
    print(f"{'='*70}")
    
    local_dir = Path(local_dir)
    local_dir.mkdir(parents=True, exist_ok=True)
    
    success_count = 0
    for filename in files:
        try:
            print(f"  Downloading {filename}...", end=" ", flush=True)
            
            file_path = hf_hub_download(
                repo_id=REPO_ID,
                repo_type=REPO_TYPE,
                filename=filename,
                local_dir=local_dir,
                local_dir_use_symlinks=False
            )
            
            file_size = Path(file_path).stat().st_size / (1024 * 1024)  # MB
            print(f"✓ ({file_size:.1f} MB)")
            success_count += 1
            
        except Exception as e:
            print(f"✗ Error: {e}")
    
    if success_count == len(files):
        print(f"\n✓ All {success_count} files downloaded successfully")
        return True
    else:
        print(f"\n⚠ Downloaded {success_count}/{len(files)} files")
        return False

def main():
    """Download all STT models"""
    models_dir = Path(__file__).parent / "models" / "stt"
    models_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*70)
    print("Speech-to-Text Model Downloader")
    print("="*70)
    print(f"\nBase directory: {models_dir}")
    print(f"\nModels to download: {len(MODELS)}")
    
    for model in MODELS:
        print(f"\n{model['name']}:")
        print(f"  - Description: {model['description']}")
        print(f"  - Size: {model['size']}")
        print(f"  - Files: {len(model['files'])}")
    
    input("\nPress Enter to start downloading...")
    
    success_count = 0
    for model in MODELS:
        local_dir = models_dir / model['name']
        if download_model_files(model['name'], model['files'], str(local_dir)):
            success_count += 1
    
    print("\n" + "="*70)
    print(f"Download Summary: {success_count}/{len(MODELS)} successful")
    print("="*70)
    
    if success_count == len(MODELS):
        print("\n✓ All models downloaded successfully!")
        print("\nNext steps:")
        print("  1. Test the models with test_stt.py")
        print("  2. Integrate STT into your pipeline")
        print("  3. Update API endpoints to support audio input")
    else:
        print("\n⚠ Some models failed to download. Please check the errors above.")

if __name__ == "__main__":
    main()
