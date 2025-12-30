#!/bin/bash

# ==============================================================================
# 🚀 Start Titan Services on Oracle Cloud
# ==============================================================================
# This script starts all Titan components on Oracle Cloud
# Usage: ./start_oracle.sh
# ==============================================================================

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   🚀 Starting Titan Services              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root (for systemd commands)
if [ "$EUID" -eq 0 ]; then 
    SUDO=""
else
    SUDO="sudo"
fi

# Redis is optional - start if available
if systemctl list-unit-files | grep -q titan-redis.service; then
    echo -e "${YELLOW}[1/3]${NC} Starting Redis (optional)..."
    if $SUDO systemctl start titan-redis 2>/dev/null; then
        echo -e "${GREEN}  ✓${NC} Redis started successfully"
    else
        echo -e "${YELLOW}  ℹ${NC} Redis not configured (optional - Titan uses file-based signals)"
    fi
    sleep 1
    echo ""
fi

# Start Brain service
echo -e "${YELLOW}[2/3]${NC} Starting Titan Brain (AI Engine)..."
if $SUDO systemctl start titan-brain; then
    echo -e "${GREEN}  ✓${NC} Brain started successfully"
    sleep 2
else
    echo -e "${RED}  ✗${NC} Failed to start Brain"
    exit 1
fi
echo ""

# Start Executor service
echo -e "${YELLOW}[3/3]${NC} Starting Titan Executor (Trading Bot)..."
if $SUDO systemctl start titan-executor; then
    echo -e "${GREEN}  ✓${NC} Executor started successfully"
else
    echo -e "${RED}  ✗${NC} Failed to start Executor"
    exit 1
fi
echo ""

echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ Titan Started Successfully           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}📊 Next Steps:${NC}"
echo ""
echo -e "  ${YELLOW}1. Check status:${NC}"
echo "     ./status_oracle.sh"
echo ""
echo -e "  ${YELLOW}2. View real-time logs:${NC}"
echo "     sudo journalctl -u titan-brain -f"
echo "     sudo journalctl -u titan-executor -f"
echo ""
echo -e "  ${YELLOW}3. Run health check:${NC}"
echo "     ./oracle_health_check.sh"
echo ""
