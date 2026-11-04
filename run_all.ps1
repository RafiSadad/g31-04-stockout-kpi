# Rebuild everything on Windows PowerShell.
# Default: the 4 CSVs are in the folder above this repository. Override with $env:DATA_DIR = "C:\path\to\csvs".
# Usage: powershell -ExecutionPolicy Bypass -File run_all.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not $env:DATA_DIR) { $env:DATA_DIR = ".." }
foreach ($f in "category_tree.csv", "events.csv", "item_properties_part1.csv", "item_properties_part2.csv") {
    if (-not (Test-Path (Join-Path $env:DATA_DIR $f))) { throw "Missing $f in DATA_DIR=$($env:DATA_DIR)" }
}
foreach ($s in "01_extract_properties", "02_explore_snapshots", "03_build_kpis", "04_demand_features", "05_docs") {
    Write-Host "== $s"
    python "scripts/$s.py"
    if ($LASTEXITCODE -ne 0) { throw "$s failed" }
}
Write-Host "Done. Check the Reconcile sheet in outputs/G31-04 KPI Tables.xlsx"
