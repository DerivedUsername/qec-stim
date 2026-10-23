# One-time setup on Windows. Run from the repo root:  .\setup.ps1
# If scripts are blocked:  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
# and, for a downloaded zip:  Get-ChildItem -Recurse | Unblock-File

$ErrorActionPreference = "Stop"

if (-not (Test-Path .venv)) {
    python -m venv .venv
}
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

Write-Host "`n--- Quick threshold run ---"
python scripts\threshold.py --quick --out results\quick

Write-Host "`n--- Tests (Parts 2 and 3 skip until implemented) ---"
pytest -q

if (-not (Test-Path .git)) {
    git init
    git add -A
    git commit -m "Scaffold: surface-code threshold, tests, agent rules"
}
