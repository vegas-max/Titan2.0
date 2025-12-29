#!/bin/bash

# ==============================================================================
# 🌩️ APEX-OMEGA TITAN: Oracle Cloud Automated Deployment Script
# ==============================================================================
# This script automates the deployment of Titan on Oracle Cloud Always Free tier
# Supports both ARM (Ampere) and AMD instances
#
# Usage: ./deploy_oracle_cloud.sh
# ==============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ASCII Art Banner
print_banner() {
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                                                                ║"
    echo "║          ████████╗██╗████████╗ █████╗ ███╗   ██╗              ║"
    echo "║          ╚══██╔══╝██║╚══██╔══╝██╔══██╗████╗  ██║              ║"
    echo "║             ██║   ██║   ██║   ███████║██╔██╗ ██║              ║"
    echo "║             ██║   ██║   ██║   ██╔══██║██║╚██╗██║              ║"
    echo "║             ██║   ██║   ██║   ██║  ██║██║ ╚████║              ║"
    echo "║             ╚═╝   ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝              ║"
    echo "║                                                                ║"
    echo "║              Oracle Cloud Deployment Script v1.0              ║"
    echo "║                                                                ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Function to print status messages
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

print_step() {
    echo -e "${PURPLE}[→]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect architecture
detect_architecture() {
    ARCH=$(uname -m)
    if [ "$ARCH" = "aarch64" ]; then
        echo "arm64"
    elif [ "$ARCH" = "x86_64" ]; then
        echo "amd64"
    else
        echo "unknown"
    fi
}

# Detect OS
detect_os() {
    if [ -f /etc/oracle-release ]; then
        echo "oracle"
    elif [ -f /etc/lsb-release ]; then
        echo "ubuntu"
    elif [ -f /etc/debian_version ]; then
        echo "debian"
    else
        echo "unknown"
    fi
}

# Get memory in GB
get_memory_gb() {
    MEM_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    MEM_GB=$((MEM_KB / 1024 / 1024))
    echo $MEM_GB
}

# Get CPU count
get_cpu_count() {
    nproc
}

# Main deployment function
main() {
    print_banner
    
    echo -e "${BLUE}===================================================${NC}"
    echo -e "${BLUE}   STEP 1: System Detection${NC}"
    echo -e "${BLUE}===================================================${NC}"
    echo ""
    
    # Detect system
    ARCH=$(detect_architecture)
    OS=$(detect_os)
    MEM_GB=$(get_memory_gb)
    CPU_COUNT=$(get_cpu_count)
    
    print_info "Architecture: $ARCH"
    print_info "Operating System: $OS"
    print_info "Memory: ${MEM_GB}GB"
    print_info "CPU Cores: $CPU_COUNT"
    echo ""
    
    # Determine configuration
    if [ "$ARCH" = "arm64" ] && [ $MEM_GB -ge 20 ]; then
        INSTANCE_TYPE="ARM_HIGH"
        print_status "Detected: ARM High-Performance Instance (A1.Flex)"
        LIGHTWEIGHT_MODE="false"
        MAX_CONCURRENT=20
        WORKER_THREADS=4
    elif [ $MEM_GB -le 2 ]; then
        INSTANCE_TYPE="AMD_MICRO"
        print_warning "Detected: Low Memory Instance (E2.1.Micro)"
        print_warning "Enabling lightweight mode for optimal performance"
        LIGHTWEIGHT_MODE="true"
        MAX_CONCURRENT=3
        WORKER_THREADS=1
    else
        INSTANCE_TYPE="STANDARD"
        print_status "Detected: Standard Instance"
        LIGHTWEIGHT_MODE="false"
        MAX_CONCURRENT=10
        WORKER_THREADS=2
    fi
    echo ""
    
    echo -e "${BLUE}===================================================${NC}"
    echo -e "${BLUE}   STEP 2: Update System${NC}"
    echo -e "${BLUE}===================================================${NC}"
    echo ""
    
    print_step "Updating system packages..."
    if [ "$OS" = "oracle" ]; then
        sudo dnf update -y
    else
        sudo apt update && sudo apt upgrade -y
    fi
    print_status "System updated"
    echo ""
    
    echo -e "${BLUE}===================================================${NC}"
    echo -e "${BLUE}   STEP 3: Install Dependencies${NC}"
    echo -e "${BLUE}===================================================${NC}"
    echo ""
    
    # Install Node.js
    print_step "Installing Node.js 18..."
    if ! command_exists node; then
        if [ "$OS" = "oracle" ]; then
            curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
            sudo dnf install -y nodejs
        else
            curl -fsSL https://deb.nodesource.com/setup_18.x | sudo bash -
            sudo apt install -y nodejs
        fi
        print_status "Node.js installed: $(node -v)"
    else
        print_status "Node.js already installed: $(node -v)"
    fi
    echo ""
    
    # Install Python
    print_step "Installing Python 3.11..."
    if ! command_exists python3; then
        if [ "$OS" = "oracle" ]; then
            sudo dnf install -y python3.11 python3.11-pip python3.11-devel
        else
            sudo apt install -y python3.11 python3.11-pip python3-dev
        fi
        print_status "Python installed: $(python3 --version)"
    else
        print_status "Python already installed: $(python3 --version)"
    fi
    echo ""
    
    # Install Redis
    print_step "Installing Redis..."
    if ! command_exists redis-server; then
        if [ "$OS" = "oracle" ]; then
            sudo dnf install -y redis
        else
            sudo apt install -y redis-server
        fi
        print_status "Redis installed"
    else
        print_status "Redis already installed"
    fi
    echo ""
    
    # Install build tools
    print_step "Installing build tools..."
    if [ "$OS" = "oracle" ]; then
        sudo dnf groupinstall -y "Development Tools"
        sudo dnf install -y git gcc make
    else
        sudo apt install -y build-essential git gcc make
    fi
    print_status "Build tools installed"
    echo ""
    
    # Install additional utilities
    print_step "Installing system utilities..."
    if [ "$OS" = "oracle" ]; then
        sudo dnf install -y htop iotop iftop wget curl vim nano
    else
        sudo apt install -y htop iotop iftop wget curl vim nano
    fi
    print_status "Utilities installed"
    echo ""
    
    echo -e "${BLUE}===================================================${NC}"
    echo -e "${BLUE}   STEP 4: Setup Titan${NC}"
    echo -e "${BLUE}===================================================${NC}"
    echo ""
    
    # Check if already in Titan directory
    if [ ! -f "package.json" ]; then
        print_error "package.json not found. Please run this script from the Titan2.0 directory"
        exit 1
    fi
    
    # Install Node.js dependencies
    print_step "Installing Node.js dependencies..."
    if command_exists yarn; then
        yarn install
    else
        npm install --legacy-peer-deps
    fi
    print_status "Node.js dependencies installed"
    echo ""
    
    # Install Python dependencies
    print_step "Installing Python dependencies..."
    pip3 install -r requirements.txt
    print_status "Python dependencies installed"
    echo ""
    
    # Compile contracts
    print_step "Compiling smart contracts..."
    npx hardhat compile
    print_status "Smart contracts compiled"
    echo ""
    
    echo -e "${BLUE}===================================================${NC}"
    echo -e "${BLUE}   STEP 5: Configure Environment${NC}"
    echo -e "${BLUE}===================================================${NC}"
    echo ""
    
    # Create .env if it doesn't exist
    if [ ! -f ".env" ]; then
        print_step "Creating .env file from template..."
        cp .env.example .env
        
        # Apply optimizations based on instance type
        if [ "$LIGHTWEIGHT_MODE" = "true" ]; then
            cat >> .env << EOF

# Oracle Cloud Optimizations (Auto-configured)
LIGHTWEIGHT_MODE=true
MAX_CONCURRENT_SCANS=$MAX_CONCURRENT
WORKER_THREADS=$WORKER_THREADS
ENABLE_GRAPH_VISUALIZATION=false
CACHE_SIZE_MB=50
EXECUTION_MODE=PAPER
EOF
        else
            cat >> .env << EOF

# Oracle Cloud Optimizations (Auto-configured)
LIGHTWEIGHT_MODE=false
MAX_CONCURRENT_SCANS=$MAX_CONCURRENT
WORKER_THREADS=$WORKER_THREADS
ENABLE_GRAPH_VISUALIZATION=true
CACHE_SIZE_MB=1000
EXECUTION_MODE=PAPER
EOF
        fi
        
        print_status ".env file created with optimized settings"
        print_warning "IMPORTANT: You must edit .env and add your credentials!"
        echo ""
        
        # Prompt for basic configuration
        read -p "Do you want to configure .env now? (y/n): " CONFIGURE_NOW
        if [ "$CONFIGURE_NOW" = "y" ] || [ "$CONFIGURE_NOW" = "Y" ]; then
            nano .env
        fi
    else
        print_status ".env file already exists"
    fi
    echo ""
    
    echo -e "${BLUE}===================================================${NC}"
    echo -e "${BLUE}   STEP 6: Setup System Services${NC}"
    echo -e "${BLUE}===================================================${NC}"
    echo ""
    
    # Create systemd service directory if it doesn't exist
    if [ ! -d "systemd" ]; then
        mkdir -p systemd
    fi
    
    # Get current user and directory
    CURRENT_USER=$(whoami)
    CURRENT_DIR=$(pwd)
    
    # Create Redis service file
    print_step "Creating systemd service files..."
    
    cat > systemd/titan-redis.service << EOF
[Unit]
Description=Redis Server for Titan
After=network.target

[Service]
Type=notify
ExecStart=/usr/bin/redis-server /etc/redis/redis.conf
ExecStop=/bin/kill -s TERM \$MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    
    # Create Brain service file
    cat > systemd/titan-brain.service << EOF
[Unit]
Description=Titan Brain (AI Engine)
After=network.target titan-redis.service
Requires=titan-redis.service

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 $CURRENT_DIR/offchain/ml/brain.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
MemoryLimit=$([ "$LIGHTWEIGHT_MODE" = "true" ] && echo "700M" || echo "4G")

[Install]
WantedBy=multi-user.target
EOF
    
    # Create Executor service file
    cat > systemd/titan-executor.service << EOF
[Unit]
Description=Titan Executor (Trading Bot)
After=network.target titan-redis.service titan-brain.service
Requires=titan-redis.service

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="NODE_ENV=production"
ExecStart=/usr/bin/node $CURRENT_DIR/offchain/execution/bot.js
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
MemoryLimit=$([ "$LIGHTWEIGHT_MODE" = "true" ] && echo "250M" || echo "2G")

[Install]
WantedBy=multi-user.target
EOF
    
    print_status "Service files created"
    echo ""
    
    # Install service files
    print_step "Installing systemd services..."
    sudo cp systemd/titan-redis.service /etc/systemd/system/
    sudo cp systemd/titan-brain.service /etc/systemd/system/
    sudo cp systemd/titan-executor.service /etc/systemd/system/
    sudo systemctl daemon-reload
    print_status "Services installed"
    echo ""
    
    # Enable services
    print_step "Enabling services to start on boot..."
    sudo systemctl enable titan-redis
    sudo systemctl enable titan-brain
    sudo systemctl enable titan-executor
    print_status "Services enabled"
    echo ""
    
    echo -e "${BLUE}===================================================${NC}"
    echo -e "${BLUE}   STEP 7: Setup Swap (Low Memory Only)${NC}"
    echo -e "${BLUE}===================================================${NC}"
    echo ""
    
    if [ $MEM_GB -le 2 ]; then
        print_step "Setting up 4GB swap file for low memory instance..."
        
        if [ ! -f /swapfile ]; then
            sudo fallocate -l 4G /swapfile
            sudo chmod 600 /swapfile
            sudo mkswap /swapfile
            sudo swapon /swapfile
            
            # Make swap permanent
            if ! grep -q "/swapfile" /etc/fstab; then
                echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
            fi
            
            print_status "Swap configured: 4GB"
        else
            print_status "Swap already configured"
        fi
    else
        print_info "Sufficient memory detected, skipping swap setup"
    fi
    echo ""
    
    echo -e "${BLUE}===================================================${NC}"
    echo -e "${BLUE}   STEP 8: Create Management Scripts${NC}"
    echo -e "${BLUE}===================================================${NC}"
    echo ""
    
    # Create start script
    cat > start_oracle.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Titan services..."
sudo systemctl start titan-redis
sleep 2
sudo systemctl start titan-brain
sleep 2
sudo systemctl start titan-executor
echo "✅ Titan started!"
echo ""
echo "Check status with: sudo systemctl status titan-brain titan-executor"
echo "View logs with: sudo journalctl -u titan-brain -f"
EOF
    chmod +x start_oracle.sh
    
    # Create stop script
    cat > stop_oracle.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping Titan services..."
sudo systemctl stop titan-executor
sudo systemctl stop titan-brain
sudo systemctl stop titan-redis
echo "✅ Titan stopped!"
EOF
    chmod +x stop_oracle.sh
    
    # Create restart script
    cat > restart_oracle.sh << 'EOF'
#!/bin/bash
echo "🔄 Restarting Titan services..."
sudo systemctl restart titan-brain
sudo systemctl restart titan-executor
echo "✅ Titan restarted!"
EOF
    chmod +x restart_oracle.sh
    
    # Create status script
    cat > status_oracle.sh << 'EOF'
#!/bin/bash
echo "📊 Titan Service Status:"
echo ""
sudo systemctl status titan-redis --no-pager
echo ""
sudo systemctl status titan-brain --no-pager
echo ""
sudo systemctl status titan-executor --no-pager
EOF
    chmod +x status_oracle.sh
    
    print_status "Management scripts created"
    print_info "  - start_oracle.sh   - Start all services"
    print_info "  - stop_oracle.sh    - Stop all services"
    print_info "  - restart_oracle.sh - Restart services"
    print_info "  - status_oracle.sh  - View service status"
    echo ""
    
    echo -e "${BLUE}===================================================${NC}"
    echo -e "${BLUE}   STEP 9: Configure Firewall${NC}"
    echo -e "${BLUE}===================================================${NC}"
    echo ""
    
    print_step "Configuring firewall..."
    if command_exists firewall-cmd; then
        # Oracle Linux firewall
        sudo firewall-cmd --permanent --add-port=22/tcp 2>/dev/null || true
        sudo firewall-cmd --permanent --add-port=8000/tcp 2>/dev/null || true
        sudo firewall-cmd --reload 2>/dev/null || true
        print_status "Firewall configured (firewalld)"
    elif command_exists ufw; then
        # Ubuntu firewall
        sudo ufw allow 22/tcp 2>/dev/null || true
        sudo ufw allow 8000/tcp 2>/dev/null || true
        print_status "Firewall configured (ufw)"
    else
        print_warning "No firewall detected, skipping"
    fi
    echo ""
    
    echo -e "${BLUE}===================================================${NC}"
    echo -e "${BLUE}   STEP 10: Security Hardening${NC}"
    echo -e "${BLUE}===================================================${NC}"
    echo ""
    
    print_step "Applying security settings..."
    
    # Secure .env file
    chmod 600 .env
    
    # Configure Redis security
    if [ -f /etc/redis/redis.conf ]; then
        sudo sed -i 's/^bind .*/bind 127.0.0.1 ::1/' /etc/redis/redis.conf
        print_status "Redis configured to listen only on localhost"
    fi
    
    # Create log directory
    sudo mkdir -p /var/log/titan
    sudo chown $CURRENT_USER:$CURRENT_USER /var/log/titan
    
    print_status "Security settings applied"
    echo ""
    
    # Final status
    echo -e "${GREEN}===================================================${NC}"
    echo -e "${GREEN}   ✅ DEPLOYMENT COMPLETED SUCCESSFULLY!${NC}"
    echo -e "${GREEN}===================================================${NC}"
    echo ""
    
    # Display summary
    echo -e "${CYAN}📋 Deployment Summary:${NC}"
    echo ""
    echo -e "  Instance Type: ${YELLOW}$INSTANCE_TYPE${NC}"
    echo -e "  Architecture:  ${YELLOW}$ARCH${NC}"
    echo -e "  Memory:        ${YELLOW}${MEM_GB}GB${NC}"
    echo -e "  CPU Cores:     ${YELLOW}$CPU_COUNT${NC}"
    echo -e "  Lightweight:   ${YELLOW}$LIGHTWEIGHT_MODE${NC}"
    echo ""
    
    echo -e "${CYAN}📝 Next Steps:${NC}"
    echo ""
    echo -e "  ${YELLOW}1. Configure your environment:${NC}"
    echo -e "     nano .env"
    echo -e "     ${BLUE}Add your PRIVATE_KEY, API keys (Infura, Alchemy, Li.Fi)${NC}"
    echo ""
    echo -e "  ${YELLOW}2. Deploy smart contract (if needed):${NC}"
    echo -e "     npx hardhat run onchain/scripts/deploy.js --network polygon"
    echo -e "     ${BLUE}Copy the deployed address to .env as EXECUTOR_ADDRESS_POLYGON${NC}"
    echo ""
    echo -e "  ${YELLOW}3. Start Titan:${NC}"
    echo -e "     ./start_oracle.sh"
    echo ""
    echo -e "  ${YELLOW}4. Monitor status:${NC}"
    echo -e "     ./status_oracle.sh"
    echo -e "     sudo journalctl -u titan-brain -f"
    echo ""
    echo -e "  ${YELLOW}5. Check health:${NC}"
    echo -e "     ./health-check.sh"
    echo ""
    
    echo -e "${CYAN}📚 Documentation:${NC}"
    echo -e "  - ORACLE_CLOUD_DEPLOYMENT.md - Complete deployment guide"
    echo -e "  - QUICKSTART.md              - Quick start guide"
    echo -e "  - OPERATIONS_GUIDE.md        - Operations manual"
    echo ""
    
    echo -e "${CYAN}⚠️  Important Reminders:${NC}"
    echo -e "  - Start in ${YELLOW}PAPER MODE${NC} first (already configured)"
    echo -e "  - Monitor for ${YELLOW}24 hours${NC} before going live"
    echo -e "  - Keep your ${YELLOW}private key secure${NC}"
    echo -e "  - Use a ${YELLOW}dedicated wallet${NC} with limited funds"
    echo ""
    
    echo -e "${GREEN}🎉 Happy Trading!${NC}"
    echo ""
}

# Run main function
main
