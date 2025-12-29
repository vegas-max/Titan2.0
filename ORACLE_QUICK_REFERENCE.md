# ⚡ Oracle Cloud Quick Reference

One-page reference for managing Titan on Oracle Cloud.

## 🚀 Common Commands

### Service Management
```bash
./start_oracle.sh                  # Start all services
./stop_oracle.sh                   # Stop all services
./restart_oracle.sh                # Restart services
./status_oracle.sh                 # Check status
```

### System Commands
```bash
sudo systemctl start titan-brain titan-executor    # Start
sudo systemctl stop titan-executor titan-brain     # Stop
sudo systemctl restart titan-brain titan-executor  # Restart
sudo systemctl status titan-brain titan-executor   # Status
```

### Logs
```bash
sudo journalctl -u titan-brain -f              # Follow brain logs
sudo journalctl -u titan-executor -f           # Follow executor logs
sudo journalctl -u titan-brain -n 50           # Last 50 lines
sudo journalctl -u titan-* --since "1h ago"    # Last hour all services
```

### Health & Monitoring
```bash
./oracle_health_check.sh           # Run health check
htop                               # Resource monitor
free -h                            # Memory usage
df -h                              # Disk usage
```

## 📝 Configuration

### Edit Configuration
```bash
nano .env                          # Main configuration
nano config.json                   # Advanced settings
```

### Key .env Settings
```bash
# Required
PRIVATE_KEY=0x...                  # Your wallet private key
RPC_POLYGON=https://...            # Polygon RPC endpoint
LIFI_API_KEY=...                   # Li.Fi API key

# Performance (ARM instance)
LIGHTWEIGHT_MODE=false
MAX_CONCURRENT_SCANS=20
WORKER_THREADS=4

# Performance (AMD Micro)
LIGHTWEIGHT_MODE=true
MAX_CONCURRENT_SCANS=3
WORKER_THREADS=1

# Mode
EXECUTION_MODE=PAPER               # Paper trading (safe)
EXECUTION_MODE=LIVE                # Live trading (real money!)
```

## 🔍 Troubleshooting

### Quick Diagnostics
```bash
./oracle_health_check.sh                                    # Health check
sudo systemctl status titan-*                               # All services
redis-cli ping                                              # Redis check
curl -s http://localhost:8000/health                        # API check
```

### Common Fixes
```bash
# Services won't start
sudo systemctl restart titan-brain titan-executor
sudo journalctl -u titan-brain -n 50                        # Check errors

# Out of memory
nano .env                                                   # Set LIGHTWEIGHT_MODE=true
sudo swapon --show                                          # Check swap

# Redis not working
sudo systemctl restart titan-redis
redis-cli ping                                              # Test

# High CPU usage
nano .env                                                   # Reduce MAX_CONCURRENT_SCANS
```

## 📊 Performance Tuning

### ARM Instance (24GB RAM)
```bash
# .env settings
LIGHTWEIGHT_MODE=false
MAX_CONCURRENT_SCANS=20
CACHE_SIZE_MB=1000
WORKER_THREADS=4
```

### AMD Micro (1GB RAM)
```bash
# .env settings
LIGHTWEIGHT_MODE=true
MAX_CONCURRENT_SCANS=3
CACHE_SIZE_MB=50
WORKER_THREADS=1
ENABLE_GRAPH_VISUALIZATION=false

# Add swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 🔐 Security

### File Permissions
```bash
chmod 600 .env                     # Secure .env file
ls -la .env                        # Verify: -rw-------
```

### Firewall
```bash
sudo firewall-cmd --list-all       # Oracle Linux
sudo ufw status                    # Ubuntu
```

### Updates
```bash
# System
sudo dnf update -y                 # Oracle Linux
sudo apt update && sudo apt upgrade -y    # Ubuntu

# Titan
cd ~/Titan2.0
git pull origin main
npm install --legacy-peer-deps
pip3 install -r requirements.txt
```

## 💾 Backup & Restore

### Backup
```bash
# Manual backup
tar -czf ~/backup-$(date +%Y%m%d).tar.gz .env config.json

# Copy to local machine
scp opc@YOUR_IP:~/backup-*.tar.gz ./
```

### Restore
```bash
cd ~/Titan2.0
tar -xzf ~/backup-YYYYMMDD.tar.gz
./restart_oracle.sh
```

## 📈 Monitoring

### Redis Stats
```bash
redis-cli INFO stats               # Statistics
redis-cli DBSIZE                   # Number of keys
redis-cli GET total_profit         # Total profit
redis-cli GET trades_executed      # Trade count
```

### System Resources
```bash
free -h                            # Memory
df -h                              # Disk
uptime                             # Load average
top -b -n 1 | head -20            # Top processes
```

## 🚨 Emergency

### Stop Everything
```bash
./stop_oracle.sh
# Or manually:
sudo systemctl stop titan-executor titan-brain titan-redis
```

### Kill Stuck Processes
```bash
pkill -f brain.py
pkill -f bot.js
```

### Complete Reset
```bash
./stop_oracle.sh
cd ~/Titan2.0
git pull origin main
./deploy_oracle_cloud.sh
nano .env                          # Configure
./start_oracle.sh
```

## 📚 Documentation

- **ORACLE_CLOUD_DEPLOYMENT.md** - Full deployment guide
- **ORACLE_TROUBLESHOOTING.md** - Troubleshooting guide
- **QUICKSTART.md** - Titan quick start
- **OPERATIONS_GUIDE.md** - Operations manual

## 🌐 Access

### SSH
```bash
ssh opc@YOUR_PUBLIC_IP            # Oracle Linux
ssh ubuntu@YOUR_PUBLIC_IP         # Ubuntu
```

### Dashboard
```bash
# Start dashboard
python3 live_operational_dashboard.py

# Access via SSH tunnel from local machine:
ssh -L 8000:localhost:8000 opc@YOUR_PUBLIC_IP
# Then browse to: http://localhost:8000
```

## ⚡ Instance Types

### ARM A1.Flex (Recommended)
- 4 OCPUs
- 24 GB RAM
- Best for Titan
- Free forever

### AMD E2.1.Micro
- 1 OCPU
- 1 GB RAM
- Requires lightweight mode
- Free forever

## 🎯 Key Files

```
~/Titan2.0/
├── .env                           # Configuration (SECURE!)
├── config.json                    # Advanced config
├── deploy_oracle_cloud.sh         # Deployment script
├── start_oracle.sh                # Start services
├── stop_oracle.sh                 # Stop services
├── restart_oracle.sh              # Restart services
├── status_oracle.sh               # Check status
├── oracle_health_check.sh         # Health check
└── systemd/                       # Service files
    ├── titan-brain.service.template
    ├── titan-executor.service.template
    └── titan-redis.service.template
```

## 💡 Pro Tips

1. **Always use Paper Mode first:**
   ```bash
   # In .env:
   EXECUTION_MODE=PAPER
   ```

2. **Monitor for 24 hours before going live**

3. **Use ARM instance for best performance**

4. **Set up swap on low-memory instances**

5. **Check logs daily:**
   ```bash
   sudo journalctl -u titan-* --since "24 hours ago" | grep -i error
   ```

6. **Backup .env weekly:**
   ```bash
   tar -czf ~/backup-$(date +%Y%m%d).tar.gz .env config.json
   ```

7. **Update monthly:**
   ```bash
   cd ~/Titan2.0 && git pull && npm install --legacy-peer-deps
   ```

---

**Need help?** Run `./oracle_health_check.sh` or check `ORACLE_TROUBLESHOOTING.md`
