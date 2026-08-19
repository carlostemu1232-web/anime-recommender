param(
    [string]$ProjectRoot = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
}

$MobileDir = Join-Path $ProjectRoot "mobile_kivy"

if (-not (Test-Path $MobileDir)) {
    throw "No existe mobile_kivy en $ProjectRoot"
}

$DockerCommand = Get-Command docker -ErrorAction SilentlyContinue
$DockerExe = if ($DockerCommand) {
    $DockerCommand.Source
} else {
    "C:\Program Files\Docker\Docker\resources\bin\docker.exe"
}

if (-not (Test-Path $DockerExe)) {
    throw "Docker no esta instalado o no esta en PATH. Instala Docker Desktop para compilar APK en Windows."
}

& $DockerExe info *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Docker esta instalado pero el daemon no esta activo. Abre Docker Desktop y espera a que diga Running antes de compilar."
}

Push-Location $MobileDir
try {
    & $DockerExe run --rm -v "${MobileDir}:/home/user/hostcwd" -w /home/user/hostcwd kivy/buildozer:latest buildozer -v android debug
    if ($LASTEXITCODE -ne 0) {
        throw "Buildozer fallo al construir la APK"
    }
}
finally {
    Pop-Location
}

Write-Host "APK generada en mobile_kivy/bin" -ForegroundColor Green
