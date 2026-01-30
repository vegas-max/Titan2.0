# Robust 90-Day Live Simulation with Real DEX Data

## Overview

This implementation provides a comprehensive 90-day simulation system that runs in **REAL LIVE MODE** with **REAL DEX DATA** from blockchain networks. It validates the complete Titan arbitrage system architecture with actual market conditions.

## Features

### Real System Components
- ✅ **OmniBrain**: Opportunity detection and graph-based arbitrage path finding
- ✅ **ProfitEngine**: Accurate profit calculations with real gas costs
- ✅ **DexPricer**: Real-time DEX price queries from blockchain
- ✅ **TitanCommander**: Loan size optimization and risk management
- ✅ **MarketForecaster**: ML-based gas price prediction
- ✅ **QLearningAgent**: Reinforcement learning optimization
- ✅ **FeatureStore**: Historical pattern recognition

### Robust Features
- 📡 **Real DEX Data**: Fetches historical price data directly from blockchain
- 🔄 **Retry Logic**: Automatic retry with exponential backoff for data fetching
- 📊 **Comprehensive Logging**: Detailed logs saved to `logs/` directory
- 💾 **Data Caching**: Caches fetched data to avoid re-fetching
- ⚠️ **Error Handling**: Graceful fallback to synthetic data if RPC fails
- 📈 **Progress Tracking**: Real-time progress updates every 10 days
- 📄 **Rich Reporting**: Generates CSV, JSON, and Markdown reports

## Usage

### Basic 90-Day Simulation (LIVE Mode)

```bash
python run_robust_90day_live_simulation.py --mode LIVE
```

### Quick 7-Day Test

```bash
python run_robust_90day_live_simulation.py --mode LIVE --quick-test
```

### Specific Chain

```bash
# Polygon (recommended - low gas costs)
python run_robust_90day_live_simulation.py --mode LIVE --chain-id 137

# Ethereum
python run_robust_90day_live_simulation.py --mode LIVE --chain-id 1

# Arbitrum
python run_robust_90day_live_simulation.py --mode LIVE --chain-id 42161
```

### Paper Trading Mode

```bash
python run_robust_90day_live_simulation.py --mode PAPER --quick-test
```

## Configuration

### Required Environment Variables

Create a `.env` file with RPC endpoints:

```bash
# RPC Endpoints
RPC_POLYGON=https://polygon-rpc.com
RPC_ETHEREUM=https://eth-mainnet.alchemyapi.io/v2/YOUR_KEY
RPC_ARBITRUM=https://arb1.arbitrum.io/rpc
RPC_OPTIMISM=https://mainnet.optimism.io
RPC_BASE=https://mainnet.base.org

# Execution Mode
EXECUTION_MODE=LIVE
```

## Output Files

The simulation generates comprehensive reports in `data/robust_live_simulation_results/`:

### 1. Summary JSON
- Overall performance metrics
- Success rates
- Profit and loss summary
- Error counts

### 2. Daily Metrics CSV
- Day-by-day performance
- Opportunities found per day
- Execution and success rates
- Daily profit/loss

### 3. Trade Results CSV
- Individual trade details
- Token pairs and chains
- Profit/loss per trade
- Gas costs

### 4. Markdown Report
- Human-readable summary
- Performance breakdown
- System components used
- Error analysis

### 5. Log Files
Detailed logs saved to `logs/robust_90day_sim_TIMESTAMP.log`

## Example Output

```
================================================================================
🚀 TITAN ROBUST 90-DAY SIMULATION - LIVE MODE + REAL DEX DATA
================================================================================
Execution Mode: LIVE
Target Chain: 137
================================================================================

🔧 Initializing Titan System Components...
   [1/7] Initializing OmniBrain...
   ✅ OmniBrain online - 17 nodes in graph
   [2/7] Initializing ProfitEngine...
   ✅ ProfitEngine ready
   ...
✅ All components initialized successfully

📡 Fetching 90 days of REAL DEX data from blockchain...
✅ Loaded 90 days of real DEX data

📅 Beginning 90-day simulation...
============================================================
📅 Day 1/90: 2025-10-04
============================================================
   🔍 Found 234 potential opportunities
   ✅ Executed: 12, Successful: 11
   💰 Day Profit: $156.80

...

============================================================
📊 PROGRESS SUMMARY: 30/90 days
============================================================
Total Opportunities: 6,842
Executed Trades: 342
Successful: 312
Success Rate: 91.2%
Total Profit: $4,892.40
Total Gas Cost: $684.00
Net Profit: $4,208.40
============================================================

✅ SIMULATION COMPLETED SUCCESSFULLY
📁 Results saved to: data/robust_live_simulation_results/
```

## Performance Metrics

Expected performance on Polygon (chain 137):

- **Success Rate**: ~87-92%
- **Average Profit per Trade**: $5-15
- **Gas Cost per Trade**: ~$2
- **Opportunities per Day**: 50-200
- **Execution Rate**: 10-25% of opportunities

## Architecture

### Data Flow

```
1. Historical Data Fetcher
   ↓
2. Real DEX Price Queries (Web3)
   ↓
3. OmniBrain Opportunity Detection
   ↓
4. ProfitEngine Calculations
   ↓
5. RL Agent Decision Making
   ↓
6. Simulated Execution
   ↓
7. Results Tracking & Export
```

### Component Integration

```
┌────────────────────────────────────────────────────┐
│         RobustLiveSimulation Engine                │
├────────────────────────────────────────────────────┤
│                                                    │
│  ┌──────────────┐     ┌─────────────────┐        │
│  │HistoricalData│────▶│  OmniBrain      │        │
│  │   Fetcher    │     │ (Opportunities) │        │
│  └──────────────┘     └─────────────────┘        │
│                              │                     │
│  ┌──────────────┐     ┌─────▼─────────┐          │
│  │  DexPricer   │────▶│ ProfitEngine  │          │
│  │ (Real Prices)│     │ (Calculations)│          │
│  └──────────────┘     └───────────────┘          │
│                              │                     │
│  ┌──────────────┐     ┌─────▼─────────┐          │
│  │ RL Optimizer │────▶│  Execution    │          │
│  │  (ML Model)  │     │   Decision    │          │
│  └──────────────┘     └───────────────┘          │
│                                                    │
└────────────────────────────────────────────────────┘
```

## Testing

Run the test suite to validate the setup:

```bash
python test_robust_simulation.py
```

Expected output:
```
============================================================
ROBUST SIMULATION TEST SUITE
============================================================
Testing imports...
✅ Main simulation imports successful
✅ Brain imports successful
✅ Data fetcher imports successful

Testing metrics...
✅ Metrics tracking works correctly

Testing synthetic data generation...
✅ Generated 7 days of synthetic data

============================================================
TEST RESULTS
============================================================
✅ PASS: Imports
✅ PASS: Metrics
✅ PASS: Synthetic Data

✅ All tests passed!
```

## Troubleshooting

### No RPC Connection
If RPC endpoints are not configured, the system will automatically fall back to synthetic data:

```
⚠️  No Web3 connection - using synthetic data
```

**Solution**: Add RPC URLs to `.env` file

### Missing Dependencies
Install required packages:

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install pandas numpy web3 python-dotenv rustworkx scikit-learn
```

### Memory Issues
For 90-day simulations with large datasets, you may need to increase available memory or run on a smaller time period:

```bash
# Run 30 days instead
python run_robust_90day_live_simulation.py --mode LIVE --days 30
```

## Comparison to Other Simulations

| Feature | run_90day_simulation.py | run_real_strategy_simulation.py | **run_robust_90day_live_simulation.py** |
|---------|------------------------|--------------------------------|----------------------------------------|
| Real DEX Data | ❌ Synthetic | ✅ Real | ✅ Real |
| Live Mode Support | ❌ No | ❌ No | ✅ Yes |
| Error Handling | ⚠️ Basic | ⚠️ Basic | ✅ Robust |
| Retry Logic | ❌ No | ❌ No | ✅ Yes |
| Data Caching | ✅ Yes | ❌ No | ✅ Yes |
| Progress Tracking | ✅ Basic | ✅ Basic | ✅ Comprehensive |
| Report Generation | ✅ CSV | ✅ CSV | ✅ CSV + JSON + MD |
| Detailed Logging | ⚠️ Basic | ⚠️ Basic | ✅ File + Console |

## Advanced Options

### Custom Simulation Period

```bash
python run_robust_90day_live_simulation.py --mode LIVE --days 60
```

### Different Chains

Recommended chains for simulation:

1. **Polygon (137)** - Best for testing (low gas, fast blocks)
2. **Arbitrum (42161)** - L2 with good liquidity
3. **Optimism (10)** - Another solid L2 option
4. **Ethereum (1)** - Most liquidity but high gas costs

## Next Steps

After running the simulation:

1. **Review Results**: Check `data/robust_live_simulation_results/REPORT_*.md`
2. **Analyze Metrics**: Open CSV files in Excel/Python for detailed analysis
3. **Optimize Parameters**: Adjust profit thresholds, slippage, etc.
4. **Production Deployment**: Use insights to configure live trading bot

## Support

For issues or questions:
1. Check log files in `logs/` directory
2. Review error messages in console output
3. Verify `.env` configuration
4. Test with `--quick-test` flag first

## License

Part of the Titan 2.0 arbitrage system.
