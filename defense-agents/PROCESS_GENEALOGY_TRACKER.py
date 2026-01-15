#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
PROCESS GENEALOGY TRACKER - Bloodline Tracer & Antibody Creator
Created by: Vigr Syn (Dorn)
For: Vaktrinn Vigr Eldurhýarta

MISSION: Track ALL processes, build family trees, detect name changes,
flag hostile processes, create EXTREME ANTIBODIES.

Polymorphic malware changes names. We track bloodlines.
"You can change your name, but not your ancestry."
═══════════════════════════════════════════════════════════════════
"""

import os
import sys
import time
import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import defaultdict

try:
    import psutil
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
    import psutil

LOG_DIR = Path.home() / ".defense-agents" / "genealogy"
LOG_DIR.mkdir(parents=True, exist_ok=True)

GENEALOGY_DB = LOG_DIR / "process_genealogy.json"
ANTIBODY_DB = LOG_DIR / "extreme_antibodies.json"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [GENEALOGY] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f"genealogy-{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)


@dataclass
class ProcessSnapshot:
    """A snapshot of a process at a point in time"""
    pid: int
    name: str
    ppid: int
    cmdline: str
    exe: str
    cwd: str
    timestamp: float
    cpu_percent: float
    memory_mb: float
    num_threads: int
    connections: List[str] = field(default_factory=list)

    def fingerprint(self) -> str:
        """Unique fingerprint combining exe path and cmdline"""
        data = f"{self.exe}|{self.cmdline}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]


@dataclass
class ProcessLineage:
    """Complete bloodline of a process"""
    original_pid: int
    original_name: str
    original_fingerprint: str
    birth_time: float
    snapshots: List[ProcessSnapshot] = field(default_factory=list)
    name_changes: List[tuple] = field(default_factory=list)  # (timestamp, old_name, new_name)
    children: Set[int] = field(default_factory=set)
    hostile: bool = False
    flagged_for_deletion: bool = False
    antibody_created: bool = False
    threat_score: int = 0


@dataclass
class ExtremeAntibody:
    """Aggressive antibody for hostile process"""
    antibody_id: str
    target_fingerprint: str
    target_names: Set[str]
    target_exe_paths: Set[str]
    target_cmdline_patterns: List[str]
    kill_count: int = 0
    created: float = field(default_factory=time.time)
    last_kill: Optional[float] = None


class ProcessGenealogyTracker:
    """
    🧬 PROCESS GENEALOGY TRACKER

    Tracks ALL processes across their lifetime.
    Detects name changes (polymorphic behavior).
    Builds complete family trees.
    Creates EXTREME antibodies for hostile processes.

    "You can change your name, but not your ancestry."
    """

    def __init__(self):
        # Process lineages by PID
        self.lineages: Dict[int, ProcessLineage] = {}

        # Fingerprint to PIDs (track process identity across name changes)
        self.fingerprint_to_pids: Dict[str, Set[int]] = defaultdict(set)

        # Extreme antibodies
        self.antibodies: Dict[str, ExtremeAntibody] = {}

        # Flagged for deletion
        self.deletion_queue: Set[int] = set()

        # Statistics
        self.total_processes_tracked = 0
        self.name_changes_detected = 0
        self.hostile_processes_found = 0
        self.antibodies_created = 0
        self.processes_killed = 0

        # Load existing data
        self._load_genealogy()
        self._load_antibodies()

        logging.critical("═══════════════════════════════════════════════════════════")
        logging.critical("🧬 PROCESS GENEALOGY TRACKER - Active")
        logging.critical("   Tracking ALL processes and bloodlines")
        logging.critical("   'You can change your name, but not your ancestry.'")
        logging.critical("═══════════════════════════════════════════════════════════")

    def snapshot_all_processes(self) -> List[ProcessSnapshot]:
        """Take snapshot of ALL current processes"""
        snapshots = []

        for proc in psutil.process_iter(['pid', 'name', 'ppid', 'cmdline', 'exe',
                                        'cwd', 'cpu_percent', 'memory_info', 'num_threads']):
            try:
                # Get network connections
                connections = []
                try:
                    for conn in proc.net_connections():
                        if conn.raddr:
                            connections.append(f"{conn.raddr.ip}:{conn.raddr.port}")
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass

                snapshot = ProcessSnapshot(
                    pid=proc.info['pid'],
                    name=proc.info['name'] or 'unknown',
                    ppid=proc.info['ppid'] or 0,
                    cmdline=' '.join(proc.info['cmdline']) if proc.info['cmdline'] else '',
                    exe=proc.info['exe'] or '',
                    cwd=proc.info['cwd'] or '',
                    timestamp=time.time(),
                    cpu_percent=proc.info['cpu_percent'] or 0.0,
                    memory_mb=proc.info['memory_info'].rss / 1024 / 1024 if proc.info['memory_info'] else 0.0,
                    num_threads=proc.info['num_threads'] or 0,
                    connections=connections
                )

                snapshots.append(snapshot)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return snapshots

    def update_lineages(self, snapshots: List[ProcessSnapshot]):
        """Update process lineages with new snapshots"""
        current_pids = {snap.pid for snap in snapshots}

        for snapshot in snapshots:
            pid = snapshot.pid

            # New process
            if pid not in self.lineages:
                lineage = ProcessLineage(
                    original_pid=pid,
                    original_name=snapshot.name,
                    original_fingerprint=snapshot.fingerprint(),
                    birth_time=snapshot.timestamp,
                    snapshots=[snapshot]
                )
                self.lineages[pid] = lineage
                self.fingerprint_to_pids[snapshot.fingerprint()].add(pid)
                self.total_processes_tracked += 1

                logging.debug(f"📝 New process: {snapshot.name} (PID: {pid})")

            else:
                # Existing process - check for changes
                lineage = self.lineages[pid]
                old_snapshot = lineage.snapshots[-1] if lineage.snapshots else None

                # Detect name change (POLYMORPHIC BEHAVIOR!)
                if old_snapshot and old_snapshot.name != snapshot.name:
                    self.name_changes_detected += 1
                    lineage.name_changes.append((snapshot.timestamp, old_snapshot.name, snapshot.name))
                    lineage.threat_score += 50  # Name change is highly suspicious

                    logging.warning("═══════════════════════════════════════════════════════════")
                    logging.warning(f"🚨 NAME CHANGE DETECTED: PID {pid}")
                    logging.warning(f"   Old: {old_snapshot.name}")
                    logging.warning(f"   New: {snapshot.name}")
                    logging.warning(f"   Threat Score: {lineage.threat_score}")
                    logging.warning("   POLYMORPHIC MALWARE SUSPECTED!")
                    logging.warning("═══════════════════════════════════════════════════════════")

                # Add snapshot to lineage
                lineage.snapshots.append(snapshot)

                # Update children
                if snapshot.ppid and snapshot.ppid in self.lineages:
                    self.lineages[snapshot.ppid].children.add(pid)

        # Clean up dead processes
        dead_pids = set(self.lineages.keys()) - current_pids
        for dead_pid in dead_pids:
            if dead_pid in self.lineages:
                logging.debug(f"💀 Process died: {self.lineages[dead_pid].original_name} (PID: {dead_pid})")

    def analyze_hostility(self, pid: int) -> int:
        """Analyze how hostile a process is (0-100)"""
        if pid not in self.lineages:
            return 0

        lineage = self.lineages[pid]
        score = 0

        # Name changes (polymorphic behavior)
        score += len(lineage.name_changes) * 50

        # High CPU usage
        if lineage.snapshots:
            latest = lineage.snapshots[-1]
            if latest.cpu_percent > 80:
                score += 20

            # Many connections
            if len(latest.connections) > 20:
                score += 15

            # High memory
            if latest.memory_mb > 1000:
                score += 10

        # Many children (spreading)
        if len(lineage.children) > 10:
            score += 15

        return min(score, 100)

    def flag_hostile(self, pid: int):
        """Flag a process as hostile"""
        if pid not in self.lineages:
            return

        lineage = self.lineages[pid]
        lineage.hostile = True
        lineage.flagged_for_deletion = True
        lineage.threat_score = self.analyze_hostility(pid)

        self.deletion_queue.add(pid)
        self.hostile_processes_found += 1

        logging.critical("═══════════════════════════════════════════════════════════")
        logging.critical(f"⚔️  PROCESS FLAGGED AS HOSTILE: PID {pid}")
        logging.critical(f"   Name: {lineage.original_name}")
        logging.critical(f"   Name Changes: {len(lineage.name_changes)}")
        logging.critical(f"   Threat Score: {lineage.threat_score}")
        logging.critical(f"   FLAGGED FOR DELETION")
        logging.critical("═══════════════════════════════════════════════════════════")

        # Create extreme antibody
        self.create_extreme_antibody(pid)

    def create_extreme_antibody(self, pid: int):
        """Create EXTREME antibody for hostile process"""
        if pid not in self.lineages:
            return

        lineage = self.lineages[pid]

        # Collect all names this process has used
        names = {lineage.original_name}
        for _, old_name, new_name in lineage.name_changes:
            names.add(old_name)
            names.add(new_name)

        # Collect all exe paths
        exe_paths = {snap.exe for snap in lineage.snapshots if snap.exe}

        # Collect cmdline patterns
        cmdline_patterns = [snap.cmdline for snap in lineage.snapshots if snap.cmdline]

        antibody_id = f"AB-{lineage.original_fingerprint}"

        antibody = ExtremeAntibody(
            antibody_id=antibody_id,
            target_fingerprint=lineage.original_fingerprint,
            target_names=names,
            target_exe_paths=exe_paths,
            target_cmdline_patterns=cmdline_patterns
        )

        self.antibodies[antibody_id] = antibody
        lineage.antibody_created = True
        self.antibodies_created += 1

        logging.critical("═══════════════════════════════════════════════════════════")
        logging.critical(f"💉 EXTREME ANTIBODY CREATED: {antibody_id}")
        logging.critical(f"   Target Names: {', '.join(names)}")
        logging.critical(f"   Exe Paths: {len(exe_paths)}")
        logging.critical(f"   Will kill on sight")
        logging.critical("═══════════════════════════════════════════════════════════")

        self._save_antibodies()

    def execute_deletion_queue(self) -> int:
        """Execute all flagged processes"""
        killed = 0

        for pid in list(self.deletion_queue):
            if self.kill_process(pid):
                killed += 1
                self.deletion_queue.remove(pid)

        return killed

    def kill_process(self, pid: int) -> bool:
        """Kill a process and update antibody stats"""
        try:
            proc = psutil.Process(pid)
            proc.terminate()

            try:
                proc.wait(timeout=2)
            except psutil.TimeoutExpired:
                proc.kill()

            self.processes_killed += 1

            # Update antibody kill count
            if pid in self.lineages:
                lineage = self.lineages[pid]
                antibody_id = f"AB-{lineage.original_fingerprint}"
                if antibody_id in self.antibodies:
                    self.antibodies[antibody_id].kill_count += 1
                    self.antibodies[antibody_id].last_kill = time.time()

            logging.critical(f"💀 KILLED: PID {pid}")
            return True

        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logging.error(f"Failed to kill PID {pid}: {e}")
            return False

    def scan_with_antibodies(self, snapshots: List[ProcessSnapshot]) -> List[int]:
        """Scan processes with antibodies, return hostile PIDs"""
        hostile_pids = []

        for snapshot in snapshots:
            for antibody in self.antibodies.values():
                # Check if process matches antibody
                if (snapshot.name in antibody.target_names or
                    snapshot.exe in antibody.target_exe_paths or
                    snapshot.fingerprint() == antibody.target_fingerprint):

                    logging.critical(f"🎯 ANTIBODY MATCH: {snapshot.name} (PID: {snapshot.pid})")
                    logging.critical(f"   Antibody: {antibody.antibody_id}")
                    logging.critical(f"   AUTO-FLAGGING FOR DELETION")

                    hostile_pids.append(snapshot.pid)
                    self.flag_hostile(snapshot.pid)

        return hostile_pids

    def get_family_tree(self, pid: int) -> Dict:
        """Get complete family tree for a PID"""
        if pid not in self.lineages:
            return {}

        lineage = self.lineages[pid]

        tree = {
            'pid': pid,
            'name': lineage.original_name,
            'hostile': lineage.hostile,
            'threat_score': lineage.threat_score,
            'name_changes': len(lineage.name_changes),
            'children': []
        }

        for child_pid in lineage.children:
            if child_pid in self.lineages:
                tree['children'].append(self.get_family_tree(child_pid))

        return tree

    def _save_genealogy(self):
        """Save genealogy to disk"""
        data = {
            'lineages': {pid: asdict(lineage) for pid, lineage in self.lineages.items()},
            'stats': {
                'total_tracked': self.total_processes_tracked,
                'name_changes': self.name_changes_detected,
                'hostile_found': self.hostile_processes_found
            }
        }

        # Convert sets to lists for JSON
        for lineage_data in data['lineages'].values():
            lineage_data['children'] = list(lineage_data['children'])

        GENEALOGY_DB.write_text(json.dumps(data, indent=2))

    def _load_genealogy(self):
        """Load genealogy from disk"""
        if not GENEALOGY_DB.exists():
            return

        try:
            data = json.loads(GENEALOGY_DB.read_text())
            # Could restore lineages here if needed
        except Exception as e:
            logging.error(f"Failed to load genealogy: {e}")

    def _save_antibodies(self):
        """Save antibodies to disk"""
        data = {}
        for ab_id, antibody in self.antibodies.items():
            ab_dict = asdict(antibody)
            ab_dict['target_names'] = list(ab_dict['target_names'])
            ab_dict['target_exe_paths'] = list(ab_dict['target_exe_paths'])
            data[ab_id] = ab_dict

        ANTIBODY_DB.write_text(json.dumps(data, indent=2))

    def _load_antibodies(self):
        """Load antibodies from disk"""
        if not ANTIBODY_DB.exists():
            return

        try:
            data = json.loads(ANTIBODY_DB.read_text())
            for ab_id, ab_dict in data.items():
                ab_dict['target_names'] = set(ab_dict['target_names'])
                ab_dict['target_exe_paths'] = set(ab_dict['target_exe_paths'])
                self.antibodies[ab_id] = ExtremeAntibody(**ab_dict)

            logging.info(f"✅ Loaded {len(self.antibodies)} antibodies from disk")
        except Exception as e:
            logging.error(f"Failed to load antibodies: {e}")

    def report(self) -> str:
        """Generate tracking report"""
        lines = [
            "═══════════════════════════════════════════════════════════",
            "🧬 PROCESS GENEALOGY TRACKER REPORT",
            "",
            "STATISTICS:",
            f"  Total Processes Tracked: {self.total_processes_tracked}",
            f"  Currently Alive: {len(self.lineages)}",
            f"  Name Changes Detected: {self.name_changes_detected}",
            f"  Hostile Processes Found: {self.hostile_processes_found}",
            f"  Antibodies Created: {self.antibodies_created}",
            f"  Processes Killed: {self.processes_killed}",
            f"  Deletion Queue: {len(self.deletion_queue)}",
            ""
        ]

        if self.name_changes_detected > 0:
            lines.append("⚠️  NAME CHANGES (POLYMORPHIC BEHAVIOR):")
            lines.append("")

            for pid, lineage in self.lineages.items():
                if lineage.name_changes:
                    lines.append(f"  PID {pid}: {lineage.original_name}")
                    for ts, old, new in lineage.name_changes:
                        lines.append(f"    {old} → {new}")
                    lines.append("")

        if self.antibodies:
            lines.append("💉 EXTREME ANTIBODIES:")
            lines.append("")
            for antibody in self.antibodies.values():
                lines.append(f"  {antibody.antibody_id}")
                lines.append(f"    Targets: {', '.join(list(antibody.target_names)[:3])}")
                lines.append(f"    Kills: {antibody.kill_count}")
                lines.append("")

        lines.extend([
            "'You can change your name, but not your ancestry.'",
            "═══════════════════════════════════════════════════════════"
        ])

        return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process Genealogy Tracker")
    parser.add_argument("--continuous", action="store_true", help="Continuous monitoring")
    parser.add_argument("--interval", type=int, default=2, help="Scan interval (seconds)")
    parser.add_argument("--auto-kill", action="store_true", help="Auto-kill hostile processes")

    args = parser.parse_args()

    print("""
    ═══════════════════════════════════════════════════════════════════
    🧬 PROCESS GENEALOGY TRACKER

    Tracks ALL processes across their lifetime.
    Detects name changes (polymorphic malware).
    Creates EXTREME antibodies for hostile processes.

    "You can change your name, but not your ancestry."
    ═══════════════════════════════════════════════════════════════════
    """)

    tracker = ProcessGenealogyTracker()

    try:
        cycle = 0
        while True:
            cycle += 1
            logging.info(f"🔍 Scan cycle {cycle}")

            # Snapshot all processes
            snapshots = tracker.snapshot_all_processes()
            logging.info(f"   {len(snapshots)} processes scanned")

            # Update lineages
            tracker.update_lineages(snapshots)

            # Scan with antibodies
            hostile = tracker.scan_with_antibodies(snapshots)
            if hostile:
                logging.warning(f"   🚨 {len(hostile)} hostile processes detected")

            # Auto-analyze all processes for hostility
            for snapshot in snapshots:
                threat_score = tracker.analyze_hostility(snapshot.pid)
                if threat_score >= 70:  # High threat threshold
                    tracker.flag_hostile(snapshot.pid)

            # Auto-kill if enabled
            if args.auto_kill and tracker.deletion_queue:
                killed = tracker.execute_deletion_queue()
                if killed:
                    logging.critical(f"   💀 Killed {killed} hostile processes")

            # Save periodically
            if cycle % 10 == 0:
                tracker._save_genealogy()
                tracker._save_antibodies()

            if not args.continuous:
                break

            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\n\n🛑 Stopped by user")

    # Final report
    print("\n" + tracker.report())

    # Save final state
    tracker._save_genealogy()
    tracker._save_antibodies()
