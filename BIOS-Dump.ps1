# BIOS FIRMWARE DUMP SCRIPT
# WARNING: Requires Administrator privileges

Write-Host "🔧 BIOS FIRMWARE DUMP UTILITY" -ForegroundColor Cyan

$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ ERROR: Must run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    pause
    exit
}

$outDir = "$env:USERPROFILE\Desktop\BIOS-BACKUP-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
New-Item -ItemType Directory -Path $outDir -Force | Out-Null

Write-Host "Dumping BIOS information..." -ForegroundColor Yellow

# BIOS details
Get-WmiObject -Class Win32_BIOS | Out-File "$outDir\bios-info.txt"

# System firmware table (UEFI variables if available)
try {
    Get-SecureBootUEFI -Name PK -OutputFilePath "$outDir\secureboot-pk.bin" -ErrorAction SilentlyContinue
    Write-Host "✓ Secure Boot keys dumped" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Secure Boot keys not accessible" -ForegroundColor Yellow
}

# Full system info
systeminfo > "$outDir\systeminfo.txt"

# Registry: Boot configuration
reg export "HKLM\SYSTEM\CurrentControlSet\Control\SecureBoot" "$outDir\secureboot-registry.reg" /y 2>$null

Write-Host ""
Write-Host "✅ BIOS data backed up to: $outDir" -ForegroundColor Green
Write-Host ""
Write-Host "To dump actual firmware (advanced):" -ForegroundColor Yellow
Write-Host "  1. Download: https://github.com/chipsec/chipsec" -ForegroundColor White
Write-Host "  2. Run: python -m chipsec_main --dump_rom bios_backup.bin" -ForegroundColor White
Write-Host ""
