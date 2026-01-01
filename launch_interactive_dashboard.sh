#!/usr/bin/env bash
#
# TITAN Interactive Dashboard Launcher
# Starts the multi-page interactive dashboard server
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   🚀 TITAN Multi-Page Interactive Dashboard Launcher     ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
echo -e "${GREEN}✓ Python ${PYTHON_VERSION} found${NC}"

# Check for required Python packages
echo ""
echo -e "${YELLOW}Checking dependencies...${NC}"

MISSING_DEPS=()

# Check for aiohttp
if ! python3 -c "import aiohttp" 2>/dev/null; then
    MISSING_DEPS+=("aiohttp")
fi

# Check for aiohttp_cors
if ! python3 -c "import aiohttp_cors" 2>/dev/null; then
    MISSING_DEPS+=("aiohttp-cors")
fi

# Check for redis (optional)
if ! python3 -c "import redis" 2>/dev/null; then
    echo -e "${YELLOW}⚠  redis-py not found - dashboard will run in simulation mode${NC}"
fi

# Install missing dependencies
if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo -e "${YELLOW}Missing dependencies: ${MISSING_DEPS[*]}${NC}"
    echo -e "${YELLOW}Installing...${NC}"
    
    pip3 install "${MISSING_DEPS[@]}" || {
        echo -e "${RED}Failed to install dependencies${NC}"
        echo -e "${YELLOW}Please run manually: pip3 install ${MISSING_DEPS[*]}${NC}"
        exit 1
    }
    
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${GREEN}✓ All dependencies satisfied${NC}"
fi

# Check if Redis is running (optional)
echo ""
echo -e "${YELLOW}Checking Redis connection...${NC}"
if command -v redis-cli &> /dev/null && redis-cli ping &> /dev/null; then
    echo -e "${GREEN}✓ Redis is running - live data mode enabled${NC}"
    REDIS_STATUS="CONNECTED"
else
    echo -e "${YELLOW}⚠  Redis not running - dashboard will use simulation mode${NC}"
    echo -e "${YELLOW}   To connect to live system, start Redis: redis-server${NC}"
    REDIS_STATUS="SIMULATION"
fi

# Parse command line arguments
PORT=8080
HOST="0.0.0.0"

while [[ $# -gt 0 ]]; do
    case $1 in
        --port|-p)
            PORT="$2"
            shift 2
            ;;
        --host|-h)
            HOST="$2"
            shift 2
            ;;
        --help)
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --port, -p PORT    Port to bind to (default: 8080)"
            echo "  --host, -h HOST    Host to bind to (default: 0.0.0.0)"
            echo "  --help             Show this help message"
            echo ""
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Display configuration
echo ""
echo -e "${BLUE}Configuration:${NC}"
echo -e "  Host: ${GREEN}${HOST}${NC}"
echo -e "  Port: ${GREEN}${PORT}${NC}"
echo -e "  Redis: ${GREEN}${REDIS_STATUS}${NC}"

# Display access URLs
echo ""
echo -e "${BLUE}Dashboard will be available at:${NC}"
echo -e "  Local:   ${GREEN}http://localhost:${PORT}${NC}"
if [ "$HOST" = "0.0.0.0" ]; then
    # Try to get the local IP address
    if command -v hostname &> /dev/null; then
        LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
        if [ -n "$LOCAL_IP" ]; then
            echo -e "  Network: ${GREEN}http://${LOCAL_IP}:${PORT}${NC}"
        fi
    fi
fi

echo ""
echo -e "${BLUE}Features:${NC}"
echo -e "  ✓ Multi-page navigation (5 pages)"
echo -e "  ✓ Real-time market opportunity scanner"
echo -e "  ✓ Executable transaction queue"
echo -e "  ✓ Live execution monitor"
echo -e "  ✓ Performance analytics"
echo -e "  ✓ Interactive control buttons"
echo -e "  ✓ WebSocket live updates"

echo ""
echo -e "${YELLOW}Starting dashboard server...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""

# Start the dashboard server
python3 dashboard_server.py --host "$HOST" --port "$PORT"
