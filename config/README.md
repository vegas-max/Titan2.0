# Configuration

## Overview

The `config` directory contains JSON configuration files for various Titan system modes and optimizations. These files allow customization of system behavior without modifying code.

## Purpose

This configuration directory provides:
- **Mode-specific settings** for different operational scenarios
- **Optimization profiles** for specific hardware platforms
- **Agent configurations** for AI/ML components
- **Feature toggles** for enabling/disabling functionality

## Project Structure

```
config/
├── agent_config.json           # Agent system configuration
├── arm_optimization.json       # ARM platform optimizations
├── lightweight_mode.json       # Lightweight mode settings
└── README.md                  # This file
```

## Configuration Files

### agent_config.json

Configuration for the agent system:
- Agent behavior parameters
- Decision-making thresholds
- Communication settings
- Resource allocation

**Example structure:**
```json
{
  "agents": {
    "scanner": {
      "enabled": true,
      "scan_interval": 3000,
      "max_concurrent_scans": 20
    },
    "executor": {
      "enabled": true,
      "max_gas_price": 500,
      "min_profit_threshold": 5.0
    }
  }
}
```

### arm_optimization.json

Optimization settings for ARM-based platforms (Raspberry Pi, Oracle Cloud ARM):
- Memory limits
- Thread pool sizes
- Cache configurations
- Platform-specific tuning

**Example structure:**
```json
{
  "memory": {
    "brain_limit_mb": 700,
    "executor_limit_mb": 250,
    "cache_size_mb": 50
  },
  "performance": {
    "max_workers": 8,
    "enable_caching": true,
    "use_native_optimizations": true
  }
}
```

### lightweight_mode.json

Settings for running Titan in lightweight mode (reduced resource usage):
- Reduced scanning frequency
- Limited concurrent operations
- Minimal caching
- Lower memory footprint

**Example structure:**
```json
{
  "mode": "lightweight",
  "scanning": {
    "interval_ms": 10000,
    "max_concurrent": 5,
    "skip_low_liquidity": true
  },
  "execution": {
    "simulation_enabled": true,
    "max_gas_price": 300,
    "batch_size": 1
  }
}
```

## Usage

### Loading Configuration

#### Python
```python
import json

with open('config/lightweight_mode.json') as f:
    config = json.load(f)

# Use configuration
scan_interval = config['scanning']['interval_ms']
```

#### JavaScript
```javascript
const fs = require('fs');
const config = JSON.parse(fs.readFileSync('config/arm_optimization.json'));

// Use configuration
const memoryLimit = config.memory.brain_limit_mb;
```

### Environment-Specific Configuration

Set configuration file via environment variable:
```bash
export TITAN_CONFIG_FILE=config/lightweight_mode.json
python3 offchain/ml/brain.py
```

### Command-Line Override

```bash
# Use specific configuration
node offchain/execution/bot.js --config=config/arm_optimization.json

# Or with Python
python3 offchain/ml/brain.py --config=config/lightweight_mode.json
```

## Configuration Schema

### Common Configuration Sections

All configuration files may include:

#### Scanning Configuration
```json
{
  "scanning": {
    "interval_ms": 3000,           // Scan interval in milliseconds
    "max_concurrent": 20,          // Max parallel scans
    "timeout_ms": 5000,            // Scan timeout
    "skip_low_liquidity": false    // Skip low-liquidity pairs
  }
}
```

#### Execution Configuration
```json
{
  "execution": {
    "simulation_enabled": true,    // Pre-execution simulation
    "max_gas_price": 500,         // Max gas price in gwei
    "min_profit_threshold": 5.0,  // Min profit in USD
    "slippage_tolerance": 0.01,   // 1% slippage
    "retry_attempts": 3           // Failed TX retries
  }
}
```

#### Resource Limits
```json
{
  "resources": {
    "memory_limit_mb": 1024,      // Memory limit
    "cpu_cores": 4,               // CPU core allocation
    "max_workers": 20,            // Thread pool size
    "cache_size_mb": 100          // Cache memory
  }
}
```

#### Feature Flags
```json
{
  "features": {
    "cross_chain_enabled": true,
    "ml_optimization": true,
    "mev_protection": true,
    "advanced_routing": true
  }
}
```

## Creating Custom Configurations

### Step 1: Copy Template

```bash
cp config/lightweight_mode.json config/my_custom_config.json
```

### Step 2: Modify Settings

Edit the file with your preferred settings:
```json
{
  "mode": "custom",
  "description": "Custom configuration for high-performance setup",
  "scanning": {
    "interval_ms": 1000,
    "max_concurrent": 50
  },
  "execution": {
    "min_profit_threshold": 10.0
  }
}
```

### Step 3: Validate Configuration

```bash
# Validate JSON syntax
python3 -m json.tool config/my_custom_config.json

# Or use a linter
jsonlint config/my_custom_config.json
```

### Step 4: Test Configuration

```bash
# Test with your configuration
python3 offchain/ml/brain.py --config=config/my_custom_config.json --dry-run
```

## Configuration Profiles

### Default Profile
Standard configuration with balanced settings for most use cases.

### Lightweight Profile (`lightweight_mode.json`)
- Minimal resource usage
- Reduced scanning frequency
- Lower memory footprint
- Ideal for: Testing, low-resource environments

### ARM-Optimized Profile (`arm_optimization.json`)
- Optimized for ARM processors
- Adjusted thread pools
- Reduced memory limits
- Ideal for: Raspberry Pi, Oracle Cloud ARM instances

### High-Performance Profile
- Maximum concurrent operations
- Aggressive caching
- Higher resource usage
- Ideal for: Dedicated servers, high-volume trading

### Conservative Profile
- Higher profit thresholds
- More simulation checks
- Lower gas limits
- Ideal for: Risk-averse operation, testing

## Configuration Best Practices

1. **Start with templates** - Don't create from scratch
2. **Validate JSON** - Always check syntax before using
3. **Test in dry-run mode** - Verify behavior before live use
4. **Document changes** - Add comments explaining modifications
5. **Version control** - Track configuration changes in git
6. **Environment-specific** - Use different configs for test/prod

## Dynamic Configuration

Some settings can be changed at runtime:

```python
# In Python code
from offchain.core.config import update_runtime_config

update_runtime_config({
    'min_profit_threshold': 10.0,
    'max_gas_price': 400
})
```

```javascript
// In JavaScript code
const config = require('./config_manager');
config.update({
    minProfitThreshold: 10.0,
    maxGasPrice: 400
});
```

## Configuration Hierarchy

Configuration is loaded in this order (later overrides earlier):

1. Default hardcoded values in code
2. Configuration file (`config/*.json`)
3. Environment variables
4. Command-line arguments

Example:
```bash
# File sets min_profit = 5.0
# Environment variable overrides it
export TITAN_MIN_PROFIT=10.0

# Command-line argument overrides both
python3 brain.py --min-profit=15.0
```

## Further Documentation Needed

- [ ] Complete schema documentation for all configuration options
- [ ] Configuration validation utility
- [ ] Migration guide for config format changes
- [ ] Performance impact analysis for each setting
- [ ] Configuration examples for specific use cases
- [ ] Auto-tuning recommendations based on hardware

## Troubleshooting

### Invalid Configuration

**Symptom**: System fails to start or behaves unexpectedly

**Solution**:
1. Validate JSON syntax
2. Check all required fields are present
3. Verify value types match schema
4. Review error logs for specific issues

### Performance Issues

**Symptom**: System is slow or unresponsive

**Solution**:
1. Try lightweight configuration
2. Reduce concurrent operations
3. Increase scan interval
4. Lower memory limits if swapping

### Configuration Not Loading

**Symptom**: Changes to config file have no effect

**Solution**:
1. Verify correct file path
2. Check file permissions
3. Ensure no syntax errors
4. Restart the system completely

## Contributing

When adding configuration options:
1. Add to appropriate config file(s)
2. Document in this README
3. Add validation in code
4. Provide sensible defaults
5. Test with various values

## License

Configuration files are part of the Titan 2.0 project and follow the same MIT License.

## Support

For configuration issues:
- Check JSON syntax validity
- Review system logs for errors
- Start with default configuration
- Try lightweight mode if having resource issues

See main README.md for general support information.
