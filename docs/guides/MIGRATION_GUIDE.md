# Migration Guide: On-Chain and Off-Chain Separation

> **⚠️ UPDATE (v4.2.1+):** As of version 4.2.1, smart contracts have been removed from this repository as they are already deployed and the Hardhat development infrastructure is no longer needed. The information below is kept for historical reference only. For current system architecture, see [README.md](README.md).

## Overview

The Titan 2.0 repository has been reorganized to clearly separate on-chain (blockchain-executable) code from off-chain (traditional computing) code. This improves code organization, maintainability, and developer experience.

## What Changed?

### Directory Structure

**Before:**
```
Titan2.0/
├── contracts/           # Smart contracts
├── core/                # Python infrastructure
├── execution/           # Node.js execution
├── ml/                  # Machine learning
├── routing/             # Cross-chain routing
├── monitoring/          # Monitoring tools
├── scripts/             # Deployment scripts
├── test/                # Contract tests
└── tests/               # Integration tests
```

**After:**
```
Titan2.0/
├── onchain/             # Blockchain-executable components
│   ├── contracts/       # Solidity smart contracts
│   ├── scripts/         # Deployment scripts
│   ├── test/            # Contract tests
│   └── README.md        # On-chain documentation
├── offchain/            # Traditional computing components
│   ├── core/            # Python infrastructure
│   ├── execution/       # Node.js execution layer
│   ├── ml/              # Machine learning & AI
│   ├── routing/         # Cross-chain routing
│   ├── monitoring/      # Real-time monitoring
│   ├── tests/           # Integration tests
│   └── README.md        # Off-chain documentation
└── ...                  # Root configuration files
```

## Migration Steps

### For Developers

#### 1. Update Git Repository

```bash
# Pull the latest changes
git pull origin main

# Update your dependencies
npm install
pip install -r requirements.txt
```

#### 2. Update Import Statements

**Python imports:**
```python
# Old
from core.config import CHAINS
from ml.brain import OmniBrain
from routing.bridge_aggregator import BridgeAggregator

# New
from offchain.core.config import CHAINS
from offchain.ml.brain import OmniBrain
from offchain.routing.bridge_aggregator import BridgeAggregator
```

**JavaScript/Node.js imports:**
```javascript
// Old
const { TitanBot } = require('./execution/bot.js');
const { GasManager } = require('./execution/gas_manager.js');

// New
const { TitanBot } = require('./offchain/execution/bot.js');
const { GasManager } = require('./offchain/execution/gas_manager.js');
```

#### 3. Update File Paths in Scripts

If you have custom scripts that reference files:

```bash
# Old
python3 ml/brain.py
node execution/bot.js

# New
python3 offchain/ml/brain.py
node offchain/execution/bot.js
```

### For Deployment

#### Smart Contracts

All contract deployment commands remain the same thanks to updated `package.json`:

```bash
# These still work without changes
npm run compile
npm run deploy:polygon
npm run deploy:arbitrum
```

Hardhat configuration has been updated to point to `onchain/contracts` automatically.

#### Off-Chain Services

All off-chain startup commands remain the same:

```bash
# These still work without changes
npm start          # Starts offchain/execution/bot.js
npm run brain      # Starts offchain/ml/brain.py
```

### Configuration Files

The following files have been updated automatically:
- `package.json` - Updated all script paths
- `hardhat.config.js` - Updated contract source paths
- Shell scripts (`.sh` files) - Updated all references
- Batch scripts (`.bat` files) - Updated all references

## Benefits of the New Structure

1. **Clarity**: Immediately clear what runs on blockchain vs. servers
2. **Modularity**: Easier to deploy components independently
3. **Maintenance**: Better organization for large teams
4. **Documentation**: Dedicated READMEs for each subsystem
5. **Deployment**: Clear separation for CI/CD pipelines

## Common Issues and Solutions

### Issue: Python ImportError

**Error:**
```
ModuleNotFoundError: No module named 'core'
```

**Solution:**
Update your import statements to use `offchain.core` instead of `core`:
```python
from offchain.core.config import CHAINS
```

### Issue: JavaScript Module Not Found

**Error:**
```
Cannot find module './execution/bot.js'
```

**Solution:**
Update the require path:
```javascript
const bot = require('./offchain/execution/bot.js');
```

### Issue: Hardhat Can't Find Contracts

**Error:**
```
Error: Cannot find contracts
```

**Solution:**
This should not happen as `hardhat.config.js` has been updated. If you see this, ensure you have the latest config:
```javascript
module.exports = {
  paths: {
    sources: "./onchain/contracts",
    tests: "./onchain/test",
    // ...
  },
  // ...
};
```

## Testing the Migration

### Test Smart Contracts

```bash
# Compile contracts (should work without errors)
npx hardhat compile

# Run contract tests
npx hardhat test
```

### Test Python Imports

```bash
# Test core imports
python3 -c "from offchain.core.config import CHAINS; print('OK')"

# Test ML imports
python3 -c "from offchain.ml.brain import OmniBrain; print('OK')"
```

### Test JavaScript Imports

```bash
# Test execution imports
node -e "require('./offchain/execution/bot.js'); console.log('OK')"
```

### Run the Full System

```bash
# Start the brain
npm run brain

# In another terminal, start the bot
npm start
```

## Need Help?

If you encounter issues during migration:

1. Check [onchain/README.md](onchain/README.md) for on-chain component details
2. Check [offchain/README.md](offchain/README.md) for off-chain component details
3. Review this migration guide
4. Open an issue on GitHub with details about your problem

## Rollback

If you need to revert to the old structure temporarily:

```bash
# Checkout the previous commit
git checkout <previous-commit-hash>

# Or checkout the old branch
git checkout <old-branch-name>
```

## Timeline

- **Migration Date**: December 27, 2024
- **Backward Compatibility**: None - all imports must be updated
- **Recommended Action**: Update your code as soon as possible

## Summary

This reorganization is a one-time breaking change that significantly improves the codebase structure. While it requires updating import paths, the long-term benefits for maintainability and clarity are substantial.

All core functionality remains the same - only file locations and import paths have changed.
