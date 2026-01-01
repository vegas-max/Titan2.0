#!/bin/bash

# ==============================================================================
# 🔄 Restart Titan Services on Oracle Cloud
# ==============================================================================
# This script restarts all Titan components on Oracle Cloud
# Usage: ./restart_oracle.sh
# ==============================================================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   🔄 Restarting Titan Services            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root (for systemd commands)
if [ "$EUID" -eq 0 ]; then 
    SUDO=""
else
    SUDO="sudo"
fi

# Redis is optional - restart if available
if systemctl list-unit-files | grep -q titan-redis.service; then
    echo -e "${YELLOW}[1/3]${NC} Restarting Redis (optional)..."
    if $SUDO systemctl restart titan-redis 2>/dev/null; then
        echo -e "${GREEN}  ✓${NC} Redis restarted successfully"
    else
        echo -e "${YELLOW}  ℹ${NC} Redis not configured (optional)"
    fi
    sleep 1
    echo ""
fi

# Restart Brain service
echo -e "${YELLOW}[2/3]${NC} Restarting Titan Brain..."
if $SUDO systemctl restart titan-brain; then
    echo -e "${GREEN}  ✓${NC} Brain restarted successfully"
    sleep 2
else
    echo -e "${RED}  ✗${NC} Failed to restart Brain"
    exit 1
fi
echo ""

# Restart Executor service
echo -e "${YELLOW}[3/3]${NC} Restarting Titan Executor..."
if $SUDO systemctl restart titan-executor; then
    echo -e "${GREEN}  ✓${NC} Executor restarted successfully"
else
    echo -e "${RED}  ✗${NC} Failed to restart Executor"
    exit 1
fi
echo ""

echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ Titan Restarted Successfully         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}📊 Next Steps:${NC}"
echo ""
echo -e "  ${YELLOW}Check status:${NC}"
echo "    ./status_oracle.sh"
echo ""
echo -e "  ${YELLOW}View logs:${NC}"
echo "    sudo journalctl -u titan-brain -f"
echo ""
