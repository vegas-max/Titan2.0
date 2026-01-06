# 📋 TITAN 2.0 - Deployment Prerequisites Quick Reference

**Print this page or keep it open while setting up TITAN**

---

## ✅ Required Information Checklist

### 1. Google Account
- [ ] Have a Google account (for Colab)
- [ ] Logged in to Google

### 2. Wallet Private Key
- [ ] **Private Key:** `________________________________________________` (64 hex characters)
- [ ] ⚠️ Use DEDICATED wallet (NOT main wallet)
- [ ] ⚠️ For testing: Can use test wallet
- [ ] ⚠️ For LIVE mode: Wallet with minimal funds only

**Format:** Remove `0x` prefix, enter 64 hexadecimal characters only

**Example:** `1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef`

---

### 3. Infura Project ID (REQUIRED)
- [ ] **Infura Project ID:** `________________________________________`
- [ ] Sign up: https://infura.io
- [ ] Create new project
- [ ] Copy Project ID

**Where to find it:**
1. Go to https://app.infura.io/
2. Click your project
3. Copy the "PROJECT ID"

---

## 📝 Optional (But Recommended) Information

### 4. Alchemy API Key (Backup RPC)
- [ ] **Alchemy API Key:** `________________________________________`
- [ ] Sign up: https://alchemy.com
- [ ] Create new app
- [ ] Copy API Key

**Benefits:** Backup RPC provider, higher rate limits, better reliability

---

### 5. Li.Fi API Key (Cross-Chain Bridges)
- [ ] **Li.Fi API Key:** `________________________________________`
- [ ] Sign up: https://li.fi
- [ ] Get free API key

**Benefits:** Cross-chain arbitrage opportunities, 15+ bridge protocols

---

### 6. CoinGecko API Key (Price Feeds)
- [ ] **CoinGecko API Key:** `________________________________________`
- [ ] Sign up: https://www.coingecko.com/en/api
- [ ] Get free API key

**Benefits:** Reliable token price data, fallback price oracle

---

## 🔐 Optional Advanced Features

### 7. 1inch API Key (DEX Aggregation)
- [ ] **1inch API Key:** `________________________________________`
- [ ] Get key: https://portal.1inch.dev/

---

### 8. 0x API Key (Swap Aggregation)
- [ ] **0x API Key:** `________________________________________`
- [ ] Get key: https://0x.org/docs/introduction/getting-started

---

### 9. BloxRoute Auth (MEV Protection)
- [ ] **BloxRoute Auth:** `________________________________________`
- [ ] Sign up: https://bloxroute.com/

**Benefits:** Private mempool, MEV protection for high-value trades

---

## ⚙️ Configuration Decisions

### Execution Mode
- [ ] **PAPER** - Simulated trading (RECOMMENDED for testing)
- [ ] **LIVE** - Real trading with real funds (⚠️ USE WITH CAUTION)

**Recommendation:** Always start with PAPER mode

---

### Strategy Parameters

**Minimum Profit Threshold:**
- [ ] Default: `$5.00`
- [ ] Custom: `$________`

**Maximum Slippage:**
- [ ] Default: `50` basis points (0.5%)
- [ ] Custom: `_____` basis points

**Maximum Gas Fees:**
- [ ] Max Priority Fee: `50` gwei (default)
- [ ] Max Base Fee: `200` gwei (default)

---

## 🚀 Quick Start Commands

### Using Interactive Script (Recommended)

```bash
# Make script executable
chmod +x deployment_prerequisites_setup.sh

# Run the wizard
./deployment_prerequisites_setup.sh
```

The script will:
- ✅ Prompt you for all values
- ✅ Validate your inputs
- ✅ Generate .env file
- ✅ Create deployment summary

---

### Manual Setup

If you prefer to create .env manually:

```bash
# Copy example file
cp .env.example .env

# Edit with your values
nano .env
```

Then fill in:
- `PRIVATE_KEY=` (your private key)
- `INFURA_PROJECT_ID=` (your Infura ID)
- `ALCHEMY_API_KEY=` (optional)
- `LIFI_API_KEY=` (optional)
- Other values as needed

---

## 📍 Where to Use This Information

### Google Colab
1. Open `Titan_Google_Colab.ipynb` in Colab
2. Run "Step 4: Configure Environment Variables" cell
3. Enter values when prompted

### Interactive Setup Script
1. Run `./deployment_prerequisites_setup.sh`
2. Answer prompts using info from this sheet

### Oracle Cloud Deployment
1. SSH into Oracle instance
2. Transfer your .env file
3. Run `./deploy_oracle_cloud.sh`

### Local Installation
1. Create .env file in Titan2.0 directory
2. Fill with your values
3. Run `./setup.sh`

---

## 🔒 Security Reminders

- ✅ NEVER commit .env file to Git
- ✅ NEVER share your private key publicly
- ✅ Use dedicated wallet (NOT main wallet)
- ✅ Keep API keys secure
- ✅ Test in PAPER mode first
- ✅ Use minimal funds in LIVE mode

---

## 📚 Documentation Links

- **Step-by-Step Colab Guide:** GOOGLE_COLAB_STEP_BY_STEP.md
- **Interactive Setup:** Run `./deployment_prerequisites_setup.sh`
- **Quick Start:** QUICKSTART.md
- **Oracle Deployment:** ORACLE_CLOUD_DEPLOYMENT.md
- **Full Guide:** README.md

---

## ❓ Quick FAQ

**Q: What if I don't have all the API keys?**
A: Only Infura is required. Others are optional enhancements.

**Q: Can I change these values later?**
A: Yes! Edit .env file and restart TITAN.

**Q: Is my private key safe?**
A: Use a dedicated wallet with minimal funds. Never share the key.

**Q: What's the difference between PAPER and LIVE?**
A: PAPER simulates trades (no real money). LIVE executes real trades.

**Q: How much money do I need?**
A: For PAPER: $0 (just gas for setup). For LIVE: Start with $100-500.

---

## ✅ Final Checklist Before Deployment

- [ ] All required values filled in
- [ ] Private key validated (64 hex characters)
- [ ] Infura Project ID tested
- [ ] Execution mode selected (PAPER recommended)
- [ ] .env file created
- [ ] Security reminders reviewed
- [ ] Ready to deploy!

---

**Built with ❤️ by the Titan Team**

⭐ Star the repo: https://github.com/vegas-max/Titan2.0
