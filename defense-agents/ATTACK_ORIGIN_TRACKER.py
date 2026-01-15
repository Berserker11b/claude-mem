#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
ATTACK ORIGIN TRACKER - Find the Source
Created by: Vigr Syn (Dorn)
For: Vaktrinn Vigr Eldurhýarta

MISSION: Determine if attacks come from WITHIN the device or OUTSIDE.
Everything leaves a fingerprint. We find it. We trace it. We kill it.

"Inside or outside - we will find you."
═══════════════════════════════════════════════════════════════════
"""

import os
import sys
import time
import socket
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime

try:
    import psutil
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
    import psutil

LOG_DIR = Path.home() / ".defense-agents" / "attack-origin"
LOG_DIR.mkdir(parents=True, exist_ok=True)

FINGERPRINT_DB = LOG_DIR / "attack_fingerprints.txt"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [ORIGIN] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f"attack-origin-{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)


@dataclass
class AttackFingerprint:
    """A unique fingerprint left by an attack"""
    fingerprint_id: str
    origin_type: str  # 'INTERNAL' or 'EXTERNAL'
    source_ip: Optional[str]
    source_port: Optional[int]
    target_ip: Optional[str]
    target_port: Optional[int]
    process_name: Optional[str]
    process_pid: Optional[int]
    exe_path: Optional[str]
    cmdline: Optional[str]
    timestamp: float
    threat_indicators: List[str] = field(default_factory=list)
    raw_signature: str = ""

    def signature(self) -> str:
        """Generate unique signature"""
        data = f"{self.origin_type}|{self.source_ip}|{self.process_name}|{self.exe_path}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]


@dataclass
class AttackAnalysis:
    """Analysis of attack origin"""
    total_attacks: int = 0
    internal_attacks: int = 0
    external_attacks: int = 0
    internal_fingerprints: Set[str] = field(default_factory=set)
    external_fingerprints: Set[str] = field(default_factory=set)
    compromised_processes: Set[int] = field(default_factory=set)
    attack_ips: Set[str] = field(default_factory=set)


class AttackOriginTracker:
    """
    🎯 ATTACK ORIGIN TRACKER

    Determines if attacks originate from within device or outside.
    Every attack leaves fingerprints. We collect them all.

    "Inside or outside - we will find you."
    """

    def __init__(self):
        self.fingerprints: List[AttackFingerprint] = []
        self.analysis = AttackAnalysis()

        # Known internal IPs
        self.internal_ips = {'127.0.0.1', '::1', 'localhost'}

        # Suspicious ports (common attack vectors)
        self.suspicious_ports = {
            4444, 5555, 6666, 7777, 8888, 9999,  # Reverse shells
            31337, 1337,                          # Leet ports
            6667, 6668, 6669,                     # IRC
            1080, 3128, 8080,                     # Proxies
            3389, 5900,                           # RDP, VNC
        }

        logging.critical("═══════════════════════════════════════════════════════════")
        logging.critical("🎯 ATTACK ORIGIN TRACKER - Active")
        logging.critical("   Fingerprinting all attacks")
        logging.critical("   'Inside or outside - we will find you.'")
        logging.critical("═══════════════════════════════════════════════════════════")

    def analyze_all_connections(self) -> List[AttackFingerprint]:
        """Analyze ALL network connections to find attack origins"""
        fingerprints = []

        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
            try:
                connections = proc.net_connections()

                for conn in connections:
                    # Analyze this connection
                    fp = self._analyze_connection(proc, conn)
                    if fp:
                        fingerprints.append(fp)
                        self.fingerprints.append(fp)

            except (psutil.AccessDenied, psutil.NoSuchProcess):
                continue

        return fingerprints

    def _analyze_connection(self, proc, conn) -> Optional[AttackFingerprint]:
        """Analyze a single connection for attack origin"""
        if not conn.raddr:  # No remote address
            return None

        # Determine origin type
        origin_type = self._determine_origin(conn)

        # Detect threat indicators
        threat_indicators = []

        # Suspicious port
        if conn.raddr.port in self.suspicious_ports:
            threat_indicators.append(f"Suspicious port: {conn.raddr.port}")

        # Suspicious process name
        suspicious_names = ['python', 'perl', 'bash', 'sh', 'nc', 'ncat', 'curl', 'wget']
        proc_name = proc.info['name'] or ''
        if any(sus in proc_name.lower() for sus in suspicious_names):
            threat_indicators.append(f"Suspicious process: {proc_name}")

        # Established connection to unknown remote
        if conn.status == 'ESTABLISHED' and not self._is_trusted_ip(conn.raddr.ip):
            threat_indicators.append(f"Untrusted connection: {conn.raddr.ip}")

        # Only create fingerprint if there are threat indicators
        if not threat_indicators and origin_type != 'INTERNAL':
            return None

        # Create fingerprint
        fp = AttackFingerprint(
            fingerprint_id=f"FP-{int(time.time() * 1000)}",
            origin_type=origin_type,
            source_ip=conn.laddr.ip if conn.laddr else None,
            source_port=conn.laddr.port if conn.laddr else None,
            target_ip=conn.raddr.ip,
            target_port=conn.raddr.port,
            process_name=proc.info['name'],
            process_pid=proc.info['pid'],
            exe_path=proc.info['exe'],
            cmdline=' '.join(proc.info['cmdline']) if proc.info['cmdline'] else '',
            timestamp=time.time(),
            threat_indicators=threat_indicators,
            raw_signature=f"{conn.laddr}→{conn.raddr}:{conn.status}"
        )

        # Update analysis
        self.analysis.total_attacks += 1

        if origin_type == 'INTERNAL':
            self.analysis.internal_attacks += 1
            self.analysis.internal_fingerprints.add(fp.signature())
            self.analysis.compromised_processes.add(proc.info['pid'])

            logging.critical("═══════════════════════════════════════════════════════════")
            logging.critical(f"🚨 INTERNAL ATTACK DETECTED")
            logging.critical(f"   Process: {proc.info['name']} (PID: {proc.info['pid']})")
            logging.critical(f"   Exe: {proc.info['exe']}")
            logging.critical(f"   Connection: {conn.laddr} → {conn.raddr}")
            logging.critical(f"   Indicators:")
            for indicator in threat_indicators:
                logging.critical(f"     - {indicator}")
            logging.critical("   ⚠️  DEVICE MAY BE COMPROMISED")
            logging.critical("═══════════════════════════════════════════════════════════")

        else:
            self.analysis.external_attacks += 1
            self.analysis.external_fingerprints.add(fp.signature())
            self.analysis.attack_ips.add(conn.raddr.ip)

            logging.warning("═══════════════════════════════════════════════════════════")
            logging.warning(f"🌐 EXTERNAL ATTACK DETECTED")
            logging.warning(f"   From: {conn.raddr.ip}:{conn.raddr.port}")
            logging.warning(f"   To: {proc.info['name']} (PID: {proc.info['pid']})")
            logging.warning(f"   Indicators:")
            for indicator in threat_indicators:
                logging.warning(f"     - {indicator}")
            logging.warning("═══════════════════════════════════════════════════════════")

        return fp

    def _determine_origin(self, conn) -> str:
        """Determine if connection is INTERNAL or EXTERNAL origin"""
        if not conn.raddr:
            return 'UNKNOWN'

        remote_ip = conn.raddr.ip

        # Check if localhost
        if remote_ip in self.internal_ips:
            return 'INTERNAL'

        # Check if private IP
        if self._is_private_ip(remote_ip):
            return 'INTERNAL'

        # Check if loopback
        if remote_ip.startswith('127.') or remote_ip == '::1':
            return 'INTERNAL'

        return 'EXTERNAL'

    def _is_private_ip(self, ip: str) -> bool:
        """Check if IP is private/internal"""
        if ':' in ip:  # IPv6
            return ip.startswith('fe80:') or ip.startswith('::1')

        # IPv4
        octets = ip.split('.')
        if len(octets) != 4:
            return False

        first = int(octets[0])
        second = int(octets[1])

        # Private ranges
        if first == 10:
            return True
        if first == 172 and 16 <= second <= 31:
            return True
        if first == 192 and second == 168:
            return True

        return False

    def _is_trusted_ip(self, ip: str) -> bool:
        """Check if IP is trusted (add your trusted IPs here)"""
        trusted = {
            # Add trusted IPs here
            # Example: your VPN server, trusted APIs, etc.
        }
        return ip in trusted

    def trace_attack_source(self, fingerprint: AttackFingerprint) -> Dict:
        """Trace attack source with reverse DNS and geolocation"""
        trace = {
            'fingerprint_id': fingerprint.fingerprint_id,
            'origin_type': fingerprint.origin_type,
            'hostname': None,
            'organization': None,
            'country': None
        }

        if fingerprint.target_ip:
            # Reverse DNS lookup
            try:
                hostname = socket.gethostbyaddr(fingerprint.target_ip)[0]
                trace['hostname'] = hostname
                logging.info(f"   Hostname: {hostname}")
            except (socket.herror, socket.gaierror):
                logging.debug(f"   No reverse DNS for {fingerprint.target_ip}")

        return trace

    def save_fingerprints(self):
        """Save all fingerprints to disk"""
        with open(FINGERPRINT_DB, 'a') as f:
            for fp in self.fingerprints:
                line = f"{fp.timestamp}|{fp.origin_type}|{fp.signature()}|{fp.target_ip}|{fp.process_name}|{','.join(fp.threat_indicators)}\n"
                f.write(line)

    def report(self) -> str:
        """Generate attack origin report"""
        lines = [
            "═══════════════════════════════════════════════════════════",
            "🎯 ATTACK ORIGIN TRACKER REPORT",
            "",
            "ATTACK ANALYSIS:",
            f"  Total Attacks Detected: {self.analysis.total_attacks}",
            f"  Internal Attacks: {self.analysis.internal_attacks}",
            f"  External Attacks: {self.analysis.external_attacks}",
            ""
        ]

        # Verdict
        if self.analysis.internal_attacks > 0:
            lines.append("⚠️  VERDICT: DEVICE MAY BE COMPROMISED")
            lines.append(f"   {self.analysis.internal_attacks} internal attack(s) detected")
            lines.append(f"   Compromised processes: {len(self.analysis.compromised_processes)}")
            lines.append("")

        if self.analysis.external_attacks > 0:
            lines.append("🌐 EXTERNAL ATTACKS DETECTED")
            lines.append(f"   {self.analysis.external_attacks} attack(s) from outside")
            lines.append(f"   Attack IPs: {len(self.analysis.attack_ips)}")
            lines.append("")

        # Internal fingerprints
        if self.analysis.internal_fingerprints:
            lines.append("INTERNAL ATTACK FINGERPRINTS:")
            for fp_sig in list(self.analysis.internal_fingerprints)[:10]:
                lines.append(f"  - {fp_sig}")
            lines.append("")

        # External IPs
        if self.analysis.attack_ips:
            lines.append("EXTERNAL ATTACK IPs:")
            for ip in list(self.analysis.attack_ips)[:10]:
                lines.append(f"  - {ip}")
            lines.append("")

        # Compromised processes
        if self.analysis.compromised_processes:
            lines.append("COMPROMISED PROCESSES (PIDs):")
            lines.append(f"  {', '.join(str(pid) for pid in sorted(self.analysis.compromised_processes))}")
            lines.append("")

        lines.extend([
            f"Fingerprints saved to: {FINGERPRINT_DB}",
            "",
            "'Inside or outside - we will find you.'",
            "═══════════════════════════════════════════════════════════"
        ])

        return "\n".join(lines)


if __name__ == "__main__":
    print("""
    ═══════════════════════════════════════════════════════════════════
    🎯 ATTACK ORIGIN TRACKER

    Determines if attacks come from WITHIN or OUTSIDE your device.
    Everything leaves a fingerprint. We find it all.

    "Inside or outside - we will find you."
    ═══════════════════════════════════════════════════════════════════
    """)

    tracker = AttackOriginTracker()

    # Analyze all connections
    logging.info("🔍 Analyzing all network connections...")
    fingerprints = tracker.analyze_all_connections()

    logging.info(f"   Found {len(fingerprints)} suspicious connections")

    # Trace each fingerprint
    for fp in fingerprints:
        tracker.trace_attack_source(fp)

    # Save fingerprints
    tracker.save_fingerprints()

    # Generate report
    print("\n" + tracker.report())

    # Detailed fingerprints
    if fingerprints:
        print("\nDETAILED FINGERPRINTS:\n")
        for fp in fingerprints[:20]:  # Show first 20
            print(f"Fingerprint: {fp.signature()}")
            print(f"  Origin: {fp.origin_type}")
            print(f"  Process: {fp.process_name} (PID: {fp.process_pid})")
            if fp.target_ip:
                print(f"  Target: {fp.target_ip}:{fp.target_port}")
            print(f"  Indicators:")
            for indicator in fp.threat_indicators:
                print(f"    - {indicator}")
            print("")
