param(
    [string]$LogLevel = 'info'
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$projectPython = Join-Path $projectRoot '.venv/Scripts/python.exe'

if (-not (Test-Path -LiteralPath $projectPython)) {
    throw 'Project virtual environment is missing. Install requirements first.'
}

Push-Location $projectRoot
try {
    # Windows development uses one process; Linux can use the default prefork pool.
    & $projectPython -m celery -A ai_asistant_with_sina worker --pool=solo --concurrency=1 --loglevel=$LogLevel --hostname=sina@%h
    if ($LASTEXITCODE -ne 0) {
        throw "Celery worker exited with code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}
