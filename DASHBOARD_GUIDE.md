# 📊 Operational Dashboard Guide

## Overview

TITAN provides **two real-time operational dashboards** for 24/7 monitoring and sanity checks:

1. **Terminal Dashboard** (`live_operational_dashboard.py`) - CLI-based, perfect for SSH/remote monitoring
2. **Web Dashboard** (`operational_dashboard.html`) - Browser-based with modern UI

Both dashboards provide:
- ✅ Real-time profit/loss tracking
- ✅ Gas price monitoring with trends
- ✅ Success rate and performance metrics
- ✅ Chain-specific activity tracking
- ✅ Recent trades history
- ✅ Automated sanity checks with alerts
- ✅ 24/7 operational visibility

---

## Quick Start

### Option 1: Terminal Dashboard (Recommended for SSH)

```bash
# Launch terminal dashboard
npm run dashboard

# Or directly with Python
python3 live_operational_dashboard.py
```

**Features:**
- Beautiful terminal UI with Rich library
- Real-time updates every second
- Gas price trend visualization (ASCII chart)
- Color-coded alerts and metrics
- Works over SSH connections
- Low resource usage

**Controls:**
- `Ctrl+C` to exit

---

### Option 2: Web Dashboard (Browser-Based)

```bash
# Start web server on port 3001
npm run dashboard:web

# Then open in browser:
# http://localhost:3001/operational_dashboard.html
```

**Features:**
- Modern gradient UI
- Interactive charts (Canvas-based)
- Auto-refreshing every second
- Works on mobile devices
- Share via local network

**Access:**
- Local: `http://localhost:3001/operational_dashboard.html`
- Network: `http://YOUR_IP:3001/operational_dashboard.html`

---

### Option 3: Launch Both (Maximum Visibility)

```bash
# Interactive launcher
./launch_dashboard.sh

# Select option 3 to run both simultaneously
```

This will:
1. Start web server in background
2. Open browser automatically (if available)
3. Launch terminal dashboard in foreground
4. Both dashboards update in real-time

---

## Dashboard Metrics Explained

### Performance Metrics

| Metric | Description | Good Value |
|--------|-------------|------------|
| **Total Profit** | Gross profit from all trades | Increasing |
| **Gas Spent** | Total gas costs in USD | Minimized |
| **Net Profit** | Profit - Gas (your actual earnings) | Positive & growing |
| **Total Trades** | Number of trades executed | Growing |
| **Success Rate** | % of successful trades | > 70% |
| **Opportunities Scanned** | Total opportunities analyzed | High |
| **Opportunities Profitable** | Opportunities that met profit threshold | Growing |
| **Avg Execution Time** | Average trade execution time | < 10s |
| **Current Gas Price** | Real-time gas price | < 150 Gwei |

### Chain Metrics

Each active chain shows:
- **Trades**: Number of trades on this chain
- **Profit**: Total profit from this chain
- **Gas**: Gas costs on this chain
- **Net**: Profit - Gas for this chain
- **Last Active**: Time since last trade

### Recent Trades

Shows last 10 trades with:
- **Time**: When the trade was executed
- **Chain**: Which blockchain
- **Strategy**: Type of arbitrage (Flash Arb, Cross-DEX, etc.)
- **Profit**: Profit from this trade
- **Gas**: Gas cost for this trade
- **Status**: SUCCESS or FAILED

---

## Automated Sanity Checks

The dashboard performs these checks every second:

### ⚠️ Warning Alerts

1. **High Gas Price**: Gas > 150 Gwei
2. **Net Loss**: Total profit < gas costs
3. **Inactive System**: No trades for 5+ minutes

### 🚨 Critical Alerts

1. **Low Success Rate**: < 70% of trades successful
2. **Consecutive Failures**: 10+ failed trades in a row
3. **System Unresponsive**: No data updates

### Alert Severity Levels

- 🟢 **Healthy**: All systems nominal
- 🟡 **Degraded**: Minor issues detected
- 🔴 **Critical**: Immediate attention required
- 🔵 **Starting**: System initializing

---

## Configuration

### Environment Variables

Set in `.env`:

```bash
# Minimum profit threshold
MIN_PROFIT_USD=5.00

# Maximum gas price before alerting
MAX_GAS_PRICE_GWEI=150

# Redis connection for live data
REDIS_URL=redis://localhost:6379
```

### Sanity Check Thresholds

Customize in `live_operational_dashboard.py`:

```python
self.thresholds = {
    "min_profit_usd": 5.0,              # Minimum profit per trade
    "max_gas_price_gwei": 150,          # Maximum acceptable gas
    "max_execution_time_ms": 30000,     # Max execution time
    "min_success_rate": 0.70,           # Minimum 70% success
    "max_consecutive_failures": 10,     # Alert after 10 failures
}
```

---

## Data Sources

### Redis Integration

When Redis is available, the dashboard reads from:

- **Channel**: `trade_signals`
- **Keys**: `latest_trade_signal`, `system_metrics`

### Simulation Mode

If Redis is not available, the dashboard runs in **simulation mode**:
- Generates realistic test data
- Useful for testing and demonstrations
- Same UI and functionality

To connect to Redis:

```bash
# Make sure Redis is running
redis-cli ping
# Should return: PONG

# Set Redis URL in .env
REDIS_URL=redis://localhost:6379
```

---

## Troubleshooting

### Dashboard won't start

```bash
# Install required packages
pip install rich redis python-dotenv

# Check Python version (3.8+ required)
python3 --version
```

### Web dashboard shows blank page

```bash
# Make sure you're accessing the HTML file
http://localhost:3001/operational_dashboard.html
#                      ↑ Don't forget the filename

# Check web server is running
lsof -i :3001
```

### No live data in terminal dashboard

```bash
# Check Redis connection
redis-cli ping

# Verify REDIS_URL in .env
echo $REDIS_URL

# Dashboard will work in simulation mode without Redis
```

### Colors not showing in terminal

```bash
# Your terminal may not support colors
# Try a modern terminal like:
# - iTerm2 (macOS)
# - Windows Terminal (Windows)
# - GNOME Terminal (Linux)
```

---

## Advanced Usage

### Run dashboard on system startup

**Linux (systemd):**

```bash
# Create service file
sudo nano /etc/systemd/system/titan-dashboard.service

[Unit]
Description=TITAN Operational Dashboard
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/Titan2.0
ExecStart=/usr/bin/python3 live_operational_dashboard.py
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable titan-dashboard
sudo systemctl start titan-dashboard
```

**macOS (launchd):**

```bash
# Create plist file
nano ~/Library/LaunchAgents/com.titan.dashboard.plist

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.titan.dashboard</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/Titan2.0/live_operational_dashboard.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>

# Load the service
launchctl load ~/Library/LaunchAgents/com.titan.dashboard.plist
```

### Export dashboard data

The dashboard can log metrics to files:

```python
# In live_operational_dashboard.py, add to update loop:
with open('dashboard_log.json', 'a') as f:
    f.write(json.dumps({
        'timestamp': datetime.now().isoformat(),
        'metrics': self.current_metrics
    }) + '\n')
```

### Remote access to web dashboard

```bash
# Bind to all interfaces (CAUTION: Security risk!)
python3 -m http.server 3001 --bind 0.0.0.0

# Access from other devices
http://YOUR_SERVER_IP:3001/operational_dashboard.html

# Better: Use SSH tunnel
ssh -L 3001:localhost:3001 user@server
# Then access locally at http://localhost:3001/operational_dashboard.html
```

---

## Dashboard Screenshots

### Terminal Dashboard

```
┌─────────────────────────────────────────────────────────┐
│        🚀 TITAN OPERATIONAL DASHBOARD                   │
│ Status: HEALTHY | Uptime: 2h 34m | 2025-12-27 06:52:00 │
└─────────────────────────────────────────────────────────┘

┌─ 📊 Performance Metrics ──────────────────────────────┐
│ 💰 Total Profit (USD)    $1,247.50  ⛽ Gas Spent      │
│ 📊 Net Profit (USD)      $1,089.30  📈 Avg Profit     │
│ ✅ Total Trades           142       🎯 Success Rate   │
│ 🔍 Opps Scanned          45,231     💎 Opps Profitable│
└───────────────────────────────────────────────────────┘

┌─ 🌐 Active Chains ────────────────────────────────────┐
│ Polygon      89  $847.20  $98.40  $748.80  2m ago    │
│ Arbitrum     32  $254.10  $38.60  $215.50  5m ago    │
│ Ethereum     21  $146.20  $21.20  $125.00  12m ago   │
└───────────────────────────────────────────────────────┘
```

### Web Dashboard

- Modern gradient background (purple/blue)
- Live updating metrics cards
- Animated alerts
- Interactive gas price chart
- Responsive design

---

## Best Practices

1. **Always monitor during live trading**
   - Keep dashboard visible on a dedicated screen
   - Set up alerts for critical thresholds

2. **Review metrics regularly**
   - Check success rate hourly
   - Monitor gas costs vs profit ratio
   - Track which chains are most profitable

3. **Respond to alerts immediately**
   - 🟡 Yellow alerts: Investigate when convenient
   - 🔴 Red alerts: Stop trading and investigate

4. **Log important events**
   - Take screenshots of unusual metrics
   - Note times of high performance
   - Document any manual interventions

5. **Use appropriate dashboard**
   - SSH/Remote: Terminal dashboard
   - Local development: Web dashboard
   - Production monitoring: Both

---

## Support

For issues or questions:
- Check the main [README.md](README.md)
- Review [OPERATIONS_GUIDE.md](OPERATIONS_GUIDE.md)
- Open an issue on GitHub

---

**Remember**: These dashboards are your eyes on the system. Keep them running 24/7 during live operations!
