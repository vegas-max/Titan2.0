#!/bin/bash
# Titan 2.0 - Mainnet Dependency Installer
# This script installs all required dependencies for mainnet operation

set -e  # Exit on any error

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                 TITAN 2.0 DEPENDENCY INSTALLER                 ║${NC}"
echo -e "${CYAN}║            Preparing System for Mainnet Deployment             ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to print step
print_step() {
    echo -e "\n${BLUE}>>> $1${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if running with Python 3
print_step "Checking Python version"
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found. Please install Python 3.11 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_success "Python $PYTHON_VERSION found"

# Check if pip is available
print_step "Checking pip"
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 not found. Please install pip3."
    exit 1
fi
print_success "pip3 found"

# Check if Node.js is available
print_step "Checking Node.js version"
if ! command -v node &> /dev/null; then
    print_warning "Node.js not found. Install Node.js 18+ for execution layer."
else
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION found"
fi

# Install critical Python dependencies
print_step "Installing critical Python dependencies"
echo -e "${CYAN}Installing: web3, rustworkx${NC}"

pip3 install --upgrade pip
pip3 install web3>=6.0.0
print_success "web3 installed"

pip3 install rustworkx>=0.13.0
print_success "rustworkx installed"

# Install optional but recommended dependencies
print_step "Installing recommended Python dependencies"
echo -e "${CYAN}Installing: redis, websockets${NC}"

pip3 install redis>=5.0.0
print_success "redis installed"

pip3 install websockets>=10.0
print_success "websockets installed"

# Install additional dependencies from requirements.txt if it exists
if [ -f "requirements.txt" ]; then
    print_step "Installing remaining dependencies from requirements.txt"
    pip3 install -r requirements.txt
    print_success "Additional dependencies installed"
fi

# Install Node.js dependencies if package.json exists
if [ -f "package.json" ] && command -v npm &> /dev/null; then
    print_step "Installing Node.js dependencies"
    npm install
    print_success "Node.js dependencies installed"
elif [ -f "package.json" ]; then
    print_warning "package.json found but npm not available. Please install npm and run 'npm install'"
fi

# Create signals directories if they don't exist
print_step "Creating signal directories"
mkdir -p signals/outgoing
mkdir -p signals/incoming
mkdir -p signals/processed
print_success "Signal directories created"

# Verify installation
print_step "Verifying installation"

VERIFY_PASSED=0
VERIFY_FAILED=0

# Test web3
if python3 -c "import web3" 2>/dev/null; then
    print_success "web3 import test passed"
    VERIFY_PASSED=$((VERIFY_PASSED + 1))
else
    print_error "web3 import test failed"
    VERIFY_FAILED=$((VERIFY_FAILED + 1))
fi

# Test rustworkx
if python3 -c "import rustworkx" 2>/dev/null; then
    print_success "rustworkx import test passed"
    VERIFY_PASSED=$((VERIFY_PASSED + 1))
else
    print_error "rustworkx import test failed"
    VERIFY_FAILED=$((VERIFY_FAILED + 1))
fi

# Test redis (optional)
if python3 -c "import redis" 2>/dev/null; then
    print_success "redis import test passed"
    VERIFY_PASSED=$((VERIFY_PASSED + 1))
else
    print_warning "redis import test failed (optional)"
fi

# Test websockets (optional)
if python3 -c "import websockets" 2>/dev/null; then
    print_success "websockets import test passed"
    VERIFY_PASSED=$((VERIFY_PASSED + 1))
else
    print_warning "websockets import test failed (optional)"
fi

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                    INSTALLATION SUMMARY                        ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Verification Tests Passed: ${GREEN}$VERIFY_PASSED${NC}"
if [ $VERIFY_FAILED -gt 0 ]; then
    echo -e "Verification Tests Failed: ${RED}$VERIFY_FAILED${NC}"
fi
echo ""

if [ $VERIFY_FAILED -eq 0 ]; then
    print_success "All critical dependencies installed successfully!"
    echo ""
    echo -e "${CYAN}Next Steps:${NC}"
    echo -e "  1. Run system audit: ${GREEN}python3 mainnet_operations_audit.py${NC}"
    echo -e "  2. Test data flow:   ${GREEN}python3 test_data_flow_integration.py${NC}"
    echo -e "  3. Start paper mode: ${GREEN}export EXECUTION_MODE=PAPER && ./start_mainnet.sh${NC}"
    echo ""
    exit 0
else
    print_error "Some dependencies failed to install. Please check the errors above."
    exit 1
fi
