# DEX Integration Index
## Comprehensive DEX Registry for Titan2.0 Arbitrage System

**Version:** 1.0  
**Date:** January 5, 2026  
**Purpose:** Complete index of DEX integrations, APIs, and market coverage

---

## Overview

This document provides the comprehensive DEX integration index for the Titan2.0 arbitrage system, including API endpoints, market coverage assessment, integration status, and optimal swapping strategies.

---

## 1. Uniswap

### Protocol Information
- **Versions:** V2, V3
- **Chains:** Ethereum, Polygon, Arbitrum, Optimism, BSC
- **Market Coverage:** ⭐⭐⭐⭐⭐ **High** (Industry leader)
- **Integration Status:** ✅ **Fully Integrated**

### API Endpoints

#### Uniswap V2
```
GraphQL Subgraph: https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2
REST API: https://api.uniswap.org/v2/
```

#### Uniswap V3 (Polygon)
```
GraphQL Subgraph: https://api.thegraph.com/subgraphs/name/ianlapham/uniswap-v3-polygon
Router: 0xE592427A0AEce92De3Edee1F18E0157C05861564
Quoter: 0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6
```

### Integration Code
```python
# Uniswap V2 Integration
UNIV2_ABI = '[{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"}]'

def get_uniswap_v2_price(router_address, token_in, token_out, amount_in):
    router = w3.eth.contract(address=router_address, abi=UNIV2_ABI)
    path = [token_in, token_out]
    amounts = router.functions.getAmountsOut(amount_in, path).call()
    return amounts[-1]
```

### Fee Structure
- **V2:** 0.3% swap fee
- **V3:** 0.05%, 0.30%, or 1.00% (pool-specific)

---

## 2. SushiSwap

### Protocol Information
- **Version:** V2 (Uniswap V2 fork)
- **Chains:** Ethereum, Polygon, Arbitrum, BSC, Avalanche
- **Market Coverage:** ⭐⭐⭐⭐ **Moderate-High**
- **Integration Status:** ✅ **Fully Integrated**

### API Endpoints

#### SushiSwap (Polygon)
```
GraphQL Subgraph: https://api.thegraph.com/subgraphs/name/sushiswap/matic-exchange
WebSocket: wss://api.thegraph.com/subgraphs/name/sushiswap/matic-exchange
Router: 0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506
```

### Integration Status
- ✅ HTTP queries implemented
- ✅ WebSocket support enabled
- ✅ Price quoter integrated
- ✅ Quantum optimizer compatible

### Fee Structure
- **Swap Fee:** 0.3%
- **Protocol Fee:** 0.05% (to treasury)

---

## 3. QuickSwap

### Protocol Information
- **Version:** V2, V3
- **Chains:** Polygon (primary)
- **Market Coverage:** ⭐⭐⭐⭐ **Moderate-High** (Polygon leader)
- **Integration Status:** ✅ **Fully Integrated**

### API Endpoints

#### QuickSwap V2
```
GraphQL Subgraph: https://api.thegraph.com/subgraphs/name/sameepsi/quickswap-v3
WebSocket: wss://api.thegraph.com/subgraphs/name/sameepsi/quickswap-v3
Router V2: 0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff
Router V3: 0xf5b509bB0909a69B1c207E495f687a596C168E12
```

### Integration Features
- ✅ Real-time WebSocket price feeds
- ✅ V2 + V3 support
- ✅ Primary Polygon DEX
- ✅ High liquidity for MATIC pairs

### Fee Structure
- **V2:** 0.3% swap fee
- **V3:** Variable (0.01%, 0.05%, 0.3%, 1%)

---

## 4. Curve Finance

### Protocol Information
- **Version:** Stableswap
- **Chains:** Ethereum, Polygon, Arbitrum, Optimism, Avalanche
- **Market Coverage:** ⭐⭐⭐⭐⭐ **High** (Stablecoin leader)
- **Integration Status:** ✅ **Fully Integrated**

### API Endpoints

#### Curve (Polygon)
```
GraphQL Subgraph: https://api.thegraph.com/subgraphs/name/curvefi/curve-polygon
Direct Contract Queries: Preferred method for Curve
```

### Integration Code
```python
# Curve Pool Direct Query
CURVE_ABI = '[{"stateMutability":"view","type":"function","name":"get_dy","inputs":[{"name":"i","type":"int128"},{"name":"j","type":"int128"},{"name":"dx","type":"uint256"}],"outputs":[{"name":"","type":"uint256"}]}]'

def get_curve_price(pool_address, token_in_idx, token_out_idx, amount_in):
    pool = w3.eth.contract(address=pool_address, abi=CURVE_ABI)
    amount_out = pool.functions.get_dy(token_in_idx, token_out_idx, amount_in).call()
    return amount_out
```

### Integration Features
- ✅ Dynamic index resolution
- ✅ Support for get_dy and get_dy_underlying
- ✅ Pool coin caching
- ✅ Optimal for stablecoin swaps

### Fee Structure
- **Typical:** 0.04% swap fee
- **Pool-specific:** Varies (0.03% - 0.10%)

---

## 5. Balancer

### Protocol Information
- **Version:** V2, V3
- **Chains:** Ethereum, Polygon, Arbitrum, Optimism
- **Market Coverage:** ⭐⭐⭐⭐ **Moderate**
- **Integration Status:** ✅ **Fully Integrated**

### API Endpoints

#### Balancer V3 (Polygon)
```
GraphQL Subgraph: https://api.thegraph.com/subgraphs/name/balancer-labs/balancer-polygon-v2
Vault: 0xBA12222222228d8Ba445958a75a0704d566BF2C8
```

### Integration Features
- ✅ Flashloan provider (0% fee)
- ✅ Multi-token pools
- ✅ Weighted pools support
- ✅ Stable pools support

### Fee Structure
- **Swap Fee:** Variable per pool (0.01% - 10%)
- **Flashloan Fee:** 0% (free!)
- **Protocol Fee:** Variable

---

## 6. 1inch

### Protocol Information
- **Type:** DEX Aggregator
- **Chains:** Ethereum, Polygon, BSC, Arbitrum, Optimism, Avalanche
- **Market Coverage:** ⭐⭐⭐⭐⭐ **High** (Aggregator)
- **Integration Status:** ✅ **Fully Integrated**

### API Endpoints

#### 1inch Aggregation Protocol
```
REST API: https://api.1inch.io/v5.0/137/
Swagger: https://api.1inch.io/swagger/

Endpoints:
- /quote: Get best price quote
- /swap: Get swap transaction data
- /liquidity-sources: List available sources
```

### Integration Code
```python
import requests

def get_1inch_quote(from_token, to_token, amount):
    url = f"https://api.1inch.io/v5.0/137/quote"
    params = {
        'fromTokenAddress': from_token,
        'toTokenAddress': to_token,
        'amount': amount
    }
    response = requests.get(url, params=params)
    return response.json()
```

### Features
- ✅ Aggregates multiple DEXes
- ✅ Best price discovery
- ✅ Gas optimization
- ⚠️ API rate limits apply

---

## 7. Kyber Network

### Protocol Information
- **Version:** DMM (Dynamic Market Maker)
- **Chains:** Ethereum, Polygon, BSC, Avalanche, Arbitrum
- **Market Coverage:** ⭐⭐⭐ **Moderate**
- **Integration Status:** ✅ **Integrated**

### API Endpoints

#### Kyber Network (Polygon)
```
GraphQL Subgraph: https://polygon-graph.kyberswap.com/subgraphs/name/kybernetwork/kyberswap-exchange-polygon
Router: 0x546C79662E028B661dFB4767664d0273184E4dD1
```

### Fee Structure
- **Swap Fee:** Variable (0.04% - 0.30%)
- **Dynamic fees** based on market conditions

---

## 8. PancakeSwap (BSC)

### Protocol Information
- **Version:** V2, V3
- **Chains:** BSC (primary), Ethereum, Polygon
- **Market Coverage:** ⭐⭐⭐⭐⭐ **High** (BSC leader)
- **Integration Status:** ✅ **Integrated**

### API Endpoints

#### PancakeSwap (BSC)
```
GraphQL Subgraph: https://api.thegraph.com/subgraphs/name/pancakeswap/exchange-v2
Router V2: 0x10ED43C718714eb63d5aA57B78B54704E256024E
Router V3: 0x1b81D678ffb9C0263b24A97847620C99d213eB14
```

### Fee Structure
- **V2:** 0.25% swap fee
- **V3:** Variable tiers

---

## 9. DODO

### Protocol Information
- **Type:** Proactive Market Maker (PMM)
- **Chains:** Ethereum, BSC, Polygon, Arbitrum
- **Market Coverage:** ⭐⭐⭐ **Moderate**
- **Integration Status:** ✅ **Integrated**

### API Endpoints

#### DODO (Polygon)
```
REST API: https://api.dodoex.io/
GraphQL: https://api.thegraph.com/subgraphs/name/dodoex/dodoex-v2-polygon
```

### Features
- ✅ PMM algorithm (capital efficient)
- ✅ Lower slippage for large trades
- ✅ Crowdpooling support

---

## 10. Bancor

### Protocol Information
- **Version:** V3
- **Chains:** Ethereum (primary)
- **Market Coverage:** ⭐⭐⭐ **Moderate**
- **Integration Status:** ⚠️ **Limited** (Ethereum only)

### API Endpoints

#### Bancor (Ethereum)
```
REST API: https://api-v3.bancor.network/
GraphQL: https://api.thegraph.com/subgraphs/name/bancor/bancor-v3
```

### Features
- Single-sided liquidity
- Impermanent loss protection
- ⚠️ Not available on Polygon

---

## DEX Comparison Matrix

| DEX | Polygon | Ethereum | BSC | Arbitrum | Market Coverage | Fee % | Integration |
|-----|---------|----------|-----|----------|----------------|-------|-------------|
| **Uniswap V2** | ✅ | ✅ | ❌ | ✅ | ⭐⭐⭐⭐⭐ | 0.30 | ✅ Full |
| **Uniswap V3** | ✅ | ✅ | ❌ | ✅ | ⭐⭐⭐⭐⭐ | 0.05-1.00 | ✅ Full |
| **SushiSwap** | ✅ | ✅ | ✅ | ✅ | ⭐⭐⭐⭐ | 0.30 | ✅ Full |
| **QuickSwap** | ✅ | ❌ | ❌ | ❌ | ⭐⭐⭐⭐ | 0.30 | ✅ Full |
| **Curve** | ✅ | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ | 0.04 | ✅ Full |
| **Balancer** | ✅ | ✅ | ❌ | ✅ | ⭐⭐⭐⭐ | 0.01-10 | ✅ Full |
| **1inch** | ✅ | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ | Variable | ✅ Full |
| **Kyber** | ✅ | ✅ | ✅ | ✅ | ⭐⭐⭐ | 0.04-0.30 | ✅ Integrated |
| **PancakeSwap** | ⚠️ | ❌ | ✅ | ❌ | ⭐⭐⭐⭐⭐ | 0.25 | ✅ Integrated |
| **DODO** | ✅ | ✅ | ✅ | ✅ | ⭐⭐⭐ | Variable | ✅ Integrated |

---

## Integration Architecture

### Data Flow for DEX Price Scanning

```
┌─────────────────────────────────────────────────────────────┐
│                    DEX INTEGRATION LAYER                    │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   GraphQL     │   │ Direct RPC    │   │  REST API     │
│   Subgraphs   │   │  Queries      │   │   Calls       │
├───────────────┤   ├───────────────┤   ├───────────────┤
│ • Uniswap     │   │ • Curve       │   │ • 1inch       │
│ • SushiSwap   │   │ • Balancer    │   │ • DODO        │
│ • QuickSwap   │   │ • Custom      │   │ • Kyber       │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
                  ┌──────────────────┐
                  │   DexPricer      │
                  │   • Normalize    │
                  │   • Cache        │
                  │   • Validate     │
                  └────────┬─────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │ QuantumLiquidityDetector     │
            │ • Volatility tracking        │
            │ • Stability assessment       │
            └──────────────┬───────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  OmniBrain      │
                  │  Opportunity    │
                  │  Detection      │
                  └─────────────────┘
```

---

## Optimal Swapping Strategies

### Strategy 1: Stablecoin Arbitrage
**Best DEXes:** Curve, Uniswap V3 (0.05% pools)

```python
# Example: USDC → DAI arbitrage
route_1 = {
    'dex': 'curve',
    'pool': '0x...',  # aave pool
    'fee': 0.04,
    'liquidity': 50_000_000  # $50M
}

route_2 = {
    'dex': 'uniswap_v3',
    'pool': '0x...',
    'fee': 0.05,
    'liquidity': 30_000_000  # $30M
}

# Quantum score: Higher for Curve due to lower fee
```

### Strategy 2: Major Token Pairs
**Best DEXes:** Uniswap V2/V3, SushiSwap, QuickSwap

```python
# Example: WETH → USDC
# Use Quantum Pathfinder for multi-dimensional optimization
optimizer.find_quantum_optimal_paths(
    token_start='0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619',  # WETH
    token_end='0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',    # USDC
    available_dexes={
        'uniswap_v3': [...],
        'quickswap': [...],
        'sushiswap': [...]
    }
)
```

### Strategy 3: Multi-hop Routes
**Best DEXes:** 1inch (aggregator), Quantum Pathfinder

```python
# Example: AAVE → WMATIC → USDC
# 3-hop route with quantum optimization
route = {
    'path': [AAVE, WMATIC, USDC],
    'dexes': ['sushiswap', 'quickswap'],
    'quantum_score': 0.78,  # High score
    'expected_profit': Decimal('25.50')
}
```

---

## API Rate Limits & Best Practices

### The Graph Subgraphs
- **Free Tier:** 1000 queries/day
- **Paid Tier:** Unlimited
- **Best Practice:** Cache responses for 10 seconds

### 1inch API
- **Free Tier:** 1 request/second
- **Paid Tier:** Higher limits
- **Best Practice:** Use for aggregation, not real-time scanning

### Direct RPC Calls (Curve, Balancer)
- **Rate Limit:** Depends on RPC provider
- **Best Practice:** Use multicall for batch queries

---

## Integration Code Examples

### Multi-DEX Price Comparison

```python
from offchain.ml.dex_pricer import DexPricer
from decimal import Decimal

def compare_dex_prices(token_in, token_out, amount_in):
    """Compare prices across all integrated DEXes"""
    
    prices = {}
    
    # Uniswap V2
    prices['uniswap_v2'] = pricer.get_uniswap_v2_price(
        router='0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff',
        token_in=token_in,
        token_out=token_out,
        amount_in=amount_in
    )
    
    # SushiSwap
    prices['sushiswap'] = pricer.get_uniswap_v2_price(
        router='0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506',
        token_in=token_in,
        token_out=token_out,
        amount_in=amount_in
    )
    
    # Curve (if stablecoin pair)
    if is_stablecoin_pair(token_in, token_out):
        prices['curve'] = pricer.get_curve_price(
            pool='0x...',
            token_in=token_in,
            token_out=token_out,
            amount_in=amount_in
        )
    
    # Find best price
    best_dex = max(prices, key=prices.get)
    best_price = prices[best_dex]
    
    return {
        'prices': prices,
        'best_dex': best_dex,
        'best_price': best_price,
        'spread': max(prices.values()) - min(prices.values())
    }
```

### Quantum-Enhanced DEX Selection

```python
from offchain.core.quantum_protocol_optimizer import QuantumProtocolOptimizer

optimizer = QuantumProtocolOptimizer()

# Build DEX map
available_dexes = {
    'quickswap': [USDC, WETH, WMATIC],
    'uniswap_v3': [USDC, WETH, WMATIC],
    'sushiswap': [USDC, WETH, WMATIC],
    'curve': [USDC, DAI, USDT]
}

# Build liquidity map from real-time data
liquidity_map = {
    ('quickswap', USDC, WETH): Decimal('5000000'),
    ('uniswap_v3', USDC, WETH): Decimal('8000000'),
    ('sushiswap', USDC, WETH): Decimal('3000000'),
    ('curve', USDC, DAI): Decimal('50000000'),
}

# Get quantum-optimized route
result = optimizer.optimize_opportunity(
    token_start=USDC,
    token_end=WETH,
    available_dexes=available_dexes,
    liquidity_map=liquidity_map,
    current_gas_price=45
)

# Result includes:
# - timing_recommendation: 'EXECUTE_NOW' | 'WAIT' | 'EXECUTE_OPTIMAL'
# - expected_gas_price: 38 gwei (predicted)
# - quantum_routes: List of routes sorted by efficiency
# - optimization_score: 0.87 (high quality)
```

---

## Maintenance & Updates

### Update Schedule
- **Daily:** Check for new high-liquidity pools
- **Weekly:** Review DEX API changes
- **Monthly:** Add new DEX integrations
- **Quarterly:** Full integration audit

### Monitoring
- Track API uptime for each DEX
- Monitor subgraph sync status
- Alert on API rate limit issues
- Validate price accuracy vs. external sources

---

## Summary

### Integration Status
- **Fully Integrated:** 8 DEXes
- **Partial Integration:** 2 DEXes
- **Total Coverage:** 10+ DEXes across 6 chains

### Market Coverage
- **High Coverage DEXes:** 5 (Uniswap, Curve, 1inch, PancakeSwap, QuickSwap)
- **Moderate Coverage DEXes:** 5 (SushiSwap, Balancer, Kyber, DODO, Bancor)

### Polygon Focus
- **Primary DEXes:** QuickSwap, Uniswap V3, SushiSwap, Curve
- **Recommended for:** All Polygon arbitrage operations
- **Quantum Optimizer:** Optimizes across all integrated DEXes

---

**Document Status:** ✅ Complete  
**Last Updated:** January 5, 2026  
**Maintained By:** Titan2.0 Development Team  
**Version:** 1.0
