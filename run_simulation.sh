#!/bin/bash
#
# Quick launcher for Titan Robust 90-Day Live Simulation
#
# Usage:
#   ./run_simulation.sh              # Quick 7-day test in PAPER mode
#   ./run_simulation.sh live         # Quick 7-day test in LIVE mode
#   ./run_simulation.sh full         # Full 90-day simulation in LIVE mode
#   ./run_simulation.sh full paper   # Full 90-day simulation in PAPER mode

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  TITAN ROBUST 90-DAY SIMULATION LAUNCHER${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

# Parse arguments
MODE="PAPER"
QUICK_TEST="--quick-test"

if [ "$1" == "live" ]; then
    MODE="LIVE"
    echo -e "${YELLOW}⚠️  Running in LIVE mode${NC}"
elif [ "$1" == "full" ]; then
    QUICK_TEST=""
    if [ "$2" == "paper" ]; then
        MODE="PAPER"
    else
        MODE="LIVE"
    fi
    echo -e "${GREEN}Running full 90-day simulation${NC}"
else
    echo -e "${GREEN}Running quick 7-day test${NC}"
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  No .env file found${NC}"
    echo -e "${YELLOW}   Creating from .env.example...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}   ✅ Created .env from example${NC}"
    else
        echo -e "${YELLOW}   No .env.example found either${NC}"
    fi
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python 3 found${NC}"

# Check dependencies
echo -e "${BLUE}Checking dependencies...${NC}"
python3 -c "import pandas, numpy, web3" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Installing dependencies...${NC}"
    pip install -q pandas numpy web3 python-dotenv rustworkx scikit-learn
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${GREEN}✅ Dependencies OK${NC}"
fi

# Run simulation
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Starting simulation...${NC}"
echo -e "${BLUE}Mode: ${MODE}${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

python3 run_robust_90day_live_simulation.py --mode ${MODE} ${QUICK_TEST}

# Check if successful
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ Simulation completed successfully!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${BLUE}Results saved to:${NC}"
    echo -e "  📁 ${GREEN}data/robust_live_simulation_results/${NC}"
    echo ""
    echo -e "${BLUE}View the report:${NC}"
    LATEST_REPORT=$(ls -t data/robust_live_simulation_results/REPORT_*.md 2>/dev/null | head -1)
    if [ -n "$LATEST_REPORT" ]; then
        echo -e "  📄 ${GREEN}${LATEST_REPORT}${NC}"
    fi
    echo ""
    echo -e "${BLUE}Log files:${NC}"
    LATEST_LOG=$(ls -t logs/robust_90day_sim_*.log 2>/dev/null | head -1)
    if [ -n "$LATEST_LOG" ]; then
        echo -e "  📝 ${GREEN}${LATEST_LOG}${NC}"
    fi
    echo ""
else
    echo -e "${RED}❌ Simulation failed${NC}"
    exit 1
fi
