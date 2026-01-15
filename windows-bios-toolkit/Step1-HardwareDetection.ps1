# ════════════════════════════════════════════════════════════════
# BIOS INVESTIGATION TOOLKIT - STEP 1: Hardware Detection
# ════════════════════════════════════════════════════════════════
# Created for: BIOS Security Investigation
# Purpose: Detect hardware, BIOS type, and collect system info
# ════════════════════════════════════════════════════════════════

Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🔍 BIOS INVESTIGATION - HARDWARE DETECTION" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  WARNING: Not running as Administrator" -ForegroundColor Yellow
    Write-Host "   Some information may not be available." -ForegroundColor Yellow
    Write-Host "   Right-click PowerShell and 'Run as Administrator' for full access." -ForegroundColor Yellow
    Write-Host ""
}

# Create output directory
$outputDir = "$env:USERPROFILE\Desktop\BIOS-Investigation"
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

Write-Host "📁 Output Directory: $outputDir" -ForegroundColor Green
Write-Host ""

# ═══════════════════════════════════════════════════════════════
# SYSTEM INFORMATION
# ═══════════════════════════════════════════════════════════════

Write-Host "📊 Collecting System Information..." -ForegroundColor Yellow

$report = @"
════════════════════════════════════════════════════════════════
BIOS SECURITY INVESTIGATION REPORT
════════════════════════════════════════════════════════════════
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Computer: $env:COMPUTERNAME
User: $env:USERNAME
════════════════════════════════════════════════════════════════

"@

# System Info
$computerSystem = Get-WmiObject -Class Win32_ComputerSystem
$os = Get-WmiObject -Class Win32_OperatingSystem

$report += @"

[SYSTEM INFORMATION]
------------------------------------------------------------
Manufacturer:    $($computerSystem.Manufacturer)
Model:           $($computerSystem.Model)
OS:              $($os.Caption)
OS Version:      $($os.Version)
Architecture:    $($os.OSArchitecture)
Install Date:    $($os.ConvertToDateTime($os.InstallDate))

"@

Write-Host "  ✓ System information collected" -ForegroundColor Green

# ═══════════════════════════════════════════════════════════════
# BIOS INFORMATION
# ═══════════════════════════════════════════════════════════════

Write-Host "🔧 Collecting BIOS Information..." -ForegroundColor Yellow

$bios = Get-WmiObject -Class Win32_BIOS
$report += @"

[BIOS INFORMATION]
------------------------------------------------------------
Manufacturer:    $($bios.Manufacturer)
Name:            $($bios.Name)
Version:         $($bios.Version)
Release Date:    $($bios.ConvertToDateTime($bios.ReleaseDate))
SMBIOS Version:  $($bios.SMBIOSBIOSVersion)
Serial Number:   $($bios.SerialNumber)

"@

Write-Host "  ✓ BIOS information collected" -ForegroundColor Green

# ═══════════════════════════════════════════════════════════════
# UEFI vs LEGACY BIOS DETECTION
# ═══════════════════════════════════════════════════════════════

Write-Host "🎯 Detecting Firmware Type..." -ForegroundColor Yellow

$firmwareType = "UNKNOWN"
try {
    $firmwareEnv = [System.Environment]::GetEnvironmentVariable("firmware_type")
    if ($firmwareEnv -eq "UEFI") {
        $firmwareType = "UEFI"
    } else {
        # Check for EFI system partition
        $efiPartition = Get-Partition | Where-Object { $_.GptType -eq '{c12a7328-f81f-11d2-ba4b-00a0c93ec93b}' }
        if ($efiPartition) {
            $firmwareType = "UEFI"
        } else {
            $firmwareType = "Legacy BIOS"
        }
    }
} catch {
    $firmwareType = "Legacy BIOS (assumed)"
}

$report += @"

[FIRMWARE TYPE]
------------------------------------------------------------
Type:            $firmwareType

"@

Write-Host "  ✓ Firmware type: $firmwareType" -ForegroundColor Green

# ═══════════════════════════════════════════════════════════════
# CPU INFORMATION
# ═══════════════════════════════════════════════════════════════

Write-Host "🖥️  Collecting CPU Information..." -ForegroundColor Yellow

$cpu = Get-WmiObject -Class Win32_Processor
$report += @"

[CPU INFORMATION]
------------------------------------------------------------
Manufacturer:    $($cpu.Manufacturer)
Name:            $($cpu.Name)
Cores:           $($cpu.NumberOfCores)
Logical CPUs:    $($cpu.NumberOfLogicalProcessors)
Architecture:    $($cpu.DataWidth)-bit

"@

Write-Host "  ✓ CPU information collected" -ForegroundColor Green

# ═══════════════════════════════════════════════════════════════
# SECURITY FEATURES
# ═══════════════════════════════════════════════════════════════

Write-Host "🔒 Checking Security Features..." -ForegroundColor Yellow

$report += @"

[SECURITY FEATURES]
------------------------------------------------------------

"@

# Check Secure Boot
try {
    $secureBoot = Confirm-SecureBootUEFI
    $report += "Secure Boot:     $($secureBoot ? 'ENABLED' : 'DISABLED')`n"
    Write-Host "  ✓ Secure Boot: $($secureBoot ? 'ENABLED' : 'DISABLED')" -ForegroundColor $(if($secureBoot) {'Green'} else {'Yellow'})
} catch {
    $report += "Secure Boot:     Not supported or not running UEFI`n"
    Write-Host "  ⚠️  Secure Boot: Not available" -ForegroundColor Yellow
}

# Check BitLocker
$bitlockerVolumes = Get-BitLockerVolume -ErrorAction SilentlyContinue
if ($bitlockerVolumes) {
    $report += "BitLocker:       DETECTED`n"
    Write-Host "  ✓ BitLocker: Detected" -ForegroundColor Green
} else {
    $report += "BitLocker:       Not detected`n"
    Write-Host "  ⚠️  BitLocker: Not detected" -ForegroundColor Yellow
}

# Check Windows Defender
$defenderStatus = Get-MpComputerStatus -ErrorAction SilentlyContinue
if ($defenderStatus) {
    $report += "Defender:        $($defenderStatus.AntivirusEnabled ? 'ENABLED' : 'DISABLED')`n"
    Write-Host "  ✓ Windows Defender: $($defenderStatus.AntivirusEnabled ? 'ENABLED' : 'DISABLED')" -ForegroundColor Green
}

# ═══════════════════════════════════════════════════════════════
# SAVE REPORT
# ═══════════════════════════════════════════════════════════════

$reportPath = "$outputDir\HardwareReport.txt"
$report | Out-File -FilePath $reportPath -Encoding UTF8

Write-Host ""
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ HARDWARE DETECTION COMPLETE" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📄 Report saved to: $reportPath" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Review the hardware report above" -ForegroundColor White
Write-Host "  2. Run Step2-BIOSForensics.ps1 to check for infections" -ForegroundColor White
Write-Host ""

# Open report
$openReport = Read-Host "Open report now? (Y/N)"
if ($openReport -eq 'Y' -or $openReport -eq 'y') {
    Start-Process notepad.exe -ArgumentList $reportPath
}
