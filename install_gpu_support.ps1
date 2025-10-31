# GPU Acceleration Installation Script
# Run this after installing CUDA Toolkit

Write-Host "=" * 60
Write-Host "GRMR-V3 GPU Acceleration Setup"
Write-Host "=" * 60
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Cyan

# Check if nvcc is available
try {
    $nvccVersion = nvcc --version 2>&1 | Select-String "release"
    Write-Host "✓ CUDA Toolkit found: $nvccVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ CUDA Toolkit not found (nvcc not in PATH)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install CUDA Toolkit first:" -ForegroundColor Yellow
    Write-Host "  1. Download from: https://developer.nvidia.com/cuda-12-1-0-download-archive"
    Write-Host "  2. Choose: Windows → x86_64 → 11 → exe (local)"
    Write-Host "  3. Install with default options"
    Write-Host "  4. Restart PowerShell and run this script again"
    Write-Host ""
    exit 1
}

# Check if Visual Studio Build Tools are available
try {
    $vsWhere = "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe"
    if (Test-Path $vsWhere) {
        Write-Host "✓ Visual Studio Build Tools found" -ForegroundColor Green
    } else {
        Write-Host "⚠ Visual Studio Build Tools not detected" -ForegroundColor Yellow
        Write-Host "  Build may fail. Install from: https://visualstudio.microsoft.com/downloads/" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Could not verify Visual Studio installation" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" * 60
Write-Host "Building llama-cpp-python with CUDA support"
Write-Host "This will take 5-10 minutes..."
Write-Host "=" * 60
Write-Host ""

# Activate virtual environment
$venvPath = ".venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    & $venvPath
} else {
    Write-Host "✗ Virtual environment not found at .venv/" -ForegroundColor Red
    exit 1
}

# Uninstall existing version
Write-Host ""
Write-Host "Uninstalling CPU-only version..." -ForegroundColor Cyan
python -m pip uninstall llama-cpp-python -y

# Set build flags
Write-Host ""
Write-Host "Setting CUDA build flags..." -ForegroundColor Cyan
$env:CMAKE_ARGS = "-DGGML_CUDA=on"

Write-Host "Building from source with CUDA support..." -ForegroundColor Cyan
Write-Host "(This will take several minutes - please be patient)" -ForegroundColor Yellow
Write-Host ""

# Install with CUDA
python -m pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir --verbose

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Green
    Write-Host "✓ Installation successful!" -ForegroundColor Green
    Write-Host "=" * 60 -ForegroundColor Green
    Write-Host ""
    Write-Host "Testing GPU acceleration..." -ForegroundColor Cyan
    
    # Run test
    python test_grmr_v3_integration.py
    
    Write-Host ""
    Write-Host "Check output above for:" -ForegroundColor Cyan
    Write-Host "  - 'Using CUDA for GRMR-V3 inference (GPU acceleration)'" -ForegroundColor White
    Write-Host "  - Faster inference times (~0.1-0.2s per sentence)" -ForegroundColor White
    Write-Host ""
    Write-Host "Run benchmark for detailed comparison:" -ForegroundColor Cyan
    Write-Host "  python benchmark_grmr_vs_t5.py" -ForegroundColor White
    Write-Host ""
    
} else {
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Red
    Write-Host "✗ Installation failed" -ForegroundColor Red
    Write-Host "=" * 60 -ForegroundColor Red
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "  1. CUDA Toolkit not installed or not in PATH"
    Write-Host "  2. Visual Studio Build Tools missing"
    Write-Host "  3. Incompatible CUDA version"
    Write-Host ""
    Write-Host "See docs/GRMR_V3_GPU_SETUP.md for troubleshooting" -ForegroundColor Yellow
    Write-Host ""
}
