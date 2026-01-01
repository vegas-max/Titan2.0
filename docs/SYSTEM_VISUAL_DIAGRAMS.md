# Titan System Visual Diagrams

This document provides visual representations of the Titan system architecture, enum registry, and token design.

---

## 1. System Architecture Overview

```
╔══════════════════════════════════════════════════════════════════════════╗
║                     TITAN ARBITRAGE SYSTEM ARCHITECTURE                   ║
╚══════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────┐
│                         OFF-CHAIN COMPONENTS                              │
└──────────────────────────────────────────────────────────────────────────┘

    ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
    │   Python    │      │ Aggregator  │      │    Route    │
    │    Brain    │─────▶│  Selector   │─────▶│   Builder   │
    │             │      │             │      │             │
    │ • ML Model  │      │ • DEX pick  │      │ • Encoding  │
    │ • Signals   │      │ • Routing   │      │ • Payload   │
    └─────────────┘      └─────────────┘      └──────┬──────┘
                                                      │
                                                      │ Transaction
                                                      ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                         ON-CHAIN COMPONENTS                               │
└──────────────────────────────────────────────────────────────────────────┘

    ┌───────────────────────────────────────────────────────────────┐
    │                    OmniArbExecutor.sol                         │
    │  ┌──────────────────────────────────────────────────────┐    │
    │  │              execute(flashSource, token, amount,     │    │
    │  │                      routeData)                       │    │
    │  └───────────────────────┬──────────────────────────────┘    │
    │                          │                                     │
    │         ┌────────────────┴────────────────┐                   │
    │         ▼                                 ▼                   │
    │  ┌─────────────┐                 ┌─────────────┐             │
    │  │  Aave V3    │                 │ Balancer V3 │             │
    │  │  Flashloan  │                 │   Unlock    │             │
    │  └──────┬──────┘                 └──────┬──────┘             │
    │         │                               │                     │
    │         └────────────┬──────────────────┘                     │
    │                      ▼                                        │
    │         ┌────────────────────────┐                            │
    │         │    _runRoute()         │                            │
    │         │  (Hop-by-Hop Execute)  │                            │
    │         └────────────┬───────────┘                            │
    │                      │                                        │
    │         ┌────────────┴────────────┐                           │
    │         │     SwapHandler         │                           │
    │         │   (Swap Primitive)      │                           │
    │         │                         │                           │
    │         │  Protocol 1: UniV2      │                           │
    │         │  Protocol 2: UniV3      │                           │
    │         │  Protocol 3: Curve      │                           │
    │         └─────────────────────────┘                           │
    └───────────────────────────────────────────────────────────────┘

    ┌───────────────────────────────────────────────────────────────┐
    │                   OmniArbDecoder.sol                           │
    │                                                                │
    │  • Chain Enum Validation (A-J)                                │
    │  • Token Rank Resolution                                       │
    │  • USDC Normalization                                          │
    │  • Payload Validation                                          │
    └───────────────────────────────────────────────────────────────┘
```

---

## 2. Enum Registry Hierarchy

```
╔══════════════════════════════════════════════════════════════════════════╗
║                        ENUM REGISTRY SYSTEM                               ║
╚══════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────┐
│                      CHAIN ENUM LAYER (A-J)                               │
└──────────────────────────────────────────────────────────────────────────┘

       A          B          C          D          E
   ┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐
   │Ethereum││Polygon ││  Base  ││Arbitrum││Optimism│
   │  (1)   ││ (137)  ││ (8453) ││(42161) ││  (10)  │
   └────────┘└────────┘└────────┘└────────┘└────────┘

       F          G          H          I          J
   ┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐
   │Avalanche│ Fantom │ Gnosis │  Celo  │ Linea  │
   │(43114) ││ (250)  ││ (100)  ││(42220) ││(59144) │
   └────────┘└────────┘└────────┘└────────┘└────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                      TOKEN RANK LAYER (Ranges)                            │
└──────────────────────────────────────────────────────────────────────────┘

  Chain A (Ethereum)          Chain B (Polygon)         Chain C (Base)
  ┌──────────────┐           ┌──────────────┐          ┌──────────────┐
  │ 1000-1999    │           │ 2000-2999    │          │ 3000-3999    │
  │              │           │              │          │              │
  │ 1000: WETH   │           │ 2000: WMATIC │          │ 3000: WETH   │
  │ 1001: USDC   │           │ 2001: WETH   │          │ 3001: USDC   │
  │ 1002: USDT   │           │ 2002: USDC   │          │ 3002: USDT   │
  │ 1003: DAI    │           │ 2003: USDC.e │          │ 3003: DAI    │
  │ 1004: WBTC   │           │ 2004: USDT   │          │ ...          │
  │ ...          │           │ ...          │          │              │
  └──────────────┘           └──────────────┘          └──────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                       DEX REGISTRY LAYER                                  │
└──────────────────────────────────────────────────────────────────────────┘

  Per-Chain DEX Registry: dexRouter[chainId][dexId] → address

  Polygon (137):
  ┌────┬──────────────┬──────────────────────────────────────────┐
  │ ID │    DEX       │           Router Address                 │
  ├────┼──────────────┼──────────────────────────────────────────┤
  │ 0  │ UNISWAP_V2   │ 0x... (Quickswap Router)                │
  │ 1  │ UNISWAP_V3   │ 0x... (UniV3 SwapRouter)                │
  │ 2  │ CURVE        │ 0x... (Curve Pool Address)              │
  │ 3  │ SUSHISWAP    │ 0x... (Sushi Router)                    │
  └────┴──────────────┴──────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                      TOKEN REGISTRY LAYER                                 │
└──────────────────────────────────────────────────────────────────────────┘

  tokenRegistry[chain][tokenId][tokenType] → address

  Example: Polygon (Chain.POLYGON)
  ┌─────────┬──────────────┬────────────────────────────────────┐
  │ TokenId │  TokenType   │        Address                     │
  ├─────────┼──────────────┼────────────────────────────────────┤
  │ WMATIC  │ WRAPPED (2)  │ 0x0d500B1d8E8eF31E21C99d1Db9A6444d│
  │ USDC    │ CANONICAL(0) │ 0x2791Bca1f2de4661ED88A30C99A7a94│
  │ USDC    │ BRIDGED (1)  │ 0x... (USDC.e)                    │
  │ WETH    │ BRIDGED (1)  │ 0x7ceB23fD6bC0adD59E62ac25578270c│
  └─────────┴──────────────┴────────────────────────────────────┘
```

---

## 3. Token Design Flow

```
╔══════════════════════════════════════════════════════════════════════════╗
║                        TOKEN RESOLUTION FLOW                              ║
╚══════════════════════════════════════════════════════════════════════════╝

TWO SYSTEMS: OmniArbDecoder (A-J + Rank) vs OmniArbExecutor (Enum + Type)

┌──────────────────────────────────────────────────────────────────────────┐
│            SYSTEM 1: OmniArbDecoder (A-J Token Ranks)                    │
└──────────────────────────────────────────────────────────────────────────┘

  Input: chainEnum (A-J) + tokenRank (uint16)
         ↓
  Step 1: Validate chainEnum matches current chain
         A-J → Chain ID lookup
         ↓
  Step 2: Resolve token address from rank
         tokenRank → rankToToken[tokenRank]
         ↓
  Step 3: Apply USDC normalization
         If bridged USDC → return canonical USDC
         Else → return original token
         ↓
  Output: Token Address

  Example (Polygon):
    Input:  chainEnum = 'B', tokenRank = 2003
    Step 1: 'B' → 137 (Polygon) ✓
    Step 2: 2003 → 0x... (USDC.e address)
    Step 3: USDC.e → 0x... (Canonical USDC)
    Output: Canonical USDC address

┌──────────────────────────────────────────────────────────────────────────┐
│            SYSTEM 2: OmniArbExecutor (Token Enum + Type)                 │
└──────────────────────────────────────────────────────────────────────────┘

  Input: chain (enum), tokenId (enum), tokenType (enum)
         ↓
  Step 1: Get current chain from block.chainid
         block.chainid → Chain enum
         ↓
  Step 2: Resolve token address from registry
         tokenRegistry[chain][tokenId][tokenType] → address
         ↓
  Output: Token Address

  Example (Polygon):
    Input:  tokenId = Token.USDC, tokenType = TokenType.BRIDGED
    Step 1: block.chainid = 137 → Chain.POLYGON
    Step 2: tokenRegistry[POLYGON][USDC][BRIDGED] → 0x... (USDC.e)
    Output: USDC.e address
```

---

## 4. Route Execution Flow

```
╔══════════════════════════════════════════════════════════════════════════╗
║                         ROUTE EXECUTION FLOW                              ║
╚══════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────┐
│  Example: 3-Hop Arbitrage Route on Polygon                               │
│  Loan: 10,000 USDT                                                       │
└──────────────────────────────────────────────────────────────────────────┘

         Flashloan Borrow
         10,000 USDT
              │
              ▼
    ┌─────────────────────┐
    │  Hop 1: UniV2       │
    │  USDT → WMATIC      │
    │  Protocol: 1        │
    │  Router: Quickswap  │
    │  Extra: 0x          │
    └──────────┬──────────┘
               │ Output: X WMATIC
               ▼
    ┌─────────────────────┐
    │  Hop 2: UniV3       │
    │  WMATIC → USDC      │
    │  Protocol: 2        │
    │  Router: UniV3      │
    │  Extra: fee=500     │
    └──────────┬──────────┘
               │ Output: Y USDC
               ▼
    ┌─────────────────────┐
    │  Hop 3: Curve       │
    │  USDC → USDT        │
    │  Protocol: 3        │
    │  Pool: Aave Pool    │
    │  Extra: i=0, j=1    │
    └──────────┬──────────┘
               │ Output: Z USDT
               ▼
         Repay Flashloan
         10,000 USDT + Fee
              │
              ▼
         Profit = Z - (10,000 + Fee)
         (Retained in contract)

Token Flow:
  currentToken = loanToken (USDT)
  └→ Hop 1: currentToken → tokenOutPath[0] (WMATIC)
     └→ Hop 2: currentToken → tokenOutPath[1] (USDC)
        └→ Hop 3: currentToken → tokenOutPath[2] (USDT)
           └→ finalToken = USDT
```

---

## 5. Dual Encoding Modes

```
╔══════════════════════════════════════════════════════════════════════════╗
║                    RAW_ADDRESSES vs REGISTRY_ENUMS                        ║
╚══════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────┐
│                MODE 0: RAW_ADDRESSES (Explicit)                           │
└──────────────────────────────────────────────────────────────────────────┘

  Payload Structure:
  ┌──────────────────────────────────────────────────────────────┐
  │ RouteEncoding: 0 (RAW_ADDRESSES)                             │
  ├──────────────────────────────────────────────────────────────┤
  │ protocols:      [1, 2, 3]         (uint8[])                  │
  │ routersOrPools: [0xAAA..., 0xBBB..., 0xCCC...] (address[])  │
  │ tokenOutPath:   [0xDDD..., 0xEEE..., 0xFFF...] (address[])  │
  │ extra:          [0x, feeBytes, indicesBytes]   (bytes[])     │
  └──────────────────────────────────────────────────────────────┘
                           ↓
  On-Chain Processing:
  ┌──────────────────────────────────────────────────────────────┐
  │ Direct Usage (No Registry Lookup)                            │
  │ • Use provided router addresses directly                     │
  │ • Use provided token addresses directly                      │
  │ • Fast execution                                             │
  └──────────────────────────────────────────────────────────────┘

  Pros: ✓ Faster execution        Cons: ✗ Larger calldata
        ✓ No registry setup              ✗ No centralized control
        ✓ Flexible addresses             ✗ Address changes need new tx

┌──────────────────────────────────────────────────────────────────────────┐
│                MODE 1: REGISTRY_ENUMS (Resolved)                          │
└──────────────────────────────────────────────────────────────────────────┘

  Payload Structure:
  ┌──────────────────────────────────────────────────────────────┐
  │ RouteEncoding: 1 (REGISTRY_ENUMS)                            │
  ├──────────────────────────────────────────────────────────────┤
  │ protocols:       [1, 2, 3]       (uint8[])                   │
  │ dexIds:          [0, 1, 2]       (uint8[])                   │
  │ tokenOutIds:     [4, 1, 2]       (uint8[])                   │
  │ tokenOutTypes:   [0, 0, 0]       (uint8[])                   │
  │ extra:           [0x, feeBytes, indicesBytes] (bytes[])      │
  └──────────────────────────────────────────────────────────────┘
                           ↓
  On-Chain Processing:
  ┌──────────────────────────────────────────────────────────────┐
  │ Registry Lookup Required                                      │
  │ • router = dexRouter[chainId][dexId]                         │
  │ • token = tokenRegistry[chainId][tokenId][tokenType]         │
  │ • Centralized management                                     │
  └──────────────────────────────────────────────────────────────┘

  Pros: ✓ Smaller calldata        Cons: ✗ Registry setup needed
        ✓ Centralized governance         ✗ Slightly slower (lookup)
        ✓ Easy address updates           ✗ Registry must be maintained
```

---

## 6. Token Type Classification

```
╔══════════════════════════════════════════════════════════════════════════╗
║                      TOKEN TYPE CLASSIFICATION                            ║
╚══════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────┐
│                        Type 0: CANONICAL                                  │
│                     (Native to the chain)                                 │
└──────────────────────────────────────────────────────────────────────────┘

  Examples:
    Ethereum:  USDC, USDT, DAI (originated on Ethereum)
    Polygon:   Native Polygon USDC (Circle-issued)
    Arbitrum:  Native Arbitrum USDC (Circle-issued)
    Base:      Native Base USDC (Circle-issued)

  Characteristics:
    ✓ Highest liquidity
    ✓ Most trusted
    ✓ Direct issuance
    ✓ Primary trading pairs

┌──────────────────────────────────────────────────────────────────────────┐
│                        Type 1: BRIDGED                                    │
│                   (Bridged from another chain)                            │
└──────────────────────────────────────────────────────────────────────────┘

  Examples:
    Polygon:   USDC.e (bridged from Ethereum), WETH (bridged)
    Arbitrum:  USDC.e (bridged from Ethereum)
    Optimism:  USDC.e (bridged from Ethereum)
    Avalanche: USDC.e (bridged from Ethereum)

  Characteristics:
    ⚠ Lower liquidity than canonical
    ⚠ Depends on bridge security
    ⚠ May trade at slight discount
    ⚠ Migration path to canonical

┌──────────────────────────────────────────────────────────────────────────┐
│                        Type 2: WRAPPED                                    │
│                  (Wrapped native gas token)                               │
└──────────────────────────────────────────────────────────────────────────┘

  Examples:
    Ethereum:  WETH (Wrapped ETH)
    Polygon:   WMATIC (Wrapped MATIC)
    BSC:       WBNB (Wrapped BNB)
    Avalanche: WAVAX (Wrapped AVAX)
    Fantom:    WFTM (Wrapped FTM)

  Characteristics:
    ✓ 1:1 peg with native token
    ✓ ERC20 compatible
    ✓ Highest liquidity
    ✓ Most trading pairs

USDC Normalization Example:
  ┌───────────────────────────────────────────────────┐
  │  Polygon: USDC.e (BRIDGED) → USDC (CANONICAL)    │
  │  Reason: Prevent mixing non-fungible variants     │
  └───────────────────────────────────────────────────┘
```

---

## 7. Security Architecture

```
╔══════════════════════════════════════════════════════════════════════════╗
║                        SECURITY ARCHITECTURE                              ║
╚══════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────┐
│                      MULTI-LAYER SECURITY MODEL                           │
└──────────────────────────────────────────────────────────────────────────┘

Layer 1: Access Control
├─ Owner-only execution (Ownable)
├─ Owner-only registry configuration
└─ Emergency withdrawal functions

Layer 2: Validation
├─ Chain enum validation (must match current chain)
├─ Token rank validation (must be configured)
├─ Expiry validation (timestamp check)
├─ Nonce uniqueness (prevent replay)
├─ Route registry hash verification (optional)
└─ Profit validation (minProfitBps check)

Layer 3: Flashloan Security
├─ Callback authentication (validate msg.sender)
├─ Reentrancy guard (ReentrancyGuard)
└─ Profit validation (ensure repayment + profit)

Layer 4: Token Security
├─ SafeERC20 usage (safe transfers)
├─ Zero address checks
├─ USDC normalization (prevent variant mixing)
└─ Token type validation

Layer 5: Execution Security
├─ Array length validation (all arrays must match)
├─ Zero amount checks (validate swap outputs)
├─ Route length limits (max 5 hops)
├─ Slippage protection (deadline parameter)
└─ Gas optimization (avoid excessive operations)

Immutability Guarantees:
┌────────────────────────────────────────────────────────┐
│ NEVER CHANGE:                                          │
│ • Chain enum letters (A-J mapping)                    │
│ • Enum value ordering (declaration order = value)     │
│ • Token rank ranges (1000-1999, 2000-2999, ...)       │
│ • STATIC_ORDER sequence (append only, never reorder)  │
└────────────────────────────────────────────────────────┘
```

---

## 8. End-to-End Operational Data Flow

```
╔══════════════════════════════════════════════════════════════════════════╗
║            TITAN PRODUCTION OPERATIONS: END-TO-END DATA FLOW              ║
╚══════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────┐
│                    PHASE 1: OFF-CHAIN OPPORTUNITY DISCOVERY               │
│                         (Python Brain / ML Layer)                         │
└──────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────┐
    │                      OmniBrain.py (Entry Point)                  │
    │  • Multi-threaded scanner (ThreadPoolExecutor)                   │
    │  • RustworkX graph construction (256+ nodes)                     │
    │  • Real-time blockchain monitoring via Web3                      │
    └───────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │                   Token Discovery & Inventory                     │
    │  • TokenDiscovery: Multi-chain token scanning                    │
    │  • DexPricer: Real-time price queries (UniV3, Curve, etc.)       │
    │  • BridgeOracle: Cross-chain price verification                  │
    └───────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │                    AI Analysis & Optimization                     │
    │  • MarketForecaster: Gas price prediction                        │
    │  • QLearningAgent: Strategy optimization                         │
    │  • FeatureStore: Historical pattern analysis                     │
    └───────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │                     Profit Calculation Engine                     │
    │  Π_net = V_loan × [(P_A × (1-S_A)) - (P_B × (1+S_B))]            │
    │          - F_flat - (V_loan × F_rate)                            │
    │                                                                   │
    │  Legend:                                                          │
    │  • Π_net: Net profit after fees                                   │
    │  • V_loan: Notional loan volume                                  │
    │  • P_A, P_B: Asset prices on exchange A and B                     │
    │  • S_A, S_B: Effective slippage fractions on exchanges A and B    │
    │  • F_flat: Flat operational/bridge fee (in USD-equivalent)       │
    │  • F_rate: Proportional fee rate applied to V_loan               │
    │                                                                   │
    │  Input Parameters:                                                │
    │  • amount: Loan amount                                           │
    │  • amount_out: Expected output (simulated)                       │
    │  • bridge_fee_usd: Cross-chain bridge fees                       │
    │  • gas_cost_usd: Estimated gas costs                             │
    │                                                                   │
    │  Output (Expected):                                               │
    │  • net_profit: Final profit after all costs                      │
    │  • gross_spread: Revenue - Loan cost                             │
    │  • total_fees: Sum of all operational costs                      │
    │  • is_profitable: Boolean (profit > MIN_PROFIT_USD)              │
    └───────────────────────────┬──────────────────────────────────────┘
                                │ IF is_profitable == True
                                ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │                 Signal Generation & Serialization                 │
    │  File: signals/outgoing/{timestamp}-{token}-{chain}.json         │
    │                                                                   │
    │  Signal Structure (JSON):                                         │
    │  {                                                                │
    │    "type": "intra-chain" | "cross-chain",                        │
    │    "chainId": 137,                                               │
    │    "token": "USDC",                                              │
    │    "amount": "10000.00",                                         │
    │    "expectedProfit": "7.23",                                     │
    │    "route": {                                                    │
    │      "protocols": [1, 2, 3],  // Protocol IDs                   │
    │      "dexs": [...],            // DEX routers                    │
    │      "tokenPath": [...],       // Token swap path                │
    │      "extra": [...]            // Protocol-specific params       │
    │    },                                                            │
    │    "gasEstimate": "285000",                                      │
    │    "timestamp": 1704067200                                       │
    │  }                                                               │
    └───────────────────────────┬──────────────────────────────────────┘
                                │
                                │ File-based message passing
                                ▼

┌──────────────────────────────────────────────────────────────────────────┐
│                    PHASE 2: OFF-CHAIN EXECUTION LAYER                     │
│                      (Node.js Bot / Execution Engine)                     │
└──────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────────────┐
    │                    TitanBot.js (Signal Watcher)                   │
    │  • File system watcher (1-second polling)                        │
    │  • Reads signals/outgoing/*.json                                 │
    │  • Deduplication via processedSignals Set                        │
    └───────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │                      Execution Mode Router                        │
    │                                                                   │
    │  Mode Selection (TITAN_EXECUTION_MODE):                          │
    │                                                                   │
    │  ┌─────────────────┐              ┌─────────────────┐           │
    │  │  PAPER MODE     │              │   LIVE MODE     │           │
    │  │  (Simulation)   │              │  (Production)   │           │
    │  ├─────────────────┤              ├─────────────────┤           │
    │  │ • No blockchain │              │ • Real txs      │           │
    │  │ • No gas costs  │              │ • Real gas      │           │
    │  │ • Validate logic│              │ • Real profit   │           │
    │  │ • Track metrics │              │ • MEV protected │           │
    │  │                 │              │                 │           │
    │  │ Return:         │              │ (Continue to    │           │
    │  │ • Simulated P/L │              │  validation)    │           │
    │  │ • Validation ✓  │              │                 │           │
    │  └─────────────────┘              └────────┬────────┘           │
    └─────────────────────────────────────────────┼────────────────────┘
                                                  │ (LIVE mode only)
                                                  ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │                  Pre-Execution Validation Layer                   │
    │                                                                   │
    │  1. Wallet Balance Check:                                        │
    │     • provider.getBalance(EXECUTOR_ADDRESS)                      │
    │     • Ensure sufficient gas funds                                │
    │                                                                   │
    │  2. Gas Price Validation (GasManager):                           │
    │     • Current base fee < MAX_BASE_FEE_GWEI                       │
    │     • EIP-1559 fee estimation                                    │
    │     • Network congestion check                                   │
    │                                                                   │
    │  3. On-Chain Simulation (OmniSDKEngine):                         │
    │     • eth_call simulation                                        │
    │     • Validate route execution                                   │
    │     • Verify profitability                                       │
    │                                                                   │
    │  4. Aggregator Selection (if applicable):                        │
    │     • AggregatorSelector.selectBestRoute()                       │
    │     • Compare: Li.Fi, 1inch, ParaSwap, 0x, CoW, etc.            │
    │     • Pick lowest-cost, highest-profit route                     │
    │                                                                   │
    │  Return (Produced):                                               │
    │  • validationSuccess: true/false                                 │
    │  • simulatedProfit: Actual expected profit                       │
    │  • gasEstimate: Updated gas estimate                             │
    │  • optimalRoute: Best execution path                             │
    └───────────────────────────┬──────────────────────────────────────┘
                                │ IF validationSuccess == true
                                ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │                    Payload Construction Layer                     │
    │                                                                   │
    │  Route Encoding (per RouteEncodingSpec.md):                      │
    │                                                                   │
    │  Option A: RAW_ADDRESSES (Mode 0)                                │
    │  ┌────────────────────────────────────────────────────────┐     │
    │  │ routeData = abi.encode(                                │     │
    │  │   ["uint8", "uint8[]", "address[]", "address[]",       │     │
    │  │    "bytes[]"],                                         │     │
    │  │   [0, protocols, routers, tokenPath, extra]            │     │
    │  │ )                                                      │     │
    │  └────────────────────────────────────────────────────────┘     │
    │                                                                   │
    │  Option B: REGISTRY_ENUMS (Mode 1)                               │
    │  ┌────────────────────────────────────────────────────────┐     │
    │  │ routeData = abi.encode(                                │     │
    │  │   ["uint8", "uint8[]", "uint8[]", "uint8[]",           │     │
    │  │    "uint8[]", "bytes[]"],                              │     │
    │  │   [1, protocols, dexIds, tokenIds, tokenTypes, extra]  │     │
    │  │ )                                                      │     │
    │  └────────────────────────────────────────────────────────┘     │
    │                                                                   │
    │  Transaction Parameters:                                          │
    │  • flashSource: 0 (Aave V3) | 1 (Balancer V3)                   │
    │  • loanToken: Token address for flashloan                        │
    │  • loanAmount: Loan amount in token units                        │
    │  • routeData: Encoded route (above)                              │
    │                                                                   │
    │  Output (Import):                                                 │
    │  • txRequest: Populated transaction object                       │
    │  • gasLimit: Calculated gas limit                                │
    │  • maxFeePerGas: EIP-1559 max fee                                │
    │  • maxPriorityFeePerGas: Priority fee                            │
    └───────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │                    Transaction Signing Layer                      │
    │                                                                   │
    │  const wallet = new ethers.Wallet(PRIVATE_KEY, provider);        │
    │  const signedTx = await wallet.signTransaction(txRequest);       │
    │                                                                   │
    │  Signed Transaction Components:                                   │
    │  • nonce: Account nonce                                          │
    │  • to: Contract address (OmniArbExecutor)                        │
    │  • data: Encoded function call                                   │
    │  • gasLimit: Maximum gas                                         │
    │  • maxFeePerGas: EIP-1559 max fee                                │
    │  • maxPriorityFeePerGas: Priority fee                            │
    │  • chainId: Network chain ID                                     │
    │  • v, r, s: ECDSA signature components                           │
    │                                                                   │
    │  Output:                                                          │
    │  • signedTx: Signed transaction (RLP encoded)                    │
    │  Usage: Submitted to Transaction Broadcast Layer                  │
    └───────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │                 Transaction Broadcast Layer                       │
    │                                                                   │
    │  Path Selection (MEV Protection):                                │
    │                                                                   │
    │  IF (gasCostHigh && profitLarge):                                │
    │    ┌────────────────────────────────────────────┐               │
    │    │     BloxRoute Private Mempool               │               │
    │    │  • Bundle submission                        │               │
    │    │  • MEV protection                           │               │
    │    │  • Frontrun prevention                      │               │
    │    │  await bloxRoute.submitBundle([signedTx])   │               │
    │    └────────────────────────────────────────────┘               │
    │  ELSE:                                                           │
    │    ┌────────────────────────────────────────────┐               │
    │    │     Standard Public Mempool                 │               │
    │    │  • Direct RPC submission                    │               │
    │    │  • Lower latency                            │               │
    │    │  • Standard propagation                     │               │
    │    │  await wallet.sendTransaction(txRequest)    │               │
    │    └────────────────────────────────────────────┘               │
    │                                                                   │
    │  Broadcast Output:                                                │
    │  • txHash: Transaction hash (0x...)                              │
    │  • timestamp: Submission time                                    │
    │  • blockNumber: Target block (estimated)                         │
    └───────────────────────────┬──────────────────────────────────────┘
                                │ TX broadcast to network
                                ▼

┌──────────────────────────────────────────────────────────────────────────┐
│                    PHASE 3: ON-CHAIN EXECUTION                            │
│                        (Smart Contract Layer)                             │
└──────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────────────┐
    │              Mempool → Block Inclusion → Execution                │
    │                                                                   │
    │  1. Mempool Queue:                                               │
    │     • Transaction enters mempool                                 │
    │     • Miners/validators select based on gas price                │
    │     • Sorted by maxPriorityFeePerGas                             │
    │                                                                   │
    │  2. Block Inclusion:                                             │
    │     • Transaction included in block                              │
    │     • Block validated and propagated                             │
    │     • EVM execution begins                                       │
    └───────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │          OmniArbExecutor.sol - execute() Entry Point              │
    │                                                                   │
    │  function execute(                                                │
    │      uint8 flashSource,    // 0=Aave, 1=Balancer                │
    │      address loanToken,    // Token to borrow                    │
    │      uint256 loanAmount,   // Amount to borrow                   │
    │      bytes calldata routeData  // Encoded route                  │
    │  ) external onlyOwner nonReentrant                               │
    │                                                                   │
    │  Security Checks:                                                 │
    │  • onlyOwner: Only contract owner can execute                    │
    │  • nonReentrant: Prevents reentrancy attacks                     │
    │  • Validates flashSource (0 or 1)                                │
    └───────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │                    Flashloan Initiation                           │
    │                                                                   │
    │  IF flashSource == 0 (Aave V3):                                  │
    │  ┌────────────────────────────────────────────────────────┐     │
    │  │ IPool(AAVE_POOL).flashLoanSimple(                      │     │
    │  │   address(this),    // Receiver                        │     │
    │  │   loanToken,        // Asset                           │     │
    │  │   loanAmount,       // Amount                          │     │
    │  │   routeData,        // Params                          │     │
    │  │   0                 // Referral code                   │     │
    │  │ )                                                      │     │
    │  │                                                         │     │
    │  │ → Callback: executeOperation()                         │     │
    │  └────────────────────────────────────────────────────────┘     │
    │                                                                   │
    │  IF flashSource == 1 (Balancer V3):                              │
    │  ┌────────────────────────────────────────────────────────┐     │
    │  │ IVault(BALANCER_VAULT).unlock(                         │     │
    │  │   abi.encodeCall(                                      │     │
    │  │     this.unlockCallback,                               │     │
    │  │     (loanToken, loanAmount, routeData)                 │     │
    │  │   )                                                    │     │
    │  │ )                                                      │     │
    │  │                                                         │     │
    │  │ → Callback: unlockCallback()                           │     │
    │  └────────────────────────────────────────────────────────┘     │
    │                                                                   │
    │  Loan Received:                                                   │
    │  • loanToken transferred to contract                             │
    │  • startBalance = IERC20(loanToken).balanceOf(address(this))    │
    └───────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │                     Route Decoding & Parsing                      │
    │                                                                   │
    │  Decode routeData based on encoding mode:                        │
    │                                                                   │
    │  IF encodingMode == 0 (RAW_ADDRESSES):                           │
    │  • Extract: protocols, routers, tokenPath, extra                 │
    │  • Use addresses directly (no registry lookup)                   │
    │                                                                   │
    │  IF encodingMode == 1 (REGISTRY_ENUMS):                          │
    │  • Extract: protocols, dexIds, tokenIds, tokenTypes, extra       │
    │  • Resolve routers: dexRouter[chainId][dexId]                    │
    │  • Resolve tokens: tokenRegistry[chain][tokenId][tokenType]      │
    │                                                                   │
    │  Validation:                                                      │
    │  • Require all arrays have matching lengths                      │
    │  • Require at least one hop (protocols.length > 0)               │
    │  • Require tokenPath.length == protocols.length + 1             │
    └───────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │                   Hop-by-Hop Route Execution                      │
    │                     (SwapHandler.sol Module)                      │
    │                                                                   │
    │  FOR each hop in route:                                          │
    │  ┌────────────────────────────────────────────────────────┐     │
    │  │ Hop i: currentToken → tokenOut                         │     │
    │  │                                                         │     │
    │  │ 1. Get current balance:                                │     │
    │  │    amountIn = IERC20(currentToken).balanceOf(this)     │     │
    │  │                                                         │     │
    │  │ 2. Approve DEX router:                                 │     │
    │  │    IERC20(currentToken).approve(router, amountIn)      │     │
    │  │                                                         │     │
    │  │ 3. Execute swap based on protocol:                     │     │
    │  │                                                         │     │
    │  │    Protocol 1 (UniV2):                                 │     │
    │  │    • swapExactTokensForTokens(amountIn, ...)           │     │
    │  │                                                         │     │
    │  │    Protocol 2 (UniV3):                                 │     │
    │  │    • exactInputSingle(params)                          │     │
    │  │    • Decode fee from extra[i]                          │     │
    │  │                                                         │     │
    │  │    Protocol 3 (Curve):                                 │     │
    │  │    • exchange(i, j, amountIn, minOut)                  │     │
    │  │    • Decode indices from extra[i]                      │     │
    │  │                                                         │     │
    │  │ 4. Verify output:                                      │     │
    │  │    amountOut = IERC20(tokenOut).balanceOf(this)        │     │
    │  │    require(amountOut > 0, "Zero output")               │     │
    │  │                                                         │     │
    │  │ 5. Update currentToken = tokenOut                      │     │
    │  └────────────────────────────────────────────────────────┘     │
    │  END FOR                                                         │
    │                                                                   │
    │  Final State:                                                     │
    │  • currentToken = original loanToken (for intra-chain circular   │
    │    arbitrage routes)                                             │
    │  • finalBalance > startBalance (profit condition)                │
    └───────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │                 Flashloan Repayment & Profit Lock                 │
    │                                                                   │
    │  1. Calculate amounts:                                           │
    │     finalBalance = IERC20(loanToken).balanceOf(address(this))    │
    │     owed = loanAmount + flashFee                                 │
    │                                                                   │
    │  2. Validate profitability:                                      │
    │     require(finalBalance >= owed, "Insufficient return")         │
    │     profit = finalBalance - owed                                 │
    │                                                                   │
    │  3. Repay flashloan:                                             │
    │     IF Aave V3:                                                  │
    │       • IERC20(loanToken).approve(AAVE_POOL, owed)               │
    │       • Aave automatically pulls repayment                       │
    │     IF Balancer V3:                                              │
    │       • vault.settle(loanToken, owed)                            │
    │       • Balancer handles transient debt settlement               │
    │                                                                   │
    │  4. Profit retention:                                            │
    │     • Profit remains in contract                                 │
    │     • Owner can withdraw via withdraw() function                 │
    │                                                                   │
    │  5. Emit event:                                                  │
    │     emit ArbitrageExecuted(                                      │
    │       flashSource,                                               │
    │       loanToken,                                                 │
    │       loanAmount,                                                │
    │       profit                                                     │
    │     );                                                           │
    │                                                                   │
    │  Transaction Outcome:                                             │
    │  • SUCCESS: Transaction confirmed, profit locked                 │
    │  • REVERT: Transaction fails, gas fees still charged             │
    └───────────────────────────┬──────────────────────────────────────┘
                                │ Transaction finalized
                                ▼

┌──────────────────────────────────────────────────────────────────────────┐
│                  PHASE 4: POST-EXECUTION MONITORING                       │
│                      (Off-Chain Confirmation Layer)                       │
└──────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────────────┐
    │                  Transaction Confirmation Watcher                 │
    │                                                                   │
    │  const receipt = await tx.wait(1);  // Wait 1 confirmation       │
    │                                                                   │
    │  Receipt Analysis:                                                │
    │  • receipt.status: 1 (success) | 0 (failure)                     │
    │  • receipt.gasUsed: Actual gas consumed                          │
    │  • receipt.effectiveGasPrice: Actual gas price paid              │
    │  • receipt.logs: Event logs (ArbitrageExecuted)                  │
    │  • receipt.blockNumber: Inclusion block                          │
    │  • receipt.transactionHash: Final tx hash                        │
    └───────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │                   Profit/Loss Calculation (Produced)              │
    │                                                                   │
    │  IF receipt.status == 1 (SUCCESS):                               │
    │  ┌────────────────────────────────────────────────────────┐     │
    │  │ Parse ArbitrageExecuted event:                         │     │
    │  │ • actualProfit = event.profit                          │     │
    │  │                                                         │     │
    │  │ Calculate real costs:                                  │     │
    │  │ • actualGasCost = gasUsed × effectiveGasPrice          │     │
    │  │ • actualGasCostUSD = gasCost × ethPriceUSD             │     │
    │  │                                                         │     │
    │  │ Net result:                                            │     │
    │  │ • netProfitUSD = actualProfit - actualGasCostUSD       │     │
    │  │ • profitMargin = (netProfit / loanAmount) × 100        │     │
    │  │                                                         │     │
    │  │ Return (Produced):                                     │     │
    │  │ {                                                      │     │
    │  │   success: true,                                       │     │
    │  │   txHash: "0x...",                                     │     │
    │  │   profit: actualProfit,                                │     │
    │  │   netProfitUSD: 7.23,                                  │     │
    │  │   gasCostUSD: 2.15,                                    │     │
    │  │   gasUsed: 285000,                                     │     │
    │  │   blockNumber: 12345678,                               │     │
    │  │   executionTime: "2.3s",                               │     │
    │  │   mode: "LIVE"                                         │     │
    │  │ }                                                      │     │
    │  └────────────────────────────────────────────────────────┘     │
    │                                                                   │
    │  IF receipt.status == 0 (FAILURE):                               │
    │  ┌────────────────────────────────────────────────────────┐     │
    │  │ Return (Produced):                                     │     │
    │  │ {                                                      │     │
    │  │   success: false,                                      │     │
    │  │   txHash: "0x...",                                     │     │
    │  │   profit: 0,                                           │     │
    │  │   netProfitUSD: -actualGasCostUSD,  // Loss           │     │
    │  │   gasCostUSD: 2.15,                                    │     │
    │  │   error: "Transaction reverted",                       │     │
    │  │   blockNumber: 12345678,                               │     │
    │  │   mode: "LIVE"                                         │     │
    │  │ }                                                      │     │
    │  └────────────────────────────────────────────────────────┘     │
    └───────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │                   Logging & Metrics Recording                     │
    │                                                                   │
    │  Console Output:                                                  │
    │  • "✅ TX CONFIRMED: 0x... | Profit: $7.23 | Gas: $2.15"         │
    │  • "❌ TX FAILED: 0x... | Loss: $2.15 (gas only)"                │
    │                                                                   │
    │  File Output (signals/processed/):                               │
    │  • Move signal file from outgoing/ to processed/                 │
    │  • Append execution result to signal                             │
    │                                                                   │
    │  Metrics Tracking:                                                │
    │  • Update success rate counter                                   │
    │  • Update total profit counter                                   │
    │  • Update gas cost counter                                       │
    │  • Update execution time average                                 │
    │                                                                   │
    │  Circuit Breaker Check:                                           │
    │  • IF consecutive failures > 10 (configurable threshold):        │
    │    → Activate circuit breaker                                    │
    │    → Pause execution for 60 seconds (configurable backoff)       │
    │    → Alert operator                                              │
    └───────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │                    Feedback Loop to Brain                         │
    │                                                                   │
    │  Update AI Models (FeatureStore):                                │
    │  • Record actual profit vs expected profit                       │
    │  • Update gas price predictions (MarketForecaster)               │
    │  • Adjust strategy parameters (QLearningAgent)                   │
    │  • Update success rate by chain/protocol                         │
    │                                                                   │
    │  Strategy Optimization:                                           │
    │  • IF profitability declining:                                   │
    │    → Increase MIN_PROFIT_USD threshold                           │
    │    → Disable underperforming chains                              │
    │  • IF success rate high:                                         │
    │    → Lower MIN_PROFIT_USD (capture more opportunities)           │
    │    → Enable additional chains                                    │
    └──────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════
                          SUMMARY: KEY METRICS
═══════════════════════════════════════════════════════════════════════════

MODES:
├─ PAPER MODE: Simulation only, no blockchain execution
│  └─ Returns: Simulated profit, validation checks
└─ LIVE MODE: Real blockchain execution
   └─ Returns: Actual profit, gas costs, transaction hash

TASKS & RETURN VALUES:
├─ Opportunity Discovery (Brain)
│  └─ Expected: Profitable signals with net_profit > MIN_PROFIT_USD
├─ Pre-Execution Validation (Bot)
│  └─ Expected: Simulation success, validated route
├─ Payload Construction
│  └─ Import: Route data, transaction parameters
├─ Transaction Broadcast
│  └─ Export: Signed transaction to mempool/BloxRoute
├─ On-Chain Execution (Contract)
│  └─ Produced: Actual profit, event logs
└─ Post-Execution Analysis (Bot)
   └─ Produced: Net profit, gas costs, success/failure

IMPORTS:
• Token prices (DexPricer, BridgeOracle)
• Gas prices (MarketForecaster, RPC providers)
• Route data (AggregatorSelector, Li.Fi)
• Historical patterns (FeatureStore)

EXPORTS:
• Signed transactions → Blockchain mempool
• Execution results → Logs, metrics
• Profits → Contract (on-chain) → Wallet (withdrawal)
• Feedback → AI models for optimization

PERFORMANCE TARGETS:
• Opportunity detection: 5-15 signals/minute
• Execution success rate: 80-90%
• Expected profit: $200-800/day (moderate conditions)
• Gas costs: $50-150/day
• Net ROI: up to ~500% in historical best-case simulations; actual ROI will vary and is not guaranteed
```

---

**Last Updated**: 2026-01-01  
**Version**: 1.1.0  
**Status**: Complete ✅
