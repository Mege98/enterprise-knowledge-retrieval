[CmdletBinding()]
param([string]$Version = "0.4.0")

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$DistRoot = Join-Path $ProjectRoot "dist"
$PackageDir = Join-Path $DistRoot "EnterpriseKnowledgeRetrieval"
$ZipPath = Join-Path $DistRoot "EnterpriseKnowledgeRetrieval-Windows-x64-v$Version.zip"

if (-not (Test-Path -LiteralPath (Join-Path $PackageDir "EnterpriseKnowledgeRetrieval.exe"))) {
    throw "请先运行 scripts/build_windows.ps1。"
}

foreach ($name in @("README.md", "LICENSE", "THIRD_PARTY_NOTICES.md")) {
    Copy-Item -LiteralPath (Join-Path $ProjectRoot $name) -Destination (Join-Path $PackageDir $name) -Force
}
Get-ChildItem -LiteralPath $PackageDir -Recurse -File | Where-Object {
    $_.Extension -in ".log", ".sqlite", ".db" -or $_.Name -eq ".env"
} | ForEach-Object { Remove-Item -LiteralPath $_.FullName -Force }

if (Test-Path -LiteralPath $ZipPath) {
    Remove-Item -LiteralPath $ZipPath -Force
}
Compress-Archive -Path (Join-Path $PackageDir "*") -DestinationPath $ZipPath -CompressionLevel Optimal
$Hash = Get-FileHash -Algorithm SHA256 -LiteralPath $ZipPath
Write-Host $ZipPath -ForegroundColor Green
Write-Host "SHA256: $($Hash.Hash)"
