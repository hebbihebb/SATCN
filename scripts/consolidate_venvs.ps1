# Consolidate Virtual Environments Script
# This script backs up old environments and makes .venv-gpu the primary environment

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Virtual Environment Consolidation" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Create backup directory
Write-Host "[1/5] Creating backup directory..." -ForegroundColor Yellow
New-Item -Path "venv_backups" -ItemType Directory -Force | Out-Null
Write-Host "      Created: venv_backups/`n" -ForegroundColor Green

# Step 2: Backup old environments
Write-Host "[2/5] Backing up old environments..." -ForegroundColor Yellow

if (Test-Path ".venv") {
    Write-Host "      Moving .venv -> venv_backups/.venv.backup" -ForegroundColor Gray
    Move-Item -Path ".venv" -Destination "venv_backups/.venv.backup" -Force
    Write-Host "      ✓ .venv backed up" -ForegroundColor Green
} else {
    Write-Host "      (no .venv found, skipping)" -ForegroundColor Gray
}

if (Test-Path ".venv310") {
    Write-Host "      Moving .venv310 -> venv_backups/.venv310.backup" -ForegroundColor Gray
    Move-Item -Path ".venv310" -Destination "venv_backups/.venv310.backup" -Force
    Write-Host "      ✓ .venv310 backed up`n" -ForegroundColor Green
} else {
    Write-Host "      (no .venv310 found, skipping)`n" -ForegroundColor Gray
}

# Step 3: Verify .venv-gpu exists
Write-Host "[3/5] Verifying .venv-gpu environment..." -ForegroundColor Yellow

if (-not (Test-Path ".venv-gpu")) {
    Write-Host "      ✗ ERROR: .venv-gpu not found!" -ForegroundColor Red
    Write-Host "      Cannot proceed without GPU environment.`n" -ForegroundColor Red
    exit 1
}

# Test GPU support
Write-Host "      Testing GPU support..." -ForegroundColor Gray
$testResult = & ".\.venv-gpu\Scripts\python.exe" -c "from llama_cpp import Llama; print('OK')" 2>&1

if ($testResult -match "OK") {
    Write-Host "      ✓ .venv-gpu has working llama-cpp-python`n" -ForegroundColor Green
} else {
    Write-Host "      ✗ WARNING: Could not verify llama-cpp-python" -ForegroundColor Yellow
    Write-Host "      Error: $testResult`n" -ForegroundColor Gray
}

# Step 4: Create activation script
Write-Host "[4/5] Creating activation helper script..." -ForegroundColor Yellow

$activateScript = @'
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
'@

$activateScript | Out-File -FilePath "activate_gpu.ps1" -Encoding utf8 -Force
Write-Host "      Created: activate_gpu.ps1" -ForegroundColor Green
Write-Host "      Usage: .\activate_gpu.ps1`n" -ForegroundColor Gray

# Step 5: Update VS Code settings
Write-Host "[5/5] Updating VS Code settings..." -ForegroundColor Yellow

$vscodeDir = ".vscode"
$settingsFile = "$vscodeDir\settings.json"

# Create .vscode directory if it doesn't exist
if (-not (Test-Path $vscodeDir)) {
    New-Item -Path $vscodeDir -ItemType Directory -Force | Out-Null
}

# Read existing settings or create new
if (Test-Path $settingsFile) {
    $settings = Get-Content $settingsFile -Raw | ConvertFrom-Json
} else {
    $settings = @{}
}

# Update Python interpreter path
$settings | Add-Member -NotePropertyName "python.defaultInterpreterPath" -NotePropertyValue "`${workspaceFolder}/.venv-gpu/Scripts/python.exe" -Force

# Save settings
$settings | ConvertTo-Json -Depth 10 | Out-File -FilePath $settingsFile -Encoding utf8 -Force
Write-Host "      Updated: .vscode/settings.json" -ForegroundColor Green
Write-Host "      Default interpreter: .venv-gpu`n" -ForegroundColor Gray

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Consolidation Complete!" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Summary:" -ForegroundColor White
Write-Host "  • Old environments backed up to: venv_backups/" -ForegroundColor Gray
Write-Host "  • Active environment: .venv-gpu" -ForegroundColor Gray
Write-Host "  • Activation script: activate_gpu.ps1" -ForegroundColor Gray
Write-Host "  • VS Code updated to use .venv-gpu`n" -ForegroundColor Gray

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Restart VS Code to apply new Python interpreter" -ForegroundColor White
Write-Host "  2. Test GPU: .\activate_gpu.ps1 && python scripts\quick_gpu_test.py" -ForegroundColor White
Write-Host "  3. Run benchmarks: python scripts\compare_q4_vs_q8.py --gpu" -ForegroundColor White
Write-Host "  4. If all works, delete backups: Remove-Item -Recurse venv_backups`n" -ForegroundColor White

Write-Host "Rollback (if needed):" -ForegroundColor Yellow
Write-Host "  Move-Item venv_backups\.venv.backup .venv -Force`n" -ForegroundColor White

Write-Host "✓ Ready to use GPU-accelerated environment!`n" -ForegroundColor Green
