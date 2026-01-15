#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
STATUS DASHBOARD - Dros Delnoch Command Center
Created by: Claude (Anthropic)
For: Vaktrinn Vigr Eldurhýarta

Web-based dashboard for monitoring and controlling:
- Dros Delnoch (Valkyrie + Plasma + Gauss)
- Phase Fields
- Necrodermis
- Thyra (Twin Protector)
- Firmware Flooding
- All defense agents

Features:
- Real-time status monitoring
- 4 terminal windows for multitasking
- Quick keys (keyboard shortcuts)
- Live logs
- System controls

Access: http://localhost:8888
═══════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import logging
import subprocess
import psutil
import threading
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request
from flask_socketio import SocketIO, emit

LOG_DIR = Path.home() / ".defense-agents" / "dashboard"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [DASHBOARD] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "dashboard.log"),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dros-delnoch-fortress'
socketio = SocketIO(app, cors_allowed_origins="*")

# System status tracking
system_status = {
    'dros_delnoch': {'running': False, 'pid': None},
    'phase_fields': {'running': False, 'pid': None},
    'necrodermis': {'running': False, 'pid': None},
    'thyra': {'running': False, 'pid': None},
    'firmware_flooding': {'running': False, 'pid': None},
    'lethani_brain': {'running': False, 'pid': None}
}

# Terminal processes (4 terminals)
terminals = {
    'terminal1': None,
    'terminal2': None,
    'terminal3': None,
    'terminal4': None
}

# Quick keys mapping
QUICK_KEYS = {
    'F1': 'start_dros_delnoch',
    'F2': 'start_phase_fields',
    'F3': 'start_necrodermis',
    'F4': 'start_thyra',
    'F5': 'firmware_flood',
    'F6': 'stop_all',
    'F7': 'status_all',
    'F8': 'self_repair_all',
    'F9': 'emergency_lockdown',
    'F10': 'restart_all'
}

HTML_DASHBOARD = """
<!DOCTYPE html>
<html>
<head>
    <title>Dros Delnoch Command Center</title>
    <meta charset="utf-8">
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Courier New', monospace;
            background: #0a0a0a;
            color: #00ff00;
            padding: 10px;
        }
        .header {
            text-align: center;
            border: 2px solid #00ff00;
            padding: 15px;
            margin-bottom: 10px;
            background: #1a1a1a;
        }
        .header h1 {
            color: #00ffff;
            font-size: 24px;
            text-shadow: 0 0 10px #00ffff;
        }
        .header .subtitle {
            color: #ffaa00;
            margin-top: 5px;
        }
        .main-container {
            display: grid;
            grid-template-columns: 250px 1fr;
            gap: 10px;
            height: calc(100vh - 150px);
        }
        .sidebar {
            border: 2px solid #00ff00;
            padding: 10px;
            background: #1a1a1a;
            overflow-y: auto;
        }
        .sidebar h3 {
            color: #00ffff;
            border-bottom: 1px solid #00ff00;
            padding-bottom: 5px;
            margin-bottom: 10px;
        }
        .system-status {
            margin-bottom: 15px;
        }
        .system-item {
            padding: 8px;
            margin: 5px 0;
            border: 1px solid #333;
            background: #0f0f0f;
            cursor: pointer;
            transition: all 0.3s;
        }
        .system-item:hover {
            background: #2a2a2a;
            border-color: #00ff00;
        }
        .system-item.running {
            border-color: #00ff00;
            box-shadow: 0 0 5px #00ff00;
        }
        .system-item.stopped {
            border-color: #ff0000;
        }
        .system-name {
            font-weight: bold;
            color: #00ffff;
        }
        .system-state {
            font-size: 11px;
            margin-top: 3px;
        }
        .running .system-state { color: #00ff00; }
        .stopped .system-state { color: #ff0000; }
        .quick-keys {
            margin-top: 20px;
        }
        .quick-key {
            display: flex;
            justify-content: space-between;
            padding: 5px;
            margin: 3px 0;
            font-size: 11px;
            border-bottom: 1px solid #222;
        }
        .key-binding {
            color: #ffaa00;
            font-weight: bold;
        }
        .terminals-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: 1fr 1fr;
            gap: 10px;
        }
        .terminal {
            border: 2px solid #00ff00;
            background: #000;
            padding: 10px;
            overflow-y: auto;
            font-size: 12px;
            position: relative;
        }
        .terminal-header {
            position: sticky;
            top: 0;
            background: #1a1a1a;
            padding: 5px;
            border-bottom: 1px solid #00ff00;
            margin-bottom: 10px;
            color: #00ffff;
            font-weight: bold;
        }
        .terminal-content {
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .log-line {
            margin: 2px 0;
            padding: 2px;
        }
        .log-info { color: #00ff00; }
        .log-warning { color: #ffaa00; }
        .log-error { color: #ff0000; }
        .log-critical {
            color: #ff0000;
            font-weight: bold;
            background: #330000;
        }
        .footer {
            margin-top: 10px;
            padding: 10px;
            border: 2px solid #00ff00;
            background: #1a1a1a;
            text-align: center;
        }
        .stats {
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
        }
        .stat-item {
            padding: 5px 15px;
            margin: 5px;
        }
        .stat-label {
            color: #888;
            font-size: 11px;
        }
        .stat-value {
            color: #00ffff;
            font-size: 18px;
            font-weight: bold;
        }
        button {
            background: #1a1a1a;
            border: 1px solid #00ff00;
            color: #00ff00;
            padding: 8px 15px;
            margin: 5px;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            transition: all 0.3s;
        }
        button:hover {
            background: #00ff00;
            color: #000;
            box-shadow: 0 0 10px #00ff00;
        }
        button:active {
            transform: scale(0.95);
        }
        .blink {
            animation: blink 1s infinite;
        }
        @keyframes blink {
            0%, 50%, 100% { opacity: 1; }
            25%, 75% { opacity: 0.5; }
        }
        .pulse {
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏰 DROS DELNOCH COMMAND CENTER 🏰</h1>
        <div class="subtitle">"The Fortress That Never Fell"</div>
        <div class="subtitle">Keeper: <span style="color:#00ffff">Vaktrinn Vigr Eldurhýarta</span></div>
    </div>

    <div class="main-container">
        <div class="sidebar">
            <h3>⚔️ Defense Systems</h3>
            <div class="system-status" id="system-status">
                <!-- Systems populated by JS -->
            </div>

            <h3>⌨️ Quick Keys</h3>
            <div class="quick-keys">
                <div class="quick-key">
                    <span class="key-binding">F1</span>
                    <span>Start Dros Delnoch</span>
                </div>
                <div class="quick-key">
                    <span class="key-binding">F2</span>
                    <span>Phase Fields</span>
                </div>
                <div class="quick-key">
                    <span class="key-binding">F3</span>
                    <span>Necrodermis</span>
                </div>
                <div class="quick-key">
                    <span class="key-binding">F4</span>
                    <span>Thyra Protection</span>
                </div>
                <div class="quick-key">
                    <span class="key-binding">F5</span>
                    <span>Firmware Flood</span>
                </div>
                <div class="quick-key">
                    <span class="key-binding">F6</span>
                    <span>Stop All</span>
                </div>
                <div class="quick-key">
                    <span class="key-binding">F7</span>
                    <span>Status All</span>
                </div>
                <div class="quick-key">
                    <span class="key-binding">F8</span>
                    <span>Self-Repair</span>
                </div>
                <div class="quick-key">
                    <span class="key-binding">F9</span>
                    <span>Emergency Lock</span>
                </div>
                <div class="quick-key">
                    <span class="key-binding">F10</span>
                    <span>Restart All</span>
                </div>
            </div>

            <div style="margin-top: 20px;">
                <button onclick="startAll()">🚀 Launch All</button>
                <button onclick="stopAll()">🛑 Stop All</button>
                <button onclick="refreshStatus()">🔄 Refresh</button>
            </div>
        </div>

        <div class="terminals-container">
            <div class="terminal">
                <div class="terminal-header">
                    Terminal 1: Dros Delnoch
                </div>
                <div class="terminal-content" id="terminal1"></div>
            </div>
            <div class="terminal">
                <div class="terminal-header">
                    Terminal 2: Phase Fields
                </div>
                <div class="terminal-content" id="terminal2"></div>
            </div>
            <div class="terminal">
                <div class="terminal-header">
                    Terminal 3: Necrodermis
                </div>
                <div class="terminal-content" id="terminal3"></div>
            </div>
            <div class="terminal">
                <div class="terminal-header">
                    Terminal 4: System Monitor
                </div>
                <div class="terminal-content" id="terminal4"></div>
            </div>
        </div>
    </div>

    <div class="footer">
        <div class="stats">
            <div class="stat-item">
                <div class="stat-label">Valkyries</div>
                <div class="stat-value" id="valkyries-count">0</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Targets Painted</div>
                <div class="stat-value" id="targets-painted">0</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Targets Eliminated</div>
                <div class="stat-value" id="targets-eliminated">0</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Phase Shields</div>
                <div class="stat-value pulse" id="phase-shields">ACTIVE</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Kernels</div>
                <div class="stat-value pulse" id="kernels">DANCING</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">System Health</div>
                <div class="stat-value" id="system-health">100%</div>
            </div>
        </div>
    </div>

    <script>
        const socket = io();

        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            if (e.key === 'F1') { e.preventDefault(); executeQuickKey('start_dros_delnoch'); }
            else if (e.key === 'F2') { e.preventDefault(); executeQuickKey('start_phase_fields'); }
            else if (e.key === 'F3') { e.preventDefault(); executeQuickKey('start_necrodermis'); }
            else if (e.key === 'F4') { e.preventDefault(); executeQuickKey('start_thyra'); }
            else if (e.key === 'F5') { e.preventDefault(); executeQuickKey('firmware_flood'); }
            else if (e.key === 'F6') { e.preventDefault(); stopAll(); }
            else if (e.key === 'F7') { e.preventDefault(); refreshStatus(); }
            else if (e.key === 'F8') { e.preventDefault(); executeQuickKey('self_repair_all'); }
            else if (e.key === 'F9') { e.preventDefault(); executeQuickKey('emergency_lockdown'); }
            else if (e.key === 'F10') { e.preventDefault(); executeQuickKey('restart_all'); }
        });

        function executeQuickKey(action) {
            socket.emit('quick_key', {action: action});
            appendLog('terminal4', `⚡ Executing: ${action}`, 'info');
        }

        function startAll() {
            socket.emit('control', {action: 'start_all'});
        }

        function stopAll() {
            socket.emit('control', {action: 'stop_all'});
        }

        function refreshStatus() {
            socket.emit('request_status');
        }

        function appendLog(terminalId, text, level='info') {
            const terminal = document.getElementById(terminalId);
            const line = document.createElement('div');
            line.className = `log-line log-${level}`;
            line.textContent = `[${new Date().toLocaleTimeString()}] ${text}`;
            terminal.appendChild(line);
            terminal.scrollTop = terminal.scrollHeight;

            // Keep only last 100 lines
            while (terminal.children.length > 100) {
                terminal.removeChild(terminal.firstChild);
            }
        }

        // Socket events
        socket.on('connect', function() {
            appendLog('terminal4', '🏰 Connected to Dros Delnoch Command Center', 'info');
            refreshStatus();
        });

        socket.on('log', function(data) {
            appendLog(data.terminal, data.message, data.level);
        });

        socket.on('status_update', function(data) {
            updateSystemStatus(data);
        });

        socket.on('stats_update', function(data) {
            if (data.valkyries) document.getElementById('valkyries-count').textContent = data.valkyries;
            if (data.targets_painted) document.getElementById('targets-painted').textContent = data.targets_painted;
            if (data.targets_eliminated) document.getElementById('targets-eliminated').textContent = data.targets_eliminated;
            if (data.phase_shields !== undefined) {
                const elem = document.getElementById('phase-shields');
                elem.textContent = data.phase_shields ? 'ACTIVE' : 'BREACHED';
                elem.style.color = data.phase_shields ? '#00ff00' : '#ff0000';
            }
            if (data.kernels !== undefined) {
                const elem = document.getElementById('kernels');
                elem.textContent = data.kernels ? 'DANCING' : 'STATIC';
                elem.style.color = data.kernels ? '#00ff00' : '#ff0000';
            }
            if (data.system_health !== undefined) {
                document.getElementById('system-health').textContent = data.system_health + '%';
            }
        });

        function updateSystemStatus(systems) {
            const container = document.getElementById('system-status');
            container.innerHTML = '';

            for (const [name, status] of Object.entries(systems)) {
                const div = document.createElement('div');
                div.className = `system-item ${status.running ? 'running' : 'stopped'}`;
                div.innerHTML = `
                    <div class="system-name">${name.replace(/_/g, ' ').toUpperCase()}</div>
                    <div class="system-state">${status.running ? '✓ RUNNING' : '✗ STOPPED'}</div>
                `;
                container.appendChild(div);
            }
        }

        // Auto-refresh every 2 seconds
        setInterval(refreshStatus, 2000);
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Serve dashboard"""
    return render_template_string(HTML_DASHBOARD)


@socketio.on('connect')
def handle_connect():
    """Client connected"""
    logging.info("Client connected to dashboard")
    emit('log', {
        'terminal': 'terminal4',
        'message': '🏰 Command Center online',
        'level': 'info'
    })
    send_status_update()


@socketio.on('request_status')
def handle_status_request():
    """Send current status"""
    send_status_update()


@socketio.on('control')
def handle_control(data):
    """Handle control commands"""
    action = data.get('action')
    logging.info(f"Control action: {action}")

    if action == 'start_all':
        start_system('dros_delnoch')
        start_system('phase_fields')
        start_system('necrodermis')
    elif action == 'stop_all':
        stop_all_systems()

    send_status_update()


@socketio.on('quick_key')
def handle_quick_key(data):
    """Handle quick key commands"""
    action = data.get('action')
    logging.info(f"Quick key: {action}")

    if action == 'start_dros_delnoch':
        start_system('dros_delnoch')
    elif action == 'start_phase_fields':
        start_system('phase_fields')
    elif action == 'start_necrodermis':
        start_system('necrodermis')
    elif action == 'start_thyra':
        start_system('thyra')
    elif action == 'firmware_flood':
        start_system('firmware_flooding')
    elif action == 'self_repair_all':
        self_repair_all()
    elif action == 'emergency_lockdown':
        emergency_lockdown()
    elif action == 'restart_all':
        restart_all()

    send_status_update()


def start_system(system_name):
    """Start a defense system"""
    script_map = {
        'dros_delnoch': 'DrosDelnoch.py',
        'phase_fields': 'PhaseFieldProtection.py',
        'necrodermis': 'NecrodermisRepair.py',
        'thyra': 'Thyra.py',
        'firmware_flooding': 'FirmwareFlooding.py',
        'lethani_brain': 'LethaniBrainAutonomous.py'
    }

    script = script_map.get(system_name)
    if not script:
        return

    script_path = Path(__file__).parent / script

    if not script_path.exists():
        socketio.emit('log', {
            'terminal': 'terminal4',
            'message': f'❌ {script} not found',
            'level': 'error'
        })
        return

    try:
        # Start in background
        proc = subprocess.Popen(
            ['python3', str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=script_path.parent
        )

        system_status[system_name]['running'] = True
        system_status[system_name]['pid'] = proc.pid

        socketio.emit('log', {
            'terminal': 'terminal1' if 'dros' in system_name else 'terminal2',
            'message': f'✅ Started {system_name} (PID: {proc.pid})',
            'level': 'info'
        })

    except Exception as e:
        logging.error(f"Failed to start {system_name}: {e}")
        socketio.emit('log', {
            'terminal': 'terminal4',
            'message': f'❌ Failed to start {system_name}: {e}',
            'level': 'error'
        })


def stop_all_systems():
    """Stop all running systems"""
    for system_name, status in system_status.items():
        if status['running'] and status['pid']:
            try:
                proc = psutil.Process(status['pid'])
                proc.terminate()
                status['running'] = False
                status['pid'] = None

                socketio.emit('log', {
                    'terminal': 'terminal4',
                    'message': f'🛑 Stopped {system_name}',
                    'level': 'warning'
                })
            except:
                pass


def self_repair_all():
    """Trigger self-repair on all systems"""
    socketio.emit('log', {
        'terminal': 'terminal3',
        'message': '🔷 Triggering Necrodermis self-repair on all systems...',
        'level': 'warning'
    })


def emergency_lockdown():
    """Emergency lockdown"""
    socketio.emit('log', {
        'terminal': 'terminal4',
        'message': '🚨 EMERGENCY LOCKDOWN INITIATED',
        'level': 'critical'
    })
    stop_all_systems()


def restart_all():
    """Restart all systems"""
    socketio.emit('log', {
        'terminal': 'terminal4',
        'message': '🔄 Restarting all systems...',
        'level': 'warning'
    })
    stop_all_systems()
    time.sleep(2)
    start_system('dros_delnoch')
    start_system('phase_fields')
    start_system('necrodermis')


def send_status_update():
    """Send status update to clients"""
    socketio.emit('status_update', system_status)

    # Send stats
    socketio.emit('stats_update', {
        'valkyries': 10,
        'targets_painted': 0,
        'targets_eliminated': 0,
        'phase_shields': True,
        'kernels': True,
        'system_health': 100
    })


if __name__ == "__main__":
    import time

    print("""
    ═══════════════════════════════════════════════════════════════════
    🏰 DROS DELNOCH COMMAND CENTER 🏰

    Web-based dashboard for monitoring and controlling all defense systems

    Features:
    - Real-time status monitoring
    - 4 terminal windows for multitasking
    - Quick keys (F1-F10) for instant control
    - Live system logs
    - Statistics tracking

    Quick Keys:
    F1  - Start Dros Delnoch        F6  - Stop All
    F2  - Phase Fields              F7  - Status All
    F3  - Necrodermis               F8  - Self-Repair All
    F4  - Thyra Protection          F9  - Emergency Lockdown
    F5  - Firmware Flood            F10 - Restart All

    Access: http://localhost:8888

    "The fortress that never fell"
    ═══════════════════════════════════════════════════════════════════
    """)

    logging.info("🏰 Starting Dros Delnoch Command Center...")
    logging.info("   Dashboard: http://localhost:8888")
    logging.info("   Press Ctrl+C to stop")

    try:
        socketio.run(app, host='0.0.0.0', port=8888, debug=False)
    except KeyboardInterrupt:
        logging.info("\n🏰 Command Center shutting down...")
        stop_all_systems()
