#!/bin/bash
#
# Titan Comprehensive Simulation Launcher
# ========================================
#
# Full-scale updated comprehensive simulation system launcher with
# configurable timeframes and execution modes.
#
# Usage:
#   ./run_comprehensive_simulation.sh [OPTIONS]
#
# Options:
#   --days DAYS              Number of days (7, 14, 30, 60, 90) [default: 7]
#   --mode MODE              Execution mode (LIVE, PAPER, DRY_RUN) [default: PAPER]
#   --chain-id ID            Chain ID [default: 137]
#   --comprehensive          Enable all features (full simulation)
#   --help                   Show this help message
#
# Examples:
#   ./run_comprehensive_simulation.sh                           # Quick 7-day test
#   ./run_comprehensive_simulation.sh --days 30 --mode LIVE     # 30-day live simulation
#   ./run_comprehensive_simulation.sh --days 90 --comprehensive # Full 90-day comprehensive

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Default values
DAYS=7
MODE="PAPER"
CHAIN_ID=137
COMPREHENSIVE=false
MIN_PROFIT=5.0
MAX_GAS=500.0

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --days)
            DAYS="$2"
            shift 2
            ;;
        --mode)
            MODE="$2"
            shift 2
            ;;
        --chain-id)
            CHAIN_ID="$2"
            shift 2
            ;;
        --comprehensive)
            COMPREHENSIVE=true
            shift
            ;;
        --min-profit)
            MIN_PROFIT="$2"
            shift 2
            ;;
        --max-gas)
            MAX_GAS="$2"
            shift 2
            ;;
        --help)
            head -n 25 "$0" | tail -n 21
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Print banner
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  ████████╗██╗████████╗ █████╗ ███╗   ██╗${NC}"
echo -e "${CYAN}  ╚══██╔══╝██║╚══██╔══╝██╔══██╗████╗  ██║${NC}"
echo -e "${CYAN}     ██║   ██║   ██║   ███████║██╔██╗ ██║${NC}"
echo -e "${CYAN}     ██║   ██║   ██║   ██╔══██║██║╚██╗██║${NC}"
echo -e "${CYAN}     ██║   ██║   ██║   ██║  ██║██║ ╚████║${NC}"
echo -e "${CYAN}     ╚═╝   ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${MAGENTA}      COMPREHENSIVE SIMULATION SYSTEM${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Display configuration
echo -e "${CYAN}📋 Configuration:${NC}"
echo -e "   Days:          ${GREEN}${DAYS}${NC}"
echo -e "   Mode:          ${GREEN}${MODE}${NC}"
echo -e "   Chain ID:      ${GREEN}${CHAIN_ID}${NC}"
echo -e "   Min Profit:    ${GREEN}\$${MIN_PROFIT}${NC}"
echo -e "   Max Gas:       ${GREEN}${MAX_GAS} gwei${NC}"
if [ "$COMPREHENSIVE" = true ]; then
    echo -e "   Features:      ${GREEN}ALL ENABLED (Comprehensive Mode)${NC}"
else
    echo -e "   Features:      ${YELLOW}Standard${NC}"
fi
echo ""

# Validate mode
if [[ "$MODE" != "LIVE" && "$MODE" != "PAPER" && "$MODE" != "DRY_RUN" ]]; then
    echo -e "${RED}❌ Invalid mode: $MODE${NC}"
    echo -e "${YELLOW}   Valid modes: LIVE, PAPER, DRY_RUN${NC}"
    exit 1
fi

# Validate days
if [[ ! "$DAYS" =~ ^[0-9]+$ ]] || [ "$DAYS" -lt 1 ] || [ "$DAYS" -gt 365 ]; then
    echo -e "${RED}❌ Invalid days: $DAYS${NC}"
    echo -e "${YELLOW}   Days must be between 1 and 365${NC}"
    exit 1
fi

# Warn for LIVE mode
if [ "$MODE" = "LIVE" ]; then
    echo -e "${YELLOW}⚠️  WARNING: Running in LIVE mode${NC}"
    echo -e "${YELLOW}   This will simulate actual execution with real-world constraints${NC}"
    echo -e "${YELLOW}   Press Ctrl+C within 5 seconds to cancel...${NC}"
    echo ""
    sleep 5
fi

# Check environment
echo -e "${CYAN}🔍 Checking environment...${NC}"

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  No .env file found${NC}"
    if [ -f .env.example ]; then
        echo -e "${YELLOW}   Creating from .env.example...${NC}"
        cp .env.example .env
        echo -e "${GREEN}   ✅ Created .env from example${NC}"
        echo -e "${YELLOW}   Please edit .env with your configuration${NC}"
    else
        echo -e "${RED}   ❌ No .env.example found${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ .env file found${NC}"
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python ${PYTHON_VERSION} found${NC}"

# Check/install dependencies
echo -e "${CYAN}📦 Checking dependencies...${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}   Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}   ✅ Virtual environment created${NC}"
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || true

# Install required packages
python3 -c "import pandas, numpy, dotenv" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}   Installing required packages...${NC}"
    pip install -q --upgrade pip
    pip install -q pandas numpy python-dotenv
    echo -e "${GREEN}   ✅ Packages installed${NC}"
else
    echo -e "${GREEN}✅ Required packages installed${NC}"
fi

# Check optional packages
python3 -c "import web3" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}   Optional: web3 not installed (real blockchain data unavailable)${NC}"
else
    echo -e "${GREEN}✅ Optional: web3 installed${NC}"
fi

# Create output directories
echo -e "${CYAN}📁 Creating output directories...${NC}"
mkdir -p data/comprehensive_simulation_results
mkdir -p data/historical_cache
mkdir -p logs/comprehensive_simulation
echo -e "${GREEN}✅ Directories ready${NC}"

# Build command
CMD="python3 comprehensive_simulation.py"
CMD="$CMD --days $DAYS"
CMD="$CMD --mode $MODE"
CMD="$CMD --chain-id $CHAIN_ID"
CMD="$CMD --min-profit $MIN_PROFIT"
CMD="$CMD --max-gas $MAX_GAS"

if [ "$COMPREHENSIVE" = true ]; then
    CMD="$CMD --comprehensive"
fi

# Run simulation
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}🚀 STARTING COMPREHENSIVE SIMULATION${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Record start time
START_TIME=$(date +%s)

# Execute simulation
$CMD

# Calculate runtime
END_TIME=$(date +%s)
RUNTIME=$((END_TIME - START_TIME))
HOURS=$((RUNTIME / 3600))
MINUTES=$(((RUNTIME % 3600) / 60))
SECONDS=$((RUNTIME % 60))

# Check if successful
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ SIMULATION COMPLETED SUCCESSFULLY!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Display runtime
    echo -e "${CYAN}⏱️  Runtime:${NC}"
    if [ $HOURS -gt 0 ]; then
        echo -e "   ${GREEN}${HOURS}h ${MINUTES}m ${SECONDS}s${NC}"
    elif [ $MINUTES -gt 0 ]; then
        echo -e "   ${GREEN}${MINUTES}m ${SECONDS}s${NC}"
    else
        echo -e "   ${GREEN}${SECONDS}s${NC}"
    fi
    echo ""
    
    # Display output locations
    echo -e "${CYAN}📁 Results Location:${NC}"
    echo -e "   ${GREEN}data/comprehensive_simulation_results/${NC}"
    echo ""
    
    # Find and display latest files
    echo -e "${CYAN}📄 Output Files:${NC}"
    
    LATEST_REPORT=$(ls -t data/comprehensive_simulation_results/REPORT_*.md 2>/dev/null | head -1)
    if [ -n "$LATEST_REPORT" ]; then
        echo -e "   📊 Report:        ${GREEN}${LATEST_REPORT}${NC}"
    fi
    
    LATEST_SUMMARY=$(ls -t data/comprehensive_simulation_results/summary_*.json 2>/dev/null | head -1)
    if [ -n "$LATEST_SUMMARY" ]; then
        echo -e "   📈 Summary:       ${GREEN}${LATEST_SUMMARY}${NC}"
    fi
    
    LATEST_DAILY=$(ls -t data/comprehensive_simulation_results/daily_metrics_*.csv 2>/dev/null | head -1)
    if [ -n "$LATEST_DAILY" ]; then
        echo -e "   📅 Daily Metrics: ${GREEN}${LATEST_DAILY}${NC}"
    fi
    
    LATEST_TRADES=$(ls -t data/comprehensive_simulation_results/trades_*.csv 2>/dev/null | head -1)
    if [ -n "$LATEST_TRADES" ]; then
        echo -e "   💱 Trades:        ${GREEN}${LATEST_TRADES}${NC}"
    fi
    
    LATEST_LOG=$(ls -t logs/comprehensive_simulation/sim_*.log 2>/dev/null | head -1)
    if [ -n "$LATEST_LOG" ]; then
        echo -e "   📝 Log File:      ${GREEN}${LATEST_LOG}${NC}"
    fi
    
    echo ""
    
    # Display quick summary
    if [ -n "$LATEST_SUMMARY" ]; then
        echo -e "${CYAN}📊 Quick Summary:${NC}"
        python3 -c "
import json
try:
    with open('$LATEST_SUMMARY') as f:
        data = json.load(f)
    print(f\"   Total Opportunities: {data.get('total_opportunities', 0):,}\")
    print(f\"   Total Executed:      {data.get('total_executed', 0):,}\")
    print(f\"   Success Rate:        {data.get('overall_success_rate', 0) * 100:.2f}%\")
    print(f\"   Total Net Profit:    \${data.get('total_net_profit', 0):,.2f}\")
except:
    pass
" 2>/dev/null
        echo ""
    fi
    
    # Next steps
    echo -e "${CYAN}🎯 Next Steps:${NC}"
    echo -e "   1. Review the generated report (Markdown file)"
    echo -e "   2. Analyze daily metrics (CSV file)"
    echo -e "   3. Examine individual trades (CSV file)"
    echo -e "   4. Check logs for detailed execution info"
    echo ""
    
    # Tips
    echo -e "${CYAN}💡 Tips:${NC}"
    echo -e "   • Run with --comprehensive for full feature set"
    echo -e "   • Use --mode DRY_RUN for validation without execution"
    echo -e "   • Increase --days for longer simulations (up to 90)"
    echo -e "   • Try different --chain-id values for other networks"
    echo ""
    
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    
    exit 0
else
    echo ""
    echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}❌ SIMULATION FAILED${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}Please check the log file for details:${NC}"
    LATEST_LOG=$(ls -t logs/comprehensive_simulation/sim_*.log 2>/dev/null | head -1)
    if [ -n "$LATEST_LOG" ]; then
        echo -e "   ${YELLOW}${LATEST_LOG}${NC}"
    fi
    echo ""
    exit 1
fi
