# 📊 Oracle Cloud Dashboard Access Guide

**Complete guide for accessing the Titan real-time monitoring dashboard on Oracle Cloud**

---

## 🎯 Quick Answer

After deploying to Oracle Cloud, access the dashboard using an **SSH tunnel**:

```bash
# On your LOCAL machine (not on Oracle Cloud)
ssh -L 8000:localhost:8000 opc@YOUR_ORACLE_PUBLIC_IP

# Then open your browser to:
http://localhost:8000
```

---

## 📋 Prerequisites

Before accessing the dashboard:

1. ✅ Titan deployed and running on Oracle Cloud
2. ✅ Services started: `./start_oracle.sh`
3. ✅ Dashboard script available: `live_operational_dashboard.py`
4. ✅ Your Oracle Cloud instance public IP address

---

## 🚀 Step-by-Step Dashboard Access

### Step 1: Start Dashboard on Oracle Cloud

**SSH into your Oracle Cloud instance:**
```bash
ssh opc@YOUR_PUBLIC_IP
```

**Navigate to Titan directory:**
```bash
cd ~/Titan2.0
```

**Start the dashboard:**
```bash
python3 live_operational_dashboard.py
```

**Expected output:**
```
🚀 Titan Operational Dashboard Starting...
📊 Dashboard running on http://localhost:8000
✅ Real-time monitoring active
```

**Keep this terminal open** - the dashboard is now running on port 8000.

---

### Step 2: Create SSH Tunnel (On Your Local Machine)

**Open a NEW terminal on your LOCAL computer** (not on Oracle Cloud):

```bash
ssh -L 8000:localhost:8000 opc@YOUR_ORACLE_PUBLIC_IP
```

**What this does:**
- `-L 8000:localhost:8000` - Forwards local port 8000 to remote port 8000
- Creates a secure tunnel through SSH
- Keeps your dashboard secure (not exposed to internet)

**Example:**
```bash
ssh -L 8000:localhost:8000 opc@129.213.45.67
```

**Keep this terminal open** - the tunnel must stay active.

---

### Step 3: Access Dashboard in Browser

**Open your web browser and navigate to:**
```
http://localhost:8000
```

**You should see:**
- 📊 Real-time trading metrics
- 💰 Profit/loss statistics
- 📈 Opportunity detection graphs
- 🔄 Active trades monitoring
- ⚡ System health indicators

---

## 🎨 Dashboard Features

### Real-Time Metrics:
- **Total Profit/Loss** - Cumulative P&L
- **Active Opportunities** - Current scans
- **Trades Executed** - Total trade count
- **Success Rate** - Win/loss ratio
- **Gas Spent** - Total gas costs
- **System Uptime** - Runtime duration

### Live Monitoring:
- 🔴 Real-time opportunity detection
- 📊 Profit trend charts
- 🌐 Network status
- 💾 Memory/CPU usage
- 🔄 Recent trade history
- ⚠️ Error logs and alerts

---

## 🔐 Security Configuration

### Option 1: SSH Tunnel (Recommended - Already Configured)

**Advantages:**
- ✅ Most secure
- ✅ No firewall changes needed
- ✅ Encrypted connection
- ✅ No public exposure

**How to use:**
```bash
# Local machine
ssh -L 8000:localhost:8000 opc@YOUR_IP
# Browse to http://localhost:8000
```

---

### Option 2: Direct Access (Not Recommended - Requires Firewall Changes)

**⚠️ WARNING: This exposes your dashboard to the internet!**

If you must access directly (e.g., from mobile):

**On Oracle Cloud instance:**

1. **Configure Oracle Cloud Firewall:**
   - Login to Oracle Cloud Console
   - Navigate to: VCN → Security Lists → Default Security List
   - Add Ingress Rule:
     - Source CIDR: **YOUR_IP_ADDRESS/32** (not 0.0.0.0/0!)
     - IP Protocol: TCP
     - Destination Port: 8000

2. **Configure OS Firewall:**
   ```bash
   # Oracle Linux
   sudo firewall-cmd --permanent --add-port=8000/tcp
   sudo firewall-cmd --reload
   
   # Ubuntu
   sudo ufw allow from YOUR_IP_ADDRESS to any port 8000
   ```

3. **Access directly:**
   ```
   http://YOUR_ORACLE_PUBLIC_IP:8000
   ```

**⚠️ CRITICAL: Replace YOUR_IP_ADDRESS with your actual public IP, NOT 0.0.0.0/0**

---

## 🛠️ Alternative Dashboard Options

### Terminal-Based Dashboard (No Browser Needed)

For a terminal-only view:

```bash
# On Oracle Cloud instance
cd ~/Titan2.0

# Terminal dashboard with rich formatting
python3 live_operational_dashboard.py --terminal-only

# Or use the simple status script
./status_oracle.sh
```

**Features:**
- No browser required
- Works over SSH directly
- Lightweight (minimal resources)
- Real-time terminal updates

---

### Log-Based Monitoring (Most Lightweight)

Monitor via logs:

```bash
# Watch Brain logs
sudo journalctl -u titan-brain -f

# Watch Executor logs
sudo journalctl -u titan-executor -f

# Watch all Titan services
sudo journalctl -u titan-* -f

# Filter for specific events
sudo journalctl -u titan-executor -f | grep "TRADE\|PROFIT"
```

---

## 📱 Mobile Access

### Via SSH Tunnel (Recommended):

**On iPhone/iPad:**
1. Install **Termius** or **Blink Shell**
2. Configure SSH connection with port forwarding:
   - Local port: 8000
   - Remote port: 8000
   - Remote host: localhost
3. Connect to tunnel
4. Open Safari to `http://localhost:8000`

**On Android:**
1. Install **JuiceSSH** or **Termux**
2. Configure port forwarding
3. Connect
4. Open browser to `http://localhost:8000`

---

## 🔧 Troubleshooting

### Dashboard Won't Start

**Issue:** `Port 8000 already in use`

**Solution:**
```bash
# Find and kill process using port 8000
sudo lsof -i :8000
sudo kill -9 PID_NUMBER

# Or use different port
python3 live_operational_dashboard.py --port 8001
# Then tunnel: ssh -L 8001:localhost:8001 opc@YOUR_IP
```

---

### Can't Connect to Dashboard

**Issue:** `Connection refused` or `Unable to connect`

**Check:**
```bash
# 1. Verify dashboard is running
ps aux | grep live_operational_dashboard

# 2. Verify port is listening
sudo netstat -tlnp | grep 8000

# 3. Verify SSH tunnel is active
# On local machine, check for ssh process with -L 8000
ps aux | grep "ssh -L 8000"
```

**Restart tunnel:**
```bash
# Kill existing tunnel
pkill -f "ssh -L 8000"

# Create new tunnel
ssh -L 8000:localhost:8000 opc@YOUR_IP
```

---

### Dashboard Shows No Data

**Possible causes:**

1. **Redis not running (if using Redis mode):**
   ```bash
   sudo systemctl status titan-redis
   sudo systemctl start titan-redis
   ```

2. **Services not running:**
   ```bash
   ./status_oracle.sh
   ./start_oracle.sh
   ```

3. **No opportunities detected yet:**
   - Wait 5-10 minutes for first scans
   - Check logs: `sudo journalctl -u titan-brain -n 50`

---

## 📊 Dashboard Startup Script

Create a convenient startup script:

```bash
#!/bin/bash
# save as: start_dashboard.sh

echo "🚀 Starting Titan Dashboard..."

# Check if services are running
if ! systemctl is-active --quiet titan-brain; then
    echo "⚠️  Starting Titan services..."
    ./start_oracle.sh
    sleep 5
fi

# Start dashboard
echo "📊 Starting dashboard on port 8000..."
python3 live_operational_dashboard.py

# Note: Create SSH tunnel from local machine:
# ssh -L 8000:localhost:8000 opc@YOUR_IP
```

Make executable:
```bash
chmod +x start_dashboard.sh
```

Run:
```bash
./start_dashboard.sh
```

---

## 🎯 Quick Reference

### Start Everything:
```bash
# On Oracle Cloud
cd ~/Titan2.0
./start_oracle.sh
python3 live_operational_dashboard.py &

# On local machine
ssh -L 8000:localhost:8000 opc@YOUR_IP

# In browser
# http://localhost:8000
```

### Stop Everything:
```bash
# On Oracle Cloud
pkill -f live_operational_dashboard
./stop_oracle.sh
```

---

## 📞 Support

Dashboard not working?

1. **Check dashboard process:**
   ```bash
   ps aux | grep live_operational_dashboard
   ```

2. **Check dashboard logs:**
   ```bash
   python3 live_operational_dashboard.py 2>&1 | tee dashboard.log
   ```

3. **Verify dependencies:**
   ```bash
   pip3 install rich redis python-dotenv
   ```

4. **Try alternative monitoring:**
   ```bash
   ./status_oracle.sh
   ./oracle_health_check.sh
   ```

---

## ✅ Summary

**To access the dashboard:**

1. **On Oracle Cloud:** `python3 live_operational_dashboard.py`
2. **On Local Machine:** `ssh -L 8000:localhost:8000 opc@YOUR_IP`
3. **In Browser:** `http://localhost:8000`

**Most secure method:** SSH tunnel (recommended)  
**Port:** 8000 (default)  
**Requirements:** SSH access, Python 3, running Titan services

---

**Need more help?** See:
- [ORACLE_TROUBLESHOOTING.md](ORACLE_TROUBLESHOOTING.md)
- [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md)
- [MONITORING_ALERTING.md](MONITORING_ALERTING.md)
