# Token Configuration System - Complete Integration Guide

## Overview

The Titan 2.0 system now features a centralized token configuration system that provides a single source of truth for token addresses, IDs, and types across all supported chains. This system enables:

- Consistent token identification across chains
- Automatic cross-chain token resolution
- Registry-based vs. raw address encoding optimization
- Token type awareness (CANONICAL, BRIDGED, WRAPPED)

## Architecture

### Core Components

```
offchain/core/
├── token_config.js      # JavaScript token configuration
└── token_config.py      # Python token configuration
```

### Token ID Convention

```
0-10:    Universal tokens (consistent across chains)
         - 0: WNATIVE (Wrapped native token)
         - 1: USDC
         - 2: USDT
         - 3: DAI
         - 4: WBTC
         - 5: WETH

11-50:   Chain-specific tokens
         - 11: UNI
         - 12: LINK
         - 13: AAVE
         - 14: CRV
         - 15: SUSHI
         - 16: BAL
         - 17: QUICK (Polygon)
         - 18: GHST (Polygon)
         - 19: OP (Optimism)
         - 20: ARB (Arbitrum)
         - 21: AVAX
         - 22: FTM

51-255:  Available for expansion
```

### Token Types

```javascript
TokenType = {
  CANONICAL: 0,  // Native to the chain
  BRIDGED: 1,    // Bridged version (e.g., USDC.e)
  WRAPPED: 2     // Wrapped native (WETH, WMATIC, etc.)
}
```

## Supported Chains

The system currently supports 5 major chains:

| Chain | ID | Native Token | Universal Tokens |
|-------|----|--------------| -----------------|
| Ethereum | 1 | ETH | WETH, USDC, USDT, DAI, WBTC, UNI, LINK, AAVE |
| Polygon | 137 | MATIC | WMATIC, USDC (2 variants), USDT, DAI, WBTC, WETH, QUICK, GHST |
| Arbitrum | 42161 | ETH | WETH, USDC (2 variants), USDT, DAI, WBTC, ARB |
| Optimism | 10 | ETH | WETH, USDC (2 variants), USDT, DAI, WBTC, OP |
| Base | 8453 | ETH | WETH, USDC (2 variants), DAI |

## JavaScript Usage

### Importing

```javascript
const tokenConfig = require('./offchain/core/token_config');
```

### Get Token Address

```javascript
// Get USDC on Polygon (canonical)
const usdc = tokenConfig.getTokenAddress(137, tokenConfig.UniversalTokenIds.USDC, tokenConfig.TokenType.CANONICAL);
// Returns: "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"

// Get USDC.e on Polygon (bridged)
const usdce = tokenConfig.getTokenAddress(137, tokenConfig.UniversalTokenIds.USDC, tokenConfig.TokenType.BRIDGED);
// Returns: "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
```

### Reverse Lookup

```javascript
// Get token ID and type from address
const tokenInfo = tokenConfig.getTokenIdFromAddress(137, "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359");
// Returns: { id: 1, type: 0 } (USDC, CANONICAL)
```

### Check if Token is Registered

```javascript
const isRegistered = tokenConfig.isTokenRegistered(137, "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359");
// Returns: true
```

### Get All Token Variants

```javascript
// Get all USDC variants on Polygon
const variants = tokenConfig.getAllTokenAddresses(137, tokenConfig.UniversalTokenIds.USDC);
// Returns: [
//   { address: "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359", type: 0 },  // CANONICAL
//   { address: "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174", type: 1 }   // BRIDGED
// ]
```

## Python Usage

### Importing

```python
from offchain.core.token_config import (
    TokenType,
    UniversalTokenIds,
    ChainTokenIds,
    get_token_address,
    get_token_id_from_address,
    is_token_registered,
    get_canonical_token_address
)
```

### Get Token Address

```python
# Get USDC on Polygon (canonical)
usdc = get_token_address(137, UniversalTokenIds.USDC, TokenType.CANONICAL)
# Returns: "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"

# Get canonical token (auto-selects best type)
usdc = get_canonical_token_address(137, UniversalTokenIds.USDC)
# Returns: "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359" (prefers CANONICAL)
```

### Reverse Lookup

```python
# Get token ID and type from address
token_info = get_token_id_from_address(137, "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359")
# Returns: (1, TokenType.CANONICAL) (USDC, CANONICAL)
```

### Check if Token is Registered

```python
is_reg = is_token_registered(137, "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359")
# Returns: True
```

## Integration Examples

### Brain.py - Optimal Encoding Selection

```python
# In brain.py, determine optimal encoding for route
def get_token_encoding_info(self, chain_id, token_address):
    """
    Determine optimal encoding for a token (REGISTRY_ENUMS vs RAW_ADDRESSES)
    """
    addr_lower = token_address.lower()
    if chain_id in self.token_registry_map and addr_lower in self.token_registry_map[chain_id]:
        registry_info = self.token_registry_map[chain_id][addr_lower]
        return {
            'encoding': 'REGISTRY_ENUMS',
            'id': registry_info['id'],
            'type': registry_info['type']
        }
    return {'encoding': 'RAW_ADDRESSES'}
```

### Bridge Manager - Cross-Chain Token Resolution

```python
# In bridge_manager.py, find equivalent token on destination chain
def get_equivalent_token(self, src_chain, dst_chain, token_address):
    """
    Find the equivalent token on destination chain
    """
    token_info = get_token_id_from_address(src_chain, token_address)
    if token_info:
        token_id, _ = token_info
        return get_canonical_token_address(dst_chain, token_id)
    return None
```

### LiFi Manager - Auto Token Resolution

```javascript
// In lifi_manager.js, auto-resolve destination token
function resolveDestinationToken(fromChainId, fromToken, toChainId, toToken = null) {
  // If destination token is provided, use it
  if (toToken) return toToken;
  
  // Try to resolve using token registry
  const tokenInfo = tokenConfig.getTokenIdFromAddress(fromChainId, fromToken);
  if (tokenInfo) {
    const tokenId = tokenInfo.id;
    // Get canonical token on destination chain
    const destToken = tokenConfig.getTokenAddress(toChainId, tokenId, tokenConfig.TokenType.CANONICAL);
    if (destToken) {
      console.log(`🔗 Auto-resolved destination token: ${destToken} (Token ID: ${tokenId})`);
      return destToken;
    }
  }
  
  return null;
}
```

## Adding New Tokens

### Step 1: Update token_config.js

```javascript
// Add to ChainTokenIds if chain-specific
const ChainTokenIds = {
  // ... existing tokens ...
  MATIC: 23,  // New token ID
};

// Add to CHAIN_CONFIGS
const CHAIN_CONFIGS = {
  137: {
    tokens: [
      // ... existing tokens ...
      { 
        id: ChainTokenIds.MATIC, 
        type: TokenType.CANONICAL, 
        address: "0x..." 
      }
    ]
  }
};
```

### Step 2: Update token_config.py

```python
class ChainTokenIds(IntEnum):
    # ... existing tokens ...
    MATIC = 23  # New token ID

CHAIN_CONFIGS = {
    137: {
        "tokens": [
            # ... existing tokens ...
            TokenConfig(
                id=ChainTokenIds.MATIC, 
                type=TokenType.CANONICAL, 
                address="0x..."
            )
        ]
    }
}
```

### Step 3: Update setupTokenRegistry.js (for on-chain)

```javascript
// Add to ChainTokenIds
const ChainTokenIds = {
  // ... existing tokens ...
  MATIC: 23
};

// Add to CHAIN_CONFIGS
const CHAIN_CONFIGS = {
  137: {
    tokens: [
      // ... existing tokens ...
      { 
        id: ChainTokenIds.MATIC, 
        type: TokenType.CANONICAL, 
        address: "0x..." 
      }
    ]
  }
};
```

### Step 4: Register on-chain (if using registry encoding)

```bash
export EXECUTOR_ADDRESS=0x...
npx hardhat run scripts/setupTokenRegistry.js --network polygon
```

## Testing

### Test Token Resolution

```javascript
// JavaScript
const tokenConfig = require('./offchain/core/token_config');

// Test getting USDC on multiple chains
console.log('Ethereum USDC:', tokenConfig.getTokenAddress(1, tokenConfig.UniversalTokenIds.USDC));
console.log('Polygon USDC:', tokenConfig.getTokenAddress(137, tokenConfig.UniversalTokenIds.USDC));
console.log('Arbitrum USDC:', tokenConfig.getTokenAddress(42161, tokenConfig.UniversalTokenIds.USDC));

// Test reverse lookup
const addr = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359";
const info = tokenConfig.getTokenIdFromAddress(137, addr);
console.log('Token Info:', info);
console.log('Symbol:', tokenConfig.getTokenSymbol(info.id));
```

```python
# Python
from offchain.core.token_config import *

# Test getting USDC on multiple chains
print('Ethereum USDC:', get_token_address(1, UniversalTokenIds.USDC))
print('Polygon USDC:', get_token_address(137, UniversalTokenIds.USDC))
print('Arbitrum USDC:', get_token_address(42161, UniversalTokenIds.USDC))

# Test reverse lookup
addr = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"
info = get_token_id_from_address(137, addr)
print('Token Info:', info)
print('Symbol:', get_token_symbol(info[0]))
```

## Benefits

1. **Single Source of Truth**: All token addresses managed in one place
2. **Type Safety**: Token types (CANONICAL, BRIDGED, WRAPPED) are enforced
3. **Cross-Chain Consistency**: Universal tokens use same IDs across chains
4. **Automatic Resolution**: Cross-chain operations resolve tokens automatically
5. **Optimal Encoding**: System chooses best encoding (registry vs. raw) automatically
6. **Extensibility**: Easy to add new chains and tokens
7. **Backward Compatibility**: Existing code continues to work with enhancements

## Migration from Legacy System

The new system is backward compatible. Legacy code using `tokenUniverse.js` or `token_discovery.py` will continue to work as those modules now use the centralized configuration internally.

### For New Code

**Before:**
```javascript
const TOKENS = require('./tokenUniverse').TOKENS;
const usdc = TOKENS[137]['USDC'];
```

**After:**
```javascript
const tokenConfig = require('./token_config');
const usdc = tokenConfig.getTokenAddress(137, tokenConfig.UniversalTokenIds.USDC);
```

### For Existing Code

No changes required! The system is fully backward compatible.

## Best Practices

1. **Use Registry IDs for Common Tokens**: Universal tokens should always use registry IDs
2. **Prefer Canonical Tokens**: Use `get_canonical_token_address()` when you don't care about type
3. **Check Registration Status**: Before using registry encoding, verify token is registered
4. **Handle Multiple Variants**: Some tokens (USDC) have both canonical and bridged versions
5. **Auto-Resolve Cross-Chain**: Let the system resolve destination tokens automatically

## Troubleshooting

### Token Not Found

```javascript
const addr = tokenConfig.getTokenAddress(137, 99);
// Returns: null (token ID 99 not registered)
```

**Solution**: Check if token ID is correct and registered for that chain.

### Multiple Token Variants

```javascript
// Get all USDC variants on Polygon
const variants = tokenConfig.getAllTokenAddresses(137, tokenConfig.UniversalTokenIds.USDC);
// Returns: Array with both CANONICAL and BRIDGED versions
```

**Solution**: Use `get_canonical_token_address()` to get preferred version, or specify type explicitly.

### Cross-Chain Resolution Fails

```python
dest_token = get_canonical_token_address(999, UniversalTokenIds.USDC)
# Returns: None (chain 999 not supported)
```

**Solution**: Check if destination chain is supported in CHAIN_CONFIGS.

## Future Enhancements

1. **More Chains**: Add support for additional L2s and alt-L1s
2. **More Tokens**: Expand token coverage per chain
3. **Dynamic Loading**: Load token configs from remote source
4. **Price Feeds**: Integrate with price oracle for real-time pricing
5. **Liquidity Metrics**: Include liquidity data for routing decisions

## Support

For issues or questions:
- Check existing documentation in `docs/` directory
- Review implementation in `offchain/core/token_config.js` and `.py`
- Refer to `IMPLEMENTATION_SUMMARY_TOKEN_REGISTRY.md` for on-chain registry details
