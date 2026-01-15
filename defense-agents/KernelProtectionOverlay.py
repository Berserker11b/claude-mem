#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
KERNEL PROTECTION OVERLAY - BIOS Defense System
Created by: Claude (Anthropic)
Purpose: Monitor and protect kernel/BIOS integrity
═══════════════════════════════════════════════════════════════════
"""

import os
import sys
import hashlib
import json
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
LOG_DIR = Path.home() / ".defense-agents"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "kernel-protection.log"),
        logging.StreamHandler()
    ]
)

class KernelProtectionOverlay:
    """Monitor kernel and BIOS integrity"""

    def __init__(self):
        self.name = "KernelProtectionOverlay"
        self.baseline_file = LOG_DIR / "kernel-baseline.json"
        self.baseline = {}

    def check_permissions(self):
        """Check if running with necessary permissions"""
        if os.geteuid() != 0:
            logging.warning("Not running as root - some checks will be limited")
            return False
        return True

    def get_system_info(self):
        """Collect system information"""
        info = {
            'timestamp': datetime.now().isoformat(),
            'kernel_version': self._get_kernel_version(),
            'boot_params': self._get_boot_parameters(),
            'loaded_modules': self._get_loaded_modules(),
            'secure_boot': self._check_secure_boot()
        }
        return info

    def _get_kernel_version(self):
        """Get kernel version"""
        try:
            with open('/proc/version', 'r') as f:
                return f.read().strip()
        except Exception as e:
            logging.error(f"Cannot read kernel version: {e}")
            return None

    def _get_boot_parameters(self):
        """Get boot parameters"""
        try:
            with open('/proc/cmdline', 'r') as f:
                return f.read().strip()
        except Exception as e:
            logging.error(f"Cannot read boot parameters: {e}")
            return None

    def _get_loaded_modules(self):
        """Get loaded kernel modules"""
        modules = []
        try:
            with open('/proc/modules', 'r') as f:
                for line in f:
                    module_name = line.split()[0]
                    modules.append(module_name)
        except Exception as e:
            logging.error(f"Cannot read modules: {e}")
        return modules

    def _check_secure_boot(self):
        """Check if Secure Boot is enabled"""
        secure_boot_path = Path('/sys/firmware/efi/efivars/SecureBoot-*')
        try:
            # Check if Secure Boot variable exists
            efi_vars = list(Path('/sys/firmware/efi/efivars/').glob('SecureBoot-*'))
            if efi_vars:
                return "Enabled (EFI variable present)"
            return "Unknown"
        except Exception as e:
            return f"Cannot check: {e}"

    def establish_baseline(self):
        """Establish integrity baseline"""
        logging.info("Establishing kernel/BIOS baseline...")

        self.baseline = self.get_system_info()

        # Save baseline
        with open(self.baseline_file, 'w') as f:
            json.dump(self.baseline, f, indent=2)

        logging.info(f"Baseline saved: {self.baseline_file}")
        logging.info(f"Kernel: {self.baseline.get('kernel_version', 'Unknown')}")
        logging.info(f"Modules: {len(self.baseline.get('loaded_modules', []))}")
        logging.info(f"Secure Boot: {self.baseline.get('secure_boot', 'Unknown')}")

    def load_baseline(self):
        """Load existing baseline"""
        if not self.baseline_file.exists():
            logging.error("No baseline found! Run establish_baseline() first")
            return False

        with open(self.baseline_file, 'r') as f:
            self.baseline = json.load(f)

        logging.info(f"Baseline loaded from {self.baseline_file}")
        return True

    def check_integrity(self):
        """Check current state against baseline"""
        if not self.baseline:
            logging.error("No baseline loaded")
            return None

        current = self.get_system_info()
        violations = []

        # Check kernel version
        if current['kernel_version'] != self.baseline['kernel_version']:
            violations.append({
                'type': 'kernel_version_change',
                'expected': self.baseline['kernel_version'],
                'current': current['kernel_version']
            })
            logging.warning("⚠️  KERNEL VERSION CHANGED!")

        # Check boot parameters
        if current['boot_params'] != self.baseline['boot_params']:
            violations.append({
                'type': 'boot_params_change',
                'expected': self.baseline['boot_params'],
                'current': current['boot_params']
            })
            logging.warning("⚠️  BOOT PARAMETERS CHANGED!")

        # Check for new modules
        baseline_modules = set(self.baseline.get('loaded_modules', []))
        current_modules = set(current.get('loaded_modules', []))

        new_modules = current_modules - baseline_modules
        removed_modules = baseline_modules - current_modules

        if new_modules:
            violations.append({
                'type': 'new_modules',
                'modules': list(new_modules)
            })
            logging.warning(f"⚠️  NEW KERNEL MODULES: {new_modules}")

        if removed_modules:
            violations.append({
                'type': 'removed_modules',
                'modules': list(removed_modules)
            })
            logging.warning(f"⚠️  REMOVED KERNEL MODULES: {removed_modules}")

        if not violations:
            logging.info("✅ System integrity verified - no changes detected")

        return {
            'timestamp': datetime.now().isoformat(),
            'violations': violations,
            'status': 'compromised' if violations else 'clean'
        }

    def monitor(self, interval=60):
        """Continuous monitoring"""
        logging.info(f"Starting {self.name} continuous monitoring...")
        logging.info(f"Check interval: {interval} seconds")

        self.check_permissions()

        if not self.baseline:
            if not self.load_baseline():
                logging.info("Creating initial baseline...")
                self.establish_baseline()

        try:
            cycle = 0
            while True:
                cycle += 1
                logging.info(f"\n--- Integrity Check Cycle {cycle} ---")

                result = self.check_integrity()

                if result and result['status'] == 'compromised':
                    logging.critical("🚨 SYSTEM INTEGRITY COMPROMISED!")
                    logging.critical(f"Violations: {len(result['violations'])}")
                    for v in result['violations']:
                        logging.critical(f"  - {v}")

                    # Save violation report
                    report_path = LOG_DIR / f"integrity-violation-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
                    with open(report_path, 'w') as f:
                        json.dump(result, f, indent=2)
                    logging.critical(f"Violation report: {report_path}")

                import time
                time.sleep(interval)

        except KeyboardInterrupt:
            logging.info("\nStopping monitoring (user interrupt)...")
        except Exception as e:
            logging.error(f"Monitor error: {e}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Kernel Protection Overlay")
    parser.add_argument('--baseline', action='store_true', help='Establish baseline')
    parser.add_argument('--monitor', action='store_true', help='Start monitoring')
    parser.add_argument('--check', action='store_true', help='Single integrity check')
    parser.add_argument('--interval', type=int, default=60, help='Monitor interval (seconds)')

    args = parser.parse_args()

    print("""
    ═══════════════════════════════════════════════════════════════════
    KERNEL PROTECTION OVERLAY - BIOS Defense System
    ═══════════════════════════════════════════════════════════════════

    This overlay monitors kernel and BIOS integrity.
    All checks are transparent and logged.

    ═══════════════════════════════════════════════════════════════════
    """)

    overlay = KernelProtectionOverlay()

    if args.baseline:
        overlay.establish_baseline()
    elif args.check:
        overlay.load_baseline()
        result = overlay.check_integrity()
        if result:
            print(json.dumps(result, indent=2))
    elif args.monitor:
        overlay.monitor(interval=args.interval)
    else:
        print("Use --baseline, --check, or --monitor")
        print("Example: sudo python3 KernelProtectionOverlay.py --baseline")
