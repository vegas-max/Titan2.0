#!/bin/bash

# ==============================================================================
# 📊 Titan Service Status on Oracle Cloud
# ==============================================================================
# This script shows the status of all Titan components
# Usage: ./status_oracle.sh
# ==============================================================================

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   📊 Titan Service Status                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root (for systemd commands)
if [ "$EUID" -eq 0 ]; then 
    SUDO=""
else
    SUDO="sudo"
fi

# Check if systemd services are installed
if ! systemctl list-unit-files | grep -q titan-brain.service; then
    echo -e "${YELLOW}⚠${NC} Systemd services not installed yet."
    echo "   Run: ./deploy_oracle_cloud.sh to set up services"
    exit 1
fi

# Redis is optional - show status if available
if systemctl list-unit-files | grep -q titan-redis.service; then
    echo -e "${YELLOW}Redis (Optional):${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    $SUDO systemctl status titan-redis --no-pager 2>/dev/null || echo "  Not configured (optional - Titan uses file-based signals)"
    echo ""
fi

echo -e "${YELLOW}Titan Brain (AI Engine):${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
$SUDO systemctl status titan-brain --no-pager
echo ""

echo -e "${YELLOW}Titan Executor (Trading Bot):${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
$SUDO systemctl status titan-executor --no-pager
echo ""

# Quick summary
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Quick Summary                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Function to check service status
check_service() {
    if $SUDO systemctl is-active --quiet $1; then
        echo -e "  ${GREEN}✓${NC} $2: ${GREEN}Running${NC}"
        return 0
    else
        echo -e "  ${YELLOW}✗${NC} $2: ${YELLOW}Stopped${NC}"
        return 1
    fi
}

RUNNING_COUNT=0

if systemctl list-unit-files | grep -q titan-redis.service; then
    if check_service titan-redis "Redis"; then
        ((RUNNING_COUNT++))
    fi
fi

if check_service titan-brain "Brain"; then
    ((RUNNING_COUNT++))
fi

if check_service titan-executor "Executor"; then
    ((RUNNING_COUNT++))
fi

echo ""

# Show useful commands
echo -e "${BLUE}Useful Commands:${NC}"
echo "  Start:   ./start_oracle.sh"
echo "  Stop:    ./stop_oracle.sh"
echo "  Restart: ./restart_oracle.sh"
echo "  Health:  ./oracle_health_check.sh"
echo ""
echo "  View logs:"
echo "    sudo journalctl -u titan-brain -f"
echo "    sudo journalctl -u titan-executor -f"
echo ""
