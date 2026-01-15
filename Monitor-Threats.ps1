# CONTINUOUS THREAT MONITORING
# Watches for suspicious activity in real-time

Write-Host "👁️  THREAT MONITOR - ACTIVE" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

$logFile = "$env:USERPROFILE\Desktop\threat-monitor-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

function Write-ThreatLog {
    param($message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $message" | Add-Content -Path $logFile
    Write-Host "[$timestamp] $message" -ForegroundColor Red
}

# Baseline processes
$baselineProcesses = (Get-Process).Name

while ($true) {
    Start-Sleep -Seconds 5

    # Check for new processes
    $currentProcesses = (Get-Process).Name
    $newProcesses = Compare-Object -ReferenceObject $baselineProcesses -DifferenceObject $currentProcesses |
                    Where-Object { $_.SideIndicator -eq '=>' }

    foreach ($proc in $newProcesses) {
        $processName = $proc.InputObject

        # Check if suspicious
        if ($processName -match "(?i)(inject|exploit|payload|pwn|shell|cmd|powershell|wscript)") {
            Write-ThreatLog "🚨 SUSPICIOUS PROCESS DETECTED: $processName"

            # Optionally kill it
            $response = Read-Host "Kill process $processName? (Y/N)"
            if ($response -eq 'Y') {
                Get-Process -Name $processName -ErrorAction SilentlyContinue | Stop-Process -Force
                Write-ThreatLog "✓ Killed process: $processName"
            }
        }
    }

    # Update baseline
    $baselineProcesses = $currentProcesses

    # Check network connections for suspicious IPs
    $connections = Get-NetTCPConnection -State Established -ErrorAction SilentlyContinue
    foreach ($conn in $connections) {
        # Check for non-standard ports
        if ($conn.RemotePort -in @(4444, 31337, 1337, 8080, 6666)) {
            Write-ThreatLog "🚨 SUSPICIOUS CONNECTION: $($conn.RemoteAddress):$($conn.RemotePort)"
        }
    }
}
