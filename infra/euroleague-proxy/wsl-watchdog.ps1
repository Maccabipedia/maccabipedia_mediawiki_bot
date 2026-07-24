# WSL health watchdog. Run every 5 minutes by the WslWatchdog scheduled task.
#
# Handles TWO failure modes; the original `wsl -e true` one-liner only handled
# the first:
#
#   1. WSL is DOWN  -- `wsl -e true` boots the distro. tinyproxy and
#      claude-mobile.service are enabled (+ linger), so they follow on their own.
#   2. WSL is WEDGED -- the VM is alive but unresponsive (guest memory
#      exhaustion; the kernel can wedge before the OOM killer is ever
#      scheduled, so nothing is reclaimed and nothing recovers). Here
#      `wsl -e true` blocks forever instead of failing, so the old watchdog
#      spun uselessly every 5 minutes and the box needed a human at the
#      keyboard to type `wsl --shutdown`. That is the case this script exists
#      for: after $MaxConsecutiveFailures probe timeouts it issues the
#      shutdown itself and boots the distro back up.
#
# Every probe is bounded by a timeout, so this script can never itself become
# the thing that hangs.
#
# KEEP THIS FILE PURE ASCII. Windows PowerShell 5.1 decodes a BOM-less .ps1 as
# Windows-1252, so a UTF-8 em-dash arrives as three bytes -- one of them 0x94,
# a curly quote that PowerShell honours as a real string delimiter. The result
# is a parse error reported far from the character that caused it. Check with:
#   grep -nP '[^\x00-\x7F]' wsl-watchdog.ps1

$ErrorActionPreference = 'Stop'

# A cold boot of the distro finishes well inside 90s, so a probe that exceeds
# it is genuinely pathological rather than merely slow. At a 5-minute task
# interval, 3 consecutive failures means ~11 minutes of confirmed
# unresponsiveness before we force a restart -- deliberately conservative,
# because `wsl --shutdown` kills whatever the VM was doing. Lower it for
# faster recovery at the cost of more false positives.
$ProbeTimeoutSec         = 90
$ShutdownTimeoutSec      = 60
$BootTimeoutSec          = 120
$MobileTabTimeoutSec     = 60
$MaxConsecutiveFailures  = 3
$MaxLogBytes             = 512KB

$StateDir  = Join-Path $env:LOCALAPPDATA 'wsl-watchdog'
$LogFile   = Join-Path $StateDir 'watchdog.log'
$FailFile  = Join-Path $StateDir 'consecutive-failures.txt'
$LockFile  = Join-Path $StateDir 'watchdog.lock'
$WslExe    = Join-Path $env:SystemRoot 'System32\wsl.exe'

if (-not (Test-Path $StateDir)) { New-Item -ItemType Directory -Path $StateDir -Force | Out-Null }

function Write-Log {
    param([string]$Message)
    $line = "{0} {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Message
    try {
        if ((Test-Path $LogFile) -and ((Get-Item $LogFile).Length -gt $MaxLogBytes)) {
            Move-Item $LogFile "$LogFile.1" -Force
        }
        Add-Content -Path $LogFile -Value $line -Encoding UTF8
    } catch { }
}

# Runs wsl.exe under a hard timeout. On timeout the whole process tree is
# killed -- a wedged `wsl.exe` spawns children that outlive a bare Kill() and
# would otherwise pile up once per tick for the length of the outage.
function Invoke-Wsl {
    param([string]$Arguments, [int]$TimeoutSec)

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName               = $WslExe
    $psi.Arguments              = $Arguments
    $psi.UseShellExecute        = $false
    $psi.CreateNoWindow         = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError  = $true

    $proc = [System.Diagnostics.Process]::Start($psi)
    # Drain both pipes asynchronously: a synchronous ReadToEnd would deadlock
    # against WaitForExit if the child ever filled a pipe buffer.
    $null = $proc.StandardOutput.ReadToEndAsync()
    $null = $proc.StandardError.ReadToEndAsync()

    if ($proc.WaitForExit($TimeoutSec * 1000)) {
        return [pscustomobject]@{ TimedOut = $false; ExitCode = $proc.ExitCode }
    }

    try {
        & "$env:SystemRoot\System32\taskkill.exe" /PID $proc.Id /T /F 2>&1 | Out-Null
    } catch { }
    return [pscustomobject]@{ TimedOut = $true; ExitCode = $null }
}

# The claude-mobile tmux server dies with WSL, taking its Windows Terminal tab
# with it, and the Startup-folder VBS only reopens that tab at logon -- so a
# mid-session WSL restart leaves the service healed but headless.
# ensure-mobile-tab reopens it once per tmux generation.
#
# Best-effort: a failure here must not fail the watchdog, but it must not
# vanish either. The `if` form (rather than `&&`) keeps the exit code 0 on
# hosts that don't run the mobile session at all, so their logs stay quiet
# while a genuine failure on this host still gets recorded.
function Invoke-MobileTab {
    $result = Invoke-Wsl -TimeoutSec $MobileTabTimeoutSec `
        -Arguments '-e bash -lc "if command -v ensure-mobile-tab >/dev/null; then ensure-mobile-tab; fi"'
    if ($result.TimedOut) {
        Write-Log 'WARN ensure-mobile-tab timed out'
    } elseif ($result.ExitCode -ne 0) {
        Write-Log ("WARN ensure-mobile-tab exited {0}" -f $result.ExitCode)
    }
}

function Get-FailureCount {
    if (-not (Test-Path $FailFile)) { return 0 }
    $raw = (Get-Content $FailFile -Raw -ErrorAction SilentlyContinue)
    $parsed = 0
    if ([int]::TryParse(($raw -replace '\s', ''), [ref]$parsed)) { return $parsed }
    return 0
}

function Set-FailureCount {
    param([int]$Count)
    Set-Content -Path $FailFile -Value $Count -Encoding ASCII
}

# The scheduled task is configured MultipleInstances=IgnoreNew, but that only
# guards overlap when the action actually blocks -- keep a lock of our own so a
# stuck run can never be lapped by the next tick.
$lockStream = $null
try {
    $lockStream = [System.IO.File]::Open($LockFile, 'OpenOrCreate', 'ReadWrite', 'None')
} catch {
    Write-Log 'SKIP previous run still in progress'
    exit 0
}

try {
    $probe = Invoke-Wsl -Arguments '-e true' -TimeoutSec $ProbeTimeoutSec

    if (-not $probe.TimedOut -and $probe.ExitCode -eq 0) {
        if ((Get-FailureCount) -gt 0) {
            Write-Log 'OK wsl responsive again -- clearing failure count'
            Set-FailureCount 0
        }
        Invoke-MobileTab
        exit 0
    }

    if ($probe.TimedOut) {
        $failures = (Get-FailureCount) + 1
        Set-FailureCount $failures
        Write-Log ("HANG probe timed out after ${ProbeTimeoutSec}s ({0}/{1})" -f $failures, $MaxConsecutiveFailures)

        if ($failures -lt $MaxConsecutiveFailures) { exit 1 }

        # Confirmed wedge. `wsl --shutdown` tears the VM down at the hypervisor
        # level, which is the only thing that clears this state -- and until
        # now the only thing nobody could do remotely.
        Write-Log 'RECOVER threshold reached -- issuing wsl --shutdown'
        $shutdown = Invoke-Wsl -Arguments '--shutdown' -TimeoutSec $ShutdownTimeoutSec
        if ($shutdown.TimedOut) {
            Write-Log 'ERROR wsl --shutdown itself timed out -- leaving count set for next tick'
            exit 1
        }

        Start-Sleep -Seconds 5
        $boot = Invoke-Wsl -Arguments '-e true' -TimeoutSec $BootTimeoutSec
        if ($boot.TimedOut -or $boot.ExitCode -ne 0) {
            Write-Log 'ERROR distro did not come back after shutdown -- will retry next tick'
            exit 1
        }

        Write-Log 'RECOVER distro is back up'
        Set-FailureCount 0
        Invoke-MobileTab
        exit 0
    }

    # Probe returned promptly but non-zero. WSL is reachable and answering, so
    # this is not the wedge case -- don't let it accumulate toward a restart.
    Write-Log ("WARN probe exited {0} -- not a hang, not counting toward restart" -f $probe.ExitCode)
    exit $probe.ExitCode
}
finally {
    if ($lockStream) { $lockStream.Close() }
}
