#!/bin/bash

# ==============================================================================
# 🩺 Oracle Cloud Health Check Script
# ==============================================================================
# Comprehensive health check for Titan running on Oracle Cloud
# Usage: ./oracle_health_check.sh
# ==============================================================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Titan Oracle Cloud Health Check        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Function to print status
check_ok() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Counter for issues
ISSUES=0

# 1. Check System Resources
echo -e "${BLUE}[1] System Resources${NC}"
echo "-------------------"

# Memory
TOTAL_MEM=$(free -h | grep Mem: | awk '{print $2}')
USED_MEM=$(free -h | grep Mem: | awk '{print $3}')
MEM_PERCENT=$(free | grep Mem | awk '{print int($3/$2 * 100)}')

echo "Memory: $USED_MEM / $TOTAL_MEM ($MEM_PERCENT% used)"
if [ $MEM_PERCENT -lt 80 ]; then
    check_ok "Memory usage healthy"
elif [ $MEM_PERCENT -lt 90 ]; then
    check_warn "Memory usage high: ${MEM_PERCENT}%"
    ((ISSUES++))
else
    check_fail "Memory usage critical: ${MEM_PERCENT}%"
    ((ISSUES++))
fi

# Disk
DISK_PERCENT=$(df -h / | tail -1 | awk '{print int($5)}')
echo "Disk: $(df -h / | tail -1 | awk '{print $3 " / " $2}') ($DISK_PERCENT% used)"
if [ $DISK_PERCENT -lt 80 ]; then
    check_ok "Disk usage healthy"
else
    check_warn "Disk usage high: ${DISK_PERCENT}%"
    ((ISSUES++))
fi

# CPU Load
CPU_LOAD=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}')
echo "CPU Load: $CPU_LOAD"
check_ok "CPU load: $CPU_LOAD"

echo ""

# 2. Check Dependencies
echo -e "${BLUE}[2] Dependencies${NC}"
echo "-------------------"

# Node.js
if command -v node >/dev/null 2>&1; then
    NODE_VERSION=$(node -v)
    check_ok "Node.js: $NODE_VERSION"
else
    check_fail "Node.js not found"
    ((ISSUES++))
fi

# Python
if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version)
    check_ok "Python: $PYTHON_VERSION"
else
    check_fail "Python not found"
    ((ISSUES++))
fi

# Redis (OPTIONAL - Titan uses file-based signals)
if command -v redis-cli >/dev/null 2>&1; then
    if redis-cli ping >/dev/null 2>&1; then
        check_ok "Redis: Running (optional)"
    else
        check_warn "Redis: Not responding (optional - not required)"
    fi
else
    check_ok "Redis: Not installed (optional - Titan uses file-based signals)"
fi

echo ""

# 3. Check Titan Services
echo -e "${BLUE}[3] Titan Services${NC}"
echo "-------------------"

# Check if systemd services exist
if systemctl list-unit-files | grep -q titan-brain.service; then
    # Check brain service
    if systemctl is-active --quiet titan-brain; then
        check_ok "Titan Brain: Running"
    else
        check_fail "Titan Brain: Not running"
        ((ISSUES++))
    fi
    
    # Check executor service
    if systemctl is-active --quiet titan-executor; then
        check_ok "Titan Executor: Running"
    else
        check_fail "Titan Executor: Not running"
        ((ISSUES++))
    fi
else
    check_warn "Systemd services not installed (may be running manually)"
fi

echo ""

# 4. Check Configuration
echo -e "${BLUE}[4] Configuration${NC}"
echo "-------------------"

# Check .env file
if [ -f ".env" ]; then
    check_ok ".env file exists"
    
    # Check if PRIVATE_KEY is set and not empty/placeholder
    if grep -q "^PRIVATE_KEY=" .env && ! grep -q "^PRIVATE_KEY=$" .env && ! grep -q "^PRIVATE_KEY=\s*$" .env && ! grep -q "^PRIVATE_KEY=YOUR" .env; then
        check_ok "Private key configured"
    else
        check_warn "Private key not configured in .env"
        ((ISSUES++))
    fi
    
    # Check if RPC endpoints are set
    if grep -q "^RPC_POLYGON=" .env && ! grep -q "YOUR_INFURA" .env; then
        check_ok "RPC endpoints configured"
    else
        check_warn "RPC endpoints not fully configured"
        ((ISSUES++))
    fi
else
    check_fail ".env file not found"
    ((ISSUES++))
fi

# Check config.json
if [ -f "config.json" ]; then
    check_ok "config.json exists"
else
    check_warn "config.json not found"
fi

echo ""

# 5. Check Network Connectivity
echo -e "${BLUE}[5] Network Connectivity${NC}"
echo "-------------------"

# Check internet connectivity
if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
    check_ok "Internet connectivity"
else
    check_fail "No internet connectivity"
    ((ISSUES++))
fi

# Check RPC connectivity (if .env is configured)
if [ -f ".env" ]; then
    if grep -q "^RPC_POLYGON=" .env; then
        RPC_URL=$(grep "^RPC_POLYGON=" .env | cut -d'=' -f2)
        if [ ! -z "$RPC_URL" ] && [[ ! "$RPC_URL" =~ "YOUR_INFURA" ]]; then
            if curl -s -X POST -H "Content-Type: application/json" \
                --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' \
                "$RPC_URL" | grep -q "result"; then
                check_ok "RPC endpoint reachable (Polygon)"
            else
                check_warn "RPC endpoint not responding (Polygon)"
                ((ISSUES++))
            fi
        fi
    fi
fi

echo ""

# 6. Check Signal Files (File-based Communication)
echo -e "${BLUE}[6] Signal Communication${NC}"
echo "-------------------"

# Check signals directory
if [ -d "signals/outgoing" ]; then
    SIGNAL_COUNT=$(find signals/outgoing -name "*.json" 2>/dev/null | wc -l)
    echo "Signal files: $SIGNAL_COUNT"
    check_ok "File-based signal system active"
    
    # Check for recent signals (last 5 minutes)
    RECENT_SIGNALS=$(find signals/outgoing -name "*.json" -mmin -5 2>/dev/null | wc -l)
    if [ $RECENT_SIGNALS -gt 0 ]; then
        check_ok "Recent signals found ($RECENT_SIGNALS in last 5 minutes)"
    else
        check_warn "No recent signals (brain may be idle or starting)"
    fi
else
    check_warn "Signals directory not found (will be created on first run)"
fi

# Optional: Check Redis if installed
if redis-cli ping >/dev/null 2>&1; then
    echo ""
    echo "Redis Status (Optional):"
    KEYS_COUNT=$(redis-cli DBSIZE | awk '{print $2}')
    echo "Keys in Redis: $KEYS_COUNT"
    
    if [ $KEYS_COUNT -gt 0 ]; then
        check_ok "Redis has data"
    else
        check_ok "Redis is empty (not required for operation)"
    fi
    
    # Check memory usage
    REDIS_MEM=$(redis-cli INFO memory | grep used_memory_human | cut -d':' -f2 | tr -d '\r')
    echo "Redis memory: $REDIS_MEM"
fi

echo ""

# 7. Check Recent Logs
echo -e "${BLUE}[7] Recent Logs${NC}"
echo "-------------------"

if systemctl list-unit-files | grep -q titan-brain.service; then
    # Check for recent errors in brain
    BRAIN_ERRORS=$(journalctl -u titan-brain --since "1 hour ago" | grep -i error | wc -l)
    if [ $BRAIN_ERRORS -eq 0 ]; then
        check_ok "No errors in Brain logs (last hour)"
    else
        check_warn "Found $BRAIN_ERRORS errors in Brain logs (last hour)"
    fi
    
    # Check for recent errors in executor
    EXEC_ERRORS=$(journalctl -u titan-executor --since "1 hour ago" | grep -i error | wc -l)
    if [ $EXEC_ERRORS -eq 0 ]; then
        check_ok "No errors in Executor logs (last hour)"
    else
        check_warn "Found $EXEC_ERRORS errors in Executor logs (last hour)"
    fi
fi

echo ""

# 8. Summary
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Health Check Summary                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! System is healthy.${NC}"
    echo ""
    echo "You can view real-time logs with:"
    echo "  sudo journalctl -u titan-brain -f"
    echo "  sudo journalctl -u titan-executor -f"
else
    echo -e "${YELLOW}⚠ Found $ISSUES issue(s) that need attention.${NC}"
    echo ""
    echo "Review the warnings above and take action if needed."
    echo ""
    echo "Common fixes:"
    echo "  - Configure .env: nano .env"
    echo "  - Start services: ./start_oracle.sh"
    echo "  - Check logs: sudo journalctl -u titan-brain -n 50"
fi

echo ""
echo "For more help, see ORACLE_CLOUD_DEPLOYMENT.md"
echo ""

# Exit with 0 for success (no issues), 1 for failure (issues found)
if [ $ISSUES -eq 0 ]; then
    exit 0
else
    exit 1
fi
