# ⚡ Oracle Cloud Always Free - Quick Start

**Get Titan running on Oracle Cloud in 15 minutes!**

---

## 📝 Prerequisites

Before you start, have these ready:

1. ✅ Oracle Cloud Free Tier account (https://www.oracle.com/cloud/free/)
2. ✅ SSH key pair (`ssh-keygen -t rsa -b 4096`)
3. ✅ Wallet private key (dedicated wallet, NOT your main one)
4. ✅ API keys ready:
   - Infura Project ID
   - Alchemy API key
   - Li.Fi API key

---

## 🚀 Step 1: Create Oracle Cloud Instance (5 minutes)

1. **Login to Oracle Cloud**: https://cloud.oracle.com/

2. **Create Compute Instance**:
   - Go to: **Compute** → **Instances** → **Create Instance**
   
3. **Configure**:
   - **Name**: `titan-arbitrage-bot`
   - **Image**: Oracle Linux 8 or Ubuntu 22.04
   - **Shape**: **VM.Standard.A1.Flex** (ARM) ← **RECOMMENDED**
     - OCPUs: **4**
     - Memory: **24 GB**
   - Alternative: VM.Standard.E2.1.Micro (1 OCPU, 1 GB RAM)
   - **Public IP**: ✅ Enabled
   - **SSH Key**: Upload your `id_rsa.pub`
   - **Boot Volume**: 50 GB

4. **Add Firewall Rules**:
   - Navigate to: **Networking** → **VCN** → **Security Lists**
   - Add Ingress Rule: Port **22** (SSH) from `0.0.0.0/0`
   - Add Ingress Rule: Port **8000** (Dashboard) from your IP

5. **Note your public IP address**: `_______________`

---

## 🔧 Step 2: Connect and Deploy (5 minutes)

### Connect via SSH
```bash
ssh -i ~/.ssh/id_rsa opc@YOUR_PUBLIC_IP
# For Ubuntu: ssh -i ~/.ssh/id_rsa ubuntu@YOUR_PUBLIC_IP
```

### Clone and Deploy (One Command!)
```bash
# Clone repository
git clone https://github.com/vegas-max/Titan2.0.git
cd Titan2.0

# Run automated deployment
chmod +x deploy_oracle_cloud.sh
./deploy_oracle_cloud.sh
```

The script will:
- ✅ Detect your system (ARM or AMD)
- ✅ Install all dependencies (Node.js, Python, Redis)
- ✅ Setup Titan
- ✅ Configure systemd services
- ✅ Create management scripts
- ✅ Optimize for your instance type

**Note**: When asked about Redis, you can skip it (type 'n') - Titan uses file-based signals and Redis is optional.

---

## ⚙️ Step 3: Configure (3 minutes)

### Edit .env file
```bash
nano .env
```

**Add your credentials** (minimum required):
```bash
# Wallet
PRIVATE_KEY=0xYOUR_PRIVATE_KEY_HERE

# RPC Endpoints
RPC_POLYGON=https://polygon-mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID
ALCHEMY_RPC_POLYGON=https://polygon-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY

# DEX Aggregator
LIFI_API_KEY=your_lifi_api_key_here

# Execution Mode (PAPER for testing - REQUIRED!)
EXECUTION_MODE=PAPER
```

**Save**: `Ctrl+O`, Enter, `Ctrl+X`

### Secure .env file
```bash
chmod 600 .env
```

---

## 🎯 Step 4: Start Titan (2 minutes)

### Start Services
```bash
./start_oracle.sh
```

### Check Status
```bash
./status_oracle.sh
```

You should see:
- ✅ Brain: **Running**
- ✅ Executor: **Running**

### Run Health Check
```bash
./oracle_health_check.sh
```

---

## 📊 Step 5: Monitor (Ongoing)

### View Live Logs
```bash
# Brain logs (opportunity detection)
sudo journalctl -u titan-brain -f

# Executor logs (trade execution)
sudo journalctl -u titan-executor -f
```

### Check Signal System
```bash
# View recent signals
ls -lh signals/outgoing/

# Check signal files
cat signals/outgoing/*.json | head -20
```

---

## ✅ Verification Checklist

Quick checklist to ensure everything is working:

- [ ] **Services Running**: `./status_oracle.sh` shows all green
- [ ] **No Critical Errors**: `sudo journalctl -u titan-brain -n 50 | grep -i error`
- [ ] **Signals Being Created**: `ls signals/outgoing/` shows .json files
- [ ] **Health Check Passes**: `./oracle_health_check.sh` returns 0 issues
- [ ] **Paper Mode Active**: `grep EXECUTION_MODE .env` shows `PAPER`

---

## 🎮 Management Commands

### Service Control
```bash
./start_oracle.sh          # Start all Titan services
./stop_oracle.sh           # Stop all Titan services
./restart_oracle.sh        # Restart all services
./status_oracle.sh         # Check status
```

### Monitoring
```bash
./oracle_health_check.sh           # Comprehensive health check
sudo journalctl -u titan-brain -f  # View Brain logs
sudo journalctl -u titan-executor -f  # View Executor logs
htop                               # System resources
```

### Logs
```bash
# Last 50 lines
sudo journalctl -u titan-brain -n 50

# Last hour
sudo journalctl -u titan-* --since "1 hour ago"

# Follow all Titan logs
sudo journalctl -u titan-* -f

# Search for errors
sudo journalctl -u titan-* | grep -i error
```

---

## 🧪 Testing Phase (REQUIRED!)

**⚠️ IMPORTANT**: You MUST test in Paper Mode before going live!

### Paper Mode Testing (24-48 hours minimum)
```bash
# Verify paper mode is active
grep EXECUTION_MODE .env
# Should show: EXECUTION_MODE=PAPER
```

**Monitor for at least 24-48 hours:**
- Check logs every 4-6 hours
- Verify opportunities are being detected
- Confirm trades are simulated (not executed)
- Ensure no critical errors
- Verify system stability

### Check Paper Trading Results
```bash
# If Redis is installed
redis-cli GET total_profit_paper
redis-cli GET trades_executed_paper

# Or check logs
sudo journalctl -u titan-executor --since "24 hours ago" | grep -i "paper"
```

---

## 🚀 Going Live (Only After Successful Testing!)

**After 24-48 hours of successful paper trading:**

### Switch to Live Mode
```bash
nano .env
# Change: EXECUTION_MODE=LIVE
```

### Restart Services
```bash
./restart_oracle.sh
```

### Monitor Closely (First 24 hours)
- Check logs every 2-4 hours
- Watch for executed trades
- Verify profitability
- Monitor gas usage
- Be ready to stop: `./stop_oracle.sh`

---

## 🔐 Security Checklist

- [ ] ✅ Using dedicated wallet (NOT main wallet)
- [ ] ✅ .env file permissions set to 600
- [ ] ✅ SSH access limited to your IP (recommended)
- [ ] ✅ Started with small gas amount ($20-50)
- [ ] ✅ Tested in PAPER mode for 24+ hours
- [ ] ✅ Firewall configured properly

---

## 🆘 Quick Troubleshooting

### Services Won't Start
```bash
# Check logs
sudo journalctl -u titan-brain -n 50
sudo journalctl -u titan-executor -n 50

# Verify .env is configured
cat .env | grep PRIVATE_KEY

# Restart services
./restart_oracle.sh
```

### Out of Memory (AMD 1GB instance)
```bash
# Enable lightweight mode
nano .env
# Add: LIGHTWEIGHT_MODE=true

# Add swap space
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Restart
./restart_oracle.sh
```

### Redis Not Working (Optional - Not Required)
```bash
# Redis is OPTIONAL - Titan uses file-based signals
# If you want Redis, check status:
sudo systemctl status titan-redis

# Start if needed
sudo systemctl start titan-redis

# Test connection
redis-cli ping
```

### No Opportunities Detected
```bash
# Check RPC connection
curl -X POST -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' \
  YOUR_RPC_URL

# Check brain logs for errors
sudo journalctl -u titan-brain -n 100 | grep -i error

# Verify config
cat config.json | grep -A 5 "polygon"
```

---

## 📚 Full Documentation

For detailed information:
- **Complete Guide**: [ORACLE_CLOUD_DEPLOYMENT.md](ORACLE_CLOUD_DEPLOYMENT.md)
- **Deployment Checklist**: [ORACLE_DEPLOYMENT_CHECKLIST.md](ORACLE_DEPLOYMENT_CHECKLIST.md)
- **Quick Reference**: [ORACLE_QUICK_REFERENCE.md](ORACLE_QUICK_REFERENCE.md)
- **Troubleshooting**: [ORACLE_TROUBLESHOOTING.md](ORACLE_TROUBLESHOOTING.md)

---

## 🎯 Instance Recommendations

### ⭐ RECOMMENDED: ARM A1.Flex
- **4 OCPUs**, **24 GB RAM**
- Best performance
- Can run multiple concurrent scans
- No memory issues
- **Free forever**

### Alternative: AMD E2.1.Micro
- **1 OCPU**, **1 GB RAM**
- Requires lightweight mode
- Need swap space
- Limited concurrent scans
- Still **free forever**

---

## 💡 Pro Tips

1. **Always start in PAPER mode** - Test for 24-48 hours minimum
2. **Use ARM instance** - Much better performance
3. **Monitor closely first 24 hours** when going live
4. **Start with small amounts** - Limit wallet to $20-50 initially
5. **Check logs daily** - `sudo journalctl -u titan-* --since "24 hours ago" | grep -i error`
6. **Backup weekly** - `tar -czf backup-$(date +%Y%m%d).tar.gz .env config.json`
7. **Update monthly** - Keep Titan and system updated

---

## 📞 Need Help?

1. Run health check: `./oracle_health_check.sh`
2. Check troubleshooting guide: [ORACLE_TROUBLESHOOTING.md](ORACLE_TROUBLESHOOTING.md)
3. Review logs: `sudo journalctl -u titan-brain -n 100`
4. GitHub Issues: https://github.com/vegas-max/Titan2.0/issues

---

## ⚡ You're All Set!

Titan is now running on Oracle Cloud Always Free tier!

**Remember:**
- ✅ Currently in **PAPER MODE** (safe testing)
- ✅ Monitor for **24-48 hours** before going live
- ✅ Use **dedicated wallet** with limited funds
- ✅ Check **logs regularly**
- ✅ Have **emergency stop ready**: `./stop_oracle.sh`

**Happy Trading! 🚀**
