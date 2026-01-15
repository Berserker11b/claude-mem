@echo off
REM ═══════════════════════════════════════════════════════════════
REM MASTER CONTROL - Top-level factory orchestrator
REM Monitors the factory itself and rebuilds if destroyed
REM ═══════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion

echo ═══════════════════════════════════════════════════════════════
echo   👑 MASTER CONTROL - INITIALIZING
echo ═══════════════════════════════════════════════════════════════
echo.

set MASTER_DIR=%USERPROFILE%\.defense-master
set FACTORY_DIR=%USERPROFILE%\.defense-factory
set BACKUP_DIR=%MASTER_DIR%\backups

REM Create master structure
if not exist "%MASTER_DIR%" mkdir "%MASTER_DIR%"
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

echo [MASTER] Control directory: %MASTER_DIR%
echo.

REM ═══════════════════════════════════════════════════════════════
REM BACKUP ALL CRITICAL FILES
REM ═══════════════════════════════════════════════════════════════

echo [BACKUP] Creating redundant copies...

REM Backup this script itself
copy "%~f0" "%BACKUP_DIR%\MASTER-CONTROL.bat" >nul 2>&1
copy "%~f0" "%MASTER_DIR%\..\.MASTER-CONTROL-HIDDEN.bat" >nul 2>&1
attrib +h "%MASTER_DIR%\..\.MASTER-CONTROL-HIDDEN.bat"

REM Backup factory
if exist "%~dp0FACTORY.bat" (
    copy "%~dp0FACTORY.bat" "%BACKUP_DIR%\FACTORY.bat" >nul 2>&1
    copy "%~dp0FACTORY.bat" "%MASTER_DIR%\..\.FACTORY-HIDDEN.bat" >nul 2>&1
    attrib +h "%MASTER_DIR%\..\.FACTORY-HIDDEN.bat"
)

REM Backup defense scripts
if exist "%~dp0AUTO-DEFEND.bat" copy "%~dp0AUTO-DEFEND.bat" "%BACKUP_DIR%\" >nul 2>&1
if exist "%~dp0QUICK-DEFEND.bat" copy "%~dp0QUICK-DEFEND.bat" "%BACKUP_DIR%\" >nul 2>&1

echo [OK] Backups created
echo.

REM ═══════════════════════════════════════════════════════════════
REM CREATE STARTUP PERSISTENCE (optional - user controlled)
REM ═══════════════════════════════════════════════════════════════

set /p PERSIST="Enable auto-start on boot? (Y/N): "
if /i "%PERSIST%"=="Y" (
    echo [PERSIST] Adding to startup...
    copy "%~f0" "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\SystemDefense.bat" >nul 2>&1
    echo [OK] Will auto-start on next boot
) else (
    echo [SKIP] Persistence disabled
)
echo.

REM ═══════════════════════════════════════════════════════════════
REM START FACTORY
REM ═══════════════════════════════════════════════════════════════

echo [MASTER] Launching factory...
echo.

if exist "%~dp0FACTORY.bat" (
    start /min "FACTORY" cmd /c "%~dp0FACTORY.bat"
    echo [OK] Factory started
) else if exist "%BACKUP_DIR%\FACTORY.bat" (
    echo [REBUILD] Factory missing - using backup
    copy "%BACKUP_DIR%\FACTORY.bat" "%~dp0FACTORY.bat"
    start /min "FACTORY" cmd /c "%~dp0FACTORY.bat"
) else if exist "%MASTER_DIR%\..\.FACTORY-HIDDEN.bat" (
    echo [REBUILD] Using hidden backup
    copy "%MASTER_DIR%\..\.FACTORY-HIDDEN.bat" "%~dp0FACTORY.bat"
    start /min "FACTORY" cmd /c "%~dp0FACTORY.bat"
) else (
    echo [ERROR] Cannot find factory - manual rebuild needed
)

echo.

REM ═══════════════════════════════════════════════════════════════
REM MASTER WATCHDOG LOOP
REM ═══════════════════════════════════════════════════════════════

echo ═══════════════════════════════════════════════════════════════
echo   🛡️  MASTER WATCHDOG - ACTIVE
echo ═══════════════════════════════════════════════════════════════
echo.
echo Monitoring factory health...
echo Watching for deletion attacks...
echo Press Ctrl+C to shutdown (NOT recommended during attack)
echo.

:master_loop
timeout /t 10 >nul

REM Check if factory process is running
tasklist /fi "WINDOWTITLE eq FACTORY" 2>nul | findstr /i "cmd.exe" >nul
if errorlevel 1 (
    echo [CRITICAL] Factory process dead - RESPAWNING
    start /min "FACTORY" cmd /c "%~dp0FACTORY.bat"
)

REM Check if factory file exists
if not exist "%~dp0FACTORY.bat" (
    echo [CRITICAL] Factory file deleted - REBUILDING

    if exist "%BACKUP_DIR%\FACTORY.bat" (
        copy "%BACKUP_DIR%\FACTORY.bat" "%~dp0FACTORY.bat" >nul 2>&1
    ) else if exist "%MASTER_DIR%\..\.FACTORY-HIDDEN.bat" (
        copy "%MASTER_DIR%\..\.FACTORY-HIDDEN.bat" "%~dp0FACTORY.bat" >nul 2>&1
    )

    start /min "FACTORY" cmd /c "%~dp0FACTORY.bat"
)

REM Check if defense directory is intact
if not exist "%FACTORY_DIR%" (
    echo [CRITICAL] Factory directory deleted - FULL REBUILD
    start /min "FACTORY" cmd /c "%~dp0FACTORY.bat"
)

REM Self-healing check - restore this script if deleted
if not exist "%~f0" (
    if exist "%BACKUP_DIR%\MASTER-CONTROL.bat" (
        copy "%BACKUP_DIR%\MASTER-CONTROL.bat" "%~f0" >nul 2>&1
    ) else if exist "%MASTER_DIR%\..\.MASTER-CONTROL-HIDDEN.bat" (
        copy "%MASTER_DIR%\..\.MASTER-CONTROL-HIDDEN.bat" "%~f0" >nul 2>&1
    )
)

REM Status report
echo [%time%] Status: Factory running, %NUM_AGENTS% agents active

goto master_loop
