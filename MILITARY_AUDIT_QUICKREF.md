# Military Audit System - Quick Reference

## Quick Commands

```bash
# Run full military audit
make military-audit

# Build with validation (recommended for production)
make validated-build

# Pre-start validation check
./pre_start_validation.sh

# Or use Python directly
python3 military_audit.py
```

## Gate Status Quick Check

### ✓ PASSED - All tests passed, benchmarks met
### ✗ FAILED - One or more tests failed or benchmarks not met
### ⚠ WARNING - Non-critical issues detected

## 8 Validation Gates

| Gate | Module | Critical Tests | Benchmarks |
|------|--------|---------------|------------|
| 1 | Configuration | config.json valid, networks configured | load_time < 0.5s, ≥3 DEXs, ≥5 tokens |
| 2 | Core Infrastructure | Core files exist, dependencies installed | import_time < 2.0s |
| 3 | RPC Connections | RPC vars configured, connection works | connect < 5s, block_fetch < 3s |
| 4 | DEX Integration | DEX pricer exists, endpoints configured | ≥3 DEX endpoints |
| 5 | ML/AI Components | Brain exists, cortex modules present | - |
| 6 | Execution Engine | Bot exists, Node.js available | - |
| 7 | Security Systems | .env in gitignore, keys valid | - |
| 8 | System Integration | All components present, health check | - |

## Common Failures & Fixes

### Gate 1: Configuration Failed
```bash
# Issue: config.json not found
cp config.json.example config.json

# Issue: .env not found
cp .env.example .env
# Edit .env with your settings
```

### Gate 2: Core Infrastructure Failed
```bash
# Issue: Python dependencies missing
pip3 install -r requirements.txt

# Issue: Node.js dependencies missing
npm install --legacy-peer-deps

# Issue: Core files missing
git pull origin main
```

### Gate 3: RPC Connections Failed
```bash
# Issue: RPC environment variables not set
# Edit .env and add:
RPC_POLYGON=https://polygon-rpc.com
RPC_ETHEREUM=https://eth-rpc.com
INFURA_API_KEY=your_key_here
ALCHEMY_API_KEY=your_key_here

# Issue: RPC connection timeout
# Check internet connection
# Try different RPC provider
```

### Gate 4: DEX Integration Failed
```bash
# Issue: DEX pricer module missing
git pull origin main

# Issue: Not enough DEX endpoints
# Edit config.json and ensure dex_endpoints has ≥3 entries
```

### Gate 5: ML/AI Components Failed
```bash
# Issue: Brain module missing
git pull origin main

# Issue: ML dependencies missing
pip3 install pandas numpy
```

### Gate 6: Execution Engine Failed
```bash
# Issue: Bot module missing
git pull origin main

# Issue: Node.js not available
# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### Gate 7: Security Failed
```bash
# Issue: .env not in .gitignore
echo ".env" >> .gitignore

# Issue: Private key format invalid
# Edit .env and ensure:
WALLET_PRIVATE_KEY=0x1234...  # Must be 66 chars (0x + 64 hex)
```

### Gate 8: System Integration Failed
```bash
# Issue: Components missing
git pull origin main

# Issue: Signals directory missing (non-critical)
mkdir -p signals/outgoing signals/incoming
```

## Validation Cache

Validation results are cached for **1 hour** in `.last_validation`

```bash
# Force fresh validation (delete cache)
rm .last_validation

# Check last validation time
cat .last_validation
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All gates passed - system ready |
| 1 | One or more gates failed - fix required |

## Integration with Startup

The validation system is integrated into system startup:

```bash
# These commands run pre-start validation automatically:
make start
./start.sh
make start-mainnet-paper
make start-mainnet-live

# Startup will abort if validation fails
```

## Bypass Validation (NOT RECOMMENDED)

⚠️ **WARNING**: Bypassing validation can lead to system failures

To skip validation (emergency use only):
```bash
# Skip pre-start validation
export SKIP_VALIDATION=1
./start.sh

# Or start components directly (no validation)
python3 offchain/ml/brain.py &
node offchain/execution/bot.js &
```

## Best Practices

1. ✓ Run validation before every deployment
2. ✓ Fix all failed gates immediately
3. ✓ Use `make validated-build` for fresh installs
4. ✓ Check audit logs: `cat military_audit_*.log`
5. ✓ Never bypass validation in production

## Customization

Add custom tests by editing `military_audit.py`:

```python
def _validate_my_module(self, gate: AuditGate) -> bool:
    logger.info("Validating My Module...")
    
    # Add test
    gate.record_test("Test name", True, "")
    
    # Add benchmark
    gate.record_benchmark("metric", value, threshold, "unit")
    
    return gate.tests_failed == 0
```

## Troubleshooting

### Audit Takes Too Long
- Check internet connection
- Verify RPC providers are responding
- Review audit log for slow operations

### Audit Crashes
- Check Python version (need 3.11+)
- Verify all dependencies installed
- Review error in audit log file

### False Positives
- Review specific test in `military_audit.py`
- Adjust thresholds if needed
- Report issue if test is incorrect

## Support

For detailed documentation, see: `MILITARY_AUDIT_SYSTEM.md`

For issues, check audit log: `military_audit_YYYYMMDD_HHMMSS.log`
