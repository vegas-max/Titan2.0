# Chainlink Oracle Feeds Integration

## Overview

The `chainlink_oracle_feeds` module provides comprehensive on-chain and off-chain price data integration for the Titan 2.0 arbitrage system. It implements a multi-tier fallback mechanism to ensure reliable token pricing across all supported chains.

## Features

### Multi-Tier Price Fallback
1. **Chainlink (On-chain)** - Most reliable, direct from blockchain
2. **Coingecko (Off-chain)** - REST API fallback
3. **Binance (Off-chain)** - Final fallback option

### Supported Chains
- **Ethereum** (7 feeds: ETH, USDC, USDT, DAI, WBTC, LINK, AAVE)
- **Polygon** (8 feeds: ETH, USDC, USDT, DAI, WBTC, MATIC, LINK, AAVE)
- **Arbitrum** (6 feeds: ETH, USDC, USDT, WBTC, DAI, LINK)
- **Optimism** (6 feeds: ETH, USDC, USDT, WBTC, DAI, LINK)
- **Base** (2 feeds: ETH, USDC)
- **BSC** (6 feeds: BNB, BUSD, USDC, USDT, ETH, WBTC)
- **Avalanche** (5 feeds: AVAX, USDC, USDT, ETH, WBTC)
- **Fantom** (2 feeds: FTM, USDC)

## Usage

### Basic Price Fetching

```python
from offchain.core import chainlink_oracle_feeds

# Get price using chain name
price = chainlink_oracle_feeds.get_price_usd("ETH", "ethereum")
print(f"ETH price: ${price:.2f}")

# Get price using chain ID
price = chainlink_oracle_feeds.get_price_usd_by_chain_id("USDC", 137)  # Polygon
print(f"USDC price: ${price:.2f}")
```

### Check Feed Availability

```python
# Check if a Chainlink feed is available
if chainlink_oracle_feeds.is_chainlink_feed_available("ETH", "polygon"):
    print("Chainlink feed available for ETH on Polygon")

# Get all available feeds for a chain
feeds = chainlink_oracle_feeds.get_available_feeds("ethereum")
for token, address in feeds.items():
    print(f"{token}: {address}")
```

### Integration with DynamicPriceOracle

The module is automatically integrated with the existing `DynamicPriceOracle` class:

```python
from offchain.core.dynamic_price_oracle import DynamicPriceOracle
from web3 import Web3

# Initialize oracle with web3 connections
web3_connections = {
    1: Web3(Web3.HTTPProvider(ethereum_rpc)),
    137: Web3(Web3.HTTPProvider(polygon_rpc)),
}

oracle = DynamicPriceOracle(web3_connections)

# Get price with enhanced fallback
price = oracle.get_price_with_enhanced_fallback(chain_id=1, token_symbol="ETH")
print(f"ETH price: ${price}")
```

### Direct Chainlink Price Fetching

```python
# Fetch directly from Chainlink (on-chain)
try:
    price = chainlink_oracle_feeds.chainlink_price_usd("ETH", "ethereum")
    print(f"Chainlink price: ${price:.2f}")
except Exception as e:
    print(f"Chainlink fetch failed: {e}")
```

### Off-chain Price Fetching

```python
# Fetch from Coingecko/Binance (off-chain)
price = chainlink_oracle_feeds.get_offchain_price("ETH")
print(f"Off-chain price: ${price:.2f}")
```

## Environment Configuration

### Required RPC Endpoints

The module uses the following environment variables for RPC connections:

```bash
# Polygon
POLYGON_RPC=https://polygon-mainnet.infura.io/v3/YOUR_KEY
# or
RPC_POLYGON=https://polygon-mainnet.infura.io/v3/YOUR_KEY

# Ethereum
ALCHEMY_RPC_ETH=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
# or
RPC_ETHEREUM=https://mainnet.infura.io/v3/YOUR_KEY

# Arbitrum
ALCHEMY_RPC_ARB=https://arb-mainnet.g.alchemy.com/v2/YOUR_KEY
# or
RPC_ARBITRUM=https://arbitrum-mainnet.infura.io/v3/YOUR_KEY

# Optimism
ALCHEMY_RPC_OPT=https://opt-mainnet.g.alchemy.com/v2/YOUR_KEY
# or
RPC_OPTIMISM=https://optimism-mainnet.infura.io/v3/YOUR_KEY

# Base
ALCHEMY_RPC_BASE=https://base-mainnet.g.alchemy.com/v2/YOUR_KEY
# or
RPC_BASE=https://base-mainnet.g.alchemy.com/v2/YOUR_KEY

# BSC
RPC_BSC=https://bsc-dataseed.binance.org

# Avalanche
RPC_AVALANCHE=https://api.avax.network/ext/bc/C/rpc

# Fantom
RPC_FANTOM=https://rpc.ftm.tools
```

### Optional API Keys

For enhanced off-chain price fetching:

```bash
# CoinGecko API Key (optional, but recommended for rate limits)
COINGECKO_API_KEY=your_coingecko_api_key
```

## Architecture Integration

### Integration Points

1. **DynamicPriceOracle** - Enhanced with automatic fallback to `chainlink_oracle_feeds`
2. **BridgeOracle** - Can leverage enhanced price feeds for cross-chain arbitrage
3. **TitanCommander** - Can use for real-time price validation

### Key Design Decisions

- **Stateless Design**: No persistent state, all data fetched fresh or from short-term cache
- **Graceful Fallbacks**: Never fails completely, always tries all available sources
- **Comprehensive Coverage**: 42 Chainlink feeds across 8 chains
- **Easy Extension**: Simple to add new chains or feeds

## Testing

Run the integration tests:

```bash
python test_chainlink_oracle_integration.py
```

Expected output:
```
✓ All tests passed!
Total: 5/5 tests passed
```

## Error Handling

The module implements comprehensive error handling:

```python
# Chainlink not available → Try Coingecko
# Coingecko fails → Try Binance
# All fail → Return 0.0 with warning

price = chainlink_oracle_feeds.get_price_usd("UNKNOWN_TOKEN", "ethereum")
# Returns: 0.0 with warning logged
```

## Performance Considerations

- **Chainlink**: ~200-500ms per call (on-chain RPC call)
- **Coingecko**: ~50-200ms per call (REST API)
- **Binance**: ~50-150ms per call (REST API)

Cache prices when possible using `DynamicPriceOracle`'s built-in caching (10 second TTL).

## Future Enhancements

Potential improvements for future iterations:

1. Add more Chainlink feeds as they become available
2. Implement connection pooling for RPC calls
3. Add Redis-based distributed caching
4. Support for additional DEX TWAP oracles
5. Weighted average from multiple sources
6. Real-time price volatility detection

## Support

For issues or questions:
1. Check the test file: `test_chainlink_oracle_integration.py`
2. Review module source: `offchain/core/chainlink_oracle_feeds.py`
3. Consult Chainlink docs: https://docs.chain.link/data-feeds/price-feeds/addresses
