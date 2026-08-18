[CmdletBinding()]
param(
    [switch]$Clean,
    [string]$BootstrapPython = "python"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Venv = Join-Path $ProjectRoot ".build-venv"
$Python = Join-Path $Venv "Scripts\python.exe"
Set-Location $ProjectRoot

if ($Clean) {
    foreach ($name in @("build", "dist")) {
        $target = Join-Path $ProjectRoot $name
        if (Test-Path -LiteralPath $target) {
            Remove-Item -LiteralPath $target -Recurse -Force
        }
    }
}

if (-not (Test-Path -LiteralPath $Python)) {
    & $BootstrapPython -m venv $Venv
}
& $Python -m pip install --upgrade pip
& $Python -m pip install -r requirements-build.txt
& $Python -m PyInstaller --noconfirm --clean EnterpriseKnowledgeRetrieval.spec
Write-Host "Build completed: $ProjectRoot\dist\EnterpriseKnowledgeRetrieval" -ForegroundColor Green
