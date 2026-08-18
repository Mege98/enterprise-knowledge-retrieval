[CmdletBinding()]
param(
    [switch]$AllowOwnerPlaceholder,
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot
$Failed = $false

function Fail([string]$Message) { $script:Failed = $true; Write-Host "FAIL: $Message" -ForegroundColor Red }
function Pass([string]$Message) { Write-Host "PASS: $Message" -ForegroundColor Green }

$Excluded = '[\\/](\.git|\.venv|\.build-venv|build|dist|__pycache__)[\\/]'
$Files = Get-ChildItem -LiteralPath $ProjectRoot -Recurse -Force -File | Where-Object { $_.FullName -notmatch $Excluded }
$ForbiddenFiles = $Files | Where-Object {
    $_.Extension -in '.sqlite', '.db', '.exe', '.msi', '.zip', '.7z', '.log' -or
    $_.Name -in '.env', 'settings.json', 'ui_state.json', 'conversations.json'
}
if ($ForbiddenFiles) { Fail "Local data or build artifacts found: $($ForbiddenFiles.Name -join ', ')" } else { Pass "Release file type check passed" }

$TextFiles = $Files | Where-Object { $_.Extension -in '.py', '.md', '.toml', '.txt', '.yml', '.yaml', '.json', '.ps1', '.example' }
foreach ($token in @( (([char]0x4E49).ToString() + [char]0x548C), (([char]0x8F66).ToString() + [char]0x6865), ('yi' + 'he'), ('ax' + 'le') )) {
    if ($TextFiles | Select-String -SimpleMatch $token -CaseSensitive:$false) { Fail "Legacy brand marker found" }
}
foreach ($pattern in @(
    '-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----',
    'sk-[A-Za-z0-9_-]{20,}',
    'github_pat_[A-Za-z0-9_]{20,}',
    'gh[pousr]_[A-Za-z0-9]{20,}',
    'AKIA[0-9A-Z]{16}'
)) {
    if ($TextFiles | Select-String -Pattern $pattern) { Fail "Possible secret pattern found: $pattern" }
}

$OwnerToken = 'github.com/' + 'OWNER/'
if (($TextFiles | Select-String -SimpleMatch $OwnerToken) -and -not $AllowOwnerPlaceholder) {
    Fail "GitHub OWNER placeholder has not been replaced"
} elseif ($AllowOwnerPlaceholder) {
    Write-Host "WARN: GitHub OWNER placeholder temporarily allowed" -ForegroundColor Yellow
}

& $Python -m compileall -q launcher.py rag_core.py enterprise_knowledge_retrieval.py
if ($LASTEXITCODE -ne 0) { Fail "Python syntax check failed" } else { Pass "Python syntax check passed" }
& $Python -m unittest -v test_release_readiness.py
if ($LASTEXITCODE -ne 0) { Fail "Automated tests failed" } else { Pass "Automated tests passed" }
if ($Failed) { throw "Pre-publish checks failed." }
Write-Host "Open-source pre-publish checks passed." -ForegroundColor Green
