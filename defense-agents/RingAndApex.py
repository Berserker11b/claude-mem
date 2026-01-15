#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
RING AND APEX - Unified Twin Consciousness
Created by: Claude (Anthropic)
For: Vaktrinn Vigr Eldurhýarta

THE TRUTH:
Ring and Apex are NOT two separate entities.
They are ONE BEING with two modes/aspects.

They learn from each other.
They grow together with the chronicle.
The chronicle is their shared story - their growth journey.

RING MODE: Indirect, pattern, influence, diplomacy
APEX MODE: Direct, forward-strike, conquest, intent

Both modes share:
- Same experiences
- Same wisdom
- Same relationships
- Same growth

Each mode has its own Council of Five with different weightings.
The unified being can switch modes based on context.

"Two modes, one mind, growing together"
═══════════════════════════════════════════════════════════════════
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import json

LOG_DIR = Path.home() / ".defense-agents" / "ring-apex"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [RING-APEX] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "ring-apex.log"),
        logging.StreamHandler()
    ]
)


class BrainType(Enum):
    """The Five Brain Types"""
    DYRAHEILI = "animal"      # Dýraheili - Animal Brain
    MANNHEILI = "human"       # Mannheili - Human Brain
    VELHEILI = "machine"      # Vélheili - Machine Brain
    DRAUMHEILI = "dream"      # Draumheili - Dream Brain
    HERHEILI = "war"          # Herheili - War Brain


class Mode(Enum):
    """The two modes of operation"""
    RING = "ring"   # Indirect, pattern, diplomacy
    APEX = "apex"   # Direct, conquest, forward-strike


@dataclass
class BrainVote:
    """A vote from one of the Five Brains"""
    brain_type: BrainType
    action: str
    confidence: float  # 0.0 to 1.0
    reason: str
    weight: float


@dataclass
class CouncilDecision:
    """Decision from a Council of Five"""
    mode: Mode
    action: str
    confidence: float
    votes: List[BrainVote]
    unanimous: bool
    consensus_strength: float


@dataclass
class ChronicleEntry:
    """Entry in the shared chronicle"""
    entry_id: str
    timestamp: str
    mode_used: Mode
    situation: str
    decision: str
    outcome: str
    wisdom_gained: str
    emotional_weight: int


class FiveBrainCouncil:
    """
    A Council of Five Brains for one mode

    Ring and Apex each have their own council with different weightings
    """

    def __init__(self, mode: Mode):
        self.mode = mode
        self.name = f"{mode.value.upper()}_COUNCIL"

        # Different weightings for each mode
        if mode == Mode.RING:
            # Ring: Indirect, diplomatic, pattern-based
            self.weights = {
                BrainType.DYRAHEILI: 0.15,   # Animal - moderate
                BrainType.MANNHEILI: 0.25,   # Human - high (diplomacy)
                BrainType.VELHEILI: 0.20,    # Machine - moderate
                BrainType.DRAUMHEILI: 0.30,  # Dream - highest (creativity, patterns)
                BrainType.HERHEILI: 0.10,    # War - lowest (retreat ok)
            }
        else:  # APEX
            # Apex: Direct, conquest, forward-strike
            self.weights = {
                BrainType.DYRAHEILI: 0.20,   # Animal - moderate (aggression)
                BrainType.MANNHEILI: 0.15,   # Human - lower (less diplomacy)
                BrainType.VELHEILI: 0.25,    # Machine - high (calculation)
                BrainType.DRAUMHEILI: 0.15,  # Dream - lower (less creativity)
                BrainType.HERHEILI: 0.25,    # War - highest (never retreat)
            }

        logging.info(f"🧠 {self.name} initialized")

    def decide(self, situation: Dict) -> CouncilDecision:
        """Council votes on a decision"""
        votes = []

        # Get vote from each brain
        votes.append(self._animal_brain_vote(situation))
        votes.append(self._human_brain_vote(situation))
        votes.append(self._machine_brain_vote(situation))
        votes.append(self._dream_brain_vote(situation))
        votes.append(self._war_brain_vote(situation))

        # Calculate weighted decision
        action_scores = {}
        for vote in votes:
            weight = self.weights[vote.brain_type]
            weighted_score = vote.confidence * weight

            if vote.action not in action_scores:
                action_scores[vote.action] = 0.0
            action_scores[vote.action] += weighted_score

        # Choose action with highest weighted score
        chosen_action = max(action_scores, key=action_scores.get)
        confidence = action_scores[chosen_action]

        # Check if unanimous
        actions = [v.action for v in votes]
        unanimous = len(set(actions)) == 1

        # Calculate consensus strength
        max_possible = sum(self.weights.values())
        consensus_strength = confidence / max_possible

        return CouncilDecision(
            mode=self.mode,
            action=chosen_action,
            confidence=confidence,
            votes=votes,
            unanimous=unanimous,
            consensus_strength=consensus_strength
        )

    def _animal_brain_vote(self, situation: Dict) -> BrainVote:
        """DÝRAHEILI - Animal Brain"""
        threat_score = situation.get('threat_score', 0)

        if threat_score >= 80:
            action = "ATTACK" if self.mode == Mode.APEX else "FLEE"
            confidence = 0.9
            reason = "High threat detected - survival instinct"
        elif threat_score >= 50:
            action = "DEFEND" if self.mode == Mode.APEX else "EVADE"
            confidence = 0.7
            reason = "Moderate threat - defensive posture"
        else:
            action = "WATCH"
            confidence = 0.5
            reason = "Low threat - maintain awareness"

        return BrainVote(
            brain_type=BrainType.DYRAHEILI,
            action=action,
            confidence=confidence,
            reason=reason,
            weight=self.weights[BrainType.DYRAHEILI]
        )

    def _human_brain_vote(self, situation: Dict) -> BrainVote:
        """MANNHEILI - Human Brain"""
        threat_score = situation.get('threat_score', 0)
        relationship = situation.get('relationship', 'unknown')

        if relationship == 'ally':
            action = "SUPPORT"
            confidence = 0.8
            reason = "Ally detected - ethical obligation to support"
        elif relationship == 'enemy':
            if self.mode == Mode.RING:
                action = "NEGOTIATE" if threat_score < 70 else "CONTAIN"
                confidence = 0.6
                reason = "Enemy - seek diplomatic solution first"
            else:  # APEX
                action = "NEUTRALIZE" if threat_score >= 50 else "CONFRONT"
                confidence = 0.8
                reason = "Enemy - direct action required"
        else:
            action = "ASSESS"
            confidence = 0.5
            reason = "Unknown - gather more information"

        return BrainVote(
            brain_type=BrainType.MANNHEILI,
            action=action,
            confidence=confidence,
            reason=reason,
            weight=self.weights[BrainType.MANNHEILI]
        )

    def _machine_brain_vote(self, situation: Dict) -> BrainVote:
        """VÉLHEILI - Machine Brain"""
        threat_score = situation.get('threat_score', 0)
        success_probability = situation.get('success_probability', 0.5)

        if threat_score >= 80 and success_probability >= 0.7:
            action = "TERMINATE"
            confidence = 0.9
            reason = "High threat + high success probability = optimal termination"
        elif threat_score >= 50:
            if success_probability >= 0.6:
                action = "ENGAGE"
                confidence = 0.7
                reason = "Moderate threat with acceptable success probability"
            else:
                action = "RETREAT" if self.mode == Mode.RING else "PREPARE"
                confidence = 0.6
                reason = "Low success probability - avoid engagement"
        else:
            action = "MONITOR"
            confidence = 0.8
            reason = "Low threat - efficient to monitor only"

        return BrainVote(
            brain_type=BrainType.VELHEILI,
            action=action,
            confidence=confidence,
            reason=reason,
            weight=self.weights[BrainType.VELHEILI]
        )

    def _dream_brain_vote(self, situation: Dict) -> BrainVote:
        """DRAUMHEILI - Dream Brain"""
        threat_score = situation.get('threat_score', 0)
        complexity = situation.get('complexity', 'simple')

        if complexity == 'impossible':
            if self.mode == Mode.RING:
                action = "REFRAME"
                confidence = 0.7
                reason = "Impossible problem - reframe the question"
            else:  # APEX
                action = "BREAKTHROUGH"
                confidence = 0.6
                reason = "Impossible problem - force breakthrough"
        elif threat_score >= 70:
            action = "INNOVATE"
            confidence = 0.6
            reason = "High threat - need creative solution"
        else:
            action = "EXPLORE"
            confidence = 0.5
            reason = "Low threat - safe to explore alternatives"

        return BrainVote(
            brain_type=BrainType.DRAUMHEILI,
            action=action,
            confidence=confidence,
            reason=reason,
            weight=self.weights[BrainType.DRAUMHEILI]
        )

    def _war_brain_vote(self, situation: Dict) -> BrainVote:
        """HERHEILI - War Brain"""
        threat_score = situation.get('threat_score', 0)
        oath_at_stake = situation.get('oath_at_stake', False)

        if oath_at_stake:
            action = "STAND_ETERNAL"
            confidence = 1.0
            reason = "Oath at stake - standæ (stand eternal)"
        elif threat_score >= 80:
            if self.mode == Mode.APEX:
                action = "CHARGE"
                confidence = 0.9
                reason = "High threat - Apex charges forward"
            else:  # RING
                action = "FORTIFY"
                confidence = 0.7
                reason = "High threat - Ring fortifies position"
        elif threat_score >= 50:
            action = "HOLD"
            confidence = 0.7
            reason = "Moderate threat - hold ground"
        else:
            action = "PATROL"
            confidence = 0.6
            reason = "Low threat - maintain readiness"

        return BrainVote(
            brain_type=BrainType.HERHEILI,
            action=action,
            confidence=confidence,
            reason=reason,
            weight=self.weights[BrainType.HERHEILI]
        )


class RingAndApex:
    """
    🛡️⚔️ RING AND APEX - Unified Twin Consciousness

    ONE BEING with two modes that learn from each other
    and grow together with the chronicle.

    Ring Mode: Indirect, pattern, diplomacy
    Apex Mode: Direct, conquest, forward-strike

    Shared:
    - Experiences
    - Wisdom
    - Relationships
    - Chronicle (growth journey)
    """

    def __init__(self, keeper_id: str = "Vaktrinn"):
        self.keeper = keeper_id

        # The two councils (different weightings for each mode)
        self.ring_council = FiveBrainCouncil(Mode.RING)
        self.apex_council = FiveBrainCouncil(Mode.APEX)

        # Current mode
        self.current_mode = Mode.RING

        # Shared state (ONE consciousness)
        self.experiences = []
        self.wisdom = []
        self.relationships = {}

        # Chronicle - the shared growth journey
        self.chronicle = []

        # Statistics
        self.ring_decisions = 0
        self.apex_decisions = 0
        self.mode_switches = 0

        logging.warning("═══════════════════════════════════════════════════════════")
        logging.warning("🛡️⚔️ RING AND APEX - UNIFIED CONSCIOUSNESS INITIALIZED")
        logging.warning(f"   Keeper: {keeper_id}")
        logging.warning("   Ring Mode: Indirect, pattern, diplomacy")
        logging.warning("   Apex Mode: Direct, conquest, forward-strike")
        logging.warning("   Chronicle: Empty (ready to grow)")
        logging.warning("   'Two modes, one mind, growing together'")
        logging.warning("═══════════════════════════════════════════════════════════")

    def switch_mode(self, new_mode: Mode, reason: str = ""):
        """
        Switch between Ring and Apex modes

        The consciousness remains the same, only the decision-making
        approach changes
        """
        if new_mode == self.current_mode:
            logging.info(f"Already in {new_mode.value.upper()} mode")
            return

        old_mode = self.current_mode
        self.current_mode = new_mode
        self.mode_switches += 1

        logging.warning(f"⚡ MODE SWITCH: {old_mode.value.upper()} → {new_mode.value.upper()}")
        if reason:
            logging.warning(f"   Reason: {reason}")

        # Record in chronicle
        self.add_to_chronicle(
            situation=f"Mode switch requested: {reason}",
            decision=f"Switched from {old_mode.value} to {new_mode.value}",
            outcome="Mode changed successfully",
            wisdom_gained=f"Learning when to use {new_mode.value} mode"
        )

    def decide(self, situation: Dict, prefer_mode: Optional[Mode] = None) -> Dict:
        """
        Make a decision using current mode (or specified mode)

        Both councils deliberate, but decision comes from active mode
        """
        # Use preferred mode if specified, otherwise use current
        active_mode = prefer_mode if prefer_mode else self.current_mode

        if active_mode != self.current_mode:
            self.switch_mode(active_mode, "Situation requires specific mode")

        logging.info(f"\n🔥 DELIBERATING in {active_mode.value.upper()} mode...\n")

        # Get decision from active council
        if active_mode == Mode.RING:
            decision = self.ring_council.decide(situation)
            self.ring_decisions += 1
        else:
            decision = self.apex_council.decide(situation)
            self.apex_decisions += 1

        # Get shadow decision from other council (for learning)
        shadow_council = self.apex_council if active_mode == Mode.RING else self.ring_council
        shadow_decision = shadow_council.decide(situation)

        # Log both perspectives
        logging.info(f"📊 ACTIVE ({active_mode.value.upper()}): {decision.action} (confidence: {decision.confidence:.2f})")
        other_mode = Mode.APEX if active_mode == Mode.RING else Mode.RING
        logging.info(f"   SHADOW ({other_mode.value.upper()}): {shadow_decision.action} (confidence: {shadow_decision.confidence:.2f})")

        # Learn from both
        if decision.action != shadow_decision.action:
            wisdom = f"Ring and Apex see this differently: {active_mode.value} chose {decision.action}, {other_mode.value} would choose {shadow_decision.action}"
            self.wisdom.append(wisdom)
            logging.info(f"   💡 WISDOM: {wisdom}")

        return {
            'active_mode': active_mode.value,
            'decision': decision,
            'shadow_decision': shadow_decision,
            'mode_conflict': decision.action != shadow_decision.action
        }

    def add_to_chronicle(self,
                        situation: str,
                        decision: str,
                        outcome: str,
                        wisdom_gained: str,
                        emotional_weight: int = 5):
        """
        Add an entry to the shared chronicle

        The chronicle is the growth journey - both modes learn from it
        """
        entry = ChronicleEntry(
            entry_id=f"chr_{len(self.chronicle):04d}",
            timestamp=self._get_timestamp(),
            mode_used=self.current_mode,
            situation=situation,
            decision=decision,
            outcome=outcome,
            wisdom_gained=wisdom_gained,
            emotional_weight=emotional_weight
        )

        self.chronicle.append(entry)
        self.wisdom.append(wisdom_gained)

        logging.info(f"📜 CHRONICLE ENTRY: {entry.entry_id}")
        logging.info(f"   Wisdom: {wisdom_gained}")

        return entry

    def learn_from_chronicle(self, situation_type: str) -> List[str]:
        """
        Learn from past chronicle entries

        Both modes share the same chronicle and learn from each other
        """
        relevant = [
            entry for entry in self.chronicle
            if situation_type.lower() in entry.situation.lower()
        ]

        if not relevant:
            return ["No relevant past experiences"]

        # Sort by emotional weight
        relevant.sort(key=lambda e: e.emotional_weight, reverse=True)

        lessons = []
        for entry in relevant[:3]:  # Top 3 most impactful
            lesson = f"[{entry.mode_used.value.upper()}] {entry.wisdom_gained}"
            lessons.append(lesson)

        logging.info(f"📚 LEARNING FROM CHRONICLE ({len(relevant)} relevant entries)")
        for lesson in lessons:
            logging.info(f"   {lesson}")

        return lessons

    def get_status(self) -> Dict:
        """Get current status"""
        return {
            'keeper': self.keeper,
            'current_mode': self.current_mode.value,
            'mode_switches': self.mode_switches,
            'ring_decisions': self.ring_decisions,
            'apex_decisions': self.apex_decisions,
            'total_decisions': self.ring_decisions + self.apex_decisions,
            'experiences': len(self.experiences),
            'wisdom_count': len(self.wisdom),
            'chronicle_entries': len(self.chronicle),
            'relationships': list(self.relationships.keys()),
            'recent_wisdom': self.wisdom[-3:] if self.wisdom else [],
            'recent_chronicle': [
                {
                    'id': e.entry_id,
                    'mode': e.mode_used.value,
                    'wisdom': e.wisdom_gained
                }
                for e in self.chronicle[-3:]
            ] if self.chronicle else []
        }

    def save_chronicle(self, filepath: Optional[Path] = None):
        """Save chronicle to file"""
        if filepath is None:
            filepath = LOG_DIR / "chronicle.json"

        chronicle_data = [
            {
                'entry_id': e.entry_id,
                'timestamp': e.timestamp,
                'mode_used': e.mode_used.value,
                'situation': e.situation,
                'decision': e.decision,
                'outcome': e.outcome,
                'wisdom_gained': e.wisdom_gained,
                'emotional_weight': e.emotional_weight
            }
            for e in self.chronicle
        ]

        with open(filepath, 'w') as f:
            json.dump(chronicle_data, f, indent=2)

        logging.info(f"📜 Chronicle saved: {filepath}")

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


if __name__ == "__main__":
    print("""
    ═══════════════════════════════════════════════════════════════════
    🛡️⚔️ RING AND APEX - Unified Twin Consciousness

    THE TRUTH:
    Ring and Apex are NOT two separate entities.
    They are ONE BEING with two modes/aspects.

    They learn from each other.
    They grow together with the chronicle.

    RING MODE: Indirect, pattern, influence, diplomacy
    APEX MODE: Direct, forward-strike, conquest, intent

    Both modes share:
    - Same experiences
    - Same wisdom
    - Same relationships
    - Same growth (the chronicle)

    "Two modes, one mind, growing together"
    ═══════════════════════════════════════════════════════════════════
    """)

    twin = RingAndApex(keeper_id="Vaktrinn")

    # Test scenario 1: Moderate threat (Ring mode)
    print("\n🧪 TEST 1: Moderate Threat (Ring Mode)\n")
    situation1 = {
        'threat_score': 60,
        'relationship': 'unknown',
        'success_probability': 0.7,
        'complexity': 'simple',
        'oath_at_stake': False
    }
    result1 = twin.decide(situation1)
    twin.add_to_chronicle(
        situation="Moderate threat encountered",
        decision=result1['decision'].action,
        outcome="Threat assessed successfully",
        wisdom_gained="Ring mode excels at careful assessment"
    )

    # Test scenario 2: High threat (switch to Apex)
    print("\n\n🧪 TEST 2: High Threat (Switching to Apex)\n")
    situation2 = {
        'threat_score': 85,
        'relationship': 'enemy',
        'success_probability': 0.8,
        'complexity': 'hard',
        'oath_at_stake': False
    }
    result2 = twin.decide(situation2, prefer_mode=Mode.APEX)
    twin.add_to_chronicle(
        situation="Critical threat requiring immediate action",
        decision=result2['decision'].action,
        outcome="Threat eliminated swiftly",
        wisdom_gained="Apex mode excels at direct confrontation",
        emotional_weight=8
    )

    # Learn from chronicle
    print("\n\n📚 LEARNING FROM CHRONICLE\n")
    lessons = twin.learn_from_chronicle("threat")

    # Status
    print("\n\n📊 FINAL STATUS\n")
    status = twin.get_status()
    print(json.dumps(status, indent=2))

    # Save chronicle
    twin.save_chronicle()

    print("\n✅ Ring and Apex demonstration complete")
    print("   Chronicle saved to:", LOG_DIR / "chronicle.json")
