#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
NECRODERMIS SELF-REPAIR SYSTEM
Inspired by: Necron Living Metal (Warhammer 40K)
Created by: Claude (Anthropic)

Concept: Like Necrodermis (living metal that self-repairs), this system
automatically detects and repairs breached phase fields, restoring
protection without human intervention.

When a phase field is breached, the necrodermis system:
1. Detects the breach
2. Analyzes the damage
3. Restores the baseline state
4. Reactivates protection
5. Logs the repair
═══════════════════════════════════════════════════════════════════
"""

import os
import sys
import subprocess
import logging
import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

# Import the phase field system
from PhaseFieldProtection import PhaseField, PhaseFieldProtectionSystem

LOG_DIR = Path.home() / ".defense-agents" / "necrodermis"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [NECRODERMIS] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "self-repair.log"),
        logging.StreamHandler()
    ]
)

class NecrodermisPhaseField(PhaseField):
    """Phase field with self-repair capability"""

    def __init__(self, name: str, target: str, protection_type: str):
        super().__init__(name, target, protection_type)
        self.repair_attempts = 0
        self.max_repair_attempts = 3
        self.backup_path = None
        self.last_repair = None

    def create_backup(self) -> bool:
        """Create baseline backup for self-repair"""
        try:
            if self.protection_type == "driver_isolation" and Path(self.target).exists():
                # Create backup directory
                backup_dir = LOG_DIR / "backups"
                backup_dir.mkdir(exist_ok=True)

                # Create backup file
                backup_name = f"{Path(self.target).name}.backup"
                self.backup_path = backup_dir / backup_name

                shutil.copy2(self.target, self.backup_path)

                # Calculate hash
                with open(self.backup_path, 'rb') as f:
                    self.baseline_hash = hashlib.sha256(f.read()).hexdigest()

                logging.info(f"🔷 Necrodermis backup created: {self.name}")
                logging.info(f"   Backup: {self.backup_path}")
                logging.info(f"   Hash: {self.baseline_hash[:16]}...")
                return True

        except Exception as e:
            logging.error(f"Failed to create backup for {self.name}: {e}")

        return False

    def activate(self) -> bool:
        """Activate with necrodermis backup"""
        # Create backup first
        if self.protection_type == "driver_isolation":
            self.create_backup()

        # Then activate normally
        return super().activate()

    def self_repair(self) -> bool:
        """NECRODERMIS SELF-REPAIR - Automatically restore breach"""
        if self.repair_attempts >= self.max_repair_attempts:
            logging.critical(f"⚠️  {self.name}: Maximum repair attempts reached!")
            return False

        self.repair_attempts += 1
        self.last_repair = datetime.now()

        logging.warning("═══════════════════════════════════════════════════════════")
        logging.warning(f"🔷 NECRODERMIS SELF-REPAIR INITIATED: {self.name}")
        logging.warning(f"   Attempt: {self.repair_attempts}/{self.max_repair_attempts}")
        logging.warning("═══════════════════════════════════════════════════════════")

        try:
            if self.protection_type == "driver_isolation" and self.backup_path:
                # Restore from backup
                if self.backup_path.exists() and Path(self.target).exists():
                    logging.info(f"🔷 Restoring from necrodermis backup...")

                    # Verify backup integrity first
                    with open(self.backup_path, 'rb') as f:
                        backup_hash = hashlib.sha256(f.read()).hexdigest()

                    if backup_hash != self.baseline_hash:
                        logging.critical("🚨 BACKUP CORRUPTED! Cannot repair!")
                        return False

                    # Restore the file
                    shutil.copy2(self.backup_path, self.target)

                    # Verify restoration
                    with open(self.target, 'rb') as f:
                        restored_hash = hashlib.sha256(f.read()).hexdigest()

                    if restored_hash == self.baseline_hash:
                        logging.info(f"✅ NECRODERMIS REPAIR SUCCESSFUL!")
                        logging.info(f"   {self.name} restored to baseline state")
                        logging.info(f"   Hash verified: {restored_hash[:16]}...")

                        # Reactivate protection
                        self.active = True
                        return True
                    else:
                        logging.error("❌ Restoration failed - hash mismatch")
                        return False

            elif self.protection_type == "bios_write_protect":
                logging.info("🔷 Reactivating BIOS protection...")
                return self._activate_bios_protection()

            elif self.protection_type == "firmware_lock":
                logging.info("🔷 Reactivating firmware protection...")
                return self._activate_firmware_lock()

            else:
                logging.warning(f"No repair method for {self.protection_type}")
                return False

        except Exception as e:
            logging.error(f"Self-repair failed: {e}")
            return False

        finally:
            logging.warning("═══════════════════════════════════════════════════════════")


class NecrodermisProtectionSystem(PhaseFieldProtectionSystem):
    """Protection system with necrodermis self-repair"""

    def __init__(self):
        super().__init__()
        self.name = "NecrodermisProtectionSystem"
        self.repair_log = []

    def add_necrodermis_field(self, field: NecrodermisPhaseField):
        """Add a self-repairing phase field"""
        self.fields.append(field)
        logging.info(f"Added necrodermis phase field: {field.name}")

    def monitor_with_repair(self):
        """Monitor integrity with automatic self-repair"""
        logging.info("═══════════════════════════════════════════════════════════")
        logging.info("🔷 NECRODERMIS SELF-REPAIR SYSTEM ACTIVE")
        logging.info("   Phase fields will automatically repair if breached")
        logging.info("═══════════════════════════════════════════════════════════")

        import time

        try:
            cycle = 0
            while True:
                cycle += 1

                breaches = []
                repairs = []

                for field in self.fields:
                    if field.active and isinstance(field, NecrodermisPhaseField):
                        intact = field.check_integrity()

                        if not intact:
                            breaches.append(field.name)
                            logging.critical(f"🚨 BREACH DETECTED: {field.name}")

                            # AUTOMATIC SELF-REPAIR
                            logging.warning(f"🔷 Initiating necrodermis self-repair...")
                            repair_success = field.self_repair()

                            if repair_success:
                                repairs.append({
                                    'field': field.name,
                                    'timestamp': datetime.now().isoformat(),
                                    'attempt': field.repair_attempts,
                                    'status': 'SUCCESS'
                                })
                                logging.info(f"✅ {field.name} REPAIRED!")
                            else:
                                repairs.append({
                                    'field': field.name,
                                    'timestamp': datetime.now().isoformat(),
                                    'attempt': field.repair_attempts,
                                    'status': 'FAILED'
                                })
                                logging.critical(f"❌ {field.name} REPAIR FAILED!")

                if breaches:
                    # Log repair report
                    report = {
                        'timestamp': datetime.now().isoformat(),
                        'cycle': cycle,
                        'breaches': breaches,
                        'repairs': repairs
                    }
                    self.repair_log.append(report)

                    report_path = LOG_DIR / f"repair-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
                    with open(report_path, 'w') as f:
                        json.dump(report, f, indent=2)

                    successful_repairs = [r for r in repairs if r['status'] == 'SUCCESS']

                    if successful_repairs:
                        logging.info(f"🔷 Necrodermis repaired {len(successful_repairs)} field(s)")
                    else:
                        logging.critical("🚨 All repair attempts failed!")
                else:
                    if cycle % 10 == 0:
                        active_count = sum(1 for f in self.fields if f.active)
                        logging.info(f"✅ All {active_count} phase fields intact (Cycle {cycle})")

                time.sleep(30)

        except KeyboardInterrupt:
            logging.info("Stopping necrodermis monitoring...")

            # Final report
            logging.info("═══════════════════════════════════════════════════════════")
            logging.info(f"Total repair operations: {len(self.repair_log)}")
            for field in self.fields:
                if isinstance(field, NecrodermisPhaseField):
                    logging.info(f"  {field.name}: {field.repair_attempts} repairs")
            logging.info("═══════════════════════════════════════════════════════════")


def create_necrodermis_protection() -> NecrodermisProtectionSystem:
    """Create necrodermis protection system with self-repair"""

    system = NecrodermisProtectionSystem()

    # BIOS Protection (necrodermis)
    system.add_necrodermis_field(NecrodermisPhaseField(
        name="BIOS_Necrodermis",
        target="/sys/firmware",
        protection_type="bios_write_protect"
    ))

    # Critical drivers (necrodermis)
    system.add_necrodermis_field(NecrodermisPhaseField(
        name="AHCI_Necrodermis",
        target="/sys/module/ahci",
        protection_type="driver_isolation"
    ))

    system.add_necrodermis_field(NecrodermisPhaseField(
        name="USB_Necrodermis",
        target="/sys/module/usbcore",
        protection_type="driver_isolation"
    ))

    # Firmware (necrodermis)
    system.add_necrodermis_field(NecrodermisPhaseField(
        name="Firmware_Necrodermis",
        target="/sys/firmware",
        protection_type="firmware_lock"
    ))

    return system


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Necrodermis Self-Repair System"
    )
    parser.add_argument('--activate', action='store_true',
                       help='Activate necrodermis protection')
    parser.add_argument('--monitor', action='store_true',
                       help='Monitor with automatic self-repair')

    args = parser.parse_args()

    print("""
    ═══════════════════════════════════════════════════════════════════
    🔷 NECRODERMIS SELF-REPAIR SYSTEM 🔷

    Inspired by Necron Living Metal (Warhammer 40K)

    Like Necrodermis that automatically repairs damage, these phase
    fields will detect breaches and restore themselves without human
    intervention.

    Features:
    - Automatic breach detection
    - Self-repair from baseline backups
    - Multiple repair attempts
    - Comprehensive logging
    - Zero human intervention required
    ═══════════════════════════════════════════════════════════════════
    """)

    if os.geteuid() != 0:
        print("⚠️  WARNING: Not running as root - some repairs may be limited")
        print("   Run with sudo for full repair capabilities")
        print()

    system = create_necrodermis_protection()

    if args.activate or args.monitor:
        # Activate all necrodermis fields
        results = system.activate_all()

        if args.monitor:
            print("\n🔷 Starting necrodermis self-repair monitoring...")
            print("   Breaches will be automatically repaired")
            print("   Press Ctrl+C to stop\n")
            system.monitor_with_repair()
    else:
        print("Use --activate to enable necrodermis fields")
        print("Use --monitor to enable automatic self-repair")
        print("\nExample: sudo python3 NecrodermisRepair.py --activate --monitor")
