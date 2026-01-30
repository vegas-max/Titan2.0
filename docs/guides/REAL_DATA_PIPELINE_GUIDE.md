# Real Data Pipeline Implementation Guide

## Overview

This guide covers the implementation of the real data pipeline, Rust HTTP server, and ML model training features added to Titan 2.0.

## Table of Contents

1. [Real Data Pipeline](#real-data-pipeline)
2. [Rust HTTP Server](#rust-http-server)
3. [ML Model Training](#ml-model-training)
4. [Configuration](#configuration)
5. [Usage Examples](#usage-examples)
6. [Troubleshooting](#troubleshooting)

---

## Real Data Pipeline

### Features

The real data pipeline replaces simulated scanning with actual blockchain data:

- **WebSocket Connections**: Real-time streaming data from DEX subgraphs
- **Direct Pool Queries**: On-chain queries for exact pool reserves
- **Multi-DEX Support**: Uniswap V3, Sushiswap, QuickSwap, Curve, Balancer
- **Automatic Fallback**: Falls back to direct queries if WebSocket unavailable

### Components

#### 1. WebSocket Manager (`offchain/core/websocket_manager.py`)

Manages WebSocket connections to multiple DEX endpoints:

```python
from offchain.core.websocket_manager import WebSocketManager

# Initialize
config = load_config()
ws_manager = WebSocketManager(config)

# Start connections
await ws_manager.start()
await ws_manager.connect('uniswap_v3', 'polygon')

# Register callback
def on_pool_update(data):
    print(f"Pool update: {data}")

ws_manager.register_callback('uniswap_v3:polygon', on_pool_update)

# Check connection health
status = ws_manager.get_connection_status()
```

#### 2. Real Data Pipeline (`offchain/core/real_data_pipeline.py`)

Main pipeline for fetching and caching real DEX data:

```python
from offchain.core.real_data_pipeline import RealDataPipeline

# Initialize
pipeline = RealDataPipeline(
    config=config,
    web3_connections=web3_pool,
    use_websockets=True
)

# Start pipeline
await pipeline.start()

# Get pool reserves
reserves = await pipeline.get_pool_reserves(
    chain_id=137,  # Polygon
    pool_address="0x...",
    dex_type='uniswap_v3'
)

# Scan for opportunities
opportunities = await pipeline.scan_opportunities(
    chains=[137, 1],
    token_pairs=[('WMATIC', 'USDC'), ('WETH', 'USDT')],
    min_liquidity_usd=10000
)

# Get statistics
stats = pipeline.get_stats()
```

### Configuration

Add to `config.json`:

```json
{
  "advanced_features": {
    "real_data_pipeline": {
      "enabled": true,
      "use_websockets": true,
      "polling_interval_seconds": 5,
      "cache_duration_seconds": 10,
      "description": "Use real DEX data via WebSockets and direct queries"
    }
  }
}
```

Add to `.env`:

```bash
# Real Data Pipeline Configuration
USE_REAL_DATA=true
USE_WEBSOCKETS=true
REAL_DATA_POLLING_INTERVAL=5
```

---

## Rust HTTP Server

### Features

High-performance HTTP server for performance-critical operations:

- **Built with Axum**: Fast, ergonomic web framework
- **REST API**: Query pool data, check health, get metrics
- **CORS Support**: Cross-origin resource sharing enabled
- **Concurrent Processing**: Handles multiple requests efficiently

### API Endpoints

#### 1. Health Check

```bash
GET /health

Response:
{
  "status": "healthy",
  "version": "0.1.0",
  "uptime_seconds": 3600,
  "rust_engine": true
}
```

#### 2. Pool Query

```bash
POST /api/pool
Content-Type: application/json

{
  "chain_id": 137,
  "pool_address": "0x...",
  "dex_type": "uniswap_v3"
}

Response:
{
  "pool_address": "0x...",
  "reserves": {
    "reserve0": "1000000000000000000",
    "reserve1": "2000000000000000000",
    "token0": "0x...",
    "token1": "0x..."
  },
  "error": null
}
```

#### 3. Metrics

```bash
GET /api/metrics

Response:
{
  "queries_total": 1234,
  "queries_success": 1200,
  "queries_failed": 34,
  "avg_response_time_ms": 45.2,
  "uptime_seconds": 86400
}
```

### Building and Running

#### Build

```bash
cd core-rust
cargo build --release --bin titan_server
```

#### Run

```bash
# Using the startup script
./start_rust_server.sh

# Or manually
export RUST_SERVER_PORT=3000
./core-rust/target/release/titan_server

# With custom port
RUST_SERVER_PORT=8080 ./start_rust_server.sh
```

### Configuration

Add to `.env`:

```bash
# Rust Engine Configuration
ENABLE_RUST_ENGINE=true
RUST_SERVER_PORT=3000
```

---

## ML Model Training

### Features

Real machine learning model training for:

- **Market Forecaster**: Gas price prediction using XGBoost and Gradient Boosting
- **RL Optimizer**: Q-Learning agent for parameter optimization
- **Model Persistence**: Save/load trained models
- **Performance Metrics**: Track accuracy, MSE, MAE, R²

### Training Script

The `train_ml_models.py` script trains both models:

```bash
# Basic training (10,000 samples, 10,000 episodes)
./train_ml_models.py

# Custom training parameters
./train_ml_models.py --samples 50000 --episodes 20000

# Specify data directory
./train_ml_models.py --data-dir /path/to/data
```

### Using Trained Models

#### MarketForecaster

```python
from offchain.ml.cortex.forecaster import MarketForecaster

forecaster = MarketForecaster()

# Load pre-trained models automatically
# Models are saved in data/models/

# Make predictions
forecaster.ingest_gas(45.2)  # Current gas price
forecaster.ingest_price(2000)  # ETH price
forecaster.ingest_volume(1e9)  # Trading volume

prediction = forecaster.predict_gas_trend()
# Returns: 'rising', 'stable', or 'falling'
```

#### QLearningAgent

```python
from offchain.ml.cortex.rl_optimizer import QLearningAgent

agent = QLearningAgent()

# Load pre-trained Q-table automatically
# Q-table is saved in data/q_table.json

# Get optimal action for current state
state = "ethereum_medium_normal"
action_params = agent.get_action(state)
# Returns: {'slippage': 0.5, 'priority_fee': 2.5}

# Update agent after execution
reward = 100  # Profit in USD
success = True
next_state = "ethereum_low_low"
agent.update(state, action_params, reward, next_state, success)
```

### Model Files

After training, the following files are created:

```
data/
├── models/
│   ├── forecaster_xgb.pkl          # XGBoost model
│   ├── forecaster_gb.pkl           # Gradient Boosting model
│   ├── forecaster_scaler.pkl       # Feature scaler
│   └── forecaster_metadata.json    # Model metadata
├── q_table.json                     # Q-Learning table
├── rl_metrics.json                  # RL agent metrics
├── replay_buffer.json               # Experience replay buffer
└── training_data.csv                # Training dataset
```

### Configuration

Add to `.env`:

```bash
# ML Model Configuration
ENABLE_ML_MODELS=true
ML_MODELS_TRAINED=false  # Set to true after training
ML_AUTO_RETRAIN=false
```

---

## Configuration

### Complete `.env` Configuration

```bash
# Real Data Pipeline
USE_REAL_DATA=true
USE_WEBSOCKETS=true
REAL_DATA_POLLING_INTERVAL=5

# Rust Engine
ENABLE_RUST_ENGINE=true
RUST_SERVER_PORT=3000

# ML Models
ENABLE_ML_MODELS=true
ML_MODELS_TRAINED=false
ML_AUTO_RETRAIN=false
```

### config.json Updates

```json
{
  "advanced_features": {
    "real_data_pipeline": {
      "enabled": true,
      "use_websockets": true,
      "polling_interval_seconds": 5,
      "cache_duration_seconds": 10
    }
  }
}
```

---

## Usage Examples

### Example 1: Start Complete System with Real Data

```bash
# 1. Train ML models (first time only)
./train_ml_models.py --samples 10000 --episodes 10000

# 2. Update .env
echo "ML_MODELS_TRAINED=true" >> .env

# 3. Start Rust server
./start_rust_server.sh &

# 4. Start Python brain with real data
USE_REAL_DATA=true python3 arm_brain.py
```

### Example 2: Test WebSocket Connections

```python
import asyncio
from offchain.core.websocket_manager import WebSocketManager
import json

async def test_websockets():
    # Load config
    with open('config.json') as f:
        config = json.load(f)
    
    # Create manager
    ws_manager = WebSocketManager(config)
    
    # Define callback
    def on_update(data):
        print(f"Received: {data}")
    
    # Start and connect
    await ws_manager.start()
    await ws_manager.connect('uniswap_v3', 'polygon')
    ws_manager.register_callback('uniswap_v3:polygon', on_update)
    
    # Let it run for 30 seconds
    await asyncio.sleep(30)
    
    # Check status
    status = ws_manager.get_connection_status()
    print(f"Status: {status}")
    
    # Stop
    await ws_manager.stop()

asyncio.run(test_websockets())
```

### Example 3: Query Rust Server

```bash
# Health check
curl http://localhost:3000/health

# Get metrics
curl http://localhost:3000/api/metrics

# Query pool (requires JSON)
curl -X POST http://localhost:3000/api/pool \
  -H "Content-Type: application/json" \
  -d '{
    "chain_id": 137,
    "pool_address": "0x...",
    "dex_type": "uniswap_v3"
  }'
```

---

## Troubleshooting

### WebSocket Connection Issues

**Problem**: WebSocket connections failing

**Solutions**:
1. Check if GraphQL endpoints support WebSocket (wss://)
2. Verify network connectivity
3. Check firewall settings
4. Enable fallback to polling:
   ```bash
   USE_WEBSOCKETS=false
   ```

### Rust Server Build Errors

**Problem**: Compilation fails

**Solutions**:
1. Update Rust toolchain:
   ```bash
   rustup update
   ```
2. Clean and rebuild:
   ```bash
   cd core-rust
   cargo clean
   cargo build --release --bin titan_server
   ```
3. Check dependencies in Cargo.toml

### ML Training Issues

**Problem**: Training fails or models not loading

**Solutions**:
1. Install required packages:
   ```bash
   pip install scikit-learn xgboost joblib pandas numpy
   ```
2. Ensure data directory exists:
   ```bash
   mkdir -p data/models
   ```
3. Check permissions
4. Run with debug output:
   ```bash
   LOG_LEVEL=DEBUG ./train_ml_models.py
   ```

### Performance Issues

**Problem**: Slow data fetching

**Solutions**:
1. Enable WebSocket for faster updates
2. Increase cache duration:
   ```bash
   REAL_DATA_POLLING_INTERVAL=10
   ```
3. Use Rust server for queries
4. Check RPC endpoint latency

---

## Next Steps

1. **Test Real Data Pipeline**: Run end-to-end tests with live DEX data
2. **Benchmark Rust Server**: Measure performance improvements
3. **Validate ML Models**: Test model predictions against real outcomes
4. **Production Deployment**: Deploy to Oracle Cloud with monitoring

---

## Support

For issues or questions:
- Check logs: `tail -f logs/titan.log`
- Review configuration: Ensure all environment variables are set
- Test individual components before full integration
- Consult main README.md for system architecture

---

**Last Updated**: January 2026
**Version**: 2.0.0
