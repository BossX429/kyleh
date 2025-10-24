<#
.SYNOPSIS
    Package Security Monitor as standalone executable

.DESCRIPTION
    Builds a standalone .exe using PyInstaller with all dependencies included.
    Output: dist/SecurityMonitor.exe (~50MB)

.PARAMETER Clean
    Clean build directories before packaging

.PARAMETER Debug
    Create debug build with console window

.EXAMPLE
    .\package.ps1
    .\package.ps1 -Clean
    .\package.ps1 -Debug

.NOTES
    Requires: PyInstaller, Python 3.8+
    Output: dist/SecurityMonitor.exe
#>

param(
    [switch]$Clean,
    [switch]$Debug
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Security Monitor Packaging Script" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "🔍 Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python not found! Install Python 3.8+ first." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green

# Check PyInstaller
Write-Host "🔍 Checking PyInstaller..." -ForegroundColor Yellow
python -c "import PyInstaller" 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ PyInstaller not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Install with:" -ForegroundColor Yellow
    Write-Host "  pip install pyinstaller" -ForegroundColor White
    exit 1
}
Write-Host "✅ PyInstaller found" -ForegroundColor Green

# Clean build directories
if ($Clean) {
    Write-Host ""
    Write-Host "🧹 Cleaning build directories..." -ForegroundColor Yellow
    
    $dirsToClean = @("build", "dist", "__pycache__")
    foreach ($dir in $dirsToClean) {
        if (Test-Path $dir) {
            Remove-Item $dir -Recurse -Force
            Write-Host "  Removed: $dir" -ForegroundColor Gray
        }
    }
    
    # Clean .spec file
    if (Test-Path "SecurityMonitor.spec") {
        Remove-Item "SecurityMonitor.spec" -Force
        Write-Host "  Removed: SecurityMonitor.spec" -ForegroundColor Gray
    }
    
    Write-Host "✅ Clean complete" -ForegroundColor Green
}

# Build PyInstaller command
Write-Host ""
Write-Host "📦 Building executable..." -ForegroundColor Yellow

$pyinstallerArgs = @(
    "--name=SecurityMonitor",
    "--onefile",
    "--clean"
)

# Icon (if available)
if (Test-Path "icon.ico") {
    $pyinstallerArgs += "--icon=icon.ico"
}

# Console window control
if (-not $Debug) {
    $pyinstallerArgs += "--noconsole"
    Write-Host "  Mode: Windowed (no console)" -ForegroundColor Gray
} else {
    Write-Host "  Mode: Debug (with console)" -ForegroundColor Gray
}

# Hidden imports for optional dependencies
$hiddenImports = @(
    "plyer",
    "pyttsx3",
    "GPUtil",
    "sklearn.linear_model",
    "joblib",
    "wmi"
)

foreach ($import in $hiddenImports) {
    $pyinstallerArgs += "--hidden-import=$import"
}

# Add data files
$pyinstallerArgs += "--add-data=pyproject.toml;."
if (Test-Path "README.md") {
    $pyinstallerArgs += "--add-data=README.md;."
}

# Entry point
$pyinstallerArgs += "security_monitor.py"

# Run PyInstaller
Write-Host ""
Write-Host "⚙️  Running PyInstaller..." -ForegroundColor Yellow
Write-Host "  Command: pyinstaller $($pyinstallerArgs -join ' ')" -ForegroundColor Gray
Write-Host ""

& pyinstaller @pyinstallerArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}

# Check output
if (Test-Path "dist\SecurityMonitor.exe") {
    $exeSize = (Get-Item "dist\SecurityMonitor.exe").Length / 1MB
    Write-Host ""
    Write-Host "✅ Build successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📂 Output:" -ForegroundColor Cyan
    Write-Host "  Location: dist\SecurityMonitor.exe" -ForegroundColor White
    Write-Host "  Size: $([math]::Round($exeSize, 2)) MB" -ForegroundColor White
    Write-Host ""
    Write-Host "🚀 Run with:" -ForegroundColor Yellow
    Write-Host "  .\dist\SecurityMonitor.exe" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Executable not found in dist\ directory!" -ForegroundColor Red
    exit 1
}

# Optional: Create installer
if (-not $Debug) {
    Write-Host "💡 Tip: Create installer with NSIS or Inno Setup" -ForegroundColor Cyan
    Write-Host "   Or use: iscc (Inno Setup Compiler)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "✅ Packaging complete!" -ForegroundColor Green
