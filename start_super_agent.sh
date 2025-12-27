#!/bin/bash
# APEX-OMEGA TITAN: Super Agent Startup Script
# =============================================

set -e

echo "================================"
echo "🤖 TITAN SUPER AGENT SYSTEM"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python
echo -n "Checking Python... "
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "${GREEN}✓${NC} $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python 3 not found"
    exit 1
fi

# Check Node.js
echo -n "Checking Node.js... "
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version 2>&1)
    echo -e "${GREEN}✓${NC} $NODE_VERSION"
else
    echo -e "${YELLOW}⚠${NC} Node.js not found (optional for full features)"
fi

# Create logs directory if it doesn't exist
mkdir -p logs

echo ""
echo "Starting Super Agent Manager..."
echo "================================"
echo ""

# Parse command line arguments
MODE="${1:-interactive}"
ACTION="${2:-}"
SYSTEM_MODE="${3:-paper}"

# Run the super agent manager
if [ "$MODE" = "interactive" ]; then
    python3 agents/super_agent_manager.py --mode interactive
elif [ "$MODE" = "daemon" ]; then
    echo "Starting in daemon mode..."
    nohup python3 agents/super_agent_manager.py --mode daemon > logs/super_agent_daemon.log 2>&1 &
    echo "Super Agent daemon started with PID: $!"
    echo "Check logs/super_agent_daemon.log for output"
elif [ "$MODE" = "once" ]; then
    if [ -z "$ACTION" ]; then
        echo -e "${RED}Error:${NC} Action required for 'once' mode"
        echo "Usage: $0 once <action> [system-mode]"
        echo "Actions: health, start, stop, test, build, status"
        exit 1
    fi
    python3 agents/super_agent_manager.py --mode once --action "$ACTION" --system-mode "$SYSTEM_MODE"
else
    echo -e "${RED}Error:${NC} Unknown mode: $MODE"
    echo "Usage: $0 [interactive|daemon|once] [action] [system-mode]"
    exit 1
fi
