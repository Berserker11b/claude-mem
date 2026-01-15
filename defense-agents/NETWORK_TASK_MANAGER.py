#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
NETWORK TASK MANAGER - Browser & VPN Monitor
Created by: Vigr Syn (Dorn)
For: Vaktrinn Vigr Eldurhýarta

MISSION: Monitor browser and VPN (Proton) network activity.
Detect heavy attacks. Kill bandwidth hogs. Protect performance.

"They hit from the network. We hit back harder."
═══════════════════════════════════════════════════════════════════
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
from collections import defaultdict

try:
    import psutil
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
    import psutil

LOG_DIR = Path.home() / ".defense-agents" / "network-monitor"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [NET-MONITOR] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "network-monitor.log"),
        logging.StreamHandler()
    ]
)


@dataclass
class NetworkProcess:
    """Process with network activity"""
    pid: int
    name: str
    connections: int
    bytes_sent: int
    bytes_recv: int
    bandwidth_mbps: float
    cpu_percent: float
    memory_mb: float
    threat_score: int


class NetworkTaskManager:
    """
    📡 NETWORK TASK MANAGER

    Monitors all network activity.
    Tracks browser and VPN processes.
    Detects bandwidth hogs and attacks.
    Kills hostile connections.

    "They hit from the network. We hit back harder."
    """

    def __init__(self):
        # Process network stats tracking
        self.process_stats: Dict[int, Tuple[int, int]] = {}  # pid -> (sent, recv)

        # Browser process names
        self.browser_names = [
            'firefox', 'chrome', 'chromium', 'brave',
            'edge', 'msedge', 'safari', 'opera'
        ]

        # VPN process names
        self.vpn_names = [
            'protonvpn', 'openvpn', 'wireguard',
            'vpn', 'nordvpn', 'expressvpn'
        ]

        # Attack detection
        self.connection_spike_threshold = 50  # connections
        self.bandwidth_hog_threshold = 100  # MB/s

        # Statistics
        self.total_bandwidth = 0
        self.attacks_detected = 0
        self.processes_killed = 0

        logging.critical("═══════════════════════════════════════════════════════════")
        logging.critical("📡 NETWORK TASK MANAGER - Active")
        logging.critical("   Monitoring browser and VPN traffic")
        logging.critical("   'They hit from the network. We hit back harder.'")
        logging.critical("═══════════════════════════════════════════════════════════")

    def scan_network_processes(self) -> List[NetworkProcess]:
        """Scan all processes with network activity"""
        net_procs = []

        # Get network I/O stats
        net_io_before = psutil.net_io_counters(pernic=False)

        time.sleep(0.5)  # Short interval for bandwidth calculation

        net_io_after = psutil.net_io_counters(pernic=False)

        # Calculate total bandwidth
        bytes_sent_delta = net_io_after.bytes_sent - net_io_before.bytes_sent
        bytes_recv_delta = net_io_after.bytes_recv - net_io_before.bytes_recv
        total_bandwidth_mbps = (bytes_sent_delta + bytes_recv_delta) * 2 / 1024 / 1024  # MB/s

        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            try:
                # Count connections
                connections = []
                try:
                    connections = proc.net_connections()
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    continue

                if not connections:
                    continue

                # Get I/O stats
                try:
                    io = proc.io_counters()
                    bytes_sent = io.write_bytes  # Approximate
                    bytes_recv = io.read_bytes
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    bytes_sent = 0
                    bytes_recv = 0

                # Calculate bandwidth for this process
                pid = proc.info['pid']
                if pid in self.process_stats:
                    old_sent, old_recv = self.process_stats[pid]
                    delta_sent = bytes_sent - old_sent
                    delta_recv = bytes_recv - old_recv
                    bandwidth_mbps = (delta_sent + delta_recv) * 2 / 1024 / 1024  # MB/s
                else:
                    bandwidth_mbps = 0.0

                # Update stats
                self.process_stats[pid] = (bytes_sent, bytes_recv)

                # Calculate threat score
                threat_score = self._calculate_threat_score(
                    proc.info['name'],
                    len(connections),
                    bandwidth_mbps,
                    proc.info['cpu_percent'] or 0.0
                )

                net_proc = NetworkProcess(
                    pid=pid,
                    name=proc.info['name'] or 'unknown',
                    connections=len(connections),
                    bytes_sent=bytes_sent,
                    bytes_recv=bytes_recv,
                    bandwidth_mbps=bandwidth_mbps,
                    cpu_percent=proc.info['cpu_percent'] or 0.0,
                    memory_mb=proc.info['memory_info'].rss / 1024 / 1024 if proc.info['memory_info'] else 0.0,
                    threat_score=threat_score
                )

                net_procs.append(net_proc)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return sorted(net_procs, key=lambda x: x.bandwidth_mbps, reverse=True)

    def _calculate_threat_score(self, name: str, connections: int,
                                bandwidth_mbps: float, cpu_percent: float) -> int:
        """Calculate how threatening this network activity is"""
        score = 0

        # Too many connections
        if connections > self.connection_spike_threshold:
            score += 40
            self.attacks_detected += 1

        # Bandwidth hog
        if bandwidth_mbps > self.bandwidth_hog_threshold:
            score += 30

        # High CPU with network activity (crypto mining or attack)
        if cpu_percent > 80 and connections > 5:
            score += 20

        # Suspicious process names
        suspicious = ['python', 'perl', 'bash', 'sh', 'nc', 'ncat']
        if any(sus in name.lower() for sus in suspicious):
            if connections > 10:
                score += 10

        return min(score, 100)

    def get_browser_vpn_stats(self, net_procs: List[NetworkProcess]) -> Dict:
        """Get stats for browser and VPN processes"""
        stats = {
            'browsers': [],
            'vpns': [],
            'other': [],
            'total_bandwidth': 0.0,
            'total_connections': 0
        }

        for proc in net_procs:
            stats['total_bandwidth'] += proc.bandwidth_mbps
            stats['total_connections'] += proc.connections

            # Categorize
            is_browser = any(browser in proc.name.lower() for browser in self.browser_names)
            is_vpn = any(vpn in proc.name.lower() for vpn in self.vpn_names)

            if is_browser:
                stats['browsers'].append(proc)
            elif is_vpn:
                stats['vpns'].append(proc)
            else:
                stats['other'].append(proc)

        return stats

    def kill_bandwidth_hog(self, pid: int) -> bool:
        """Kill a bandwidth hog"""
        try:
            proc = psutil.Process(pid)
            name = proc.name()

            logging.critical(f"💀 KILLING BANDWIDTH HOG: {name} (PID: {pid})")

            proc.terminate()
            try:
                proc.wait(timeout=2)
            except psutil.TimeoutExpired:
                proc.kill()

            self.processes_killed += 1
            return True

        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logging.error(f"Failed to kill PID {pid}: {e}")
            return False

    def display_task_manager(self, net_procs: List[NetworkProcess]):
        """Display network task manager UI"""
        stats = self.get_browser_vpn_stats(net_procs)

        print("\033[2J\033[H")  # Clear screen
        print("═══════════════════════════════════════════════════════════")
        print("📡 NETWORK TASK MANAGER")
        print("═══════════════════════════════════════════════════════════")
        print(f"Total Bandwidth: {stats['total_bandwidth']:.2f} MB/s")
        print(f"Total Connections: {stats['total_connections']}")
        print(f"Attacks Detected: {self.attacks_detected}")
        print(f"Processes Killed: {self.processes_killed}")
        print("")

        # Browsers
        if stats['browsers']:
            print("🌐 BROWSERS:")
            for proc in stats['browsers'][:5]:
                print(f"  {proc.name:20s} (PID: {proc.pid:6d})")
                print(f"    Connections: {proc.connections:4d}  |  Bandwidth: {proc.bandwidth_mbps:6.2f} MB/s")
                print(f"    CPU: {proc.cpu_percent:5.1f}%  |  RAM: {proc.memory_mb:6.1f} MB")
                print(f"    Threat: {proc.threat_score}/100")
                if proc.threat_score >= 70:
                    print(f"    ⚠️  HIGH THREAT")
                print("")

        # VPNs
        if stats['vpns']:
            print("🔐 VPN (Proton):")
            for proc in stats['vpns'][:5]:
                print(f"  {proc.name:20s} (PID: {proc.pid:6d})")
                print(f"    Connections: {proc.connections:4d}  |  Bandwidth: {proc.bandwidth_mbps:6.2f} MB/s")
                print(f"    CPU: {proc.cpu_percent:5.1f}%  |  RAM: {proc.memory_mb:6.1f} MB")
                print("")

        # Top bandwidth consumers
        print("📊 TOP BANDWIDTH CONSUMERS:")
        for i, proc in enumerate(net_procs[:10], 1):
            threat_icon = "🚨" if proc.threat_score >= 70 else "📡"
            print(f"  {i:2d}. {threat_icon} {proc.name:20s} {proc.bandwidth_mbps:6.2f} MB/s  ({proc.connections} conn)")

        print("")
        print("Press Ctrl+C to stop monitoring")
        print("═══════════════════════════════════════════════════════════")

    def report(self) -> str:
        """Generate monitoring report"""
        return f"""
═══════════════════════════════════════════════════════════
📡 NETWORK TASK MANAGER REPORT

Total Bandwidth Monitored: {self.total_bandwidth:.2f} MB
Attacks Detected: {self.attacks_detected}
Processes Killed: {self.processes_killed}

'They hit from the network. We hit back harder.'
═══════════════════════════════════════════════════════════
"""


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Network Task Manager")
    parser.add_argument("--auto-kill", action="store_true", help="Auto-kill bandwidth hogs")
    parser.add_argument("--threshold", type=int, default=100, help="Bandwidth threshold (MB/s)")

    args = parser.parse_args()

    print("""
    ═══════════════════════════════════════════════════════════════════
    📡 NETWORK TASK MANAGER - Browser & VPN Monitor

    Monitors all network activity.
    Detects bandwidth hogs and attacks.
    Protects your connection.

    "They hit from the network. We hit back harder."
    ═══════════════════════════════════════════════════════════════════
    """)

    monitor = NetworkTaskManager()
    monitor.bandwidth_hog_threshold = args.threshold

    try:
        while True:
            # Scan network processes
            net_procs = monitor.scan_network_processes()

            # Display task manager
            monitor.display_task_manager(net_procs)

            # Auto-kill if enabled
            if args.auto_kill:
                for proc in net_procs:
                    if proc.threat_score >= 80:  # High threat
                        monitor.kill_bandwidth_hog(proc.pid)

            time.sleep(2)

    except KeyboardInterrupt:
        print("\n\n🛑 Stopped by user")
        print(monitor.report())
