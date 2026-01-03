# 🔧 Oracle Cloud .env Configuration Guide

**Quick Answer:** Yes, the `.env` file is **automatically created and pre-configured** during deployment, but you **must add your credentials** before the system is 100% ready.

---

## ✅ What's Automatically Configured

When you run `./deploy_oracle_cloud.sh`, the script **automatically**:

### 1. Creates .env from Template
```bash
cp .env.example .env
```

### 2. Auto-Configures Performance Settings

**For ARM A1.Flex (4 OCPU, 24GB RAM):**
```bash
LIGHTWEIGHT_MODE=false
MAX_CONCURRENT_SCANS=20
WORKER_THREADS=4
ENABLE_GRAPH_VISUALIZATION=true
CACHE_SIZE_MB=1000
EXECUTION_MODE=PAPER
```

**For AMD E2.1.Micro (1 OCPU, 1GB RAM):**
```bash
LIGHTWEIGHT_MODE=true
MAX_CONCURRENT_SCANS=3
WORKER_THREADS=1
ENABLE_GRAPH_VISUALIZATION=false
CACHE_SIZE_MB=50
EXECUTION_MODE=PAPER
```

### 3. Sets Safe Defaults
- ✅ `EXECUTION_MODE=PAPER` - Safe paper trading mode (no real trades)
- ✅ Performance optimized for your instance type
- ✅ Resource limits appropriate for available RAM

---

## ⚠️ What You MUST Configure Manually

Before the system is 100% ready, you **must add** these credentials:

### Required (Minimum for Basic Operation):

```bash
# 1. Wallet Private Key (CRITICAL)
PRIVATE_KEY=0xYOUR_ACTUAL_PRIVATE_KEY_64_HEX_CHARACTERS

# 2. RPC Endpoints (CRITICAL)
RPC_POLYGON=https://polygon-mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID
RPC_ETHEREUM=https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID

# 3. Backup RPC (RECOMMENDED)
ALCHEMY_RPC_POLY=https://polygon-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY
ALCHEMY_RPC_ETH=https://eth-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY

# 4. Li.Fi API Key (CRITICAL for cross-chain)
LIFI_API_KEY=your_lifi_api_key_from_https://li.fi/
```

### Recommended (For Better Performance):

```bash
# Price feeds
COINGECKO_API_KEY=your_coingecko_key

# DEX aggregators
ONEINCH_API_KEY=your_1inch_key
ZEROX_API_KEY=your_0x_key
RANGO_API_KEY=your_rango_key
```

---

## 📝 Configuration Steps

### After Running deploy_oracle_cloud.sh:

**Step 1: Edit .env**
```bash
nano .env
```

**Step 2: Add Your Credentials**
Scroll down and replace these placeholders:
- `YOUR_PRIVATE_KEY_HERE_64_HEX_CHARACTERS`
- `YOUR_INFURA_PROJECT_ID`
- `YOUR_ALCHEMY_API_KEY`
- `your_lifi_api_key`

**Step 3: Save and Exit**
- Press `Ctrl+O` to save
- Press `Enter` to confirm
- Press `Ctrl+X` to exit

**Step 4: Verify Configuration**
```bash
# Check that PRIVATE_KEY is set
grep PRIVATE_KEY .env | grep -v "YOUR_PRIVATE"

# Check that RPC endpoints are set
grep RPC_POLYGON .env | grep -v "YOUR_INFURA"
```

**Step 5: Start Services**
```bash
./start_oracle.sh
```

---

## 🎯 Configuration Checklist

Before starting Titan, verify:

- [ ] ✅ `.env` file exists (auto-created by deployment script)
- [ ] ✅ Performance settings added (auto-configured)
- [ ] ✅ `EXECUTION_MODE=PAPER` (auto-set for safety)
- [ ] ⚠️ **PRIVATE_KEY** set to your actual key
- [ ] ⚠️ **RPC_POLYGON** set to your Infura/Alchemy endpoint
- [ ] ⚠️ **RPC_ETHEREUM** set to your Infura/Alchemy endpoint
- [ ] ⚠️ **LIFI_API_KEY** set to your Li.Fi key
- [ ] ✅ File permissions: `chmod 600 .env` (auto-set)

---

## 🔐 Security Notes

1. **Never commit .env to git** - Already in `.gitignore`
2. **Use a dedicated wallet** - Not your main wallet
3. **Start with small funds** - $20-50 recommended for testing
4. **Keep in PAPER mode** - Test for 24-48 hours before going live

---

## ✅ System 100% Ready When:

The system is **100% configured** and ready to deploy when:

1. ✅ `./deploy_oracle_cloud.sh` completed successfully
2. ✅ `.env` file created with auto-configured performance settings
3. ✅ You added your **PRIVATE_KEY**, **RPC endpoints**, and **LIFI_API_KEY**
4. ✅ `./oracle_health_check.sh` passes all checks
5. ✅ Services start successfully: `./start_oracle.sh`

---

## 🚀 Quick Verification Command

Run this to check if your .env is ready:

```bash
#!/bin/bash
echo "Checking .env configuration..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found"
    exit 1
fi

# Check for required variables
MISSING=0

if grep -q "YOUR_PRIVATE_KEY" .env; then
    echo "❌ PRIVATE_KEY not configured"
    ((MISSING++))
else
    echo "✅ PRIVATE_KEY configured"
fi

if grep -q "YOUR_INFURA_PROJECT_ID" .env; then
    echo "❌ RPC endpoints not configured"
    ((MISSING++))
else
    echo "✅ RPC endpoints configured"
fi

if grep -q "LIFI_API_KEY=$" .env || ! grep -q "LIFI_API_KEY=" .env; then
    echo "⚠️  LIFI_API_KEY not configured (recommended)"
fi

if [ $MISSING -eq 0 ]; then
    echo ""
    echo "✅ .env is ready for deployment!"
else
    echo ""
    echo "⚠️  Please configure missing credentials in .env"
fi
```

Save as `check_env.sh`, make executable: `chmod +x check_env.sh`, then run: `./check_env.sh`

---

## 📞 Need Help?

If configuration issues persist:
1. Run `./oracle_health_check.sh` for diagnostics
2. Check [ORACLE_TROUBLESHOOTING.md](ORACLE_TROUBLESHOOTING.md)
3. Verify API keys are valid and active

---

**TL;DR:** The deployment script creates and pre-configures `.env`, but you must manually add your `PRIVATE_KEY`, RPC endpoints, and API keys before the system is 100% ready to run.
