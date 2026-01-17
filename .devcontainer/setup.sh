#!/bin/bash

# ==============================================================================
# GitHub Codespace Setup Script
# ==============================================================================
# This script automatically sets up the Titan 2.0 development environment
# in GitHub Codespaces.
# ==============================================================================

set -e

echo "===================================================="
echo "  🚀 TITAN 2.0 - CODESPACE SETUP"
echo "===================================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

# Step 1: Verify prerequisites
echo "Step 1: Verifying prerequisites..."
print_info "Checking installed tools..."

if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js installed: $NODE_VERSION"
else
    print_error "Node.js not found"
    exit 1
fi

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python installed: $PYTHON_VERSION"
else
    print_error "Python not found"
    exit 1
fi

if command -v cargo &> /dev/null; then
    RUST_VERSION=$(cargo --version)
    print_success "Rust installed: $RUST_VERSION"
else
    print_warning "Rust not found (optional)"
fi

if command -v go &> /dev/null; then
    GO_VERSION=$(go version)
    print_success "Go installed: $GO_VERSION"
else
    print_warning "Go not found (optional)"
fi

echo ""

# Step 2: Install Node.js dependencies
echo "Step 2: Installing Node.js dependencies..."
if [ -f "package-lock.json" ]; then
    if npm ci; then
        print_success "Node.js dependencies installed"
    else
        print_warning "npm ci failed, trying with npm install..."
        if npm install; then
            print_success "Node.js dependencies installed"
        else
            print_error "Failed to install Node.js dependencies"
            exit 1
        fi
    fi
else
    print_info "No package-lock.json found, using npm install..."
    if npm install; then
        print_success "Node.js dependencies installed"
    else
        print_error "Failed to install Node.js dependencies"
        exit 1
    fi
fi
echo ""

# Step 3: Install Python dependencies
echo "Step 3: Installing Python dependencies..."
if pip3 install --user -r requirements.txt; then
    print_success "Python dependencies installed"
else
    print_error "Failed to install Python dependencies"
    exit 1
fi
echo ""

# Step 4: Create necessary directories
echo "Step 4: Creating necessary directories..."
mkdir -p data logs certs
print_success "Directories created: data, logs, certs"
echo ""

# Step 5: Setup environment file
echo "Step 5: Setting up environment configuration..."
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        print_success "Created .env from .env.example"
        print_warning "Please edit .env file with your API keys and configuration"
    else
        print_warning ".env.example not found, skipping .env creation"
    fi
else
    print_info ".env file already exists, skipping"
fi
echo ""

# Step 6: Build Rust core (optional)
echo "Step 6: Building Rust core library (optional)..."
if command -v cargo &> /dev/null && [ -d "core-rust" ]; then
    if cd core-rust && cargo build --release 2>/dev/null; then
        print_success "Rust core library built successfully"
        cd ..
    else
        print_warning "Rust build failed or skipped (not required for basic operations)"
        cd .. 2>/dev/null || true
    fi
else
    print_info "Skipping Rust build (cargo not installed or core-rust not found)"
fi
echo ""

# Step 7: Build Go core (optional)
echo "Step 7: Building Go core binary (optional)..."
if command -v go &> /dev/null && [ -d "core-go" ]; then
    if cd core-go && go build -ldflags="-s -w" -o titan-core ./main.go 2>/dev/null; then
        print_success "Go core binary built successfully"
        cd ..
    else
        print_warning "Go build failed or skipped (not required for basic operations)"
        cd .. 2>/dev/null || true
    fi
else
    print_info "Skipping Go build (go not installed or core-go not found)"
fi
echo ""

# Step 8: Make scripts executable
echo "Step 8: Making scripts executable..."
chmod +x setup.sh 2>/dev/null || true
chmod +x start.sh 2>/dev/null || true
chmod +x start_mainnet.sh 2>/dev/null || true
chmod +x health-check.sh 2>/dev/null || true
chmod +x build.sh 2>/dev/null || true
chmod +x build_rust_engine.sh 2>/dev/null || true
chmod +x emergency_shutdown.sh 2>/dev/null || true
chmod +x launch_dashboard.sh 2>/dev/null || true
chmod +x launch_interactive_dashboard.sh 2>/dev/null || true
print_success "Scripts made executable"
echo ""

# Step 9: Run system audit
echo "Step 9: Running system audit..."
if python3 audit_system.py 2>/dev/null; then
    print_success "System audit completed"
else
    print_warning "System audit skipped or failed (not critical)"
fi
echo ""

# Final message
echo "===================================================="
echo "  ✨ CODESPACE SETUP COMPLETE"
echo "===================================================="
echo ""
print_success "Your Titan 2.0 Codespace is ready!"
echo ""
echo "📚 Next Steps:"
echo "  1. Edit .env file with your configuration:"
echo "     - Add your PRIVATE_KEY (use a test wallet)"
echo "     - Add RPC endpoints (Infura/Alchemy)"
echo "     - Add LIFI_API_KEY for cross-chain support"
echo ""
echo "  2. Quick commands:"
echo "     make help          - View all available commands"
echo "     make start         - Start the system"
echo "     make health        - Check system health"
echo "     make test          - Run tests"
echo ""
echo "  3. Read documentation:"
echo "     - GETTING_STARTED.md  - New user guide"
echo "     - QUICKSTART.md       - 15-minute setup"
echo "     - README.md           - Full documentation"
echo ""
echo "===================================================="
