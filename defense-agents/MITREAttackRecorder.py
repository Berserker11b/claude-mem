#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
MITRE ATT&CK PROCESS RECORDER
Created by: Claude (Anthropic)

Records all processes with MITRE ATT&CK technique tagging.
Detects attack patterns in real-time.

Monitored Techniques:
- T1499: Endpoint Denial of Service (CPU spikes)
- T1490: Inhibit System Recovery (file deletion)
- T1485: Data Destruction
- T1055: Process Injection (respawn loops)
- T1036: Masquerading (title changes)
- T1562: Impair Defenses
- T1071: Application Layer Protocol (C2)
═══════════════════════════════════════════════════════════════════
"""

import psutil
import time
import json
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Set

LOG_DIR = Path.home() / ".defense-agents" / "mitre-recorder"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [MITRE] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "attack-recorder.log"),
        logging.StreamHandler()
    ]
)

class ProcessRecord:
    """Record of a single process with MITRE tagging"""

    def __init__(self, pid: int, name: str, cmdline: List[str]):
        self.pid = pid
        self.name = name
        self.cmdline = cmdline
        self.first_seen = datetime.now()
        self.last_seen = datetime.now()
        self.title_changes = 0
        self.previous_names = []
        self.respawn_count = 0
        self.cpu_usage_history = []
        self.mitre_tags = set()

    def update_title(self, new_name: str):
        """Track title changes (T1036 - Masquerading)"""
        if new_name != self.name:
            self.previous_names.append(self.name)
            self.name = new_name
            self.title_changes += 1
            self.mitre_tags.add("T1036")  # Masquerading

    def record_cpu(self, cpu_percent: float):
        """Record CPU usage"""
        self.cpu_usage_history.append({
            'timestamp': datetime.now().isoformat(),
            'cpu': cpu_percent
        })
        # Keep last 100 readings
        if len(self.cpu_usage_history) > 100:
            self.cpu_usage_history.pop(0)

    def to_dict(self):
        return {
            'pid': self.pid,
            'name': self.name,
            'cmdline': ' '.join(self.cmdline) if self.cmdline else '',
            'first_seen': self.first_seen.isoformat(),
            'last_seen': self.last_seen.isoformat(),
            'title_changes': self.title_changes,
            'previous_names': self.previous_names,
            'respawn_count': self.respawn_count,
            'mitre_tags': list(self.mitre_tags)
        }


class MITREAttackRecorder:
    """Records and tags processes with MITRE ATT&CK techniques"""

    def __init__(self):
        self.name = "MITREAttackRecorder"
        self.process_records: Dict[int, ProcessRecord] = {}
        self.process_history = []
        self.dead_processes = []

        # Attack pattern tracking
        self.cpu_spike_count = 0
        self.critical_cpu_spikes = 0
        self.respawn_loops: Dict[str, int] = defaultdict(int)
        self.title_change_processes: List[ProcessRecord] = []

        # Thresholds
        self.CPU_SPIKE_THRESHOLD = 90.0
        self.CRITICAL_CPU_THRESHOLD = 100.0
        self.RESPAWN_THRESHOLD = 3
        self.TITLE_CHANGE_THRESHOLD = 2

        # Alert file
        self.alert_file = LOG_DIR / "alerts.jsonl"

    def scan_processes(self):
        """Scan all running processes"""
        current_pids = set()

        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent']):
            try:
                info = proc.info
                pid = info['pid']
                name = info['name']
                cmdline = info['cmdline'] or []
                cpu = info.get('cpu_percent', 0) or 0

                current_pids.add(pid)

                # Update or create process record
                if pid in self.process_records:
                    record = self.process_records[pid]
                    record.last_seen = datetime.now()

                    # Check for title change (T1036)
                    if name != record.name:
                        old_name = record.name
                        record.update_title(name)
                        logging.warning(f"🏷️  T1036 DETECTED: PID {pid} title changed: {old_name} → {name}")
                        self._alert("T1036", "Masquerading", {
                            'pid': pid,
                            'old_name': old_name,
                            'new_name': name,
                            'changes': record.title_changes
                        })

                        if record.title_changes >= self.TITLE_CHANGE_THRESHOLD:
                            if record not in self.title_change_processes:
                                self.title_change_processes.append(record)
                else:
                    # New process
                    record = ProcessRecord(pid, name, cmdline)
                    self.process_records[pid] = record
                    self.process_history.append(record)

                # Record CPU usage
                if cpu > 0:
                    record.record_cpu(cpu)

                    # Check for CPU spike (T1499)
                    if cpu >= self.CPU_SPIKE_THRESHOLD:
                        self._detect_cpu_spike(record, cpu)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Detect dead processes and respawn loops
        self._detect_dead_and_respawns(current_pids)

    def _detect_cpu_spike(self, record: ProcessRecord, cpu: float):
        """Detect T1499 - Endpoint Denial of Service"""
        self.cpu_spike_count += 1

        if cpu >= self.CRITICAL_CPU_THRESHOLD:
            self.critical_cpu_spikes += 1
            record.mitre_tags.add("T1499")
            logging.critical(f"🔥 T1499 CRITICAL: PID {record.pid} ({record.name}) CPU: {cpu}%")
            self._alert("T1499", "Endpoint Denial of Service - CRITICAL", {
                'pid': record.pid,
                'name': record.name,
                'cpu': cpu,
                'spike_count': self.critical_cpu_spikes
            })
        else:
            logging.warning(f"⚠️  T1499 WARNING: PID {record.pid} ({record.name}) CPU: {cpu}%")

    def _detect_dead_and_respawns(self, current_pids: Set[int]):
        """Detect T1055 - Process Injection (respawn loops)"""
        dead_pids = set(self.process_records.keys()) - current_pids

        for pid in dead_pids:
            record = self.process_records[pid]
            self.dead_processes.append(record)

            # Check for respawn (same name spawns again quickly)
            process_name = record.name
            self.respawn_loops[process_name] += 1

            if self.respawn_loops[process_name] >= self.RESPAWN_THRESHOLD:
                record.mitre_tags.add("T1055")
                record.mitre_tags.add("T1490")
                logging.critical(f"🔄 T1055/T1490 DETECTED: {process_name} respawn loop! Count: {self.respawn_loops[process_name]}")
                self._alert("T1055+T1490", "Process Injection + Inhibit Recovery", {
                    'name': process_name,
                    'respawn_count': self.respawn_loops[process_name],
                    'pattern': 'Respawn loop detected'
                })

            # Remove from active tracking
            del self.process_records[pid]

    def check_system_health(self) -> Dict:
        """Check overall system health for T1499 indicators"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)

        health = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'load_average': load_avg[0],
            'status': 'healthy'
        }

        # Detect T1499 - Resource exhaustion
        if cpu_percent >= self.CRITICAL_CPU_THRESHOLD:
            health['status'] = 'critical'
            health['mitre_technique'] = 'T1499'
            logging.critical(f"🚨 T1499 SYSTEM-WIDE: CPU {cpu_percent}%, Load {load_avg[0]}")
            self._alert("T1499", "System-Wide Resource Exhaustion", health)
        elif cpu_percent >= self.CPU_SPIKE_THRESHOLD:
            health['status'] = 'warning'
            logging.warning(f"⚠️  T1499 WARNING: High CPU {cpu_percent}%")

        return health

    def check_file_integrity(self, critical_files: List[str]):
        """Check for T1485 - Data Destruction / T1490 - Inhibit Recovery"""
        for file_path in critical_files:
            path = Path(file_path)

            if not path.exists():
                logging.critical(f"🚨 T1485/T1490: Critical file MISSING: {file_path}")
                self._alert("T1485+T1490", "Data Destruction + Inhibit Recovery", {
                    'file': file_path,
                    'status': 'DELETED',
                    'severity': 'CRITICAL'
                })
            elif path.stat().st_size == 0:
                logging.critical(f"🚨 T1485/T1490: Critical file EMPTY: {file_path}")
                self._alert("T1485+T1490", "Data Destruction + Inhibit Recovery", {
                    'file': file_path,
                    'status': 'EMPTIED',
                    'size': 0,
                    'severity': 'CRITICAL'
                })

    def _alert(self, technique: str, description: str, data: Dict):
        """Generate MITRE ATT&CK alert"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'technique': technique,
            'description': description,
            'data': data,
            'recorder': self.name
        }

        # Append to alert file
        with open(self.alert_file, 'a') as f:
            f.write(json.dumps(alert) + '\n')

    def generate_report(self) -> Dict:
        """Generate comprehensive MITRE ATT&CK report"""
        # Count processes by MITRE tags
        technique_counts = defaultdict(int)
        for record in self.process_history:
            for tag in record.mitre_tags:
                technique_counts[tag] += 1

        report = {
            'timestamp': datetime.now().isoformat(),
            'recorder': self.name,
            'summary': {
                'total_processes_seen': len(self.process_history),
                'active_processes': len(self.process_records),
                'dead_processes': len(self.dead_processes),
                'cpu_spikes': self.cpu_spike_count,
                'critical_cpu_spikes': self.critical_cpu_spikes,
                'title_changes': len(self.title_change_processes),
                'respawn_loops': len(self.respawn_loops)
            },
            'mitre_techniques': dict(technique_counts),
            'top_suspicious_processes': [
                p.to_dict() for p in sorted(
                    self.process_history,
                    key=lambda x: (len(x.mitre_tags), x.title_changes),
                    reverse=True
                )[:20]
            ],
            'title_change_processes': [p.to_dict() for p in self.title_change_processes[:50]],
            'respawn_loops': dict(self.respawn_loops)
        }

        # Save report
        report_path = LOG_DIR / f"report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        logging.info(f"Report saved: {report_path}")
        return report

    def monitor(self, interval=5, duration=None, critical_files=None):
        """Continuous MITRE ATT&CK monitoring"""
        logging.info("═══════════════════════════════════════════════════════════")
        logging.info("🎯 MITRE ATT&CK PROCESS RECORDER - ACTIVE")
        logging.info("   Monitoring for attack patterns in real-time")
        logging.info("═══════════════════════════════════════════════════════════")

        critical_files = critical_files or []
        start_time = time.time()
        cycle = 0

        try:
            while True:
                cycle += 1
                logging.info(f"\n--- Scan Cycle {cycle} ---")

                # Scan processes
                self.scan_processes()

                # Check system health
                health = self.check_system_health()
                logging.info(f"System: {health['status']} - CPU: {health['cpu_percent']}%")

                # Check file integrity
                if critical_files:
                    self.check_file_integrity(critical_files)

                # Periodic report
                if cycle % 12 == 0:  # Every ~1 minute (5s * 12)
                    report = self.generate_report()
                    logging.info(f"📊 Report: {len(report['mitre_techniques'])} MITRE techniques detected")

                # Check duration
                if duration and (time.time() - start_time) > duration:
                    break

                time.sleep(interval)

        except KeyboardInterrupt:
            logging.info("\nStopping recorder...")
        finally:
            final_report = self.generate_report()
            logging.info("\n═══════════════════════════════════════════════════════════")
            logging.info("📊 FINAL MITRE ATT&CK REPORT")
            logging.info("═══════════════════════════════════════════════════════════")
            logging.info(f"Total processes: {final_report['summary']['total_processes_seen']}")
            logging.info(f"CPU spikes: {final_report['summary']['cpu_spikes']}")
            logging.info(f"Critical spikes: {final_report['summary']['critical_cpu_spikes']}")
            logging.info(f"Title changes: {final_report['summary']['title_changes']}")
            logging.info(f"Respawn loops: {final_report['summary']['respawn_loops']}")
            logging.info(f"\nMITRE Techniques Detected:")
            for technique, count in final_report['mitre_techniques'].items():
                logging.info(f"  {technique}: {count} processes")
            logging.info("═══════════════════════════════════════════════════════════")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="MITRE ATT&CK Process Recorder")
    parser.add_argument('--monitor', action='store_true', help='Start monitoring')
    parser.add_argument('--interval', type=int, default=5, help='Scan interval (seconds)')
    parser.add_argument('--duration', type=int, help='Monitoring duration (seconds)')
    parser.add_argument('--critical-files', nargs='+', help='Critical files to monitor')

    args = parser.parse_args()

    print("""
    ═══════════════════════════════════════════════════════════════════
    🎯 MITRE ATT&CK PROCESS RECORDER

    Monitors and tags processes with MITRE ATT&CK techniques:
    - T1499: Endpoint Denial of Service
    - T1490: Inhibit System Recovery
    - T1485: Data Destruction
    - T1055: Process Injection
    - T1036: Masquerading
    - T1562: Impair Defenses
    - T1071: Application Layer Protocol

    All detections logged and tagged for analysis.
    ═══════════════════════════════════════════════════════════════════
    """)

    recorder = MITREAttackRecorder()

    if args.monitor:
        critical_files = args.critical_files or [
            str(Path.home() / ".defense-agents" / "TIME_REGISTRY_CORE.py"),
            "/sys/firmware",
        ]

        recorder.monitor(
            interval=args.interval,
            duration=args.duration,
            critical_files=critical_files
        )
    else:
        print("Use --monitor to start recording")
        print("Example: python3 MITREAttackRecorder.py --monitor --interval 5")
