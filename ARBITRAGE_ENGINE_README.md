# Arbitrage Engine - Off-Chain Decision Logic

## Overview

This module implements a strict deterministic logic system for evaluating arbitrage opportunities and selecting the optimal execution path between two smart contracts:

- **HFT Executor (0xAF54D81835F811F1D4aB35c5856DDAE8834cdDA2)**: Optimized for direct pair swaps on Uniswap V2 forks, bypasses routers for flash loans
- **Router Executor (0x4442782681b668365334C3D2A6F004F0760DA393)**: Supports complex multi-hop paths and various DEX types, uses routers for flash loans

Both are executors chosen for specific reasons:
- HFT provides gas efficiency on simple V2-compatible swaps
- Router handles complex multi-hop paths and non-V2 exchanges

## Architecture

### Decision Flow

The engine uses a three-gate sequential evaluation system:

```
Opportunity → Gate 1 → Gate 2 → Gate 3 → Execution
             (Topology) (Liquidity) (Gas)
```

Each gate can either:
- **Exit**: Select a contract and return
- **Continue**: Pass to the next gate

### Gate 1: Topology Check (Hard Constraint)

**Purpose**: Determine if the arbitrage path complexity exceeds HFT capabilities

**Logic**:
- If `path.length > 2` → Select **ROUTER**
- If `path.length = 2` → Continue to Gate 2

**Rationale**: HFT contract only supports direct A↔B swaps. Multi-hop paths (A→B→C→A) require Router's path-based execution.

**Example**:
```javascript
// Multi-hop (triangular) - Uses Router
path: [WETH, USDC, DAI, WETH]  // length = 4

// Simple swap - Continues to Gate 2
path: [WETH, USDC]  // length = 2
```

### Gate 2: Liquidity Source Check (Technology Constraint)

**Purpose**: Verify all exchanges use Uniswap V2-compatible interfaces

**Logic**:
- Check each exchange against V2 compatibility list
- If any exchange is V3, Curve, Balancer, etc. → Select **ROUTER**
- If all exchanges are V2 compatible → Continue to Gate 3

**Rationale**: HFT uses `IUniswapV2Pair` ABI signatures. Non-V2 pools have different interfaces and will cause reverts.

**V2 Compatible DEXes by Chain**:
```javascript
Ethereum (1):   Uniswap, SushiSwap, ShibaSwap
Polygon (137):  QuickSwap, SushiSwap, ApeSwap
BSC (56):       PancakeSwap, ApeSwap, BiSwap
Arbitrum:       SushiSwap, Camelot
Optimism:       Velodrome, ZipSwap
```

### Gate 3: Gas Simulation (Economic Determinism)

**Purpose**: Select the most gas-efficient execution path

**Logic**:
1. Build payloads for both HFT and Router
2. Simulate gas via `eth_estimateGas`
3. If `gas_HFT < gas_Router` → Select **HFT**
4. Otherwise → Select **ROUTER**

**Rationale**: HFT bypasses router abstraction, typically saving 30-50k gas on simple swaps.

**Fallback**: On simulation error, default to Router for safety.

## Contract Interfaces

### HFT Executor (0xAF54D81835F811F1D4aB35c5856DDAE8834cdDA2)

**Function Signature**:
```solidity
function startArbitrage(
    address _poolA,
    address _poolB,
    uint256 _amount
) external
```

**Usage**: Direct pool-to-pool arbitrage on V2 forks

**Payload Construction**:
```javascript
const payload = iface.encodeFunctionData('startArbitrage', [
    poolAddressA,  // Specific UniV2 pair contract
    poolAddressB,  // Specific UniV2 pair contract
    amountInWei
]);
```

### Router Executor (0x4442782681b668365334C3D2A6F004F0760DA393)

**Function Signature**:
```solidity
function startArbitrage(
    address[] _path,
    address[] _routers,
    uint256 _amount
) external
```

**Usage**: Multi-hop or non-V2 arbitrage

**Payload Construction**:
```javascript
const payload = iface.encodeFunctionData('startArbitrage', [
    [tokenA, tokenB, tokenA],  // Token path
    [uniRouter, sushiRouter],   // Router addresses
    amountInWei
]);
```

## Usage Examples

### Basic Integration

```javascript
const { ArbitrageEngine } = require('./execution/arbitrage_engine');
const { ethers } = require('ethers');

// Initialize
const provider = new ethers.JsonRpcProvider(RPC_URL);
const engine = new ArbitrageEngine(provider, chainId);

// Evaluate opportunity
const opportunity = {
    path: [WETH, USDC],
    exchanges: ['Quickswap', 'Sushiswap'],
    routers: [quickswapRouter, sushiRouter],
    poolAddressA: quickswapPair,
    poolAddressB: sushiPair,
    amountIn: ethers.parseEther('1.0')
};

const decision = await engine.selectExecutionEngine(opportunity);

console.log(`Target: ${decision.target}`);
console.log(`Reason: ${decision.reason}`);
console.log(`Payload: ${decision.payload}`);

// Execute
const tx = await wallet.sendTransaction({
    to: decision.target,
    data: decision.payload
});
```

### Decision Examples

**Example 1: Multi-hop Arbitrage**
```javascript
// Input
opportunity = {
    path: [WETH, USDC, DAI, WETH],
    exchanges: ['Quickswap', 'Sushiswap', 'Quickswap']
}

// Output (Gate 1)
{
    target: ROUTER_CONTRACT,
    reason: 'TOPOLOGY_CHECK: Path length > 2 requires Router',
    gate: 'GATE_1'
}
```

**Example 2: Uniswap V3 Pool**
```javascript
// Input
opportunity = {
    path: [WETH, USDC],
    exchanges: ['Uniswap V3']
}

// Output (Gate 2)
{
    target: ROUTER_CONTRACT,
    reason: 'LIQUIDITY_CHECK: Exchange Uniswap V3 is not V2 compatible',
    gate: 'GATE_2'
}
```

**Example 3: V2 Simple Swap (Gas Optimized)**
```javascript
// Input
opportunity = {
    path: [WETH, USDC],
    exchanges: ['Quickswap', 'Sushiswap'],
    poolAddressA: '0x...',
    poolAddressB: '0x...'
}

// Output (Gate 3)
{
    target: HFT_CONTRACT,
    reason: 'GAS_SIMULATION: HFT is more gas efficient',
    gate: 'GATE_3',
    gasHFT: '145000',
    gasRouter: '195000'
}
```

## Configuration

### Environment Variables

```bash
# Contract addresses
HFT_CONTRACT_ADDRESS=0xAF54D81835F811F1D4aB35c5856DDAE8834cdDA2
ROUTER_CONTRACT_ADDRESS=0x4442782681b668365334C3D2A6F004F0760DA393
```

### Custom V2 DEX List

To add support for new V2 forks:

```javascript
// In arbitrage_engine.js
const V2_COMPATIBLE_DEXES = {
    // ...
    999: ['custom-dex-v2', 'another-v2-fork']
};
```

## Testing

Run standalone tests:
```bash
node test/arbitrage_engine_standalone_test.js
```

Run Hardhat tests:
```bash
npx hardhat test test/ArbitrageEngine.test.js
```

## Decision Matrix Summary

| Condition | Gate | Action |
|-----------|------|--------|
| Path length > 2 | Gate 1 | → ROUTER |
| Path length = 2 | Gate 1 | Continue |
| Exchange is V3/Curve/Balancer | Gate 2 | → ROUTER |
| All exchanges are V2 | Gate 2 | Continue |
| HFT gas < Router gas | Gate 3 | → HFT |
| HFT gas ≥ Router gas | Gate 3 | → ROUTER |
| Gas estimation fails | Gate 3 | → ROUTER (safe) |

## Security Considerations

1. **Payload Validation**: Both contracts validate inputs on-chain
2. **Simulation Required**: Always simulate before execution
3. **Profit Threshold**: Contracts enforce minimum profit requirements
4. **Owner Control**: Only contract owner can execute arbitrage
5. **Reentrancy Protection**: Both contracts use reentrancy guards

## Performance

- **Gate 1**: O(1) - Instant path length check
- **Gate 2**: O(n) - Linear scan of exchanges
- **Gate 3**: O(1) - Two parallel gas estimations

**Total Decision Time**: < 100ms (excluding network latency)

## Error Handling

The engine includes comprehensive error handling:

```javascript
try {
    const decision = await engine.selectExecutionEngine(opportunity);
} catch (error) {
    if (error.message.includes('Invalid opportunity structure')) {
        // Handle invalid input
    }
    // Default to Router on any error
    const fallback = {
        target: ROUTER_CONTRACT,
        payload: buildRouterPayload(opportunity),
        reason: 'ERROR_FALLBACK'
    };
}
```

## Integration with Existing Bot

The engine integrates seamlessly with the existing bot.js:

```javascript
const { ArbitrageEngine } = require('./arbitrage_engine');

// In executeTrade function
const arbEngine = new ArbitrageEngine(provider, chainId);
const decision = await arbEngine.selectExecutionEngine(opportunity);

// Use decision
const tx = await wallet.sendTransaction({
    to: decision.target,
    data: decision.payload,
    ...gasParams
});
```

## License

MIT
