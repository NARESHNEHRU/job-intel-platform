
$root = $PSScriptRoot

Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root'; .\venv\Scripts\Activate.ps1; chroma run --path data/chroma --port 8001"

Start-Sleep -Seconds 5

Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root'; .\venv\Scripts\Activate.ps1; uvicorn backend.app.api.main:app --reload --reload-dir backend"

Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root\frontend'; npm run dev"

Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root'; .\venv\Scripts\Activate.ps1; python -m backend.scripts.run_all"
