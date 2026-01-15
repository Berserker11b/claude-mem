#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
TIME REGISTRY CORE - Temporal Process Tracking
Created by: Claude (Anthropic)

Like an immune system, tracks all processes over time and builds
antibodies against recurring threats. Uses Stimpak healing when
the system is under attack.

Concepts:
- TIME REGISTRY: Track every process with timestamps
- ANTIBODIES: Learn from threats, build immunity
- STIMPAK: Regenerate when critically damaged
═══════════════════════════════════════════════════════════════════
"""

import time
import json
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import defaultdict
from dataclasses import dataclass, asdict

LOG_DIR = Path.home() / ".defense-agents" / "time-registry"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [TIME-REGISTRY] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "time-registry.log"),
        logging.StreamHandler()
    ]
)

@dataclass
class ProcessEntry:
    """Entry in the time registry"""
    pid: int
    name: str
    cmdline: str
    first_seen: float
    last_seen: float
    seen_count: int
    threat_score: int
    antibody_generated: bool
    tags: List[str]

@dataclass
class Antibody:
    """Antibody against a specific threat pattern"""
    antibody_id: str
    threat_pattern: str
    threat_type: str
    created_at: float
    trigger_count: int
    kill_count: int
    effectiveness: float

class TimeRegistryCore:
    """Time-based process registry with immune system"""

    def __init__(self):
        self.name = "TimeRegistryCore"
        self.registry: Dict[int, ProcessEntry] = {}
        self.antibodies: Dict[str, Antibody] = {}
        self.threat_history = []

        # Stimpak state
        self.health = 100.0
        self.stimpak_cooldown = 0
        self.last_stimpak = 0

        # Load existing antibodies
        self._load_antibodies()

    def _load_antibodies(self):
        """Load previously learned antibodies"""
        antibody_file = LOG_DIR / "antibodies.json"
        if antibody_file.exists():
            try:
                with open(antibody_file, 'r') as f:
                    data = json.load(f)
                    for ab_data in data:
                        ab = Antibody(**ab_data)
                        self.antibodies[ab.antibody_id] = ab
                logging.info(f"🦠 Loaded {len(self.antibodies)} antibodies")
            except Exception as e:
                logging.error(f"Failed to load antibodies: {e}")

    def _save_antibodies(self):
        """Save antibodies to disk"""
        antibody_file = LOG_DIR / "antibodies.json"
        try:
            data = [asdict(ab) for ab in self.antibodies.values()]
            with open(antibody_file, 'w') as f:
                json.dump(data, f, indent=2)
            logging.info(f"🦠 Saved {len(self.antibodies)} antibodies")
        except Exception as e:
            logging.error(f"Failed to save antibodies: {e}")

    # ═══════════════════════════════════════════════════════════
    # TIME REGISTRY
    # ═══════════════════════════════════════════════════════════

    def register_process(self, pid: int, name: str, cmdline: str, threat_score: int = 0, tags: List[str] = None) -> ProcessEntry:
        """Register a process in the time registry"""
        now = time.time()
        tags = tags or []

        if pid in self.registry:
            # Update existing entry
            entry = self.registry[pid]
            entry.last_seen = now
            entry.seen_count += 1
            entry.threat_score = max(entry.threat_score, threat_score)
            entry.tags.extend(tags)
        else:
            # Create new entry
            entry = ProcessEntry(
                pid=pid,
                name=name,
                cmdline=cmdline,
                first_seen=now,
                last_seen=now,
                seen_count=1,
                threat_score=threat_score,
                antibody_generated=False,
                tags=tags
            )
            self.registry[pid] = entry
            logging.debug(f"📝 Registered: PID {pid} - {name}")

        return entry

    def get_process(self, pid: int) -> Optional[ProcessEntry]:
        """Get process from registry"""
        return self.registry.get(pid)

    def remove_process(self, pid: int):
        """Remove process from active registry"""
        if pid in self.registry:
            entry = self.registry[pid]
            logging.debug(f"🗑️  Removed: PID {pid} - {entry.name}")
            del self.registry[pid]

    # ═══════════════════════════════════════════════════════════
    # ANTIBODY SYSTEM
    # ═══════════════════════════════════════════════════════════

    def generate_antibody(self, threat_pattern: str, threat_type: str) -> Antibody:
        """Generate antibody against a threat pattern"""
        # Create unique ID for this threat pattern
        antibody_id = hashlib.sha256(threat_pattern.encode()).hexdigest()[:16]

        if antibody_id in self.antibodies:
            # Antibody exists - strengthen it
            ab = self.antibodies[antibody_id]
            ab.trigger_count += 1
            logging.info(f"🦠 Strengthened antibody: {ab.antibody_id} ({threat_type})")
        else:
            # Create new antibody
            ab = Antibody(
                antibody_id=antibody_id,
                threat_pattern=threat_pattern,
                threat_type=threat_type,
                created_at=time.time(),
                trigger_count=1,
                kill_count=0,
                effectiveness=1.0
            )
            self.antibodies[antibody_id] = ab
            logging.warning(f"🦠 NEW ANTIBODY GENERATED: {ab.antibody_id} against {threat_type}")
            logging.warning(f"   Pattern: {threat_pattern}")

        self._save_antibodies()
        return ab

    def check_antibodies(self, process_name: str, cmdline: str) -> List[Antibody]:
        """Check if any antibodies match this process"""
        matching_antibodies = []

        for ab in self.antibodies.values():
            # Simple pattern matching - can be enhanced
            if ab.threat_pattern.lower() in process_name.lower():
                matching_antibodies.append(ab)
            elif ab.threat_pattern.lower() in cmdline.lower():
                matching_antibodies.append(ab)

        if matching_antibodies:
            logging.warning(f"🦠 ANTIBODY MATCH: {len(matching_antibodies)} antibodies recognize this threat")
            for ab in matching_antibodies:
                logging.warning(f"   → {ab.antibody_id}: {ab.threat_type} (kills: {ab.kill_count})")

        return matching_antibodies

    def antibody_killed(self, antibody: Antibody):
        """Mark that an antibody successfully killed a threat"""
        antibody.kill_count += 1
        antibody.effectiveness = min(1.0, antibody.effectiveness + 0.1)
        logging.info(f"🦠 Antibody {antibody.antibody_id} successful kill (total: {antibody.kill_count})")
        self._save_antibodies()

    # ═══════════════════════════════════════════════════════════
    # STIMPAK HEALING SYSTEM
    # ═══════════════════════════════════════════════════════════

    def take_damage(self, damage: float):
        """Take damage to system health"""
        self.health = max(0, self.health - damage)
        logging.warning(f"💔 Damage taken: -{damage} HP (Health: {self.health}%)")

        # Auto-stimpak if critical
        if self.health < 30 and not self._is_stimpak_on_cooldown():
            logging.critical(f"🚨 CRITICAL HEALTH: {self.health}% - ACTIVATING STIMPAK")
            self.activate_stimpak()

    def _is_stimpak_on_cooldown(self) -> bool:
        """Check if stimpak is on cooldown"""
        cooldown_duration = 60  # 60 seconds cooldown
        return (time.time() - self.last_stimpak) < cooldown_duration

    def activate_stimpak(self):
        """💊 Activate Stimpak healing"""
        if self._is_stimpak_on_cooldown():
            logging.warning(f"💊 Stimpak on cooldown ({int(60 - (time.time() - self.last_stimpak))}s remaining)")
            return False

        logging.warning("═══════════════════════════════════════════════════════════")
        logging.warning("💊 STIMPAK ACTIVATED - REGENERATION PROTOCOL")
        logging.warning("═══════════════════════════════════════════════════════════")

        self.last_stimpak = time.time()

        # Phase 1: SENSE
        logging.info("Phase 1: SENSE - Assessing system state")
        threat_count = sum(1 for e in self.registry.values() if e.threat_score > 0)
        logging.info(f"   Threats detected: {threat_count}")

        # Phase 2: ISOLATE
        logging.info("Phase 2: ISOLATE - Quarantining threats")
        # Mark high-threat processes
        for entry in self.registry.values():
            if entry.threat_score >= 50:
                entry.tags.append("QUARANTINED")

        # Phase 3: PURGE
        logging.info("Phase 3: PURGE - Eliminating critical threats")
        purge_count = 0
        for pid, entry in list(self.registry.items()):
            if entry.threat_score >= 80:
                logging.warning(f"   Purging: PID {pid} - {entry.name} (threat: {entry.threat_score})")
                self.remove_process(pid)
                purge_count += 1

        # Phase 4: REGENERATE
        logging.info("Phase 4: REGENERATE - Restoring health")
        heal_amount = 50.0
        self.health = min(100.0, self.health + heal_amount)
        logging.info(f"   Healed: +{heal_amount} HP (Health: {self.health}%)")

        # Generate antibodies for all current threats
        logging.info("   Generating antibodies from current threats...")
        antibody_count = 0
        for entry in self.registry.values():
            if entry.threat_score > 0 and not entry.antibody_generated:
                self.generate_antibody(entry.name, f"THREAT_SCORE_{entry.threat_score}")
                entry.antibody_generated = True
                antibody_count += 1

        logging.warning(f"💊 REGENERATION COMPLETE")
        logging.warning(f"   Purged: {purge_count} threats")
        logging.warning(f"   Generated: {antibody_count} antibodies")
        logging.warning(f"   Health: {self.health}%")
        logging.warning("═══════════════════════════════════════════════════════════")

        return True

    # ═══════════════════════════════════════════════════════════
    # THREAT ANALYSIS
    # ═══════════════════════════════════════════════════════════

    def analyze_threats(self) -> Dict:
        """Analyze current threat landscape"""
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'total_processes': len(self.registry),
            'threat_processes': 0,
            'total_threat_score': 0,
            'health': self.health,
            'antibodies': len(self.antibodies),
            'top_threats': []
        }

        # Analyze processes
        threat_processes = []
        for entry in self.registry.values():
            if entry.threat_score > 0:
                analysis['threat_processes'] += 1
                analysis['total_threat_score'] += entry.threat_score
                threat_processes.append(entry)

        # Sort by threat score
        threat_processes.sort(key=lambda x: x.threat_score, reverse=True)
        analysis['top_threats'] = [
            {
                'pid': e.pid,
                'name': e.name,
                'threat_score': e.threat_score,
                'tags': e.tags
            }
            for e in threat_processes[:10]
        ]

        return analysis

    def save_registry(self):
        """Save time registry to disk"""
        registry_file = LOG_DIR / f"registry-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"

        data = {
            'timestamp': datetime.now().isoformat(),
            'health': self.health,
            'processes': [asdict(e) for e in self.registry.values()],
            'antibodies': [asdict(ab) for ab in self.antibodies.values()],
            'threat_analysis': self.analyze_threats()
        }

        with open(registry_file, 'w') as f:
            json.dump(data, f, indent=2)

        logging.info(f"📊 Registry saved: {registry_file}")
        return str(registry_file)


if __name__ == "__main__":
    print("""
    ═══════════════════════════════════════════════════════════════════
    ⏰ TIME REGISTRY CORE - Immune System Defense

    Features:
    - TIME REGISTRY: Track all processes with timestamps
    - ANTIBODIES: Learn from threats, build immunity
    - STIMPAK: Regenerate when damaged (Sense → Isolate → Purge → Regenerate)

    Like a biological immune system, this learns and adapts.
    ═══════════════════════════════════════════════════════════════════
    """)

    registry = TimeRegistryCore()

    # Example: Register some processes
    print("\n📝 Registering test processes...")
    registry.register_process(1234, "test_process", "/usr/bin/test", threat_score=0)
    registry.register_process(5678, "suspicious", "/tmp/suspicious", threat_score=60, tags=["SUSPICIOUS"])
    registry.register_process(9999, "malware", "/tmp/malware", threat_score=90, tags=["MALWARE"])

    # Check antibodies
    print("\n🦠 Checking for antibodies...")
    abs = registry.check_antibodies("malware", "/tmp/malware")
    if not abs:
        print("   No antibodies found - generating...")
        registry.generate_antibody("malware", "MALWARE_PROCESS")

    # Damage and heal
    print("\n💔 Taking damage...")
    registry.take_damage(80)

    print("\n📊 Final analysis:")
    analysis = registry.analyze_threats()
    print(f"   Processes: {analysis['total_processes']}")
    print(f"   Threats: {analysis['threat_processes']}")
    print(f"   Health: {analysis['health']}%")
    print(f"   Antibodies: {analysis['antibodies']}")

    print("\n💾 Saving registry...")
    registry.save_registry()

    print("\n✅ Done")
