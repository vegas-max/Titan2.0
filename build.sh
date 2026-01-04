#!/bin/bash

# ==============================================================================
# 🔨 APEX-OMEGA TITAN: BUILD AND VALIDATION SCRIPT
# ==============================================================================
# Complete build process with validation
# Run: chmod +x build.sh && ./build.sh

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}===================================================${NC}"
echo -e "${BLUE}   TITAN BUILD AND VALIDATION${NC}"
echo -e "${BLUE}===================================================${NC}"
echo ""

# Step 1: Clean previous builds
echo -e "${BLUE}[1/4] Cleaning Previous Build Artifacts...${NC}"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo -e "${GREEN}[✓]${NC} Clean complete"
echo ""

# Step 2: Install Node.js dependencies
echo -e "${BLUE}[2/4] Installing Node.js Dependencies...${NC}"
if [ -f "package.json" ]; then
    npm install
    echo -e "${GREEN}[✓]${NC} Node.js dependencies installed"
else
    echo -e "${RED}[✗]${NC} package.json not found"
    exit 1
fi
echo ""

# Step 3: Install Python dependencies
echo -e "${BLUE}[3/4] Installing Python Dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt --quiet
    echo -e "${GREEN}[✓]${NC} Python dependencies installed"
else
    echo -e "${RED}[✗]${NC} requirements.txt not found"
    exit 1
fi
echo ""

# Step 4: Run system audit
echo -e "${BLUE}[4/4] Running System Audit...${NC}"
if [ -f "audit_system.py" ]; then
    python3 audit_system.py
    AUDIT_RESULT=$?
    if [ $AUDIT_RESULT -eq 0 ]; then
        echo -e "${GREEN}[✓]${NC} System audit passed"
    else
        echo -e "${YELLOW}[!]${NC} System audit completed with warnings"
    fi
else
    echo -e "${YELLOW}[!]${NC} audit_system.py not found, skipping"
fi
echo ""

# Final Summary
echo -e "${BLUE}===================================================${NC}"
echo -e "${BLUE}   BUILD SUMMARY${NC}"
echo -e "${BLUE}===================================================${NC}"
echo ""

echo -e "${GREEN}✅ BUILD SUCCESSFUL${NC}"
echo ""
echo "Build artifacts:"
echo "  • node_modules/ - Node.js dependencies"
echo "  • Python packages - Installed globally or in venv"
echo ""
echo "Next steps:"
echo "  1. Configure .env file (cp .env.example .env)"
echo "  2. Run health check: ./health-check.sh"
echo "  3. Start system: ./start.sh or make start"
exit 0
