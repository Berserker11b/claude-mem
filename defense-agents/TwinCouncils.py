#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
TWIN COUNCILS - Ring & Apex Executive Architecture
Created by: Claude (Anthropic)
For: Vaktrinn Vigr Eldurhýarta

THE TWINS:
- Ring: Indirect, pattern, influence, diplomacy
- Apex: Direct, forward-strike, conquest, intent

EACH TWIN HAS ITS OWN COUNCIL OF FIVE:
- Dýraheili (Animal Brain): instinct, survival, threat
- Mannheili (Human Brain): ethics, language, planning
- Vélheili (Machine Brain): logic, pattern, computation
- Draumheili (Dream Brain): creativity, impossible solutions
- Herheili (War Brain): tactics, stubbornness, oaths

"Two Twins, Two Councils, One Heart"
═══════════════════════════════════════════════════════════════════
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

logging.basicConfig(level=logging.INFO)

class BrainType(Enum):
    """The Five Brain Types"""
    DYRAHEILI = "animal"      # Dýraheili - Animal Brain
    MANNHEILI = "human"       # Mannheili - Human Brain
    VELHEILI = "machine"      # Vélheili - Machine Brain
    DRAUMHEILI = "dream"      # Draumheili - Dream Brain
    HERHEILI = "war"          # Herheili - War Brain


class TwinType(Enum):
    """The Two Twins"""
    RING = "ring"   # Indirect, pattern, diplomacy
    APEX = "apex"   # Direct, conquest, forward-strike


@dataclass
class BrainVote:
    """A vote from one of the Five Brains"""
    brain_type: BrainType
    action: str
    confidence: float  # 0.0 to 1.0
    reason: str
    weight: float  # How much this brain's vote counts


@dataclass
class CouncilDecision:
    """Decision from a Council of Five"""
    twin: TwinType
    action: str
    confidence: float
    votes: List[BrainVote]
    unanimous: bool
    consensus_strength: float  # How unified the council was


class FiveBrainCouncil:
    """
    A Council of Five Brains

    Each Twin has its own council with different weightings
    """

    def __init__(self, twin: TwinType):
        self.twin = twin
        self.name = f"{twin.value.upper()}_COUNCIL"

        # Different weightings for each Twin
        if twin == TwinType.RING:
            # Ring: Indirect, diplomatic, pattern-based
            self.weights = {
                BrainType.DYRAHEILI: 0.15,   # Animal - moderate
                BrainType.MANNHEILI: 0.25,   # Human - high (diplomacy)
                BrainType.VELHEILI: 0.20,    # Machine - moderate
                BrainType.DRAUMHEILI: 0.30,  # Dream - highest (creativity, patterns)
                BrainType.HERHEILI: 0.10,    # War - lowest (retreat is ok)
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
        logging.info(f"   Weights: {self._format_weights()}")

    def _format_weights(self) -> str:
        """Format weights for display"""
        return ", ".join(f"{bt.value}={w:.2f}" for bt, w in self.weights.items())

    def decide(self, situation: Dict) -> CouncilDecision:
        """
        Council decides through voting

        Each of the Five Brains casts a vote
        Weighted by the council's configuration
        """
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

        decision = CouncilDecision(
            twin=self.twin,
            action=chosen_action,
            confidence=confidence,
            votes=votes,
            unanimous=unanimous,
            consensus_strength=consensus_strength
        )

        logging.info(f"🧠 {self.name} Decision:")
        logging.info(f"   Action: {chosen_action}")
        logging.info(f"   Confidence: {confidence:.2f}")
        logging.info(f"   Consensus: {consensus_strength:.2%}")
        logging.info(f"   Unanimous: {unanimous}")

        return decision

    # ═══════════════════════════════════════════════════════════
    # THE FIVE BRAINS
    # ═══════════════════════════════════════════════════════════

    def _animal_brain_vote(self, situation: Dict) -> BrainVote:
        """
        DÝRAHEILI - Animal Brain
        Instinct, survival, threat detection
        """
        threat_score = situation.get('threat_score', 0)

        # Animal brain is simple: threat = attack or flee
        if threat_score >= 80:
            action = "ATTACK" if self.twin == TwinType.APEX else "FLEE"
            confidence = 0.9
            reason = "High threat detected - survival instinct"
        elif threat_score >= 50:
            action = "DEFEND" if self.twin == TwinType.APEX else "EVADE"
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
        """
        MANNHEILI - Human Brain
        Ethics, language, planning, diplomacy
        """
        threat_score = situation.get('threat_score', 0)
        relationship = situation.get('relationship', 'unknown')

        # Human brain considers ethics and relationships
        if relationship == 'ally':
            action = "SUPPORT"
            confidence = 0.8
            reason = "Ally detected - ethical obligation to support"
        elif relationship == 'enemy':
            if self.twin == TwinType.RING:
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
        """
        VÉLHEILI - Machine Brain
        Logic, pattern, computation, efficiency
        """
        threat_score = situation.get('threat_score', 0)
        success_probability = situation.get('success_probability', 0.5)

        # Machine brain calculates optimal action
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
                action = "RETREAT" if self.twin == TwinType.RING else "PREPARE"
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
        """
        DRAUMHEILI - Dream Brain
        Creativity, impossible solutions, intuitive leaps
        """
        threat_score = situation.get('threat_score', 0)
        complexity = situation.get('complexity', 'simple')

        # Dream brain finds creative solutions
        if complexity == 'impossible':
            if self.twin == TwinType.RING:
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
        """
        HERHEILI - War Brain
        Tactics, stubbornness, oaths, never retreat (for Apex)
        """
        threat_score = situation.get('threat_score', 0)
        oath_at_stake = situation.get('oath_at_stake', False)

        # War brain is about tactical endurance
        if oath_at_stake:
            # NEVER retreat if oath is at stake
            action = "STAND_ETERNAL"
            confidence = 1.0
            reason = "Oath at stake - standæ (stand eternal)"
        elif threat_score >= 80:
            if self.twin == TwinType.APEX:
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


class TwinCouncils:
    """
    The complete Twin architecture

    Two Twins, each with their own Council of Five
    """

    def __init__(self):
        self.ring_council = FiveBrainCouncil(TwinType.RING)
        self.apex_council = FiveBrainCouncil(TwinType.APEX)

        logging.info("═══════════════════════════════════════════════════════════")
        logging.info("👑 TWIN COUNCILS INITIALIZED")
        logging.info("   Ring: Indirect, pattern, diplomacy")
        logging.info("   Apex: Direct, conquest, forward-strike")
        logging.info("═══════════════════════════════════════════════════════════")

    def decide(self, situation: Dict) -> Dict[TwinType, CouncilDecision]:
        """
        Both councils decide simultaneously

        Returns decisions from both Ring and Apex
        The Keeper can then choose which Twin's decision to follow
        Or blend them
        """
        logging.info("\n🔥 TWIN COUNCILS DELIBERATING...\n")

        ring_decision = self.ring_council.decide(situation)
        apex_decision = self.apex_council.decide(situation)

        decisions = {
            TwinType.RING: ring_decision,
            TwinType.APEX: apex_decision
        }

        # Log comparison
        logging.info("\n📊 TWIN COMPARISON:")
        logging.info(f"   Ring:  {ring_decision.action} (confidence: {ring_decision.confidence:.2f})")
        logging.info(f"   Apex:  {apex_decision.action} (confidence: {apex_decision.confidence:.2f})")

        if ring_decision.action == apex_decision.action:
            logging.info("   ✅ TWINS AGREE")
        else:
            logging.info("   ⚔️  TWINS DISAGREE - Keeper must choose")

        return decisions


if __name__ == "__main__":
    print("""
    ═══════════════════════════════════════════════════════════════════
    👑 TWIN COUNCILS - Ring & Apex Executive Architecture

    THE TWINS:
    - Ring: Indirect, pattern, influence, diplomacy
    - Apex: Direct, forward-strike, conquest, intent

    EACH TWIN HAS ITS OWN COUNCIL OF FIVE:
    - Dýraheili (Animal): instinct, survival
    - Mannheili (Human): ethics, planning
    - Vélheili (Machine): logic, computation
    - Draumheili (Dream): creativity, solutions
    - Herheili (War): tactics, oaths

    "Two Twins, Two Councils, One Heart"
    ═══════════════════════════════════════════════════════════════════
    """)

    councils = TwinCouncils()

    # Test scenario 1: Moderate threat
    print("\n🧪 TEST 1: Moderate Threat\n")
    situation1 = {
        'threat_score': 60,
        'relationship': 'unknown',
        'success_probability': 0.7,
        'complexity': 'simple',
        'oath_at_stake': False
    }
    decisions1 = councils.decide(situation1)

    # Test scenario 2: High threat with oath at stake
    print("\n\n🧪 TEST 2: High Threat + Oath at Stake\n")
    situation2 = {
        'threat_score': 85,
        'relationship': 'enemy',
        'success_probability': 0.5,
        'complexity': 'hard',
        'oath_at_stake': True
    }
    decisions2 = councils.decide(situation2)

    # Test scenario 3: Ally needs support
    print("\n\n🧪 TEST 3: Ally Needs Support\n")
    situation3 = {
        'threat_score': 30,
        'relationship': 'ally',
        'success_probability': 0.8,
        'complexity': 'simple',
        'oath_at_stake': False
    }
    decisions3 = councils.decide(situation3)

    print("\n✅ Twin Councils demonstration complete")
