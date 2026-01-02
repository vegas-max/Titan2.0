# Custom Enum Usage Analysis for Tokens and DEXes

## Executive Summary

This document analyzes the current usage of identifiers for tokens and DEXes in the Titan 2.0 codebase and provides recommendations for standardization using Python enums.

**Current State**: String-based identifiers (e.g., `"USDC"`, `"WETH"`, `"UNIV3"`, `"SUSHI"`)  
**Recommendation**: Implement custom Python enums for type safety and consistency

---

## Current Implementation Analysis

### 1. Chain Identifiers ✅ (Already Using Enum)

**Location**: `offchain/core/enum_matrix.py`

```python
class ChainID(IntEnum):
    ETHEREUM = 1
    POLYGON = 137
    ARBITRUM = 42161
    OPTIMISM = 10
    BASE = 8453
    BSC = 56
    AVALANCHE = 43114
    FANTOM = 250
    LINEA = 59144
    SCROLL = 534352
    MANTLE = 5000
    ZKSYNC = 324
    CELO = 42220
    OPBNB = 204
```

**Status**: ✅ **Well-implemented** - Uses Python `IntEnum` for type safety and direct mapping to chain IDs.

---

### 2. Token Identifiers ❌ (Currently String-Based)

**Current Usage Pattern**: String identifiers scattered throughout codebase

**Files Using String Token Identifiers**:
- `offchain/core/token_discovery.py` - Hardcoded token registry with strings
- `offchain/ml/brain.py` - Token tier lists as strings (`tier1_tokens = ['USDC', 'USDT', 'DAI', 'WETH', 'WBTC', 'ETH']`)
- `offchain/ml/strategies/instant_scalper.py` - Strategy tiers with string tuples
- `demo_terminal_display.py` - Display functions using strings
- `test_terminal_display.py` - Test data with strings
- `dashboard_server.py` - Mock data generation with strings
- Multiple simulation and test files

**Example Current Usage**:
```python
# offchain/ml/brain.py (Line 308)
tier1_tokens = ['USDC', 'USDT', 'DAI', 'WETH', 'WBTC', 'ETH']

# offchain/core/token_discovery.py (Lines 12-13)
BRIDGE_ASSETS = [
    "USDC", "USDT", "DAI", "WETH", "WBTC", 
    "LINK", "UNI", "AAVE", "MATIC", "FRAX"
]
```

**Issues with Current Approach**:
1. ❌ No type safety - typos can cause runtime errors
2. ❌ No IDE autocomplete support
3. ❌ Inconsistent naming (e.g., `"WETH"` vs `"weth"` vs `"Weth"`)
4. ❌ No central definition - tokens defined multiple times
5. ❌ Difficult to refactor or rename

---

### 3. DEX Identifiers ❌ (Currently String-Based)

**Current Usage Pattern**: String identifiers for DEX names

**Files Using String DEX Identifiers**:
- `offchain/core/config.py` - DEX router mappings with string keys
- `offchain/ml/brain.py` - DEX selection using strings (`dex1 == 'UNIV3'`)
- `offchain/ml/dex_pricer.py` - Method names based on string DEX types
- `demo_terminal_display.py` - Display with string DEX names
- `dashboard_server.py` - Mock data with string DEX names

**Example Current Usage**:
```python
# offchain/core/config.py (Lines 150-154)
DEX_ROUTERS = {
    1: {  # Ethereum
        "UNIV2": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
        "SUSHI": "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F",
    },
}

# offchain/ml/brain.py (Line 410-411)
if dex1 == 'UNIV3':
    step1_out = pricer.get_univ3_price(token_addr, weth_addr, safe_amount, fee=500)
```

**Issues with Current Approach**:
1. ❌ No type safety - typos can cause incorrect DEX selection
2. ❌ No IDE autocomplete support
3. ❌ Inconsistent naming across files
4. ❌ Difficult to add new DEX protocols
5. ❌ No validation of supported DEX names

---

## Recommended Implementation

### 1. Token Enum

**File**: `offchain/core/token_enum.py` (new file)

```python
from enum import Enum

class Token(str, Enum):
    """
    Enumeration of supported tokens across all chains.
    
    Uses str inheritance for JSON serialization compatibility.
    """
    # Wrapped Native Tokens
    WETH = "WETH"
    WMATIC = "WMATIC"
    WBNB = "WBNB"
    WAVAX = "WAVAX"
    WFTM = "WFTM"
    
    # Stablecoins
    USDC = "USDC"
    USDC_E = "USDC.e"  # Bridged USDC
    USDT = "USDT"
    DAI = "DAI"
    FRAX = "FRAX"
    
    # Major Assets
    WBTC = "WBTC"
    ETH = "ETH"
    
    # DeFi Tokens
    LINK = "LINK"
    UNI = "UNI"
    AAVE = "AAVE"
    CRV = "CRV"
    BAL = "BAL"
    SUSHI = "SUSHI"
    MATIC = "MATIC"
    
    def __str__(self):
        """Return the string value for backward compatibility"""
        return self.value

class TokenType(Enum):
    """Token type classification per chain"""
    CANONICAL = 0  # Native to the chain
    BRIDGED = 1    # Bridged version
    WRAPPED = 2    # Wrapped native
```

**Benefits**:
- ✅ Type-safe token references
- ✅ IDE autocomplete (`Token.USDC`)
- ✅ Prevents typos at development time
- ✅ Central definition
- ✅ JSON serializable (str inheritance)

---

### 2. DEX Enum

**File**: `offchain/core/dex_enum.py` (new file)

```python
from enum import Enum, IntEnum

class DEXProtocol(IntEnum):
    """
    DEX protocol type identifiers.
    Maps to on-chain protocol IDs in OmniArbExecutor.
    """
    UNIV2 = 1  # Uniswap V2 and forks
    UNIV3 = 2  # Uniswap V3
    CURVE = 3  # Curve pools

class DEX(str, Enum):
    """
    Enumeration of supported DEX platforms.
    
    Uses str inheritance for JSON serialization compatibility.
    """
    # Uniswap V2 Forks
    UNIV2 = "UNIV2"
    SUSHISWAP = "SUSHI"
    QUICKSWAP = "QUICKSWAP"
    PANCAKESWAP = "PANCAKE"
    TRADERJOE = "TRADERJOE"
    SPOOKYSWAP = "SPOOKYSWAP"
    
    # Uniswap V3
    UNIV3 = "UNIV3"
    
    # Curve
    CURVE = "CURVE"
    
    # Balancer
    BALANCER = "BALANCER"
    
    # Solidly Forks
    AERODROME = "AERODROME"
    VELODROME = "VELODROME"
    
    # Other
    CAMELOT = "CAMELOT"
    UBESWAP = "UBESWAP"
    SYNCSWAP = "SYNCSWAP"
    THRUSTER = "THRUSTER"
    
    def __str__(self):
        """Return the string value for backward compatibility"""
        return self.value
    
    @property
    def protocol(self) -> DEXProtocol:
        """Get the protocol type for this DEX"""
        # Map DEX to protocol type
        univ2_dexes = {
            DEX.UNIV2, DEX.SUSHISWAP, DEX.QUICKSWAP, 
            DEX.PANCAKESWAP, DEX.TRADERJOE, DEX.SPOOKYSWAP
        }
        
        if self in univ2_dexes:
            return DEXProtocol.UNIV2
        elif self == DEX.UNIV3:
            return DEXProtocol.UNIV3
        elif self == DEX.CURVE:
            return DEXProtocol.CURVE
        else:
            return DEXProtocol.UNIV2  # Default fallback
```

**Benefits**:
- ✅ Type-safe DEX references
- ✅ Protocol type mapping built-in
- ✅ IDE autocomplete (`DEX.QUICKSWAP`)
- ✅ Prevents invalid DEX names
- ✅ JSON serializable

---

## Migration Strategy

### Phase 1: Add Enum Definitions (Non-Breaking)

1. Create `offchain/core/token_enum.py`
2. Create `offchain/core/dex_enum.py`
3. Add backward compatibility via `__str__()` methods
4. Update `offchain/core/__init__.py` to export new enums

**Impact**: None (additive only)

### Phase 2: Update Core Modules (Low Risk)

Update these high-value files first:

1. `offchain/core/token_discovery.py`
   - Replace `BRIDGE_ASSETS` list with `Token` enum references
   - Update `TOKEN_REGISTRY` keys to use `Token` enum

2. `offchain/core/config.py`
   - Replace `DEX_ROUTERS` string keys with `DEX` enum

3. `offchain/ml/brain.py`
   - Replace tier token lists with `Token` enum references
   - Update DEX comparisons to use `DEX` enum

**Impact**: Low (internal modules with good test coverage)

### Phase 3: Update Pricing & Strategy Modules (Medium Risk)

1. `offchain/ml/dex_pricer.py` - Use `DEX` enum for method selection
2. `offchain/ml/strategies/instant_scalper.py` - Use `Token` enum in tiers

**Impact**: Medium (core trading logic)

### Phase 4: Update Display & Dashboard (Low Risk)

1. `offchain/core/terminal_display.py`
2. `dashboard_server.py`
3. `demo_terminal_display.py`

**Impact**: Low (display only, not trading critical)

### Phase 5: Update Tests (Low Risk)

1. Update all test files to use enums
2. Add new tests for enum functionality

**Impact**: Low (test code only)

---

## Implementation Example

### Before (Current):
```python
# offchain/ml/brain.py
tier1_tokens = ['USDC', 'USDT', 'DAI', 'WETH', 'WBTC', 'ETH']

for token_sym in tier1_tokens:
    if dex1 == 'UNIV3':
        price = pricer.get_univ3_price(...)
```

### After (With Enums):
```python
# offchain/ml/brain.py
from offchain.core.token_enum import Token
from offchain.core.dex_enum import DEX

tier1_tokens = [Token.USDC, Token.USDT, Token.DAI, Token.WETH, Token.WBTC, Token.ETH]

for token in tier1_tokens:
    token_sym = token.value  # Get string value
    if dex1 == DEX.UNIV3:
        price = pricer.get_univ3_price(...)
```

**Benefits of This Change**:
- ✅ IDE autocomplete prevents typos
- ✅ Type checkers can validate DEX names
- ✅ Refactoring tools work correctly
- ✅ Backward compatible (`.value` gives string)

---

## Compatibility Considerations

### JSON Serialization

Both enums inherit from `str` which makes them JSON-serializable:

```python
import json
from offchain.core.token_enum import Token

data = {
    "token": Token.USDC,
    "amount": 1000
}

json_str = json.dumps(data)  # Works: '{"token": "USDC", "amount": 1000}'
```

### Database Storage

Enums with `str` inheritance work seamlessly with databases:

```python
# SQLAlchemy example
token_symbol = Token.USDC  # Stores as "USDC" string in database
```

### API Compatibility

External APIs expect strings, which works with `__str__()` override:

```python
api_call(token=str(Token.USDC))  # Sends "USDC"
api_call(token=Token.USDC)       # Also sends "USDC" (implicit)
```

---

## Risk Assessment

| Phase | Risk Level | Mitigation |
|-------|-----------|------------|
| Add Enum Definitions | **None** | Non-breaking addition |
| Core Module Updates | **Low** | Comprehensive unit tests, gradual rollout |
| Pricing Module Updates | **Medium** | Extensive testing in paper trading mode first |
| Display Updates | **Low** | Visual verification only, no trading impact |
| Test Updates | **Low** | Test failures caught in CI/CD |

---

## Estimated Effort

| Phase | Estimated Time | Priority |
|-------|---------------|----------|
| 1. Add Enum Definitions | 2 hours | High |
| 2. Update Core Modules | 4 hours | High |
| 3. Update Pricing/Strategy | 6 hours | Medium |
| 4. Update Display/Dashboard | 3 hours | Low |
| 5. Update Tests | 4 hours | Medium |
| **Total** | **19 hours** | - |

---

## Recommendations

### Immediate Actions (High Priority)

1. ✅ **Create token enum** (`offchain/core/token_enum.py`)
2. ✅ **Create DEX enum** (`offchain/core/dex_enum.py`)
3. ✅ **Add comprehensive tests** for enum functionality
4. ✅ **Update core modules** (`token_discovery.py`, `config.py`, `brain.py`)

### Medium-Term Actions

5. **Update pricing modules** with enum usage
6. **Update strategy modules** with enum usage
7. **Run full integration tests** in paper trading mode

### Long-Term Maintenance

8. **Update documentation** to reference enums
9. **Add linting rules** to prevent string usage for tokens/DEXes
10. **Create migration guide** for contributors

---

## Alternative Approaches Considered

### 1. Keep Strings (Status Quo)
- ❌ No type safety
- ❌ Error-prone
- ❌ Not recommended

### 2. Use Literal Types
```python
from typing import Literal

TokenSymbol = Literal["USDC", "USDT", "DAI", "WETH"]
```
- ✅ Type checking in static analyzers
- ❌ No IDE autocomplete at runtime
- ❌ No central enum for iteration

### 3. Use Dataclasses
```python
@dataclass
class Token:
    symbol: str
    decimals: int
```
- ✅ Rich type information
- ❌ Overkill for simple identifiers
- ❌ More complex migration

**Chosen Approach**: Python Enums (str-based) - Best balance of type safety, simplicity, and compatibility

---

## Conclusion

**Recommendation**: Implement custom Python enums for both tokens and DEXes using the phased migration strategy outlined above.

**Key Benefits**:
1. 🔒 Type safety prevents runtime errors
2. 🚀 IDE autocomplete improves developer productivity
3. 📚 Central definitions improve maintainability
4. ✅ Backward compatibility ensures smooth migration
5. 🧪 Better testability and refactoring support

**Next Steps**:
1. Get stakeholder approval for migration plan
2. Create enum definition files
3. Begin Phase 1 implementation with comprehensive tests
4. Gradually roll out phases 2-5 with monitoring

---

**Document Version**: 1.0  
**Date**: 2026-01-02  
**Author**: GitHub Copilot  
**Status**: Analysis Complete - Awaiting Approval
