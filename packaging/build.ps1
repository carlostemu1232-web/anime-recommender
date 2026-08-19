$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot '..\.venv\Scripts\python.exe'

if (-not (Test-Path $python)) {
    throw "Virtual environment not found at $python"
}

Push-Location $projectRoot
try {
    & $python -m PyInstaller --noconfirm --clean packaging\AniVerse.spec

    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE"
    }

    Write-Host "Build complete: $projectRoot\dist\AniVerse\AniVerse.exe"
} finally {
    Pop-Location
}
