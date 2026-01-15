@echo off
REM ═══════════════════════════════════════════════════════════════
REM AGENT FACTORY - Self-Replicating Defense System
REM Creates and monitors multiple defensive agents
REM Auto-respawns if agents are killed
REM ═══════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion

echo ═══════════════════════════════════════════════════════════════
echo   🏭 AGENT FACTORY - INITIALIZING
echo ═══════════════════════════════════════════════════════════════
echo.

REM Factory configuration
set FACTORY_DIR=%USERPROFILE%\.defense-factory
set AGENT_DIR=%FACTORY_DIR%\agents
set LOG_DIR=%FACTORY_DIR%\logs
set HEARTBEAT_DIR=%FACTORY_DIR%\heartbeats
set NUM_AGENTS=5

REM Create factory structure
if not exist "%FACTORY_DIR%" mkdir "%FACTORY_DIR%"
if not exist "%AGENT_DIR%" mkdir "%AGENT_DIR%"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%HEARTBEAT_DIR%" mkdir "%HEARTBEAT_DIR%"

echo [FACTORY] Directory: %FACTORY_DIR%
echo [FACTORY] Spawning %NUM_AGENTS% agents...
echo.

REM ═══════════════════════════════════════════════════════════════
REM CREATE AGENT TEMPLATES
REM ═══════════════════════════════════════════════════════════════

REM Agent 1: Process Monitor
echo [BUILD] Creating Agent-1: Process Monitor
(
echo @echo off
echo setlocal enabledelayedexpansion
echo set AGENT_ID=Agent-1-ProcessMonitor
echo set HEARTBEAT_FILE=%HEARTBEAT_DIR%\%%AGENT_ID%%.beat
echo set LOG_FILE=%LOG_DIR%\%%AGENT_ID%%.log
echo :agent_loop
echo echo %%date%% %%time%% - ALIVE ^>^> "%%HEARTBEAT_FILE%%"
echo tasklist ^| findstr /i "inject exploit payload pwn" ^> nul
echo if %%errorLevel%% EQU 0 ^(
echo     echo [%%AGENT_ID%%] THREAT DETECTED ^>^> "%%LOG_FILE%%"
echo     for /f "tokens=1" %%%%a in ^('tasklist ^| findstr /i "inject exploit payload"'^) do ^(
echo         echo [%%AGENT_ID%%] KILL: %%%%a ^>^> "%%LOG_FILE%%"
echo         taskkill /F /IM %%%%a ^>nul 2^>^&1
echo     ^)
echo ^)
echo timeout /t 3 ^>nul
echo goto agent_loop
) > "%AGENT_DIR%\Agent-1.bat"

REM Agent 2: Network Monitor
echo [BUILD] Creating Agent-2: Network Monitor
(
echo @echo off
echo setlocal enabledelayedexpansion
echo set AGENT_ID=Agent-2-NetworkMonitor
echo set HEARTBEAT_FILE=%HEARTBEAT_DIR%\%%AGENT_ID%%.beat
echo set LOG_FILE=%LOG_DIR%\%%AGENT_ID%%.log
echo :agent_loop
echo echo %%date%% %%time%% - ALIVE ^>^> "%%HEARTBEAT_FILE%%"
echo netstat -ano ^| findstr "4444 31337 1337 6666" ^> nul
echo if %%errorLevel%% EQU 0 ^(
echo     echo [%%AGENT_ID%%] SUSPICIOUS PORT DETECTED ^>^> "%%LOG_FILE%%"
echo     netstat -ano ^| findstr "4444 31337 1337 6666" ^>^> "%%LOG_FILE%%"
echo ^)
echo timeout /t 5 ^>nul
echo goto agent_loop
) > "%AGENT_DIR%\Agent-2.bat"

REM Agent 3: File System Monitor
echo [BUILD] Creating Agent-3: File System Monitor
(
echo @echo off
echo setlocal enabledelayedexpansion
echo set AGENT_ID=Agent-3-FileMonitor
echo set HEARTBEAT_FILE=%HEARTBEAT_DIR%\%%AGENT_ID%%.beat
echo set LOG_FILE=%LOG_DIR%\%%AGENT_ID%%.log
echo :agent_loop
echo echo %%date%% %%time%% - ALIVE ^>^> "%%HEARTBEAT_FILE%%"
echo if exist "%FACTORY_DIR%\*.deleted" ^(
echo     echo [%%AGENT_ID%%] DELETION DETECTED - REBUILDING ^>^> "%%LOG_FILE%%"
echo     call "%~f0"
echo ^)
echo timeout /t 5 ^>nul
echo goto agent_loop
) > "%AGENT_DIR%\Agent-3.bat"

REM Agent 4: BIOS Guard
echo [BUILD] Creating Agent-4: BIOS Guard
(
echo @echo off
echo setlocal enabledelayedexpansion
echo set AGENT_ID=Agent-4-BIOSGuard
echo set HEARTBEAT_FILE=%HEARTBEAT_DIR%\%%AGENT_ID%%.beat
echo set LOG_FILE=%LOG_DIR%\%%AGENT_ID%%.log
echo :agent_loop
echo echo %%date%% %%time%% - ALIVE ^>^> "%%HEARTBEAT_FILE%%"
echo wmic bios get version /value ^> "%FACTORY_DIR%\bios-check.tmp"
echo fc "%FACTORY_DIR%\bios-baseline.txt" "%FACTORY_DIR%\bios-check.tmp" ^>nul 2^>^&1
echo if %%errorLevel%% NEQ 0 ^(
echo     echo [%%AGENT_ID%%] BIOS CHANGE DETECTED ^>^> "%%LOG_FILE%%"
echo ^)
echo timeout /t 10 ^>nul
echo goto agent_loop
) > "%AGENT_DIR%\Agent-4.bat"

REM Agent 5: Factory Guardian (rebuilds other agents)
echo [BUILD] Creating Agent-5: Factory Guardian
(
echo @echo off
echo setlocal enabledelayedexpansion
echo set AGENT_ID=Agent-5-FactoryGuardian
echo set HEARTBEAT_FILE=%HEARTBEAT_DIR%\%%AGENT_ID%%.beat
echo set LOG_FILE=%LOG_DIR%\%%AGENT_ID%%.log
echo :agent_loop
echo echo %%date%% %%time%% - ALIVE ^>^> "%%HEARTBEAT_FILE%%"
echo for %%%%a in ^(1 2 3 4^) do ^(
echo     if not exist "%AGENT_DIR%\Agent-%%%%a.bat" ^(
echo         echo [%%AGENT_ID%%] Agent-%%%%a MISSING - REBUILDING ^>^> "%%LOG_FILE%%"
echo         call "%~f0"
echo     ^)
echo ^)
echo timeout /t 5 ^>nul
echo goto agent_loop
) > "%AGENT_DIR%\Agent-5.bat"

echo.
echo [OK] All agent templates created
echo.

REM ═══════════════════════════════════════════════════════════════
REM CREATE BIOS BASELINE
REM ═══════════════════════════════════════════════════════════════

wmic bios get version /value > "%FACTORY_DIR%\bios-baseline.txt" 2>nul

REM ═══════════════════════════════════════════════════════════════
REM SPAWN AGENTS
REM ═══════════════════════════════════════════════════════════════

echo [SPAWN] Launching agents in background...
echo.

for %%a in (1 2 3 4 5) do (
    echo [START] Agent-%%a
    start /min "Agent-%%a" cmd /c "%AGENT_DIR%\Agent-%%a.bat"
    timeout /t 1 >nul
)

echo.
echo [OK] All agents spawned
echo.

REM ═══════════════════════════════════════════════════════════════
REM HEARTBEAT MONITOR (Factory oversight)
REM ═══════════════════════════════════════════════════════════════

echo ═══════════════════════════════════════════════════════════════
echo   💓 HEARTBEAT MONITOR - ACTIVE
echo ═══════════════════════════════════════════════════════════════
echo.
echo Monitoring agent health...
echo Press Ctrl+C to stop factory
echo.

:monitor_loop
timeout /t 5 >nul

REM Check each agent's heartbeat
for %%a in (1 2 3 4 5) do (
    set AGENT_NAME=Agent-%%a
    set HEARTBEAT_FILE=%HEARTBEAT_DIR%\!AGENT_NAME!*.beat

    REM Check if heartbeat file exists and is recent
    if exist "!HEARTBEAT_FILE!" (
        REM Check file age (within last 15 seconds)
        forfiles /p "%HEARTBEAT_DIR%" /m "!AGENT_NAME!*.beat" /d -0 >nul 2>&1
        if errorlevel 1 (
            echo [ALERT] !AGENT_NAME! - HEARTBEAT STALE - RESPAWNING
            start /min "!AGENT_NAME!" cmd /c "%AGENT_DIR%\!AGENT_NAME!.bat"
        )
    ) else (
        echo [ALERT] !AGENT_NAME! - NO HEARTBEAT - RESPAWNING
        start /min "!AGENT_NAME!" cmd /c "%AGENT_DIR%\!AGENT_NAME!.bat"
    )
)

REM Check if agent files still exist
for %%a in (1 2 3 4 5) do (
    if not exist "%AGENT_DIR%\Agent-%%a.bat" (
        echo [CRITICAL] Agent-%%a FILE DELETED - REBUILDING FACTORY
        call "%~f0"
        exit /b
    )
)

goto monitor_loop
