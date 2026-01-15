@echo off
REM QUICK DEFENSE - NO ADMIN REQUIRED
REM Run this immediately if you can't get admin access

echo ============================================
echo   QUICK DEFENSE MODE (No Admin)
echo ============================================
echo.

set OUTPUT_DIR=%USERPROFILE%\Desktop\QuickDefense-%random%
mkdir "%OUTPUT_DIR%" 2>nul

echo [ACTION] Collecting forensics...

REM Collect what we can without admin
tasklist > "%OUTPUT_DIR%\processes.txt"
netstat -ano > "%OUTPUT_DIR%\connections.txt"

echo [ACTION] Checking for known malware patterns...

REM Scan for suspicious processes
tasklist | findstr /i "inject exploit payload pwn backdoor" > "%OUTPUT_DIR%\suspicious.txt"

echo [OK] Quick scan complete
echo.
echo Results saved to: %OUTPUT_DIR%
echo.
echo If possible, run AUTO-DEFEND.bat as Administrator for full protection
echo.
pause
