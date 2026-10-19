# Build script for Windows Inno Setup installer
param (
    [string]$Version = "1.0.0"
)

$ErrorActionPreference = "Stop"

$RootDir = Resolve-Path "$PSScriptRoot\..\.."
$DistExe = Join-Path $RootDir "dist\vocalis.exe"

if (-not (Test-Path $DistExe)) {
    Write-Host "vocalis.exe not found in dist/. Running PyInstaller first..." -ForegroundColor Yellow
    & pyinstaller "$RootDir\vocalis.spec"
    if (-not (Test-Path $DistExe)) {
        Write-Error "Failed to build vocalis.exe."
    }
}

$IsccPaths = @(
    "ISCC.exe",
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe",
    "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
)

$IsccExe = $null
foreach ($path in $IsccPaths) {
    if (Get-Command $path -ErrorAction SilentlyContinue) {
        $IsccExe = $path
        break
    }
    if (Test-Path $path) {
        $IsccExe = $path
        break
    }
}

if (-not $IsccExe) {
    Write-Error "Inno Setup compiler (ISCC.exe) was not found. Please install Inno Setup 6 (e.g. 'winget install JRSoftware.InnoSetup' or 'choco install innosetup')."
}

Write-Host "Compiling Windows installer with $IsccExe..." -ForegroundColor Cyan
& $IsccExe /DMyAppVersion="$Version" "$PSScriptRoot\vocalis.iss"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Installer created successfully in dist/!" -ForegroundColor Green
} else {
    Write-Error "Inno Setup failed with exit code $LASTEXITCODE."
}
