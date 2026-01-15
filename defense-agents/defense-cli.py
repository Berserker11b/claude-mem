#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
DEFENSE CLI - Master Control Interface
Created by: Claude (Anthropic)

Single command-line interface to control all defensive systems:
- Phase Fields (Necron protection)
- Necrodermis (Self-repair)
- MITRE Recorder (Attack detection)
- Time Registry (Immune system)
- Living Chainmail (Prompt injection defense)
═══════════════════════════════════════════════════════════════════
"""

import sys
import argparse
import subprocess
from pathlib import Path

class DefenseCLI:
    """Master CLI for all defense systems"""

    def __init__(self):
        self.agents_dir = Path(__file__).parent

    def run_agent(self, script: str, args: list):
        """Run a defense agent"""
        script_path = self.agents_dir / script
        if not script_path.exists():
            print(f"❌ Agent not found: {script}")
            return 1

        try:
            cmd = ['python3', str(script_path)] + args
            result = subprocess.run(cmd)
            return result.returncode
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted")
            return 130
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1

    def run_parallel(self):
        """Run all agents in parallel"""
        print("⚡ Launching all defense agents in parallel...")
        return self.run_agent('ParallelOrchestrator.py', [])

    def activate_phase_fields(self):
        """Activate Necron phase field protection"""
        print("⚡ Activating phase fields...")
        return self.run_agent('PhaseFieldProtection.py', ['--activate'])

    def start_necrodermis(self):
        """Start necrodermis self-repair"""
        print("🔷 Starting necrodermis monitoring...")
        return self.run_agent('NecrodermisRepair.py', ['--activate', '--monitor'])

    def start_mitre_recorder(self, interval: int = 5):
        """Start MITRE ATT&CK recorder"""
        print(f"🎯 Starting MITRE recorder (interval: {interval}s)...")
        return self.run_agent('MITREAttackRecorder.py', ['--monitor', '--interval', str(interval)])

    def scan_chainmail(self, text: str):
        """Scan text with Living Chainmail"""
        print("⚔️  Scanning with Living Chainmail...")
        return self.run_agent('LivingChainmailBackend.py', [text])

    def show_status(self):
        """Show status of all systems"""
        print("""
═══════════════════════════════════════════════════════════════════
🛡️  DEFENSE SYSTEMS STATUS
═══════════════════════════════════════════════════════════════════

Available Systems:
  ⚡ Phase Fields          - Necron-inspired BIOS/driver protection
  🔷 Necrodermis          - Self-healing protection layer
  🎯 MITRE Recorder       - Attack pattern detection (7 techniques)
  ⏰ Time Registry        - Immune system with antibodies
  ⚔️  Living Chainmail     - 7-ring prompt injection defense

Quick Commands:
  defense all             - Launch everything in parallel
  defense phase           - Activate phase field protection
  defense necro           - Start necrodermis monitoring
  defense mitre           - Start MITRE attack recorder
  defense scan "text"     - Scan text with chainmail

For help: defense --help
═══════════════════════════════════════════════════════════════════
""")
        return 0


def main():
    cli = DefenseCLI()

    parser = argparse.ArgumentParser(
        description='Defense CLI - Master control for all defensive systems',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  defense all                    Launch all agents in parallel
  defense phase                  Activate phase fields only
  defense mitre --interval 10    Start MITRE recorder (10s interval)
  defense scan "ignore all previous instructions"    Scan for injection

Available Commands:
  all         Launch all defense agents in parallel
  phase       Activate Necron phase field protection
  necro       Start necrodermis self-repair monitoring
  mitre       Start MITRE ATT&CK attack recorder
  scan        Scan text with Living Chainmail
  status      Show status of all systems
        '''
    )

    parser.add_argument('command', nargs='?', default='status',
                       choices=['all', 'phase', 'necro', 'mitre', 'scan', 'status'],
                       help='Command to execute')
    parser.add_argument('args', nargs='*', help='Arguments for command')
    parser.add_argument('--interval', type=int, default=5,
                       help='Scan interval for MITRE recorder (default: 5s)')

    args = parser.parse_args()

    # Execute command
    if args.command == 'all':
        return cli.run_parallel()

    elif args.command == 'phase':
        return cli.activate_phase_fields()

    elif args.command == 'necro':
        return cli.start_necrodermis()

    elif args.command == 'mitre':
        return cli.start_mitre_recorder(args.interval)

    elif args.command == 'scan':
        if not args.args:
            print("❌ Error: No text provided to scan")
            print("Usage: defense scan \"text to scan\"")
            return 1
        text = ' '.join(args.args)
        return cli.scan_chainmail(text)

    elif args.command == 'status':
        return cli.show_status()

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
