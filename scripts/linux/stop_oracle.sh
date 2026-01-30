#!/bin/bash

# ==============================================================================
# 🛑 Stop Titan Services on Oracle Cloud
# ==============================================================================
# This script stops all Titan components on Oracle Cloud
# Usage: ./stop_oracle.sh
# ==============================================================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   🛑 Stopping Titan Services              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root (for systemd commands)
if [ "$EUID" -eq 0 ]; then 
    SUDO=""
else
    SUDO="sudo"
fi

# Stop Executor first (depends on Brain)
echo -e "${YELLOW}[1/3]${NC} Stopping Titan Executor..."
if $SUDO systemctl stop titan-executor; then
    echo -e "${GREEN}  ✓${NC} Executor stopped successfully"
else
    echo -e "${YELLOW}  ⚠${NC} Executor may not have been running"
fi
echo ""

# Stop Brain
echo -e "${YELLOW}[2/3]${NC} Stopping Titan Brain..."
if $SUDO systemctl stop titan-brain; then
    echo -e "${GREEN}  ✓${NC} Brain stopped successfully"
else
    echo -e "${YELLOW}  ⚠${NC} Brain may not have been running"
fi
echo ""

# Redis is optional - stop if available
if systemctl list-unit-files | grep -q titan-redis.service; then
    echo -e "${YELLOW}[3/3]${NC} Stopping Redis (optional)..."
    if $SUDO systemctl stop titan-redis 2>/dev/null; then
        echo -e "${GREEN}  ✓${NC} Redis stopped successfully"
    else
        echo -e "${YELLOW}  ℹ${NC} Redis not running (optional)"
    fi
    echo ""
fi

echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ Titan Stopped Successfully           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}ℹ  Info:${NC}"
echo "  All Titan services have been stopped."
echo "  To start them again, run: ./start_oracle.sh"
echo ""
