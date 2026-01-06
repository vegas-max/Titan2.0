# 📓 TITAN 2.0 - Step-by-Step Google Colab Instructions

**Complete walkthrough for running TITAN 2.0 in Google Colab from scratch**

---

## 📋 Table of Contents

1. [Prerequisites Checklist](#prerequisites-checklist)
2. [Step-by-Step Setup](#step-by-step-setup)
3. [Troubleshooting](#troubleshooting)
4. [Next Steps](#next-steps)

---

## ✅ Prerequisites Checklist

Before you begin, gather the following information. **Print this checklist** or keep it open in another tab:

### Required Items

- [ ] **Google Account** - For accessing Google Colab
  - Already have one? ✓
  - Need to create one? Go to https://accounts.google.com/signup

- [ ] **Wallet Private Key** (64 hexadecimal characters)
  - Use a **dedicated test/trading wallet** (NOT your main wallet)
  - For PAPER mode: Any test wallet works
  - For LIVE mode: Wallet with minimal ETH/MATIC for gas only
  - Format: `0x` followed by 64 hex characters OR just 64 hex characters
  - Example: `0x1234567890abcdef...` (64 characters total after 0x)
  
- [ ] **Infura Project ID** - Free blockchain RPC access
  - Sign up: https://infura.io
  - Create new project
  - Copy your Project ID
  - Example: `abc123def456...`

### Recommended Items (Optional)

- [ ] **Alchemy API Key** - Backup RPC provider for reliability
  - Sign up: https://alchemy.com
  - Create new app
  - Copy API key
  
- [ ] **Li.Fi API Key** - For cross-chain bridge aggregation
  - Sign up: https://li.fi
  - Get free API key
  - Enables cross-chain arbitrage

- [ ] **CoinGecko API Key** - For price feeds
  - Sign up: https://www.coingecko.com/en/api
  - Get free API key

### For Production Deployment (Optional)

- [ ] **Oracle Cloud Account** - For free 24/7 hosting
  - Sign up: https://www.oracle.com/cloud/free/
  - Always Free tier: 4 vCPU, 24GB RAM

---

## 🚀 Step-by-Step Setup

### STEP 1: Open Google Colab

**Option A: Direct Upload (Easiest)**

1. Go to https://colab.research.google.com/
2. Click **File** → **Upload notebook**
3. Navigate to your downloaded Titan2.0 folder
4. Select `Titan_Google_Colab.ipynb`
5. Click **Open**

**Option B: From GitHub**

1. Go to https://colab.research.google.com/
2. Click the **GitHub** tab
3. Enter repository: `vegas-max/Titan2.0`
4. Click the search icon
5. Select `Titan_Google_Colab.ipynb` from the list

**Option C: Using Launcher Script (Windows)**

1. In your Titan2.0 folder, double-click `LAUNCH_GOOGLE_COLAB.bat`
2. Your browser will open Google Colab
3. Upload the `Titan_Google_Colab.ipynb` file when prompted

✅ **Checkpoint:** You should now see the TITAN notebook open in Google Colab

---

### STEP 2: Enable Runtime and Connect

1. At the top right, click **Connect** button
2. Wait for the connection to establish (green checkmark)
3. You'll see "Connected" with RAM and Disk usage

⏱️ **Time:** ~10-15 seconds

✅ **Checkpoint:** Green checkmark next to "Connected" in top right

---

### STEP 3: Install System Dependencies

1. Find the first code cell labeled **"Step 1: Install System Dependencies"**
2. Click the **Play button** (▶) on the left side of the cell
3. Wait for installation to complete

**What's happening:**
- Installing Node.js 18.x
- Installing Redis server
- Installing build tools

⏱️ **Time:** ~2-3 minutes

✅ **Checkpoint:** You'll see "✅ Installation complete!" with version numbers

**Troubleshooting:**
- If you see errors, click the play button again
- Some warnings are normal and can be ignored

---

### STEP 4: Clone TITAN Repository

1. Find the cell labeled **"Step 2: Clone Titan Repository"**
2. Click the **Play button** (▶)
3. Wait for cloning to complete

**What's happening:**
- Removing any existing Titan2.0 folder
- Cloning fresh copy from GitHub

⏱️ **Time:** ~30 seconds

✅ **Checkpoint:** You'll see "✅ Repository cloned successfully!"

---

### STEP 5: Install Project Dependencies

1. Find the cell labeled **"Step 3: Install Project Dependencies"**
2. Click the **Play button** (▶)
3. Wait for all packages to install

**What's happening:**
- Installing Python packages (web3, pandas, numpy, etc.)
- Installing Node.js packages (ethers.js, etc.)

⏱️ **Time:** ~3-5 minutes

✅ **Checkpoint:** You'll see "✅ All dependencies installed!"

**Troubleshooting:**
- If installation fails, try running the cell again
- Check internet connection
- Some warnings about peer dependencies are normal

---

### STEP 6: Configure Your Environment Variables

**⚠️ IMPORTANT: This is where you enter YOUR specific information**

1. Find the cell labeled **"Step 4: Configure Environment Variables"**
2. Click the **Play button** (▶)
3. **Answer each prompt carefully:**

#### Prompt 1: Execution Mode
```
Execution Mode [PAPER/LIVE] (default: PAPER):
```
- Type `PAPER` for testing (recommended) → Press Enter
- Type `LIVE` for real trading → Press Enter
- **Recommendation:** Start with PAPER mode

#### Prompt 2: Private Key
```
Private Key (hidden):
```
- **Copy** your wallet private key from your checklist
- **Paste** it here (text will be hidden for security)
- Press Enter
- **Important:** Do NOT include `0x` prefix if copying from MetaMask

#### Prompt 3: Infura Project ID
```
Infura Project ID:
```
- **Copy** your Infura Project ID from your checklist
- **Paste** it here
- Press Enter

#### Prompt 4: Alchemy API Key (Optional)
```
Alchemy API Key (optional):
```
- **If you have one:** Paste it and press Enter
- **If you don't:** Just press Enter to skip

#### Prompt 5: Li.Fi API Key (Optional)
```
Li.Fi API Key (optional):
```
- **If you have one:** Paste it and press Enter
- **If you don't:** Just press Enter to skip

⏱️ **Time:** ~1-2 minutes

✅ **Checkpoint:** You'll see a summary showing:
```
✅ Configuration saved to .env file

⚙️  Mode: PAPER
🔑 Private Key: ********************...abcd
🌐 Infura: ✓ Configured
🌉 Li.Fi: ✓ Configured (or ✗ Not set)
```

**Troubleshooting:**
- **"Invalid private key"**: Make sure it's 64 hexadecimal characters
- **"Infura required"**: You must provide an Infura Project ID
- To re-enter values: Run the cell again

---

### STEP 7: Start Redis Server (Optional)

1. Find the cell labeled **"Step 5: Start Redis Server"**
2. Click the **Play button** (▶)

**What's happening:**
- Starting Redis for real-time dashboard updates
- If Redis fails, system will use file-based signals (works fine)

⏱️ **Time:** ~5 seconds

✅ **Checkpoint:** You'll see either:
- "✅ Redis is running" - Great!
- "⚠️ Redis failed to start" - OK, system will use files

---

### STEP 8: Start TITAN Dashboard

1. Find the cell labeled **"Step 6: Start TITAN Dashboard"**
2. Click the **Play button** (▶)
3. Wait for dashboard to start

**What's happening:**
- Starting web server on port 8080
- Initializing dashboard interface
- Setting up real-time monitoring

⏱️ **Time:** ~5-10 seconds

✅ **Checkpoint:** You'll see:
```
✅ Dashboard server started!

📊 Dashboard Features:
   • Real-time market opportunities
   • Executable transaction queue
   • Live execution monitoring
   • Performance analytics
   • Cloud deployment configuration
```

---

### STEP 9: Create Public URL (Access Dashboard)

1. Find the cell labeled **"Step 7: Create Public URL"**
2. Click the **Play button** (▶)
3. **IMPORTANT:** Copy the URL that appears

**What's happening:**
- Creating public tunnel using ngrok
- Generating a URL you can access from anywhere

⏱️ **Time:** ~5-10 seconds

✅ **Checkpoint:** You'll see:
```
✅ Public URL created!

🔗 Access your dashboard at: https://xxxx-xx-xxx-xxx-xx.ngrok.io
```

**Action Required:**
1. **Copy the URL** (highlight and Ctrl+C or Cmd+C)
2. **Open it in a new tab**
3. **Bookmark it** for easy access

**What you'll see:**
- TITAN Dashboard web interface
- Real-time opportunities scanner
- System statistics
- Configuration options

---

### STEP 10: Start TITAN Brain (Intelligence Layer)

1. Find the cell labeled **"Step 8: Start TITAN Brain"**
2. Click the **Play button** (▶)
3. Brain will start running in background

**What's happening:**
- Scanning 15 blockchain networks
- Detecting arbitrage opportunities
- Running AI/ML models
- Publishing trade signals

⏱️ **Time:** ~5-10 seconds to start

✅ **Checkpoint:** You'll see:
```
✅ Brain started!

Brain is now:
   • Scanning 15 blockchain networks
   • Analyzing arbitrage opportunities
   • Running AI/ML models
   • Publishing signals for execution
```

**In the Dashboard:**
- Opportunities tab will start showing detected opportunities
- Scanner will update every few seconds

---

### STEP 11: Start TITAN Bot (Execution Layer)

1. Find the cell labeled **"Step 9: Start TITAN Bot"**
2. Click the **Play button** (▶)
3. Bot will start running in background

**What's happening:**
- Listening for trade signals from Brain
- Simulating transactions (PAPER mode) or executing (LIVE mode)
- Monitoring gas prices
- Reporting results

⏱️ **Time:** ~5-10 seconds to start

✅ **Checkpoint:** You'll see:
```
✅ Bot started!

Bot is now:
   • Listening for trade signals
   • Simulating transactions (PAPER mode)
   • Monitoring gas prices
   • Reporting results to dashboard
```

**In the Dashboard:**
- Execution monitor will show activity
- Transactions will appear as they're processed

---

### STEP 12: Monitor Your System

1. **Go to your dashboard** (the ngrok URL from Step 9)
2. **Explore the tabs:**

**Overview Tab:**
- System status
- Recent opportunities
- Quick statistics

**Market Scanner:**
- Live opportunities detected
- Profitability analysis
- Gas prices

**Execution Monitor:**
- Transaction queue
- Execution history
- Success/failure rate

**Analytics:**
- Performance metrics
- Chain comparisons
- Profit trends

**Deployment:** (For later)
- Cloud deployment wizard
- Configuration export

✅ **Checkpoint:** You should see:
- Live updates appearing
- Opportunities being scanned
- System statistics updating

---

### STEP 13: Let It Run and Monitor

**In PAPER Mode:**
- System will simulate trades
- No real money spent
- Monitor for 10-30 minutes to see results
- Check execution success rate

**In LIVE Mode:**
- ⚠️ **Make sure you understand the risks**
- System will execute REAL transactions
- Monitor carefully
- Start with minimal funds

**What to watch:**
1. **Opportunities detected** - Should see several per minute
2. **Execution attempts** - Bot trying to execute profitable ones
3. **Success rate** - How many succeed vs fail
4. **Gas costs** - Monitor to ensure they're reasonable
5. **Profit** - In PAPER mode, simulated profit

⏱️ **Recommended:** Let run for at least 15-30 minutes

---

### STEP 14: Stop the System (When Done)

When you want to stop TITAN:

1. Find the cell labeled **"Step 12: Stop System"**
2. Click the **Play button** (▶)
3. Wait for confirmation

⏱️ **Time:** ~5 seconds

✅ **Checkpoint:** You'll see:
```
✅ System stopped
```

**What's happening:**
- Stopping Brain (Python processes)
- Stopping Bot (Node.js processes)
- Stopping Dashboard
- Stopping Redis

**To restart:**
- Just run the Start cells (Steps 8-11) again
- Configuration is saved, no need to re-enter

---

## 🔍 Troubleshooting

### Common Issues

#### 1. "Module not found" errors

**Problem:** Python or Node packages not installed

**Solution:**
```python
# Run in a new cell:
!pip install -r /content/Titan2.0/requirements.txt
!cd /content/Titan2.0 && npm install --legacy-peer-deps
```

#### 2. "Invalid private key" error

**Problem:** Private key format incorrect

**Solution:**
- Remove `0x` prefix if present
- Make sure it's exactly 64 hexadecimal characters
- Use dedicated test wallet, not your main wallet

#### 3. Dashboard URL not working

**Problem:** ngrok tunnel failed or expired

**Solution:**
- Re-run Step 9 to get a new URL
- Or use Colab's built-in port forwarding:
  - Click the 🔌 icon in left sidebar
  - Find port 8080
  - Click the link

#### 4. No opportunities detected

**Problem:** RPC providers not responding or rate limiting

**Possible causes:**
- Infura rate limit reached (100k requests/day on free tier)
- Invalid API keys
- Network connectivity issues

**Solution:**
- Add Alchemy API key for backup
- Wait a few minutes
- Check Infura dashboard for rate limits

#### 5. "Redis connection failed"

**Problem:** Redis server not starting

**Solution:**
- This is OK! System will use file-based signals
- Dashboard real-time updates may be slower
- Execution will still work fine

#### 6. Session timeout / Runtime disconnected

**Problem:** Colab sessions timeout after 12 hours

**Solution:**
- Save your configuration first
- For 24/7 operation, deploy to Oracle Cloud (see Step 15)
- Reconnect and re-run cells to restart

#### 7. "Error: command not found"

**Problem:** System dependencies not installed

**Solution:**
- Re-run Step 1 (Install System Dependencies)
- Make sure it completes successfully

---

## 🎓 Understanding the Dashboard

### Key Metrics to Watch

**Opportunities Detected:**
- How many price differences found
- Higher volatility = more opportunities

**Execution Success Rate:**
- Percentage of trades that succeed
- 70-90% is normal (some fail due to gas, slippage)

**Average Profit per Trade:**
- In PAPER mode: Simulated profit
- In LIVE mode: Actual profit minus gas

**Gas Costs:**
- Monitor to ensure profitable after gas
- Adjust `MAX_BASE_FEE_GWEI` if too high

### Understanding Execution States

**DETECTED:** Opportunity found
**ANALYZING:** Calculating profitability
**APPROVED:** Profitable, sending to Bot
**SIMULATING:** Testing transaction
**EXECUTING:** Submitting to blockchain (LIVE) or simulating (PAPER)
**SUCCESS:** Transaction succeeded
**FAILED:** Transaction failed (gas, slippage, etc.)

---

## 🚀 Next Steps

### After Testing in Google Colab

Once you've tested TITAN in Colab and are ready for 24/7 operation:

#### Option 1: Deploy to Oracle Cloud Free Tier (Recommended)

**Why Oracle Cloud:**
- ✅ FREE forever (Always Free tier)
- ✅ 4 vCPU, 24GB RAM
- ✅ 200GB storage
- ✅ 24/7 uptime
- ✅ No session timeouts

**How to deploy:**
1. In dashboard, click **Deployment** tab
2. Select **Oracle Cloud Free Tier**
3. Follow the step-by-step wizard
4. Download the generated deployment script
5. Run on your Oracle instance

**Detailed guide:** See `ORACLE_CLOUD_DEPLOYMENT.md`

#### Option 2: Run Locally

**Requirements:**
- Computer that stays on 24/7
- Stable internet connection
- 4GB+ RAM

**How to deploy:**
1. Clone repository: `git clone https://github.com/vegas-max/Titan2.0.git`
2. Copy your `.env` from Colab
3. Run: `./setup.sh`
4. Run: `make start`

**Detailed guide:** See `QUICKSTART.md`

#### Option 3: Other Cloud Providers

**Supported:**
- AWS EC2 (~$30/month)
- Google Cloud (~$25/month)
- Azure VMs (~$30/month)

**How to deploy:**
Use the dashboard deployment wizard to generate scripts

---

## 📚 Additional Resources

### Documentation
- **README.md** - Complete system overview
- **GOOGLE_COLAB_GUIDE.md** - Extended Colab guide
- **QUICKSTART.md** - 15-minute local setup
- **ORACLE_CLOUD_DEPLOYMENT.md** - Oracle Cloud guide
- **OPERATIONS_GUIDE.md** - System operations

### Community
- **GitHub Repository:** https://github.com/vegas-max/Titan2.0
- **Issues:** https://github.com/vegas-max/Titan2.0/issues
- **Discussions:** https://github.com/vegas-max/Titan2.0/discussions

---

## ⚠️ Important Reminders

### Security

- ✅ Use dedicated wallet (NOT your main wallet)
- ✅ Keep private key secure
- ✅ Never share your .env file
- ✅ Start with PAPER mode
- ✅ Use minimal funds in LIVE mode

### Expectations

- ✅ PAPER mode has no risk (simulated trading)
- ✅ LIVE mode has real risks (can lose money)
- ✅ Not all opportunities will be profitable
- ✅ Gas costs can exceed small profits
- ✅ Market conditions affect results

### Google Colab Limitations

- ⚠️ Sessions timeout after 12 hours
- ⚠️ Not suitable for 24/7 production
- ⚠️ Good for testing and learning
- ⚠️ Deploy to cloud for real trading

---

## ✅ Success Checklist

By the end of this guide, you should have:

- [x] TITAN running in Google Colab
- [x] Dashboard accessible via public URL
- [x] Brain scanning for opportunities
- [x] Bot executing trades (simulated or real)
- [x] Understanding of system metrics
- [x] Configuration saved for future use
- [x] Plan for production deployment (if needed)

---

## 🎉 Congratulations!

You've successfully set up TITAN 2.0 in Google Colab!

**Questions or issues?**
- Check the Troubleshooting section above
- Review the detailed guides in the repository
- Open an issue on GitHub
- Join the community discussions

**Ready for production?**
- Follow the Oracle Cloud deployment guide
- Start with PAPER mode
- Test thoroughly before using LIVE mode
- Monitor carefully and adjust parameters

---

**Built with ❤️ by the Titan Team**

⭐ **Star the repo if this guide helped you!** ⭐

[GitHub](https://github.com/vegas-max/Titan2.0) • [Documentation](https://github.com/vegas-max/Titan2.0/wiki) • [Issues](https://github.com/vegas-max/Titan2.0/issues)
