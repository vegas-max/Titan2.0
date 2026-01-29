# Executor Contracts - Quick Reference Guide

## TL;DR - What You Need to Know

### The Confusion (RESOLVED)
People often confuse **flash loan providers** with **executor contracts**. They are **completely different concepts**.

---

## Two Separate Concepts

### 1️⃣ Flash Loan Provider (Active System)
**What:** WHERE to borrow flash loan capital
**Values:** 
- `1` = Balancer V3
- `2` = Aave V3

**Environment Variable:** `FLASH_LOAN_PROVIDER`
**Used in bot.js:** ✅ YES (actively used)

---

### 2️⃣ Executor Contracts (Reference Only)
**What:** HOW to execute arbitrage trades
**Values:**
- `HFT_CONTRACT_ADDRESS` = Simple V2 swaps
- `ROUTER_CONTRACT_ADDRESS` = Complex multi-hop paths

**Environment Variables:** `HFT_CONTRACT_ADDRESS`, `ROUTER_CONTRACT_ADDRESS`
**Used in bot.js:** ❌ NO (reference architecture only)

---

## Current System Architecture

```
┌─────────────────────────────────┐
│         bot.js                  │
│  Selects flash provider (1/2)   │
└─────────────────────────────────┘
              ↓
┌─────────────────────────────────┐
│    EXECUTOR_ADDRESS             │
│    (One unified contract)       │
│                                 │
│  If flashSource=1 → Balancer    │
│  If flashSource=2 → Aave        │
└─────────────────────────────────┘
```

**Current active approach:**
- ONE executor contract (EXECUTOR_ADDRESS)
- Selectable flash loan source (Balancer or Aave)
- Configured via FLASH_LOAN_PROVIDER

---

## Configuration Guide

### ✅ What to Configure (Active)
```bash
# In .env file:
EXECUTOR_ADDRESS=0x1234...         # Your deployed OmniArbExecutor
FLASH_LOAN_PROVIDER=1              # 1=Balancer, 2=Aave
FLASH_LOAN_ENABLED=true            # Must be true
```

### ⚠️ What to Ignore (Reference Only)
```bash
# These are NOT used by bot.js:
HFT_CONTRACT_ADDRESS=0xAF54...     # Reference architecture only
ROUTER_CONTRACT_ADDRESS=0x4442...   # Reference architecture only
```

---

## Common Questions

### Q: What does FLASH_LOAN_PROVIDER control?
**A:** WHERE to borrow flash loan funds (Balancer or Aave)

### Q: Does FLASH_LOAN_PROVIDER select HFT vs Router?
**A:** NO. It selects Balancer vs Aave (liquidity source)

### Q: Are HFT and Router contracts used?
**A:** NO. They are reference architecture. bot.js uses EXECUTOR_ADDRESS only.

### Q: Can I use both flash loan approaches?
**A:** NO. Environment supports ONE approach: unified executor with Balancer/Aave choice

### Q: How do I switch to HFT/Router architecture?
**A:** You need to:
1. Deploy HFT and Router contracts
2. Integrate ArbitrageEngine into bot.js (not currently done)
3. Stop using EXECUTOR_ADDRESS
4. See `execution/arbitrage_engine_integration_example.js`

---

## Decision Tree

```
Do you want to change which contract executes trades?
├─ YES: You need to modify bot.js code (not just .env)
│       Deploy new executor contract
│       Update EXECUTOR_ADDRESS
│
└─ NO: Just change flash loan provider?
       ├─ Set FLASH_LOAN_PROVIDER=1 (Balancer)
       └─ Set FLASH_LOAN_PROVIDER=2 (Aave)
```

---

## Files to Reference

| Topic | File |
|-------|------|
| Complete Architecture | `EXECUTOR_CONTRACTS_CLARIFICATION.md` |
| ArbitrageEngine Details | `ARBITRAGE_ENGINE_README.md` |
| Active Implementation | `offchain/execution/bot.js` |
| Integration Example | `execution/arbitrage_engine_integration_example.js` |
| Flash Loan Enforcement | `FLASH_LOAN_ENFORCEMENT_SUMMARY.md` |

---

## Summary

✅ **Active System:** One executor (EXECUTOR_ADDRESS) + Balancer/Aave selection
❌ **Not Active:** HFT/Router dual executors (reference architecture only)
🎯 **Flash Provider ≠ Executor Contract** (different concepts)
📚 **Read Full Docs:** See EXECUTOR_CONTRACTS_CLARIFICATION.md for details
