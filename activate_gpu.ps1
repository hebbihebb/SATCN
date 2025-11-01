# activate_gpu.ps1 - Quick GPU environment activation
Write-Host "`n===========================================" -ForegroundColor Cyan
Write-Host "  SATCN GPU Environment" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "Activating .venv-gpu...`n" -ForegroundColor Gray

.\.venv-gpu\Scripts\Activate.ps1

Write-Host "✓ GPU environment active!" -ForegroundColor Green
Write-Host ""
Write-Host "Environment: .venv-gpu" -ForegroundColor Gray
Write-Host "CUDA Support: llama-cpp-python with CUDA" -ForegroundColor Gray
Write-Host "GPU: RTX 4060 Laptop GPU (Ampere)" -ForegroundColor Gray
Write-Host ""
Write-Host "Ready for GPU-accelerated inference!`n" -ForegroundColor Green
