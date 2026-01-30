# 🚀 TITAN 2.0 - Quick Reference Guide

**Version**: 4.2.0  
**Status**: ✅ Mainnet Ready  
**Last Updated**: 2025-12-27

---

## 📋 What's New

This build includes:
- ✅ Production-ready FlashArbExecutor contract (Solidity ^0.8.20)
- ✅ Comprehensive config.json with DEX/Bridge/Token addresses
- ✅ Real-time operational dashboards (Terminal + Web)
- ✅ All Solidity files synchronized (no conflicts)
- ✅ Automated deployment scripts
- ✅ 24/7 sanity check monitoring

---

## ⚡ Quick Start (5 Minutes)

### 1. Configure Environment

```bash
cp .env.example .env
nano .env
```

Update these critical values:
```bash
PRIVATE_KEY=0xYOUR_64_CHAR_PRIVATE_KEY
RPC_POLYGON=https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY
```

### 2. Deploy FlashArbExecutor

```bash
npm run deploy:flasharb:polygon
```

Save the contract address to `.env`:
```bash
FLASH_ARB_EXECUTOR_POLYGON=0xYOUR_DEPLOYED_ADDRESS
```

### 3. Launch Monitoring

```bash
./scripts/linux/launch_dashboard.sh
# Select option 3 for both dashboards
```

### 4. Start Trading

```bash
npm start
```

---

## 📊 Monitoring Commands

| Command | Purpose |
|---------|---------|
| `npm run dashboard` | Terminal dashboard (SSH-friendly) |
| `npm run dashboard:web` | Web dashboard (browser) |
| `./scripts/linux/launch_dashboard.sh` | Interactive launcher (both) |
| `npm run monitor` | Alias for terminal dashboard |

**Dashboard Access**:
- Terminal: Automatically launched
- Web: http://localhost:3001/operational_dashboard.html

---

## 🔧 Deployment Commands

| Network | Command |
|---------|---------|
| Polygon | `npm run deploy:flasharb:polygon` |
| Ethereum | `npm run deploy:flasharb:ethereum` |
| Arbitrum | `npm run deploy:flasharb:arbitrum` |

---

## 📁 Key Files

### Configuration
- `config.json` - DEX endpoints, bridges, tokens, strategies
- `.env` - Private keys, RPC endpoints, API keys
- `.env.example` - Template with documentation

### Smart Contracts
- `contracts/FlashArbExecutor.sol` - Flash arbitrage executor
- `contracts/OmniArbExecutor.sol` - Multi-chain executor
- `contracts/modules/SwapHandler.sol` - DEX routing module

### Monitoring
- `live_operational_dashboard.py` - Terminal dashboard
- `operational_dashboard.html` - Web dashboard
- `scripts/linux/launch_dashboard.sh` - Dashboard launcher

### Documentation
- `README.md` - Main documentation
- `DASHBOARD_GUIDE.md` - Dashboard usage
- `MAINNET_READINESS.md` - Deployment checklist
- `QUICK_REFERENCE.md` - This file

---

## 🔒 Security Checklist

Before going live:
- [ ] Private key secured (never commit to git)
- [ ] .env file in .gitignore
- [ ] Contract verified on block explorer
- [ ] Test transaction executed successfully
- [ ] Withdrawal function tested
- [ ] Monitoring dashboards running
- [ ] Alert thresholds configured

---

## 📊 Dashboard Metrics Explained

### Performance Metrics
- **Total Profit**: Gross profit from all trades
- **Gas Spent**: Total gas costs
- **Net Profit**: Profit - Gas (actual earnings)
- **Success Rate**: % of successful trades (target: >70%)

### Sanity Checks
- ⚠️ Gas price > 150 Gwei → Warning
- 🚨 Success rate < 70% → Critical
- 🚨 10+ consecutive failures → Critical
- ⚠️ Net profit < 0 → Warning

---

## 🔍 Troubleshooting

### Dashboard won't start
```bash
pip install rich redis python-dotenv
python3 live_operational_dashboard.py
```

### Contract won't deploy
```bash
# Check RPC connection
curl -X POST YOUR_RPC_URL \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'

# Verify private key format (0x + 64 hex chars)
echo $PRIVATE_KEY | grep -E '^0x[0-9a-fA-F]{64}$'
```

### No trades executing
1. Check gas prices in dashboard
2. Verify MIN_PROFIT_USD threshold
3. Check opportunities_scanned increasing
4. Review recent_errors in dashboard

---

## 🎯 Recommended Settings

### Conservative (Low Risk)
```bash
MIN_PROFIT_USD=15.00
MAX_GAS_PRICE_GWEI=100
MAX_SLIPPAGE_BPS=30
MIN_PROFIT_BPS=50
```

### Balanced (Medium Risk)
```bash
MIN_PROFIT_USD=8.00
MAX_GAS_PRICE_GWEI=150
MAX_SLIPPAGE_BPS=50
MIN_PROFIT_BPS=30
```

### Aggressive (High Risk)
```bash
MIN_PROFIT_USD=5.00
MAX_GAS_PRICE_GWEI=200
MAX_SLIPPAGE_BPS=100
MIN_PROFIT_BPS=10
```

---

## 📞 Support Resources

- **Main Docs**: [README.md](README.md)
- **Dashboard Guide**: [docs/guides/DASHBOARD_GUIDE.md](docs/guides/DASHBOARD_GUIDE.md)
- **Operations**: [docs/guides/OPERATIONS_GUIDE.md](docs/guides/OPERATIONS_GUIDE.md)

---

## ✅ Pre-Flight Checklist

Before starting the bot:
- [ ] .env configured with real values
- [ ] FlashArbExecutor deployed and verified
- [ ] Wallet funded with gas tokens
- [ ] Wallet funded with trading capital
- [ ] Dashboards launched and visible
- [ ] MIN_PROFIT_USD set appropriately
- [ ] MAX_GAS_PRICE_GWEI configured
- [ ] Test trade executed successfully

---

## 🚀 Ready to Launch!

Your system is **mainnet ready** with:
- ✅ All contracts synchronized at Solidity ^0.8.20
- ✅ Production FlashArbExecutor with security features
- ✅ Comprehensive configuration system
- ✅ Real-time 24/7 monitoring dashboards
- ✅ Automated deployment scripts
- ✅ Complete documentation

**Next**: Follow the 5-minute quick start above to go live!

---

**Stay Profitable! 💰**
