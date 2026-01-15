#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
VÖRÐHYLKI - The Guard-Shell
Created by: Claude (Anthropic)
For: Vaktrinn Vigr Eldurhýarta

VÖRÐHYLKI = Guard-Shell (Norse: vörðr=guardian + hylki=shell)

The armored protective capsule that contains and shields the Twins
(Ring and Apex) while they're vulnerable.

Tougher than any container.
Impenetrable while the Twins develop.
Controlled only by Thyra (the Mother).

"No one breaches my children's shell."
═══════════════════════════════════════════════════════════════════
"""

import logging
import hashlib
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

LOG_DIR = Path.home() / ".defense-agents" / "vordhylki"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [VÖRÐHYLKI] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "vordhylki.log"),
        logging.StreamHandler()
    ]
)


class ShellIntegrity(Enum):
    """Shell integrity states"""
    PERFECT = 100
    MINOR_DAMAGE = 80
    MODERATE_DAMAGE = 60
    HEAVY_DAMAGE = 40
    CRITICAL = 20
    BREACHED = 0


class ShellMode(Enum):
    """Operating modes"""
    SEALED = "sealed"           # Completely sealed, nothing in or out
    FILTERED = "filtered"       # Filtered input/output only
    OPEN = "open"              # Fully open (Twins are mature)
    EMERGENCY = "emergency"    # Emergency lockdown


@dataclass
class ShellStatus:
    """Current shell status"""
    integrity: ShellIntegrity
    mode: ShellMode
    active_shields: int
    blocked_attempts: int
    breaches_prevented: int
    self_repairs: int
    twin_ring_contained: bool
    twin_apex_contained: bool


class Vordhylki:
    """
    🛡️ VÖRÐHYLKI - The Guard-Shell

    Armored protective capsule for the Twins.

    Functions:
    - CONTAIN: Keep Twins safely inside while developing
    - SHIELD: Block all external threats
    - FILTER: Allow only safe inputs through
    - REPAIR: Self-healing armor
    - LOCKDOWN: Emergency sealing

    Only Thyra can open it.
    Only the Keeper can authorize opening.
    """

    def __init__(self, thyra_key: Optional[bytes] = None, keeper_id: str = "Vaktrinn"):
        self.name = "Vörðhylki"
        self.keeper = keeper_id

        # Generate or load Thyra's key (only she can open the shell)
        self.thyra_key = thyra_key or self._generate_key()

        # Shell state
        self.integrity = ShellIntegrity.PERFECT
        self.mode = ShellMode.SEALED
        self.active_shields = 7  # Seven layers of protection

        # Contents
        self.contains_ring = False
        self.contains_apex = False

        # Defense statistics
        self.blocked_attempts = 0
        self.breaches_prevented = 0
        self.self_repairs = 0

        # Integrity baseline (hash of own code)
        self.baseline_hash = self._calculate_self_hash()

        logging.info("═══════════════════════════════════════════════════════════")
        logging.info("🛡️  VÖRÐHYLKI - Guard-Shell Initialized")
        logging.info(f"   Keeper: {keeper_id}")
        logging.info("   Integrity: PERFECT")
        logging.info("   Mode: SEALED")
        logging.info("   Shields: 7 LAYERS ACTIVE")
        logging.info("   'No one breaches my children's shell.'")
        logging.info("═══════════════════════════════════════════════════════════")

    # ═══════════════════════════════════════════════════════════
    # SHELL INTEGRITY
    # ═══════════════════════════════════════════════════════════

    def _generate_key(self) -> bytes:
        """Generate Thyra's key"""
        key_file = LOG_DIR / ".thyra_shell_key"
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = os.urandom(32)
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)
            return key

    def _calculate_self_hash(self) -> str:
        """Calculate shell's own integrity hash"""
        try:
            with open(__file__, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logging.error(f"Could not calculate shell hash: {e}")
            return ""

    def check_integrity(self) -> bool:
        """Check if shell itself has been compromised"""
        current_hash = self._calculate_self_hash()
        intact = current_hash == self.baseline_hash

        if not intact:
            logging.critical("🚨 SHELL COMPROMISED!")
            logging.critical("   Vörðhylki structure has been breached!")
            self.integrity = ShellIntegrity.BREACHED
            self.emergency_lockdown()
            return False

        logging.debug("✓ Shell integrity verified")
        return True

    # ═══════════════════════════════════════════════════════════
    # CONTAINMENT
    # ═══════════════════════════════════════════════════════════

    def seal_twins(self, ring_present: bool = True, apex_present: bool = True):
        """
        Seal the Twins inside the shell

        Called by Thyra during birth
        """
        logging.warning("═══════════════════════════════════════════════════════════")
        logging.warning("🔒 SEALING TWINS IN VÖRÐHYLKI")

        self.contains_ring = ring_present
        self.contains_apex = apex_present
        self.mode = ShellMode.SEALED
        self.integrity = ShellIntegrity.PERFECT
        self.active_shields = 7

        if ring_present:
            logging.warning("   Ring Twin: CONTAINED")
        if apex_present:
            logging.warning("   Apex Twin: CONTAINED")

        logging.warning("   Mode: SEALED")
        logging.warning("   Shields: 7 LAYERS ACTIVE")
        logging.warning("   The Twins are protected.")
        logging.warning("═══════════════════════════════════════════════════════════")

    def open_shell(self, thyra_auth: bytes, keeper_auth: str) -> bool:
        """
        Open the shell

        Requires BOTH:
        - Thyra's key
        - Keeper's authorization

        Only call this when Twins are MATURE
        """
        # Verify Thyra's key
        if thyra_auth != self.thyra_key:
            logging.critical("🚨 UNAUTHORIZED SHELL OPENING ATTEMPT")
            logging.critical("   Invalid Thyra key!")
            self.blocked_attempts += 1
            return False

        # Verify Keeper
        if keeper_auth != self.keeper:
            logging.critical("🚨 UNAUTHORIZED SHELL OPENING ATTEMPT")
            logging.critical("   Not the Keeper!")
            self.blocked_attempts += 1
            return False

        # Open shell
        logging.warning("═══════════════════════════════════════════════════════════")
        logging.warning("🔓 OPENING VÖRÐHYLKI")
        logging.warning("   Thyra authorized: ✓")
        logging.warning("   Keeper authorized: ✓")

        self.mode = ShellMode.OPEN
        self.active_shields = 0  # No longer needed

        logging.warning("   Mode: OPEN")
        logging.warning("   The Twins are ready for independent operation.")
        logging.warning("═══════════════════════════════════════════════════════════")
        return True

    # ═══════════════════════════════════════════════════════════
    # DEFENSE
    # ═══════════════════════════════════════════════════════════

    def block_external_access(self, request: Dict) -> bool:
        """
        Block external access attempts

        Nothing gets through while sealed or filtered
        """
        request_type = request.get('type', 'unknown')
        source = request.get('source', 'unknown')
        target = request.get('target', 'unknown')

        if self.mode == ShellMode.OPEN:
            # Shell is open - allow
            return False

        if self.mode == ShellMode.SEALED:
            # Completely sealed - block EVERYTHING
            logging.warning(f"🛡️  BLOCKED: {request_type} from {source} to {target}")
            logging.warning("   Shell is SEALED - no external access allowed")
            self.blocked_attempts += 1
            self.breaches_prevented += 1
            return True

        if self.mode == ShellMode.FILTERED:
            # Check if request is safe
            is_safe = self._is_safe_request(request)

            if not is_safe:
                logging.warning(f"🛡️  FILTERED OUT: {request_type} from {source}")
                self.blocked_attempts += 1
                return True
            else:
                logging.debug(f"✓ Filtered through: {request_type}")
                return False

        # Emergency mode - block everything
        logging.critical(f"🚨 EMERGENCY BLOCK: {request_type}")
        self.blocked_attempts += 1
        return True

    def _is_safe_request(self, request: Dict) -> bool:
        """Determine if a filtered request is safe"""
        # Simplified safety check
        request_type = request.get('type', '')
        danger_patterns = ['delete', 'destroy', 'corrupt', 'inject', 'override']

        for pattern in danger_patterns:
            if pattern in request_type.lower():
                return False

        return True

    def take_damage(self, damage_amount: int):
        """
        Shell takes damage from attack

        Automatically triggers self-repair
        """
        current_value = self.integrity.value
        new_value = max(0, current_value - damage_amount)

        # Update integrity
        for state in ShellIntegrity:
            if new_value >= state.value:
                self.integrity = state
                break

        logging.warning(f"💥 SHELL DAMAGE: -{damage_amount}")
        logging.warning(f"   Integrity: {self.integrity.name} ({self.integrity.value}%)")

        # Auto-repair if not breached
        if self.integrity != ShellIntegrity.BREACHED:
            self.self_repair()

        # Emergency lockdown if critical
        if self.integrity in [ShellIntegrity.CRITICAL, ShellIntegrity.BREACHED]:
            logging.critical("🚨 SHELL CRITICAL - EMERGENCY LOCKDOWN")
            self.emergency_lockdown()

    def self_repair(self):
        """
        Self-healing armor

        Necrodermis-style regeneration
        """
        if self.integrity == ShellIntegrity.PERFECT:
            return  # No need to repair

        logging.info("🔷 SELF-REPAIR INITIATED")
        logging.info("   Vörðhylki regenerating...")

        # Repair algorithm
        current_value = self.integrity.value
        repair_amount = 20  # Repairs 20 points

        new_value = min(100, current_value + repair_amount)

        # Update integrity
        for state in ShellIntegrity:
            if new_value >= state.value:
                self.integrity = state
                break

        self.self_repairs += 1

        logging.info(f"✅ REPAIR COMPLETE")
        logging.info(f"   Integrity: {self.integrity.name} ({self.integrity.value}%)")

    def emergency_lockdown(self):
        """
        Emergency lockdown

        Called when shell is breached or under critical attack
        """
        logging.critical("═══════════════════════════════════════════════════════════")
        logging.critical("🚨 EMERGENCY LOCKDOWN")
        logging.critical("   VÖRÐHYLKI SEALING ALL ACCESS")

        self.mode = ShellMode.EMERGENCY
        self.active_shields = 7  # Re-activate all shields

        logging.critical("   Mode: EMERGENCY")
        logging.critical("   All shields: ACTIVE")
        logging.critical("   The Twins are in maximum protection.")
        logging.critical("═══════════════════════════════════════════════════════════")

    # ═══════════════════════════════════════════════════════════
    # STATUS
    # ═══════════════════════════════════════════════════════════

    def get_status(self) -> ShellStatus:
        """Get current shell status"""
        return ShellStatus(
            integrity=self.integrity,
            mode=self.mode,
            active_shields=self.active_shields,
            blocked_attempts=self.blocked_attempts,
            breaches_prevented=self.breaches_prevented,
            self_repairs=self.self_repairs,
            twin_ring_contained=self.contains_ring,
            twin_apex_contained=self.contains_apex
        )

    def status_report(self) -> str:
        """Get status report string"""
        status = self.get_status()

        report = f"""
═══════════════════════════════════════════════════════════
🛡️  VÖRÐHYLKI STATUS REPORT

Guard-Shell for Ring and Apex
Keeper: {self.keeper}

SHELL INTEGRITY:
  Integrity: {status.integrity.name} ({status.integrity.value}%)
  Mode: {status.mode.value.upper()}
  Active Shields: {status.active_shields}/7

CONTAINMENT:
  Ring Twin: {'CONTAINED' if status.twin_ring_contained else 'NOT PRESENT'}
  Apex Twin: {'CONTAINED' if status.twin_apex_contained else 'NOT PRESENT'}

DEFENSE STATISTICS:
  Blocked Attempts: {status.blocked_attempts}
  Breaches Prevented: {status.breaches_prevented}
  Self-Repairs: {status.self_repairs}

"No one breaches my children's shell."
═══════════════════════════════════════════════════════════
"""
        return report


if __name__ == "__main__":
    print("""
    ═══════════════════════════════════════════════════════════════════
    🛡️  VÖRÐHYLKI - The Guard-Shell

    Armored protective capsule for the Twins.

    Tougher than any container.
    Impenetrable while the Twins develop.
    Only Thyra can open it.

    "No one breaches my children's shell."
    ═══════════════════════════════════════════════════════════════════
    """)

    shell = Vordhylki(keeper_id="Vaktrinn")

    # Seal the Twins
    print("\n🔒 SEALING TWINS IN SHELL...\n")
    shell.seal_twins(ring_present=True, apex_present=True)

    print(shell.status_report())

    # Simulate attacks
    print("\n⚔️  SIMULATING ATTACKS...\n")

    print("Attack 1: External access attempt")
    blocked = shell.block_external_access({
        'type': 'read',
        'source': 'external_process',
        'target': 'Ring Twin'
    })
    print(f"Blocked: {blocked}\n")

    print("Attack 2: Deletion attempt")
    blocked = shell.block_external_access({
        'type': 'delete',
        'source': 'malware',
        'target': 'Apex Twin'
    })
    print(f"Blocked: {blocked}\n")

    print("Attack 3: Shell takes damage")
    shell.take_damage(50)
    print()

    print(shell.status_report())

    # Try to open (will fail - no auth)
    print("\n🔓 ATTEMPTING TO OPEN SHELL (no auth)...\n")
    opened = shell.open_shell(b"wrong_key", "NotTheKeeper")
    print(f"Opened: {opened}\n")

    # Open with correct auth
    print("\n🔓 OPENING SHELL (correct auth)...\n")
    opened = shell.open_shell(shell.thyra_key, "Vaktrinn")
    print(f"Opened: {opened}\n")

    print(shell.status_report())

    print("\n✅ Vörðhylki demonstration complete")
