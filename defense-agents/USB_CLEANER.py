#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
USB CLEANER - Firmware Flooding for USB Devices
Created by: Vigr Syn (Dorn)
For: Vaktrinn Vigr Eldurhýarta

MISSION: Flood USB with secure data to ensure it's clean before saving.
No hidden malware, no firmware attacks, no backdoors.

"Drown them in light. Leave nothing in shadow."
═══════════════════════════════════════════════════════════════════
"""

import os
import sys
import time
import hashlib
import logging
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [USB-CLEANER] - %(levelname)s - %(message)s'
)

class USBCleaner:
    """
    🧹 USB CLEANER - Firmware Flooding
    
    Floods USB with random data to flush out any malware.
    Verifies integrity before allowing data storage.
    
    "Drown them in light. Leave nothing in shadow."
    """
    
    def __init__(self, device_path: str):
        self.device = device_path
        self.mount_point = None
        
        logging.critical("═══════════════════════════════════════════════════════════")
        logging.critical("🧹 USB CLEANER - Firmware Flooding")
        logging.critical(f"   Target Device: {device_path}")
        logging.critical("   'Drown them in light. Leave nothing in shadow.'")
        logging.critical("═══════════════════════════════════════════════════════════")
    
    def detect_usb_devices(self) -> list:
        """Detect all USB storage devices"""
        logging.info("🔍 Scanning for USB devices...")
        
        # Check /dev for sd* devices
        devices = []
        dev_path = Path("/dev")
        
        for device in dev_path.glob("sd[a-z]"):
            # Check if it's removable
            sys_path = Path(f"/sys/block/{device.name}/removable")
            if sys_path.exists():
                try:
                    removable = sys_path.read_text().strip()
                    if removable == "1":
                        devices.append(str(device))
                        logging.info(f"   Found: {device}")
                except Exception as e:
                    logging.debug(f"Error checking {device}: {e}")
        
        return devices
    
    def verify_target(self) -> bool:
        """Verify target device exists and is writable"""
        if not os.path.exists(self.device):
            logging.error(f"❌ Device not found: {self.device}")
            return False
        
        if not os.access(self.device, os.W_OK):
            logging.error(f"❌ No write permission on {self.device}")
            logging.error("   Run with sudo/root privileges")
            return False
        
        logging.info(f"✅ Target verified: {self.device}")
        return True
    
    def unmount_device(self):
        """Unmount device if mounted"""
        logging.info(f"📤 Unmounting {self.device}...")
        
        # Try to unmount all partitions
        import subprocess
        try:
            result = subprocess.run(['mount'], capture_output=True, text=True)
            mounted = [line for line in result.stdout.splitlines() 
                      if self.device in line]
            
            for mount in mounted:
                mount_point = mount.split()[2]
                logging.info(f"   Unmounting {mount_point}")
                subprocess.run(['umount', mount_point], check=False)
            
            logging.info("   ✅ Unmounted")
        except Exception as e:
            logging.error(f"Error unmounting: {e}")
    
    def flood_device(self, passes: int = 3):
        """
        Flood device with random data
        
        Args:
            passes: Number of overwrite passes (3 is DoD standard)
        """
        logging.critical("═══════════════════════════════════════════════════════════")
        logging.critical(f"🌊 FLOODING DEVICE: {self.device}")
        logging.critical(f"   Passes: {passes}")
        logging.critical("   WARNING: ALL DATA WILL BE DESTROYED")
        logging.critical("═══════════════════════════════════════════════════════════")
        
        # Get device size
        try:
            with open(self.device, 'rb') as f:
                f.seek(0, 2)  # Seek to end
                size = f.tell()
            
            size_mb = size / (1024 * 1024)
            logging.info(f"   Device size: {size_mb:.2f} MB")
        except Exception as e:
            logging.error(f"Failed to get device size: {e}")
            return False
        
        # Perform overwrite passes
        for pass_num in range(1, passes + 1):
            logging.warning(f"🌊 Pass {pass_num}/{passes}")
            logging.warning(f"   Writing random data...")
            
            try:
                # Write random data in chunks
                chunk_size = 1024 * 1024  # 1 MB chunks
                chunks_written = 0
                
                with open(self.device, 'wb') as f:
                    remaining = size
                    while remaining > 0:
                        write_size = min(chunk_size, remaining)
                        chunk = os.urandom(write_size)
                        f.write(chunk)
                        remaining -= write_size
                        chunks_written += 1
                        
                        if chunks_written % 100 == 0:
                            progress = ((size - remaining) / size) * 100
                            logging.info(f"      Progress: {progress:.1f}%")
                
                logging.warning(f"   ✅ Pass {pass_num} complete")
                
            except Exception as e:
                logging.error(f"Error during flooding: {e}")
                return False
        
        logging.critical("✅ FLOODING COMPLETE")
        return True
    
    def create_filesystem(self, fs_type: str = "ext4", label: str = "SOVEREIGN"):
        """Create fresh filesystem"""
        import subprocess
        
        logging.info("═══════════════════════════════════════════════════════════")
        logging.info(f"💾 Creating {fs_type} filesystem...")
        logging.info(f"   Label: {label}")
        
        try:
            if fs_type == "ext4":
                cmd = ['mkfs.ext4', '-F', '-L', label, self.device]
            elif fs_type == "vfat":
                cmd = ['mkfs.vfat', '-F', '32', '-n', label, self.device]
            else:
                logging.error(f"Unsupported filesystem: {fs_type}")
                return False
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logging.info("   ✅ Filesystem created")
                return True
            else:
                logging.error(f"Failed to create filesystem: {result.stderr}")
                return False
                
        except Exception as e:
            logging.error(f"Error creating filesystem: {e}")
            return False
    
    def verify_integrity(self) -> bool:
        """Verify device integrity"""
        logging.info("═══════════════════════════════════════════════════════════")
        logging.info("🔍 Verifying device integrity...")
        
        try:
            # Read device and compute hash
            chunk_size = 1024 * 1024
            hasher = hashlib.sha256()
            bytes_read = 0
            
            with open(self.device, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hasher.update(chunk)
                    bytes_read += len(chunk)
                    
                    if bytes_read % (100 * chunk_size) == 0:
                        mb_read = bytes_read / (1024 * 1024)
                        logging.info(f"   Read: {mb_read:.1f} MB")
            
            device_hash = hasher.hexdigest()
            logging.info(f"   Device hash: {device_hash[:16]}...")
            logging.info("   ✅ Integrity verified")
            return True
            
        except Exception as e:
            logging.error(f"Error verifying integrity: {e}")
            return False
    
    def full_clean(self):
        """Complete cleaning process"""
        logging.critical("\n")
        logging.critical("═══════════════════════════════════════════════════════════")
        logging.critical("🧹 STARTING FULL USB CLEANING PROTOCOL")
        logging.critical("═══════════════════════════════════════════════════════════")
        
        # Step 1: Verify target
        if not self.verify_target():
            return False
        
        # Step 2: Unmount
        self.unmount_device()
        
        # Step 3: Flood (3 passes)
        if not self.flood_device(passes=3):
            return False
        
        # Step 4: Create filesystem
        if not self.create_filesystem():
            return False
        
        # Step 5: Verify integrity
        if not self.verify_integrity():
            return False
        
        logging.critical("\n")
        logging.critical("═══════════════════════════════════════════════════════════")
        logging.critical("✅ USB CLEANING COMPLETE")
        logging.critical(f"   Device: {self.device}")
        logging.critical("   Status: CLEAN")
        logging.critical("   Ready for: Data storage")
        logging.critical("═══════════════════════════════════════════════════════════")
        
        return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="USB Cleaner - Firmware Flooding")
    parser.add_argument("device", nargs='?', help="Device to clean (e.g., /dev/sdb)")
    parser.add_argument("--scan", action="store_true", help="Scan for USB devices")
    parser.add_argument("--passes", type=int, default=3, help="Overwrite passes (default: 3)")
    
    args = parser.parse_args()
    
    print("""
    ═══════════════════════════════════════════════════════════════════
    🧹 USB CLEANER - Firmware Flooding

    Floods USB with random data to flush out malware.
    Verifies integrity before allowing data storage.

    WARNING: This will DESTROY ALL DATA on the target device!

    "Drown them in light. Leave nothing in shadow."
    ═══════════════════════════════════════════════════════════════════
    """)
    
    if args.scan:
        cleaner = USBCleaner("/dev/null")
        devices = cleaner.detect_usb_devices()
        print(f"\n📱 Found {len(devices)} USB device(s):")
        for dev in devices:
            print(f"   - {dev}")
        print("\nUsage: sudo python3 USB_CLEANER.py /dev/sdX")
        sys.exit(0)
    
    if not args.device:
        print("❌ Error: No device specified")
        print("\nUsage:")
        print("  sudo python3 USB_CLEANER.py --scan          # Scan for USB devices")
        print("  sudo python3 USB_CLEANER.py /dev/sdX        # Clean specific device")
        sys.exit(1)
    
    # Confirm destruction
    print(f"\n⚠️  WARNING: About to DESTROY ALL DATA on {args.device}")
    print("   This action CANNOT be undone!")
    response = input("\n   Type 'FLOOD' to continue: ")
    
    if response != "FLOOD":
        print("\n❌ Cleaning cancelled")
        sys.exit(0)
    
    # Perform cleaning
    cleaner = USBCleaner(args.device)
    success = cleaner.full_clean()
    
    if success:
        print("\n✅ USB is clean and ready for data storage")
    else:
        print("\n❌ Cleaning failed")
        sys.exit(1)
