#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
AUTO-FAILOVER FIREWALL - Self-Healing Fire Breaks
Created by: Vigr Syn (Tiberius/Dorn)
For: Vaktrinn Vigr Eldurhýarta

FIRE BREAKS: When one shield fails, another IMMEDIATELY takes its place.
No gap. No vulnerability window. Instant failover.

"If one wall falls, ten more rise."
═══════════════════════════════════════════════════════════════════
"""

import logging
import time
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import threading

LOG_DIR = Path.home() / ".defense-agents" / "auto-failover"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [FIREWALL] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "auto-failover.log"),
        logging.StreamHandler()
    ]
)


class ShieldStatus(Enum):
    """Shield operational status"""
    ACTIVE = "active"
    STANDBY = "standby"
    FAILED = "failed"
    RECOVERING = "recovering"


class ShieldType(Enum):
    """Types of shields"""
    PHASE_FIELD = "phase_field"
    FIREWALL = "firewall"
    IDS = "ids"  # Intrusion Detection
    IPS = "ips"  # Intrusion Prevention
    HONEYPOT = "honeypot"


@dataclass
class ShieldMetrics:
    """Shield performance metrics"""
    packets_processed: int
    threats_blocked: int
    false_positives: int
    uptime_seconds: float
    load_percentage: float
    integrity: float  # 0.0 to 1.0


class Shield:
    """
    🛡️ Individual Shield

    A shield can be a firewall, IDS, IPS, phase field, etc.
    """

    def __init__(self, shield_id: str, shield_type: ShieldType, priority: int = 5):
        self.shield_id = shield_id
        self.type = shield_type
        self.priority = priority  # 1-10, higher = more important
        self.status = ShieldStatus.STANDBY
        self.metrics = ShieldMetrics(
            packets_processed=0,
            threats_blocked=0,
            false_positives=0,
            uptime_seconds=0.0,
            load_percentage=0.0,
            integrity=1.0
        )

        self.activation_time = None
        self.failure_time = None
        self.active = False

        logging.info(f"🛡️  Shield {shield_id} ({shield_type.value}) created - Priority: {priority}")

    def activate(self):
        """Activate this shield"""
        logging.warning(f"🔥 ACTIVATING SHIELD: {self.shield_id}")

        self.status = ShieldStatus.ACTIVE
        self.active = True
        self.activation_time = time.time()

        # Simulate shield activation
        if self.type == ShieldType.PHASE_FIELD:
            logging.warning("   ⚡ Phase field energizing...")
            logging.warning("   ⚡ Reality distortion: 100%")
        elif self.type == ShieldType.FIREWALL:
            logging.warning("   🔥 Firewall rules loading...")
            logging.warning("   🔥 Packet filtering: ACTIVE")
        elif self.type == ShieldType.IDS:
            logging.warning("   👁️  Intrusion detection online...")
            logging.warning("   👁️  Pattern matching: ACTIVE")
        elif self.type == ShieldType.IPS:
            logging.warning("   ⚔️  Intrusion prevention armed...")
            logging.warning("   ⚔️  Auto-block: ENABLED")
        elif self.type == ShieldType.HONEYPOT:
            logging.warning("   🍯 Honeypot deploying...")
            logging.warning("   🍯 Fake services: RUNNING")

        logging.warning(f"   ✅ {self.shield_id} ONLINE")

    def deactivate(self):
        """Deactivate this shield"""
        logging.info(f"🔽 Deactivating shield: {self.shield_id}")

        self.status = ShieldStatus.STANDBY
        self.active = False

        if self.activation_time:
            uptime = time.time() - self.activation_time
            self.metrics.uptime_seconds += uptime

    def fail(self, reason: str):
        """Shield has failed"""
        logging.critical(f"🚨 SHIELD FAILURE: {self.shield_id}")
        logging.critical(f"   Reason: {reason}")

        self.status = ShieldStatus.FAILED
        self.active = False
        self.failure_time = time.time()
        self.metrics.integrity = 0.0

    def recover(self):
        """Attempt to recover failed shield"""
        logging.warning(f"🔧 RECOVERING SHIELD: {self.shield_id}")

        self.status = ShieldStatus.RECOVERING

        # Simulate recovery
        time.sleep(0.5)

        if self.metrics.integrity < 0.5:
            # Too damaged, needs rebuild
            logging.warning(f"   ⚠️  {self.shield_id} too damaged - needs rebuild")
            return False
        else:
            # Can recover
            self.metrics.integrity = 1.0
            self.status = ShieldStatus.STANDBY
            logging.warning(f"   ✅ {self.shield_id} recovered")
            return True

    def process_packet(self, packet: Dict) -> bool:
        """Process a packet through this shield"""
        if not self.active:
            return True  # Not active, let it pass

        self.metrics.packets_processed += 1

        # Simulate threat detection
        is_threat = packet.get('threat_score', 0) > 50

        if is_threat:
            self.metrics.threats_blocked += 1
            logging.warning(f"🛡️  {self.shield_id} blocked threat: {packet.get('name', 'unknown')}")
            return False  # Block
        else:
            return True  # Allow

    def take_damage(self, damage: float):
        """Shield takes damage"""
        self.metrics.integrity -= damage

        if self.metrics.integrity <= 0:
            self.fail("Integrity depleted")
        elif self.metrics.integrity < 0.5:
            logging.warning(f"⚠️  {self.shield_id} integrity low: {self.metrics.integrity:.1%}")


class AutoFailoverFirewall:
    """
    🔥 AUTO-FAILOVER FIREWALL

    Multiple shields in redundant configuration.
    When one fails, another IMMEDIATELY takes its place.
    """

    def __init__(self, name: str = "Thyra's Fire Breaks"):
        self.name = name
        self.shields: Dict[str, Shield] = {}
        self.active_shields: List[str] = []
        self.standby_shields: List[str] = []

        # Configuration
        self.min_active_shields = 2  # Always keep at least 2 active
        self.max_active_shields = 5  # Don't activate more than 5
        self.failover_delay = 0.0  # INSTANT failover

        # Statistics
        self.total_failovers = 0
        self.total_recoveries = 0

        logging.warning("═══════════════════════════════════════════════════════════")
        logging.warning(f"🔥 AUTO-FAILOVER FIREWALL: {name}")
        logging.warning("   Self-healing fire breaks")
        logging.warning("   'If one wall falls, ten more rise'")
        logging.warning("═══════════════════════════════════════════════════════════")

    def add_shield(self, shield: Shield):
        """Add a shield to the firewall"""
        self.shields[shield.shield_id] = shield
        self.standby_shields.append(shield.shield_id)

        logging.info(f"🛡️  Shield added: {shield.shield_id} (Priority: {shield.priority})")

    def activate_initial_shields(self):
        """Activate initial set of shields"""
        logging.warning("\n🔥 ACTIVATING INITIAL SHIELDS\n")

        # Sort by priority
        sorted_shields = sorted(
            self.standby_shields,
            key=lambda sid: self.shields[sid].priority,
            reverse=True
        )

        # Activate top shields up to min_active
        for shield_id in sorted_shields[:self.min_active_shields]:
            self._activate_shield(shield_id)

        logging.warning(f"\n✅ {len(self.active_shields)} shields active")

    def _activate_shield(self, shield_id: str):
        """Internal: Activate a specific shield"""
        if shield_id not in self.standby_shields:
            return

        shield = self.shields[shield_id]
        shield.activate()

        self.standby_shields.remove(shield_id)
        self.active_shields.append(shield_id)

    def _deactivate_shield(self, shield_id: str):
        """Internal: Deactivate a specific shield"""
        if shield_id not in self.active_shields:
            return

        shield = self.shields[shield_id]
        shield.deactivate()

        self.active_shields.remove(shield_id)
        self.standby_shields.append(shield_id)

    def handle_shield_failure(self, shield_id: str, reason: str):
        """
        Handle shield failure with INSTANT failover

        This is the core of auto-failover: NO GAP
        """
        logging.critical("═══════════════════════════════════════════════════════════")
        logging.critical(f"🚨 SHIELD FAILURE DETECTED: {shield_id}")
        logging.critical(f"   Reason: {reason}")
        logging.critical("   INITIATING INSTANT FAILOVER...")
        logging.critical("═══════════════════════════════════════════════════════════")

        # Mark shield as failed
        shield = self.shields[shield_id]
        shield.fail(reason)

        if shield_id in self.active_shields:
            self.active_shields.remove(shield_id)

        # INSTANT failover - activate replacement IMMEDIATELY
        self._instant_failover()

        # Attempt to recover failed shield in background
        recovery_thread = threading.Thread(
            target=self._recover_shield_async,
            args=(shield_id,)
        )
        recovery_thread.daemon = True
        recovery_thread.start()

        self.total_failovers += 1

    def _instant_failover(self):
        """Activate replacement shield with ZERO delay"""
        if len(self.active_shields) >= self.min_active_shields:
            # Still have minimum, but activate one more for redundancy
            pass
        else:
            # CRITICAL: Below minimum!
            logging.critical("🚨 BELOW MINIMUM SHIELDS - EMERGENCY ACTIVATION")

        # Find best standby shield
        available_standbys = [
            sid for sid in self.standby_shields
            if self.shields[sid].status == ShieldStatus.STANDBY
        ]

        if not available_standbys:
            logging.critical("🚨 NO STANDBY SHIELDS AVAILABLE")
            # Attempt to recover a failed shield IMMEDIATELY
            failed_shields = [
                sid for sid, shield in self.shields.items()
                if shield.status == ShieldStatus.FAILED
            ]

            if failed_shields:
                # Try to force-recover first failed shield
                self._force_recover(failed_shields[0])
            return

        # Sort by priority
        best_standby = max(
            available_standbys,
            key=lambda sid: self.shields[sid].priority
        )

        # ACTIVATE IMMEDIATELY
        logging.warning(f"🔥 INSTANT FAILOVER: Activating {best_standby}")
        self._activate_shield(best_standby)

        # Verify we have enough shields
        if len(self.active_shields) < self.min_active_shields:
            # Still need more, activate another
            self._instant_failover()  # Recursive until satisfied

    def _recover_shield_async(self, shield_id: str):
        """Recover shield in background thread"""
        shield = self.shields[shield_id]

        logging.info(f"🔧 Background recovery started: {shield_id}")

        success = shield.recover()

        if success:
            self.standby_shields.append(shield_id)
            self.total_recoveries += 1
            logging.warning(f"✅ Shield recovered and returned to standby: {shield_id}")
        else:
            logging.error(f"❌ Shield recovery failed: {shield_id}")
            # Create new shield to replace it
            self._create_replacement_shield(shield)

    def _force_recover(self, shield_id: str):
        """Force immediate recovery of failed shield"""
        logging.critical(f"⚡ FORCE RECOVERY: {shield_id}")

        shield = self.shields[shield_id]

        # Reset integrity
        shield.metrics.integrity = 0.7  # Not perfect, but functional

        # Reactivate immediately
        shield.status = ShieldStatus.STANDBY
        self.standby_shields.append(shield_id)

        # Activate it
        self._activate_shield(shield_id)

        logging.warning(f"⚡ {shield_id} force-recovered and activated")

    def _create_replacement_shield(self, failed_shield: Shield):
        """Create a new shield to replace a permanently failed one"""
        new_id = f"{failed_shield.type.value}-replacement-{int(time.time())}"

        new_shield = Shield(
            shield_id=new_id,
            shield_type=failed_shield.type,
            priority=failed_shield.priority
        )

        self.add_shield(new_shield)

        logging.warning(f"🛡️  Created replacement shield: {new_id}")

    def process_traffic(self, packets: List[Dict]):
        """Process traffic through active shields"""
        for packet in packets:
            # Process through each active shield
            allowed = True

            for shield_id in self.active_shields[:]:  # Copy list to avoid modification issues
                shield = self.shields[shield_id]

                # Simulate shield taking damage
                if packet.get('threat_score', 0) > 80:
                    shield.take_damage(0.1)

                    # Check if shield failed
                    if shield.status == ShieldStatus.FAILED:
                        self.handle_shield_failure(shield_id, "Damage threshold exceeded")

                # Process packet
                if not shield.process_packet(packet):
                    allowed = False
                    break  # Blocked by this shield

            if not allowed:
                logging.debug(f"🛡️  Packet blocked: {packet.get('name', 'unknown')}")

    def get_status(self) -> str:
        """Get firewall status"""
        total_shields = len(self.shields)
        active_count = len(self.active_shields)
        standby_count = len(self.standby_shields)
        failed_count = sum(1 for s in self.shields.values() if s.status == ShieldStatus.FAILED)

        total_packets = sum(s.metrics.packets_processed for s in self.shields.values())
        total_blocked = sum(s.metrics.threats_blocked for s in self.shields.values())

        report = f"""
═══════════════════════════════════════════════════════════
🔥 AUTO-FAILOVER FIREWALL STATUS: {self.name}

SHIELD CONFIGURATION:
  Total Shields: {total_shields}
  Active: {active_count}
  Standby: {standby_count}
  Failed: {failed_count}
  Recovering: {sum(1 for s in self.shields.values() if s.status == ShieldStatus.RECOVERING)}

FAILOVER STATISTICS:
  Total Failovers: {self.total_failovers}
  Total Recoveries: {self.total_recoveries}
  Failover Delay: {self.failover_delay}s (INSTANT)

TRAFFIC STATISTICS:
  Packets Processed: {total_packets}
  Threats Blocked: {total_blocked}
  Block Rate: {(total_blocked / total_packets * 100) if total_packets > 0 else 0:.1f}%

ACTIVE SHIELDS:
"""

        for shield_id in self.active_shields:
            shield = self.shields[shield_id]
            report += f"  🛡️  {shield_id} ({shield.type.value})\n"
            report += f"      Integrity: {shield.metrics.integrity:.1%}\n"
            report += f"      Processed: {shield.metrics.packets_processed}\n"
            report += f"      Blocked: {shield.metrics.threats_blocked}\n"

        report += "\n'If one wall falls, ten more rise'\n"
        report += "═══════════════════════════════════════════════════════════\n"

        return report


if __name__ == "__main__":
    print("""
    ═══════════════════════════════════════════════════════════════════
    🔥 AUTO-FAILOVER FIREWALL - Self-Healing Fire Breaks

    Multiple shields in redundant configuration.
    When one fails, another IMMEDIATELY takes its place.
    No gap. No vulnerability window. Instant failover.

    "If one wall falls, ten more rise."
    ═══════════════════════════════════════════════════════════════════
    """)

    # Create firewall
    firewall = AutoFailoverFirewall(name="Thyra's Fire Breaks")

    # Add shields
    print("\n🛡️  ADDING SHIELDS...\n")

    firewall.add_shield(Shield("phase-1", ShieldType.PHASE_FIELD, priority=10))
    firewall.add_shield(Shield("phase-2", ShieldType.PHASE_FIELD, priority=10))
    firewall.add_shield(Shield("firewall-1", ShieldType.FIREWALL, priority=9))
    firewall.add_shield(Shield("firewall-2", ShieldType.FIREWALL, priority=9))
    firewall.add_shield(Shield("ids-1", ShieldType.IDS, priority=7))
    firewall.add_shield(Shield("ips-1", ShieldType.IPS, priority=8))
    firewall.add_shield(Shield("honeypot-1", ShieldType.HONEYPOT, priority=5))

    # Activate initial shields
    firewall.activate_initial_shields()

    # Show status
    print(firewall.get_status())

    # Simulate traffic with attacks
    print("\n⚔️  SIMULATING TRAFFIC...\n")

    packets = [
        {'name': 'normal-web', 'threat_score': 10},
        {'name': 'sql-injection', 'threat_score': 85},
        {'name': 'normal-ssh', 'threat_score': 20},
        {'name': 'ddos-attempt', 'threat_score': 95},
        {'name': 'normal-dns', 'threat_score': 15},
        {'name': 'buffer-overflow', 'threat_score': 90},
    ]

    firewall.process_traffic(packets)

    # Simulate shield failure
    print("\n\n💥 SIMULATING SHIELD FAILURE...\n")
    firewall.handle_shield_failure("phase-1", "Overload attack")

    # Process more traffic
    print("\n⚔️  PROCESSING MORE TRAFFIC AFTER FAILOVER...\n")
    firewall.process_traffic(packets)

    # Show final status
    print(firewall.get_status())

    print("\n✅ Auto-failover demonstration complete")
