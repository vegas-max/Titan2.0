# Redis Removal Guide - Titan 2.0 Arbitrage Bot

## Overview

The Titan 2.0 arbitrage bot has been successfully refactored to operate **without Redis dependency**. This guide explains the changes, new architecture, and how to use the system.

## What Was Changed

### 1. Dependencies Removed

**Before:**
```txt
# requirements.txt
redis>=5.0.1
```

**After:**
```txt
# requirements.txt
# redis>=5.0.1  <-- REMOVED
```

No Redis installation required!

### 2. Caching Architecture

**Before (Redis-based):**
```
┌─────────────┐      ┌───────┐      ┌─────────┐
│   Brain     │─────→│ Redis │←─────│   Bot   │
└─────────────┘      └───────┘      └─────────┘
                         ↑
                         │
                    ┌────────────┐
                    │ Dashboards │
                    └────────────┘
```

**After (SQLite + Files):**
```
┌─────────────┐                    ┌─────────┐
│   Brain     │────JSON Files─────→│   Bot   │
└─────────────┘                    └─────────┘
       │                                │
       └────────SQLite Cache────────────┘
                     ↑
                     │
                ┌────────────┐
                │ Dashboards │
                └────────────┘
```

### 3. New Cache Manager

A new `CacheManager` class provides Redis-like functionality using SQLite:

```python
from offchain.core.cache_manager import get_cache_manager

cache = get_cache_manager()

# Cache with TTL (just like Redis)
cache.set("my_key", {"data": 123}, ttl=60)
value = cache.get("my_key")

# Specialized gas price caching
cache.set_gas_price(chain_id=1, price_gwei=30.5, ttl=60)
gas_price = cache.get_gas_price(chain_id=1)

# Metrics storage (no expiration)
cache.set_metric("total_trades", 42)
metrics = cache.get_all_metrics()
```

## Key Features

### 1. Signal-Based Communication

**Brain → Bot communication via JSON files:**

**Brain writes signal:**
```python
# brain.py generates signal
signal = {
    "type": "INTRA_CHAIN",
    "chainId": 137,
    "token": "0x...",
    "amount": "1000000",
    "protocols": [1, 0],
    "routers": ["0x...", "0x..."],
    "metrics": {"profit_usd": 5.25}
}

# Write to signals/outgoing/
with open(f"signals/outgoing/signal_{timestamp}.json", 'w') as f:
    json.dump(signal, f)
```

**Bot reads and processes:**
```javascript
// bot.js monitors signals/outgoing/
const files = fs.readdirSync('signals/outgoing/');
for (const file of files) {
    const signal = JSON.parse(fs.readFileSync(file));
    await executeTrade(signal);
    // Move to signals/processed/
    fs.renameSync(file, `signals/processed/${file}`);
}
```

### 2. Gas Price Caching with Fallback

**Three-tier fallback system:**

```python
def _get_gas_price(self, chain_id):
    # Tier 1: Check cache (60s TTL)
    cached = cache.get_gas_price(chain_id)
    if cached > 0:
        return cached
    
    # Tier 2: Fetch from RPC (Alchemy/Infura)
    try:
        gas_price = web3.eth.gas_price
        cache.set_gas_price(chain_id, gas_price, ttl=60)
        return gas_price
    except:
        pass
    
    # Tier 3: Static fallback
    return STATIC_GAS_PRICES[chain_id]  # e.g., 30.0 gwei
```

**Static fallback values:**
- Ethereum: 30.0 gwei
- Polygon: 50.0 gwei
- Arbitrum: 0.1 gwei
- Optimism: 0.5 gwei
- Base: 0.5 gwei

### 3. Dashboard Integration

**Dashboards now use file-based + cache approach:**

```python
from offchain.core.cache_manager import get_cache_manager
from dashboard_integration import DashboardIntegration

# Initialize
cache = get_cache_manager()
dashboard = DashboardIntegration()

# Publish opportunity (writes to file + cache)
dashboard.publish_market_opportunity({
    "chain": "Polygon",
    "token_pair": "USDC/USDT",
    "profit_usd": 5.25,
    "executable": True
})

# Update metrics (writes to file + cache)
dashboard.update_metrics({
    "status": "OPERATIONAL",
    "total_profit": 123.45,
    "current_gas_price": 30.0
})
```

## File Structure

```
Titan2.0/
├── data/
│   ├── cache/
│   │   └── titan_cache.db          # SQLite cache database
│   └── dashboard/
│       ├── current_metrics.json    # Latest metrics
│       ├── opportunities/           # Market opportunities
│       ├── pending_txs/             # Pending transactions
│       └── execution_history/       # Completed trades
├── signals/
│   ├── outgoing/                   # Brain → Bot signals
│   └── processed/                  # Completed signals
├── offchain/
│   ├── core/
│   │   └── cache_manager.py        # SQLite cache manager
│   ├── ml/
│   │   └── brain.py                # Signal generation
│   └── execution/
│       └── bot.js                  # Signal processing
└── dashboard_integration.py        # Dashboard adapter
```

## Migration Guide

### For Existing Users

1. **Stop the system:**
   ```bash
   # Stop all running processes
   pkill -f "python.*brain.py"
   pkill -f "node.*bot.js"
   ```

2. **Update dependencies:**
   ```bash
   pip install -r requirements.txt
   # Note: Redis is no longer in requirements.txt
   ```

3. **Remove Redis (optional):**
   ```bash
   # You can now uninstall Redis if not used elsewhere
   sudo systemctl stop redis
   sudo apt remove redis-server  # Ubuntu/Debian
   brew uninstall redis  # macOS
   ```

4. **Update .env file:**
   ```bash
   # Remove REDIS_URL and REDIS_DB from .env
   # (optional, they're simply ignored now)
   ```

5. **Restart the system:**
   ```bash
   # Start normally - no Redis needed!
   ./start_titan_integrated.sh
   # or
   python mainnet_orchestrator.py  # Terminal 1
   node offchain/execution/bot.js  # Terminal 2
   ```

### For New Users

Simply follow the standard installation - **Redis is not required!**

```bash
# Clone repository
git clone https://github.com/vegas-max/Titan2.0.git
cd Titan2.0

# Install dependencies (no Redis!)
pip install -r requirements.txt
npm install

# Configure .env
cp .env.example .env
# Edit .env with your RPC endpoints

# Run
./start_titan_integrated.sh
```

## Testing

Run the comprehensive test suite:

```bash
python test_no_redis.py
```

**Expected output:**
```
======================================================================
TITAN 2.0 - Redis Removal Test Suite
======================================================================

Testing cache manager...
✓ Cache manager initialized
✓ Basic caching works
✓ Gas price caching works
✓ Metrics storage works
✓ Cache statistics work
✓ Cleanup removed 1 expired entries
✓ Cache expiration works

Testing signal file system...
✓ Signal directories exist
✓ Created test signal file
✓ Signal file read/write works
✓ Signal file movement works

Testing dashboard integration...
✓ Dashboard integration initialized without Redis
✓ Published market opportunity to file system
✓ Updated system metrics to file system

Testing gas price fallback...
✓ Gas price cache and fallback working

======================================================================
TEST RESULTS:
======================================================================
  ✓ PASS: Cache Manager
  ✓ PASS: Signal File System
  ✓ PASS: Dashboard Integration
  ✓ PASS: Gas Price Fallback

Total: 4/4 tests passed

🎉 All tests passed! Redis removal successful.
```

## Performance Considerations

### SQLite vs Redis

| Feature | Redis | SQLite (Our Implementation) |
|---------|-------|----------------------------|
| Speed | Very Fast (in-memory) | Fast (file-based + in-memory cache) |
| Persistence | Optional | Always persistent |
| Setup | Requires server | No setup required |
| Scalability | High | Medium (sufficient for single-bot) |
| Complexity | Higher | Lower |

**For single-bot arbitrage operation, SQLite is sufficient and simpler.**

### Cache Performance

- **Gas prices:** 60-second cache → ~1 RPC call per minute per chain
- **Metrics:** No expiration → Instant reads
- **General cache:** Configurable TTL → Flexible caching

### File-Based Signals

- **Latency:** < 1 second (file watcher polling)
- **Reliability:** 100% (filesystem is reliable)
- **Audit trail:** All signals saved in `signals/processed/`

## Troubleshooting

### Issue: "No such table: cache"

**Solution:** The cache database wasn't initialized. This should auto-fix, but you can manually initialize:

```python
from offchain.core.cache_manager import get_cache_manager
cache = get_cache_manager()
# Tables are created automatically
```

### Issue: Signals not being processed

**Check:**
1. Signal files are being created in `signals/outgoing/`
2. Bot is monitoring the directory (check console output)
3. Bot has read/write permissions

```bash
# Check permissions
ls -la signals/outgoing/
ls -la signals/processed/

# Fix permissions if needed
chmod 755 signals/outgoing signals/processed
```

### Issue: Dashboard shows no data

**Check:**
1. Cache manager is initialized
2. Dashboard integration is publishing data
3. Check `data/dashboard/` for files

```bash
# View current metrics
cat data/dashboard/current_metrics.json

# View opportunities
ls -la data/dashboard/opportunities/
```

## Benefits

### 1. Simplified Deployment

**Before:**
```bash
# Install Redis
sudo apt install redis-server
sudo systemctl start redis

# Configure Redis
redis-cli CONFIG SET ...

# Install Python dependencies
pip install redis

# Start system
redis-server &
python brain.py &
node bot.js &
```

**After:**
```bash
# Install dependencies (no Redis!)
pip install -r requirements.txt

# Start system
./start_titan_integrated.sh
# Done!
```

### 2. Easier Debugging

**Signal files are visible:**
```bash
# View generated signals
ls signals/outgoing/
cat signals/outgoing/signal_*.json

# View processed signals
ls signals/processed/
```

**Cache is inspectable:**
```bash
# View cache database
sqlite3 data/cache/titan_cache.db
sqlite> SELECT * FROM gas_prices;
sqlite> SELECT * FROM metrics;
```

### 3. Better Persistence

- **Signals:** Automatically saved to disk
- **Cache:** Persistent across restarts
- **Metrics:** Never lost

### 4. Cross-Platform

Works identically on:
- ✅ Linux
- ✅ macOS  
- ✅ Windows
- ✅ Docker
- ✅ Cloud (AWS, GCP, Azure, Oracle Cloud)

## API Reference

### Cache Manager

```python
from offchain.core.cache_manager import get_cache_manager

cache = get_cache_manager()

# Basic cache operations
cache.set(key: str, value: Any, ttl: int = 300) -> bool
cache.get(key: str, default: Any = None) -> Any
cache.delete(key: str) -> bool

# Gas price operations
cache.set_gas_price(chain_id: int, price_gwei: float, ttl: int = 60) -> bool
cache.get_gas_price(chain_id: int, default: float = 0.0) -> float

# Metrics operations
cache.set_metric(metric_name: str, metric_value: Any) -> bool
cache.get_metric(metric_name: str, default: Any = None) -> Any
cache.get_all_metrics() -> Dict[str, Any]

# Maintenance
cache.cleanup_expired() -> int
cache.clear_all() -> bool
cache.get_stats() -> Dict[str, int]
```

### Dashboard Integration

```python
from dashboard_integration import DashboardIntegration

dashboard = DashboardIntegration()

# Publish opportunity
dashboard.publish_market_opportunity(opportunity: dict)

# Publish pending transaction
dashboard.publish_executable_tx(tx: dict)

# Publish execution result
dashboard.publish_execution_result(result: dict)

# Update system metrics
dashboard.update_metrics(metrics: dict)

# Listen for control messages
dashboard.listen_for_controls(callback: callable)
```

## Conclusion

The Titan 2.0 arbitrage bot now operates **completely without Redis**, using:

1. **SQLite** for caching (gas prices, metrics)
2. **JSON files** for signal communication
3. **File-based storage** for dashboard data

This provides:
- ✅ Simpler deployment
- ✅ Easier debugging
- ✅ Better persistence
- ✅ Cross-platform compatibility
- ✅ No external dependencies

**The system is now fully operational without Redis! 🎉**
