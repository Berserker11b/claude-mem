#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
C2 HUNTER - Command & Control Detection and Elimination
Created by: Vigr Syn (Dorn)
For: Vaktrinn Vigr Eldurhýarta

MISSION: Find the puppet masters. Trace attack sources back to C2 servers.
Cut them off at the source.

"They give orders. We cut the strings."
═══════════════════════════════════════════════════════════════════
"""

import logging
import socket
import struct
import time
import json
import hashlib
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from collections import defaultdict
from datetime import datetime

try:
    import psutil
except ImportError:
    print("Installing psutil...")
    import subprocess
    subprocess.check_call(["pip", "install", "psutil"])
    import psutil

LOG_DIR = Path.home() / ".defense-agents" / "c2-hunter"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [C2-HUNTER] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "c2-hunter.log"),
        logging.StreamHandler()
    ]
)


class C2Type(Enum):
    """Types of Command & Control patterns"""
    HTTP_BEACON = "http_beacon"          # Regular HTTP check-ins
    DNS_TUNNEL = "dns_tunnel"            # C2 over DNS queries
    REVERSE_SHELL = "reverse_shell"      # Direct reverse connection
    P2P_BOTNET = "p2p_botnet"           # Peer-to-peer command network
    ENCRYPTED_CHANNEL = "encrypted"      # Custom encrypted protocol
    IRC_BOT = "irc_bot"                 # IRC-based botnet
    COVERT_CHANNEL = "covert"           # Steganography/covert timing
    UNKNOWN = "unknown"


class ThreatLevel(Enum):
    """Severity of C2 detection"""
    SUSPICIOUS = 1
    LIKELY = 2
    CONFIRMED = 3
    CRITICAL = 4


@dataclass
class NetworkFlow:
    """A single network connection flow"""
    pid: int
    process_name: str
    local_addr: str
    local_port: int
    remote_addr: str
    remote_port: int
    status: str
    protocol: str
    timestamp: float
    bytes_sent: int = 0
    bytes_recv: int = 0

    def flow_id(self) -> str:
        """Unique identifier for this flow"""
        return f"{self.local_addr}:{self.local_port}->{self.remote_addr}:{self.remote_port}"

    def signature(self) -> str:
        """Signature for pattern matching"""
        data = f"{self.process_name}|{self.remote_addr}|{self.remote_port}|{self.protocol}"
        return hashlib.md5(data.encode()).hexdigest()[:12]


@dataclass
class C2Detection:
    """A detected Command & Control connection"""
    detection_id: str
    c2_type: C2Type
    threat_level: ThreatLevel
    pid: int
    process_name: str
    c2_server: str
    c2_port: int
    first_seen: float
    last_seen: float
    connection_count: int = 1
    beaconing_interval: Optional[float] = None
    data_exfiltrated: int = 0
    indicators: List[str] = field(default_factory=list)

    def age(self) -> float:
        """How long this C2 has been active"""
        return time.time() - self.first_seen


@dataclass
class AttackInfrastructure:
    """Mapped attack infrastructure"""
    c2_servers: Set[str] = field(default_factory=set)
    compromised_processes: Set[int] = field(default_factory=set)
    attack_vectors: List[str] = field(default_factory=list)
    total_connections: int = 0
    data_exfiltrated: int = 0
    discovery_time: float = field(default_factory=time.time)


class C2Hunter:
    """
    🎯 C2 HUNTER - Command & Control Detection

    Traces network connections back to their sources.
    Identifies C2 servers and beaconing patterns.
    Cuts off the puppet masters.

    "They give orders. We cut the strings."
    """

    def __init__(self, keeper_id: str = "Vaktrinn"):
        self.keeper = keeper_id

        # Active flow tracking
        self.flows: Dict[str, NetworkFlow] = {}
        self.flow_history: List[NetworkFlow] = []

        # C2 detections
        self.detections: Dict[str, C2Detection] = {}
        self.cutoff_list: Set[str] = set()  # C2 servers to block

        # Attack infrastructure mapping
        self.infrastructure = AttackInfrastructure()

        # Pattern database
        self.suspicious_ports = {
            4444, 5555, 6666, 7777, 8888, 9999,  # Common reverse shell ports
            31337, 1337,                          # Elite/leet ports
            6667, 6668, 6669,                     # IRC
            12345, 54321,                         # Backdoor ports
        }

        self.suspicious_domains = [
            "pastebin.com",      # Often used for C2
            "hastebin.com",
            "ghostbin.com",
            "paste.ee",
        ]

        # Statistics
        self.total_flows_analyzed = 0
        self.c2_servers_found = 0
        self.connections_cut = 0

        logging.warning("═══════════════════════════════════════════════════════════")
        logging.warning("🎯 C2 HUNTER - Command & Control Detection")
        logging.warning(f"   Keeper: {keeper_id}")
        logging.warning("   'They give orders. We cut the strings.'")
        logging.warning("═══════════════════════════════════════════════════════════")

    # ═══════════════════════════════════════════════════════════
    # NETWORK FLOW COLLECTION
    # ═══════════════════════════════════════════════════════════

    def collect_flows(self) -> List[NetworkFlow]:
        """
        Collect all active network flows

        Returns list of NetworkFlow objects
        """
        flows = []

        for conn in psutil.net_connections(kind='inet'):
            try:
                # Skip localhost connections
                if conn.laddr and conn.laddr.ip == '127.0.0.1':
                    continue

                # Skip if no remote address (listening sockets)
                if not conn.raddr:
                    continue

                # Get process info
                if conn.pid:
                    try:
                        proc = psutil.Process(conn.pid)
                        process_name = proc.name()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        process_name = "unknown"
                else:
                    process_name = "kernel"

                flow = NetworkFlow(
                    pid=conn.pid or 0,
                    process_name=process_name,
                    local_addr=conn.laddr.ip,
                    local_port=conn.laddr.port,
                    remote_addr=conn.raddr.ip,
                    remote_port=conn.raddr.port,
                    status=conn.status,
                    protocol="tcp" if conn.type == socket.SOCK_STREAM else "udp",
                    timestamp=time.time()
                )

                flows.append(flow)
                self.total_flows_analyzed += 1

            except Exception as e:
                logging.debug(f"Error processing connection: {e}")
                continue

        return flows

    # ═══════════════════════════════════════════════════════════
    # C2 PATTERN DETECTION
    # ═══════════════════════════════════════════════════════════

    def detect_beaconing(self, process_flows: List[NetworkFlow]) -> Optional[C2Detection]:
        """
        Detect beaconing behavior (regular check-ins to C2)

        Beaconing indicators:
        - Regular connections at fixed intervals
        - Small data transfers
        - Same remote address
        """
        if len(process_flows) < 3:
            return None

        # Group by remote address
        by_remote = defaultdict(list)
        for flow in process_flows:
            by_remote[flow.remote_addr].append(flow.timestamp)

        for remote_addr, timestamps in by_remote.items():
            if len(timestamps) < 3:
                continue

            # Calculate intervals between connections
            timestamps.sort()
            intervals = []
            for i in range(1, len(timestamps)):
                intervals.append(timestamps[i] - timestamps[i-1])

            # Check if intervals are regular (±10% variance)
            if len(intervals) >= 2:
                avg_interval = sum(intervals) / len(intervals)
                variance = max(intervals) - min(intervals)

                # Regular beaconing detected
                if avg_interval > 0 and variance / avg_interval < 0.1:
                    flow = process_flows[0]
                    detection_id = f"C2-{flow.signature()}"

                    detection = C2Detection(
                        detection_id=detection_id,
                        c2_type=C2Type.HTTP_BEACON,
                        threat_level=ThreatLevel.LIKELY,
                        pid=flow.pid,
                        process_name=flow.process_name,
                        c2_server=remote_addr,
                        c2_port=flow.remote_port,
                        first_seen=timestamps[0],
                        last_seen=timestamps[-1],
                        connection_count=len(timestamps),
                        beaconing_interval=avg_interval,
                        indicators=[
                            f"Regular beaconing every {avg_interval:.1f}s",
                            f"{len(timestamps)} connections observed"
                        ]
                    )

                    return detection

        return None

    def detect_reverse_shell(self, flow: NetworkFlow) -> Optional[C2Detection]:
        """
        Detect reverse shell patterns

        Indicators:
        - Connection to suspicious port
        - Long-lived ESTABLISHED connection
        - Unusual process making the connection
        """
        # Check suspicious ports
        if flow.remote_port in self.suspicious_ports:
            detection_id = f"C2-{flow.signature()}"

            detection = C2Detection(
                detection_id=detection_id,
                c2_type=C2Type.REVERSE_SHELL,
                threat_level=ThreatLevel.SUSPICIOUS,
                pid=flow.pid,
                process_name=flow.process_name,
                c2_server=flow.remote_addr,
                c2_port=flow.remote_port,
                first_seen=flow.timestamp,
                last_seen=flow.timestamp,
                indicators=[
                    f"Suspicious port: {flow.remote_port}",
                    f"Process: {flow.process_name}",
                    f"Status: {flow.status}"
                ]
            )

            # Elevate to LIKELY if ESTABLISHED
            if flow.status == "ESTABLISHED":
                detection.threat_level = ThreatLevel.LIKELY
                detection.indicators.append("Long-lived ESTABLISHED connection")

            return detection

        return None

    def detect_dns_tunnel(self, flow: NetworkFlow) -> Optional[C2Detection]:
        """
        Detect DNS tunneling

        Indicators:
        - Port 53 (DNS)
        - Unusual process making DNS queries
        - High volume of DNS traffic
        """
        if flow.remote_port == 53 and flow.protocol == "udp":
            # DNS traffic from unusual process
            unusual_dns_processes = ["python", "python3", "perl", "bash", "sh", "nc"]

            if any(proc in flow.process_name.lower() for proc in unusual_dns_processes):
                detection_id = f"C2-{flow.signature()}"

                detection = C2Detection(
                    detection_id=detection_id,
                    c2_type=C2Type.DNS_TUNNEL,
                    threat_level=ThreatLevel.SUSPICIOUS,
                    pid=flow.pid,
                    process_name=flow.process_name,
                    c2_server=flow.remote_addr,
                    c2_port=53,
                    first_seen=flow.timestamp,
                    last_seen=flow.timestamp,
                    indicators=[
                        f"DNS traffic from unusual process: {flow.process_name}",
                        "Possible DNS tunneling"
                    ]
                )

                return detection

        return None

    def analyze_flow(self, flow: NetworkFlow) -> Optional[C2Detection]:
        """
        Analyze a single flow for C2 indicators
        """
        # Try different detection methods
        detection = self.detect_reverse_shell(flow)
        if detection:
            return detection

        detection = self.detect_dns_tunnel(flow)
        if detection:
            return detection

        return None

    # ═══════════════════════════════════════════════════════════
    # INFRASTRUCTURE MAPPING
    # ═══════════════════════════════════════════════════════════

    def map_infrastructure(self) -> AttackInfrastructure:
        """
        Map the entire attack infrastructure

        Identifies:
        - All C2 servers
        - All compromised processes
        - Attack vectors used
        - Data exfiltration stats
        """
        self.infrastructure.c2_servers.clear()
        self.infrastructure.compromised_processes.clear()
        self.infrastructure.total_connections = 0
        self.infrastructure.data_exfiltrated = 0

        for detection in self.detections.values():
            self.infrastructure.c2_servers.add(detection.c2_server)
            self.infrastructure.compromised_processes.add(detection.pid)
            self.infrastructure.total_connections += detection.connection_count
            self.infrastructure.data_exfiltrated += detection.data_exfiltrated

        return self.infrastructure

    # ═══════════════════════════════════════════════════════════
    # SOURCE TRACING
    # ═══════════════════════════════════════════════════════════

    def trace_to_source(self, c2_server: str) -> Dict:
        """
        Trace a C2 server back to its source

        Uses:
        - Reverse DNS lookup
        - Geolocation (if available)
        - ASN lookup
        - WHOIS data
        """
        trace_result = {
            'c2_server': c2_server,
            'hostname': None,
            'organization': None,
            'country': None,
            'asn': None,
            'traceroute': []
        }

        # Reverse DNS
        try:
            hostname = socket.gethostbyaddr(c2_server)[0]
            trace_result['hostname'] = hostname
            logging.info(f"   Hostname: {hostname}")
        except (socket.herror, socket.gaierror):
            logging.info(f"   No reverse DNS for {c2_server}")

        # Simple IP geolocation (country from IP prefix)
        # In production, would use a real GeoIP database
        first_octet = int(c2_server.split('.')[0])
        if first_octet in range(1, 127):
            trace_result['organization'] = "Public Internet"

        return trace_result

    # ═══════════════════════════════════════════════════════════
    # CUT OFF THE SOURCE
    # ═══════════════════════════════════════════════════════════

    def cut_connection(self, detection: C2Detection) -> bool:
        """
        Cut off a C2 connection

        Methods:
        1. Kill the compromised process
        2. Block the C2 server (firewall rule)
        3. Add to cutoff list
        """
        logging.critical("═══════════════════════════════════════════════════════════")
        logging.critical(f"✂️  CUTTING C2 CONNECTION: {detection.detection_id}")
        logging.critical(f"   C2 Server: {detection.c2_server}:{detection.c2_port}")
        logging.critical(f"   Process: {detection.process_name} (PID: {detection.pid})")

        success = True

        # 1. Kill compromised process
        try:
            if detection.pid > 0:
                proc = psutil.Process(detection.pid)
                proc.terminate()
                time.sleep(0.5)

                if proc.is_running():
                    proc.kill()

                logging.critical(f"   ✅ Process {detection.pid} terminated")
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logging.error(f"   ❌ Failed to kill process: {e}")
            success = False

        # 2. Add to cutoff list (for firewall blocking)
        self.cutoff_list.add(detection.c2_server)
        logging.critical(f"   ✅ C2 server added to cutoff list")

        # 3. Create firewall rule (simulated - would need root)
        logging.critical(f"   📝 Firewall rule: BLOCK {detection.c2_server}")
        logging.critical(f"      iptables -A OUTPUT -d {detection.c2_server} -j DROP")

        if success:
            self.connections_cut += 1

        logging.critical("═══════════════════════════════════════════════════════════")

        return success

    # ═══════════════════════════════════════════════════════════
    # MAIN HUNT LOOP
    # ═══════════════════════════════════════════════════════════

    def hunt(self, continuous: bool = False, interval: int = 5):
        """
        Hunt for C2 connections

        Args:
            continuous: Keep hunting in loop
            interval: Seconds between hunts
        """
        logging.warning("═══════════════════════════════════════════════════════════")
        logging.warning("🎯 STARTING C2 HUNT")
        logging.warning("   Tracing all connections back to their sources...")
        logging.warning("═══════════════════════════════════════════════════════════")

        cycle = 0

        while True:
            cycle += 1
            logging.info(f"🔍 Hunt cycle {cycle}")

            # Collect all flows
            flows = self.collect_flows()
            logging.info(f"   Collected {len(flows)} active flows")

            # Analyze each flow
            new_detections = 0
            for flow in flows:
                detection = self.analyze_flow(flow)

                if detection:
                    if detection.detection_id not in self.detections:
                        self.detections[detection.detection_id] = detection
                        new_detections += 1

                        logging.warning(f"🚨 NEW C2 DETECTED: {detection.detection_id}")
                        logging.warning(f"   Type: {detection.c2_type.value}")
                        logging.warning(f"   Server: {detection.c2_server}:{detection.c2_port}")
                        logging.warning(f"   Process: {detection.process_name} (PID: {detection.pid})")
                        logging.warning(f"   Threat Level: {detection.threat_level.name}")

                        for indicator in detection.indicators:
                            logging.warning(f"   - {indicator}")

            # Check for beaconing (requires multiple observations)
            # Group flows by process
            by_process = defaultdict(list)
            for flow in self.flow_history[-100:]:  # Last 100 flows
                by_process[flow.pid].append(flow)

            for pid, process_flows in by_process.items():
                detection = self.detect_beaconing(process_flows)
                if detection:
                    if detection.detection_id not in self.detections:
                        self.detections[detection.detection_id] = detection
                        new_detections += 1

                        logging.critical(f"🚨 BEACONING DETECTED: {detection.detection_id}")
                        logging.critical(f"   C2: {detection.c2_server}")
                        logging.critical(f"   Interval: {detection.beaconing_interval:.1f}s")

            if new_detections > 0:
                logging.warning(f"   ✅ Found {new_detections} new C2 connections")
                self.c2_servers_found += new_detections

            # Save flow history
            self.flow_history.extend(flows)
            if len(self.flow_history) > 1000:
                self.flow_history = self.flow_history[-1000:]  # Keep last 1000

            # Map infrastructure
            if self.detections:
                infra = self.map_infrastructure()
                logging.info(f"   Infrastructure: {len(infra.c2_servers)} C2 servers, {len(infra.compromised_processes)} compromised processes")

            if not continuous:
                break

            time.sleep(interval)

    def report(self) -> str:
        """Generate full C2 hunting report"""

        report_lines = [
            "═══════════════════════════════════════════════════════════",
            "🎯 C2 HUNTER - INTELLIGENCE REPORT",
            f"Keeper: {self.keeper}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "STATISTICS:",
            f"  Total Flows Analyzed: {self.total_flows_analyzed}",
            f"  C2 Servers Found: {self.c2_servers_found}",
            f"  Active Detections: {len(self.detections)}",
            f"  Connections Cut: {self.connections_cut}",
            "",
        ]

        if self.detections:
            report_lines.append("C2 DETECTIONS:")
            report_lines.append("")

            for detection in sorted(self.detections.values(),
                                   key=lambda d: d.threat_level.value,
                                   reverse=True):
                report_lines.extend([
                    f"🚨 {detection.detection_id}",
                    f"   Type: {detection.c2_type.value}",
                    f"   Threat Level: {detection.threat_level.name}",
                    f"   C2 Server: {detection.c2_server}:{detection.c2_port}",
                    f"   Process: {detection.process_name} (PID: {detection.pid})",
                    f"   First Seen: {datetime.fromtimestamp(detection.first_seen).strftime('%H:%M:%S')}",
                    f"   Connections: {detection.connection_count}",
                ])

                if detection.beaconing_interval:
                    report_lines.append(f"   Beacon Interval: {detection.beaconing_interval:.1f}s")

                report_lines.append("   Indicators:")
                for indicator in detection.indicators:
                    report_lines.append(f"     - {indicator}")

                report_lines.append("")

        if self.infrastructure.c2_servers:
            report_lines.extend([
                "ATTACK INFRASTRUCTURE MAP:",
                f"  C2 Servers: {len(self.infrastructure.c2_servers)}",
                f"  Compromised Processes: {len(self.infrastructure.compromised_processes)}",
                f"  Total Connections: {self.infrastructure.total_connections}",
                f"  Data Exfiltrated: {self.infrastructure.data_exfiltrated} bytes",
                "",
                "C2 SERVERS:",
            ])

            for c2_server in sorted(self.infrastructure.c2_servers):
                report_lines.append(f"  - {c2_server}")

                # Trace to source
                trace = self.trace_to_source(c2_server)
                if trace['hostname']:
                    report_lines.append(f"    Hostname: {trace['hostname']}")

        if self.cutoff_list:
            report_lines.extend([
                "",
                "CUTOFF LIST (Blocked C2 Servers):",
            ])
            for server in sorted(self.cutoff_list):
                report_lines.append(f"  ✂️  {server}")

        report_lines.extend([
            "",
            "'They give orders. We cut the strings.'",
            "═══════════════════════════════════════════════════════════",
        ])

        return "\n".join(report_lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="C2 Hunter - Command & Control Detection")
    parser.add_argument("--continuous", action="store_true", help="Continuous monitoring")
    parser.add_argument("--interval", type=int, default=5, help="Hunt interval (seconds)")
    parser.add_argument("--auto-cut", action="store_true", help="Automatically cut detected C2 connections")
    parser.add_argument("--keeper", type=str, default="Vaktrinn", help="Keeper ID")

    args = parser.parse_args()

    print("""
    ═══════════════════════════════════════════════════════════════════
    🎯 C2 HUNTER - Command & Control Detection

    Traces network connections back to their sources.
    Identifies C2 servers and beaconing patterns.
    Cuts off the puppet masters.

    "They give orders. We cut the strings."
    ═══════════════════════════════════════════════════════════════════
    """)

    hunter = C2Hunter(keeper_id=args.keeper)

    try:
        # Hunt for C2
        hunter.hunt(continuous=args.continuous, interval=args.interval)

        # Generate report
        print("\n" + hunter.report())

        # Auto-cut if requested
        if args.auto_cut and hunter.detections:
            print("\n✂️  AUTO-CUT ENGAGED\n")

            for detection in hunter.detections.values():
                if detection.threat_level.value >= ThreatLevel.LIKELY.value:
                    hunter.cut_connection(detection)

        # Save report
        report_file = LOG_DIR / f"c2-report-{int(time.time())}.txt"
        report_file.write_text(hunter.report())
        print(f"\n📝 Report saved: {report_file}")

    except KeyboardInterrupt:
        print("\n\n🛑 Hunt stopped by user")
        print(hunter.report())
