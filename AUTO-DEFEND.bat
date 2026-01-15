@echo off
REM AUTONOMOUS DEFENSE AGENT - WINDOWS
REM Auto-executes defensive measures

echo ============================================
echo   AUTONOMOUS DEFENSE AGENT - ACTIVE
echo ============================================
echo.

REM Check for admin
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [ERROR] Requires Administrator privileges!
    echo Right-click this file and select "Run as Administrator"
    pause
    exit /b 1
)

echo [OK] Running as Administrator
echo.

REM Create output directory
set OUTPUT_DIR=%USERPROFILE%\Desktop\Defense-Log-%date:~-4,4%%date:~-10,2%%date:~-7,2%-%time:~0,2%%time:~3,2%%time:~6,2%
set OUTPUT_DIR=%OUTPUT_DIR: =0%
mkdir "%OUTPUT_DIR%" 2>nul

echo [ACTION] Output directory: %OUTPUT_DIR%
echo.

REM ============================================
REM STEP 1: KILL SUSPICIOUS PROCESSES
REM ============================================

echo [STEP 1] Scanning for suspicious processes...

tasklist | findstr /i "inject exploit payload pwn backdoor rootkit" > "%OUTPUT_DIR%\suspicious-processes.txt"

for /f "tokens=1" %%a in ('tasklist ^| findstr /i "inject exploit payload"') do (
    echo [KILL] Terminating suspicious process: %%a
    taskkill /F /IM %%a >nul 2>&1
)

echo [OK] Process scan complete
echo.

REM ============================================
REM STEP 2: NETWORK ISOLATION
REM ============================================

echo [STEP 2] Activating firewall...

netsh advfirewall set allprofiles state on
netsh advfirewall set allprofiles firewallpolicy blockinbound,allowoutbound

echo [OK] Firewall activated
echo.

REM ============================================
REM STEP 3: DISABLE AUTORUN
REM ============================================

echo [STEP 3] Disabling autorun...

reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v NoDriveTypeAutoRun /t REG_DWORD /d 255 /f >nul 2>&1

echo [OK] Autorun disabled
echo.

REM ============================================
REM STEP 4: COLLECT FORENSICS
REM ============================================

echo [STEP 4] Collecting forensic data...

tasklist > "%OUTPUT_DIR%\processes.txt"
netstat -ano > "%OUTPUT_DIR%\network-connections.txt"
sc query > "%OUTPUT_DIR%\services.txt"
wmic startup get caption,command > "%OUTPUT_DIR%\startup-items.txt"
systeminfo > "%OUTPUT_DIR%\system-info.txt"

echo [OK] Forensics collected
echo.

REM ============================================
REM STEP 5: BIOS INFORMATION
REM ============================================

echo [STEP 5] Collecting BIOS information...

wmic bios get /all /format:list > "%OUTPUT_DIR%\bios-info.txt"
wmic computersystem get /all /format:list > "%OUTPUT_DIR%\system-config.txt"

echo [OK] BIOS data collected
echo.

REM ============================================
REM CONTINUOUS MONITORING
REM ============================================

echo ============================================
echo   DEFENSE MEASURES ACTIVATED
echo ============================================
echo.
echo Forensic data saved to:
echo %OUTPUT_DIR%
echo.
echo Starting continuous monitoring...
echo Press Ctrl+C to stop
echo.

:monitor_loop
timeout /t 5 >nul

REM Check for new suspicious processes
tasklist | findstr /i "inject exploit payload pwn" > nul
if %errorLevel% EQU 0 (
    echo [ALERT] Suspicious process detected! >> "%OUTPUT_DIR%\alerts.log"
    echo [%date% %time%] ALERT: Suspicious process detected

    REM Kill them
    for /f "tokens=1" %%a in ('tasklist ^| findstr /i "inject exploit payload"') do (
        echo [KILL] %%a
        taskkill /F /IM %%a >nul 2>&1
    )
)

goto monitor_loop
