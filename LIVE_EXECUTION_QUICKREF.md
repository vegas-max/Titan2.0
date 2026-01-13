# 🚀 TITAN Live Execution Quick Reference

**One-page guide for running live real-time execution via Google Colab**

---

## ⚡ Quick Launch

### Windows
```batch
LAUNCH_LIVE_EXECUTION_COLAB.bat
```

### Linux/macOS
```bash
./launch_live_execution_colab.sh
```

### Manual
https://colab.research.google.com/github/vegas-max/Titan2.0/blob/main/Titan_Live_Execution_Colab.ipynb

---

## 📋 Execution Steps

| Step | Action | Duration | Critical |
|------|--------|----------|----------|
| 1 | Complete System Build | 5-10 min | ✅ Required |
| 2 | Configure Live Mode | 5 min | ⚠️ CRITICAL |
| 3 | Start Redis & Services | 30 sec | ✅ Required |
| 4 | Initialize Execution Journal | 10 sec | ✅ Required |
| 5 | Start TITAN Brain | 10 sec | ✅ Required |
| 6 | Start TITAN Bot | 10 sec | ⚠️ LIVE MODE STARTS |
| 7 | Monitor Real-Time | Continuous | 📊 Important |
| 8 | View History | As needed | 📈 Optional |
| 9 | Check Health | Periodic | 🏥 Recommended |
| 10 | Emergency Stop | As needed | 🛑 CRITICAL |
| 11 | Generate Report | End of session | 📊 Recommended |

---

## ⚠️ CRITICAL WARNINGS

Before running Step 6:

- [ ] **Understand the risks**: You can LOSE REAL MONEY
- [ ] **Dedicated wallet**: Using wallet with MINIMAL funds ($50-100)
- [ ] **Private key secure**: Never share or commit
- [ ] **Tested in PAPER**: Already tested paper mode successfully
- [ ] **Ready to monitor**: Can watch continuously
- [ ] **Emergency stop ready**: Know how to run Step 10

---

## 🛡️ Default Safety Limits

Configure in Step 2:

| Setting | Default | Purpose |
|---------|---------|---------|
| Max Gas Price | 100 gwei | Prevent overpaying in congestion |
| Min Profit | $5 USD | Ensure trades are worthwhile |
| Max Slippage | 50 bps (0.5%) | Limit price impact |
| Circuit Breaker | 5 failures | Auto-pause after failures |

**Recommended for beginners: Use defaults or more conservative**

---

## 📊 Monitor These Metrics

### Green Flags ✅
- Success rate > 70%
- Net profit positive
- Circuit breaker inactive
- Gas costs < 20% of profit
- Executions completing

### Yellow Flags ⚠️
- Success rate 50-70%
- High gas costs (20-40% of profit)
- 2-3 consecutive failures
- Simulation failures increasing
- Slow execution times

### Red Flags 🚨
- Success rate < 50%
- Net profit negative
- Circuit breaker triggered
- Gas costs > 40% of profit
- 4+ consecutive failures
- RPC connection issues

**Action: If red flags appear, run Step 10 (Emergency Stop)**

---

## 🎯 Recommended Networks

Start with these low-gas networks:

| Network | Chain ID | Gas Cost | Recommended For |
|---------|----------|----------|-----------------|
| **Polygon** | 137 | $0.01-0.10 | **Beginners** (Best) |
| Arbitrum | 42161 | $0.10-0.50 | Intermediate |
| Optimism | 10 | $0.10-0.50 | Intermediate |
| Base | 8453 | $0.10-0.50 | Intermediate |
| Ethereum | 1 | $5-50+ | **Advanced only** |

**Start with Polygon until profitable, then expand**

---

## 📓 Execution Journal Locations

All data saved to:

```
/content/Titan2.0/data/execution_journal/
├── journal_<session_id>.json     # Main journal
└── report_<session_id>.txt       # Performance report
```

Download these files before ending your Colab session!

---

## 🔧 Troubleshooting Quick Fixes

### Problem: No opportunities detected
**Fix:** Lower minimum profit to $3-4, increase max gas to 150 gwei

### Problem: All simulations failing
**Fix:** Increase slippage tolerance to 75-100 bps

### Problem: Circuit breaker triggered
**Fix:** Wait 60 seconds for auto-reset, or investigate failures

### Problem: High gas costs
**Fix:** Switch to Polygon or lower-gas network

### Problem: RPC errors
**Fix:** Check Infura dashboard for rate limits, add Alchemy backup

---

## 📞 Emergency Procedures

### Immediate Stop Required
1. Click on Step 10 cell
2. Click Run button (▶)
3. Wait for "All systems stopped" message
4. Verify processes stopped in Step 9

### Download Journal Before Stopping
1. Run Step 11 to generate report
2. Navigate to Files panel (left sidebar)
3. Go to `/content/Titan2.0/data/execution_journal/`
4. Right-click journal and report files
5. Select Download

### Lost Connection
1. Colab session will continue briefly then terminate
2. Submitted transactions will complete
3. No new executions will start
4. Journal preserved but not accessible unless you reconnect

---

## 💡 Pro Tips

### Maximize Profitability
- Start with Polygon (lowest gas)
- Run during high volatility (more opportunities)
- Monitor success rate, adjust if < 70%
- Withdraw profits regularly
- Keep only gas reserves in wallet

### Minimize Risk
- Start with $50-100 for gas only
- Use minimum profit of $5+
- Keep circuit breaker at 5 failures
- Stop if net profit goes negative
- Never leave unattended for > 30 minutes

### Optimize Performance
- Use both Infura and Alchemy
- Monitor during active trading hours
- Check dashboard every 5-10 minutes
- Generate reports after each session
- Learn from execution history

---

## 📚 Full Documentation

- **Complete Guide**: `LIVE_EXECUTION_GUIDE.md` (26KB)
- **Step-by-Step**: `GOOGLE_COLAB_STEP_BY_STEP.md`
- **System README**: `README.md`
- **Operations**: `OPERATIONS_GUIDE.md`
- **Security**: `SECURITY_SUMMARY.md`

---

## ⚖️ Legal Disclaimer

**USE AT YOUR OWN RISK**

- Not financial advice
- Can lose money
- No warranties or guarantees
- Your responsibility entirely
- Experimental software
- Test thoroughly first

**Only risk what you can afford to lose**

---

**Built with ❤️ by the Titan Team**

Need help? Open an issue: https://github.com/vegas-max/Titan2.0/issues

⭐ Star the repo if this helps you!
