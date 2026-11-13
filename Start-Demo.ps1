$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath "dist/index.html")) {
    python tools/build_web.py
    if ($LASTEXITCODE -ne 0) { throw "Could not build the demo. Install requirements-dev.txt first." }
}
Write-Host "RepairScope: http://127.0.0.1:8765"
Write-Host "Keep this window open while using the demo. Ctrl+C stops the local server."
python -m http.server 8765 --bind 127.0.0.1 --directory dist
