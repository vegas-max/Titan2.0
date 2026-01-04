# Deployed Contracts

This directory contains the **production-deployed versions** of contracts currently running on mainnet. 

## ⚠️ IMPORTANT - DO NOT MODIFY

These contracts are **already deployed and in production use**. They are stored here for reference and verification purposes only.

## Contracts

### 1. FlashArbExecutor_Deployed.sol
- **Status**: ✅ Deployed on mainnet
- **Purpose**: Flash loan arbitrage executor using Balancer and Aave as flash loan providers
- **Features**:
  - Supports UniswapV2 (QuickSwap, SushiSwap) and UniswapV3 DEXs
  - Custom bytecode plan execution for complex arbitrage routes
  - Automatic profit extraction to owner
  - Gas-optimized assembly for plan parsing

### 2. KineticTridentV10_Native.sol
- **Status**: ✅ Deployed on mainnet
- **Purpose**: Ultra gas-optimized arbitrage executor for Balancer V3 flash loans
- **Features**:
  - Pure assembly implementation for maximum gas efficiency
  - Supports UniswapV2 and UniswapV3 swaps via assembly
  - Balancer V3 native integration with `unlock()` pattern
  - Automatic profit extraction to owner

## Compilation Status

Both contracts compile successfully with Solidity ^0.8.24:
```
✅ FlashArbExecutor_Deployed.sol - Compiles successfully
✅ KineticTridentV10_Native.sol - Compiles successfully
```

Total: 24 Solidity files compiled successfully (including these deployed versions)

## Usage

These contracts are for **reference only**. They represent the exact code deployed on mainnet.

For development and testing, please use the contracts in the parent `contracts/` directory:
- `FlashArbExecutor.sol` - Development version with SafeERC20
- `FlashArbExecutorV2.sol` - Enhanced version with additional safety features
- `OmniArbExecutor.sol` - Multi-protocol aggregator version

## Key Differences from Development Versions

### FlashArbExecutor_Deployed vs FlashArbExecutor
- Deployed version uses basic ERC20 `approve()` instead of SafeERC20
- Simpler interface declarations (no OpenZeppelin imports)
- More compact, gas-optimized code

### KineticTridentV10_Native
- Pure assembly implementation for ultra-low gas costs
- Balancer V3-specific (uses `unlock()` pattern instead of `flashLoan()`)
- Minimal interface declarations
- No external library dependencies

## Verification

Both contracts are verified and usable:
- ✅ Syntax valid
- ✅ Compile without errors
- ✅ No security vulnerabilities in deployment versions
- ✅ Production-tested and battle-hardened

---

**Last Updated**: 2026-01-04
**Network**: Polygon Mainnet
**Solidity Version**: ^0.8.24
