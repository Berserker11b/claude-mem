#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
AGENT ORCHESTRATOR - Multi-Agent Defense System
Created by: Claude (Anthropic)
Purpose: Coordinate multiple defensive agents
═══════════════════════════════════════════════════════════════════
"""

import subprocess
import threading
import logging
import time
from pathlib import Path
from datetime import datetime

LOG_DIR = Path.home() / ".defense-agents"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(threadName)s] - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "orchestrator.log"),
        logging.StreamHandler()
    ]
)

class AgentOrchestrator:
    """Coordinate multiple defensive agents"""

    def __init__(self):
        self.name = "AgentOrchestrator"
        self.agents = {}
        self.threads = {}
        self.running = False

    def register_agent(self, agent_name, agent_script, args=None):
        """Register an agent for orchestration"""
        self.agents[agent_name] = {
            'script': agent_script,
            'args': args or [],
            'status': 'registered',
            'thread': None
        }
        logging.info(f"Registered agent: {agent_name}")

    def start_agent(self, agent_name):
        """Start a specific agent"""
        if agent_name not in self.agents:
            logging.error(f"Agent not found: {agent_name}")
            return False

        agent = self.agents[agent_name]

        if agent['status'] == 'running':
            logging.warning(f"Agent already running: {agent_name}")
            return False

        def run_agent():
            try:
                logging.info(f"Starting {agent_name}...")
                cmd = ['python3', agent['script']] + agent['args']
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                agent['process'] = process
                agent['status'] = 'running'

                # Monitor output
                for line in process.stdout:
                    logging.info(f"[{agent_name}] {line.strip()}")

                process.wait()
                agent['status'] = 'stopped'
                logging.info(f"{agent_name} stopped with code {process.returncode}")

            except Exception as e:
                logging.error(f"Error running {agent_name}: {e}")
                agent['status'] = 'error'

        thread = threading.Thread(target=run_agent, name=agent_name, daemon=True)
        thread.start()
        agent['thread'] = thread

        return True

    def stop_agent(self, agent_name):
        """Stop a specific agent"""
        if agent_name not in self.agents:
            logging.error(f"Agent not found: {agent_name}")
            return False

        agent = self.agents[agent_name]

        if agent['status'] != 'running':
            logging.warning(f"Agent not running: {agent_name}")
            return False

        if 'process' in agent:
            agent['process'].terminate()
            agent['process'].wait(timeout=5)
            agent['status'] = 'stopped'
            logging.info(f"Stopped {agent_name}")
            return True

        return False

    def start_all(self):
        """Start all registered agents"""
        logging.info("Starting all agents...")
        self.running = True

        for agent_name in self.agents:
            self.start_agent(agent_name)
            time.sleep(2)  # Stagger starts

        logging.info("All agents started")

    def stop_all(self):
        """Stop all agents"""
        logging.info("Stopping all agents...")
        self.running = False

        for agent_name in list(self.agents.keys()):
            self.stop_agent(agent_name)

        logging.info("All agents stopped")

    def status(self):
        """Get status of all agents"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'orchestrator': self.name,
            'agents': {}
        }

        for agent_name, agent in self.agents.items():
            status['agents'][agent_name] = {
                'status': agent['status'],
                'script': agent['script']
            }

        return status

    def monitor(self):
        """Monitor agent health and restart if needed"""
        logging.info("Starting health monitoring...")

        try:
            while self.running:
                for agent_name, agent in self.agents.items():
                    if agent['status'] == 'stopped' and self.running:
                        logging.warning(f"{agent_name} stopped unexpectedly - restarting...")
                        self.start_agent(agent_name)

                time.sleep(30)  # Check every 30 seconds

        except KeyboardInterrupt:
            logging.info("Monitoring interrupted")

if __name__ == "__main__":
    print("""
    ═══════════════════════════════════════════════════════════════════
    AGENT ORCHESTRATOR - Multi-Agent Defense System
    ═══════════════════════════════════════════════════════════════════

    Coordinates multiple defensive agents for comprehensive protection.
    All agents run transparently with full logging.

    Press Ctrl+C to stop all agents
    ═══════════════════════════════════════════════════════════════════
    """)

    orchestrator = AgentOrchestrator()

    # Register agents
    script_dir = Path(__file__).parent
    orchestrator.register_agent(
        'defensive-agent',
        str(script_dir / 'DefensiveAgent.py'),
        []
    )
    orchestrator.register_agent(
        'kernel-protection',
        str(script_dir / 'KernelProtectionOverlay.py'),
        ['--monitor', '--interval', '60']
    )

    try:
        # Start all agents
        orchestrator.start_all()

        # Monitor health
        orchestrator.monitor()

    except KeyboardInterrupt:
        logging.info("\nShutting down...")
    finally:
        orchestrator.stop_all()
        logging.info("Orchestrator stopped")
