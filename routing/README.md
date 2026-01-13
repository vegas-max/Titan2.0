# Routing Layer

## Overview

The `routing` directory contains Python modules for cross-chain bridge integration and route optimization. This layer enables Titan to execute arbitrage opportunities across different blockchain networks.

## Purpose

This routing layer provides:
- **Bridge aggregation** via Li.Fi and other protocols
- **Cross-chain route optimization** for asset transfers
- **Fee calculation** for bridge transactions
- **Bridge selection** based on cost and speed

## Project Structure

```
routing/
├── __init__.py              # Package initialization
├── bridge_aggregator.py     # Li.Fi API wrapper (BridgeAggregator class)
├── bridge_manager.py        # Bridge management and selection
├── lifi_wrapper.py          # Li.Fi SDK wrapper utilities
└── README.md               # This file
```

## Components

### bridge_aggregator.py

Main bridge aggregation interface using Li.Fi API:
- Query available bridge routes
- Get price quotes for cross-chain transfers
- Calculate bridge fees
- Estimate transfer times

**Key Class: BridgeAggregator**
```python
from routing.bridge_aggregator import BridgeAggregator

aggregator = BridgeAggregator()
routes = aggregator.get_routes(
    from_chain=137,    # Polygon
    to_chain=42161,    # Arbitrum
    token='USDC',
    amount=1000
)
```

### bridge_manager.py

High-level bridge management:
- Select optimal bridge for a transfer
- Manage bridge provider configurations
- Handle bridge-specific logic
- Coordinate with execution layer

### lifi_wrapper.py

Utility functions for Li.Fi integration:
- SDK initialization
- Response parsing
- Error handling
- Cache management

## Setup and Installation

### Prerequisites

- Python 3.11+
- Access to Li.Fi API (free tier available)

### Install Dependencies

```bash
pip install -r requirements.txt
```

Key dependencies:
- `requests` - HTTP client for API calls
- `web3` - Ethereum interaction
- `python-dotenv` - Environment configuration

## Usage

### Basic Bridge Query

```python
from routing.bridge_aggregator import BridgeAggregator

# Initialize aggregator
aggregator = BridgeAggregator()

# Get available routes
routes = aggregator.get_routes(
    from_chain_id=137,      # Polygon
    to_chain_id=42161,      # Arbitrum  
    from_token='0x...',     # Token address
    to_token='0x...',       # Token address
    amount=1000000000       # Amount in wei
)

# Select best route
best_route = aggregator.select_best_route(routes)

print(f"Bridge: {best_route['bridge']}")
print(f"Fee: ${best_route['fee_usd']}")
print(f"Time: {best_route['estimate_time']}s")
```

### Bridge Manager

```python
from routing.bridge_manager import BridgeManager

manager = BridgeManager()

# Execute cross-chain transfer
result = manager.bridge_asset(
    from_chain=137,
    to_chain=42161,
    token='USDC',
    amount=1000,
    recipient='0x...'
)

if result['success']:
    print(f"Bridge TX: {result['tx_hash']}")
```

### Using with Titan Brain

The routing layer integrates with the Titan Brain for cross-chain arbitrage:

```python
# In offchain/ml/brain.py
from routing.bridge_aggregator import BridgeAggregator

# Add cross-chain edges to graph
bridge = BridgeAggregator()
for token in bridge_assets:
    routes = bridge.get_routes(chain_a, chain_b, token)
    graph.add_edge(node_a, node_b, weight=routes[0]['fee'])
```

## Supported Bridges

The routing layer aggregates 15+ bridge protocols via Li.Fi:

- **Stargate** - Fast and secure
- **Across** - Optimistic bridge
- **Hop** - Rollup-native bridge
- **Connext** - Trust-minimized
- **Celer cBridge** - Fast transfers
- **Hyphen** - Low-cost bridge
- **Multichain** - Wide network coverage
- **Synapse** - Cross-chain swaps
- **deBridge** - Secure messaging
- **Wormhole** - Multi-chain support
- And more...

## Configuration

### Environment Variables

Configure in `.env`:
```env
LIFI_API_KEY=your_api_key_here  # Optional, free tier works without key
LIFI_API_URL=https://li.quest/v1
```

### Bridge Selection Criteria

Bridges are ranked based on:
1. **Cost** - Total fees (bridge + gas)
2. **Speed** - Estimated transfer time
3. **Reliability** - Historical success rate
4. **Liquidity** - Available for transfer amount

## API Reference

### BridgeAggregator

#### get_routes(from_chain_id, to_chain_id, from_token, to_token, amount)
Returns list of available bridge routes.

**Parameters:**
- `from_chain_id` (int): Source chain ID
- `to_chain_id` (int): Destination chain ID
- `from_token` (str): Source token address
- `to_token` (str): Destination token address
- `amount` (int): Amount in smallest unit (wei)

**Returns:**
- List of route objects with fees, estimates, and bridge details

#### select_best_route(routes, criteria='cost')
Selects optimal route from available options.

**Parameters:**
- `routes` (list): List of routes from get_routes()
- `criteria` (str): Selection criteria ('cost', 'speed', 'reliability')

**Returns:**
- Single route object

#### calculate_bridge_fee(route)
Calculates total bridge fee in USD.

**Parameters:**
- `route` (dict): Route object

**Returns:**
- Float representing fee in USD

### BridgeManager

#### bridge_asset(from_chain, to_chain, token, amount, recipient)
Executes cross-chain bridge transfer.

**Parameters:**
- `from_chain` (int): Source chain ID
- `to_chain` (int): Destination chain ID
- `token` (str): Token symbol or address
- `amount` (float): Amount to bridge
- `recipient` (str): Destination address

**Returns:**
- Dict with `success`, `tx_hash`, and `details`

## Testing

```bash
# Test bridge aggregator
python -m pytest tests/test_bridge_aggregator.py

# Test Li.Fi integration
python offchain/tests/test_lifi_integration.py
```

## Performance

### Caching
Bridge routes are cached for 5 minutes to reduce API calls:
- Reduces latency from 2-4s to <5ms
- Stays within free tier limits
- Automatically refreshes when stale

### Rate Limiting
The aggregator respects Li.Fi API rate limits:
- Free tier: 30 requests/minute
- Automatic retry with exponential backoff
- Request queuing for high volume

## Cross-Chain Arbitrage Flow

```
1. Brain detects price difference across chains
   ├─> Query bridge routes (BridgeAggregator)
   └─> Calculate total cost including bridge fees

2. Select optimal bridge route
   ├─> Compare fees, speed, reliability
   └─> Verify sufficient liquidity

3. Execute arbitrage
   ├─> Buy on source chain
   ├─> Bridge to destination chain
   └─> Sell on destination chain

4. Calculate profit
   └─> Revenue - Costs (gas + bridge + flash loan)
```

## Limitations

- **Bridge Time**: Most bridges take 5-30 minutes
- **Price Risk**: Asset price may change during bridge
- **Fees**: Bridge fees typically $5-50
- **Liquidity**: Limited by bridge pool TVL

## Best Practices

1. **Always simulate** bridge transactions before execution
2. **Check liquidity** on destination chain before bridging
3. **Monitor** bridge transaction status
4. **Use reputable bridges** with proven track record
5. **Account for time** in profit calculations

## Further Documentation Needed

- [ ] Detailed integration guide for each supported bridge
- [ ] Custom bridge provider addition instructions  
- [ ] Bridge failure recovery strategies
- [ ] Historical performance data for bridge selection
- [ ] Advanced routing algorithms documentation
- [ ] Gas optimization techniques for bridge transactions

## Troubleshooting

### API Rate Limit Exceeded
- Use caching to reduce API calls
- Implement request queuing
- Consider Li.Fi premium tier

### Route Not Found
- Check token is supported on both chains
- Verify sufficient bridge liquidity
- Try alternative token pairs

### High Bridge Fees
- Compare multiple routes
- Consider waiting for lower network congestion
- Use alternative bridges or chains

## Contributing

When adding new bridge integrations:
1. Add wrapper in appropriate file
2. Update supported bridges list
3. Add tests for new integration
4. Document configuration requirements
5. Update this README

## License

This module is part of the Titan 2.0 project and follows the same MIT License.

## Support

For routing layer issues:
- API errors: Check Li.Fi status
- Integration issues: Verify configuration
- Performance: Enable caching and request batching

See main README.md for general support information.
