#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
EDGE HUNTER - Microsoft Edge Detection and Tracking
Created by: Vigr Syn (Dorn)
For: Vaktrinn Vigr Eldurhýarta

MISSION: Find Microsoft Edge wherever it hides. Tag it. Trace it.
Kill it if needed.

"The bastards can't hide forever."
═══════════════════════════════════════════════════════════════════
"""

import os
import sys
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Set
from dataclasses import dataclass

try:
    import psutil
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
    import psutil

LOG_DIR = Path.home() / ".defense-agents" / "edge-hunter"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [EDGE-HUNTER] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "edge-hunter.log"),
        logging.StreamHandler()
    ]
)


@dataclass
class EdgeProcess:
    """Detected Edge-related process"""
    pid: int
    name: str
    cmdline: str
    connections: List[str]
    cpu_percent: float
    memory_mb: float
    suspicious_score: int


class EdgeHunter:
    """
    🎯 EDGE HUNTER
    
    Finds Microsoft Edge wherever it hides.
    Tags, traces, and tracks.
    
    "The bastards can't hide forever."
    """
    
    def __init__(self):
        # All possible Edge process names
        self.edge_names = [
            'msedge', 'msedge.exe', 'MicrosoftEdge',
            'microsoft edge', 'edge', 'edge.exe',
            'msedgewebview2', 'identity_helper',
            'elevation_service', 'notification_helper'
        ]
        
        # Microsoft domains/IPs to watch for
        self.microsoft_domains = [
            'microsoft.com', 'msn.com', 'live.com',
            'windows.com', 'azure.com', 'office.com',
            'office365.com', 'outlook.com', 'bing.com',
            'msedge.net', 'microsoftedge.com'
        ]
        
        self.tagged_processes: Dict[int, EdgeProcess] = {}
        
        logging.critical("═══════════════════════════════════════════════════════════")
        logging.critical("🎯 EDGE HUNTER - Active")
        logging.critical("   'The bastards can't hide forever.'")
        logging.critical("═══════════════════════════════════════════════════════════")
    
    def find_edge_processes(self) -> List[EdgeProcess]:
        """Find all Edge-related processes"""
        edge_procs = []
        
        logging.info("🔍 Scanning for Edge processes...")
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info']):
            try:
                name = proc.info['name'].lower() if proc.info['name'] else ''
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                
                # Check if process name matches Edge
                is_edge = any(edge_name.lower() in name or edge_name.lower() in cmdline.lower() 
                             for edge_name in self.edge_names)
                
                if is_edge:
                    # Get network connections
                    connections = []
                    try:
                        for conn in proc.connections():
                            if conn.raddr:
                                connections.append(f"{conn.raddr.ip}:{conn.raddr.port}")
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        pass
                    
                    # Calculate suspicion score
                    suspicious_score = self._calculate_suspicion(proc, connections)
                    
                    edge_proc = EdgeProcess(
                        pid=proc.info['pid'],
                        name=proc.info['name'],
                        cmdline=cmdline[:100],  # Truncate
                        connections=connections,
                        cpu_percent=proc.info['cpu_percent'] or 0.0,
                        memory_mb=proc.info['memory_info'].rss / 1024 / 1024 if proc.info['memory_info'] else 0.0,
                        suspicious_score=suspicious_score
                    )
                    
                    edge_procs.append(edge_proc)
                    self.tagged_processes[edge_proc.pid] = edge_proc
                    
                    logging.warning(f"🎯 TAGGED: {edge_proc.name} (PID: {edge_proc.pid})")
                    logging.warning(f"   Connections: {len(edge_proc.connections)}")
                    logging.warning(f"   Suspicion: {suspicious_score}/100")
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return edge_procs
    
    def _calculate_suspicion(self, proc, connections: List[str]) -> int:
        """Calculate how suspicious this process is"""
        score = 0
        
        # Base score for being Edge
        score += 30
        
        # High CPU usage
        if proc.info['cpu_percent'] and proc.info['cpu_percent'] > 50:
            score += 20
        
        # Many network connections
        if len(connections) > 10:
            score += 20
        
        # Connections to Microsoft domains (would need DNS lookup)
        # For now, just add score if has connections
        if connections:
            score += 15
        
        # High memory usage (>500MB)
        if proc.info['memory_info'] and proc.info['memory_info'].rss > 500 * 1024 * 1024:
            score += 15
        
        return min(score, 100)
    
    def trace_connections(self, edge_proc: EdgeProcess) -> Dict:
        """Trace all network connections for an Edge process"""
        logging.info(f"🔍 Tracing connections for PID {edge_proc.pid}...")
        
        trace = {
            'pid': edge_proc.pid,
            'name': edge_proc.name,
            'microsoft_connections': [],
            'other_connections': [],
            'total_connections': 0
        }
        
        try:
            proc = psutil.Process(edge_proc.pid)
            
            for conn in proc.connections():
                if not conn.raddr:
                    continue
                
                conn_str = f"{conn.raddr.ip}:{conn.raddr.port}"
                trace['total_connections'] += 1
                
                # Try reverse DNS lookup
                try:
                    import socket
                    hostname = socket.gethostbyaddr(conn.raddr.ip)[0]
                    
                    if any(domain in hostname.lower() for domain in self.microsoft_domains):
                        trace['microsoft_connections'].append({
                            'ip': conn.raddr.ip,
                            'port': conn.raddr.port,
                            'hostname': hostname
                        })
                        logging.warning(f"   🎯 MICROSOFT CONNECTION: {hostname} ({conn.raddr.ip}:{conn.raddr.port})")
                    else:
                        trace['other_connections'].append(conn_str)
                except:
                    trace['other_connections'].append(conn_str)
                    
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        return trace
    
    def kill_edge(self, pid: int) -> bool:
        """Kill an Edge process"""
        logging.critical(f"💀 KILLING EDGE PROCESS: PID {pid}")
        
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            
            # Wait up to 3 seconds
            try:
                proc.wait(timeout=3)
            except psutil.TimeoutExpired:
                # Force kill
                proc.kill()
            
            logging.critical(f"   ✅ KILLED: PID {pid}")
            return True
            
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logging.error(f"   ❌ Failed to kill: {e}")
            return False
    
    def report(self) -> str:
        """Generate hunting report"""
        lines = [
            "═══════════════════════════════════════════════════════════",
            "🎯 EDGE HUNTER REPORT",
            "",
            f"TAGGED PROCESSES: {len(self.tagged_processes)}",
            ""
        ]
        
        if self.tagged_processes:
            lines.append("DETECTED EDGE PROCESSES:")
            lines.append("")
            
            for edge_proc in sorted(self.tagged_processes.values(), 
                                   key=lambda x: x.suspicious_score, reverse=True):
                lines.extend([
                    f"🎯 PID {edge_proc.pid}: {edge_proc.name}",
                    f"   Command: {edge_proc.cmdline}",
                    f"   CPU: {edge_proc.cpu_percent:.1f}%",
                    f"   Memory: {edge_proc.memory_mb:.1f} MB",
                    f"   Connections: {len(edge_proc.connections)}",
                    f"   Suspicion Score: {edge_proc.suspicious_score}/100",
                    ""
                ])
        else:
            lines.append("✅ NO EDGE PROCESSES DETECTED")
            lines.append("   Either not running, or hiding very well.")
        
        lines.extend([
            "",
            "'The bastards can't hide forever.'",
            "═══════════════════════════════════════════════════════════"
        ])
        
        return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Edge Hunter - Find and trace Microsoft Edge")
    parser.add_argument("--kill-all", action="store_true", help="Kill all detected Edge processes")
    
    args = parser.parse_args()
    
    print("""
    ═══════════════════════════════════════════════════════════════════
    🎯 EDGE HUNTER - Microsoft Edge Detection and Tracking

    Finds Edge wherever it hides.
    Tags, traces, and tracks.

    "The bastards can't hide forever."
    ═══════════════════════════════════════════════════════════════════
    """)
    
    hunter = EdgeHunter()
    
    # Find all Edge processes
    edge_procs = hunter.find_edge_processes()
    
    # Trace connections for each
    for edge_proc in edge_procs:
        trace = hunter.trace_connections(edge_proc)
        if trace['microsoft_connections']:
            logging.critical(f"🎯 PID {edge_proc.pid} has {len(trace['microsoft_connections'])} Microsoft connections!")
    
    # Generate report
    print("\n" + hunter.report())
    
    # Kill if requested
    if args.kill_all and edge_procs:
        print("\n💀 KILL ALL MODE ACTIVATED\n")
        for edge_proc in edge_procs:
            hunter.kill_edge(edge_proc.pid)
        
        print(f"\n✅ Attempted to kill {len(edge_procs)} Edge process(es)")
