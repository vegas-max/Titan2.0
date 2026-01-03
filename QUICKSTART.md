# 🚀 Titan Quick Start Guide

Get Titan up and running in 15 minutes.

## Prerequisites

Before you begin, ensure you have:

- **Node.js 18+** - [Download here](https://nodejs.org/)
- **Python 3.11+** - [Download here](https://python.org/)
- **Redis 5.0+** - [Installation guide](https://redis.io/download)
- **Git** - [Download here](https://git-scm.com/)

## Installation

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/MavenSource/Titan.git
cd Titan

# Run automated setup
chmod +x setup.sh
./setup.sh
```

The setup script will:
- ✅ Check prerequisites
- ✅ Install dependencies (Node.js & Python)
- ✅ Compile smart contracts
- ✅ Create `.env` file from template
- ✅ Verify Redis connection
- ✅ Run system audit

### Option 2: Manual Setup

```bash
# Clone repository
git clone https://github.com/MavenSource/Titan.git
cd Titan

# Install Node.js dependencies
npm install

# Install Python dependencies
pip3 install -r requirements.txt

# Compile smart contracts
npx hardhat compile

# Create environment file
cp .env.example .env
```

## Configuration

### 1. Edit Environment File

Open `.env` in your favorite editor:

```bash
nano .env
```

**Required Configuration:**

```env
# Wallet (use a dedicated wallet with limited funds)
PRIVATE_KEY=0xYOUR_PRIVATE_KEY_HERE

# RPC Providers (get free keys from infura.io and alchemy.com)
RPC_ETHEREUM=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
RPC_POLYGON=https://polygon-mainnet.infura.io/v3/YOUR_PROJECT_ID
ALCHEMY_RPC_ETH=https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY

# Li.Fi API Key (get free key from li.fi)
LIFI_API_KEY=your_lifi_api_key_here
```

### 2. Get Required API Keys

| Service | Purpose | Link | Cost |
|---------|---------|------|------|
| **Infura** | RPC Provider | [Get Key](https://infura.io/) | Free |
| **Alchemy** | Backup RPC | [Get Key](https://alchemy.com/) | Free |
| **Li.Fi** | Cross-chain | [Get Key](https://li.fi/) | Free |
| CoinGecko | Price feeds | [Get Key](https://coingecko.com/en/api) | Optional |

### 3. Deploy Smart Contract

Deploy to your preferred network:

```bash
# Deploy to Polygon (recommended for testing)
npx hardhat run scripts/deploy.js --network polygon

# Or deploy to other networks
npx hardhat run scripts/deploy.js --network arbitrum
npx hardhat run scripts/deploy.js --network optimism
```

Copy the deployed contract address and add it to `.env`:

```env
EXECUTOR_ADDRESS_POLYGON=0xYOUR_DEPLOYED_CONTRACT_ADDRESS
```

## Starting the System

### Option 1: Using Make (Recommended)

```bash
# Start everything
make start

# Or manually start each component
make setup    # First time setup
make compile  # Compile contracts
make health   # Check system health
make start    # Launch system
```

### Option 2: Using Shell Script

```bash
chmod +x start.sh
./start.sh
```

### Option 3: Manual Start (3 Terminals)

**Terminal 1 - Redis:**
```bash
redis-server
```

**Terminal 2 - Brain (AI Engine):**
```bash
python3 offchain/ml/brain.py
```

Expected output:
```
🧠 Booting Apex-Omega Titan Brain...
🕸️  Constructing Hyper-Graph Nodes...
✅ System Online. Tracking 256 nodes.
🚀 Titan Brain: Engaging Hyper-Parallel Scan Loop...
```

**Terminal 3 - Executor (Trading Bot):**
```bash
node offchain/execution/bot.js
```

Expected output:
```
🤖 Titan Bot Online.
Subscribed to: trade_signals
Waiting for opportunities...
```

### Option 4: Windows

```batch
start_titan_full.bat
```

## Verifying Installation

### Check System Health

```bash
# Using Make
make health

# Or manually
redis-cli ping              # Should return: PONG
python3 test_phase1.py      # Tests network connectivity
python3 audit_system.py     # Validates configuration
```

### Monitor Activity

Watch the logs to see Titan in action:

```bash
# In the Brain terminal, you'll see:
📡 Connecting to POLYGON... ✅ ONLINE | Block: 52847291
💰 PROFIT FOUND: USDC | Net: $7.23
⚡ SIGNAL BROADCASTED TO REDIS

# In the Executor terminal, you'll see:
🧪 Running Full System Simulation...
✅ Simulation SUCCESS. Estimated Gas: 285000
🚀 TX: 0x1234... | Profit: $7.23
```

## Common Issues

### Issue: Redis Connection Failed

**Solution:**
```bash
# Start Redis
redis-server

# Or on Linux
sudo systemctl start redis

# Or on macOS
brew services start redis
```

### Issue: "Cannot find module 'ethers'"

**Solution:**
```bash
npm install
```

### Issue: "No module named 'web3'"

**Solution:**
```bash
pip3 install -r requirements.txt
```

### Issue: Contract Compilation Failed

**Solution:**
```bash
# Clear cache and recompile
rm -rf cache/ artifacts/
npx hardhat compile
```

### Issue: "Insufficient funds for gas"

**Solution:**
1. Fund your wallet with native tokens (ETH, MATIC, etc.)
2. Start with testnet first (Polygon Mumbai, Goerli, etc.)
3. Adjust gas limits in `.env`

## Testing Before Mainnet

**⚠️ IMPORTANT: Test on testnet first!**

### Testnet Configuration

Update `.env` for testnet:

```env
# Polygon Mumbai Testnet
RPC_POLYGON=https://rpc-mumbai.maticvigil.com

# Get testnet funds from faucets:
# Mumbai: https://faucet.polygon.technology/
# Goerli: https://goerlifaucet.com/
```

Deploy to testnet:

```bash
npx hardhat run scripts/deploy.js --network polygonMumbai
```

## Next Steps

Once Titan is running:

1. **Monitor Performance**
   - Watch the console for profit opportunities
   - Check transaction confirmations on block explorers
   - Monitor gas costs vs. profit margins

2. **Tune Parameters** (in `.env`)
   ```env
   MIN_PROFIT_USD=5.00          # Increase for larger trades
   MAX_SLIPPAGE_BPS=50          # Adjust based on market conditions
   MAX_PRIORITY_FEE_GWEI=50     # Tune for gas efficiency
   ```

3. **Enable Advanced Features**
   ```env
   ENABLE_CROSS_CHAIN=true      # Cross-chain arbitrage
   ENABLE_MEV_PROTECTION=true   # BloxRoute integration
   ```

4. **Scale Up**
   - Deploy to multiple networks
   - Increase concurrent transactions
   - Add more DEX routers via Li.Fi discovery

## Stopping the System

```bash
# If using make
make stop

# Or press Ctrl+C in each terminal

# Or kill processes manually
pkill -f "python3 offchain/ml/brain.py"
pkill -f "node offchain/execution/bot.js"
```

## Useful Commands

```bash
# View real-time logs
tail -f logs/brain.log
tail -f logs/bot.log

# Check Redis messages
redis-cli
> SUBSCRIBE trade_signals

# View system health
make health

# Run audit
make audit

# Clean and rebuild
make clean
make compile
```

## Getting Help

- **Documentation**: See [README.md](README.md) for complete documentation
- **Issues**: Open an issue on GitHub
- **Discord**: Join the community (link in README)
- **Security**: Report vulnerabilities responsibly

## Security Checklist

Before running on mainnet:

- [ ] Using dedicated wallet (not main wallet)
- [ ] Private key stored securely (not in git)
- [ ] Tested on testnet first
- [ ] Reasonable MIN_PROFIT_USD threshold
- [ ] Gas limits configured appropriately
- [ ] Redis secured (not exposed to internet)
- [ ] `.env` file in `.gitignore`
- [ ] Limited funds in bot wallet

## Performance Tips

1. **Use WebSocket RPC** for real-time data
2. **Enable caching** to reduce API calls
3. **Tune MIN_PROFIT_USD** to focus on high-value opportunities
4. **Monitor gas prices** and adjust MAX_PRIORITY_FEE_GWEI
5. **Start with 1-2 networks** then scale up

---

**You're ready! Happy arbitraging! 🚀**

For advanced configuration and optimization, see the full [README.md](README.md).
