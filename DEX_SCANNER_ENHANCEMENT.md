# DEX Scanner Enhancement - Integration Guide

## Overview

This enhancement expands the DEX scanner module with institutional-grade features for token pair management, multi-protocol routing, and TWAP-based price validation. All changes are **additive** - existing functionality remains intact.

## New Features

### 1. Token Universe (`tokenUniverse.ts`)

**Purpose**: Canonical source of truth for token addresses and trading pairs across all supported chains.

**Key Functions**:
- `getTokenAddress(chainId, symbol)` - Get token address by symbol
- `getAvailablePairs(chainId)` - Get all tradable pairs for a chain
- `getTokenSymbol(chainId, address)` - Reverse lookup: address → symbol
- `isPairSupported(chainId, tokenA, tokenB)` - Check if pair is supported
- `getChainTokens(chainId)` - Get all tokens for a chain

**Supported Chains**: Ethereum (1), Polygon (137), Arbitrum (42161)

**Supported Tokens**: WMATIC, WETH, USDC, USDT, DAI, WBTC, LINK, AAVE, UNI

**Trading Pairs**: 18 pre-configured pairs optimized for arbitrage, including:
- Major pairs (WETH/USDC, WETH/USDT, WETH/DAI)
- Native pairs (WMATIC/USDC, WMATIC/WETH)
- Stablecoin triangles (USDC/USDT, USDC/DAI, USDT/DAI)
- Blue-chip DeFi tokens (LINK, AAVE, UNI)

**Usage Example**:
```typescript
import { getAvailablePairs, getTokenSymbol } from './offchain/core/tokenUniverse';

// Get all pairs for Polygon
const pairs = getAvailablePairs(137);

// Look up token symbol
const symbol = getTokenSymbol(137, '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270');
// Returns: "WMATIC"
```

### 2. TWAP Accumulator (`twapAccumulator.ts`)

**Purpose**: Time-weighted average price tracking for institutional-grade validation. Filters spoofed liquidity, avoids MEV bait pools, and enables larger trade sizes safely.

**Features**:
- Lightweight sampling (automatic pruning)
- Time-weighted calculation (not simple average)
- Volatility metrics
- Deviation detection
- Multi-pool tracking

**Key Classes**:
- `TWAPAccumulator` - Single pool TWAP tracking
- `MultiPoolTWAP` - Manage multiple token pairs

**Usage Example**:
```typescript
import { TWAPAccumulator } from './offchain/core/twapAccumulator';

// Initialize with 30-second window
const twap = new TWAPAccumulator({ windowMs: 30000 });

// On each Sync/Swap event
twap.push(calculatePriceFromReserves(reserve0, reserve1));

// Get TWAP value
const avgPrice = twap.value();

// Check if price is within bounds
if (twap.isWithinBounds(spotPrice, 0.05)) {
  // Spot price is within 5% of TWAP - safe to trade
}
```

**Benefits**:
- Filters manipulated prices
- Reduces revert rate
- Enables higher trade sizes
- Improves win percentage → higher daily EV

### 3. Curve Multi-Coin Quoter (`curveQuoter.ts`)

**Purpose**: Dynamic Curve pair discovery with underlying token support. Enables stablecoin loops (USDC ⇄ USDT ⇄ DAI) with deep liquidity.

**Key Functions**:
- `curveQuoteByTokens()` - Quote by token addresses (auto-discovers indices)
- `discoverCurveIndices()` - Find token indices in pool
- `getCurvePoolCoins()` - List all tokens in pool
- `isCurvePairSupported()` - Check if pair is in pool

**Improvements**:
- Automatic index discovery (no manual mapping needed)
- Tries `get_dy_underlying` first (better for stablecoin pools)
- Falls back to `get_dy` automatically
- Supports up to 8 coins per pool

**Usage Example**:
```typescript
import { curveQuoteByTokens } from './offchain/core/curveQuoter';

const output = await curveQuoteByTokens(
  CURVE_POOL_ADDRESS,
  provider,
  ethers.parseUnits('1000', 6), // 1000 USDC
  USDC_ADDRESS,
  USDT_ADDRESS
);
// Returns expected USDT output
```

**Python Enhancement** (`dex_pricer.py`):
- Added `get_dy_underlying` to Curve ABI
- Automatic fallback from underlying to regular get_dy
- Improved error handling

### 4. Balancer Multi-Hop Router (`balancerRouter.ts`)

**Purpose**: Generalized multi-leg routing support for complex arbitrage paths.

**Key Functions**:
- `buildBalancerLegs()` - Build swap legs for single-pool routing
- `buildMultiPoolBalancerLegs()` - Build legs across multiple pools
- `queryBatchSwap()` - Simulate swap without execution
- `quoteBalancerMultiHop()` - High-level quote function
- `isBalancerRouteProfitable()` - Validate profitability

**Capabilities**:
- Multi-hop paths (e.g., WMATIC → WETH → USDC)
- Stable basket routing
- Pre-execution simulation (zero execution risk)
- Single-pool and multi-pool support

**Usage Example**:
```typescript
import { quoteBalancerMultiHop } from './offchain/core/balancerRouter';

// Quote: WMATIC -> WETH -> USDC
const output = await quoteBalancerMultiHop(
  BALANCER_VAULT,
  provider,
  poolId,
  [WMATIC, WETH, USDC],
  [0, 1, 2],
  ethers.parseEther('100')
);
```

### 5. DEX TWAP Oracle (`dex_twap_oracle.py`)

**Purpose**: Python adapter for TWAP-fed DEX prices with Chainlink fallback. Zero disruption to existing oracle layer.

**Key Functions**:
- `onchain_dex_price(tokenA, tokenB, chain)` - Get price with TWAP preference
- `set_dex_twap_price()` - Store TWAP price
- `get_dex_twap_price()` - Retrieve TWAP price
- `clear_twap_cache()` - Clear cache
- `get_all_twap_pairs()` - Get all tracked pairs

**Priority Order**:
1. TWAP-fed DEX price (if available) ← **Preferred**
2. Chainlink oracle (fallback)

**Usage Example**:
```python
from offchain.core.dex_twap_oracle import onchain_dex_price

# Get price (tries TWAP first, falls back to Chainlink)
price = onchain_dex_price(WETH, USDC, 137)
if price:
    print(f"WETH/USDC: ${price}")
```

## Integration with Existing System

### Brain Integration

The Brain (`offchain/ml/brain.py`) can now leverage these features:

```python
# In scan_loop():
from offchain.core.dex_twap_oracle import onchain_dex_price

# Get validated price
price = onchain_dex_price(token_in, token_out, chain_id)
```

### DexPricer Enhancement

The `DexPricer` class now supports:
- `get_curve_price()` with automatic `get_dy_underlying` fallback
- Token address-based Curve queries (no manual index mapping)

```python
from offchain.ml.dex_pricer import DexPricer

pricer = DexPricer(w3, chain_id)

# New: Query by token addresses
output = pricer.get_curve_price(
    pool_address,
    token_in=USDC,
    token_out=USDT,
    amount=1000_000000
)
```

## Testing

### Run JavaScript Tests

```bash
# Token Universe tests
node offchain/tests/test_token_universe.js

# TWAP Accumulator tests
node offchain/tests/test_twap_accumulator.js

# Integration example
node offchain/tests/integration_example.js
```

### Run Python Tests

```bash
# DEX TWAP Oracle tests
python3 offchain/tests/test_dex_twap_oracle.py

# Or with pytest
pytest offchain/tests/test_dex_twap_oracle.py -v
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Token Universe                          │
│  (Canonical token addresses & trading pairs)                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Price Discovery Layer                     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Curve Quoter │  │   Balancer   │  │  Uniswap V2  │      │
│  │ Multi-coin   │  │  Multi-hop   │  │   /V3 / XYK  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  TWAP Accumulator                           │
│  (Time-weighted validation & MEV protection)                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Python Oracle Layer (Existing)                 │
│  DEX TWAP Oracle → Chainlink → Direct Queries               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Brain / Strategy                         │
│             (Arbitrage detection & execution)               │
└─────────────────────────────────────────────────────────────┘
```

## Performance Benefits

1. **Expanded Coverage**:
   - 18 pre-configured trading pairs
   - 9 tokens across 3 chains
   - Support for stablecoin loops (Curve-optimized)

2. **Better Execution**:
   - TWAP validation reduces revert rate
   - Multi-hop routing finds better prices
   - Automatic underlying token support (Curve)

3. **Institutional-Grade Validation**:
   - Time-weighted prices (not spot prices)
   - Filters manipulated pools
   - Enables larger trade sizes safely

4. **Zero Execution Risk**:
   - Balancer `queryBatchSwap` validates before execution
   - TWAP deviation checks prevent bad trades
   - Automatic fallbacks (get_dy_underlying → get_dy)

## What This Enables

- ✅ **Stablecoin loops** (USDC ⇄ USDT ⇄ DAI) with deep liquidity
- ✅ **Multi-hop arbitrage** (WMATIC → WETH → USDC)
- ✅ **Lower slippage** on larger trade sizes
- ✅ **MEV protection** via TWAP validation
- ✅ **Better profit margins** with optimized routing
- ✅ **Reduced revert rate** with pre-execution validation

## Breaking Changes

**None.** All changes are additive. Existing functionality remains intact.

## Migration Path

1. **Phase 1** (Current): New modules available, existing system unchanged
2. **Phase 2**: Gradually integrate TWAP tracking in event listeners
3. **Phase 3**: Update Brain to prefer TWAP-validated prices
4. **Phase 4**: Enable Balancer multi-hop routing in strategy

## Future Enhancements

- [ ] Event listener integration (Sync/Swap events → TWAP)
- [ ] Redis backend for TWAP cache (production)
- [ ] Automated pool discovery (Curve/Balancer)
- [ ] Cross-DEX arbitrage optimization
- [ ] Historical TWAP analytics

## Support

For questions or issues:
1. Check existing tests for usage examples
2. Run integration example: `node offchain/tests/integration_example.js`
3. Review inline documentation in source files

## License

MIT
