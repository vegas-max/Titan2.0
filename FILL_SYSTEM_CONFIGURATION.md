# Fill System Configuration for Live Execution

## Overview

The fill system configuration controls how orders are executed in CoW Swap during live trading with real money. This setting is critical for managing execution risk in production environments.

## Configuration

### Environment Variable

```bash
COWSWAP_PARTIALLY_FILLABLE=false  # Recommended for live trading
```

### Options

#### `false` (Recommended - Default)
- **Behavior**: All-or-nothing execution
- **Description**: Orders must be filled completely or not at all
- **Use Case**: Live trading with real money
- **Risk Level**: Lower risk - ensures predictable position sizes
- **Recommendation**: **Use this setting for production/live trading**

#### `true` (Advanced)
- **Behavior**: Partial fills allowed
- **Description**: Orders can be partially filled if full liquidity is unavailable
- **Use Case**: High-volume trading where partial execution is acceptable
- **Risk Level**: Higher risk - may result in unexpected partial positions
- **Recommendation**: Only use if you understand the implications and have proper position monitoring

## Google Colab Configuration

When setting up TITAN in Google Colab, you will be prompted:

```
⚡ Fill System Configuration (CoW Swap):
  This controls how orders are filled in live execution mode
  FALSE (recommended): All-or-nothing execution - safer for real money
  TRUE: Allow partial fills - better execution rate but may result in partial positions
  
Allow partial order fills? [false/true] (default: false):
```

### For LIVE Mode
- The system will prompt you to configure this setting
- **Strongly recommended**: Press Enter to accept the default `false`
- If you choose `true`, you will see a warning about monitoring positions

### For PAPER Mode
- The system automatically sets this to `false` (no prompt needed)

## Implementation

### Location in Code

The fill system is implemented in `offchain/execution/cowswap_manager.js`:

```javascript
constructor(chainId, provider = null) {
    // ...
    // Fill system configuration: Allow partial fills or require atomic execution
    // Default: false (safer for live trading - ensures all-or-nothing execution)
    this.partiallyFillable = process.env.COWSWAP_PARTIALLY_FILLABLE === 'true';
}
```

### Configuration Files

1. **`.env.example`**: Template with documentation
2. **`.env`**: Your actual configuration (created during setup)
3. **Google Colab Notebook**: Interactive setup in Step 4

## Security Considerations

### Why `false` is Recommended for Live Trading

1. **Predictable Position Sizes**
   - You know exactly how much will be executed
   - Easier to manage risk and capital allocation

2. **Atomic Execution**
   - Either the full trade executes or nothing happens
   - No unexpected partial positions to manage

3. **Simplified Accounting**
   - Easier to track trades and P&L
   - No need to handle partial fill scenarios

### Risks of `true` (Partial Fills)

1. **Unexpected Partial Positions**
   - You may end up with positions smaller than intended
   - Can complicate position management and risk calculations

2. **Multiple Partial Fills**
   - A single intended trade might be split across multiple partial fills
   - Increased complexity in tracking and accounting

3. **Liquidity Fragmentation**
   - Partial fills may indicate insufficient liquidity
   - Could signal that the trade size is too large for current market conditions

## Best Practices

### For Production/Live Trading
```bash
# .env configuration
EXECUTION_MODE=LIVE
COWSWAP_PARTIALLY_FILLABLE=false  # Atomic execution only
```

### For Testing/Paper Trading
```bash
# .env configuration
EXECUTION_MODE=PAPER
COWSWAP_PARTIALLY_FILLABLE=false  # Also recommended for testing
```

### Monitoring

If you choose to enable partial fills (`true`):

1. **Monitor Position Sizes**
   - Check that positions match your intended sizes
   - Be prepared to handle partial fills

2. **Track Fill Rates**
   - Monitor what percentage of orders are partially filled
   - May indicate liquidity issues or order size problems

3. **Review Logs**
   - Check execution logs for partial fill notifications
   - Understand why fills are partial

## Troubleshooting

### Orders Not Executing

If orders aren't executing with `partiallyFillable=false`:

1. **Check Liquidity**
   - Ensure sufficient liquidity exists for your full order size
   - Consider reducing order size

2. **Review Market Conditions**
   - High volatility may make full fills difficult
   - Consider waiting for better market conditions

3. **Try Smaller Sizes**
   - Break large orders into smaller chunks manually
   - Execute multiple smaller all-or-nothing orders

### Unexpected Partial Positions

If you have partial positions with `partiallyFillable=true`:

1. **Review Configuration**
   - Confirm whether this is intentional
   - Consider switching to `false` for more predictable execution

2. **Adjust Position Management**
   - Update your position tracking to handle partials
   - Implement logic to complete or close partial positions

3. **Monitor More Closely**
   - Increase monitoring frequency
   - Set up alerts for partial fills

## Related Documentation

- [GO_LIVE_CHECKLIST.md](GO_LIVE_CHECKLIST.md) - Production readiness checklist
- [MAINNET_MODES.md](MAINNET_MODES.md) - Execution modes (PAPER vs LIVE)
- [GOOGLE_COLAB_GUIDE.md](GOOGLE_COLAB_GUIDE.md) - Complete Colab setup guide
- [.env.example](.env.example) - Configuration template

## Support

For questions about fill system configuration:

1. Review this documentation
2. Check the Google Colab notebook Step 4
3. Refer to `.env.example` for configuration options
4. Test in PAPER mode before going live

---

**⚠️ Important**: Always test your configuration in PAPER mode before using LIVE mode with real money. The default setting (`false`) is recommended for all production trading.

**Last Updated**: 2026-01-06  
**Version**: 1.0.0
