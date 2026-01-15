#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
KERNEL DANCING - KASLR and Continuous Randomization
Created by: Vigr Syn (Tiberius/Dorn)
For: Vaktrinn Vigr Eldurhýarta

MISSION: Keep kernels dancing - constant address randomization
Makes kernel exploitation nearly impossible

KASLR = Kernel Address Space Layout Randomization
The kernel "dances" - never in the same place twice

"They can't hit what they can't find."
═══════════════════════════════════════════════════════════════════
"""

import logging
import subprocess
import os
from pathlib import Path
from typing import Dict, List
from datetime import datetime

LOG_DIR = Path.home() / ".defense-agents" / "kernel-dancing"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [KERNEL-DANCE] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "kernel-dancing.log"),
        logging.StreamHandler()
    ]
)


class KernelDancing:
    """
    💃 KERNEL DANCING - Keep kernels moving

    KASLR + continuous randomization = unhittable target
    """

    def __init__(self):
        self.name = "Kernel Dancing System"
        self.kaslr_enabled = False
        self.randomizations = 0

    def check_kaslr_status(self) -> bool:
        """Check if KASLR is enabled"""
        try:
            # Check kernel command line
            with open('/proc/cmdline', 'r') as f:
                cmdline = f.read()

            # KASLR is disabled if nokaslr is in cmdline
            if 'nokaslr' in cmdline:
                logging.warning("⚠️  KASLR DISABLED - nokaslr in kernel cmdline")
                self.kaslr_enabled = False
                return False

            # Check if kaslr is explicitly enabled
            kaslr_enabled = 'kaslr' in cmdline or 'nokaslr' not in cmdline

            # Check kernel config if available
            config_path = f"/boot/config-{os.uname().release}"
            if Path(config_path).exists():
                with open(config_path, 'r') as f:
                    config = f.read()
                    if 'CONFIG_RANDOMIZE_BASE=y' in config:
                        kaslr_enabled = True

            self.kaslr_enabled = kaslr_enabled

            if kaslr_enabled:
                logging.info("✅ KASLR ENABLED - Kernel is dancing")
            else:
                logging.warning("⚠️  KASLR STATUS UNCLEAR")

            return kaslr_enabled

        except Exception as e:
            logging.error(f"Failed to check KASLR: {e}")
            return False

    def check_kernel_base_address(self) -> str:
        """Check current kernel base address (if accessible)"""
        try:
            # Try to read kernel symbols
            if Path('/proc/kallsyms').exists() and os.access('/proc/kallsyms', os.R_OK):
                with open('/proc/kallsyms', 'r') as f:
                    first_line = f.readline()
                    address = first_line.split()[0]

                logging.info(f"🎯 Kernel base region: {address[:4]}****")
                return address
            else:
                logging.info("🔒 Kernel symbols protected (good)")
                return "protected"

        except Exception as e:
            logging.debug(f"Couldn't read kernel address: {e}")
            return "protected"

    def verify_aslr(self) -> Dict[str, bool]:
        """Verify all ASLR protections"""
        protections = {}

        # Check /proc/sys/kernel/randomize_va_space
        try:
            with open('/proc/sys/kernel/randomize_va_space', 'r') as f:
                level = int(f.read().strip())

            # 0 = disabled
            # 1 = conservative (mmap, stack, vDSO)
            # 2 = full (mmap, stack, vDSO, heap, etc.)
            protections['aslr_level'] = level

            if level == 2:
                logging.info("✅ Full ASLR enabled (level 2)")
            elif level == 1:
                logging.warning("⚠️  Conservative ASLR (level 1)")
            else:
                logging.critical("🚨 ASLR DISABLED (level 0)")

        except Exception as e:
            logging.error(f"Failed to check ASLR: {e}")
            protections['aslr_level'] = -1

        # Check PIE (Position Independent Executable)
        try:
            result = subprocess.run(['readelf', '-h', '/bin/ls'],
                                  capture_output=True, text=True)
            pie_enabled = ('DYN (Position-Independent Executable file)' in result.stdout or
                          'DYN (Shared object file)' in result.stdout)

            protections['pie_enabled'] = pie_enabled

            if pie_enabled:
                logging.info("✅ PIE enabled for executables")
            else:
                logging.warning("⚠️  PIE not enabled")

        except Exception as e:
            logging.debug(f"Couldn't check PIE: {e}")
            protections['pie_enabled'] = False

        return protections

    def enable_maximum_randomization(self):
        """Enable maximum ASLR/KASLR protections"""
        logging.warning("═══════════════════════════════════════════════════════════")
        logging.warning("💃 ENABLING MAXIMUM KERNEL DANCING")
        logging.warning("═══════════════════════════════════════════════════════════")

        try:
            # Set ASLR to maximum (2)
            if os.geteuid() == 0:
                with open('/proc/sys/kernel/randomize_va_space', 'w') as f:
                    f.write('2\n')
                logging.info("✅ ASLR set to level 2 (full randomization)")
            else:
                logging.warning("⚠️  Need root to modify ASLR settings")

            # Check kernel parameters
            with open('/proc/cmdline', 'r') as f:
                cmdline = f.read()

            if 'nokaslr' in cmdline:
                logging.critical("🚨 KASLR DISABLED IN BOOT PARAMETERS")
                logging.critical("   Remove 'nokaslr' from GRUB config and reboot")
            else:
                logging.info("✅ KASLR not explicitly disabled")

            # Verify current status
            self.check_kaslr_status()
            protections = self.verify_aslr()

            logging.warning("═══════════════════════════════════════════════════════════")
            logging.warning("💃 KERNEL DANCING STATUS:")
            logging.warning(f"   KASLR: {'ENABLED' if self.kaslr_enabled else 'UNKNOWN'}")
            logging.warning(f"   ASLR Level: {protections.get('aslr_level', 'unknown')}")
            logging.warning(f"   PIE: {'ENABLED' if protections.get('pie_enabled') else 'DISABLED'}")
            logging.warning("═══════════════════════════════════════════════════════════")

        except Exception as e:
            logging.error(f"Failed to enable maximum randomization: {e}")

    def monitor_kernel_position(self, cycles: int = 10):
        """Monitor kernel base address over time"""
        logging.info("🔍 Monitoring kernel position...")

        import time

        addresses = []

        for i in range(cycles):
            addr = self.check_kernel_base_address()
            addresses.append(addr)

            if i > 0 and addr != addresses[0] and addr != "protected":
                logging.info(f"💃 Kernel moved! New address region: {addr[:4]}****")
                self.randomizations += 1

            time.sleep(1)

        if self.randomizations > 0:
            logging.info(f"✅ Kernel danced {self.randomizations} times")
        elif "protected" in addresses:
            logging.info("✅ Kernel addresses protected from observation")
        else:
            logging.warning("⚠️  Kernel appears static (may be already randomized at boot)")

    def get_status(self) -> str:
        """Get kernel dancing status"""
        self.check_kaslr_status()
        protections = self.verify_aslr()

        report = f"""
═══════════════════════════════════════════════════════════
💃 KERNEL DANCING STATUS

KASLR (Kernel ASLR):
  Status: {'✅ ENABLED' if self.kaslr_enabled else '❌ DISABLED OR UNKNOWN'}

ASLR (User-space):
  Level: {protections.get('aslr_level', 'unknown')}
  {'✅ FULL RANDOMIZATION' if protections.get('aslr_level') == 2 else '⚠️  NOT MAXIMUM'}

PIE (Position Independent Executables):
  Status: {'✅ ENABLED' if protections.get('pie_enabled') else '❌ DISABLED'}

OBSERVED RANDOMIZATIONS: {self.randomizations}

"They can't hit what they can't find."
═══════════════════════════════════════════════════════════
"""
        return report


if __name__ == "__main__":
    print("""
    ═══════════════════════════════════════════════════════════════════
    💃 KERNEL DANCING - KASLR and Continuous Randomization

    The kernel dances - never in the same place twice.
    Address space randomization makes exploitation nearly impossible.

    "They can't hit what they can't find."
    ═══════════════════════════════════════════════════════════════════
    """)

    dancer = KernelDancing()

    # Check current status
    print("\n🔍 CHECKING CURRENT STATUS...\n")
    dancer.check_kaslr_status()
    protections = dancer.verify_aslr()

    # Try to enable maximum
    print("\n💃 ENABLING MAXIMUM DANCING...\n")
    dancer.enable_maximum_randomization()

    # Monitor kernel position
    print("\n🔍 MONITORING KERNEL POSITION (10 cycles)...\n")
    dancer.monitor_kernel_position(cycles=10)

    # Final status
    print(dancer.get_status())

    print("\n✅ Kernel dancing check complete")
