# 🌩️ Oracle Cloud Always Free Deployment Guide

This guide will help you deploy APEX-OMEGA TITAN to an Oracle Cloud Always Free tier instance.

## 📋 Table of Contents

- [Oracle Cloud Always Free Tier Overview](#oracle-cloud-always-free-tier-overview)
- [Prerequisites](#prerequisites)
- [Instance Setup](#instance-setup)
- [Deployment Methods](#deployment-methods)
  - [Method 1: Automated Deployment Script (Recommended)](#method-1-automated-deployment-script-recommended)
  - [Method 2: Docker Deployment](#method-2-docker-deployment)
  - [Method 3: Manual Deployment](#method-3-manual-deployment)
- [System Configuration](#system-configuration)
- [Starting and Managing Titan](#starting-and-managing-titan)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Troubleshooting](#troubleshooting)
- [Security Hardening](#security-hardening)

---

## 🎯 Oracle Cloud Always Free Tier Overview

Oracle Cloud offers a generous Always Free tier that's suitable for running Titan:

### Available Resources:

**Compute Options (Choose ONE):**
- **Option A: AMD VM** - VM.Standard.E2.1.Micro
  - 1 OCPU (AMD processor)
  - 1 GB RAM
  - Better for general purpose workloads
  
- **Option B: ARM VM** - VM.Standard.A1.Flex (RECOMMENDED)
  - Up to 4 OCPUs (Ampere Altra ARM processors)
  - Up to 24 GB RAM
  - **Best for Titan** - More resources available
  - Requires ARM-compatible builds

**Storage:**
- 200 GB total Block Volume storage
- 10 GB Object Storage

**Network:**
- 10 TB monthly data transfer
- Public IPv4 and IPv6 addresses

### ⭐ Recommendation: Use ARM Instance

The ARM-based VM.Standard.A1.Flex instance is **highly recommended** because:
- ✅ 4 OCPUs vs 1 OCPU (4x processing power)
- ✅ 24 GB RAM vs 1 GB (24x memory)
- ✅ Better for multi-threaded Titan operations
- ✅ Can handle more concurrent scans
- ✅ Runs smoother with multiple components

---

## 🔧 Prerequisites

### On Your Local Machine:

1. **Oracle Cloud Account** (Free tier)
   - Sign up at: https://www.oracle.com/cloud/free/

2. **SSH Key Pair**
   - Generate if you don't have one:
   ```bash
   ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
   ```

3. **Git** (to clone the repository)

### API Keys and Credentials:

Prepare these before deployment:
- [ ] Wallet private key (dedicated for Titan)
- [ ] Infura Project ID
- [ ] Alchemy API keys
- [ ] Li.Fi API key
- [ ] Other optional API keys (CoinGecko, 1inch, etc.)

---

## 🖥️ Instance Setup

### Step 1: Create Oracle Cloud Instance

1. **Login to Oracle Cloud Console**
   - Go to: https://cloud.oracle.com/

2. **Create Compute Instance**
   - Navigate to: **Compute** → **Instances** → **Create Instance**

3. **Configure Instance:**
   
   **Name:** `titan-arbitrage-bot`
   
   **Image and Shape:**
   - Click "Edit" next to "Image and shape"
   - **Image:** Oracle Linux 8 (or Ubuntu 22.04)
   - **Shape:** 
     - For ARM: Select "Ampere" → VM.Standard.A1.Flex
       - OCPUs: 4 (use full free tier allocation)
       - Memory: 24 GB
     - For AMD: VM.Standard.E2.1.Micro
       - 1 OCPU, 1 GB RAM

   **Networking:**
   - Select your VCN (or create new)
   - Assign public IP address: ✅ Yes
   
   **SSH Keys:**
   - Upload your public key (id_rsa.pub)

   **Boot Volume:**
   - Size: 50 GB (adjust as needed, max 200 GB free)

4. **Click "Create"** and wait for instance to provision (2-3 minutes)

5. **Note the Public IP Address** - you'll need this for SSH access

### Step 2: Configure Firewall Rules

1. **In Oracle Cloud Console:**
   - Go to: **Networking** → **Virtual Cloud Networks**
   - Click your VCN → **Security Lists** → **Default Security List**
   
2. **Add Ingress Rules:**
   
   **For SSH:**
   - Source CIDR: `0.0.0.0/0` (or your IP for better security)
   - IP Protocol: TCP
   - Destination Port: 22
   
   **For Monitoring Dashboard (Optional):**
   - Source CIDR: Your IP address
   - IP Protocol: TCP
   - Destination Port: 8000, 3001

3. **Configure OS Firewall (after SSH in):**
   ```bash
   # For Oracle Linux 8
   sudo firewall-cmd --permanent --add-port=22/tcp
   sudo firewall-cmd --permanent --add-port=8000/tcp
   sudo firewall-cmd --permanent --add-port=3001/tcp
   sudo firewall-cmd --reload
   
   # For Ubuntu
   sudo ufw allow 22/tcp
   sudo ufw allow 8000/tcp
   sudo ufw allow 3001/tcp
   sudo ufw enable
   ```

### Step 3: Connect to Your Instance

```bash
ssh -i ~/.ssh/id_rsa opc@YOUR_PUBLIC_IP
# For Ubuntu: ssh -i ~/.ssh/id_rsa ubuntu@YOUR_PUBLIC_IP
```

Replace `YOUR_PUBLIC_IP` with your instance's public IP address.

---

## 🚀 Deployment Methods

### Method 1: Automated Deployment Script (Recommended)

This is the **easiest and fastest** method.

#### On Your Oracle Cloud Instance:

```bash
# 1. Clone the repository
git clone https://github.com/vegas-max/Titan2.0.git
cd Titan2.0

# 2. Make deployment script executable
chmod +x deploy_oracle_cloud.sh

# 3. Run automated deployment
./deploy_oracle_cloud.sh

# 4. Follow the interactive prompts to configure your .env file
```

The script will:
- ✅ Detect your architecture (ARM or AMD)
- ✅ Install all dependencies (Node.js, Python, Redis)
- ✅ Configure system services
- ✅ Set up auto-start on boot
- ✅ Optimize for available resources
- ✅ Install and configure Titan

**Next Steps After Script Completes:**
1. Edit `.env` with your credentials:
   ```bash
   nano .env
   # Add your PRIVATE_KEY, API keys, etc.
   # Save: Ctrl+O, Enter, Ctrl+X
   ```

2. Deploy smart contract (if needed):
   ```bash
   npx hardhat run onchain/scripts/deploy.js --network polygon
   # Copy the deployed address to .env as EXECUTOR_ADDRESS_POLYGON
   ```

3. Start Titan:
   ```bash
   sudo systemctl start titan-brain
   sudo systemctl start titan-executor
   
   # Or use the convenience command:
   ./start_oracle.sh
   ```

4. Check status:
   ```bash
   sudo systemctl status titan-brain
   sudo systemctl status titan-executor
   ```

---

### Method 2: Docker Deployment

Use Docker for isolated, containerized deployment.

#### Prerequisites:
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Log out and back in for group changes to take effect
```

#### Deployment:
```bash
# 1. Clone repository
git clone https://github.com/vegas-max/Titan2.0.git
cd Titan2.0

# 2. Copy and configure environment
cp .env.example .env
nano .env
# Add your credentials

# 3. Build and start containers
docker-compose -f docker-compose.oracle.yml up -d

# 4. Check logs
docker-compose -f docker-compose.oracle.yml logs -f

# 5. Stop containers
docker-compose -f docker-compose.oracle.yml down
```

**Advantages:**
- ✅ Isolated environment
- ✅ Easy updates and rollbacks
- ✅ Consistent across platforms
- ✅ Simple backup/restore

---

### Method 3: Manual Deployment

For advanced users who want full control.

#### Step-by-Step:

**1. Update System:**
```bash
# Oracle Linux 8
sudo dnf update -y

# Ubuntu
sudo apt update && sudo apt upgrade -y
```

**2. Install Dependencies:**

<details>
<summary><b>For ARM Instance (Ampere)</b></summary>

```bash
# Install Node.js 18 (ARM64)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo bash -
sudo apt install -y nodejs  # Ubuntu
# OR
sudo dnf install -y nodejs  # Oracle Linux

# Install Python 3.11
sudo dnf install -y python3.11 python3.11-pip  # Oracle Linux
# OR
sudo apt install -y python3.11 python3.11-pip  # Ubuntu

# Install Redis
sudo dnf install -y redis  # Oracle Linux
# OR
sudo apt install -y redis-server  # Ubuntu

# Install build tools
sudo dnf groupinstall -y "Development Tools"  # Oracle Linux
# OR
sudo apt install -y build-essential  # Ubuntu

# Install Git
sudo dnf install -y git  # Oracle Linux
# OR
sudo apt install -y git  # Ubuntu
```

</details>

<details>
<summary><b>For AMD Instance</b></summary>

```bash
# Same as ARM but with x86_64 packages
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo bash -
sudo apt install -y nodejs python3.11 python3.11-pip redis-server build-essential git

# For Oracle Linux
sudo dnf install -y nodejs python3.11 python3.11-pip redis git
sudo dnf groupinstall -y "Development Tools"
```

</details>

**3. Clone and Setup Titan:**
```bash
# Clone repository
git clone https://github.com/vegas-max/Titan2.0.git
cd Titan2.0

# Run automated setup
./setup.sh

# Configure environment
cp .env.example .env
nano .env
# Add your PRIVATE_KEY, API keys, etc.
```

**4. Install System Services:**
```bash
# Copy service files
sudo cp systemd/titan-brain.service /etc/systemd/system/
sudo cp systemd/titan-executor.service /etc/systemd/system/
sudo cp systemd/titan-redis.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable services to start on boot
sudo systemctl enable titan-brain
sudo systemctl enable titan-executor
sudo systemctl enable titan-redis
```

**5. Start Services:**
```bash
sudo systemctl start titan-redis
sudo systemctl start titan-brain
sudo systemctl start titan-executor
```

**6. Check Status:**
```bash
sudo systemctl status titan-brain
sudo systemctl status titan-executor
sudo journalctl -u titan-brain -f  # View logs
```

---

## ⚙️ System Configuration

### Resource Optimization

#### For ARM Instance (4 OCPU, 24 GB RAM):
```bash
# Use default configuration - plenty of resources
# No optimization needed
```

#### For AMD Instance (1 OCPU, 1 GB RAM):
```bash
# IMPORTANT: Enable lightweight mode
nano .env

# Add these settings:
LIGHTWEIGHT_MODE=true
MAX_CONCURRENT_SCANS=5
ENABLE_GRAPH_VISUALIZATION=false
CACHE_SIZE_MB=100
```

See [LIGHTWEIGHT_MODE_GUIDE.md](LIGHTWEIGHT_MODE_GUIDE.md) for details.

### Memory Limits

Set memory limits to prevent OOM (Out of Memory) errors:

**For 1 GB RAM instance:**
```bash
# Edit service files
sudo nano /etc/systemd/system/titan-brain.service

# Add memory limit
[Service]
MemoryLimit=700M

sudo nano /etc/systemd/system/titan-executor.service
[Service]
MemoryLimit=250M

sudo systemctl daemon-reload
sudo systemctl restart titan-brain titan-executor
```

**For 24 GB RAM instance:**
No limits needed.

### Swap Configuration (For 1 GB RAM)

Add swap space to prevent crashes:

```bash
# Create 4GB swap file
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Verify
free -h
```

---

## 🎛️ Starting and Managing Titan

### Using Systemd (Recommended)

**Start Services:**
```bash
sudo systemctl start titan-redis
sudo systemctl start titan-brain
sudo systemctl start titan-executor
```

**Stop Services:**
```bash
sudo systemctl stop titan-executor
sudo systemctl stop titan-brain
sudo systemctl stop titan-redis
```

**Restart Services:**
```bash
sudo systemctl restart titan-brain
sudo systemctl restart titan-executor
```

**Check Status:**
```bash
sudo systemctl status titan-brain
sudo systemctl status titan-executor
```

**View Logs:**
```bash
# Real-time logs
sudo journalctl -u titan-brain -f
sudo journalctl -u titan-executor -f

# Last 100 lines
sudo journalctl -u titan-brain -n 100
```

**Enable Auto-Start on Boot:**
```bash
sudo systemctl enable titan-redis
sudo systemctl enable titan-brain
sudo systemctl enable titan-executor
```

### Using Convenience Scripts

```bash
# Start all components
./start_oracle.sh

# Stop all components
./stop_oracle.sh

# Restart all components
./restart_oracle.sh

# View status
./status_oracle.sh
```

### Manual Start (For Testing)

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Brain
cd ~/Titan2.0
python3 offchain/ml/brain.py

# Terminal 3: Executor
cd ~/Titan2.0
node offchain/execution/bot.js
```

---

## 📊 Monitoring and Maintenance

### Health Monitoring

**1. Built-in Health Check:**
```bash
./health-check.sh
```

**2. System Resources:**
```bash
# CPU and Memory usage
htop

# Disk usage
df -h

# Network usage
iftop
```

**3. Titan Metrics:**
```bash
# View recent trades
redis-cli LRANGE recent_trades 0 10

# Check total profit
redis-cli GET total_profit

# Check trade count
redis-cli GET trades_executed
```

### Web Dashboard (Optional)

Start the monitoring dashboard:

```bash
# Start dashboard
python3 live_operational_dashboard.py

# Access from browser (set up SSH tunnel first):
# On your local machine:
ssh -L 8000:localhost:8000 opc@YOUR_PUBLIC_IP

# Then open browser to:
http://localhost:8000
```

### Log Rotation

Prevent logs from filling disk:

```bash
# Create logrotate config
sudo nano /etc/logrotate.d/titan

# Add:
/home/opc/Titan2.0/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 opc opc
}
```

### Backup Strategy

**1. Backup Configuration:**
```bash
# Backup .env and important configs
tar -czf titan-backup-$(date +%Y%m%d).tar.gz .env config.json

# Copy to Object Storage or local machine
scp opc@YOUR_PUBLIC_IP:~/titan-backup-*.tar.gz ./backups/
```

**2. Automated Backups:**
```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * cd ~/Titan2.0 && tar -czf ~/backups/titan-backup-$(date +\%Y\%m\%d).tar.gz .env config.json
```

### Updates

**Update Titan:**
```bash
cd ~/Titan2.0

# Stop services
sudo systemctl stop titan-executor titan-brain

# Pull latest code
git pull origin main

# Update dependencies
npm install --legacy-peer-deps
pip3 install -r requirements.txt

# Recompile contracts (if needed)
npx hardhat compile

# Restart services
sudo systemctl start titan-brain titan-executor
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Out of Memory (OOM) Errors

**Symptoms:**
- Process killed unexpectedly
- "Killed" in logs
- System becomes unresponsive

**Solutions:**
```bash
# Enable lightweight mode
nano .env
# Set: LIGHTWEIGHT_MODE=true

# Add/increase swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Reduce concurrent operations
# In .env: MAX_CONCURRENT_SCANS=3
```

#### 2. Redis Connection Failed

**Symptoms:**
- "Error: Connection refused" in logs
- Brain can't publish signals

**Solutions:**
```bash
# Check if Redis is running
sudo systemctl status titan-redis

# Start Redis
sudo systemctl start titan-redis

# Check Redis connection
redis-cli ping
# Should return: PONG
```

#### 3. RPC Rate Limiting

**Symptoms:**
- "429 Too Many Requests" errors
- Slow opportunity detection

**Solutions:**
```bash
# Use multiple RPC providers
# In .env, add Alchemy as backup:
ALCHEMY_RPC_ETH=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY

# Reduce scan frequency
# In config.json: "scanInterval": 5000 (5 seconds)
```

#### 4. Node.js/Python Version Issues

**Symptoms:**
- Import errors
- Syntax errors
- "Module not found"

**Solutions:**
```bash
# Check versions
node -v  # Should be 18+
python3 --version  # Should be 3.11+

# Update if needed
sudo dnf install nodejs python3.11
```

#### 5. Permission Denied Errors

**Solutions:**
```bash
# Fix ownership
cd ~/Titan2.0
chmod +x *.sh
chown -R $USER:$USER .

# Fix log directory
sudo mkdir -p /var/log/titan
sudo chown $USER:$USER /var/log/titan
```

### Checking Logs

```bash
# Brain logs
sudo journalctl -u titan-brain -n 50

# Executor logs
sudo journalctl -u titan-executor -n 50

# All Titan logs
sudo journalctl -u titan-* -f

# Search for errors
sudo journalctl -u titan-brain | grep -i error
```

### Performance Issues

**CPU Usage Too High:**
```bash
# Reduce concurrent scans
# In .env: MAX_CONCURRENT_SCANS=5

# Increase scan interval
# In config.json: "scanInterval": 3000
```

**High Network Usage:**
```bash
# Enable caching
# In .env: ENABLE_CACHING=true
# In .env: CACHE_TTL=600

# Reduce RPC calls
# Use batch calls where possible
```

---

## 🔒 Security Hardening

### Essential Security Steps

**1. Firewall Configuration:**
```bash
# Only allow SSH from your IP
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="YOUR_IP" port port="22" protocol="tcp" accept'
sudo firewall-cmd --permanent --remove-service=ssh
sudo firewall-cmd --reload
```

**2. Change SSH Port (Optional):**
```bash
sudo nano /etc/ssh/sshd_config
# Change: Port 22 to Port 2222
sudo systemctl restart sshd

# Update firewall
sudo firewall-cmd --permanent --add-port=2222/tcp
sudo firewall-cmd --permanent --remove-port=22/tcp
sudo firewall-cmd --reload
```

**3. Disable Root Login:**
```bash
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no
sudo systemctl restart sshd
```

**4. Install Fail2Ban:**
```bash
sudo dnf install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

**5. Enable Automatic Security Updates:**
```bash
# Oracle Linux
sudo dnf install -y dnf-automatic
sudo systemctl enable --now dnf-automatic.timer

# Ubuntu
sudo apt install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

**6. Secure .env File:**
```bash
chmod 600 .env
# Only owner can read/write
```

**7. Use Dedicated Wallet:**
- ⚠️ **NEVER** use your main wallet
- Fund with only enough for gas fees
- Keep private key secure
- Consider hardware wallet for production

**8. Monitor Failed Login Attempts:**
```bash
# View failed SSH attempts
sudo journalctl -u sshd | grep -i failed

# Check fail2ban status
sudo fail2ban-client status sshd
```

### Environment Security

**Encrypt Sensitive Data:**
```bash
# Install ansible-vault
pip3 install ansible

# Encrypt .env
ansible-vault encrypt .env

# Decrypt when needed
ansible-vault decrypt .env

# Edit encrypted file
ansible-vault edit .env
```

### Network Security

**1. Use Private IP for Redis:**
```bash
# Edit Redis config
sudo nano /etc/redis/redis.conf

# Set bind to localhost only
bind 127.0.0.1 ::1

# Require password
requirepass your_strong_password_here

sudo systemctl restart redis
```

**2. Enable HTTPS for Dashboard:**
```bash
# Generate self-signed certificate
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/titan.key \
  -out /etc/ssl/certs/titan.crt

# Update dashboard config to use HTTPS
```

---

## 📈 Performance Tuning for Oracle Cloud

### For ARM Instance (Recommended Settings)

```bash
# .env settings for optimal performance
MAX_CONCURRENT_SCANS=20
ENABLE_PARALLEL_QUOTES=true
CACHE_SIZE_MB=1000
WORKER_THREADS=4
```

### For AMD Instance (1GB RAM)

```bash
# .env settings for limited resources
LIGHTWEIGHT_MODE=true
MAX_CONCURRENT_SCANS=3
ENABLE_PARALLEL_QUOTES=false
CACHE_SIZE_MB=50
WORKER_THREADS=1
ENABLE_GRAPH_VISUALIZATION=false
```

### Network Optimization

```bash
# Use Oracle's high-speed network
# Already optimized by default

# Enable keep-alive for RPC connections
# In .env:
RPC_KEEP_ALIVE=true
RPC_TIMEOUT=30000
```

---

## 🎯 Quick Reference Commands

```bash
# Start Titan
sudo systemctl start titan-brain titan-executor

# Stop Titan
sudo systemctl stop titan-executor titan-brain

# Restart Titan
sudo systemctl restart titan-brain titan-executor

# View status
sudo systemctl status titan-brain titan-executor

# View logs
sudo journalctl -u titan-brain -f

# Health check
./health-check.sh

# Update Titan
git pull && npm install --legacy-peer-deps && pip3 install -r requirements.txt

# Check resources
htop

# Check disk
df -h

# Backup config
tar -czf backup-$(date +%Y%m%d).tar.gz .env config.json
```

---

## 📞 Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section above
2. Review logs: `sudo journalctl -u titan-brain -n 100`
3. Run health check: `./health-check.sh`
4. Check GitHub issues: https://github.com/vegas-max/Titan2.0/issues

---

## ⚠️ Important Reminders

- ✅ Always use **paper mode** first to test: `EXECUTION_MODE=PAPER` in `.env`
- ✅ Start with **small gas amounts** (~$20-50)
- ✅ Monitor for the **first 24 hours** closely
- ✅ Keep your **system updated** with security patches
- ✅ **Backup your .env** file regularly
- ✅ Never share your **private key**
- ✅ Use the **ARM instance** (VM.Standard.A1.Flex) for best results

---

**🚀 You're now ready to run Titan on Oracle Cloud!**

For additional guides, see:
- [QUICKSTART.md](QUICKSTART.md) - Basic Titan usage
- [LIGHTWEIGHT_MODE_GUIDE.md](LIGHTWEIGHT_MODE_GUIDE.md) - Resource optimization
- [ARM_OPTIMIZATION_GUIDE.md](ARM_OPTIMIZATION_GUIDE.md) - ARM-specific tuning
- [OPERATIONS_GUIDE.md](OPERATIONS_GUIDE.md) - Day-to-day operations
