# 🎯 What to Expect After Oracle Cloud Deployment

**Complete guide on what happens after deploying Titan to Oracle Cloud Always Free tier**

---

## 📋 Immediate Post-Deployment (First 5 Minutes)

### ✅ What You'll See

**1. Services Running:**
```bash
$ ./status_oracle.sh

📊 Titan Service Status:

● titan-brain.service - Titan Brain (AI Engine)
   Loaded: loaded
   Active: active (running)
   
● titan-executor.service - Titan Executor (Trading Bot)
   Loaded: loaded
   Active: active (running)
```

**2. System Logs Starting:**
```bash
$ sudo journalctl -u titan-brain -f

Jan 03 11:30:00 titan systemd[1]: Started Titan Brain (AI Engine).
Jan 03 11:30:01 titan python3[1234]: 🚀 Titan Brain Starting...
Jan 03 11:30:02 titan python3[1234]: ✅ Connected to Polygon RPC
Jan 03 11:30:03 titan python3[1234]: ✅ Signal system initialized
Jan 03 11:30:04 titan python3[1234]: 🔍 Starting opportunity scanner...
```

**3. Health Check Passes:**
```bash
$ ./oracle_health_check.sh

✓ Memory usage healthy (45% used)
✓ Disk usage healthy (28% used)
✓ Node.js installed: v18.x
✓ Python installed: v3.11
✓ Titan Brain: Running
✓ Titan Executor: Running
✓ Signal files being created
✓ No errors in logs (last hour)

✅ All checks passed! System is healthy.
```

---

## 🔍 First Hour - Initialization Phase

### What's Happening Behind the Scenes

**Brain (AI Engine):**
- 🔄 Connecting to blockchain RPCs (Polygon, Ethereum, etc.)
- 📊 Downloading token price data
- 🗺️ Building DEX routing maps
- 🔍 Starting opportunity scanning
- 💾 Caching pool data and liquidity information

**Executor (Trading Bot):**
- ⏳ Waiting for signals from Brain
- 📡 Maintaining WebSocket connections
- 🔐 Validating wallet connection
- ⚡ Monitoring gas prices

**Expected Behavior:**

```
[11:30:05] Brain: Scanning 847 pools on Polygon...
[11:30:12] Brain: Cached 234 token pairs
[11:30:18] Brain: First scan complete - 0 opportunities (normal)
[11:30:25] Brain: Scan cycle 2 starting...
[11:31:02] Brain: Found potential opportunity - analyzing...
[11:31:03] Brain: Opportunity failed profitability check (gas too high)
[11:31:15] Brain: Scan cycle 3 starting...
```

**What You'll Notice:**
- ✅ CPU usage: 40-60% (during initial scanning)
- ✅ Memory usage: 2-4GB (ARM) or 600-800MB (AMD Micro)
- ✅ Network activity: Moderate (downloading blockchain data)
- ✅ Log messages every few seconds
- ⏳ No trades yet (this is normal in PAPER mode)

---

## 📊 First 24 Hours - Paper Trading Mode

### Expected Observations

**1. Opportunity Detection (Typical Day):**
```
Opportunities Scanned:     12,847
Opportunities Identified:      234
Passed Profitability:           45
Passed Risk Checks:             12
Executed (Paper):                3
Success Rate:                 100% (paper)
Average Profit (Paper):    $12.34
```

**2. Dashboard Metrics:**

When you access `http://localhost:8000` (via SSH tunnel):

```
┌─────────────────────────────────────────┐
│  📊 Titan Real-Time Dashboard           │
├─────────────────────────────────────────┤
│  Total Profit (Paper):      $45.67      │
│  Trades Executed:                5      │
│  Success Rate:               100%       │
│  Active Opportunities:          2       │
│  System Uptime:          18h 32m        │
│  Gas Spent (Paper):         $2.34       │
└─────────────────────────────────────────┘

Recent Activity:
[11:45:23] OPPORTUNITY: ETH→USDC→DAI→ETH (+$15.23)
[12:03:45] EXECUTED: Paper trade successful
[12:18:12] OPPORTUNITY: MATIC→USDT→WETH (+$8.45)
[12:19:01] REJECTED: Slippage too high
```

**3. Signal Files (File-Based Communication):**
```bash
$ ls -lh signals/outgoing/

-rw-r--r-- 1 opc opc 2.1K Jan 3 11:45 opportunity_12847.json
-rw-r--r-- 1 opc opc 1.8K Jan 3 12:03 trade_00001.json
-rw-r--r-- 1 opc opc 2.3K Jan 3 12:18 opportunity_12848.json
```

**4. Log Patterns You'll See:**

**Brain Logs (Normal):**
```
[INFO] Scanning cycle 1247 completed - 2.3s
[INFO] Found 3 potential opportunities
[DEBUG] Checking profitability for ETH→USDC→DAI
[INFO] Opportunity validated: +$12.34 profit
[INFO] Publishing signal: opportunity_12847
```

**Executor Logs (Normal):**
```
[INFO] Received signal: opportunity_12847
[INFO] Simulating trade in PAPER mode
[SUCCESS] Paper trade executed: +$12.34
[INFO] Total paper profit: $45.67
```

---

## ⚠️ What's Normal vs. What's Not

### ✅ NORMAL Behaviors

**First Few Hours:**
- ❌ No opportunities found initially (market conditions vary)
- ✅ High CPU during initial scans (40-70%)
- ✅ Many "rejected" opportunities (gas too high, slippage, etc.)
- ✅ RPC rate limit warnings (if using free tier RPCs)
- ✅ "No profitable paths found" messages
- ✅ Constant scanning activity

**Paper Trading (24-48 hours):**
- ✅ 0-10 paper trades per day (depends on market volatility)
- ✅ Small paper profits ($5-50 per trade)
- ✅ Many scans but few executions (normal selectivity)
- ✅ 100% success rate (paper trades are simulated)

**Resource Usage:**
- ✅ ARM Instance: 2-6GB RAM, 30-60% CPU
- ✅ AMD Micro: 600-900MB RAM, 60-90% CPU
- ✅ Disk: Slowly growing (logs, cache)
- ✅ Network: Consistent moderate activity

### 🚨 ABNORMAL Behaviors (Needs Attention)

**Issues to Watch For:**

1. **Memory Errors:**
   ```
   [ERROR] Out of memory - killed
   ```
   **Solution:** Enable lightweight mode, add swap, restart services

2. **RPC Connection Failures:**
   ```
   [ERROR] Failed to connect to RPC after 5 retries
   ```
   **Solution:** Check RPC endpoints in .env, verify API keys valid

3. **No Scanning Activity:**
   ```
   # No new logs for 5+ minutes
   ```
   **Solution:** Check if services crashed, restart with `./restart_oracle.sh`

4. **Constant Errors:**
   ```
   [ERROR] [ERROR] [ERROR] [ERROR] (repeated)
   ```
   **Solution:** Check logs, verify .env configuration, review troubleshooting guide

---

## 🎯 Week 1 - Patterns and Optimization

### Expected Performance Metrics

**Typical Week 1 Stats (Paper Mode):**
```
Total Opportunities Scanned:    89,234
Opportunities Identified:        1,234
Profitable After Gas:              156
Risk-Approved:                      45
Paper Trades Executed:              12
Average Paper Profit:           $18.45
Total Paper Profit:            $221.40
Success Rate:                     100%
```

**Market-Dependent Variations:**
- 🔥 **High Volatility Days:** 5-10 opportunities
- 😴 **Low Volatility Days:** 0-2 opportunities
- ⚡ **Gas Spike Days:** Many rejections (gas too expensive)
- 🌊 **Normal Days:** 1-3 opportunities

### What Good Logs Look Like

**Healthy System (Typical Day):**
```bash
$ sudo journalctl -u titan-* --since "1 hour ago" | grep -E "ERROR|SUCCESS|OPPORTUNITY"

# Expected: Mix of found opportunities and successful validations
[12:15:43] OPPORTUNITY: Found potential path
[12:15:44] SUCCESS: Validated profitability
[12:16:01] OPPORTUNITY: Analyzing DEX rates
[12:16:02] REJECTED: Gas cost exceeds profit
[12:23:12] OPPORTUNITY: Cross-chain route identified
[12:23:14] SUCCESS: Paper trade executed
```

**Problematic System:**
```bash
# Red flag: Too many errors
[12:15:43] ERROR: Connection timeout
[12:15:44] ERROR: RPC rate limit exceeded
[12:15:45] ERROR: Failed to fetch pool data
[12:15:46] ERROR: Connection timeout
```

---

## 📈 Going Live (After Successful Testing)

### Prerequisites Before Switching to Live Mode

**Checklist:**
- ✅ Paper mode ran successfully for 24-48 hours
- ✅ No critical errors in logs
- ✅ System stable (no crashes/restarts)
- ✅ Profitable opportunities detected
- ✅ Wallet funded with small amount ($50-100 max)
- ✅ Gas settings reviewed and acceptable
- ✅ Emergency stop procedure understood

### Switching to Live Mode

**Edit .env:**
```bash
nano .env

# Change this line:
EXECUTION_MODE=PAPER

# To:
EXECUTION_MODE=LIVE
```

**Restart services:**
```bash
./restart_oracle.sh
```

**Monitor closely:**
```bash
# Watch for real trades
sudo journalctl -u titan-executor -f | grep "EXECUTED"
```

### What Changes in Live Mode

**Before (Paper):**
```
[INFO] PAPER MODE: Simulating trade
[SUCCESS] Paper profit: $12.34
[INFO] No blockchain transaction sent
```

**After (Live):**
```
[INFO] LIVE MODE: Executing real trade
[INFO] Sending transaction: 0xabc123...
[INFO] Waiting for confirmation...
[SUCCESS] Trade confirmed! Profit: $11.87
[INFO] Gas spent: $2.45
[INFO] Net profit: $9.42
```

**Key Differences:**
- 💰 Real gas costs (reduces actual profit)
- ⏱️ Transaction confirmation delays (12-60 seconds)
- 📉 Slippage impact (prices move during execution)
- 💸 Real money at risk
- 📊 Success rate may drop to 60-80% (market conditions)

---

## 🔍 Daily Monitoring Routine

### Quick Health Check (2 minutes)

**Morning Routine:**
```bash
# 1. Check service status
./status_oracle.sh

# 2. Quick health check
./oracle_health_check.sh

# 3. View recent activity
sudo journalctl -u titan-* --since "24 hours ago" | grep -i "success\|error" | tail -20

# 4. Check resources
free -h
df -h
```

**What to Look For:**
- ✅ All services "active (running)"
- ✅ Health check passes
- ✅ Mix of successes in logs
- ✅ Memory/disk usage stable
- ⚠️ Any repeated errors

### Weekly Review (10 minutes)

```bash
# Performance stats
sudo journalctl -u titan-executor --since "7 days ago" | grep "SUCCESS\|EXECUTED" | wc -l

# Error analysis
sudo journalctl -u titan-* --since "7 days ago" | grep -i "error" | sort | uniq -c | sort -rn

# Resource trends
uptime
free -h
df -h
```

---

## 📊 Expected Resource Usage

### Normal Resource Consumption

**ARM A1.Flex (4 OCPU, 24GB RAM):**
```
CPU Usage:     30-60% average, 80% during scans
Memory:        3-6GB used (25% of 24GB)
Disk:          2-5GB for Titan + logs
Network:       100-500 MB/hour
Swap:          0 MB (not needed)
```

**AMD E2.1.Micro (1 OCPU, 1GB RAM):**
```
CPU Usage:     60-90% average, 100% during scans
Memory:        700-950MB used (70-95% of 1GB)
Disk:          2-5GB for Titan + logs
Network:       50-200 MB/hour
Swap:          200-800MB used (needed for stability)
```

### Growth Over Time

**Week 1:**
- Logs: ~500MB
- Cache: ~200MB
- Total: ~3GB

**Month 1:**
- Logs: ~2GB (with rotation)
- Cache: ~500MB
- Total: ~5GB

**With Log Rotation (Recommended):**
- Logs: Stays ~500MB (auto-cleaned)
- Total: ~3GB stable

---

## 🎯 Success Indicators

### Your Deployment is Successful If:

**Week 1 Checklist:**
- ✅ Services run continuously without crashes
- ✅ Health checks consistently pass
- ✅ Opportunities detected (even if few)
- ✅ Paper trades execute successfully
- ✅ No critical errors in logs
- ✅ Resource usage within normal ranges
- ✅ Dashboard accessible and updating
- ✅ System survived restarts/reboots

**Ready for Live Trading When:**
- ✅ All Week 1 criteria met
- ✅ Ran in paper mode minimum 48 hours
- ✅ Average paper profit positive
- ✅ Understand gas costs and slippage
- ✅ Emergency stop procedure tested
- ✅ Comfortable with risk amount in wallet

---

## 🆘 Common Questions

### "I don't see any trades, is something wrong?"

**Answer:** Probably not! Low opportunity detection is normal because:
- Markets aren't always volatile
- Gas prices often too high for profitable arb
- Competition from other bots
- Your risk thresholds are conservative (good!)

**Verify it's working:**
```bash
# Check for scanning activity
sudo journalctl -u titan-brain -f | grep "Scanning"

# Should see regular scan cycles
[INFO] Scanning cycle 1234 completed
[INFO] Scanning cycle 1235 completed
```

### "CPU is at 100%, is this bad?"

**For AMD Micro:** This is normal! With only 1 OCPU, heavy usage is expected.

**For ARM A1.Flex:** Shouldn't stay at 100% constantly. Check logs for errors.

### "How much profit should I expect?"

**Paper Mode:** $5-50 per trade, 0-10 trades/day (highly variable)

**Live Mode:** 
- Per trade: $3-30 (after gas)
- Per day: $5-100 (market dependent)
- Per month: $150-3,000 (if profitable consistently)

**Reality Check:** Most arbitrage is competitive. Small consistent profits are more realistic than huge gains.

---

## 📞 When to Get Help

**Immediate attention needed if:**
- 🔴 Services crash repeatedly (>3 times/hour)
- 🔴 Out of memory errors continuously
- 🔴 No logs for 10+ minutes
- 🔴 Disk full errors
- 🔴 RPC connection fails completely

**Review documentation if:**
- 🟡 Few opportunities detected (check ORACLE_TROUBLESHOOTING.md)
- 🟡 High resource usage (check LIGHTWEIGHT_MODE_GUIDE.md)
- 🟡 Configuration questions (check ORACLE_ENV_CONFIGURATION_GUIDE.md)

---

## 🎉 Summary - What to Expect

### First 5 Minutes:
✅ Services start, logs begin, health check passes

### First Hour:
✅ System initializes, starts scanning, builds cache

### First Day:
✅ Opportunities detected, paper trades executed, metrics visible

### First Week:
✅ Consistent scanning, stable operation, pattern emerges

### Going Live:
⚠️ After 48h successful paper trading, with caution and small funds

---

**Bottom Line:** A successful deployment shows consistent scanning activity, occasional paper trades, stable system resources, and no critical errors. Don't expect immediate profits - expect a reliable, scanning, learning system that finds opportunities when market conditions allow.

See also:
- [ORACLE_TROUBLESHOOTING.md](ORACLE_TROUBLESHOOTING.md) - Problem solving
- [ORACLE_CLOUD_DEPLOYMENT.md](ORACLE_CLOUD_DEPLOYMENT.md) - Complete guide
- [ORACLE_DASHBOARD_ACCESS.md](ORACLE_DASHBOARD_ACCESS.md) - Monitoring
