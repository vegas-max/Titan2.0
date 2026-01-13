# 🛠️ Titan 2.0 Setup Guide

Complete step-by-step setup instructions for local installation.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation Steps](#installation-steps)
- [Configuration](#configuration)
- [Verification](#verification)
- [Starting Titan](#starting-titan)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

Install the following before proceeding:

1. **Node.js 18 or higher**
   ```bash
   # Verify installation
   node --version  # Should show v18.0.0 or higher
   npm --version
   ```
   Download from: https://nodejs.org/

2. **Python 3.11 or higher**
   ```bash
   # Verify installation
   python3 --version  # Should show 3.11.0 or higher
   pip3 --version
   ```
   Download from: https://python.org/

3. **Git**
   ```bash
   # Verify installation
   git --version
   ```
   Download from: https://git-scm.com/

4. **Rust 1.70+ (Optional - for high-performance features)**
   ```bash
   # Install Rust
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   
   # Verify installation
   rustc --version  # Should show 1.70.0 or higher
   ```
   More info: https://rust-lang.org/

5. **Go 1.21+ (Optional - for Go components)**
   ```bash
   # Verify installation
   go version  # Should show 1.21.0 or higher
   ```
   Download from: https://golang.org/

### Optional (but recommended)

- **Redis 5.0+** - For caching (can run without it using `NO_REDIS_QUICKSTART.md`)
- **Docker** - For containerized deployment

---

## Installation Steps

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/vegas-max/Titan2.0.git

# Navigate to the directory
cd Titan2.0
```

### Step 2: Automated Setup (Recommended)

```bash
# Make the setup script executable
chmod +x setup.sh

# Run the automated setup
./setup.sh
```

The `setup.sh` script will:
- ✅ Check all prerequisites
- ✅ Install Node.js dependencies
- ✅ Install Python dependencies
- ✅ Build Rust components (if Rust is installed)
- ✅ Build Go components (if Go is installed)
- ✅ Create `.env` file from template
- ✅ Verify Redis connection (if Redis is installed)
- ✅ Run initial system audit

**If the automated setup succeeds, skip to [Configuration](#configuration).**

### Step 3: Manual Setup (If Automated Setup Fails)

If the automated setup doesn't work, follow these manual steps:

#### 3.1 Install Node.js Dependencies
```bash
npm install
```

#### 3.2 Install Python Dependencies
```bash
pip3 install -r requirements.txt
```

#### 3.3 Build Rust Components (Optional)
```bash
# Only if you have Rust installed
cd core-rust
cargo build --release
cd ..
```

#### 3.4 Build Go Components (Optional)
```bash
# Only if you have Go installed
cd core-go
go build -o ../bin/titan-go
cd ..
```

#### 3.5 Create Environment File
```bash
# Copy the example environment file
cp .env.example .env
```

---

## Configuration

### Step 1: Edit the Environment File

Open the `.env` file in your favorite text editor:

```bash
# Using nano
nano .env

# Using vim
vim .env

# Using VS Code
code .env
```

### Step 2: Configure Required Settings

At minimum, you need to configure:

```bash
# Node RPC endpoints (get free keys from Alchemy, Infura, or QuickNode)
POLYGON_RPC_URL=https://polygon-rpc.com
ETHEREUM_RPC_URL=https://eth.llamarpc.com
ARBITRUM_RPC_URL=https://arb1.arbitrum.io/rpc

# Trading mode (ALWAYS start with PAPER mode)
TRADING_MODE=PAPER  # Use PAPER for testing, LIVE for real trading

# Wallet configuration (for LIVE mode only - leave empty for PAPER mode)
PRIVATE_KEY=  # Leave empty for PAPER mode
WALLET_ADDRESS=  # Leave empty for PAPER mode

# Optional: API keys for enhanced features
INFURA_API_KEY=
ALCHEMY_API_KEY=
ETHERSCAN_API_KEY=
```

### Step 3: Configuration Files

The main configuration is in `config.json`. The default settings work for most users, but you can customize:

- DEX endpoints and contracts
- Token lists and pairs
- Trading parameters
- Risk management settings
- Network configurations

See [Configuration Guide](README.md#️-configuration) for detailed options.

---

## Verification

### Step 1: Run Health Check

```bash
# Make the health check script executable
chmod +x health-check.sh

# Run the health check
./health-check.sh
```

The health check will verify:
- ✅ Node.js and npm versions
- ✅ Python and pip versions
- ✅ Rust and cargo versions (if installed)
- ✅ Go version (if installed)
- ✅ Redis connection (if configured)
- ✅ RPC endpoints connectivity
- ✅ Configuration files validity
- ✅ Dependencies installation

### Step 2: Run System Audit

```bash
# Run comprehensive system audit
python3 comprehensive_audit.py
```

This will check:
- System dependencies
- Configuration validity
- Network connectivity
- Smart contract compatibility
- Security settings

---

## Starting Titan

### Step 1: Start in Paper Mode (Recommended for First Time)

```bash
# Ensure TRADING_MODE=PAPER in .env file
echo "TRADING_MODE=PAPER" >> .env

# Start Titan
./start.sh
```

### Step 2: Verify Titan is Running

Check the logs to ensure everything is working:

```bash
# View logs
tail -f logs/titan.log

# Or use the quick status tool
python3 quick_status.py
```

You should see:
- ✅ Components initializing
- ✅ RPC connections established
- ✅ DEX scanners active
- ✅ Opportunity detection running

### Step 3: Access the Dashboard (Optional)

```bash
# Start the interactive dashboard
./launch_interactive_dashboard.sh

# Or start the dashboard server
python3 dashboard_server.py
```

Open your browser to: http://localhost:3000

---

## Troubleshooting

### Common Issues

#### 1. "Command not found: node"
**Solution:** Node.js is not installed or not in PATH
```bash
# Install Node.js from https://nodejs.org/
# Or use nvm (Node Version Manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
```

#### 2. "Command not found: python3"
**Solution:** Python is not installed or not in PATH
```bash
# Install Python from https://python.org/
# Or use pyenv (Python Version Manager)
curl https://pyenv.run | bash
pyenv install 3.11
```

#### 3. "ModuleNotFoundError: No module named 'web3'"
**Solution:** Python dependencies not installed
```bash
pip3 install -r requirements.txt
```

#### 4. "Error: Cannot find module '@ethersproject/abi'"
**Solution:** Node.js dependencies not installed
```bash
npm install
```

#### 5. "Redis connection failed"
**Solution:** Redis is not running or not configured

Option A - Install and start Redis:
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# macOS
brew install redis
brew services start redis
```

Option B - Run without Redis:
```bash
# See NO_REDIS_QUICKSTART.md
cp .env.example .env
echo "USE_REDIS=false" >> .env
```

#### 6. "RPC endpoint connection failed"
**Solution:** RPC URLs are not configured or invalid
```bash
# Edit .env and add valid RPC URLs
# Get free RPC URLs from:
# - Alchemy: https://www.alchemy.com/
# - Infura: https://infura.io/
# - QuickNode: https://www.quicknode.com/
```

#### 7. "Permission denied: ./setup.sh"
**Solution:** Script is not executable
```bash
chmod +x setup.sh
chmod +x start.sh
chmod +x health-check.sh
```

#### 8. Rust compilation errors
**Solution:** Update Rust to the latest version
```bash
rustup update
```

### Advanced Troubleshooting

For more detailed troubleshooting:
- **Oracle Cloud Issues:** See [ORACLE_TROUBLESHOOTING.md](ORACLE_TROUBLESHOOTING.md)
- **Redis Issues:** See [NO_REDIS_QUICKSTART.md](NO_REDIS_QUICKSTART.md)
- **Network Issues:** Check your firewall and network settings
- **Smart Contract Issues:** See [Smart Contracts Documentation](README.md#-smart-contracts)

### Getting Help

If you're still having issues:
1. Check the [FAQ in README.md](README.md)
2. Review existing [GitHub Issues](https://github.com/vegas-max/Titan2.0/issues)
3. Open a new issue with:
   - Your operating system and version
   - Node.js, Python, Rust, and Go versions
   - Complete error messages
   - Steps to reproduce the issue

---

## Next Steps

Once Titan is running successfully:

1. **Learn the Basics:**
   - Read [QUICKSTART.md](QUICKSTART.md) for basic operations
   - Review [MAINNET_MODES.md](MAINNET_MODES.md) to understand trading modes

2. **Configure Trading:**
   - Review [OPERATIONS_GUIDE.md](OPERATIONS_GUIDE.md)
   - Set up monitoring: [MONITORING_ALERTING.md](MONITORING_ALERTING.md)

3. **Test Thoroughly:**
   - Run simulations: `./run_simulation.sh`
   - Test with paper trading for at least 1 week
   - Review [TESTING_CHECKLIST.md](TESTING_CHECKLIST.md)

4. **Security Review:**
   - Read [SECURITY_SUMMARY.md](SECURITY_SUMMARY.md)
   - Complete [GO_LIVE_CHECKLIST.md](GO_LIVE_CHECKLIST.md) before going live

5. **Deploy to Production:**
   - Follow [GO_LIVE_CHECKLIST.md](GO_LIVE_CHECKLIST.md)
   - Set up monitoring and alerts
   - Start with small amounts

---

## Quick Command Reference

```bash
# Installation
./setup.sh                          # Automated setup
npm install                         # Install Node.js deps
pip3 install -r requirements.txt    # Install Python deps

# Configuration
cp .env.example .env               # Create environment file
nano .env                          # Edit configuration

# Verification
./health-check.sh                  # System health check
python3 comprehensive_audit.py     # Full system audit
python3 quick_status.py            # Quick status

# Running
./start.sh                         # Start Titan
./emergency_shutdown.sh            # Emergency stop
./run_simulation.sh                # Run simulation

# Monitoring
tail -f logs/titan.log             # View logs
./launch_interactive_dashboard.sh  # Start dashboard
python3 dashboard_server.py        # Start dashboard server

# Maintenance
./restart_oracle.sh                # Restart (Oracle Cloud)
git pull                           # Update to latest version
npm update                         # Update Node.js packages
pip3 install -r requirements.txt --upgrade  # Update Python packages
```

---

**Congratulations! You've successfully set up Titan 2.0!** 🎉

For the complete documentation, see [README.md](README.md).
