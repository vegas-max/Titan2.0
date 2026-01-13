# Execution Layer

## Overview

The `execution` directory contains standalone arbitrage engine implementations that can run independently from the main Titan system. These components provide alternative execution strategies and integration patterns.

## Purpose

This directory provides:
- **Standalone arbitrage engines** that can operate independently
- **Integration examples** showing how to use the arbitrage logic
- **Alternative execution patterns** for specific use cases

## Project Structure

```
execution/
├── arbitrage_engine.js                        # Standalone arbitrage engine
├── arbitrage_engine_integration_example.js    # Integration usage example
└── README.md                                  # This file
```

## Components

### arbitrage_engine.js

A standalone JavaScript arbitrage engine that can:
- Detect arbitrage opportunities
- Calculate profit potential
- Execute trades via flash loans
- Operate independently of the main Titan system

**Features:**
- Self-contained execution logic
- Configurable parameters
- Independent RPC connections
- Direct blockchain interaction

### arbitrage_engine_integration_example.js

Example code showing how to integrate and use the arbitrage engine:
- Configuration examples
- Usage patterns
- Integration with external systems
- Event handling

## Setup and Installation

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Environment variables configured (see `.env.example`)

### Install Dependencies

From the repository root:
```bash
npm install
```

Or using yarn:
```bash
yarn install
```

## Running the Arbitrage Engine

### Standalone Mode

```bash
node execution/arbitrage_engine.js
```

### With Custom Configuration

```javascript
const ArbitrageEngine = require('./execution/arbitrage_engine');

const engine = new ArbitrageEngine({
    rpcUrl: process.env.RPC_POLYGON,
    privateKey: process.env.PRIVATE_KEY,
    minProfit: 5.0,
    gasLimit: 500000
});

await engine.start();
```

### Integration Example

```bash
node execution/arbitrage_engine_integration_example.js
```

## Configuration

The arbitrage engine accepts various configuration options:

```javascript
{
    rpcUrl: 'https://polygon-rpc.com',           // RPC endpoint
    privateKey: '0x...',                         // Wallet private key
    minProfit: 5.0,                              // Minimum profit threshold (USD)
    maxGasPrice: 500,                            // Maximum gas price (gwei)
    flashLoanProvider: 'balancer',               // Flash loan provider
    dexes: ['uniswap', 'sushiswap', 'curve'],   // DEX list to scan
    scanInterval: 3000,                          // Scan interval (ms)
    enableSimulation: true                       // Pre-execution simulation
}
```

## Key Features

### Independent Operation
- Runs without the main Brain/Bot architecture
- Self-contained scanning and execution
- Direct blockchain interaction

### Flexible Integration
- Can be embedded in other applications
- Event-driven architecture
- Customizable callbacks

### Safety Features
- Transaction simulation before execution
- Gas price limits
- Profit threshold validation
- Slippage protection

## API

### Class: ArbitrageEngine

#### Constructor
```javascript
new ArbitrageEngine(config)
```

#### Methods

**start()**
```javascript
await engine.start();
```
Starts the arbitrage engine and begins scanning for opportunities.

**stop()**
```javascript
await engine.stop();
```
Stops the engine gracefully.

**setMinProfit(amount)**
```javascript
engine.setMinProfit(10.0);
```
Updates the minimum profit threshold.

**getStatistics()**
```javascript
const stats = engine.getStatistics();
// Returns: { scans: 1000, opportunities: 45, executions: 12, profit: 156.78 }
```

## Events

The engine emits various events:

```javascript
engine.on('opportunity', (opp) => {
    console.log('Opportunity found:', opp);
});

engine.on('execution', (result) => {
    console.log('Trade executed:', result);
});

engine.on('error', (error) => {
    console.error('Error occurred:', error);
});
```

## Testing

The `test/` directory contains test files for the arbitrage engine:

```bash
# Run arbitrage engine tests
node test/arbitrage_engine_standalone_test.js
node test/test_flash_loan_enforcement.js
```

## Performance

The standalone engine is optimized for:
- Low latency opportunity detection
- Efficient gas usage
- Minimal RPC calls
- Fast execution

## Use Cases

### 1. Standalone Trading Bot
Run the engine as an independent trading bot without the full Titan system.

### 2. Custom Integration
Integrate arbitrage logic into existing applications or services.

### 3. Research and Testing
Test arbitrage strategies and algorithms independently.

### 4. Lightweight Deployment
Deploy a minimal arbitrage system with reduced complexity.

## Comparison with Main Titan System

| Feature | Standalone Engine | Main Titan System |
|---------|------------------|-------------------|
| AI/ML Integration | No | Yes |
| Multi-threading | Limited | Yes (20 workers) |
| Graph Analysis | No | Yes (rustworkx) |
| Cross-chain | Basic | Advanced |
| Complexity | Low | High |
| Setup Time | Minutes | Hours |
| Resource Usage | Low | Medium-High |

## Further Documentation Needed

- [ ] Detailed API documentation for all methods
- [ ] Performance benchmarks vs. main system
- [ ] Advanced configuration scenarios
- [ ] Custom DEX integration guide
- [ ] Production deployment best practices
- [ ] Monitoring and alerting setup

## Troubleshooting

### Engine won't start
- Check RPC URL is accessible
- Verify private key is valid
- Ensure .env file is configured

### No opportunities found
- Check gas prices aren't too high
- Verify DEX contracts are correct
- Lower `minProfit` threshold for testing

### Transactions failing
- Enable simulation mode
- Check wallet has sufficient gas funds
- Verify contract addresses are correct

## Contributing

When modifying the arbitrage engine:
1. Test changes thoroughly on testnet
2. Maintain backward compatibility
3. Update integration examples
4. Document new configuration options
5. Add tests for new features

## License

This module is part of the Titan 2.0 project and follows the same MIT License.

## Support

For issues with the execution layer:
- Check Node.js version compatibility
- Review console error messages
- Enable debug logging
- Test on testnet first

See main README.md for general support information.
