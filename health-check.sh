#!/bin/bash

# ==============================================================================
# 🏥 APEX-OMEGA TITAN: SYSTEM HEALTH CHECK
# ==============================================================================
# Comprehensive health check for all system components
# Run: chmod +x health-check.sh && ./health-check.sh

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}===================================================${NC}"
echo -e "${BLUE}   TITAN SYSTEM HEALTH CHECK${NC}"
echo -e "${BLUE}===================================================${NC}"
echo ""

ERRORS=0
WARNINGS=0

# Function to check command
check_command() {
    if command -v $1 >/dev/null 2>&1; then
        echo -e "${GREEN}[✓]${NC} $2"
        return 0
    else
        echo -e "${RED}[✗]${NC} $2"
        ((ERRORS++))
        return 1
    fi
}

# Function to check file
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}[✓]${NC} $2"
        return 0
    else
        echo -e "${RED}[✗]${NC} $2"
        ((ERRORS++))
        return 1
    fi
}

# Function to check directory
check_directory() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}[✓]${NC} $2"
        return 0
    else
        echo -e "${YELLOW}[!]${NC} $2"
        ((WARNINGS++))
        return 1
    fi
}

# Check Prerequisites
echo -e "${BLUE}[1/7] Checking Prerequisites...${NC}"
check_command node "Node.js installed"
if command -v node >/dev/null 2>&1; then
    NODE_VERSION=$(node -v)
    echo "       Version: $NODE_VERSION"
fi

check_command python3 "Python 3 installed"
if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version)
    echo "       Version: $PYTHON_VERSION"
fi

check_command redis-server "Redis installed"
if command -v redis-server >/dev/null 2>&1; then
    REDIS_VERSION=$(redis-server --version | awk '{print $3}')
    echo "       Version: $REDIS_VERSION"
fi

check_command git "Git installed"
echo ""

# Check Required Files
echo -e "${BLUE}[2/7] Checking Required Files...${NC}"
check_file "package.json" "package.json exists"
check_file "requirements.txt" "requirements.txt exists"
check_file "hardhat.config.js" "hardhat.config.js exists"
check_file ".env" ".env configuration file exists"
check_file "contracts/OmniArbExecutor.sol" "Main smart contract exists"
check_file "ml/brain.py" "AI Brain module exists"
check_file "execution/bot.js" "Execution bot exists"
echo ""

# Check Dependencies
echo -e "${BLUE}[3/7] Checking Node.js Dependencies...${NC}"
if [ -d "node_modules" ]; then
    echo -e "${GREEN}[✓]${NC} node_modules directory exists"
    
    # Check key packages
    for pkg in ethers dotenv redis axios; do
        if [ -d "node_modules/$pkg" ]; then
            echo -e "${GREEN}[✓]${NC} $pkg installed"
        else
            echo -e "${RED}[✗]${NC} $pkg missing"
            ((ERRORS++))
        fi
    done
else
    echo -e "${RED}[✗]${NC} node_modules not found (run: npm install)"
    ((ERRORS++))
fi
echo ""

# Check Python Dependencies
echo -e "${BLUE}[4/7] Checking Python Dependencies...${NC}"
PYTHON_PACKAGES=("web3" "pandas" "numpy" "redis" "requests")
for pkg in "${PYTHON_PACKAGES[@]}"; do
    if python3 -c "import $pkg" 2>/dev/null; then
        echo -e "${GREEN}[✓]${NC} $pkg installed"
    else
        echo -e "${RED}[✗]${NC} $pkg missing"
        ((ERRORS++))
    fi
done
echo ""

# Check Compiled Contracts
echo -e "${BLUE}[5/7] Checking Compiled Contracts...${NC}"
if [ -d "artifacts" ]; then
    echo -e "${GREEN}[✓]${NC} Artifacts directory exists"
    if [ -f "artifacts/contracts/OmniArbExecutor.sol/OmniArbExecutor.json" ]; then
        echo -e "${GREEN}[✓]${NC} OmniArbExecutor compiled"
    else
        echo -e "${RED}[✗]${NC} OmniArbExecutor not compiled (run: npx hardhat compile)"
        ((ERRORS++))
    fi
else
    echo -e "${YELLOW}[!]${NC} Contracts not compiled (run: npx hardhat compile)"
    ((WARNINGS++))
fi
echo ""

# Check Redis Connection
echo -e "${BLUE}[6/7] Checking Redis Connection...${NC}"
if redis-cli ping >/dev/null 2>&1; then
    echo -e "${GREEN}[✓]${NC} Redis is running"
    REDIS_INFO=$(redis-cli INFO | grep -E "redis_version|uptime_in_seconds")
    echo "       $REDIS_INFO"
else
    echo -e "${YELLOW}[!]${NC} Redis is not running (start with: redis-server)"
    ((WARNINGS++))
fi
echo ""

# Check Environment Configuration
echo -e "${BLUE}[7/7] Checking Environment Configuration...${NC}"
if [ -f ".env" ]; then
    # Check for key variables (without revealing values)
    if grep -q "PRIVATE_KEY=" .env && ! grep -q "PRIVATE_KEY=0x0000000000000000000000000000000000000000000000000000000000000000" .env; then
        echo -e "${GREEN}[✓]${NC} PRIVATE_KEY configured"
    else
        echo -e "${YELLOW}[!]${NC} PRIVATE_KEY not configured or using default"
        ((WARNINGS++))
    fi
    
    if grep -q "RPC_POLYGON=" .env && ! grep -q "YOUR_" .env; then
        echo -e "${GREEN}[✓]${NC} RPC endpoints configured"
    else
        echo -e "${YELLOW}[!]${NC} RPC endpoints not configured"
        ((WARNINGS++))
    fi
    
    if grep -q "LIFI_API_KEY=" .env && ! grep -q "LIFI_API_KEY=$" .env; then
        echo -e "${GREEN}[✓]${NC} LIFI_API_KEY configured"
    else
        echo -e "${YELLOW}[!]${NC} LIFI_API_KEY not configured"
        ((WARNINGS++))
    fi
else
    echo -e "${RED}[✗]${NC} .env file not found"
    ((ERRORS++))
fi
echo ""

# Summary
echo -e "${BLUE}===================================================${NC}"
echo -e "${BLUE}   HEALTH CHECK SUMMARY${NC}"
echo -e "${BLUE}===================================================${NC}"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED${NC}"
    echo ""
    echo "Your system is ready to run!"
    echo "Start with: make start or ./start.sh"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  WARNINGS: $WARNINGS${NC}"
    echo ""
    echo "System can run but some features may be limited."
    echo "Review warnings above for details."
    exit 0
else
    echo -e "${RED}❌ ERRORS: $ERRORS${NC}"
    echo -e "${YELLOW}⚠️  WARNINGS: $WARNINGS${NC}"
    echo ""
    echo "System cannot run. Please fix errors above."
    echo ""
    echo "Common fixes:"
    echo "  - Run: npm install"
    echo "  - Run: pip3 install -r requirements.txt"
    echo "  - Run: npx hardhat compile"
    echo "  - Configure .env file"
    echo "  - Start Redis: redis-server"
    exit 1
fi
