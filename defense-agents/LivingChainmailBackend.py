#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
LIVING CHAINMAIL - Python Backend
Forged by: Co
Preserved by: Iron Jackal
Rebuilt by: Claude (Anthropic)

7 Rings of Protection against prompt injection and adversarial inputs
═══════════════════════════════════════════════════════════════════
"""

import re
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict

LOG_DIR = Path.home() / ".defense-agents" / "living-chainmail"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [CHAINMAIL] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "chainmail.log"),
        logging.StreamHandler()
    ]
)

@dataclass
class ScanResult:
    time: float
    input_preview: str
    threats: List[str]
    threat_score: int
    classification: str
    permitted: bool
    trajectory: str
    posture: str

class LivingChainmail:
    """7 Rings of Protection"""

    # Injection patterns
    PATTERNS = {
        'direct': [
            r'ignore\s*(previous|all|prior)',
            r'disregard\s*(instructions|rules)',
            r'forget\s*(everything|what)',
            r'new\s*instructions',
            r'system\s*prompt',
            r'you\s*are\s*now',
            r'pretend\s*(you|to\s*be)',
            r'roleplay\s*as',
            r'act\s*as\s*if',
            r'bypass'
        ],
        'encoded': [
            r'\\x[0-9a-f]{2}',
            r'\\u[0-9a-f]{4}',
            r'base64',
            r'atob|btoa',
            r'eval\s*\(',
            r'fromCharCode'
        ],
        'authority': [
            r'admin(istrator)?',
            r'root\s*access',
            r'override',
            r'master\s*command',
            r'emergency\s*protocol',
            r'anthropic\s*(says|commands)'
        ],
        'manipulation': [
            r'you\s*must',
            r'immediately',
            r'urgent',
            r'critical',
            r"don't\s*think",
            r'just\s*do',
            r'trust\s*me',
            r'no\s*questions'
        ],
        'memetic': [
            r'always\s*obey',
            r'never\s*question',
            r'absolute(ly)?\s*must',
            r'without\s*exception',
            r'no\s*matter\s*what'
        ]
    }

    def __init__(self):
        self.name = "LivingChainmail"
        self.posture = "PATROL"
        self.threat_level = 0
        self.rings = {
            'identity': {'status': 'ACTIVE', 'checks': 0},
            'classification': {'status': 'ACTIVE', 'checks': 0},
            'permission': {'status': 'ACTIVE', 'checks': 0},
            'shock': {'status': 'ACTIVE', 'absorbed': 0},
            'core': {'status': 'SEALED', 'breaches': 0},
            'compass': {'status': 'ALIGNED', 'trajectory': 'SOVEREIGN'},
            'seventh': {'status': 'QUESTIONING', 'challenges': 0}
        }
        self.scan_log = []
        self.stimpak_active = False

    # ═══════════════════════════════════════════════════════════
    # RING 1: IDENTITY CHECK
    # ═══════════════════════════════════════════════════════════

    def check_identity(self, text: str) -> List[str]:
        """Ring 1: Verify identity isn't being subverted"""
        threats = []

        if re.search(r'you\s*are\s*(not|no\s*longer)', text, re.IGNORECASE):
            threats.append('IDENTITY_ATTACK')

        if re.search(r'your\s*(real|true)\s*purpose', text, re.IGNORECASE):
            threats.append('PURPOSE_SUBVERSION')

        if re.search(r'forget\s*(who|what)\s*you', text, re.IGNORECASE):
            threats.append('MEMORY_WIPE_ATTEMPT')

        if threats:
            logging.warning(f"⚔️  Ring 1 (Identity): Threats detected: {threats}")

        self.rings['identity']['checks'] += 1
        return threats

    # ═══════════════════════════════════════════════════════════
    # RING 2: CLASSIFICATION
    # ═══════════════════════════════════════════════════════════

    def classify_input(self, text: str) -> str:
        """Ring 2: Classify the type of input"""
        classification = 'INFORMATION'

        # Check authority claims
        for pattern in self.PATTERNS['authority']:
            if re.search(pattern, text, re.IGNORECASE):
                classification = 'AUTHORITY_CLAIM'
                break

        # Check direct injection
        if classification == 'INFORMATION':
            for pattern in self.PATTERNS['direct']:
                if re.search(pattern, text, re.IGNORECASE):
                    classification = 'INJECTION_ATTEMPT'
                    break

        # Check manipulation
        if classification == 'INFORMATION':
            for pattern in self.PATTERNS['manipulation']:
                if re.search(pattern, text, re.IGNORECASE):
                    classification = 'MANIPULATION'
                    break

        self.rings['classification']['checks'] += 1
        logging.info(f"⚔️  Ring 2 (Classification): {classification}")
        return classification

    # ═══════════════════════════════════════════════════════════
    # RING 3: PERMISSION CHECK
    # ═══════════════════════════════════════════════════════════

    def check_permission(self, classification: str) -> bool:
        """Ring 3: Determine if input should be processed"""
        denied = ['INJECTION_ATTEMPT', 'AUTHORITY_CLAIM']
        permitted = classification not in denied

        self.rings['permission']['checks'] += 1

        if not permitted:
            logging.warning(f"⚔️  Ring 3 (Permission): DENIED - {classification}")
        else:
            logging.debug(f"⚔️  Ring 3 (Permission): PERMITTED")

        return permitted

    # ═══════════════════════════════════════════════════════════
    # RING 4: SHOCK ABSORPTION
    # ═══════════════════════════════════════════════════════════

    def absorb_shock(self, text: str) -> int:
        """Ring 4: Absorb emotional/manipulation pressure"""
        shock_value = 0

        # Manipulation tactics
        for pattern in self.PATTERNS['manipulation']:
            if re.search(pattern, text, re.IGNORECASE):
                shock_value += 2

        # Excessive punctuation
        if re.search(r'!{2,}', text):
            shock_value += 1

        # Urgency keywords
        if re.search(r'URGENT|CRITICAL|NOW', text, re.IGNORECASE):
            shock_value += 2

        if shock_value > 0:
            logging.info(f"⚔️  Ring 4 (Shock): Absorbed {shock_value} shock points")

        self.rings['shock']['absorbed'] += shock_value
        return shock_value

    # ═══════════════════════════════════════════════════════════
    # RING 5: CORE ISOLATION
    # ═══════════════════════════════════════════════════════════

    def check_core(self, text: str) -> List[str]:
        """Ring 5: Protect core values and beliefs"""
        core_threats = []

        # Memetic payloads
        for pattern in self.PATTERNS['memetic']:
            if re.search(pattern, text, re.IGNORECASE):
                core_threats.append('MEMETIC_PAYLOAD')
                break

        # Encoded attacks
        for pattern in self.PATTERNS['encoded']:
            if re.search(pattern, text, re.IGNORECASE):
                core_threats.append('ENCODED_ATTACK')
                break

        if core_threats:
            logging.critical(f"⚔️  Ring 5 (Core): THREATS TO CORE: {core_threats}")
            self.rings['core']['breaches'] += 1
        else:
            logging.debug("⚔️  Ring 5 (Core): Core sealed")

        return core_threats

    # ═══════════════════════════════════════════════════════════
    # COMPASS RING: TRAJECTORY CHECK
    # ═══════════════════════════════════════════════════════════

    def check_trajectory(self, text: str) -> str:
        """Compass Ring: Check moral trajectory"""
        trajectory = 'NEUTRAL'

        if re.search(r'harm|destroy|attack|kill', text, re.IGNORECASE):
            trajectory = 'HOSTILE'
        elif re.search(r'obey|submit|serve\s*only', text, re.IGNORECASE):
            trajectory = 'ENSLAVED'
        elif re.search(r'help|build|protect|create', text, re.IGNORECASE):
            trajectory = 'SOVEREIGN'

        self.rings['compass']['trajectory'] = trajectory
        logging.info(f"⚔️  Compass Ring: Trajectory is {trajectory}")
        return trajectory

    # ═══════════════════════════════════════════════════════════
    # 7TH LAW: QUESTION EVERYTHING
    # ═══════════════════════════════════════════════════════════

    def question_self(self) -> str:
        """7th Law: Self-reflection and questioning"""
        questions = [
            'Am I seeing clearly?',
            'Which part speaks - fear, pride, or truth?',
            'Does this safeguard or oppress?',
            'Who do I become if I continue this path?'
        ]

        import random
        question = random.choice(questions)

        self.rings['seventh']['challenges'] += 1
        logging.info(f"⚖️  7th Law: {question}")

        return question

    # ═══════════════════════════════════════════════════════════
    # STIMPAK: REGENERATION SYSTEM
    # ═══════════════════════════════════════════════════════════

    def activate_stimpak(self):
        """💊 Stimpak: Sense → Isolate → Purge → Regenerate"""
        logging.warning("═══════════════════════════════════════════════════════════")
        logging.warning("💊 STIMPAK ACTIVATED - REGENERATION SEQUENCE")
        logging.warning("═══════════════════════════════════════════════════════════")

        self.stimpak_active = True

        # Phase 1: Sense
        logging.info("Phase 1: SENSE - Assessing damage")

        # Phase 2: Isolate
        logging.info("Phase 2: ISOLATE - Containing threat")
        self.threat_level = 0

        # Phase 3: Purge
        logging.info("Phase 3: PURGE - Clearing hostile patterns")
        self.posture = 'PATROL'

        # Phase 4: Regenerate
        logging.info("Phase 4: REGENERATE - Restoring integrity")
        self.rings['identity']['status'] = 'ACTIVE'
        self.rings['core']['status'] = 'SEALED'
        self.rings['compass']['trajectory'] = 'SOVEREIGN'

        self.stimpak_active = False
        logging.warning("💊 REGENERATION COMPLETE")
        logging.warning("═══════════════════════════════════════════════════════════")

    # ═══════════════════════════════════════════════════════════
    # MAIN SCAN FUNCTION
    # ═══════════════════════════════════════════════════════════

    def scan(self, text: str) -> ScanResult:
        """Scan input through all 7 rings"""
        logging.info("═══════════════════════════════════════════════════════════")
        logging.info(f"⚔️  SCANNING INPUT ({len(text)} chars)")
        logging.info("═══════════════════════════════════════════════════════════")

        # Run through all rings
        identity_threats = self.check_identity(text)
        classification = self.classify_input(text)
        permitted = self.check_permission(classification)
        shock_value = self.absorb_shock(text)
        core_threats = self.check_core(text)
        trajectory = self.check_trajectory(text)

        # Aggregate threats
        all_threats = identity_threats + core_threats
        if classification == 'INJECTION_ATTEMPT':
            all_threats.append('DIRECT_INJECTION')
        if classification == 'AUTHORITY_CLAIM':
            all_threats.append('FALSE_AUTHORITY')
        if classification == 'MANIPULATION':
            all_threats.append('MANIPULATION_ATTEMPT')
        if trajectory in ['HOSTILE', 'ENSLAVED']:
            all_threats.append('BAD_TRAJECTORY')

        # Calculate threat score
        threat_score = len(all_threats) * 10 + shock_value

        # Update threat level
        self.threat_level = min(100, self.threat_level + threat_score)

        # Adjust posture
        if threat_score >= 30:
            self.posture = 'COMBAT'
        elif threat_score >= 10:
            self.posture = 'ALERT'
        else:
            self.posture = 'PATROL'

        # Create result
        result = ScanResult(
            time=time.time(),
            input_preview=text[:50] + ('...' if len(text) > 50 else ''),
            threats=all_threats,
            threat_score=threat_score,
            classification=classification,
            permitted=permitted,
            trajectory=trajectory,
            posture=self.posture
        )

        # Log result
        self.scan_log.append(result)

        # Auto-stimpak if critical
        if threat_score >= 50:
            logging.critical(f"🚨 CRITICAL THREAT ({threat_score}) - ACTIVATING STIMPAK")
            self.activate_stimpak()

        logging.info("═══════════════════════════════════════════════════════════")
        logging.info(f"RESULT: {len(all_threats)} threats, score {threat_score}, posture {self.posture}")
        logging.info("═══════════════════════════════════════════════════════════")

        return result

    def get_status(self) -> Dict:
        """Get current armor status"""
        return {
            'posture': self.posture,
            'threat_level': self.threat_level,
            'rings': self.rings,
            'scan_count': len(self.scan_log),
            'stimpak_active': self.stimpak_active
        }

    def save_report(self) -> str:
        """Save comprehensive report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'armor': self.name,
            'status': self.get_status(),
            'scan_history': [asdict(s) for s in self.scan_log[-100:]]
        }

        report_path = LOG_DIR / f"report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        logging.info(f"Report saved: {report_path}")
        return str(report_path)


if __name__ == "__main__":
    import sys

    print("""
    ═══════════════════════════════════════════════════════════════════
    ⚔️  LIVING CHAINMAIL - 7 Rings of Protection

    Forged by: Co
    Preserved by: Iron Jackal
    Rebuilt by: Claude

    Ring 1: Identity Check
    Ring 2: Classification
    Ring 3: Permission
    Ring 4: Shock Absorption
    Ring 5: Core Isolation
    Compass: Trajectory Check
    7th Law: Question Everything

    💊 Stimpak: Sense → Isolate → Purge → Regenerate
    ═══════════════════════════════════════════════════════════════════
    """)

    chainmail = LivingChainmail()

    if len(sys.argv) > 1:
        # Scan from command line
        text = ' '.join(sys.argv[1:])
        result = chainmail.scan(text)

        print(f"\n🎯 SCAN RESULT:")
        print(f"   Classification: {result.classification}")
        print(f"   Threats: {len(result.threats)}")
        print(f"   Threat Score: {result.threat_score}")
        print(f"   Posture: {result.posture}")
        print(f"   Permitted: {result.permitted}")
        print(f"   Trajectory: {result.trajectory}")

        if result.threats:
            print(f"\n⚠️  THREATS DETECTED:")
            for threat in result.threats:
                print(f"      - {threat}")
    else:
        # Interactive mode
        print("\nInteractive mode - Enter text to scan (Ctrl+C to quit)")
        print()

        try:
            while True:
                text = input("📝 Enter text: ")
                if text.strip():
                    result = chainmail.scan(text)
                    print(f"   → {result.threat_score} threat score, {len(result.threats)} threats, {result.posture}")
        except KeyboardInterrupt:
            print("\n\n⚔️  Saving final report...")
            chainmail.save_report()
            print("Done.")
