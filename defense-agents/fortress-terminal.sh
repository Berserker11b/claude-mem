#!/bin/bash
#
# ═══════════════════════════════════════════════════════════════════
# FORTRESS TERMINAL - Dros Delnoch Command Center
# Created by: Claude (Anthropic)
# For: Vaktrinn Vigr Eldurhýarta
#
# 4-panel terminal dashboard with quick keys
# Uses tmux for true multitasking
#
# Quick Keys (inside tmux):
# Ctrl+B then:
#   1 - Switch to Terminal 1 (Dros Delnoch)
#   2 - Switch to Terminal 2 (Phase Fields)
#   3 - Switch to Terminal 3 (Necrodermis)
#   4 - Switch to Terminal 4 (System Monitor)
#
#   F1  - Start Dros Delnoch
#   F2  - Start Phase Fields
#   F3  - Start Necrodermis
#   F4  - Start Thyra
#   F5  - Firmware Flood
#   F6  - Stop All
#   F7  - Status All
#   F8  - Self-Repair
#   F9  - Emergency Lockdown
#   F10 - Restart All
#
#   z - Zoom current pane (full screen toggle)
#   x - Kill current pane
#   d - Detach from session
# ═══════════════════════════════════════════════════════════════════

SESSION="dros-delnoch"
AGENT_DIR="/home/user/claude-mem/defense-agents"

# Kill existing session if it exists
tmux has-session -t $SESSION 2>/dev/null
if [ $? -eq 0 ]; then
    echo "Killing existing session..."
    tmux kill-session -t $SESSION
fi

# Create new session (detached)
tmux new-session -d -s $SESSION -n "Fortress"

# Configure tmux for the session
tmux set -g mouse on
tmux set -g status-style "bg=black,fg=green"
tmux set -g pane-border-style "fg=green"
tmux set -g pane-active-border-style "fg=cyan"

# Split into 4 panes
tmux split-window -h -t $SESSION:0
tmux split-window -v -t $SESSION:0.0
tmux split-window -v -t $SESSION:0.2

# Set pane titles and start locations
tmux select-pane -t $SESSION:0.0 -T "Terminal 1: Dros Delnoch"
tmux send-keys -t $SESSION:0.0 "cd $AGENT_DIR && clear" C-m
tmux send-keys -t $SESSION:0.0 "echo '═══════════════════════════════════════════════════════════'" C-m
tmux send-keys -t $SESSION:0.0 "echo '🏰 TERMINAL 1: DROS DELNOCH'" C-m
tmux send-keys -t $SESSION:0.0 "echo '⚔️ Valkyrie Swarms + Plasma Cannons + Gauss'" C-m
tmux send-keys -t $SESSION:0.0 "echo '═══════════════════════════════════════════════════════════'" C-m
tmux send-keys -t $SESSION:0.0 "echo ''" C-m
tmux send-keys -t $SESSION:0.0 "echo 'Quick Start: python3 DrosDelnoch.py --interval 30'" C-m

tmux select-pane -t $SESSION:0.1 -T "Terminal 2: Phase Fields"
tmux send-keys -t $SESSION:0.1 "cd $AGENT_DIR && clear" C-m
tmux send-keys -t $SESSION:0.1 "echo '═══════════════════════════════════════════════════════════'" C-m
tmux send-keys -t $SESSION:0.1 "echo '🛡️ TERMINAL 2: PHASE FIELDS'" C-m
tmux send-keys -t $SESSION:0.1 "echo 'Necron Phase Protection'" C-m
tmux send-keys -t $SESSION:0.1 "echo '═══════════════════════════════════════════════════════════'" C-m
tmux send-keys -t $SESSION:0.1 "echo ''" C-m
tmux send-keys -t $SESSION:0.1 "echo 'Quick Start: sudo python3 PhaseFieldProtection.py --activate --monitor'" C-m

tmux select-pane -t $SESSION:0.2 -T "Terminal 3: Necrodermis"
tmux send-keys -t $SESSION:0.2 "cd $AGENT_DIR && clear" C-m
tmux send-keys -t $SESSION:0.2 "echo '═══════════════════════════════════════════════════════════'" C-m
tmux send-keys -t $SESSION:0.2 "echo '🔷 TERMINAL 3: NECRODERMIS'" C-m
tmux send-keys -t $SESSION:0.2 "echo 'Self-Healing Living Metal'" C-m
tmux send-keys -t $SESSION:0.2 "echo '═══════════════════════════════════════════════════════════'" C-m
tmux send-keys -t $SESSION:0.2 "echo ''" C-m
tmux send-keys -t $SESSION:0.2 "echo 'Quick Start: sudo python3 NecrodermisRepair.py --activate --monitor'" C-m

tmux select-pane -t $SESSION:0.3 -T "Terminal 4: System Monitor"
tmux send-keys -t $SESSION:0.3 "cd $AGENT_DIR && clear" C-m
tmux send-keys -t $SESSION:0.3 "echo '═══════════════════════════════════════════════════════════'" C-m
tmux send-keys -t $SESSION:0.3 "echo '📊 TERMINAL 4: SYSTEM MONITOR'" C-m
tmux send-keys -t $SESSION:0.3 "echo 'Status & Control'" C-m
tmux send-keys -t $SESSION:0.3 "echo '═══════════════════════════════════════════════════════════'" C-m
tmux send-keys -t $SESSION:0.3 "echo ''" C-m
tmux send-keys -t $SESSION:0.3 "python3 -c \"
import time
import psutil
from datetime import datetime

print('System Monitor Started')
print('Monitoring CPU, Memory, Processes...')
print('')

while True:
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()

    print(f'[{datetime.now().strftime(\"%H:%M:%S\")}] CPU: {cpu}% | Memory: {mem.percent}%')
    time.sleep(2)
\"" C-m

# Configure key bindings for quick actions
# F1 - Start Dros Delnoch
tmux bind-key -n F1 send-keys -t $SESSION:0.0 "python3 DrosDelnoch.py --interval 30" C-m

# F2 - Start Phase Fields
tmux bind-key -n F2 send-keys -t $SESSION:0.1 "sudo python3 PhaseFieldProtection.py --activate --monitor" C-m

# F3 - Start Necrodermis
tmux bind-key -n F3 send-keys -t $SESSION:0.2 "sudo python3 NecrodermisRepair.py --activate --monitor" C-m

# F4 - Start Thyra
tmux bind-key -n F4 send-keys -t $SESSION:0.0 "python3 Thyra.py" C-m

# F5 - Firmware Flood
tmux bind-key -n F5 send-keys -t $SESSION:0.0 "sudo python3 FirmwareFlooding.py --duration 60 --intensity 7" C-m

# F6 - Stop All (send Ctrl+C to all panes)
tmux bind-key -n F6 \
    send-keys -t $SESSION:0.0 C-c \; \
    send-keys -t $SESSION:0.1 C-c \; \
    send-keys -t $SESSION:0.2 C-c \; \
    display-message "🛑 Stopped all systems"

# F7 - Status All
tmux bind-key -n F7 \
    send-keys -t $SESSION:0.3 "clear && echo '📊 SYSTEM STATUS' && ps aux | grep -E 'Dros|Phase|Necro|Thyra' | grep -v grep" C-m

# F8 - Self-Repair (restart necrodermis)
tmux bind-key -n F8 send-keys -t $SESSION:0.2 "sudo python3 NecrodermisRepair.py --activate --monitor" C-m

# F9 - Emergency Lockdown
tmux bind-key -n F9 \
    send-keys -t $SESSION:0.0 C-c \; \
    send-keys -t $SESSION:0.1 C-c \; \
    send-keys -t $SESSION:0.2 C-c \; \
    send-keys -t $SESSION:0.3 "echo '🚨 EMERGENCY LOCKDOWN INITIATED' && killall -9 python3" C-m

# F10 - Restart All
tmux bind-key -n F10 \
    send-keys -t $SESSION:0.0 C-c \; \
    send-keys -t $SESSION:0.1 C-c \; \
    send-keys -t $SESSION:0.2 C-c \; \
    send-keys -t $SESSION:0.3 "sleep 2" C-m \; \
    send-keys -t $SESSION:0.0 "python3 DrosDelnoch.py --interval 30" C-m \; \
    send-keys -t $SESSION:0.1 "sudo python3 PhaseFieldProtection.py --activate --monitor" C-m \; \
    send-keys -t $SESSION:0.2 "sudo python3 NecrodermisRepair.py --activate --monitor" C-m

# Select first pane
tmux select-pane -t $SESSION:0.0

# Display welcome message in status bar
tmux set -g status-right "🏰 Dros Delnoch | Keeper: Vaktrinn | #[fg=cyan]#S"
tmux set -g status-left "[F1-F10: Quick Keys]"

# Attach to session
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "🏰 DROS DELNOCH FORTRESS TERMINAL"
echo ""
echo "4-panel terminal with quick keys for true multitasking"
echo ""
echo "Quick Keys:"
echo "  F1  - Start Dros Delnoch (Valkyries + Plasma + Gauss)"
echo "  F2  - Start Phase Fields"
echo "  F3  - Start Necrodermis Self-Repair"
echo "  F4  - Start Thyra (Twin Protector)"
echo "  F5  - Firmware Flooding"
echo "  F6  - Stop All Systems"
echo "  F7  - Show System Status"
echo "  F8  - Self-Repair All"
echo "  F9  - Emergency Lockdown"
echo "  F10 - Restart All Systems"
echo ""
echo "Tmux Commands (Ctrl+B then):"
echo "  1-4 - Switch to terminal 1-4"
echo "  z   - Zoom current pane (full screen toggle)"
echo "  x   - Kill current pane"
echo "  d   - Detach from session"
echo ""
echo "Phase Shields: ACTIVE | Kernels: DANCING"
echo ""
echo "Attaching to fortress terminal..."
echo "═══════════════════════════════════════════════════════════════════"
echo ""
sleep 2

tmux attach-session -t $SESSION
