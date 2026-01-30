#!/bin/bash
# APEX-OMEGA TITAN: Super Agent Boot Script
# ==========================================
# This script initializes the super agent system at boot time and
# performs a complete build including Rust engine construction.

set -e

echo "================================================================="
echo "🚀 TITAN SUPER AGENT BOOT SEQUENCE"
echo "================================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}Step 1: Checking system requirements...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 installed${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠ Node.js not found (optional)${NC}"
else
    echo -e "${GREEN}✓ Node.js installed${NC}"
fi

# Check Rust/Cargo
if ! command -v cargo &> /dev/null; then
    echo -e "${YELLOW}⚠ Rust/Cargo not found (Rust engine will be skipped)${NC}"
else
    echo -e "${GREEN}✓ Rust/Cargo installed${NC}"
fi

echo ""
echo -e "${BLUE}Step 2: Starting Super Agent System...${NC}"
echo ""

# Start the super agent in daemon mode
# This will automatically:
# 1. Initialize all agents
# 2. Run build (including Rust engine) if configured
# 3. Perform health checks
# 4. Start system components if configured

python3 agents/super_agent_manager.py --mode daemon &
SUPER_AGENT_PID=$!

echo -e "${GREEN}✓ Super Agent started with PID: $SUPER_AGENT_PID${NC}"
echo ""

# Wait a moment for initialization
sleep 2

# Check if the process is still running
if ps -p $SUPER_AGENT_PID > /dev/null; then
    echo -e "${GREEN}✅ Super Agent is running and managing the system${NC}"
    echo ""
    echo "System is now self-sufficient and will:"
    echo "  • Build Rust engine and smart contracts"
    echo "  • Monitor system health"
    echo "  • Auto-heal on failures"
    echo "  • Manage all components"
    echo ""
    echo "Check logs at: logs/super_agent_*.log"
    echo "Or daemon log: logs/super_agent_daemon.log"
    echo ""
else
    echo -e "${RED}✗ Super Agent failed to start${NC}"
    echo "Check logs for details"
    exit 1
fi

echo "================================================================="
echo -e "${GREEN}🎉 TITAN SUPER AGENT BOOT COMPLETE${NC}"
echo "================================================================="
