# Executor Contract Architecture Guide

## Overview

Titan's flash loan arbitrage system supports two deployment architectures for executor contracts. This guide clarifies the differences and helps you choose the right approach.

---

## 🎯 Two Deployment Approaches

### **Approach 1: Unified FlashArbExecutor (RECOMMENDED)**

**Used by:** `offchain/execution/bot.js` (main bot)

**Description:** Deploy ONE smart contract that handles ALL arbitrage scenarios.

**Advantages:**
- ✅ Simpler deployment (one contract per chain)
- ✅ Easier to maintain and upgrade
- ✅ Single contract address to configure
- ✅ Handles all path types automatically
- ✅ Works with all DEX protocols (V2, V3, Curve, Balancer, etc.)

**Contract Function:**
```solidity
function execute(
    uint8 flashSource,     // 1=Balancer, 2=Aave
    address token,         // Token to borrow
    uint256 amount,        // Amount to borrow
    bytes calldata data    // Encoded route data
) external
```

**Route Data Format:**
```solidity
// Encoded as: (protocols[], routers[], path[], extras[])
abi.encode(
    [PROTOCOL_UNISWAP_V2, PROTOCOL_SUSHISWAP],  // Protocol IDs
    [uniRouter, sushiRouter],                    // Router addresses
    [WETH, USDC, WETH],                          // Token path
    [bytes(""), bytes("")]                       // Extra data per hop
)
```

**Configuration:**
```bash
# .env file
EXECUTOR_ADDRESS=0xYourFlashArbExecutorAddress
FLASH_LOAN_PROVIDER=1  # 1=Balancer, 2=Aave
```

**When to Use:**
- Default choice for most users
- Production deployments
- Multi-chain operations
- When you want simplicity and flexibility

---

### **Approach 2: Specialized HFT + Router Contracts (ADVANCED)**

**Used by:** `execution/arbitrage_engine.js` (optional module)

**Description:** Deploy TWO separate contracts optimized for different scenarios.

**Contracts:**

#### 1. HFT Contract (High-Frequency Trading)
- **Purpose:** Gas-optimized for direct V2 pair swaps
- **Target:** Simple 2-hop arbitrage on Uniswap V2 forks
- **Flash Loans:** Bypasses routers (direct pool integration)
- **Gas Savings:** 30-50k gas compared to Router contract

**Function:**
```solidity
function startArbitrage(
    address poolA,      // V2 pair contract A
    address poolB,      // V2 pair contract B
    uint256 amount      // Amount to arbitrage
) external
```

**Example Address (Polygon):** `0xAF54D81835F811F1D4aB35c5856DDAE8834cdDA2`

#### 2. Router Contract
- **Purpose:** Flexible execution for complex paths
- **Target:** Multi-hop (3+ hops) and non-V2 protocols
- **Flash Loans:** Uses router contracts for swap execution
- **Compatibility:** Works with V2, V3, Curve, Balancer, etc.

**Function:**
```solidity
function startArbitrage(
    address[] path,      // Token path [A, B, C, A]
    address[] routers,   // Router addresses per hop
    uint256 amount       // Amount to arbitrage
) external
```

**Example Address (Polygon):** `0x4442782681b668365334C3D2A6F004F0760DA393`

**Decision Logic (ArbitrageEngine):**

The engine uses a 3-gate system to select the optimal contract:

1. **Gate 1 - Topology:** 
   - Path length > 2? → Use Router
   - Path length = 2? → Continue

2. **Gate 2 - Technology:**
   - Any V3/Curve/Balancer? → Use Router
   - All V2 compatible? → Continue

3. **Gate 3 - Gas Simulation:**
   - Simulate both contracts
   - Pick the cheaper option
   - Fallback to Router on error

**Configuration:**
```bash
# .env file
HFT_CONTRACT_ADDRESS=0xAF54D81835F811F1D4aB35c5856DDAE8834cdDA2
ROUTER_CONTRACT_ADDRESS=0x4442782681b668365334C3D2A6F004F0760DA393
```

**Usage Example:**
```javascript
const { ArbitrageEngine } = require('./execution/arbitrage_engine');

const engine = new ArbitrageEngine(provider, chainId);
const decision = await engine.selectExecutionEngine(opportunity);

// decision.target = HFT_CONTRACT or ROUTER_CONTRACT
// decision.payload = encoded function call
// decision.reason = "TOPOLOGY_CHECK" | "LIQUIDITY_CHECK" | "GAS_SIMULATION"
```

**When to Use:**
- High-volume trading operations
- Gas optimization is critical
- You have expertise in multi-contract management
- You're deploying specialized infrastructure

---

## 📊 Comparison Table

| Feature | Unified FlashArbExecutor | HFT + Router Contracts |
|---------|-------------------------|------------------------|
| **Deployment Complexity** | Low (1 contract) | High (2 contracts) |
| **Maintenance** | Easy | Complex |
| **Gas Efficiency** | Good | Optimal (HFT saves 30-50k) |
| **Path Types** | All (2-hop to N-hop) | HFT: 2-hop only; Router: N-hop |
| **DEX Support** | All protocols | HFT: V2 only; Router: All |
| **Integration** | Simple | Requires ArbitrageEngine |
| **Used By** | bot.js (main bot) | Custom implementations |
| **Recommended For** | Most users | Gas-sensitive specialists |

---

## 🔧 Implementation Details

### Unified FlashArbExecutor (bot.js)

The main bot uses a single executor contract with dynamic routing:

```javascript
// offchain/execution/bot.js

const EXECUTOR_ADDR = process.env.EXECUTOR_ADDRESS;
const contract = new ethers.Contract(
    EXECUTOR_ADDR, 
    ["function execute(uint8,address,uint256,bytes) external"], 
    wallet
);

// Encode route data
const routeData = ethers.AbiCoder.defaultAbiCoder().encode(
    ["uint8[]", "address[]", "address[]", "bytes[]"],
    [protocols, routers, path, extras]
);

// Execute with flash loan
const tx = await contract.execute(
    FLASH_LOAN_PROVIDER,  // 1=Balancer, 2=Aave
    token,
    amount,
    routeData
);
```

**Key Points:**
- One contract handles everything
- Route complexity determined by encoded data
- Flash loan provider configurable (Balancer/Aave)
- Used by 99% of Titan deployments

### HFT + Router Contracts (ArbitrageEngine)

The specialized approach uses a selector to pick the best contract:

```javascript
// execution/arbitrage_engine.js

class ArbitrageEngine {
    async selectExecutionEngine(opportunity) {
        // Gate 1: Check topology
        if (opportunity.path.length > 2) {
            return { target: ROUTER_CONTRACT, reason: "MULTI_HOP" };
        }
        
        // Gate 2: Check DEX compatibility
        if (!this.isV2Compatible(opportunity.exchanges)) {
            return { target: ROUTER_CONTRACT, reason: "NON_V2_DEX" };
        }
        
        // Gate 3: Simulate gas
        const [gasHFT, gasRouter] = await this.simulateGas(opportunity);
        if (gasHFT < gasRouter) {
            return { target: HFT_CONTRACT, reason: "GAS_OPTIMIZED" };
        }
        
        return { target: ROUTER_CONTRACT, reason: "DEFAULT" };
    }
}
```

**Key Points:**
- Requires two deployed contracts
- Automatic contract selection
- Gas simulation for optimization
- Only for specialized deployments

---

## 🚀 Quick Start

### For Most Users (Recommended)

1. Deploy FlashArbExecutor contract:
```bash
npx hardhat run scripts/deployFlashArbExecutor.js --network polygon
```

2. Configure .env:
```bash
EXECUTOR_ADDRESS=0xYourDeployedContractAddress
FLASH_LOAN_PROVIDER=1
FLASH_LOAN_ENABLED=true
```

3. Run bot:
```bash
node offchain/execution/bot.js
```

### For Advanced Users (HFT + Router)

1. Deploy both contracts
2. Configure .env:
```bash
HFT_CONTRACT_ADDRESS=0xYourHFTContract
ROUTER_CONTRACT_ADDRESS=0xYourRouterContract
```

3. Integrate ArbitrageEngine:
```javascript
const engine = require('./execution/arbitrage_engine');
// Use engine.selectExecutionEngine() in your custom bot
```

---

## ⚠️ Common Misconceptions

### ❌ "I need to use HFT and Router contracts"
**Reality:** The main bot (bot.js) uses the unified FlashArbExecutor. HFT and Router are optional specialized contracts for advanced deployments.

### ❌ "bot.js selects between HFT and Router"
**Reality:** bot.js uses ONE contract (EXECUTOR_ADDRESS). Only ArbitrageEngine.js selects between multiple contracts.

### ❌ "HFT contract is for flash loans"
**Reality:** BOTH contracts use flash loans. The difference is HOW they execute swaps (direct pools vs routers).

### ❌ "I should set all three addresses"
**Reality:** 
- For bot.js: Only set EXECUTOR_ADDRESS
- For ArbitrageEngine: Only set HFT_CONTRACT_ADDRESS and ROUTER_CONTRACT_ADDRESS

---

## 📚 Related Documentation

- **ARBITRAGE_ENGINE_README.md** - Detailed ArbitrageEngine documentation
- **FLASH_LOAN_ENFORCEMENT_SUMMARY.md** - Flash loan configuration guide
- **.env.example** - Complete environment variable reference
- **test/ArbitrageEngine.test.js** - ArbitrageEngine test suite
- **test/test_flash_loan_enforcement.js** - Flash loan validation tests

---

## 🔐 Flash Loan Requirements

**CRITICAL:** Regardless of which approach you use, ALL arbitrage is 100% flash-funded:

- ✅ Zero working capital required (only gas fees)
- ✅ Flash loans borrowed and repaid in same transaction
- ✅ Supported providers: Balancer V3, Aave V3
- ✅ Mandatory enforcement (bot exits if disabled)

**Configuration:**
```bash
FLASH_LOAN_ENABLED=true      # MUST be true (enforced)
FLASH_LOAN_PROVIDER=1        # 1=Balancer, 2=Aave
```

---

## 💡 Choosing Your Approach

### Use Unified FlashArbExecutor if:
- ✅ You're setting up Titan for the first time
- ✅ You want simplicity and ease of maintenance
- ✅ You're deploying across multiple chains
- ✅ Gas optimization is good enough (not critical)
- ✅ You want the standard Titan experience

### Use HFT + Router Contracts if:
- ✅ You're running high-volume operations
- ✅ Gas costs are critically important (saving 30-50k gas/tx matters)
- ✅ You have experience managing multiple contracts
- ✅ You're building custom trading infrastructure
- ✅ You want to squeeze out every bit of performance

### Default Recommendation
**→ Use Unified FlashArbExecutor (Approach 1)**

Most users should start with the unified approach. You can always migrate to specialized contracts later if you need the gas optimization.

---

## 📞 Support

For questions about executor contracts:
- Review this guide and related documentation
- Check test files for usage examples
- Consult .env.example for configuration options

---

**Last Updated:** 2026-01-29
**Version:** Titan 2.0
