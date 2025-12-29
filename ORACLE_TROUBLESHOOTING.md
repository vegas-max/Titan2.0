# 🔧 Oracle Cloud Deployment - Troubleshooting Guide

Quick reference for common issues when deploying Titan to Oracle Cloud.

## 🔍 Quick Diagnostics

```bash
# Run comprehensive health check
./oracle_health_check.sh

# Check service status
./status_oracle.sh

# View recent logs
sudo journalctl -u titan-brain -n 50
sudo journalctl -u titan-executor -n 50
```

---

## 🚨 Common Issues & Solutions

### 1. Out of Memory (OOM) Errors

**Symptoms:**
- Process killed unexpectedly
- "Killed" message in logs
- System becomes unresponsive
- Service restarts frequently

**Quick Fix:**
```bash
# Enable lightweight mode
nano .env
# Add or modify: LIGHTWEIGHT_MODE=true

# Add swap space
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Reduce memory limits in services
sudo nano /etc/systemd/system/titan-brain.service
# Change MemoryLimit=4G to MemoryLimit=700M

sudo systemctl daemon-reload
sudo systemctl restart titan-brain titan-executor
```

**Prevention:**
- Use ARM instance (24GB RAM) instead of AMD Micro (1GB RAM)
- Monitor memory: `watch -n 5 free -h`

---

### 2. Redis Connection Failed

**Symptoms:**
- "Error: Connection refused" in logs
- Brain can't publish signals
- Executor not receiving trades

**Quick Fix:**
```bash
# Check Redis status
sudo systemctl status titan-redis

# Start Redis
sudo systemctl start titan-redis

# Test connection
redis-cli ping
# Should return: PONG

# If Redis CLI not working, check if it's listening
sudo netstat -tlnp | grep 6379

# Restart services after Redis is up
./restart_oracle.sh
```

**Prevention:**
- Ensure Redis starts before other services (systemd handles this)
- Check Redis logs: `sudo journalctl -u titan-redis -n 50`

---

### 3. RPC Rate Limiting / 429 Errors

**Symptoms:**
- "429 Too Many Requests" in logs
- Slow opportunity detection
- Failed RPC calls

**Quick Fix:**
```bash
# Add backup RPC providers in .env
nano .env

# Add Alchemy as backup:
ALCHEMY_RPC_ETH=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
ALCHEMY_RPC_POLY=https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY

# Reduce scan frequency
# In config.json:
nano config.json
# Increase scanInterval from 3000 to 5000 (5 seconds)

# Restart services
./restart_oracle.sh
```

**Prevention:**
- Use paid tier RPC providers for production
- Implement request caching
- Monitor RPC usage

---

### 4. Services Won't Start

**Symptoms:**
- `systemctl start titan-brain` fails
- Service shows "failed" status
- Immediate crash on start

**Diagnostic Steps:**
```bash
# 1. Check service status
sudo systemctl status titan-brain
sudo systemctl status titan-executor

# 2. View detailed logs
sudo journalctl -u titan-brain -n 100 --no-pager
sudo journalctl -u titan-executor -n 100 --no-pager

# 3. Check if files exist
ls -la ~/Titan2.0/offchain/ml/brain.py
ls -la ~/Titan2.0/offchain/execution/bot.js

# 4. Check permissions
ls -la ~/Titan2.0/.env

# 5. Test manually
cd ~/Titan2.0
python3 offchain/ml/brain.py
# If it works manually but not as service, check service file
```

**Common Fixes:**
```bash
# Fix permissions
chmod +x ~/Titan2.0/offchain/ml/brain.py
chmod 600 ~/Titan2.0/.env

# Recreate service files
cd ~/Titan2.0
./deploy_oracle_cloud.sh
# Choose to reinstall services

# Check if .env is configured
grep PRIVATE_KEY .env
# Should NOT be empty or contain "YOUR_PRIVATE_KEY"
```

---

### 5. Node.js/Python Not Found

**Symptoms:**
- "node: command not found"
- "python3: command not found"
- Services fail to start

**Quick Fix:**
```bash
# Check versions
node -v
python3 --version

# If not installed, run deployment script
./deploy_oracle_cloud.sh

# Or install manually:
# Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo bash -
sudo apt install -y nodejs

# Python 3.11
sudo apt install -y python3.11 python3.11-pip
```

---

### 6. High CPU Usage

**Symptoms:**
- CPU at 90-100% constantly
- System sluggish
- Other processes slow

**Quick Fix:**
```bash
# Check what's using CPU
htop
# Look for python3 or node processes

# Reduce concurrent scans
nano .env
# Add or modify:
MAX_CONCURRENT_SCANS=3  # For 1GB RAM instance
MAX_CONCURRENT_SCANS=10 # For 24GB RAM instance

# Increase scan interval
nano config.json
# Increase scanInterval to 5000 or higher

./restart_oracle.sh
```

---

### 7. .env Configuration Issues

**Symptoms:**
- "PRIVATE_KEY not set" errors
- RPC connection failures
- Missing API key errors

**Quick Fix:**
```bash
# Check .env exists
ls -la .env

# Verify required fields
grep -E "PRIVATE_KEY|RPC_POLYGON|LIFI_API_KEY" .env

# Copy from template if missing
cp .env.example .env

# Edit with your credentials
nano .env

# Required fields:
# - PRIVATE_KEY=0x...
# - RPC_POLYGON=https://...
# - RPC_ETHEREUM=https://...
# - LIFI_API_KEY=...

# Restart after editing
./restart_oracle.sh
```

---

### 8. Docker Issues

**Symptoms:**
- Container crashes
- "Cannot connect to Docker daemon"
- Network errors between containers

**Quick Fix:**
```bash
# Check Docker status
sudo systemctl status docker

# Start Docker
sudo systemctl start docker

# View container logs
docker-compose -f docker-compose.oracle.yml logs -f

# Restart containers
docker-compose -f docker-compose.oracle.yml down
docker-compose -f docker-compose.oracle.yml up -d

# Rebuild if needed
docker-compose -f docker-compose.oracle.yml build --no-cache
docker-compose -f docker-compose.oracle.yml up -d
```

---

### 9. Firewall Blocking Connections

**Symptoms:**
- Can't access dashboard
- SSH connection issues
- External API calls fail

**Quick Fix:**
```bash
# Check firewall status
sudo firewall-cmd --list-all  # Oracle Linux
sudo ufw status               # Ubuntu

# Open required ports
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

# Or for Ubuntu
sudo ufw allow 8000/tcp

# Verify port is open
sudo netstat -tlnp | grep 8000
```

---

### 10. Disk Space Full

**Symptoms:**
- "No space left on device"
- Can't write logs
- Services crash

**Quick Fix:**
```bash
# Check disk usage
df -h

# Find large files
du -sh /home/opc/* | sort -h

# Clean up logs
sudo journalctl --vacuum-time=7d
sudo journalctl --vacuum-size=500M

# Clean npm cache
npm cache clean --force

# Clean pip cache
pip3 cache purge

# Remove old Docker images
docker system prune -a

# Clean APT cache (Ubuntu)
sudo apt clean

# Clean DNF cache (Oracle Linux)
sudo dnf clean all
```

---

## 📊 Monitoring Commands

### System Resources
```bash
# Real-time memory usage
watch -n 2 free -h

# CPU and process monitor
htop

# Disk usage
df -h
du -sh /* | sort -h

# Network usage
iftop

# System load
uptime
```

### Service Management
```bash
# All Titan services
systemctl status titan-*

# Specific service
systemctl status titan-brain

# Enable auto-start
sudo systemctl enable titan-brain titan-executor

# Disable auto-start
sudo systemctl disable titan-brain titan-executor
```

### Logs
```bash
# Real-time logs
sudo journalctl -u titan-brain -f
sudo journalctl -u titan-executor -f

# All Titan logs
sudo journalctl -u titan-* -f

# Last N lines
sudo journalctl -u titan-brain -n 100

# Since specific time
sudo journalctl -u titan-brain --since "1 hour ago"
sudo journalctl -u titan-brain --since "2024-12-29 10:00:00"

# Export logs
sudo journalctl -u titan-brain --since "today" > brain-logs.txt
```

### Redis
```bash
# Check connection
redis-cli ping

# Get all keys
redis-cli KEYS "*"

# Get specific value
redis-cli GET total_profit
redis-cli GET trades_executed

# Monitor Redis commands
redis-cli MONITOR

# Check memory usage
redis-cli INFO memory
```

---

## 🔐 Security Check

```bash
# Verify .env permissions
ls -la .env
# Should be: -rw------- (600)

# Fix if needed
chmod 600 .env

# Check Redis is localhost only
sudo netstat -tlnp | grep 6379
# Should show 127.0.0.1:6379

# Check for failed SSH attempts
sudo journalctl -u sshd | grep -i failed

# Review firewall rules
sudo firewall-cmd --list-all
```

---

## 🆘 Emergency Procedures

### Complete System Reset
```bash
# Stop all services
./stop_oracle.sh

# Remove service files
sudo rm /etc/systemd/system/titan-*.service
sudo systemctl daemon-reload

# Clean installation
cd ~/Titan2.0
git pull origin main
npm install --legacy-peer-deps
pip3 install -r requirements.txt
npx hardhat compile

# Re-run deployment
./deploy_oracle_cloud.sh

# Configure .env
nano .env

# Start services
./start_oracle.sh
```

### Emergency Shutdown
```bash
# Stop Titan immediately
./stop_oracle.sh

# Or if script not working
sudo systemctl stop titan-executor
sudo systemctl stop titan-brain
sudo systemctl stop titan-redis

# Kill processes if services won't stop
pkill -f brain.py
pkill -f bot.js
```

### Restore from Backup
```bash
# Stop services
./stop_oracle.sh

# Restore .env from backup
cp ~/backups/titan-backup-YYYYMMDD.tar.gz .
tar -xzf titan-backup-YYYYMMDD.tar.gz

# Restart services
./start_oracle.sh
```

---

## 📞 Getting More Help

1. **Run Health Check:**
   ```bash
   ./oracle_health_check.sh
   ```

2. **Check Full Documentation:**
   - [ORACLE_CLOUD_DEPLOYMENT.md](ORACLE_CLOUD_DEPLOYMENT.md)
   - [OPERATIONS_GUIDE.md](OPERATIONS_GUIDE.md)

3. **Collect Debug Info:**
   ```bash
   # System info
   uname -a > debug-info.txt
   free -h >> debug-info.txt
   df -h >> debug-info.txt
   
   # Service status
   systemctl status titan-* >> debug-info.txt
   
   # Recent logs
   sudo journalctl -u titan-brain -n 100 >> debug-info.txt
   sudo journalctl -u titan-executor -n 100 >> debug-info.txt
   ```

4. **GitHub Issues:**
   - https://github.com/vegas-max/Titan2.0/issues

---

## ✅ Prevention Checklist

- [ ] Use ARM instance (VM.Standard.A1.Flex) for better resources
- [ ] Configure swap for low-memory instances
- [ ] Set up monitoring and alerts
- [ ] Enable auto-restart for services
- [ ] Configure log rotation
- [ ] Regular backups of .env and config
- [ ] Monitor disk space weekly
- [ ] Review logs daily for errors
- [ ] Update system and dependencies monthly
- [ ] Test in paper mode before going live

---

**Remember:** Most issues can be resolved by checking logs and restarting services. When in doubt, run the health check script first!
