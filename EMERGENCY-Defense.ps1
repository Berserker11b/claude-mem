# EMERGENCY DEFENSE SCRIPT - RUN IMMEDIATELY
# Created: $(Get-Date)
# Purpose: Quick defense against active attack

Write-Host "🚨 EMERGENCY DEFENSE ACTIVATED" -ForegroundColor Red

# 1. Kill suspicious processes
Write-Host "Scanning for suspicious processes..." -ForegroundColor Yellow
Get-Process | Where-Object {
    $_.ProcessName -match "(?i)(inject|exploit|payload|rootkit|backdoor)"
} | Stop-Process -Force -ErrorAction SilentlyContinue

# 2. Block network for suspicious apps
Write-Host "Blocking network access..." -ForegroundColor Yellow
netsh advfirewall set allprofiles state on

# 3. Disable autorun
Write-Host "Disabling autorun..." -ForegroundColor Yellow
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" -Name "NoDriveTypeAutoRun" -Value 255 -ErrorAction SilentlyContinue

# 4. Collect forensics FAST
$outDir = "$env:USERPROFILE\Desktop\EMERGENCY-FORENSICS-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
New-Item -ItemType Directory -Path $outDir -Force | Out-Null

# Running processes
Get-Process | Export-Csv "$outDir\processes.csv" -NoTypeInformation

# Network connections
Get-NetTCPConnection | Export-Csv "$outDir\network.csv" -NoTypeInformation

# Services
Get-Service | Export-Csv "$outDir\services.csv" -NoTypeInformation

# Startup items
Get-CimInstance Win32_StartupCommand | Export-Csv "$outDir\startup.csv" -NoTypeInformation

Write-Host "✅ Forensics saved to: $outDir" -ForegroundColor Green
Write-Host "🔒 Basic defenses activated" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT: Run BIOS-Dump.ps1 to backup firmware" -ForegroundColor Yellow
