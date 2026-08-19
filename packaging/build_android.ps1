param(
    [string]$Python = ""
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$OutputDirectory = Join-Path $ProjectRoot "dist\android"

if ([string]::IsNullOrWhiteSpace($Python)) {
    $Python = Join-Path (Split-Path $ProjectRoot -Parent) ".venv\Scripts\python.exe"
}

if (-not (Test-Path $Python)) {
    throw "No se encontro Python en '$Python'. Usa -Python con la ruta de un interprete configurado."
}

$missing = @()
if (-not $env:ANDROID_HOME -and -not $env:ANDROID_SDK_ROOT) { $missing += "ANDROID_HOME o ANDROID_SDK_ROOT" }
if (-not $env:ANDROID_NDK_ROOT) { $missing += "ANDROID_NDK_ROOT" }
if (-not (Get-Command javac -ErrorAction SilentlyContinue)) { $missing += "JDK/javac" }
if (-not (Get-Command adb -ErrorAction SilentlyContinue)) { $missing += "Android platform-tools/adb" }
if (-not (Get-Command pyside6-android-deploy -ErrorAction SilentlyContinue)) { $missing += "pyside6-android-deploy" }

if ($missing.Count -gt 0) {
    throw ("No se puede crear la APK. Faltan: " + ($missing -join ", ") + ". Consulta packaging/ANDROID_BUILD.md.")
}

New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
Push-Location $ProjectRoot
try {
    & pyside6-android-deploy --help | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "pyside6-android-deploy no pudo iniciarse." }
    Write-Host "El toolchain Android esta disponible. Configura el proyecto del deployer y vuelve a ejecutar este script con su configuracion." -ForegroundColor Green
} finally {
    Pop-Location
}
