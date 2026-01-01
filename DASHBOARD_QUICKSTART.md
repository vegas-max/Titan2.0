# 🚀 TITAN Interactive Dashboard - Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies (30 seconds)

```bash
# Install Python packages
pip install aiohttp aiohttp-cors redis python-dotenv rich

# Or install all requirements
pip install -r requirements.txt
```

### Step 2: Start Redis (Optional - 1 minute)

```bash
# For live data integration with TITAN system
redis-server

# Verify Redis is running
redis-cli ping
# Should return: PONG
```

**Note:** Dashboard works without Redis in simulation mode for testing!

### Step 3: Launch Dashboard (10 seconds)

```bash
# Linux/Mac - One command
./launch_interactive_dashboard.sh

# Windows - One command
launch_interactive_dashboard.bat

# Or with npm
npm run dashboard:interactive

# Or direct Python
python3 dashboard_server.py
```

### Step 4: Open Browser (5 seconds)

```
Open: http://localhost:8080
```

**That's it! The dashboard is now running! 🎉**

---

## Dashboard Features at a Glance

### 📊 Page 1: Overview
- System status indicator
- 8 key metrics (profit, gas, success rate, etc.)
- Control buttons (Pause/Resume/Emergency Stop)
- Recent executions table

### 🔍 Page 2: Market Scanner
- **Real-time** market opportunities
- Filter by profit/chain/strategy
- DEX routing details
- Spread and profitability

### ⚡ Page 3: Executable TXs
- Queue of ready transactions
- Expected profit display
- Auto-updates as queue changes

### 🎯 Page 4: Live Execution
- **Real-time** TX execution monitoring
- Transaction hashes
- Gas usage tracking
- Success/failure status

### 📈 Page 5: Analytics
- Performance statistics
- Chain-specific metrics
- Success rates and averages

---

## What You'll See

### In Simulation Mode (without TITAN system)
- Realistic simulated market opportunities appearing
- Example transactions being "executed"
- Live metrics updating
- All dashboard features working

### With Live TITAN System
- **Real** market opportunities from brain.py
- **Actual** executable transactions
- **Live** execution results from bot.js
- **True** system metrics

---

## Testing the Dashboard

### 1. Test with Simulation (No TITAN system needed)

```bash
# Just start the dashboard
./launch_interactive_dashboard.sh

# Dashboard generates realistic test data
# Perfect for demo or development
```

### 2. Test with Integration Example

```bash
# Run the integration example
python3 dashboard_wiring_example.py --example

# This will:
# - Publish 3 market opportunities
# - Add 2 executable TXs to queue
# - Execute 1 transaction
# - Update all metrics

# Then check dashboard at http://localhost:8080
```

### 3. Test Dashboard Controls

```bash
# In another terminal, listen for controls
python3 dashboard_wiring_example.py --listen

# Then in dashboard:
# - Click "Pause Scanning" button
# - Click "Resume Scanning" button
# - Watch the listener terminal for messages
```

---

## Integrating with TITAN System

### Quick Integration (3 lines of code)

```python
# In your brain.py or bot.js equivalent
from dashboard_integration import DashboardIntegration

# Create integration
integration = DashboardIntegration()

# Publish an opportunity
integration.publish_market_opportunity({
    "chain": "Polygon",
    "token_pair": "USDC/USDT",
    "strategy": "Flash Arbitrage",
    "profit_usd": 15.50,
    "gas_cost": 2.30,
    "net_profit": 13.20,
    "executable": True,
    "dex_a": "Uniswap V3",
    "dex_b": "Curve",
    "spread_bps": 42.5
})

# That's it! Dashboard updates in real-time!
```

See `dashboard_wiring_example.py` for complete integration examples.

---

## Common Commands

```bash
# Start dashboard (Linux/Mac)
./launch_interactive_dashboard.sh

# Start dashboard (Windows)
launch_interactive_dashboard.bat

# Start with custom port
./launch_interactive_dashboard.sh --port 3000

# Start with custom host (network access)
./launch_interactive_dashboard.sh --host 0.0.0.0 --port 8080

# Run integration example
python3 dashboard_wiring_example.py --example

# Listen for dashboard controls
python3 dashboard_wiring_example.py --listen

# Start Redis (if needed for live data)
redis-server
```

---

## Troubleshooting

### Dashboard won't start

**Error:** `ModuleNotFoundError: No module named 'aiohttp'`

**Fix:**
```bash
pip install aiohttp aiohttp-cors
```

### Dashboard shows "Waiting for data"

This is normal! The dashboard is in simulation mode.

**To connect to live TITAN system:**
1. Start Redis: `redis-server`
2. Start TITAN brain: `python3 offchain/ml/brain.py`
3. Start TITAN bot: `node offchain/execution/bot.js`
4. Dashboard will automatically switch to live data

### Port already in use

**Fix:** Use a different port
```bash
./launch_interactive_dashboard.sh --port 3000
```

### Can't access from network

**Fix:** Bind to all interfaces
```bash
./launch_interactive_dashboard.sh --host 0.0.0.0
```

---

## What Happens Under the Hood

### Data Flow

```
1. TITAN finds opportunity → 
2. Publishes to Redis → 
3. Dashboard server receives → 
4. Broadcasts via WebSocket → 
5. Browser updates in real-time
```

### WebSocket Updates

The dashboard uses WebSocket for instant updates:
- **No page refresh** needed
- **Sub-second** latency
- **Auto-reconnect** on disconnect
- **Multiple clients** supported

### Redis Channels

Dashboard uses these Redis pub/sub channels:
- `dashboard:market_opportunity` - New opportunities
- `dashboard:executable_tx` - Executable transactions
- `dashboard:execution_result` - TX results
- `dashboard:metrics_update` - System metrics
- `system_control` - Control commands from dashboard

---

## Advanced Usage

### Running in Background

```bash
# Linux/Mac
nohup ./launch_interactive_dashboard.sh > dashboard.log 2>&1 &

# View logs
tail -f dashboard.log
```

### Custom Configuration

Create `.env` file:
```bash
# Redis connection
REDIS_URL=redis://localhost:6379

# Metrics thresholds
MIN_PROFIT_USD=5.00
MAX_GAS_PRICE_GWEI=150
```

### Network Access

Access dashboard from other devices:

1. Start with host 0.0.0.0:
   ```bash
   ./launch_interactive_dashboard.sh --host 0.0.0.0
   ```

2. Find your IP:
   ```bash
   # Linux
   hostname -I
   
   # Mac
   ipconfig getifaddr en0
   ```

3. Access from other device:
   ```
   http://YOUR_IP:8080
   ```

---

## Next Steps

### Full Documentation
See `INTERACTIVE_DASHBOARD_README.md` for:
- Complete feature list
- WebSocket API reference
- Security best practices
- Production deployment guide

### Integration Guide
See `dashboard_wiring_example.py` for:
- Complete integration examples
- Control handler implementation
- Metrics tracking

### TITAN System
See main `README.md` for:
- TITAN system overview
- brain.py and bot.js documentation
- Complete architecture

---

## Support

**Questions?**
- Check `INTERACTIVE_DASHBOARD_README.md`
- Check main `README.md`
- Open an issue on GitHub

**Found a bug?**
- Report it on GitHub Issues

---

## Summary

✅ **5-minute setup**  
✅ **Works standalone** (simulation mode)  
✅ **Integrates easily** with TITAN  
✅ **Real-time updates** (<1 second)  
✅ **Multi-page navigation**  
✅ **Interactive controls**  
✅ **Beautiful UI**  

**Start now:**
```bash
./launch_interactive_dashboard.sh
```

**Open browser:**
```
http://localhost:8080
```

**Enjoy! 🚀**
