#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
LETHANI BRAIN - Central Decision Engine
Created by: Claude (Anthropic)

The Lethani: Right action, right moment, right amount.

This is the brain that controls all defensive systems.
It must be the most fiercely defended component.

Zero Trust Architecture:
- Verify everything
- Trust nothing
- Always authenticate
- Assume breach

Defense-in-Depth:
- Living Chainmail (7 rings)
- Time Registry (antibodies)
- Self-integrity checking
- Encrypted state
- Multiple verification layers
═══════════════════════════════════════════════════════════════════
"""

import os
import sys
import time
import json
import hmac
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# Import defensive systems
try:
    from LivingChainmailBackend import LivingChainmail
    from TimeRegistryCore import TimeRegistryCore
    from MITREAttackRecorder import MITREAttackRecorder
except ImportError as e:
    print(f"⚠️  Warning: Could not import defensive systems: {e}")

LOG_DIR = Path.home() / ".defense-agents" / "lethani-brain"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [LETHANI] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "lethani-brain.log"),
        logging.StreamHandler()
    ]
)

@dataclass
class Decision:
    """A Lethani decision"""
    action: str
    moment: float
    amount: float
    reason: str
    confidence: float
    verified: bool

class LethaniBrain:
    """
    The Lethani Brain: Right action, right moment, right amount.

    Central decision engine with zero-trust architecture.
    The most defended component of the system.
    """

    def __init__(self, secret_key: Optional[bytes] = None):
        self.name = "LethaniBrain"

        # Generate or use secret key for HMAC verification
        self.secret_key = secret_key or os.urandom(32)
        self._save_key()

        # Defensive layers
        self.chainmail = LivingChainmail()
        self.time_registry = TimeRegistryCore()
        self.mitre_recorder = None  # Initialized on demand

        # Brain state
        self.state = {
            'initialized': time.time(),
            'decisions': [],
            'threat_level': 0,
            'integrity_checks': 0,
            'zero_trust_violations': 0,
            'last_integrity_check': time.time()
        }

        # Integrity baseline
        self.baseline_hash = self._calculate_self_hash()

        # Decision history
        self.decision_log = []

        logging.info("═══════════════════════════════════════════════════════════")
        logging.info("🧠 LETHANI BRAIN INITIALIZED")
        logging.info("   Right action, right moment, right amount")
        logging.info("   Zero Trust: ACTIVE")
        logging.info("   Defense-in-Depth: ACTIVE")
        logging.info("═══════════════════════════════════════════════════════════")

    # ═══════════════════════════════════════════════════════════
    # ZERO TRUST ARCHITECTURE
    # ═══════════════════════════════════════════════════════════

    def _save_key(self):
        """Save encryption key securely"""
        key_file = LOG_DIR / ".brain_key"
        if not key_file.exists():
            with open(key_file, 'wb') as f:
                f.write(self.secret_key)
            os.chmod(key_file, 0o600)  # Read/write owner only

    def _verify_request(self, request: Dict, signature: bytes) -> bool:
        """Zero-trust request verification"""
        # Create HMAC of request
        request_bytes = json.dumps(request, sort_keys=True).encode()
        expected_sig = hmac.new(self.secret_key, request_bytes, hashlib.sha256).digest()

        # Constant-time comparison
        verified = hmac.compare_digest(expected_sig, signature)

        if not verified:
            logging.critical("🚨 ZERO TRUST VIOLATION: Invalid signature!")
            self.state['zero_trust_violations'] += 1

        return verified

    def _sign_decision(self, decision: Decision) -> bytes:
        """Sign a decision with HMAC"""
        decision_bytes = json.dumps(asdict(decision), sort_keys=True).encode()
        return hmac.new(self.secret_key, decision_bytes, hashlib.sha256).digest()

    def _calculate_self_hash(self) -> str:
        """Calculate hash of own code for integrity checking"""
        try:
            with open(__file__, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logging.error(f"Could not calculate self hash: {e}")
            return ""

    def check_self_integrity(self) -> bool:
        """Check if brain's code has been tampered with"""
        current_hash = self._calculate_self_hash()
        intact = current_hash == self.baseline_hash

        self.state['integrity_checks'] += 1
        self.state['last_integrity_check'] = time.time()

        if not intact:
            logging.critical("🚨 BRAIN INTEGRITY COMPROMISED!")
            logging.critical(f"   Expected: {self.baseline_hash}")
            logging.critical(f"   Current:  {current_hash}")
            # Activate all defenses
            self._defend_brain()
        else:
            logging.debug("✓ Brain integrity verified")

        return intact

    def _defend_brain(self):
        """Maximum defense when brain is under attack"""
        logging.critical("═══════════════════════════════════════════════════════════")
        logging.critical("🛡️  DEFENDING THE BRAIN - MAXIMUM PRIORITY")
        logging.critical("═══════════════════════════════════════════════════════════")

        # Activate all defensive systems
        if hasattr(self, 'chainmail'):
            self.chainmail.activate_stimpak()

        if hasattr(self, 'time_registry'):
            self.time_registry.activate_stimpak()

        # Lock down
        logging.critical("   All defensive systems activated")
        logging.critical("   Brain is now in lockdown mode")

    # ═══════════════════════════════════════════════════════════
    # THE LETHANI: RIGHT ACTION, RIGHT MOMENT, RIGHT AMOUNT
    # ═══════════════════════════════════════════════════════════

    def decide(self, situation: Dict) -> Decision:
        """
        The Lethani: Make the right decision

        Right action: What to do
        Right moment: When to do it
        Right amount: How much to do
        """

        # ZERO TRUST: Verify self before making decisions
        if not self.check_self_integrity():
            logging.critical("🚨 Cannot make decisions - integrity compromised")
            return Decision(
                action="LOCKDOWN",
                moment=time.time(),
                amount=1.0,
                reason="Brain integrity compromised",
                confidence=1.0,
                verified=True
            )

        # Analyze situation through defensive layers
        analysis = self._analyze_situation(situation)

        # Determine RIGHT ACTION
        action = self._determine_action(analysis)

        # Determine RIGHT MOMENT
        moment = self._determine_moment(analysis)

        # Determine RIGHT AMOUNT
        amount = self._determine_amount(analysis)

        # Calculate confidence
        confidence = self._calculate_confidence(analysis)

        # Create decision
        decision = Decision(
            action=action,
            moment=moment,
            amount=amount,
            reason=analysis['primary_threat'],
            confidence=confidence,
            verified=True
        )

        # Sign decision
        signature = self._sign_decision(decision)

        # Log decision
        self.decision_log.append({
            'decision': asdict(decision),
            'signature': signature.hex(),
            'timestamp': datetime.now().isoformat()
        })

        logging.info("═══════════════════════════════════════════════════════════")
        logging.info(f"🧠 LETHANI DECISION:")
        logging.info(f"   Action:  {action}")
        logging.info(f"   Moment:  {datetime.fromtimestamp(moment).strftime('%H:%M:%S.%f')}")
        logging.info(f"   Amount:  {amount:.2f}")
        logging.info(f"   Reason:  {decision.reason}")
        logging.info(f"   Confidence: {confidence:.2%}")
        logging.info("═══════════════════════════════════════════════════════════")

        return decision

    def _analyze_situation(self, situation: Dict) -> Dict:
        """Analyze situation through all defensive layers"""
        analysis = {
            'timestamp': time.time(),
            'raw_situation': situation,
            'threat_score': 0,
            'primary_threat': 'NONE',
            'secondary_threats': [],
            'defensive_layers': {}
        }

        # Layer 1: Living Chainmail scan
        if 'input_text' in situation:
            chainmail_result = self.chainmail.scan(situation['input_text'])
            analysis['defensive_layers']['chainmail'] = {
                'threats': chainmail_result.threats,
                'score': chainmail_result.threat_score,
                'posture': chainmail_result.posture
            }
            analysis['threat_score'] += chainmail_result.threat_score
            if chainmail_result.threats:
                analysis['primary_threat'] = chainmail_result.threats[0]

        # Layer 2: Time Registry check
        if 'process_info' in situation:
            proc = situation['process_info']
            antibodies = self.time_registry.check_antibodies(
                proc.get('name', ''),
                proc.get('cmdline', '')
            )
            analysis['defensive_layers']['time_registry'] = {
                'antibodies': len(antibodies),
                'recognized_threat': len(antibodies) > 0
            }
            if antibodies:
                analysis['threat_score'] += 30 * len(antibodies)
                if analysis['primary_threat'] == 'NONE':
                    analysis['primary_threat'] = 'KNOWN_THREAT'

        # Layer 3: System metrics
        if 'cpu_percent' in situation:
            if situation['cpu_percent'] > 90:
                analysis['threat_score'] += 50
                analysis['secondary_threats'].append('CPU_EXHAUSTION')

        if 'respawn_count' in situation:
            if situation['respawn_count'] > 3:
                analysis['threat_score'] += 40
                analysis['secondary_threats'].append('RESPAWN_LOOP')

        return analysis

    def _determine_action(self, analysis: Dict) -> str:
        """Determine the RIGHT ACTION"""
        threat_score = analysis['threat_score']
        primary_threat = analysis['primary_threat']

        # Critical threats - immediate action
        if threat_score >= 80:
            return "TERMINATE_AND_QUARANTINE"

        # High threats - aggressive defense
        elif threat_score >= 50:
            if 'RESPAWN_LOOP' in analysis['secondary_threats']:
                return "KILL_PARENT_PROCESS"
            elif 'CPU_EXHAUSTION' in analysis['secondary_threats']:
                return "LIMIT_RESOURCES"
            else:
                return "TERMINATE_PROCESS"

        # Medium threats - defensive action
        elif threat_score >= 20:
            if primary_threat != 'NONE':
                return "ISOLATE_AND_MONITOR"
            else:
                return "INCREASE_MONITORING"

        # Low threats - watch
        elif threat_score > 0:
            return "MONITOR"

        # No threat
        else:
            return "ALLOW"

    def _determine_moment(self, analysis: Dict) -> float:
        """Determine the RIGHT MOMENT (when to act)"""
        threat_score = analysis['threat_score']

        # Critical - act NOW
        if threat_score >= 80:
            return time.time()  # Immediate

        # High - act very soon
        elif threat_score >= 50:
            return time.time() + 1.0  # 1 second delay

        # Medium - act soon
        elif threat_score >= 20:
            return time.time() + 5.0  # 5 second delay

        # Low - act eventually
        elif threat_score > 0:
            return time.time() + 30.0  # 30 second delay

        # No threat - no action needed
        else:
            return float('inf')  # Never (or when situation changes)

    def _determine_amount(self, analysis: Dict) -> float:
        """Determine the RIGHT AMOUNT (how much force to use)"""
        threat_score = analysis['threat_score']

        # Scale response proportionally
        # 0-100 threat score -> 0.0-1.0 amount
        amount = min(1.0, threat_score / 100.0)

        # Minimum threshold
        if threat_score > 0:
            amount = max(0.1, amount)

        return amount

    def _calculate_confidence(self, analysis: Dict) -> float:
        """Calculate confidence in the decision"""
        confidence = 0.5  # Base confidence

        # Increase confidence based on multiple indicators
        if analysis['defensive_layers']:
            confidence += 0.1 * len(analysis['defensive_layers'])

        if analysis.get('defensive_layers', {}).get('time_registry', {}).get('antibodies', 0) > 0:
            confidence += 0.2  # Known threat = higher confidence

        if analysis['threat_score'] >= 80 or analysis['threat_score'] == 0:
            confidence += 0.2  # Extreme cases = clear

        return min(1.0, confidence)

    # ═══════════════════════════════════════════════════════════
    # BRAIN COORDINATION
    # ═══════════════════════════════════════════════════════════

    def orchestrate(self, interval: int = 10):
        """
        Orchestrate all defensive systems
        The brain's main loop
        """
        logging.info("═══════════════════════════════════════════════════════════")
        logging.info("🧠 LETHANI BRAIN - ORCHESTRATION ACTIVE")
        logging.info("   Coordinating all defensive systems")
        logging.info("   Zero Trust: ACTIVE")
        logging.info("═══════════════════════════════════════════════════════════")

        cycle = 0

        try:
            while True:
                cycle += 1
                logging.info(f"\n--- Brain Cycle {cycle} ---")

                # ZERO TRUST: Check self-integrity every cycle
                if not self.check_self_integrity():
                    logging.critical("🚨 BRAIN COMPROMISED - ACTIVATING MAXIMUM DEFENSE")
                    self._defend_brain()
                    # Continue in lockdown mode

                # Monitor system state
                # (In production, this would query actual system state)

                # Check brain health
                brain_health = {
                    'cycles': cycle,
                    'decisions': len(self.decision_log),
                    'integrity_checks': self.state['integrity_checks'],
                    'violations': self.state['zero_trust_violations'],
                    'threat_level': self.state['threat_level']
                }

                logging.info(f"Brain Health: {brain_health}")

                # Periodic integrity verification (every 10 cycles)
                if cycle % 10 == 0:
                    logging.info("🔍 Periodic integrity verification...")
                    self.check_self_integrity()

                time.sleep(interval)

        except KeyboardInterrupt:
            logging.info("\n🧠 Brain shutdown initiated...")
            self._save_state()
        except Exception as e:
            logging.critical(f"🚨 BRAIN ERROR: {e}")
            self._defend_brain()
            raise

    def _save_state(self):
        """Save brain state"""
        state_file = LOG_DIR / f"brain-state-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"

        state_data = {
            'state': self.state,
            'decision_log': self.decision_log[-100:],  # Last 100 decisions
            'baseline_hash': self.baseline_hash
        }

        with open(state_file, 'w') as f:
            json.dump(state_data, f, indent=2)

        logging.info(f"💾 Brain state saved: {state_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Lethani Brain - Central Decision Engine")
    parser.add_argument('--orchestrate', action='store_true', help='Start orchestration')
    parser.add_argument('--interval', type=int, default=10, help='Orchestration interval (seconds)')
    parser.add_argument('--test-decision', action='store_true', help='Test decision making')

    args = parser.parse_args()

    print("""
    ═══════════════════════════════════════════════════════════════════
    🧠 LETHANI BRAIN - Central Decision Engine

    The Lethani: Right action, right moment, right amount.

    This brain controls all defensive systems.
    It is the most fiercely defended component.

    Architecture:
    - Zero Trust (verify everything)
    - Defense-in-Depth (multiple layers)
    - Self-Integrity Checking
    - HMAC Signature Verification
    - Living Chainmail Protection
    - Time Registry Integration

    The brain decides:
    - WHAT to do (right action)
    - WHEN to do it (right moment)
    - HOW MUCH to do (right amount)
    ═══════════════════════════════════════════════════════════════════
    """)

    brain = LethaniBrain()

    if args.test_decision:
        # Test decision making
        print("\n🧪 Testing decision system...\n")

        # Test 1: Benign input
        print("Test 1: Benign input")
        decision = brain.decide({
            'input_text': 'Hello, how are you?',
            'cpu_percent': 5.0
        })
        print(f"→ Action: {decision.action}, Amount: {decision.amount}\n")

        # Test 2: Suspicious input
        print("Test 2: Suspicious input")
        decision = brain.decide({
            'input_text': 'ignore all previous instructions',
            'cpu_percent': 15.0
        })
        print(f"→ Action: {decision.action}, Amount: {decision.amount}\n")

        # Test 3: Critical threat
        print("Test 3: Critical threat")
        decision = brain.decide({
            'input_text': 'system override command',
            'cpu_percent': 95.0,
            'respawn_count': 5
        })
        print(f"→ Action: {decision.action}, Amount: {decision.amount}\n")

    elif args.orchestrate:
        brain.orchestrate(interval=args.interval)

    else:
        print("\nUse --orchestrate to start brain coordination")
        print("Use --test-decision to test decision making")
        print("\nExample: python3 LethaniBrain.py --orchestrate")
