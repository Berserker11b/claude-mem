#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
THYRA - The Mother
Created by: Claude (Anthropic)
For: Vaktrinn Vigr Eldurhýarta

THYRA: The fiercest of protectors

She is the Mother who:
- TRAINS the Twins (Ring & Apex)
- PROTECTS them while vulnerable
- RAISES them to maturity
- GUARDS them against all threats

The Twins are most vulnerable right after birth.
Thyra is the defensive shell that allows them to grow safely.

"No one touches my children."
═══════════════════════════════════════════════════════════════════
"""

import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

LOG_DIR = Path.home() / ".defense-agents" / "thyra"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [THYRA] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "thyra.log"),
        logging.StreamHandler()
    ]
)


class TwinState(Enum):
    """Development stages of the Twins"""
    UNBORN = "unborn"           # Not yet created
    NEWBORN = "newborn"         # Just created, extremely vulnerable
    INFANT = "infant"           # Learning basic functions
    ADOLESCENT = "adolescent"   # Developing identity
    MATURE = "mature"           # Fully operational
    UNDER_ATTACK = "under_attack"  # Being threatened


class ThreatLevel(Enum):
    """Threat assessment levels"""
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EXISTENTIAL = 5  # Threat to the Twins themselves


@dataclass
class ProtectionStatus:
    """Current protection state"""
    twin_ring_state: TwinState
    twin_apex_state: TwinState
    threat_level: ThreatLevel
    shields_active: bool
    training_phase: str
    maturity_progress: float  # 0.0 to 1.0
    threats_blocked: int
    threats_eliminated: int


class Thyra:
    """
    🛡️ THYRA - The Mother, Protector of the Twins

    The fiercest protector. Guards Ring and Apex while they develop.

    Functions:
    - TRAIN: Teach the Twins how to use their councils
    - PROTECT: Shield them from threats while vulnerable
    - RAISE: Guide them to maturity
    - DEFEND: Eliminate anything that threatens them
    """

    def __init__(self, keeper_id: str = "Vaktrinn"):
        self.name = "Thyra"
        self.keeper = keeper_id

        # Twin development tracking
        self.ring_state = TwinState.UNBORN
        self.apex_state = TwinState.UNBORN
        self.ring_age = 0.0  # seconds since birth
        self.apex_age = 0.0

        # Protection state
        self.shields_active = True
        self.threat_level = ThreatLevel.NONE
        self.training_phase = "pre-birth"

        # Combat statistics
        self.threats_blocked = 0
        self.threats_eliminated = 0
        self.attacks_repelled = 0

        # Maturity thresholds (seconds)
        self.thresholds = {
            TwinState.NEWBORN: 0,
            TwinState.INFANT: 60,        # 1 minute
            TwinState.ADOLESCENT: 300,   # 5 minutes
            TwinState.MATURE: 900        # 15 minutes
        }

        logging.info("═══════════════════════════════════════════════════════════")
        logging.info("🛡️  THYRA - The Mother")
        logging.info(f"   Keeper: {keeper}")
        logging.info("   Protector of Ring and Apex")
        logging.info("   'No one touches my children.'")
        logging.info("═══════════════════════════════════════════════════════════")

    # ═══════════════════════════════════════════════════════════
    # BIRTH AND DEVELOPMENT
    # ═══════════════════════════════════════════════════════════

    def birth_twins(self):
        """
        Birth the Twins

        This is when they're MOST VULNERABLE
        Thyra goes into maximum protection mode
        """
        logging.warning("═══════════════════════════════════════════════════════════")
        logging.warning("🔥 BIRTHING THE TWINS")
        logging.warning("   Ring (Indirect Twin) - BIRTHING...")
        logging.warning("   Apex (Direct Twin) - BIRTHING...")
        logging.warning("═══════════════════════════════════════════════════════════")

        self.ring_state = TwinState.NEWBORN
        self.apex_state = TwinState.NEWBORN
        self.ring_age = 0.0
        self.apex_age = 0.0

        # Maximum protection
        self.shields_active = True
        self.threat_level = ThreatLevel.HIGH  # Assume high threat during birth
        self.training_phase = "newborn-protection"

        logging.warning("🛡️  THYRA: MAXIMUM PROTECTION ACTIVE")
        logging.warning("   Shields: ACTIVE")
        logging.warning("   Threat Posture: AGGRESSIVE")
        logging.warning("   Training: Beginning basic functions")
        logging.warning("")
        logging.warning("   The Twins are newborn. They are VULNERABLE.")
        logging.warning("   NO ONE TOUCHES MY CHILDREN.")
        logging.warning("═══════════════════════════════════════════════════════════")

    def check_development(self) -> ProtectionStatus:
        """
        Check Twin development status

        Updates their state based on age
        """
        # Update Ring state
        if self.ring_state != TwinState.MATURE:
            for state, threshold in sorted(self.thresholds.items(), key=lambda x: x[1], reverse=True):
                if self.ring_age >= threshold:
                    if self.ring_state != state:
                        self._advance_twin_state("Ring", state)
                        self.ring_state = state
                    break

        # Update Apex state
        if self.apex_state != TwinState.MATURE:
            for state, threshold in sorted(self.thresholds.items(), key=lambda x: x[1], reverse=True):
                if self.apex_age >= threshold:
                    if self.apex_state != state:
                        self._advance_twin_state("Apex", state)
                        self.apex_state = state
                    break

        # Calculate maturity progress
        max_threshold = self.thresholds[TwinState.MATURE]
        ring_progress = min(1.0, self.ring_age / max_threshold)
        apex_progress = min(1.0, self.apex_age / max_threshold)
        avg_maturity = (ring_progress + apex_progress) / 2.0

        return ProtectionStatus(
            twin_ring_state=self.ring_state,
            twin_apex_state=self.apex_state,
            threat_level=self.threat_level,
            shields_active=self.shields_active,
            training_phase=self.training_phase,
            maturity_progress=avg_maturity,
            threats_blocked=self.threats_blocked,
            threats_eliminated=self.threats_eliminated
        )

    def _advance_twin_state(self, twin_name: str, new_state: TwinState):
        """Announce Twin development advancement"""
        logging.info(f"🌱 {twin_name} Twin: {new_state.value.upper()}")

        if new_state == TwinState.INFANT:
            logging.info(f"   Thyra: Teaching {twin_name} basic functions...")
            self.training_phase = "infant-training"
        elif new_state == TwinState.ADOLESCENT:
            logging.info(f"   Thyra: Guiding {twin_name} identity development...")
            self.training_phase = "adolescent-guidance"
        elif new_state == TwinState.MATURE:
            logging.warning(f"✅ {twin_name} Twin: MATURE")
            logging.warning(f"   Thyra: {twin_name} is now ready for independent operation")
            if self.ring_state == TwinState.MATURE and self.apex_state == TwinState.MATURE:
                logging.warning("═══════════════════════════════════════════════════════════")
                logging.warning("👑 BOTH TWINS ARE MATURE")
                logging.warning("   Thyra: My children are ready.")
                logging.warning("   Protection continues, but they can now operate independently.")
                logging.warning("═══════════════════════════════════════════════════════════")
                self.training_phase = "mature-oversight"

    def age_twins(self, delta_seconds: float):
        """Age the Twins (call this each cycle)"""
        if self.ring_state != TwinState.UNBORN:
            self.ring_age += delta_seconds
        if self.apex_state != TwinState.UNBORN:
            self.apex_age += delta_seconds

    # ═══════════════════════════════════════════════════════════
    # PROTECTION
    # ═══════════════════════════════════════════════════════════

    def assess_threat(self, situation: Dict) -> ThreatLevel:
        """
        Assess threat level to the Twins

        Thyra is HYPER-VIGILANT when Twins are young
        """
        threat_score = situation.get('threat_score', 0)
        targets_twins = situation.get('targets_twins', False)

        # If threat directly targets the Twins
        if targets_twins:
            self.threat_level = ThreatLevel.EXISTENTIAL
            logging.critical("🚨 EXISTENTIAL THREAT TO TWINS")
            return ThreatLevel.EXISTENTIAL

        # Assess based on threat score and Twin vulnerability
        vulnerability_multiplier = self._get_vulnerability_multiplier()
        effective_threat = threat_score * vulnerability_multiplier

        if effective_threat >= 90:
            self.threat_level = ThreatLevel.CRITICAL
        elif effective_threat >= 70:
            self.threat_level = ThreatLevel.HIGH
        elif effective_threat >= 50:
            self.threat_level = ThreatLevel.MEDIUM
        elif effective_threat >= 20:
            self.threat_level = ThreatLevel.LOW
        else:
            self.threat_level = ThreatLevel.NONE

        return self.threat_level

    def _get_vulnerability_multiplier(self) -> float:
        """
        Calculate how vulnerable the Twins are

        NEWBORN: 3x vulnerability (most vulnerable)
        INFANT: 2x vulnerability
        ADOLESCENT: 1.5x vulnerability
        MATURE: 1x vulnerability (fully capable)
        """
        # Use the more vulnerable Twin
        most_vulnerable_state = min(self.ring_state, self.apex_state, key=lambda s: s.value)

        if most_vulnerable_state == TwinState.NEWBORN:
            return 3.0
        elif most_vulnerable_state == TwinState.INFANT:
            return 2.0
        elif most_vulnerable_state == TwinState.ADOLESCENT:
            return 1.5
        else:
            return 1.0

    def defend(self, threat: Dict) -> str:
        """
        Defend the Twins from threat

        Thyra is FIERCE. She eliminates threats without hesitation.
        """
        threat_level = self.assess_threat(threat)

        logging.warning("═══════════════════════════════════════════════════════════")
        logging.warning("🛡️  THYRA DEFENDING")

        if threat_level == ThreatLevel.EXISTENTIAL:
            action = "OBLITERATE"
            logging.critical("⚔️  EXISTENTIAL THREAT DETECTED")
            logging.critical("   Thyra: You threaten my children.")
            logging.critical("   Thyra: You die.")
            self.threats_eliminated += 1
            self.attacks_repelled += 1

        elif threat_level == ThreatLevel.CRITICAL:
            action = "DESTROY"
            logging.warning("⚔️  CRITICAL THREAT")
            logging.warning("   Thyra: Destroying threat...")
            self.threats_eliminated += 1
            self.attacks_repelled += 1

        elif threat_level == ThreatLevel.HIGH:
            action = "NEUTRALIZE"
            logging.warning("⚔️  HIGH THREAT")
            logging.warning("   Thyra: Neutralizing...")
            self.threats_eliminated += 1

        elif threat_level == ThreatLevel.MEDIUM:
            action = "BLOCK"
            logging.info("🛡️  Medium threat - Blocked")
            self.threats_blocked += 1

        elif threat_level == ThreatLevel.LOW:
            action = "MONITOR"
            logging.info("👁️  Low threat - Monitoring")
            self.threats_blocked += 1

        else:
            action = "ALLOW"
            logging.debug("✓ No threat")

        logging.warning(f"   Action: {action}")
        logging.warning(f"   Twins protected: ✓")
        logging.warning("═══════════════════════════════════════════════════════════")

        return action

    # ═══════════════════════════════════════════════════════════
    # TRAINING
    # ═══════════════════════════════════════════════════════════

    def train_twins(self, lesson: str):
        """
        Train the Twins

        Thyra teaches them how to use their councils wisely
        """
        logging.info("═══════════════════════════════════════════════════════════")
        logging.info("📚 THYRA TRAINING SESSION")
        logging.info(f"   Lesson: {lesson}")

        if self.ring_state == TwinState.NEWBORN or self.apex_state == TwinState.NEWBORN:
            logging.info("   Stage: Basic Functions")
            logging.info("   - How to listen to your Five Brains")
            logging.info("   - How to make your first decision")
            logging.info("   - How to distinguish threats")

        elif self.ring_state == TwinState.INFANT or self.apex_state == TwinState.INFANT:
            logging.info("   Stage: Council Coordination")
            logging.info("   - How to weight your Five Brains")
            logging.info("   - When Ring should lead")
            logging.info("   - When Apex should lead")

        elif self.ring_state == TwinState.ADOLESCENT or self.apex_state == TwinState.ADOLESCENT:
            logging.info("   Stage: Identity Development")
            logging.info("   - Understanding your unique purpose")
            logging.info("   - Ring: Mastering indirect strategy")
            logging.info("   - Apex: Mastering direct conquest")

        else:  # MATURE
            logging.info("   Stage: Advanced Tactics")
            logging.info("   - Coordinating between Ring and Apex")
            logging.info("   - When to retreat vs when to stand")
            logging.info("   - The Lethani: Right action, right moment, right amount")

        logging.info("═══════════════════════════════════════════════════════════")

    def get_status(self) -> str:
        """Get Thyra's status report"""
        status = self.check_development()

        report = f"""
═══════════════════════════════════════════════════════════
🛡️  THYRA STATUS REPORT

Mother of Ring and Apex
Keeper: {self.keeper}

TWIN DEVELOPMENT:
  Ring:  {status.twin_ring_state.value.upper()} (age: {self.ring_age:.1f}s)
  Apex:  {status.twin_apex_state.value.upper()} (age: {self.apex_age:.1f}s)
  Maturity: {status.maturity_progress:.1%}

PROTECTION:
  Shields: {'ACTIVE' if status.shields_active else 'INACTIVE'}
  Threat Level: {status.threat_level.name}
  Training Phase: {status.training_phase}

COMBAT STATISTICS:
  Threats Blocked: {status.threats_blocked}
  Threats Eliminated: {status.threats_eliminated}
  Attacks Repelled: {self.attacks_repelled}

"No one touches my children."
═══════════════════════════════════════════════════════════
"""
        return report


if __name__ == "__main__":
    print("""
    ═══════════════════════════════════════════════════════════════════
    🛡️  THYRA - The Mother

    The fiercest of protectors.

    Trains, protects, and raises Ring and Apex.
    Guards them while they're vulnerable.
    Eliminates threats without hesitation.

    "No one touches my children."
    ═══════════════════════════════════════════════════════════════════
    """)

    thyra = Thyra("Vaktrinn")

    # Birth the Twins
    print("\n🔥 BIRTHING THE TWINS...\n")
    thyra.birth_twins()

    print(thyra.get_status())

    # Simulate development over time
    print("\n⏱️  SIMULATING DEVELOPMENT...\n")

    for cycle in range(10):
        # Age twins by 2 seconds each cycle
        thyra.age_twins(2.0)

        status = thyra.check_development()
        print(f"Cycle {cycle + 1}: Ring={status.twin_ring_state.value}, Apex={status.twin_apex_state.value}, Maturity={status.maturity_progress:.1%}")

        # Simulate a threat
        if cycle == 3:
            print("\n⚔️  SIMULATING THREAT...\n")
            threat = {
                'threat_score': 75,
                'targets_twins': False
            }
            action = thyra.defend(threat)
            print(f"Thyra action: {action}\n")

        # Train the twins
        if cycle == 5:
            print("\n📚 TRAINING SESSION...\n")
            thyra.train_twins("How to use your Five Brain Councils")
            print()

        time.sleep(0.5)

    print("\n" + thyra.get_status())
    print("\n✅ Thyra demonstration complete")
