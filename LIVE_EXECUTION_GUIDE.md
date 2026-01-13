# 🚀 TITAN 2.0 - Live Real-Time Execution System (Google Colab)

**Complete End-to-End System Build and Execution Journal for Live Trading**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [What's New](#whats-new)
3. [System Architecture](#system-architecture)
4. [Prerequisites](#prerequisites)
5. [Quick Start](#quick-start)
6. [Execution Journal (Drum)](#execution-journal-drum)
7. [Live Execution Features](#live-execution-features)
8. [Safety Features](#safety-features)
9. [Monitoring & Metrics](#monitoring--metrics)
10. [Troubleshooting](#troubleshooting)
11. [Best Practices](#best-practices)
12. [FAQ](#faq)

---

## 🎯 Overview

This documentation describes the **Live Real-Time Execution System** for TITAN 2.0, specifically designed for Google Colab. It provides a complete end-to-end solution for:

- ✅ **Automated Build**: Full system build with all dependencies
- ✅ **Live Execution**: Real blockchain transactions with real money
- ✅ **Execution Journal**: Comprehensive tracking system (drum) for all operations
- ✅ **Real-Time Monitoring**: Live dashboard and metrics
- ✅ **Safety Systems**: Circuit breakers and risk management
- ✅ **Performance Tracking**: Profit/loss analysis and reporting

### ⚠️ CRITICAL WARNING

**THIS IS A LIVE TRADING SYSTEM THAT USES REAL MONEY:**

- 💰 Executes REAL blockchain transactions
- 💸 Spends REAL gas fees (ETH, MATIC, etc.)
- 📉 Can result in REAL losses
- 🔐 Requires your private key
- ⚡ Operates autonomously once started

**ALWAYS test in PAPER mode first before using LIVE mode!**

---

## 🆕 What's New

This Live Execution System provides several improvements over the standard Google Colab notebook:

### Enhanced Features

1. **Complete Automated Build**
   - One-click installation of all system dependencies
   - Automated repository cloning and setup
   - Comprehensive build verification
   - Zero manual configuration steps

2. **Execution Journal (Drum)**
   - Real-time tracking of all executions
   - Comprehensive profit/loss records
   - Safety event logging
   - Performance metrics collection
   - Historical analysis

3. **Advanced Safety Systems**
   - Multi-layer safety checks
   - Circuit breaker with configurable thresholds
   - Gas price protection
   - Slippage limits
   - Emergency stop capability

4. **Real-Time Monitoring**
   - Live dashboard with auto-refresh
   - Execution statistics
   - Profit/loss tracking
   - Signal queue monitoring
   - System health checks

5. **Live Mode Focus**
   - Optimized for real trading
   - Enhanced error handling
   - Transaction simulation before execution
   - Detailed logging and reporting

---

## 🏗️ System Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                 TITAN LIVE EXECUTION SYSTEM                      │
│                    (Google Colab Environment)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  1. AUTOMATED BUILD SYSTEM                                │  │
│  │     • System dependencies (Node.js, Redis, Python)        │  │
│  │     • Repository cloning                                  │  │
│  │     • Dependency installation                             │  │
│  │     • Build verification                                  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          ↓                                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  2. CONFIGURATION SYSTEM                                  │  │
│  │     • Interactive live mode setup                         │  │
│  │     • Wallet configuration                                │  │
│  │     • Network selection                                   │  │
│  │     • Safety limits configuration                         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          ↓                                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  3. EXECUTION JOURNAL (DRUM)                              │  │
│  │     • Real-time execution tracking                        │  │
│  │     • Profit/loss recording                               │  │
│  │     • Safety event logging                                │  │
│  │     • Performance metrics                                 │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          ↓                                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  4. TITAN BRAIN (Intelligence Layer)                      │  │
│  │     • Opportunity detection                               │  │
│  │     • AI/ML analysis                                      │  │
│  │     • Signal generation                                   │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          ↓                                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  5. TITAN BOT (Execution Layer)                           │  │
│  │     • Signal processing                                   │  │
│  │     • Transaction simulation                              │  │
│  │     • Live execution                                      │  │
│  │     • Safety enforcement                                  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          ↓                                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  6. MONITORING & REPORTING                                │  │
│  │     • Real-time dashboard                                 │  │
│  │     • Execution history                                   │  │
│  │     • Performance reports                                 │  │
│  │     • Health checks                                       │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Build Phase**: System builds all components automatically
2. **Configuration Phase**: User configures wallet, networks, and safety limits
3. **Initialization Phase**: Execution journal created, services started
4. **Operation Phase**: Brain scans → Bot executes → Journal tracks
5. **Monitoring Phase**: Real-time dashboard displays metrics
6. **Reporting Phase**: Generate performance reports

---

## 📦 Prerequisites

### Required

- [ ] **Google Account**: For accessing Google Colab
- [ ] **Dedicated Wallet**: With private key (NOT your main wallet)
- [ ] **Gas Funds**: ETH, MATIC, or other native tokens for gas fees
  - Recommended starting amount: $50-$100 worth
- [ ] **Infura Account**: For RPC access (free tier works)
  - Sign up: https://infura.io

### Recommended

- [ ] **Alchemy Account**: Backup RPC provider (free tier)
  - Sign up: https://alchemy.com
- [ ] **Li.Fi API Key**: For cross-chain operations (optional)
  - Sign up: https://li.fi
- [ ] **Testing Experience**: Previous testing in PAPER mode
- [ ] **Risk Understanding**: Clear understanding of trading risks

### Knowledge Requirements

- ✅ Basic understanding of cryptocurrency wallets
- ✅ Understanding of gas fees and blockchain transactions
- ✅ Awareness of arbitrage trading risks
- ✅ Familiarity with Google Colab interface

---

## 🚀 Quick Start

### Option 1: One-Click Launch (Recommended)

**Windows:**
```batch
# Simply double-click:
LAUNCH_LIVE_EXECUTION_COLAB.bat
```

**Linux/macOS:**
```bash
# Run the launch script:
./launch_live_execution_colab.sh
```

### Option 2: Manual Open

1. Go to Google Colab: https://colab.research.google.com/
2. Click **File** → **Open notebook**
3. Select **GitHub** tab
4. Enter repository: `vegas-max/Titan2.0`
5. Select: `Titan_Live_Execution_Colab.ipynb`
6. Click **Open**

### Option 3: Direct URL

Open this URL in your browser:
```
https://colab.research.google.com/github/vegas-max/Titan2.0/blob/main/Titan_Live_Execution_Colab.ipynb
```

### Step-by-Step Execution

Once the notebook is open:

1. **Read All Warnings**: Understand the risks
2. **Run Step 1**: Complete system build (5-10 minutes)
3. **Run Step 2**: Configure live execution (5 minutes)
4. **Run Step 3**: Start Redis and services
5. **Run Step 4**: Initialize execution journal
6. **Run Step 5**: Start TITAN Brain
7. **Run Step 6**: Start TITAN Bot (LIVE execution begins!)
8. **Run Step 7**: Monitor in real-time
9. **Check Health**: Use Step 9 periodically
10. **Emergency Stop**: Use Step 10 if needed

---

## 📓 Execution Journal (Drum)

The **Execution Journal** (also called "drum") is a comprehensive tracking system that records every aspect of your live trading session.

### What It Tracks

#### 1. Session Metadata
- Session ID (timestamp-based)
- Start time
- Execution mode (LIVE)
- Duration

#### 2. Execution Records
For each trade attempt:
- Timestamp
- Network/chain
- Token pair
- Expected profit
- Actual profit
- Gas cost
- Success/failure status
- Transaction hash
- Revert reason (if failed)

#### 3. Statistics
- Total attempts
- Successful executions
- Failed executions
- Success rate
- Gross profit
- Gas costs
- Net profit
- Average profit per trade

#### 4. Safety Events
- Circuit breaker triggers
- Gas price violations
- Slippage limit hits
- Simulation failures
- RPC failures
- Other safety events

#### 5. Circuit Breaker Status
- Active/inactive status
- Consecutive failures count
- Last trigger time
- Reset events

### Journal File Structure

```json
{
  "session_id": "20260113_143022",
  "started_at": "2026-01-13T14:30:22.123456",
  "mode": "LIVE",
  "executions": [
    {
      "timestamp": "2026-01-13T14:35:15.789",
      "chain_id": 137,
      "token": "USDC",
      "expected_profit_usd": 8.50,
      "actual_profit_usd": 7.85,
      "gas_cost_usd": 0.65,
      "status": "success",
      "tx_hash": "0xabc123...",
      "duration_ms": 2400
    }
  ],
  "statistics": {
    "total_attempts": 15,
    "successful": 13,
    "failed": 2,
    "total_profit_usd": 102.05,
    "total_gas_spent_usd": 8.45,
    "net_profit_usd": 93.60
  },
  "safety_events": [
    {
      "timestamp": "2026-01-13T14:32:10.456",
      "type": "gas_limit_exceeded",
      "details": "Gas price 105 gwei exceeded limit of 100 gwei"
    }
  ],
  "circuit_breaker": {
    "active": false,
    "consecutive_failures": 0,
    "triggered_at": null
  }
}
```

### Accessing Journal Data

#### In Notebook
```python
# Load journal
with open(journal_file, 'r') as f:
    journal = json.load(f)

# Access statistics
stats = journal['statistics']
print(f"Net Profit: ${stats['net_profit_usd']:.2f}")
```

#### File Location
```
/content/Titan2.0/data/execution_journal/journal_<session_id>.json
```

### Journal Reports

Generate detailed reports:
```python
# In Step 11 of notebook
generate_report()
```

Report includes:
- Session summary
- Execution statistics
- Financial performance
- Average per trade
- Safety events summary
- Circuit breaker status

---

## ⚡ Live Execution Features

### Transaction Simulation

**Before every live execution:**

1. Build transaction with current gas prices
2. Simulate using `eth_call` (no gas cost)
3. Verify expected output
4. Check for reverts
5. Only execute if simulation succeeds

This prevents most failed transactions and wasted gas fees.

### Flash Loan Integration

- **Zero Capital Required**: Uses flash loans for all trades
- **Providers**: Balancer V3 (0% fee) or Aave V3 (0.05-0.09% fee)
- **Automatic**: Bot handles flash loan borrowing and repayment
- **Safe**: Atomic execution ensures loan is always repaid

### Gas Management

- **EIP-1559 Support**: Dynamic base fee + priority fee
- **Price Monitoring**: Real-time gas price tracking
- **Ceiling Enforcement**: Transactions blocked if gas too high
- **Optimization**: AI-powered gas price prediction

### Multi-Network Support

Supported networks for live execution:
- Ethereum (chainId: 1)
- Polygon (chainId: 137) - **Recommended for low gas**
- Arbitrum (chainId: 42161) - Low gas
- Optimism (chainId: 10) - Low gas
- Base (chainId: 8453) - Low gas

### MEV Protection

- **Private Relay**: Submit transactions privately
- **BloxRoute Integration**: Optional MEV protection
- **Sandwich Prevention**: Avoid public mempool for high-value trades

---

## 🛡️ Safety Features

### 1. Circuit Breaker

**Automatic pause after consecutive failures:**

Default configuration:
- Triggers after: 5 consecutive failures
- Cooldown period: 60 seconds
- Auto-reset: After cooldown or manual intervention

**What triggers it:**
- Failed transactions
- Simulation failures
- RPC errors
- Gas limit violations

**What it does:**
- Pauses all new executions
- Allows pending trades to complete
- Logs event to journal
- Requires manual reset or auto-reset after cooldown

### 2. Gas Price Limits

**Protects against network congestion:**

- Maximum gas price: Configurable (default: 100 gwei)
- Monitored continuously
- Transactions blocked if limit exceeded
- Prevents overpaying during congestion

### 3. Slippage Protection

**Limits price movement impact:**

- Maximum slippage: Configurable (default: 0.5%)
- Applied to all swaps
- Prevents unfavorable execution
- Dynamic adjustment based on volatility

### 4. Profit Thresholds

**Ensures trades are worthwhile:**

- Minimum profit: Configurable (default: $5)
- After all fees (gas, flash loan, slippage)
- Prevents low-profit trades that risk failure
- Adjustable based on risk tolerance

### 5. Simulation Enforcement

**No blind execution:**

- All LIVE trades must pass simulation
- Uses `eth_call` for zero-cost testing
- Verifies expected output
- Checks for revert conditions
- 95%+ accuracy in preventing failures

### 6. Emergency Stop

**Immediate shutdown capability:**

- Stop all executions instantly
- Preserve journal data
- Safe shutdown of all components
- Available at any time via Step 10

---

## 📊 Monitoring & Metrics

### Real-Time Dashboard

The live monitoring dashboard (Step 7) shows:

#### Execution Statistics
- Total attempts
- Successful trades
- Failed trades
- Success rate percentage

#### Profit & Loss
- Gross profit
- Gas costs
- Net profit
- Average per trade

#### Signal Queue
- Pending signals
- Processed signals
- Processing rate

#### Circuit Breaker Status
- Active/inactive
- Consecutive failures
- Time to reset

#### System Health
- Brain status
- Bot status
- Redis status
- RPC connectivity

### Performance Metrics

Track key performance indicators:

1. **Success Rate**: % of successful executions
2. **Average Profit**: Mean profit per successful trade
3. **Gas Efficiency**: Gas cost vs. profit ratio
4. **Execution Speed**: Time from signal to completion
5. **Opportunity Utilization**: Signals executed vs. total

### Historical Analysis

View execution history:
- Chronological trade list
- Profit/loss by trade
- Best and worst trades
- Time-series analysis
- Network-specific performance

### Health Checks

Regular system health monitoring:
- Component status (Brain, Bot, Redis)
- RPC provider connectivity
- Signal queue depth
- Memory usage
- Processing rate

---

## 🔧 Troubleshooting

### Common Issues

#### 1. "Private key invalid"

**Symptoms:**
- Error during configuration
- Cannot start bot

**Solutions:**
- Remove `0x` prefix if present
- Ensure exactly 64 hexadecimal characters
- Check for extra spaces or newlines
- Verify key is from correct wallet

#### 2. "Redis connection failed"

**Symptoms:**
- Warning during Redis start
- Bot falls back to file-based signals

**Impact:**
- System works but slower signal propagation
- Dashboard updates may be delayed

**Solutions:**
- Restart Redis (re-run Step 3)
- Check if Redis process is running
- System will work with file-based fallback

#### 3. "RPC rate limit exceeded"

**Symptoms:**
- Errors in brain logs
- Slow opportunity detection
- Failed transactions

**Solutions:**
- Add Alchemy as backup provider
- Upgrade to Infura paid tier
- Reduce scan frequency
- Use fewer concurrent networks

#### 4. "No opportunities detected"

**Symptoms:**
- Dashboard shows zero signals
- No activity after 5-10 minutes

**Possible Causes:**
- High market efficiency (few arbitrage opportunities)
- Gas prices too high (blocking trades)
- Profit threshold too high
- RPC connectivity issues

**Solutions:**
- Lower minimum profit threshold
- Increase max gas price limit
- Check network conditions
- Verify RPC providers working

#### 5. "Circuit breaker triggered"

**Symptoms:**
- All executions paused
- Dashboard shows circuit breaker active

**Causes:**
- Multiple consecutive failures
- Network issues
- Gas price spikes
- RPC problems

**Solutions:**
- Wait for auto-reset (60 seconds)
- Check underlying issue (gas, RPC, etc.)
- Manually stop and restart if needed
- Review failure logs

#### 6. "Simulation failures"

**Symptoms:**
- Trades not executing
- Many simulation errors in logs

**Causes:**
- Slippage exceeds tolerance
- Liquidity changed between detection and execution
- Gas estimation issues
- Price movements

**Solutions:**
- Increase slippage tolerance slightly
- Faster execution (reduce latency)
- Check for sufficient liquidity
- Normal in volatile markets

### Debug Mode

Enable detailed logging:

1. Edit `.env` file:
```env
LOG_LEVEL=DEBUG
```

2. Restart Brain and Bot
3. Check logs for detailed information

### Log Locations

```
Brain logs: Console output in Step 5
Bot logs: Console output in Step 6
Journal: /content/Titan2.0/data/execution_journal/
Signals: /content/Titan2.0/signals/
```

---

## ✅ Best Practices

### Before Starting

1. **Test in PAPER mode first**
   - Use `Titan_Google_Colab.ipynb` (original notebook)
   - Run for at least 30-60 minutes
   - Verify system works correctly
   - Understand the workflow

2. **Use dedicated wallet**
   - Create new wallet just for trading
   - Never use your main wallet
   - Keep private key secure
   - No personal funds in trading wallet

3. **Start with minimal funds**
   - $50-$100 for gas only
   - Test with smallest viable amounts
   - Gradually increase if successful
   - Don't risk more than you can afford to lose

4. **Choose low-gas network**
   - Start with Polygon (very low gas)
   - Or use Arbitrum, Optimism, Base
   - Avoid Ethereum mainnet initially
   - Lower gas = lower risk per trade

### During Operation

1. **Monitor continuously**
   - Keep dashboard running (Step 7)
   - Check every 5-10 minutes minimum
   - Be ready to emergency stop
   - Watch for circuit breaker triggers

2. **Respect safety limits**
   - Don't disable circuit breaker
   - Keep gas limits reasonable
   - Maintain profit thresholds
   - Don't override simulation

3. **Track performance**
   - Check execution history regularly
   - Calculate net profit/loss
   - Monitor gas efficiency
   - Adjust strategy as needed

4. **Be ready to stop**
   - Know how to run Step 10
   - Stop if unexpected behavior
   - Stop if losing money
   - Stop if gas costs too high

### After Session

1. **Generate report**
   - Run Step 11 for comprehensive report
   - Review all executions
   - Analyze what worked
   - Identify improvements

2. **Save journal**
   - Download journal file
   - Keep for tax records
   - Analyze performance trends
   - Learn from mistakes

3. **Withdraw profits**
   - Extract profits from contract
   - Don't leave large amounts on-chain
   - Keep only gas reserves
   - Secure your funds

4. **Review and adjust**
   - Analyze success rate
   - Optimize parameters
   - Try different networks
   - Refine strategy

### Security Best Practices

1. **Private key management**
   - Never share your private key
   - Don't save in browser
   - Use environment variables only
   - Revoke if compromised

2. **Access control**
   - Don't share Colab notebook if private key entered
   - Clear outputs before sharing
   - Use separate API keys per project
   - Rotate keys regularly

3. **Fund management**
   - Only keep gas money in wallet
   - Withdraw profits regularly
   - Don't accumulate large balances
   - Use multisig for large amounts

4. **Monitoring**
   - Set up alerts (optional)
   - Monitor blockchain explorer
   - Track wallet balance
   - Review all transactions

---

## ❓ FAQ

### General Questions

**Q: How much money do I need to start?**

A: You only need $50-$100 for gas fees. The system uses flash loans for trading capital (zero capital required).

**Q: Can I lose money?**

A: Yes. You can lose money from:
- Gas fees on failed transactions
- Slippage exceeding tolerance
- Market movements during execution
- Network congestion
- System bugs

**Q: Is this profitable?**

A: It can be, but:
- No guarantees
- Market-dependent
- Requires monitoring and optimization
- Competition from other bots
- Success varies by network and conditions

**Q: How long can I run it?**

A: Google Colab sessions:
- Timeout after ~12 hours of inactivity
- May be terminated during high usage
- Not suitable for 24/7 production
- Better for testing and short sessions

### Technical Questions

**Q: Which network is best for beginners?**

A: Polygon (chainId: 137) because:
- Very low gas fees ($0.01-0.10 per transaction)
- Fast block times (2 seconds)
- Good DEX liquidity
- Lower risk per trade

**Q: What is the circuit breaker?**

A: Safety mechanism that automatically pauses execution after consecutive failures to prevent:
- Cascading losses
- Gas waste on failing trades
- System overload
- Runaway execution

**Q: Can I run multiple instances?**

A: Not recommended because:
- Nonce conflicts
- Race conditions
- Increased failure rate
- Wasted gas
- Run one instance per wallet

**Q: How do I know if it's working?**

A: Check these indicators:
- Brain shows "scanning" messages
- Signals appear in queue
- Executions in dashboard
- Transactions on blockchain explorer

### Safety Questions

**Q: Can someone steal my private key?**

A: Risk factors:
- Google Colab is generally secure
- Don't share notebooks with key entered
- Clear outputs before sharing
- Use dedicated wallet with minimal funds
- Never store key in code

**Q: What if I lose internet connection?**

A: If disconnected:
- Colab session continues briefly
- Then terminates
- Pending transactions may complete
- No new executions started
- Journal preserved

**Q: How do I stop immediately?**

A: Emergency stop process:
1. Run Step 10 in notebook
2. Verify all processes stopped
3. Check blockchain explorer for pending transactions
4. Wait for pending transactions to complete

**Q: What happens to pending transactions?**

A: When stopped:
- Submitted transactions will complete
- Unsubmitted signals ignored
- Cannot cancel blockchain transactions
- Wait for completion or failure

### Performance Questions

**Q: Why aren't I seeing profits?**

A: Common reasons:
- Market efficiency (few arbitrage opportunities)
- Gas costs too high relative to profits
- Profit threshold set too high
- Wrong network selection
- High competition from other bots
- Poor market conditions

**Q: How can I improve success rate?**

A: Optimization strategies:
- Lower profit threshold (but stay profitable after gas)
- Increase slippage tolerance slightly
- Use faster RPC providers
- Select less competitive networks
- Optimize gas settings
- Run during high volatility

**Q: Why do simulations fail?**

A: Simulation failures indicate:
- Trade would revert on-chain
- Slippage too high
- Liquidity changed
- Price moved
- This is GOOD - saves gas!

**Q: What's a good success rate?**

A: Typical rates:
- 70-85%: Normal range
- 85-95%: Excellent
- <70%: Investigate issues
- 95%+: May be too conservative

---

## 📚 Additional Resources

### Documentation

- **Main README**: [README.md](README.md) - Complete system documentation
- **Google Colab Guide**: [GOOGLE_COLAB_STEP_BY_STEP.md](GOOGLE_COLAB_STEP_BY_STEP.md) - Detailed Colab walkthrough
- **Operations Guide**: [OPERATIONS_GUIDE.md](OPERATIONS_GUIDE.md) - System operations manual
- **Security Guide**: [SECURITY_SUMMARY.md](SECURITY_SUMMARY.md) - Security best practices
- **Mainnet Modes**: [MAINNET_MODES.md](MAINNET_MODES.md) - Understanding PAPER vs LIVE

### Support

- **GitHub Repository**: https://github.com/vegas-max/Titan2.0
- **Issues**: https://github.com/vegas-max/Titan2.0/issues
- **Discussions**: https://github.com/vegas-max/Titan2.0/discussions

### External Resources

- **Infura**: https://infura.io - RPC provider
- **Alchemy**: https://alchemy.com - Backup RPC provider
- **Li.Fi**: https://li.fi - Cross-chain bridge aggregator
- **Google Colab**: https://colab.research.google.com - Notebook platform

---

## ⚠️ Final Disclaimer

**THIS IS EXPERIMENTAL SOFTWARE FOR LIVE TRADING WITH REAL MONEY**

By using this system, you acknowledge and accept that:

- ❌ **NOT FINANCIAL ADVICE**: This is for educational purposes only
- ❌ **RISK OF LOSS**: You can lose money from failed trades, gas costs, and market movements
- ❌ **NO WARRANTY**: Software provided "as is" without any guarantees of functionality or profitability
- ❌ **YOUR RESPONSIBILITY**: You are fully responsible for all trades, losses, and consequences
- ❌ **NO GUARANTEES**: Past performance does not indicate future results
- ❌ **EXPERIMENTAL**: Software may contain bugs, errors, or unexpected behavior

**Recommended Approach:**

1. ✅ Test extensively in PAPER mode first
2. ✅ Start with minimal funds ($50-100 for gas)
3. ✅ Use a dedicated wallet (not your main wallet)
4. ✅ Monitor continuously during operation
5. ✅ Be ready to stop immediately if needed
6. ✅ Understand all risks before starting
7. ✅ Only risk what you can afford to lose

**The authors and contributors are not liable for any losses, damages, or consequences arising from the use of this software.**

---

**Built with ❤️ by the Titan Team**

⭐ **Star the repo if you find it useful!** ⭐

[GitHub](https://github.com/vegas-max/Titan2.0) • [Issues](https://github.com/vegas-max/Titan2.0/issues) • [Discussions](https://github.com/vegas-max/Titan2.0/discussions)
