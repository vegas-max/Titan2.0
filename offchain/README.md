# Off-Chain System Components

This directory contains all off-chain bot logic, AI intelligence, and execution infrastructure that runs on traditional computing infrastructure (not blockchain).

## Structure

```
offchain/
├── core/                # Core Python infrastructure
│   ├── config.py               # Central configuration management
│   ├── enum_matrix.py          # Chain ID enumeration & providers
│   ├── token_discovery.py      # Multi-chain token inventory
│   ├── token_loader.py         # Dynamic token list loading
│   ├── titan_commander_core.py # Master control system (TitanCommander)
│   └── titan_simulation_engine.py # On-chain simulation & TVL checking
├── execution/           # Node.js execution layer
│   ├── bot.js                  # Main execution coordinator (TitanBot)
│   ├── gas_manager.js          # EIP-1559 gas optimization
│   ├── lifi_manager.js         # Li.Fi bridge integration
│   ├── lifi_discovery.js       # Dynamic DEX router discovery
│   ├── omniarb_sdk_engine.js   # Transaction simulation engine
│   ├── bloxroute_manager.js    # MEV protection
│   ├── aggregator_selector.js  # Intelligent aggregator routing
│   ├── oneinch_manager.js      # 1inch integration
│   ├── paraswap_manager.js     # ParaSwap integration
│   ├── zerox_manager.js        # 0x protocol integration
│   ├── cowswap_manager.js      # CoW Swap integration
│   ├── kyberswap_manager.js    # KyberSwap integration
│   ├── openocean_manager.js    # OpenOcean integration
│   ├── rango_manager.js        # Rango Exchange integration
│   ├── jupiter_manager.js      # Jupiter (Solana) integration
│   ├── merkle_builder.js       # Merkle proof generation
│   ├── order_splitter.js       # Order splitting logic
│   ├── mev_strategies.js       # MEV protection strategies
│   └── nonce_manager.py        # Transaction nonce management
├── ml/                  # Machine learning & AI strategies
│   ├── brain.py                # Central AI coordinator (OmniBrain)
│   ├── dex_pricer.py           # Multi-DEX price querying
│   ├── bridge_oracle.py        # Cross-chain price oracle
│   ├── cortex/                 # AI models
│   │   ├── forecaster.py       # Gas price prediction (MarketForecaster)
│   │   ├── rl_optimizer.py     # Reinforcement learning (QLearningAgent)
│   │   └── feature_store.py    # Historical data aggregation
│   └── strategies/             # Trading strategies
│       └── instant_scalper.py  # High-frequency arbitrage strategy
├── routing/             # Cross-chain routing logic
│   ├── bridge_aggregator.py    # Li.Fi API wrapper (BridgeAggregator)
│   ├── bridge_manager.py       # Bridge management
│   └── lifi_wrapper.py         # Li.Fi wrapper utilities
├── monitoring/          # Real-time monitoring
│   ├── MempoolHound.ts         # Mempool monitoring
│   └── decoderWorker.js        # Transaction decoder worker
└── tests/               # Integration tests
    ├── test_lifi_integration.py     # Li.Fi integration tests
    ├── test_aggregator_selector.js  # Aggregator routing tests
    └── test_route_encoding.js       # Route encoding tests
```

## Components

### Core Layer (Python)

**Purpose**: Infrastructure and configuration management

- `config.py` - Central configuration with chain definitions, RPC endpoints, contract addresses
- `enum_matrix.py` - Chain ID enumeration and provider management
- `token_discovery.py` - Multi-chain token inventory and bridge asset detection
- `titan_commander_core.py` - TitanCommander class with loan optimization and TVL checking
- `titan_simulation_engine.py` - On-chain balance queries and liquidity verification

### Execution Layer (Node.js)

**Purpose**: High-performance trade execution and blockchain interaction

- `bot.js` - TitanBot main coordinator that subscribes to Redis and executes trades
- `gas_manager.js` - EIP-1559 gas fee optimization and network congestion detection
- `omniarb_sdk_engine.js` - OmniSDKEngine for transaction simulation via eth_call
- `aggregator_selector.js` - Intelligent routing across 9 DEX aggregators
- `bloxroute_manager.js` - Private mempool submission for MEV protection
- Various aggregator managers - Integrations with 1inch, ParaSwap, 0x, CoW Swap, etc.

### ML Layer (Python)

**Purpose**: AI-powered opportunity detection and profit optimization

- `brain.py` - OmniBrain with hyper-graph analysis, multi-threaded scanning, Redis broadcasting
- `dex_pricer.py` - DexPricer for multi-DEX price discovery (Uniswap V3, Curve, etc.)
- `bridge_oracle.py` - Cross-chain price oracle and bridge fee estimation
- `cortex/forecaster.py` - MarketForecaster with gas price trend prediction
- `cortex/rl_optimizer.py` - QLearningAgent for parameter tuning
- `cortex/feature_store.py` - Historical data aggregation for pattern recognition
- `strategies/instant_scalper.py` - InstantScalper for high-frequency arbitrage

### Routing Layer (Python)

**Purpose**: Cross-chain bridge integration and route optimization

- `bridge_aggregator.py` - BridgeAggregator wrapping Li.Fi API
- `bridge_manager.py` - Bridge management and selection
- `lifi_wrapper.py` - Li.Fi SDK wrapper utilities

### Monitoring Layer (TypeScript/JavaScript)

**Purpose**: Real-time blockchain monitoring

- `MempoolHound.ts` - Mempool monitoring for frontrunning detection
- `decoderWorker.js` - Transaction decoding worker for ABI parsing

## Running the System

### Start the Brain (AI Engine)

```bash
npm run brain
# or
python3 offchain/ml/brain.py
```

Expected output:
```
🧠 Booting Apex-Omega Titan Brain...
🕸️  Constructing Hyper-Graph Nodes...
🌉 Building Virtual Bridge Edges...
✅ System Online. Tracking 256 nodes.
```

### Start the Executor (Trading Bot)

```bash
npm start
# or
node offchain/execution/bot.js
```

Expected output:
```
🤖 Titan Bot Online.
Subscribed to: trade_signals
Waiting for opportunities...
```

## Data Flow

1. **Discovery Phase**: Brain scans blockchain networks for token pairs
2. **Analysis Phase**: AI models calculate expected profit and costs
3. **Signal Phase**: Profitable opportunities broadcast via Redis
4. **Validation Phase**: Bot receives signal, simulates transaction on-chain
5. **Execution Phase**: Bot signs and submits transaction
6. **Settlement Phase**: Smart contract executes trade

## Configuration

All configuration is in `offchain/core/config.py`:
- Chain definitions with RPC endpoints
- Contract addresses (Aave pools, DEX routers)
- Token lists and metadata
- Environment variable loading

## Dependencies

### Python Requirements
```bash
pip install -r requirements.txt
```

Key packages:
- web3 - Blockchain interaction
- pandas, numpy - Data processing
- rustworkx - Graph algorithms
- redis - Message queue
- eth-abi - ABI encoding/decoding

### Node.js Requirements
```bash
npm install
```

Key packages:
- ethers.js - Blockchain library
- @lifi/sdk - Bridge aggregation
- @flashbots/ethers-provider-bundle - MEV protection
- redis - Message queue client

## Testing

Run integration tests:
```bash
# Python tests
python3 offchain/tests/test_lifi_integration.py

# JavaScript tests
node offchain/tests/test_aggregator_selector.js
```

## Monitoring

Console logging shows system activity:
```
💰 PROFIT FOUND: USDC | Net: $7.23
⚡ SIGNAL BROADCASTED TO REDIS
🧪 Running Full System Simulation...
✅ Simulation SUCCESS. Estimated Gas: 285000
🚀 TX: 0x5678... | Profit: $7.23
```

## Architecture

The off-chain system follows an event-driven architecture:

1. **Intelligence Layer** (Python) - Detects opportunities using graph theory and ML
2. **Message Queue** (Redis) - Publishes trade signals
3. **Execution Layer** (Node.js) - Subscribes to signals and executes trades
4. **Blockchain Layer** - Smart contracts execute atomic flash loan arbitrage

## Performance Optimization

- **Multi-threading**: 20 concurrent opportunity evaluations
- **Connection pooling**: Redis and HTTP connection reuse
- **Caching**: Token metadata and DEX route caching
- **WebSocket streaming**: Real-time block updates
- **Batch RPC calls**: Parallel gas price and balance queries

## Security

- Transaction simulation before execution (eth_call)
- Slippage protection with dynamic tolerance
- Gas limit buffers to prevent out-of-gas
- Nonce management to prevent conflicts
- Private mempool submission via BloxRoute
