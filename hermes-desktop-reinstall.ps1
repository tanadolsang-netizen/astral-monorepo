# Hermes DESKTOP - reinstall (keeps your config, keys, memories, sessions)
# Run:  right-click > "Run with PowerShell"
#   or: powershell -ExecutionPolicy Bypass -File C:\AI\hermes-desktop-reinstall.ps1
# Log:  C:\AI\hermes-desktop-reinstall.log

$ErrorActionPreference = 'Continue'
$Root   = 'C:\AI'
$Stamp  = Get-Date -Format 'yyyyMMdd-HHmmss'
$Log    = "$Root\hermes-desktop-reinstall.log"
$Setup  = "$env:TEMP\Hermes-Setup.exe"
$Url    = 'https://hermes-assets.nousresearch.com/Hermes-Setup.exe'

Start-Transcript -Path $Log -Force | Out-Null
function Step($t) { Write-Host "`n==== $t ====" -ForegroundColor Cyan }

# ---------- 1. Where is the data? ----------
Step '1. Hermes data folder'
$userHome = [Environment]::GetEnvironmentVariable('HERMES_HOME','User')
if ($userHome) { $env:HERMES_HOME = $userHome }
$DataDir = @($env:HERMES_HOME, "$Root\hermes\data", "$env:LOCALAPPDATA\hermes") |
           Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
Write-Host "HERMES_HOME = $env:HERMES_HOME"
Write-Host "Data folder used: $DataDir"

# ---------- 2. Current desktop install ----------
Step '2. Currently installed Hermes Desktop'
$regPaths = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
            'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
            'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*'
$apps = Get-ItemProperty $regPaths -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName -match 'Hermes' }
if ($apps) { $apps | ForEach-Object { Write-Host "$($_.DisplayName)  v$($_.DisplayVersion)  at $($_.InstallLocation)" } }
else { Write-Host 'Hermes Desktop not found in installed programs' }

# ---------- 3. Backup data ----------
if ($DataDir) {
    Step '3. Backing up data'
    $Backup = "$Root\hermes-backup-$Stamp"
    robocopy $DataDir $Backup /E /R:1 /W:1 /NFL /NDL /NP /XD hermes-agent bin tools node_modules .venv venv __pycache__ .git | Out-Null
    Write-Host "Backup: $Backup"
}

# ---------- 4. Close Hermes ----------
Step '4. Closing Hermes Desktop / agent processes'
Get-CimInstance Win32_Process |
  Where-Object { $_.ProcessId -ne $PID -and ($_.Name -match 'hermes' -or $_.CommandLine -match 'hermes') -and $_.CommandLine -notmatch 'reinstall' } |
  ForEach-Object {
    Write-Host "stopping PID $($_.ProcessId): $($_.Name)"
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
  }
Start-Sleep -Seconds 2

# ---------- 4b. Point Desktop at the C:\AI install ----------
Step '4b. Pinning Desktop to C:\AI\hermes'
$AgentRoot = "$Root\hermes\hermes-agent"
if (Test-Path $AgentRoot) {
    [Environment]::SetEnvironmentVariable('HERMES_DESKTOP_HERMES_ROOT', $AgentRoot, 'User')
    $env:HERMES_DESKTOP_HERMES_ROOT = $AgentRoot
    Write-Host "HERMES_DESKTOP_HERMES_ROOT = $AgentRoot"
} else { Write-Host "$AgentRoot not found - Desktop will use its own install" -ForegroundColor Yellow }
Write-Host "HERMES_HOME (User) = $([Environment]::GetEnvironmentVariable('HERMES_HOME','User'))"

# ---------- 5. Download latest installer ----------
Step '5. Downloading latest Hermes-Setup.exe'
try {
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $Url -OutFile $Setup -UseBasicParsing
    Write-Host ("Downloaded {0:N1} MB -> $Setup" -f ((Get-Item $Setup).Length / 1MB))
} catch {
    Write-Host "DOWNLOAD FAILED: $_" -ForegroundColor Red
    Write-Host "Download it manually from https://hermes-agent.nousresearch.com/desktop"
    Stop-Transcript | Out-Null; Read-Host 'Press Enter to close'; exit 1
}

# ---------- 6. Run installer (installs over the old version) ----------
Step '6. Running installer - follow the setup window'
$p = Start-Process -FilePath $Setup -PassThru -Wait
Write-Host "Installer exit code: $($p.ExitCode)"

# ---------- 7. Verify ----------
Step '7. Verify'
$apps = Get-ItemProperty $regPaths -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName -match 'Hermes' }
$apps | ForEach-Object { Write-Host "Installed: $($_.DisplayName)  v$($_.DisplayVersion)" }
$cmd = Get-Command hermes -ErrorAction SilentlyContinue
if ($cmd) { hermes --version; hermes doctor } else { Write-Host 'hermes CLI not on PATH in this window (open a new PowerShell to check)' }

Step 'DONE - open Hermes from the Start menu'
Write-Host "Log: $Log"
Stop-Transcript | Out-Null
Read-Host 'Press Enter to close'
