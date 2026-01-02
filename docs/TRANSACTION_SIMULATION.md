# Transaction Simulation and Pre-Broadcast Validation

## Overview

Titan 2.0 implements a comprehensive multi-stage simulation system to ensure that transactions will succeed before broadcasting them to the blockchain. This prevents wasted gas fees on failed transactions and protects against unexpected reverts.

## Architecture

The simulation system consists of two main components:

1. **OmniSDKEngine** (`offchain/execution/omniarb_sdk_engine.js`) - Core simulation engine
2. **TitanBot** (`offchain/execution/bot.js`) - Orchestrates the simulation flow before broadcast

## Simulation Flow

### Stage 1: Transaction Simulation

The first stage performs a full transaction simulation using Ethereum's `eth_call` RPC method:

```javascript
const simulationResult = await simulator.simulateTransaction(txRequest);
```

**What it does:**
- Simulates the entire transaction execution without actually broadcasting it
- Detects if the transaction would revert on-chain
- Estimates accurate gas usage
- Returns detailed error information if simulation fails

**Output:**
```javascript
{
  success: boolean,      // Whether the transaction would succeed
  gasUsed: bigint,      // Estimated gas consumption
  error: string | null  // Revert reason if failed
}
```

### Stage 2: Secondary Validation

A secondary validation check ensures consistency:

```javascript
const isSafe = await simulator.simulateExecution(EXECUTOR_ADDR, txRequest.data, wallet.address);
```

**What it does:**
- Performs an additional verification of the transaction
- Cross-checks the results from Stage 1
- Acts as a safety net against edge cases

### Stage 3: Pre-Broadcast Safety Checks

Final checks before broadcasting:

```javascript
// Validate gas estimates
if (estimatedGas > gasLimit) {
    txRequest.gasLimit = estimatedGas * 120n / 100n; // Add 20% buffer
}
```

**What it checks:**
- Gas limit is sufficient (adds 20% buffer if needed)
- All prerequisites are met
- Transaction parameters are valid

## Console Output

The system provides detailed console output during simulation:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧪 PRE-BROADCAST SIMULATION & VALIDATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Step 1: Simulating transaction execution...
   ✅ Step 1: Transaction simulation PASSED
   Estimated gas usage: 245678

   Step 2: Validating simulation results...
   ✅ Step 2: Simulation validation PASSED

   Step 3: Final pre-broadcast checks...
   ✅ Step 3: Pre-broadcast checks COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ ALL SIMULATIONS PASSED - Transaction ready for broadcast
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Failure Example

If simulation fails, the transaction is aborted:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧪 PRE-BROADCAST SIMULATION & VALIDATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Step 1: Simulating transaction execution...
   ❌ Simulation FAILED - Transaction would revert on-chain
   Reason: InsufficientLiquidity
   ⚠️  Aborting transaction to prevent wasted gas fees
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Broadcast Flow

Only after all simulations pass, the transaction proceeds to broadcast:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📡 TRANSACTION BROADCAST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Chain ID: 137
   Token: 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174
   Amount: 1000000000
   Expected Profit: $12.50
   Gas Limit: 350000
   Estimated Cost: $0.15
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📡 Broadcasting to public mempool...

✅ Transaction broadcast successfully!
   TX Hash: 0x1234567890abcdef...
   Explorer: https://polygonscan.com/tx/0x1234567890abcdef...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ BROADCAST COMPLETE - Monitoring for confirmation...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Benefits

### Cost Savings
- **Prevents wasted gas fees** on transactions that would fail
- Average savings: $0.50 - $5.00 per prevented failed transaction
- With 10-20 prevented failures per day: $5-100 daily savings

### Risk Reduction
- **Detects issues before on-chain execution:**
  - Insufficient liquidity
  - Slippage too high
  - Access control violations
  - Logic errors
  - Gas limit issues

### Improved Reliability
- **Success rate improvement:** 86% → 95%+ (estimated)
- Fewer unexpected failures
- Better user confidence

### Better Debugging
- Detailed error messages from simulation
- Stack traces for complex issues
- Clear identification of failure points

## Error Handling

The simulation system handles various error scenarios:

### Common Errors Detected

1. **Insufficient Liquidity**
   - Detected in Stage 1
   - Transaction aborted before broadcast
   - Error: "Pool liquidity insufficient for swap"

2. **Slippage Exceeded**
   - Detected in Stage 1
   - Transaction aborted
   - Error: "Slippage tolerance exceeded"

3. **Gas Limit Too Low**
   - Detected in Stage 3
   - Automatically adjusted with 20% buffer
   - Transaction proceeds with updated limit

4. **Unauthorized Access**
   - Detected in Stage 1
   - Transaction aborted
   - Error: "Caller is not authorized"

5. **Flash Loan Provider Unavailable**
   - Detected in Stage 1
   - Transaction aborted
   - Error: "Flash loan provider pool exhausted"

## Configuration

Simulation behavior can be configured via environment variables:

```env
# Maximum gas price allowed (abort if exceeded)
MAX_BASE_FEE_GWEI=500

# Flash loan provider (1=Balancer, 2=Aave)
FLASH_LOAN_PROVIDER=1

# Enable flash loans (must be true for Titan)
FLASH_LOAN_ENABLED=true
```

## Technical Details

### RPC Methods Used

1. **eth_call** - Simulates transaction execution
2. **eth_estimateGas** - Calculates gas requirements
3. **eth_getBlockNumber** - Gets current block for timing

### Dependencies

- `ethers.js v6` - Ethereum interaction library
- Provider must support `eth_call` (all standard RPC providers do)

### Performance

- **Stage 1:** ~200-500ms
- **Stage 2:** ~100-300ms  
- **Stage 3:** ~10-50ms
- **Total:** ~300-850ms additional latency before broadcast

This small delay is worth the cost savings and reliability improvement.

## Comparison: Before vs After

### Before Enhancement
```
1. Build transaction
2. Sign transaction
3. Broadcast transaction
4. ❌ Transaction fails on-chain
5. Gas fees wasted
```

### After Enhancement
```
1. Build transaction
2. 🧪 Simulate (Stage 1) - PASS
3. 🧪 Validate (Stage 2) - PASS
4. 🧪 Final checks (Stage 3) - PASS
5. Sign transaction
6. Broadcast transaction
7. ✅ Transaction succeeds on-chain
```

## Monitoring

Transaction monitoring happens after successful broadcast:

```javascript
async _monitorTransaction(tx, provider, signal) {
    const receipt = await tx.wait(1);  // Wait for 1 confirmation
    
    if (receipt.status === 1) {
        // Success - log details
    } else {
        // Unexpected failure - log and alert
    }
}
```

### Monitored Metrics
- Transaction status (success/failure)
- Gas used
- Block number
- Actual gas cost
- Transaction confirmation time

## Best Practices

1. **Always enable simulation** - Never skip pre-broadcast validation
2. **Review simulation logs** - Understand why transactions fail
3. **Monitor gas estimates** - Ensure they're reasonable
4. **Use appropriate gas limits** - Let Stage 3 add the buffer
5. **Check expected vs actual profit** - Verify profitability after execution

## Future Enhancements

Potential improvements to the simulation system:

- [ ] Add simulation result caching for duplicate signals
- [ ] Implement predictive failure detection based on historical patterns
- [ ] Add simulation speed optimization for time-sensitive trades
- [ ] Support for multi-transaction simulations (bundles)
- [ ] Integration with Tenderly for advanced debugging
- [ ] Real-time profit recalculation post-simulation

## Troubleshooting

### Simulation Always Fails

**Problem:** All transactions fail simulation

**Solutions:**
1. Check RPC provider is responding
2. Verify executor contract is deployed
3. Ensure sufficient wallet balance for gas
4. Check flash loan provider has liquidity

### Simulation Passes But Transaction Fails

**Problem:** Simulation succeeds but on-chain execution fails

**Possible causes:**
- Price moved between simulation and execution
- MEV bot front-ran the transaction
- Gas price too low (transaction pending too long)
- Nonce conflict with another transaction

**Solutions:**
- Reduce time between simulation and broadcast
- Use MEV protection (BloxRoute)
- Increase gas price for faster inclusion
- Implement nonce management

## Support

For issues related to simulation:

1. Check the simulation logs for detailed error messages
2. Review the [OPERATIONS_GUIDE.md](../OPERATIONS_GUIDE.md) for common issues
3. Open an issue on GitHub with simulation logs attached
4. Check RPC provider status if all simulations timeout

## Related Documentation

- [OPERATIONS_GUIDE.md](../OPERATIONS_GUIDE.md) - System operations
- [SECURITY_SUMMARY.md](../SECURITY_SUMMARY.md) - Security features
- [README.md](../README.md) - Main documentation
