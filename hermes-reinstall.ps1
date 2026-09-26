# Hermes Agent - check + reinstall into C:\AI\hermes
# Run:  right-click > "Run with PowerShell"   (or: powershell -ExecutionPolicy Bypass -File C:\AI\hermes-reinstall.ps1)
# Log:  C:\AI\hermes-reinstall.log

$ErrorActionPreference = 'Continue'
$Root       = 'C:\AI'
$NewHome    = "$Root\hermes\data"
$NewInstall = "$Root\hermes\hermes-agent"
$Stamp      = Get-Date -Format 'yyyyMMdd-HHmmss'
$Backup     = "$Root\hermes-backup-$Stamp"
$Log        = "$Root\hermes-reinstall.log"

Start-Transcript -Path $Log -Force | Out-Null
function Step($t) { Write-Host "`n==== $t ====" -ForegroundColor Cyan }

# ---------- 1. CHECK CURRENT INSTALL ----------
Step '1. Current install'
$cmd = Get-Command hermes -ErrorAction SilentlyContinue
if ($cmd) {
    Write-Host "hermes found at: $($cmd.Source)"
    try { hermes --version } catch { Write-Host "hermes --version failed: $_" }
    try { hermes doctor }   catch { Write-Host "hermes doctor failed: $_" }
} else {
    Write-Host 'hermes is NOT on PATH (not installed, or PATH broken)'
}
Write-Host "HERMES_HOME env: $env:HERMES_HOME"

# ---------- 2. FIND OLD DATA ----------
Step '2. Looking for existing Hermes data'
$candidates = @(
    $env:HERMES_HOME,
    "$env:LOCALAPPDATA\hermes",
    "$env:USERPROFILE\.hermes",
    'D:\AI\AOS\hermes',
    'C:\AI\AOS\hermes'
) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -Unique
$candidates | ForEach-Object { Write-Host "found: $_" }
if (-not $candidates) { Write-Host 'no existing data folders found' }

# ---------- 3. STOP RUNNING HERMES ----------
Step '3. Stopping running Hermes processes'
Get-CimInstance Win32_Process |
  Where-Object { $_.ProcessId -ne $PID -and $_.CommandLine -match 'hermes' -and $_.CommandLine -notmatch 'hermes-reinstall' } |
  ForEach-Object {
    Write-Host "stopping PID $($_.ProcessId): $($_.CommandLine)"
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
  }

# ---------- 4. BACKUP (config, .env, memories, sessions, skills) ----------
Step "4. Backing up to $Backup"
$i = 0
foreach ($src in $candidates) {
    $i++
    $dst = "$Backup\$i-" + ($src -replace '[:\\]', '_')
    robocopy $src $dst /E /R:1 /W:1 /NFL /NDL /NP /XD hermes-agent bin tools node_modules .venv venv __pycache__ .git | Out-Null
    Write-Host "backed up $src -> $dst"
}

# ---------- 5. SEED NEW HOME WITH OLD DATA ----------
Step "5. Preparing new data folder $NewHome"
New-Item -ItemType Directory -Force -Path $NewHome | Out-Null
$seed = $candidates | Where-Object { (Test-Path "$_\config.yaml") -or (Test-Path "$_\.env") -or (Test-Path "$_\memories") } | Select-Object -First 1
if ($seed -and -not (Test-Path "$NewHome\config.yaml")) {
    robocopy $seed $NewHome /E /R:1 /W:1 /NFL /NDL /NP /XD hermes-agent bin tools node_modules .venv venv __pycache__ .git | Out-Null
    Write-Host "copied old config/memories from $seed"
} else {
    Write-Host 'no old config to carry over (or new home already has config) - setup wizard will ask'
}

# ---------- 6. INSTALL ----------
Step '6. Installing Hermes Agent (official installer)'
try {
    $script = Invoke-RestMethod 'https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1'
    & ([scriptblock]::Create($script)) -HermesHome $NewHome -InstallDir $NewInstall
} catch {
    Write-Host "INSTALL FAILED: $_" -ForegroundColor Red
}

# ---------- 7. PATH + ENV ----------
Step '7. PATH / HERMES_HOME'
[Environment]::SetEnvironmentVariable('HERMES_HOME', $NewHome, 'User')
$env:HERMES_HOME = $NewHome
$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
Write-Host "User PATH entries containing hermes:"
($userPath -split ';') | Where-Object { $_ -match 'hermes' } | ForEach-Object { Write-Host "  $_" }
$env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + $userPath

# ---------- 8. VERIFY ----------
Step '8. Verify'
$cmd = Get-Command hermes -ErrorAction SilentlyContinue
if ($cmd) {
    Write-Host "hermes now at: $($cmd.Source)"
    hermes --version
    hermes doctor
} else {
    Write-Host 'hermes still not on PATH - open a NEW PowerShell and run: hermes doctor' -ForegroundColor Yellow
}

Step 'DONE'
Write-Host "Backup: $Backup"
Write-Host "Log:    $Log"
Stop-Transcript | Out-Null
Read-Host 'Press Enter to close'
