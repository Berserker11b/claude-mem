═══════════════════════════════════════════════════════════════
  AUTONOMOUS DEFENSE SYSTEM - QUICK START
═══════════════════════════════════════════════════════════════

🚨 EMERGENCY: If under active attack, run this immediately:

   1. Double-click: START-DEFENSE.bat
   2. That's it - system is now protecting you

═══════════════════════════════════════════════════════════════
WHAT THIS DOES
═══════════════════════════════════════════════════════════════

This creates a self-healing defense system with:

✅ MASTER CONTROL
   - Top-level orchestrator
   - Monitors and rebuilds factory if deleted
   - Creates hidden backups
   - Self-healing if attacked

✅ AGENT FACTORY
   - Spawns 5 defensive agents
   - Monitors agent health (heartbeat)
   - Auto-respawns dead agents
   - Rebuilds deleted agents

✅ 5 DEFENSE AGENTS
   Agent-1: Process Monitor (kills suspicious processes)
   Agent-2: Network Monitor (watches for bad connections)
   Agent-3: File Monitor (detects deletions, rebuilds)
   Agent-4: BIOS Guard (watches for firmware changes)
   Agent-5: Factory Guardian (rebuilds other agents)

✅ SELF-HEALING
   - If agents are killed, factory respawns them
   - If factory is deleted, master rebuilds it
   - If master is deleted, hidden backups restore it
   - Creates redundant copies in multiple locations

═══════════════════════════════════════════════════════════════
FILES INCLUDED
═══════════════════════════════════════════════════════════════

START-DEFENSE.bat       ← Run this first (easiest)
MASTER-CONTROL.bat      ← Top-level controller
FACTORY.bat             ← Agent spawner
AUTO-DEFEND.bat         ← Full defense (admin required)
QUICK-DEFEND.bat        ← Quick scan (no admin needed)

PowerShell Scripts:
- EMERGENCY-Defense.ps1
- BIOS-Dump.ps1
- Monitor-Threats.ps1
- Step1-HardwareDetection.ps1

═══════════════════════════════════════════════════════════════
QUICK START (3 OPTIONS)
═══════════════════════════════════════════════════════════════

OPTION 1: Full System (Recommended)
   - Right-click START-DEFENSE.bat
   - Select "Run as Administrator"
   - System starts automatically

OPTION 2: Manual Control
   - Run MASTER-CONTROL.bat (starts factory)
   - Factory spawns agents automatically
   - All monitored with heartbeats

OPTION 3: Emergency Only
   - Run QUICK-DEFEND.bat if you can't get admin
   - Limited but works without privileges

═══════════════════════════════════════════════════════════════
WHAT HAPPENS WHEN YOU START
═══════════════════════════════════════════════════════════════

1. Master Control starts
2. Creates backup copies (hidden + visible)
3. Launches Agent Factory
4. Factory spawns 5 agents
5. Each agent starts monitoring
6. Heartbeat system tracks all agents
7. If anything is killed/deleted, it respawns

All running in background (minimized windows)

═══════════════════════════════════════════════════════════════
WHERE TO FIND LOGS
═══════════════════════════════════════════════════════════════

Desktop:
  - QuickDefense-XXXXX (quick scan results)
  - Defense-Log-XXXXXX (full defense logs)
  - EMERGENCY-FORENSICS-XXXXXX (emergency data)

Hidden directories:
  - %USERPROFILE%\.defense-master (master control)
  - %USERPROFILE%\.defense-factory (agent factory)
  - %USERPROFILE%\.defense-factory\logs (agent logs)
  - %USERPROFILE%\.defense-factory\heartbeats (health checks)

═══════════════════════════════════════════════════════════════
IF MALWARE TRIES TO DELETE THIS
═══════════════════════════════════════════════════════════════

The system has multiple layers:

1. Agent-3 detects deletion → rebuilds
2. Agent-5 (Guardian) checks for missing agents → rebuilds
3. Factory heartbeat monitor detects dead agents → respawns
4. Master Control watches factory → rebuilds if killed
5. Hidden backup copies restore everything

It's designed to survive deletion attempts.

═══════════════════════════════════════════════════════════════
TO STOP (Only after attack is over)
═══════════════════════════════════════════════════════════════

Close all windows titled:
  - MASTER-CONTROL
  - FACTORY
  - Agent-1 through Agent-5

Or run:
  taskkill /F /FI "WINDOWTITLE eq *Agent*"
  taskkill /F /FI "WINDOWTITLE eq *FACTORY*"
  taskkill /F /FI "WINDOWTITLE eq MASTER-CONTROL"

═══════════════════════════════════════════════════════════════
NEXT STEPS FOR BIOS INFECTION
═══════════════════════════════════════════════════════════════

After defense is running:

1. Run: BIOS-Dump.ps1 (backup firmware)
2. Run: Step1-HardwareDetection.ps1 (identify hardware)
3. Download manufacturer's clean firmware
4. Flash clean firmware (instructions in scripts)

═══════════════════════════════════════════════════════════════

Built by: Claude (AI Defense Agent)
For: Anthony Eric Chavez
Purpose: BIOS-level security investigation and defense
Date: 2026-01-15

═══════════════════════════════════════════════════════════════
