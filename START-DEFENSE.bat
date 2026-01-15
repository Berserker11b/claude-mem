@echo off
REM ═══════════════════════════════════════════════════════════════
REM START DEFENSE - Single-click launch
REM Starts the entire defense system
REM ═══════════════════════════════════════════════════════════════

echo ═══════════════════════════════════════════════════════════════
echo   🚀 STARTING COMPLETE DEFENSE SYSTEM
echo ═══════════════════════════════════════════════════════════════
echo.

REM Check for admin
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [WARNING] Not running as Administrator
    echo [WARNING] Some features will be limited
    echo.
    echo Right-click this file and "Run as Administrator" for full power
    echo.
    timeout /t 5
)

REM Launch components
echo [START] Master Control...
start /min "MASTER-CONTROL" cmd /c "%~dp0MASTER-CONTROL.bat"
timeout /t 2 >nul

echo [START] Quick Defense...
call "%~dp0QUICK-DEFEND.bat"

echo.
echo ═══════════════════════════════════════════════════════════════
echo   ✅ DEFENSE SYSTEM ACTIVE
echo ═══════════════════════════════════════════════════════════════
echo.
echo Status:
echo   - Master Control: Running (background)
echo   - Agent Factory: Running (background)
echo   - 5x Defense Agents: Active
echo   - Heartbeat Monitor: Active
echo   - Self-Healing: Enabled
echo.
echo Check Desktop for forensic data and logs
echo.
echo To stop (only if attack is over):
echo   - Press Ctrl+C in all windows
echo   - Or run: taskkill /F /FI "WINDOWTITLE eq *FACTORY*"
echo.
pause
