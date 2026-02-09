# Fast Installation Script for Linux
# Uses pre-built wheels for faster installation

echo "=================================================="
echo "STT Setup - Fast Installation (Linux)"
echo "=================================================="
echo ""
echo "Python 3.10 Required"
python3 --version

echo ""
echo "[1/3] Installing PyTorch CPU-only..."
pip install \
  https://download.pytorch.org/whl/cpu/torch-1.13.1%2Bcpu-cp310-cp310-linux_x86_64.whl \
  https://download.pytorch.org/whl/cpu/torchaudio-0.13.1%2Bcpu-cp310-cp310-linux_x86_64.whl

echo ""
echo "[2/3] Installing K2, Sherpa, KaldiFeat..."
pip install \
  https://huggingface.co/csukuangfj/k2/resolve/main/cpu/1.24.4.dev20250307/linux-x64/k2-1.24.4.dev20250307+cpu.torch1.13.1-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl \
  https://huggingface.co/csukuangfj/sherpa/resolve/main/cpu/1.4.0.dev20250307/linux-x64/k2_sherpa-1.4.0.dev20250307+cpu.torch1.13.1-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl \
  https://huggingface.co/csukuangfj/kaldifeat/resolve/main/cpu/1.25.5.dev20250307/linux-x64/kaldifeat-1.25.5.dev20250307+cpu.torch1.13.1-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl

echo ""
echo "[3/3] Installing Sherpa-ONNX..."
pip install https://huggingface.co/csukuangfj/sherpa-onnx-wheels/resolve/main/cpu/1.12.6/sherpa_onnx-1.12.6-cp310-cp310-manylinux2014_x86_64.manylinux_2_17_x86_64.whl

echo ""
echo "Installing other dependencies..."
pip install sentencepiece huggingface-hub "numpy<2"

echo ""
echo "=================================================="
echo "Installation Complete!"
echo "=================================================="
echo ""
echo "Next: Download models with: python download_stt_models.py"
