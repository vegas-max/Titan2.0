#!/bin/bash
################################################################################
# TITAN 2.0 - VALIDATED BUILD SYSTEM
# 
# This script enforces military-style module validation before allowing
# any build operations to proceed. Each component must pass ALL tests
# and meet benchmark requirements.
################################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print section headers
print_header() {
    echo -e "\n${CYAN}================================================================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}================================================================================${NC}\n"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_header "TITAN 2.0 - MILITARY-STYLE VALIDATED BUILD SYSTEM"

echo -e "${YELLOW}⚠️  DRILL-SERGEANT MODE ACTIVATED${NC}"
echo -e "${YELLOW}System will validate ALL modules before proceeding with build.${NC}"
echo -e "${YELLOW}NO builds proceed until ALL validations PASS.${NC}\n"

# Step 1: Run military audit
print_header "STEP 1: RUNNING MILITARY MODULE AUDIT"

echo "Executing comprehensive module validation..."
if python3 military_audit.py; then
    print_success "Military audit PASSED - All modules validated"
else
    print_error "Military audit FAILED - Modules did not pass validation"
    echo -e "\n${RED}╔════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  BUILD BLOCKED - FIX ALL VALIDATION ERRORS BEFORE PROCEEDING      ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════════════╝${NC}\n"
    exit 1
fi

# Step 2: Install dependencies (only after validation passes)
print_header "STEP 2: INSTALLING DEPENDENCIES"

echo "All modules validated. Proceeding with dependency installation..."

# Install Node.js dependencies
if [ -f "package.json" ]; then
    print_warning "Installing Node.js dependencies..."
    if npm install --legacy-peer-deps; then
        print_success "Node.js dependencies installed"
    else
        print_error "Failed to install Node.js dependencies"
        exit 1
    fi
else
    print_warning "package.json not found, skipping Node.js dependencies"
fi

# Install Python dependencies
if [ -f "requirements.txt" ]; then
    print_warning "Installing Python dependencies..."
    if pip3 install -r requirements.txt; then
        print_success "Python dependencies installed"
    else
        print_error "Failed to install Python dependencies"
        exit 1
    fi
else
    print_warning "requirements.txt not found, skipping Python dependencies"
fi

# Step 3: Build Rust components (optional)
print_header "STEP 3: BUILDING HIGH-PERFORMANCE COMPONENTS"

if [ -d "core-rust" ] && [ -f "core-rust/Cargo.toml" ]; then
    print_warning "Building Rust performance cores..."
    cd core-rust
    if cargo build --release; then
        print_success "Rust components built successfully"
        cd ..
    else
        print_error "Rust build failed"
        cd ..
        exit 1
    fi
else
    print_warning "Rust components not found, skipping"
fi

# Step 4: Run post-build validation
print_header "STEP 4: POST-BUILD VALIDATION"

echo "Running post-build system checks..."

# Check if critical files exist after build
CRITICAL_FILES=(
    "config.json"
    "offchain/core/config.py"
    "offchain/ml/brain.py"
    "offchain/execution/bot.js"
)

all_present=true
for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "Critical file present: $file"
    else
        print_error "Critical file missing: $file"
        all_present=false
    fi
done

if [ "$all_present" = false ]; then
    print_error "Post-build validation failed - critical files missing"
    exit 1
fi

print_success "Post-build validation passed"

# Step 5: Final system ready check
print_header "STEP 5: FINAL SYSTEM READINESS CHECK"

echo "Performing final readiness validation..."

# Check Python environment
if python3 -c "import web3, pandas, numpy" 2>/dev/null; then
    print_success "Python environment ready"
else
    print_error "Python environment not ready - missing dependencies"
    exit 1
fi

# Check Node.js environment
if node --version >/dev/null 2>&1; then
    print_success "Node.js runtime ready"
else
    print_error "Node.js runtime not available"
    exit 1
fi

# Final summary
print_header "BUILD COMPLETED SUCCESSFULLY"

echo -e "${GREEN}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                                    ║${NC}"
echo -e "${GREEN}║  ✓ ALL MODULES VALIDATED AND BENCHMARKED                          ║${NC}"
echo -e "${GREEN}║  ✓ ALL DEPENDENCIES INSTALLED                                     ║${NC}"
echo -e "${GREEN}║  ✓ HIGH-PERFORMANCE COMPONENTS BUILT                              ║${NC}"
echo -e "${GREEN}║  ✓ POST-BUILD VALIDATION PASSED                                   ║${NC}"
echo -e "${GREEN}║  ✓ SYSTEM IS READY FOR OPERATION                                  ║${NC}"
echo -e "${GREEN}║                                                                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════════╝${NC}\n"

echo -e "You can now start the system using:"
echo -e "  ${CYAN}./start.sh${NC} or ${CYAN}make start${NC}\n"

exit 0
