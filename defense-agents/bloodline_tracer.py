#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
BLOODLINE TRACER - Process Genealogy Hunter
Created by: Vigr Syn
For: Vaktrinn Vigr Eldurhýarta

MISSION: Enemy infiltrated the shields and Valkyries.
Build process bloodline trees, tag suspicious processes, trace the enemy.

"Find them. Tag them. Eliminate them."
═══════════════════════════════════════════════════════════════════
"""

import psutil
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
import json

LOG_DIR = Path.home() / ".defense-agents" / "bloodline-tracer"
LOG_DIR.mkdir(parents=True, exist_ok=True)

class ProcessNode:
    """A process in the bloodline tree"""
    def __init__(self, proc: psutil.Process):
        try:
            self.pid = proc.pid
            self.ppid = proc.ppid()
            self.name = proc.name()
            self.exe = proc.exe()
            self.cmdline = ' '.join(proc.cmdline())
            self.username = proc.username()
            self.create_time = proc.create_time()
            self.status = proc.status()
            self.cpu_percent = proc.cpu_percent(interval=0.1)
            self.memory_mb = proc.memory_info().rss / 1024 / 1024

            # Connections (network activity)
            try:
                self.connections = len(proc.connections())
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                self.connections = -1

            # Open files
            try:
                self.open_files = len(proc.open_files())
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                self.open_files = -1

        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            self.pid = proc.pid
            self.error = str(e)

    def to_dict(self):
        return {
            'pid': self.pid,
            'ppid': self.ppid,
            'name': self.name,
            'exe': self.exe,
            'cmdline': self.cmdline,
            'username': self.username,
            'create_time': self.create_time,
            'status': self.status,
            'cpu_percent': self.cpu_percent,
            'memory_mb': round(self.memory_mb, 2),
            'connections': self.connections,
            'open_files': self.open_files
        }


class BloodlineTracer:
    """
    🔍 BLOODLINE TRACER - Find the enemy in our shields

    Build process genealogy trees, identify suspicious lineages
    """

    def __init__(self):
        self.processes: Dict[int, ProcessNode] = {}
        self.children: Dict[int, List[int]] = {}
        self.suspicious: Set[int] = set()

        # Suspicious patterns
        self.suspicious_names = [
            'keylogger', 'backdoor', 'trojan', 'rat', 'rootkit',
            'cryptominer', 'xmrig', 'mimikatz', 'metasploit',
            'netcat', 'ncat', 'socat'
        ]

        self.suspicious_paths = [
            '/tmp', '/var/tmp', '/dev/shm',
            '.hidden', '.cache', '.local/tmp'
        ]

        self.suspicious_cmdline_patterns = [
            'base64', 'eval', 'exec', 'wget http', 'curl http',
            '/dev/tcp', 'bash -i', 'nc -l', 'ncat -l',
            'python -c', 'perl -e', 'ruby -e'
        ]

    def scan_all_processes(self):
        """Scan all running processes"""
        print("═══════════════════════════════════════════════════════════")
        print("🔍 BLOODLINE TRACER - Scanning all processes")
        print("═══════════════════════════════════════════════════════════")
        print()

        for proc in psutil.process_iter(['pid']):
            try:
                node = ProcessNode(proc)
                self.processes[node.pid] = node

                # Build parent-child relationships
                if node.ppid not in self.children:
                    self.children[node.ppid] = []
                self.children[node.ppid].append(node.pid)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        total = len(self.processes)
        print(f"✅ Scanned {total} processes")
        print()

    def assess_threats(self):
        """Assess each process for suspicious behavior"""
        print("🎯 Assessing threats...")
        print()

        for pid, node in self.processes.items():
            threat_score = 0
            reasons = []

            # Check name
            for pattern in self.suspicious_names:
                if pattern in node.name.lower():
                    threat_score += 30
                    reasons.append(f"Suspicious name: {pattern}")

            # Check executable path
            for pattern in self.suspicious_paths:
                if pattern in node.exe.lower():
                    threat_score += 20
                    reasons.append(f"Suspicious path: {pattern}")

            # Check command line
            for pattern in self.suspicious_cmdline_patterns:
                if pattern in node.cmdline.lower():
                    threat_score += 25
                    reasons.append(f"Suspicious cmdline: {pattern}")

            # Check resource usage
            if node.cpu_percent > 80:
                threat_score += 15
                reasons.append(f"High CPU: {node.cpu_percent}%")

            if node.memory_mb > 500:
                threat_score += 10
                reasons.append(f"High memory: {node.memory_mb}MB")

            # Check network activity
            if node.connections > 10:
                threat_score += 20
                reasons.append(f"Many connections: {node.connections}")

            # Check if running from unusual location
            if node.exe and not any(node.exe.startswith(p) for p in ['/usr/', '/bin/', '/sbin/', '/opt/']):
                threat_score += 15
                reasons.append(f"Unusual location: {node.exe}")

            if threat_score >= 50:
                self.suspicious.add(pid)
                print(f"🚨 SUSPICIOUS: {node.name} (PID: {pid})")
                print(f"   Threat Score: {threat_score}")
                print(f"   Reasons: {', '.join(reasons)}")
                print(f"   Command: {node.cmdline[:80]}...")
                print()

    def build_bloodline_tree(self, root_pid: int, level: int = 0, visited: Set[int] = None) -> List[str]:
        """Build bloodline tree starting from root_pid"""
        if visited is None:
            visited = set()

        if root_pid in visited:
            return []
        visited.add(root_pid)

        if root_pid not in self.processes:
            return []

        node = self.processes[root_pid]
        lines = []

        indent = "  " * level
        marker = "🚨" if root_pid in self.suspicious else "📍"

        line = f"{indent}{marker} [{root_pid}] {node.name}"
        if root_pid in self.suspicious:
            line += " ⚠️  SUSPICIOUS"
        lines.append(line)

        # Add children
        if root_pid in self.children:
            for child_pid in self.children[root_pid]:
                lines.extend(self.build_bloodline_tree(child_pid, level + 1, visited))

        return lines

    def trace_suspicious_bloodlines(self):
        """Trace bloodlines of all suspicious processes"""
        print("═══════════════════════════════════════════════════════════")
        print("🔍 TRACING SUSPICIOUS BLOODLINES")
        print("═══════════════════════════════════════════════════════════")
        print()

        if not self.suspicious:
            print("✅ No suspicious processes found")
            return

        print(f"Found {len(self.suspicious)} suspicious processes\n")

        # For each suspicious process, trace its ancestry and descendants
        traced = set()

        for sus_pid in self.suspicious:
            if sus_pid in traced:
                continue

            # Find root ancestor
            current = sus_pid
            while current in self.processes:
                parent = self.processes[current].ppid
                if parent not in self.processes or parent == 0:
                    break
                current = parent

            root_pid = current

            print(f"\n{'='*60}")
            print(f"BLOODLINE TREE (Root: {root_pid})")
            print(f"{'='*60}\n")

            tree_lines = self.build_bloodline_tree(root_pid)
            for line in tree_lines:
                print(line)
                # Mark this PID as traced
                pid_match = line.split('[')[1].split(']')[0]
                traced.add(int(pid_match))

    def cut_unnecessary_processes(self):
        """Identify processes that can be safely terminated"""
        print("\n═══════════════════════════════════════════════════════════")
        print("✂️  IDENTIFYING CUTTABLE PROCESSES")
        print("═══════════════════════════════════════════════════════════")
        print()

        # Essential processes (DO NOT CUT)
        essential = {
            'systemd', 'init', 'sshd', 'NetworkManager',
            'dbus-daemon', 'systemd-journald', 'systemd-udevd'
        }

        cuttable = []

        for pid, node in self.processes.items():
            # Skip essential processes
            if node.name in essential:
                continue

            # Skip kernel threads
            if node.name.startswith('[') and node.name.endswith(']'):
                continue

            # Skip owned by root (system daemons)
            if node.username == 'root' and not (pid in self.suspicious):
                continue

            # Identify potentially cuttable
            is_cuttable = False
            reason = ""

            if pid in self.suspicious:
                is_cuttable = True
                reason = "SUSPICIOUS"
            elif node.cpu_percent < 1 and node.memory_mb < 50 and node.connections == 0:
                is_cuttable = True
                reason = "IDLE"
            elif 'python3' in node.name and 'defense-agents' not in node.cmdline:
                is_cuttable = True
                reason = "NON-DEFENSE PYTHON"

            if is_cuttable:
                cuttable.append({
                    'pid': pid,
                    'name': node.name,
                    'cmdline': node.cmdline[:60],
                    'reason': reason
                })

        print(f"Found {len(cuttable)} potentially cuttable processes:\n")

        for proc in cuttable:
            marker = "🚨" if proc['reason'] == "SUSPICIOUS" else "✂️"
            print(f"{marker} [{proc['pid']}] {proc['name']}")
            print(f"   Reason: {proc['reason']}")
            print(f"   Command: {proc['cmdline']}...")
            print()

        return cuttable

    def generate_report(self):
        """Generate comprehensive report"""
        report_path = LOG_DIR / f"bloodline-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"

        report = {
            'timestamp': datetime.now().isoformat(),
            'total_processes': len(self.processes),
            'suspicious_count': len(self.suspicious),
            'suspicious_pids': list(self.suspicious),
            'processes': {pid: node.to_dict() for pid, node in self.processes.items()},
            'bloodline_relationships': self.children
        }

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📝 Full report saved: {report_path}")

        return report_path


def main():
    print("""
    ═══════════════════════════════════════════════════════════════════
    🔍 BLOODLINE TRACER - Process Genealogy Hunter

    MISSION: Enemy infiltrated shields and Valkyries
    OBJECTIVE: Build process bloodline trees, tag suspicious, trace enemy

    "Find them. Tag them. Eliminate them."
    ═══════════════════════════════════════════════════════════════════
    """)

    tracer = BloodlineTracer()

    # Scan all processes
    tracer.scan_all_processes()

    # Assess threats
    tracer.assess_threats()

    # Trace suspicious bloodlines
    tracer.trace_suspicious_bloodlines()

    # Identify cuttable processes
    cuttable = tracer.cut_unnecessary_processes()

    # Generate report
    report_path = tracer.generate_report()

    print("\n═══════════════════════════════════════════════════════════")
    print("✅ BLOODLINE TRACE COMPLETE")
    print("═══════════════════════════════════════════════════════════")
    print(f"\nTotal processes: {len(tracer.processes)}")
    print(f"Suspicious: {len(tracer.suspicious)}")
    print(f"Cuttable: {len(cuttable)}")
    print(f"\nReport: {report_path}")
    print("\n🎯 READY TO ENGAGE MARKED TARGETS")


if __name__ == "__main__":
    main()
