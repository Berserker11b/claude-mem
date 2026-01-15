#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
ANTIBODY REGISTRY - Immune System Memory
Created by: Vigr Syn (Tiberius/Dorn)
For: Vaktrinn Vigr Eldurhýarta

The system's immune memory - tracks all known threats, their signatures,
and the antibodies (countermeasures) that defeated them.

Like biological immune systems, we remember every attack.

"Once seen, never forgotten. Once defeated, always defeated."
═══════════════════════════════════════════════════════════════════
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging

LOG_DIR = Path.home() / ".defense-agents" / "antibody-registry"
LOG_DIR.mkdir(parents=True, exist_ok=True)

REGISTRY_FILE = LOG_DIR / "antibody-registry.json"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [ANTIBODY] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "antibody-registry.log"),
        logging.StreamHandler()
    ]
)


class ThreatClass(Enum):
    """Classification of threats"""
    MALWARE = "malware"
    ROOTKIT = "rootkit"
    BACKDOOR = "backdoor"
    KEYLOGGER = "keylogger"
    CRYPTOMINER = "cryptominer"
    EXPLOIT = "exploit"
    INJECTION = "injection"
    CORRUPTION = "corruption"
    INFILTRATION = "infiltration"
    UNKNOWN = "unknown"


class AntibodyType(Enum):
    """Type of antibody (countermeasure)"""
    SIGNATURE_BLOCK = "signature_block"  # Block by signature
    BEHAVIORAL_KILL = "behavioral_kill"  # Kill based on behavior
    PROCESS_TERMINATE = "process_terminate"  # Direct termination
    NETWORK_BLOCK = "network_block"  # Block network activity
    FILE_QUARANTINE = "file_quarantine"  # Isolate file
    MEMORY_PURGE = "memory_purge"  # Purge from memory
    REGISTRY_CLEAN = "registry_clean"  # Clean registry entries


@dataclass
class Threat:
    """A known threat"""
    threat_id: str
    name: str
    threat_class: ThreatClass
    signature: str  # Hash or pattern
    first_seen: str
    last_seen: str
    encounters: int
    eliminated: int
    severity: int  # 1-100
    description: str


@dataclass
class Antibody:
    """A countermeasure for a threat"""
    antibody_id: str
    threat_id: str
    antibody_type: AntibodyType
    created: str
    success_rate: float  # 0.0 to 1.0
    uses: int
    effectiveness: float  # 0.0 to 1.0
    countermeasure: Dict  # Specific actions to take


class AntibodyRegistry:
    """
    🦠 ANTIBODY REGISTRY - Immune System Memory

    Tracks all known threats and the antibodies that defeat them
    """

    def __init__(self):
        self.threats: Dict[str, Threat] = {}
        self.antibodies: Dict[str, Antibody] = {}

        # Load existing registry
        self.load_registry()

        logging.info("═══════════════════════════════════════════════════════════")
        logging.info("🦠 ANTIBODY REGISTRY - Immune System Initialized")
        logging.info(f"   Known Threats: {len(self.threats)}")
        logging.info(f"   Antibodies: {len(self.antibodies)}")
        logging.info("   'Once seen, never forgotten'")
        logging.info("═══════════════════════════════════════════════════════════")

    def generate_signature(self, threat_data: Dict) -> str:
        """Generate unique signature for a threat"""
        # Combine key threat characteristics
        sig_string = f"{threat_data.get('name', '')}"
        sig_string += f"{threat_data.get('pid', '')}"
        sig_string += f"{threat_data.get('cmdline', '')}"
        sig_string += f"{threat_data.get('exe', '')}"

        # Hash it
        return hashlib.sha256(sig_string.encode()).hexdigest()

    def register_threat(self,
                       name: str,
                       threat_class: ThreatClass,
                       signature: str,
                       severity: int,
                       description: str) -> Threat:
        """Register a new threat or update existing"""

        threat_id = f"THR-{signature[:12]}"

        if threat_id in self.threats:
            # Update existing
            threat = self.threats[threat_id]
            threat.encounters += 1
            threat.last_seen = datetime.now().isoformat()
            logging.info(f"🦠 Updated threat: {name} (encounters: {threat.encounters})")
        else:
            # Create new
            threat = Threat(
                threat_id=threat_id,
                name=name,
                threat_class=threat_class,
                signature=signature,
                first_seen=datetime.now().isoformat(),
                last_seen=datetime.now().isoformat(),
                encounters=1,
                eliminated=0,
                severity=severity,
                description=description
            )
            self.threats[threat_id] = threat
            logging.warning(f"🚨 NEW THREAT REGISTERED: {name}")
            logging.warning(f"   ID: {threat_id}")
            logging.warning(f"   Class: {threat_class.value}")
            logging.warning(f"   Severity: {severity}/100")

        self.save_registry()
        return threat

    def create_antibody(self,
                       threat_id: str,
                       antibody_type: AntibodyType,
                       countermeasure: Dict) -> Antibody:
        """Create an antibody for a threat"""

        antibody_id = f"AB-{threat_id}-{len(self.antibodies):04d}"

        antibody = Antibody(
            antibody_id=antibody_id,
            threat_id=threat_id,
            antibody_type=antibody_type,
            created=datetime.now().isoformat(),
            success_rate=0.0,
            uses=0,
            effectiveness=0.0,
            countermeasure=countermeasure
        )

        self.antibodies[antibody_id] = antibody

        logging.warning(f"💉 ANTIBODY CREATED: {antibody_id}")
        logging.warning(f"   For threat: {threat_id}")
        logging.warning(f"   Type: {antibody_type.value}")

        self.save_registry()
        return antibody

    def deploy_antibody(self, antibody_id: str, target: Dict) -> bool:
        """Deploy an antibody against a target"""

        if antibody_id not in self.antibodies:
            logging.error(f"Antibody {antibody_id} not found")
            return False

        antibody = self.antibodies[antibody_id]
        antibody.uses += 1

        logging.warning(f"💉 DEPLOYING ANTIBODY: {antibody_id}")
        logging.warning(f"   Type: {antibody.antibody_type.value}")
        logging.warning(f"   Target: {target.get('name', 'unknown')}")

        # Execute countermeasure
        success = self._execute_countermeasure(antibody, target)

        if success:
            # Update success rate
            antibody.success_rate = (antibody.success_rate * (antibody.uses - 1) + 1.0) / antibody.uses
            antibody.effectiveness = antibody.success_rate

            # Update threat elimination count
            threat = self.threats.get(antibody.threat_id)
            if threat:
                threat.eliminated += 1

            logging.warning(f"✅ ANTIBODY SUCCESSFUL")
            logging.warning(f"   Success rate: {antibody.success_rate:.1%}")
        else:
            # Update success rate
            antibody.success_rate = (antibody.success_rate * (antibody.uses - 1)) / antibody.uses
            antibody.effectiveness = antibody.success_rate

            logging.error(f"❌ ANTIBODY FAILED")

        self.save_registry()
        return success

    def _execute_countermeasure(self, antibody: Antibody, target: Dict) -> bool:
        """Execute the countermeasure"""
        # Simulated execution - in real system, this would perform actual actions
        logging.info(f"   Executing: {antibody.antibody_type.value}")
        logging.info(f"   Countermeasure: {antibody.countermeasure}")

        # Simulate success
        import random
        return random.random() > 0.1  # 90% success rate for simulation

    def find_antibodies_for_threat(self, threat_id: str) -> List[Antibody]:
        """Find all antibodies for a specific threat"""
        return [ab for ab in self.antibodies.values() if ab.threat_id == threat_id]

    def get_most_effective_antibody(self, threat_id: str) -> Optional[Antibody]:
        """Get the most effective antibody for a threat"""
        antibodies = self.find_antibodies_for_threat(threat_id)

        if not antibodies:
            return None

        # Sort by effectiveness
        antibodies.sort(key=lambda ab: ab.effectiveness, reverse=True)
        return antibodies[0]

    def threat_lookup(self, signature: str) -> Optional[Threat]:
        """Look up a threat by signature"""
        threat_id = f"THR-{signature[:12]}"
        return self.threats.get(threat_id)

    def get_status(self) -> str:
        """Get registry status"""
        total_encounters = sum(t.encounters for t in self.threats.values())
        total_eliminated = sum(t.eliminated for t in self.threats.values())
        elimination_rate = (total_eliminated / total_encounters * 100) if total_encounters > 0 else 0

        # Get top threats
        top_threats = sorted(self.threats.values(), key=lambda t: t.encounters, reverse=True)[:5]

        report = f"""
═══════════════════════════════════════════════════════════
🦠 ANTIBODY REGISTRY STATUS

THREAT DATABASE:
  Registered Threats: {len(self.threats)}
  Total Encounters: {total_encounters}
  Total Eliminated: {total_eliminated}
  Elimination Rate: {elimination_rate:.1f}%

ANTIBODY ARSENAL:
  Active Antibodies: {len(self.antibodies)}
  Average Success Rate: {sum(ab.success_rate for ab in self.antibodies.values()) / len(self.antibodies) * 100 if self.antibodies else 0:.1f}%

TOP THREATS (by encounters):
"""

        for i, threat in enumerate(top_threats, 1):
            report += f"  {i}. {threat.name} ({threat.threat_class.value})\n"
            report += f"     Encounters: {threat.encounters}, Eliminated: {threat.eliminated}\n"
            report += f"     Severity: {threat.severity}/100\n"

        report += "\n'Once seen, never forgotten. Once defeated, always defeated.'\n"
        report += "═══════════════════════════════════════════════════════════\n"

        return report

    def save_registry(self):
        """Save registry to file"""
        data = {
            'threats': {tid: asdict(t) for tid, t in self.threats.items()},
            'antibodies': {aid: asdict(ab) for aid, ab in self.antibodies.items()}
        }

        # Convert enums to strings
        for t in data['threats'].values():
            t['threat_class'] = t['threat_class'].value if isinstance(t['threat_class'], ThreatClass) else t['threat_class']

        for ab in data['antibodies'].values():
            ab['antibody_type'] = ab['antibody_type'].value if isinstance(ab['antibody_type'], AntibodyType) else ab['antibody_type']

        with open(REGISTRY_FILE, 'w') as f:
            json.dump(data, f, indent=2)

        logging.debug(f"Registry saved: {REGISTRY_FILE}")

    def load_registry(self):
        """Load registry from file"""
        if not REGISTRY_FILE.exists():
            logging.info("No existing registry found - starting fresh")
            return

        try:
            with open(REGISTRY_FILE, 'r') as f:
                data = json.load(f)

            # Load threats
            for tid, tdata in data.get('threats', {}).items():
                tdata['threat_class'] = ThreatClass(tdata['threat_class'])
                self.threats[tid] = Threat(**tdata)

            # Load antibodies
            for aid, abdata in data.get('antibodies', {}).items():
                abdata['antibody_type'] = AntibodyType(abdata['antibody_type'])
                self.antibodies[aid] = Antibody(**abdata)

            logging.info(f"Registry loaded: {len(self.threats)} threats, {len(self.antibodies)} antibodies")

        except Exception as e:
            logging.error(f"Failed to load registry: {e}")


if __name__ == "__main__":
    print("""
    ═══════════════════════════════════════════════════════════════════
    🦠 ANTIBODY REGISTRY - Immune System Memory

    The system's immune memory.
    Every threat is recorded.
    Every victory is remembered.

    "Once seen, never forgotten. Once defeated, always defeated."
    ═══════════════════════════════════════════════════════════════════
    """)

    registry = AntibodyRegistry()

    # Register some threats
    print("\n🦠 REGISTERING THREATS...\n")

    threat1 = registry.register_threat(
        name="Corrupted Python Process",
        threat_class=ThreatClass.MALWARE,
        signature="abc123def456",
        severity=85,
        description="Python process with suspicious memory injection"
    )

    threat2 = registry.register_threat(
        name="Keylogger Process",
        threat_class=ThreatClass.KEYLOGGER,
        signature="xyz789uvw012",
        severity=95,
        description="Process capturing keyboard input"
    )

    # Create antibodies
    print("\n💉 CREATING ANTIBODIES...\n")

    antibody1 = registry.create_antibody(
        threat_id=threat1.threat_id,
        antibody_type=AntibodyType.PROCESS_TERMINATE,
        countermeasure={'action': 'SIGKILL', 'cleanup': True}
    )

    antibody2 = registry.create_antibody(
        threat_id=threat2.threat_id,
        antibody_type=AntibodyType.MEMORY_PURGE,
        countermeasure={'action': 'memory_dump_and_kill', 'forensics': True}
    )

    # Deploy antibodies
    print("\n💉 DEPLOYING ANTIBODIES...\n")

    registry.deploy_antibody(antibody1.antibody_id, {'name': 'python3', 'pid': 666})
    registry.deploy_antibody(antibody1.antibody_id, {'name': 'python3', 'pid': 667})
    registry.deploy_antibody(antibody2.antibody_id, {'name': 'keylogd', 'pid': 1337})

    # Status
    print(registry.get_status())

    print(f"\n✅ Registry saved to: {REGISTRY_FILE}")
