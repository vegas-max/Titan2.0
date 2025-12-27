# Token Registry Design: Maximum Coverage Without Bloating Solidity

## Problem Statement

Traditional approaches to multi-token support in Solidity contracts face a critical dilemma:
- **Hardcoded Enums**: Easy to use but bloat the contract (300 token enum = massive bytecode)
- **Minimal Support**: Lean contracts but limited market coverage

## Solution: Hybrid Architecture

Titan solves this with a **three-layer architecture** that separates concerns:

### 1. On-Chain: Tight Whitelist Registry

**Purpose**: Store only high-liquidity tokens actually traded
**Implementation**: Flexible `uint8` registry (0-255 IDs per chain)

```solidity
// NO hardcoded TokenId enum - just uint8 IDs!
mapping(uint256 => mapping(uint8 => mapping(uint8 => address))) public tokenRegistry;
// chainId => tokenId => tokenType => address
```

**Registry Management**:
```solidity
// Owner registers high-liquidity tokens
setToken(chainId, tokenId, tokenType, address)
batchSetTokens(chainIds[], tokenIds[], tokenTypes[], addresses[])
```

**Advantages**:
- ✅ Lean contract (no enum bloat)
- ✅ Upgradeable (add tokens without redeployment)
- ✅ Deterministic (registry is explicit and auditable)
- ✅ Gas-efficient (compact calldata for registered tokens)

**Typical Registry Size**: 20-50 high-liquidity tokens per chain

### 2. Off-Chain: 300+ Token Graph

**Purpose**: Discover opportunities across entire token universe
**Implementation**: Python brain with dynamic token loading

**File**: `ml/brain.py`
```python
# Load 100+ tokens per chain from 1inch API
tokens_list = TokenLoader.get_tokens(chain_id)

# Build comprehensive graph with 300+ nodes
for token in tokens_list[:100]:
    inventory[chain_id][token['symbol']] = token

# Tiered scanning strategy
tier1_tokens = ['USDC', 'USDT', 'DAI', 'WETH', 'WBTC']  # Every cycle
tier2_tokens = ['UNI', 'LINK', 'AAVE', ...]              # Every 2nd cycle
tier3_tokens = [all other tokens]                         # Every 5th cycle
```

**Advantages**:
- ✅ Comprehensive coverage (300+ tokens)
- ✅ Dynamic updates (new tokens detected automatically)
- ✅ Flexible logic (tiering, filtering, prioritization)
- ✅ No gas costs (computation happens off-chain)

### 3. Calldata: Adaptive Encoding

**Purpose**: Flexible execution of both registered and unregistered tokens
**Implementation**: Two encoding formats

#### Format 1: REGISTRY_ENUMS (Compact)
**Use case**: Registered high-liquidity tokens

```javascript
// Calldata uses registry IDs
const tokenOutIds = [1, 2, 0];      // USDC, USDT, WNATIVE (registry IDs)
const tokenOutTypes = [0, 0, 2];    // CANONICAL, CANONICAL, WRAPPED
const dexIds = [0, 1, 2];           // UniV2, UniV3, Curve (registry IDs)

// Contract resolves addresses from registry
tokenAddress = tokenRegistry[chainId][tokenId][tokenType]
```

**Advantages**:
- Compact calldata (uint8 IDs vs full addresses)
- Gas-efficient
- Clean code (no address repetition)

#### Format 2: RAW_ADDRESSES (Flexible)
**Use case**: Rare tokens or new opportunities

```javascript
// Calldata uses explicit addresses
const tokenOutPath = [TOKEN_A, TOKEN_B, TOKEN_C];  // Full addresses
const routersOrPools = [ROUTER_1, ROUTER_2, POOL]; // Full addresses

// Contract uses addresses directly
// No registry lookup needed
```

**Advantages**:
- Maximum flexibility (ANY token immediately)
- No registration required
- Handles edge cases (new tokens, testing)

## Token ID Assignment Strategy

### Recommended Conventions (Not Enforced)

```
ID Range    Purpose                     Examples
--------    -------                     --------
0-10        Universal tokens            0=WNATIVE, 1=USDC, 2=USDT, 3=DAI, 4=WBTC
11-50       Chain-specific top tokens   11=UNI, 12=LINK, 13=AAVE, ...
51-100      DeFi protocol tokens        51=CRV, 52=BAL, 53=SUSHI, ...
101-200     Bridge tokens               101=anyUSDC, 102=ceUSDT, ...
201-255     Reserved/Custom             Project-specific tokens
```

### Multi-Chain Example

**Polygon Registry**:
```javascript
// Universal tokens (same IDs across chains when possible)
setToken(137, 1, 0, USDC_POLYGON)     // ID 1 = USDC
setToken(137, 2, 0, USDT_POLYGON)     // ID 2 = USDT
setToken(137, 0, 2, WMATIC)           // ID 0 = Wrapped native

// Chain-specific tokens
setToken(137, 11, 0, QUICK)           // Polygon: QuickSwap token
setToken(137, 12, 0, GHST)            // Polygon: Aavegotchi
```

**Ethereum Registry**:
```javascript
// Same universal IDs
setToken(1, 1, 0, USDC_ETHEREUM)      // ID 1 = USDC
setToken(1, 2, 0, USDT_ETHEREUM)      // ID 2 = USDT
setToken(1, 0, 2, WETH)               // ID 0 = Wrapped native

// Chain-specific tokens
setToken(1, 11, 0, UNI)               // Ethereum: Uniswap token
setToken(1, 12, 0, LINK)              // Ethereum: Chainlink
```

## Workflow: From Discovery to Execution

### Step 1: Off-Chain Discovery (Brain)
```python
# brain.py finds opportunity
# Route: USDC -> TOKEN_X -> WETH -> USDC
# TOKEN_X is a rare token (not in registry)

# Brain checks registry status
is_token_x_registered = check_registry(chain_id, TOKEN_X)
# Returns False - use RAW_ADDRESSES
```

### Step 2: Encoding Selection (Brain)
```javascript
// Brain chooses encoding based on registry status
if (all_tokens_registered) {
    encoding = REGISTRY_ENUMS;
    tokenIds = [1, 15, 4];  // USDC, TOKEN_Y, WETH (registry IDs)
} else {
    encoding = RAW_ADDRESSES;
    tokenPath = [USDC_ADDR, TOKEN_X_ADDR, WETH_ADDR];  // Explicit
}
```

### Step 3: On-Chain Execution (Contract)
```solidity
// OmniArbExecutor receives route
function _runRoute(address inputToken, uint256 inputAmount, bytes memory routeData) {
    RouteEncoding encoding = abi.decode(routeData, (RouteEncoding));
    
    if (encoding == RAW_ADDRESSES) {
        // Use explicit addresses from calldata
        return _runRouteRaw(inputToken, inputAmount, routeData);
    } else {
        // Resolve addresses from registry
        return _runRouteRegistry(inputToken, inputAmount, routeData);
    }
}
```

## Migration Path

### Current State
- ❌ Hardcoded `TokenId` enum with 6 tokens
- ❌ Limited to enum values
- ❌ Requires contract upgrade to add tokens

### After This Change
- ✅ Flexible `uint8` registry (0-255)
- ✅ Owner can add tokens via `setToken()`
- ✅ RAW_ADDRESSES for any token immediately
- ✅ Off-chain system manages full 300+ graph

### For Existing Deployments
1. Current enum values still work (0-5 map to same IDs)
2. New tokens added via `setToken()` use IDs 6-255
3. Rare tokens use RAW_ADDRESSES encoding
4. No breaking changes to existing integrations

## Benefits Summary

| Aspect | Old (Hardcoded Enum) | New (Flexible Registry) |
|--------|---------------------|------------------------|
| **On-Chain Size** | 300 enum values = bloat | 20-50 registrations = lean |
| **Upgradability** | Requires redeployment | `setToken()` call |
| **Coverage** | Limited to enum | 300+ via off-chain + RAW |
| **Gas Efficiency** | ❌ Large bytecode | ✅ Compact mappings |
| **Flexibility** | ❌ Fixed at deploy | ✅ Dynamic addition |
| **Audit Clarity** | ❌ Hidden limits | ✅ Explicit registry |

## Security Considerations

### Registry Manipulation
- ✅ **Mitigation**: Only `owner` can call `setToken()`
- ✅ **Transparency**: Token assignments emit events
- ✅ **Verification**: Registry is publicly readable

### Token ID Collisions
- ✅ **Prevention**: Owner must manage ID assignments
- ✅ **Convention**: Follow documented ID ranges
- ✅ **Override**: `setToken()` can update existing IDs (owner only)

### Calldata Validation
- ✅ **Registry Encoding**: Reverts if token not registered
- ✅ **Raw Encoding**: No validation needed (explicit addresses)
- ✅ **Swap Execution**: Standard ERC20 checks apply

## Conclusion

This design achieves the stated goal: **maximum coverage without bloating Solidity**.

**On-chain** remains **lean, upgradeable, and deterministic** with a tight whitelist registry.

**Off-chain** does the **heavy thinking** with a 300+ token graph and intelligent path discovery.

**Calldata** provides **flexibility** through adaptive encoding based on token registry status.

The contract stays under control, gas-efficient, and auditable—while Titan's brain handles the complexity where it belongs.
