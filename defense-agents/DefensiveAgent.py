#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
DEFENSIVE AGENT - Transparent Malware Defense
Created by: Claude (Anthropic)
Purpose: Legitimate system defense with full transparency
═══════════════════════════════════════════════════════════════════
"""

import psutil
import time
import json
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
LOG_DIR = Path.home() / ".defense-agents"
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "defense-agent.log"),
        logging.StreamHandler()
    ]
)

class DefensiveAgent:
    """Transparent defensive monitoring agent"""

    def __init__(self):
        self.name = "DefensiveAgent-1"
        self.suspicious_patterns = [
            # Actual malware patterns (not legitimate software)
            'cryptolocker',
            'wannacry',
            'ransomware',
            'keylogger',
            'backdoor',
            'rootkit',
            # Add specific IOCs for investigation
        ]
        self.baseline_processes = set()
        self.alerts = []

    def get_process_info(self):
        """Collect information about running processes"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return processes

    def establish_baseline(self):
        """Establish baseline of normal processes"""
        logging.info("Establishing process baseline...")
        processes = self.get_process_info()
        self.baseline_processes = {p['name'] for p in processes}
        logging.info(f"Baseline established: {len(self.baseline_processes)} processes")
        return self.baseline_processes

    def detect_anomalies(self):
        """Detect suspicious process activity"""
        current_processes = self.get_process_info()
        current_names = {p['name'] for p in current_processes}

        # New processes since baseline
        new_processes = current_names - self.baseline_processes

        if new_processes:
            logging.info(f"New processes detected: {new_processes}")

        # Check for suspicious patterns
        suspicious = []
        for proc in current_processes:
            proc_name = proc['name'].lower()
            for pattern in self.suspicious_patterns:
                if pattern in proc_name:
                    suspicious.append(proc)
                    logging.warning(f"SUSPICIOUS: {proc}")

        return suspicious

    def monitor_network(self):
        """Monitor network connections"""
        connections = psutil.net_connections(kind='inet')
        external_connections = [
            conn for conn in connections
            if conn.status == 'ESTABLISHED' and conn.raddr
        ]

        if external_connections:
            logging.info(f"Active external connections: {len(external_connections)}")

        return external_connections

    def check_system_health(self):
        """Check overall system health"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        health = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'disk_percent': disk.percent,
            'status': 'healthy'
        }

        # Alert on high resource usage
        if cpu_percent > 90:
            health['status'] = 'warning'
            logging.warning(f"High CPU usage: {cpu_percent}%")
        if memory.percent > 90:
            health['status'] = 'warning'
            logging.warning(f"High memory usage: {memory.percent}%")

        return health

    def generate_report(self):
        """Generate defense report"""
        report = {
            'agent': self.name,
            'timestamp': datetime.now().isoformat(),
            'processes': len(self.baseline_processes),
            'alerts': self.alerts,
            'system_health': self.check_system_health()
        }

        report_path = LOG_DIR / f"report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        logging.info(f"Report saved: {report_path}")
        return report

    def run(self, duration=None, interval=10):
        """Run continuous monitoring"""
        logging.info(f"Starting {self.name}...")
        logging.info(f"Scan interval: {interval} seconds")

        self.establish_baseline()

        start_time = time.time()
        cycle = 0

        try:
            while True:
                cycle += 1
                logging.info(f"\n--- Cycle {cycle} ---")

                # Check for anomalies
                suspicious = self.detect_anomalies()
                if suspicious:
                    self.alerts.extend(suspicious)

                # Monitor network
                self.monitor_network()

                # Check system health
                health = self.check_system_health()
                logging.info(f"System: {health['status']} - CPU: {health['cpu_percent']}% - MEM: {health['memory_percent']}%")

                # Check duration limit
                if duration and (time.time() - start_time) > duration:
                    logging.info("Duration limit reached")
                    break

                # Generate periodic report
                if cycle % 10 == 0:
                    self.generate_report()

                time.sleep(interval)

        except KeyboardInterrupt:
            logging.info("\nStopping agent (user interrupt)...")
        except Exception as e:
            logging.error(f"Agent error: {e}")
        finally:
            final_report = self.generate_report()
            logging.info("\n" + "="*60)
            logging.info("FINAL REPORT")
            logging.info("="*60)
            logging.info(f"Total cycles: {cycle}")
            logging.info(f"Total alerts: {len(self.alerts)}")
            logging.info(f"Report: {LOG_DIR / 'report-*.json'}")

if __name__ == "__main__":
    print("""
    ═══════════════════════════════════════════════════════════════════
    DEFENSIVE AGENT - Transparent System Defense
    ═══════════════════════════════════════════════════════════════════

    This agent provides transparent, legitimate system monitoring.
    All actions are logged. No stealth operations.

    Press Ctrl+C to stop
    ═══════════════════════════════════════════════════════════════════
    """)

    agent = DefensiveAgent()
    agent.run()
