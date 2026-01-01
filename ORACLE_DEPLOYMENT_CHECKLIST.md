# ✅ Oracle Cloud Always Free Deployment Checklist

Complete checklist for deploying Titan to Oracle Cloud Always Free tier.

---

## 📋 Pre-Deployment Checklist

### Oracle Cloud Account Setup
- [ ] **Oracle Cloud Account Created**
  - Sign up at: https://www.oracle.com/cloud/free/
  - Email verified
  - Free tier activated

- [ ] **SSH Key Pair Generated**
  ```bash
  ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
  ```
  - Public key: `~/.ssh/id_rsa.pub`
  - Private key: `~/.ssh/id_rsa`

### API Keys & Credentials Ready
- [ ] **Wallet Private Key**
  - Dedicated wallet created (NOT your main wallet)
  - Private key saved securely
  - Funded with gas money (~$20-50 recommended)

- [ ] **RPC Endpoints**
  - [ ] Infura Project ID: https://infura.io/
  - [ ] Alchemy API keys: https://www.alchemy.com/
  - [ ] Public RPC endpoints as backup

- [ ] **DEX Aggregator API Keys**
  - [ ] Li.Fi API key (required): https://li.fi/
  - [ ] 1inch API key (optional): https://portal.1inch.dev/
  - [ ] ParaSwap (optional - no key needed)

- [ ] **Optional API Keys**
  - [ ] CoinGecko API (price data)
  - [ ] Etherscan/Polygonscan API (verification)

---

## 🖥️ Oracle Cloud Instance Setup

### Step 1: Create Compute Instance
- [ ] **Login to Oracle Cloud Console**
  - Navigate to: https://cloud.oracle.com/
  
- [ ] **Create Instance**
  - Go to: Compute → Instances → Create Instance

- [ ] **Instance Configuration**
  - [ ] **Name**: `titan-arbitrage-bot` (or your choice)
  - [ ] **Image**: Oracle Linux 8 or Ubuntu 22.04
  - [ ] **Shape**: 
    - ✅ **RECOMMENDED**: VM.Standard.A1.Flex (ARM)
      - OCPUs: 4
      - Memory: 24 GB
    - Alternative: VM.Standard.E2.1.Micro (AMD)
      - OCPUs: 1
      - Memory: 1 GB
  - [ ] **Public IP**: Enabled
  - [ ] **SSH Key**: Uploaded (id_rsa.pub)
  - [ ] **Boot Volume**: 50 GB minimum

- [ ] **Instance Created Successfully**
  - Note public IP address: `_______________`

### Step 2: Configure Networking
- [ ] **Security List Configured**
  - Navigate to: Networking → VCN → Security Lists
  
- [ ] **Ingress Rules Added**
  - [ ] SSH (Port 22): `0.0.0.0/0` or your IP
  - [ ] Dashboard (Port 8000): Your IP only (optional)
  - [ ] Monitoring (Port 3001): Your IP only (optional)

### Step 3: First Connection
- [ ] **SSH Connection Successful**
  ```bash
  ssh -i ~/.ssh/id_rsa opc@YOUR_PUBLIC_IP
  # or for Ubuntu: ssh -i ~/.ssh/id_rsa ubuntu@YOUR_PUBLIC_IP
  ```

- [ ] **OS Firewall Configured**
  ```bash
  # For Oracle Linux 8:
  sudo firewall-cmd --permanent --add-port=22/tcp
  sudo firewall-cmd --permanent --add-port=8000/tcp
  sudo firewall-cmd --reload
  
  # For Ubuntu:
  sudo ufw allow 22/tcp
  sudo ufw allow 8000/tcp
  sudo ufw enable
  ```

---

## 🚀 Deployment Process

### Step 1: Clone Repository
- [ ] **Repository Cloned**
  ```bash
  git clone https://github.com/vegas-max/Titan2.0.git
  cd Titan2.0
  ```

### Step 2: Run Automated Deployment
- [ ] **Deployment Script Executed**
  ```bash
  chmod +x deploy_oracle_cloud.sh
  ./deploy_oracle_cloud.sh
  ```

- [ ] **Deployment Script Completed Successfully**
  - All dependencies installed
  - Node.js installed (v18+)
  - Python installed (v3.11+)
  - Redis installed (optional)
  - Build tools installed
  - Systemd services created

### Step 3: Configure Environment
- [ ] **.env File Configured**
  ```bash
  nano .env
  ```
  
  **Required Settings:**
  - [ ] `PRIVATE_KEY=0x...` (your dedicated wallet)
  - [ ] `RPC_POLYGON=https://polygon-mainnet.infura.io/v3/YOUR_KEY`
  - [ ] `ALCHEMY_RPC_POLYGON=https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY`
  - [ ] `LIFI_API_KEY=your_lifi_key`
  
  **Execution Mode:**
  - [ ] `EXECUTION_MODE=PAPER` (for testing - REQUIRED initially)
  - [ ] Or `EXECUTION_MODE=LIVE` (for real trading - only after testing)
  
  **Performance Settings (Auto-configured by script):**
  - For ARM (24GB RAM): `LIGHTWEIGHT_MODE=false`, `MAX_CONCURRENT_SCANS=20`
  - For AMD (1GB RAM): `LIGHTWEIGHT_MODE=true`, `MAX_CONCURRENT_SCANS=3`

- [ ] **.env File Permissions Set**
  ```bash
  chmod 600 .env
  ```

### Step 4: Deploy Smart Contracts (Optional)
- [ ] **Decide on Contract Deployment**
  - [ ] Use pre-deployed contracts (easier)
  - [ ] Or deploy your own contracts (more control)

- [ ] **If Deploying Contracts:**
  ```bash
  # For Polygon
  npx hardhat run onchain/scripts/deploy.js --network polygon
  
  # Copy the deployed address to .env
  # EXECUTOR_ADDRESS_POLYGON=0x...
  ```

### Step 5: Configure Swap Space (Low Memory Only)
- [ ] **Swap Configured** (if using 1GB RAM instance)
  ```bash
  sudo fallocate -l 4G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
  
  # Verify
  free -h
  ```

---

## ✅ Post-Deployment Verification

### Step 1: Service Status Check
- [ ] **Services Enabled for Auto-Start**
  ```bash
  sudo systemctl is-enabled titan-brain
  sudo systemctl is-enabled titan-executor
  ```

### Step 2: Start Services
- [ ] **Titan Services Started**
  ```bash
  ./start_oracle.sh
  ```

- [ ] **Verify Services Running**
  ```bash
  ./status_oracle.sh
  ```
  - Brain: Active (running)
  - Executor: Active (running)
  - Redis: Active (running) - optional

### Step 3: Health Check
- [ ] **Run Health Check Script**
  ```bash
  ./oracle_health_check.sh
  ```
  
  **All Checks Passed:**
  - [ ] System resources healthy
  - [ ] Dependencies installed
  - [ ] Services running
  - [ ] Configuration valid
  - [ ] Network connectivity OK
  - [ ] File-based signal system active

### Step 4: Log Verification
- [ ] **Brain Logs Look Normal**
  ```bash
  sudo journalctl -u titan-brain -n 50
  ```
  - No critical errors
  - AI engine initializing
  - Scanning for opportunities

- [ ] **Executor Logs Look Normal**
  ```bash
  sudo journalctl -u titan-executor -n 50
  ```
  - No critical errors
  - Listening for signals
  - Connected to blockchain

### Step 5: Signal System Check
- [ ] **Signal Files Being Created**
  ```bash
  ls -la signals/outgoing/
  ```
  - Signal files present (*.json)
  - Recent signals exist

---

## 🧪 Testing Phase

### Paper Trading Mode (REQUIRED FIRST)
- [ ] **Verify Paper Mode Active**
  ```bash
  grep "EXECUTION_MODE" .env
  # Should show: EXECUTION_MODE=PAPER
  ```

- [ ] **Monitor for 24-48 Hours**
  - [ ] Check logs every 6 hours
  - [ ] Verify opportunities being detected
  - [ ] Confirm trades simulated (not executed)
  - [ ] No critical errors
  - [ ] System stable

- [ ] **Review Paper Trading Results**
  ```bash
  # Check Redis stats if available
  redis-cli GET total_profit_paper
  redis-cli GET trades_executed_paper
  
  # Or check signal files
  cat signals/outgoing/*.json | grep "profit"
  ```

### Performance Monitoring
- [ ] **Resource Usage Normal**
  ```bash
  htop
  free -h
  df -h
  ```
  - Memory usage < 80%
  - Disk usage < 80%
  - CPU load acceptable

- [ ] **No OOM (Out of Memory) Errors**
  ```bash
  sudo journalctl | grep -i "out of memory"
  ```

---

## 🔐 Security Hardening

### Basic Security
- [ ] **Firewall Rules Tight**
  - SSH limited to your IP (recommended)
  - Dashboard not exposed publicly
  
- [ ] **.env File Secured**
  ```bash
  ls -la .env
  # Should show: -rw------- (600 permissions)
  ```

- [ ] **Redis Secured** (if installed)
  ```bash
  sudo grep "^bind" /etc/redis/redis.conf
  # Should bind to: 127.0.0.1 ::1 only
  ```

### Advanced Security (Optional)
- [ ] **Fail2Ban Installed**
  ```bash
  sudo dnf install -y fail2ban  # Oracle Linux
  sudo apt install -y fail2ban  # Ubuntu
  sudo systemctl enable fail2ban
  ```

- [ ] **Automatic Security Updates Enabled**
  ```bash
  # Oracle Linux
  sudo dnf install -y dnf-automatic
  sudo systemctl enable --now dnf-automatic.timer
  
  # Ubuntu
  sudo apt install unattended-upgrades
  ```

- [ ] **SSH Hardening** (optional)
  - Root login disabled
  - Password authentication disabled
  - Custom SSH port (if desired)

---

## 🎯 Going Live (After Successful Testing)

### Pre-Live Checklist
- [ ] **Paper Mode Successful**
  - Ran for at least 24-48 hours
  - No critical errors
  - Opportunities detected
  - System stable

- [ ] **Wallet Funded**
  - Dedicated wallet has gas funds
  - Amount limited (start small)
  - Main wallet NOT used

- [ ] **Live Mode Configuration**
  ```bash
  nano .env
  # Change: EXECUTION_MODE=LIVE
  ```

- [ ] **Restart Services**
  ```bash
  ./restart_oracle.sh
  ```

### Live Monitoring (First 24 Hours)
- [ ] **Monitor Closely**
  - Check logs every 2-4 hours
  - Watch for executed trades
  - Verify profitability
  - Check gas usage

- [ ] **Emergency Stop Ready**
  ```bash
  # Know how to stop quickly if needed:
  ./stop_oracle.sh
  # or
  ./emergency_shutdown.sh
  ```

---

## 📊 Ongoing Maintenance

### Daily Tasks
- [ ] **Check Service Status**
  ```bash
  ./status_oracle.sh
  ```

- [ ] **Review Logs for Errors**
  ```bash
  sudo journalctl -u titan-* --since "24 hours ago" | grep -i error
  ```

### Weekly Tasks
- [ ] **Run Health Check**
  ```bash
  ./oracle_health_check.sh
  ```

- [ ] **Backup Configuration**
  ```bash
  tar -czf ~/backup-$(date +%Y%m%d).tar.gz .env config.json
  ```

- [ ] **Review Performance**
  - Total trades executed
  - Total profit
  - Success rate
  - Gas usage

### Monthly Tasks
- [ ] **Update System**
  ```bash
  sudo dnf update -y  # Oracle Linux
  sudo apt update && sudo apt upgrade -y  # Ubuntu
  ```

- [ ] **Update Titan**
  ```bash
  cd ~/Titan2.0
  ./stop_oracle.sh
  git pull origin main
  npm install --legacy-peer-deps
  pip3 install -r requirements.txt
  npx hardhat compile
  ./start_oracle.sh
  ```

- [ ] **Rotate Logs** (if not auto-configured)
  ```bash
  # Clean old logs
  sudo journalctl --vacuum-time=30d
  ```

---

## 🆘 Troubleshooting Reference

### Quick Diagnostics
```bash
./oracle_health_check.sh              # Comprehensive check
./status_oracle.sh                    # Service status
sudo journalctl -u titan-brain -n 50  # Recent logs
```

### Common Issues
1. **Out of Memory**: Enable lightweight mode, add swap
2. **Redis Connection Failed**: Check/restart Redis (optional)
3. **RPC Rate Limiting**: Add backup RPC providers
4. **Services Won't Start**: Check logs, verify .env configuration

### Get Help
- [ ] **Documentation Read**
  - ORACLE_CLOUD_DEPLOYMENT.md (full guide)
  - ORACLE_TROUBLESHOOTING.md (common issues)
  - ORACLE_QUICK_REFERENCE.md (commands)

- [ ] **GitHub Issues Checked**
  - https://github.com/vegas-max/Titan2.0/issues

---

## 📝 Deployment Information

**Record your deployment details:**

- **Deployment Date**: _______________
- **Instance Type**: ARM A1.Flex / AMD E2.1.Micro (circle one)
- **Public IP**: _______________
- **Execution Mode**: PAPER / LIVE (circle one)
- **Networks Deployed**: _______________
- **Deployed Contract Address**: _______________

**Notes:**
```
[Add any custom configurations or notes here]




```

---

## ✅ Final Verification

- [ ] **All Services Running**: Brain, Executor
- [ ] **Health Check Passes**: No critical issues
- [ ] **Logs Clean**: No errors in last hour
- [ ] **Paper Mode Tested**: Successfully for 24+ hours
- [ ] **Monitoring Active**: Can view status and logs
- [ ] **Backup Created**: .env and config.json saved
- [ ] **Documentation Read**: Understand how to operate
- [ ] **Emergency Procedures Known**: Can stop system if needed

---

## 🎉 Success!

**Congratulations! Titan is now deployed on Oracle Cloud Always Free tier.**

### Quick Reference Commands
```bash
./start_oracle.sh          # Start Titan
./stop_oracle.sh           # Stop Titan
./restart_oracle.sh        # Restart Titan
./status_oracle.sh         # Check status
./oracle_health_check.sh   # Health check
```

### Important Reminders
- ⚠️ Start with **PAPER MODE** - test thoroughly before going live
- ⚠️ Use a **dedicated wallet** with limited funds
- ⚠️ Monitor closely during the **first 24 hours**
- ⚠️ Keep your **private key secure**
- ⚠️ Regular **backups** of configuration
- ⚠️ **Update regularly** for security patches

### Support
- Documentation: See ORACLE_CLOUD_DEPLOYMENT.md
- Troubleshooting: See ORACLE_TROUBLESHOOTING.md
- Issues: https://github.com/vegas-max/Titan2.0/issues

**Happy Trading! 🚀**
