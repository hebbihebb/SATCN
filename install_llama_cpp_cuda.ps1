# Install llama-cpp-python with CUDA support
# Requires: Visual Studio 2022 with C++ tools, CUDA Toolkit 12.1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installing llama-cpp-python with CUDA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Activate GPU environment
Write-Host "`nActivating .venv-gpu environment..." -ForegroundColor Yellow
& .\.venv-gpu\Scripts\Activate.ps1

# Set CUDA environment variables
Write-Host "Setting CUDA environment variables..." -ForegroundColor Yellow

# Auto-detect CUDA installation
$cudaBasePath = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA"
if (Test-Path $cudaBasePath) {
    $cudaVersions = Get-ChildItem $cudaBasePath | Where-Object { $_.PSIsContainer } | Sort-Object Name -Descending
    if ($cudaVersions) {
        $latestCuda = $cudaVersions[0].FullName
        $env:CUDA_PATH = $latestCuda
        $env:CUDA_HOME = $env:CUDA_PATH
        # Add both bin and bin\x64 to PATH (cuBLAS is in bin\x64)
        $env:PATH = "$env:CUDA_PATH\bin\x64;$env:CUDA_PATH\bin;$env:PATH"

        Write-Host "Found CUDA installation: $($cudaVersions[0].Name)" -ForegroundColor Green
        Write-Host "CUDA_PATH: $env:CUDA_PATH" -ForegroundColor Green
        Write-Host "CUDA_HOME: $env:CUDA_HOME" -ForegroundColor Green
    } else {
        Write-Host "Error: No CUDA installation found in $cudaBasePath" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Error: CUDA directory not found at $cudaBasePath" -ForegroundColor Red
    exit 1
}

# Set Visual Studio environment (using cmd to run vcvarsall.bat)
Write-Host "`nSetting up Visual Studio build environment..." -ForegroundColor Yellow
$vcvarsall = "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat"

# Set CMAKE flags for CUDA (use GGML_CUDA, not deprecated LLAMA_CUBLAS)
$env:CMAKE_ARGS = "-DGGML_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=native"
$env:FORCE_CMAKE = "1"
$env:CudaToolkitDir = $env:CUDA_PATH

Write-Host "CMAKE_ARGS: $env:CMAKE_ARGS" -ForegroundColor Green
Write-Host "FORCE_CMAKE: $env:FORCE_CMAKE" -ForegroundColor Green
Write-Host "CudaToolkitDir: $env:CudaToolkitDir" -ForegroundColor Green

# Upgrade pip, wheel, setuptools
Write-Host "`nUpgrading build tools..." -ForegroundColor Yellow
python -m pip install --upgrade pip wheel setuptools cmake

# Install llama-cpp-python with CUDA support
Write-Host "`nInstalling llama-cpp-python with CUDA support..." -ForegroundColor Yellow
Write-Host "This will take several minutes to compile..." -ForegroundColor Yellow

# We need to run this in a cmd shell with vcvarsall set up
$installScript = @"
call "$vcvarsall" x64
set CUDA_PATH=$env:CUDA_PATH
set CUDA_HOME=$env:CUDA_HOME
set CudaToolkitDir=$env:CudaToolkitDir
set CMAKE_ARGS=$env:CMAKE_ARGS
set FORCE_CMAKE=$env:FORCE_CMAKE
python -m pip install llama-cpp-python --force-reinstall --no-cache-dir --verbose
"@

$installScript | Out-File -FilePath "temp_install.bat" -Encoding ASCII

Write-Host "`nStarting compilation (this may take 5-10 minutes)...`n" -ForegroundColor Yellow
cmd /c temp_install.bat

# Clean up
Remove-Item "temp_install.bat" -ErrorAction SilentlyContinue

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nTesting CUDA availability..." -ForegroundColor Yellow
$env:PATH = "$env:CUDA_PATH\bin\x64;$env:PATH"
python -c "from llama_cpp import Llama; print('✅ GPU support successfully installed and working!')"

Write-Host "`nTo activate this environment, run:" -ForegroundColor Yellow
Write-Host "  .\.venv-gpu\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "`nIMPORTANT: Before using GPU, add CUDA to PATH:" -ForegroundColor Yellow
Write-Host "  `$env:PATH = 'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64;`$env:PATH'" -ForegroundColor Cyan

# Test CUDA availability
Write-Host "`nTesting CUDA availability..." -ForegroundColor Yellow
python -c "from llama_cpp import Llama; print('llama-cpp-python imported successfully'); import llama_cpp; print('GPU layers supported:', hasattr(llama_cpp.Llama, 'n_gpu_layers'))"

Write-Host "`nTo activate this environment, run:" -ForegroundColor Cyan
Write-Host "  .\.venv-gpu\Scripts\Activate.ps1" -ForegroundColor White
