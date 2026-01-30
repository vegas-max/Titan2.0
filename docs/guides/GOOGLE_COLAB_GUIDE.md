# 🚀 TITAN 2.0 - Google Colab Setup Guide

Complete guide for running TITAN 2.0 in Google Colab with cloud deployment capabilities.

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Step-by-Step Setup](#step-by-step-setup)
- [Dashboard Features](#dashboard-features)
- [Cloud Deployment](#cloud-deployment)
- [Troubleshooting](#troubleshooting)
- [Limitations](#limitations)
- [FAQ](#faq)

---

## 🎯 Overview

The Google Colab integration allows you to:
- ✅ Run TITAN 2.0 without local installation
- ✅ Test the system in a cloud environment
- ✅ Configure deployment to production cloud instances
- ✅ Access interactive dashboard with deployment wizard
- ✅ Generate deployment scripts for Oracle, AWS, GCP, Azure

### When to Use Google Colab

**✅ Recommended For:**
- Testing and learning the system
- Configuring production deployment
- Paper mode trading experiments
- Short-term development work

**❌ Not Recommended For:**
- Production 24/7 trading (sessions timeout after 12 hours)
- Live trading with significant capital
- Long-term operations requiring high uptime

**For Production:** Deploy to Oracle Cloud Free Tier (4 vCPU, 24GB RAM, free forever)

---

## ⚡ Quick Start

### Method 1: Using Windows Launcher (Easiest)

1. Double-click `LAUNCH_GOOGLE_COLAB.bat`
2. Upload the notebook to Google Colab
3. Follow the cells step-by-step
4. Configure your settings when prompted

### Method 2: Direct Upload

1. Go to https://colab.research.google.com/
2. Click **File** → **Upload notebook**
3. Select `Titan_Google_Colab.ipynb` from your Titan2.0 folder
4. Run cells in order

### Method 3: From GitHub

1. Go to https://colab.research.google.com/
2. Click **GitHub** tab
3. Enter: `vegas-max/Titan2.0`
4. Select `Titan_Google_Colab.ipynb`

---

## 🔧 Prerequisites

Before starting, prepare:

### Required
- [ ] **Google Account** (for Colab access)
- [ ] **Wallet Private Key** (dedicated test/trading wallet)
- [ ] **Infura Project ID** (free at https://infura.io)

### Recommended
- [ ] **Alchemy API Key** (free at https://alchemy.com)
- [ ] **Li.Fi API Key** (for cross-chain, free at https://li.fi)

### Optional
- [ ] **Oracle Cloud Account** (for production deployment)
- [ ] **ngrok Account** (for public dashboard access)

---

## 📝 Step-by-Step Setup

### Step 1: Open the Notebook

Choose one of the quick start methods above to open the notebook in Google Colab.

### Step 2: Install System Dependencies

Run the first cell to install:
- Node.js 18.x
- Redis server
- Build tools
- Git

**Time:** ~2-3 minutes

### Step 3: Clone Repository

The notebook will automatically clone the TITAN repository from GitHub.

**Time:** ~30 seconds

### Step 4: Install Project Dependencies

Install Python and Node.js dependencies:
- Python packages from requirements.txt
- Node.js packages from package.json

**Time:** ~3-5 minutes

### Step 5: Configure Environment

**Important:** Enter your configuration carefully

```
Execution Mode: PAPER or LIVE
  - PAPER: Simulated trading (recommended for testing)
  - LIVE: Real blockchain execution (requires funds)

Private Key: Your wallet private key
  - Use dedicated wallet (not your main wallet)
  - For PAPER mode: Test wallet is fine
  - For LIVE mode: Use wallet with minimal funds

Infura Project ID: Your Infura project ID
  - Get free at https://infura.io
  - Required for blockchain RPC access

Alchemy API Key: (optional but recommended)
  - Backup RPC provider for failover
  - Get free at https://alchemy.com

Li.Fi API Key: (optional)
  - For cross-chain bridge aggregation
  - Get free at https://li.fi
```

### Step 6: Start Redis (Optional)

Start Redis server for dashboard real-time updates. If Redis fails, the system will use file-based signals (works fine).

### Step 7: Start Dashboard

Launch the interactive dashboard server:
- Provides real-time monitoring
- Cloud deployment configuration
- Performance analytics
- Control interface

**Access:** Dashboard runs on port 8080

### Step 8: Create Public URL (Optional)

Use ngrok to create a public URL for external access:
- Allows accessing dashboard from anywhere
- Useful for mobile monitoring
- Free tier available

### Step 9: Start TITAN Brain

Start the intelligence layer:
- Scans 15 blockchain networks
- Detects arbitrage opportunities
- Runs AI/ML models
- Publishes trade signals

### Step 10: Start TITAN Bot

Start the execution layer:
- Listens for trade signals
- Simulates transactions (PAPER mode)
- Executes transactions (LIVE mode)
- Reports results to dashboard

### Step 11: Monitor System

Access the dashboard to:
- View real-time opportunities
- Monitor executions
- Check system metrics
- Analyze performance

### Step 12: Configure Cloud Deployment

Use the dashboard's **Deployment** section to:
1. Select cloud provider (Oracle recommended)
2. Configure instance settings
3. Generate deployment script
4. Deploy to production

---

## 🎛️ Dashboard Features

The TITAN dashboard provides comprehensive monitoring and control:

### Pages

1. **Overview**
   - System status
   - Key metrics
   - Recent activity
   - Performance summary

2. **Market Scanner**
   - Real-time opportunities
   - Profitability analysis
   - DEX comparisons
   - Gas price monitoring

3. **Execution Monitor**
   - Transaction queue
   - Execution history
   - Success/failure tracking
   - Profit/loss reporting

4. **Analytics**
   - Performance metrics
   - ML model statistics
   - Chain comparisons
   - Token performance

5. **Deployment** ⭐ NEW
   - Cloud provider selection
   - Configuration wizard
   - Script generation
   - Deployment instructions

### Deployment Configuration

#### Oracle Cloud Free Tier (Recommended)

1. Click **Deployment** tab in dashboard
2. Select **Oracle Cloud Free Tier**
3. Review specifications:
   - 4 vCPU (Ampere ARM)
   - 24GB RAM
   - 200GB storage
   - Free forever

4. Configure settings:
   - Execution mode (PAPER/LIVE)
   - API keys
   - Network selection
   - Optional features

5. Generate deployment script
6. Download script
7. Follow deployment instructions

#### Other Cloud Providers

Dashboard supports:
- **AWS EC2** (t3.medium, ~$30/month)
- **Google Cloud** (e2-medium, ~$25/month)
- **Azure VM** (B2s, ~$30/month)

Same configuration wizard process as Oracle.

---

## ☁️ Cloud Deployment

### Why Deploy to Cloud?

Google Colab is great for testing, but production requires:
- ✅ 24/7 uptime
- ✅ No session timeouts
- ✅ Dedicated resources
- ✅ Better performance
- ✅ Persistent storage

### Oracle Cloud Free Tier Deployment

**Complete Process:**

1. **Create Oracle Cloud Account**
   - Sign up at https://www.oracle.com/cloud/free/
   - Verify identity (credit card required but not charged)
   - Access Always Free tier

2. **Create Compute Instance**
   - Navigate to **Compute** → **Instances**
   - Click **Create Instance**
   - Select **VM.Standard.A1.Flex** (ARM)
   - Configure: 4 OCPU, 24GB RAM
   - Choose Ubuntu 22.04
   - Add your SSH key

3. **Configure Networking**
   - Add ingress rule for port 8080 (dashboard)
   - Add ingress rule for port 22 (SSH)
   - Note your public IP address

4. **Run Deployment Script**
   ```bash
   # SSH into your instance
   ssh ubuntu@YOUR_INSTANCE_IP
   
   # Download generated script
   # (Script generated from dashboard)
   wget YOUR_SCRIPT_URL -O deploy_oracle.sh
   
   # Make executable
   chmod +x deploy_oracle.sh
   
   # Run deployment
   ./deploy_oracle.sh
   ```

5. **Start Services**
   ```bash
   sudo systemctl start titan-brain
   sudo systemctl start titan-bot
   sudo systemctl start titan-dashboard
   ```

6. **Access Dashboard**
   - Open browser: `http://YOUR_INSTANCE_IP:8080`
   - Monitor system in real-time
   - Configure from anywhere

### Manual Deployment

For complete manual deployment instructions, see:
- `ORACLE_CLOUD_DEPLOYMENT.md` - Oracle Cloud guide
- `OPERATIONS_GUIDE.md` - General operations
- `MAINNET_QUICKSTART.md` - Quick mainnet setup

---

## 🔍 Troubleshooting

### Common Issues

#### 1. Dependencies Installation Fails

**Problem:** Package installation errors

**Solution:**
```bash
# In Colab cell:
!apt-get update
!apt-get install -y build-essential python3-dev
!pip install --upgrade pip
!pip install -r requirements.txt
```

#### 2. Node.js Version Error

**Problem:** Wrong Node.js version

**Solution:**
```bash
# Install Node.js 18.x specifically
!curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
!apt-get install -y nodejs
!node --version  # Should show v18.x
```

#### 3. Redis Connection Failed

**Problem:** Redis not starting

**Solution:**
- Redis is optional
- System will use file-based signals
- To fix Redis:
  ```bash
  !redis-server --daemonize yes
  !redis-cli ping  # Should return PONG
  ```

#### 4. Dashboard Not Accessible

**Problem:** Can't access dashboard URL

**Solution:**
- Use ngrok for public URL (see Step 8 in notebook)
- Or access via Colab's built-in preview
- Check firewall settings

#### 5. Private Key Error

**Problem:** Invalid private key format

**Solution:**
- Remove `0x` prefix if present
- Ensure 64 hexadecimal characters
- Use dedicated wallet for testing
- Never use your main wallet

#### 6. RPC Rate Limiting

**Problem:** Too many requests to RPC

**Solution:**
- Use both Infura and Alchemy
- System will failover automatically
- Consider paid RPC plan for production

#### 7. Session Timeout

**Problem:** Colab session expires

**Solution:**
- This is normal after 12 hours inactivity
- For 24/7 operations, deploy to cloud
- Save configuration before timeout
- Re-run cells to restart

---

## ⚠️ Limitations

### Google Colab Limitations

1. **Session Timeout**
   - 12 hours maximum with inactivity
   - Runtime may be recycled
   - Not suitable for 24/7 operations

2. **Resource Limits**
   - Shared resources
   - May be slower than dedicated instance
   - GPU not utilized by TITAN

3. **Network Access**
   - Some ports restricted
   - ngrok required for public access
   - Firewall limitations

4. **Storage**
   - Session storage is temporary
   - Files deleted when session ends
   - Must backup important data

### Recommendations

- ✅ Use Colab for testing and learning
- ✅ Configure deployment via dashboard
- ✅ Deploy to Oracle Cloud for production
- ✅ Start with PAPER mode
- ✅ Test thoroughly before LIVE mode

---

## ❓ FAQ

### General Questions

**Q: Is Google Colab free?**  
A: Yes, Google Colab provides free access with some limitations. Pro/Pro+ plans available for extended resources.

**Q: Can I run TITAN 24/7 in Colab?**  
A: No, Colab sessions timeout. For 24/7 operations, deploy to Oracle Cloud Free Tier or other cloud provider.

**Q: Is my private key safe in Colab?**  
A: Private keys are stored in session memory only. However, for maximum security, use a dedicated wallet and deploy to your own cloud instance for production.

**Q: Do I need to install anything on my computer?**  
A: No, everything runs in the cloud. Just need a web browser.

### Setup Questions

**Q: How long does setup take?**  
A: Initial setup: ~10-15 minutes. Includes all installations and configuration.

**Q: What if I don't have an Infura account?**  
A: You need Infura for RPC access. Sign up free at https://infura.io (takes 2 minutes).

**Q: Can I use the system without Redis?**  
A: Yes, TITAN uses file-based signals if Redis is unavailable. Redis is only for optional dashboard features.

**Q: Do I need all the API keys?**  
A: Only Infura is required. Alchemy (backup RPC) and Li.Fi (bridges) are optional but recommended.

### Usage Questions

**Q: Should I use PAPER or LIVE mode?**  
A: Always start with PAPER mode to test. Only use LIVE mode after thorough testing and understanding of risks.

**Q: How do I monitor the system?**  
A: Access the dashboard via the public URL. Shows real-time opportunities, executions, and metrics.

**Q: Can I stop and restart?**  
A: Yes, run the stop cell and restart cells as needed. Configuration is saved in .env file.

**Q: What happens when my Colab session expires?**  
A: You'll need to re-run all cells. Export your configuration first to save settings.

### Deployment Questions

**Q: Why deploy to cloud if Colab works?**  
A: Production requires 24/7 uptime, dedicated resources, and no session timeouts. Colab is for testing only.

**Q: Is Oracle Cloud really free?**  
A: Yes, Always Free tier is genuinely free forever. No charges for 4 vCPU ARM instance with 24GB RAM.

**Q: Can I deploy to AWS/GCP/Azure instead?**  
A: Yes, dashboard generates scripts for all major providers. Oracle Free Tier is recommended for cost.

**Q: How long does cloud deployment take?**  
A: Oracle deployment: ~30 minutes including instance creation and setup.

**Q: Do I need to reconfigure in cloud?**  
A: No, deployment script includes your configuration from Colab dashboard. Just update private key if needed.

### Trading Questions

**Q: How much profit can I make?**  
A: Profitability depends on market conditions, competition, and capital. See README.md for testnet results. No guarantees.

**Q: Do I need capital to start?**  
A: For PAPER mode: No capital needed (simulated). For LIVE mode: Need ETH/MATIC for gas fees. Flash loans require no trading capital.

**Q: Is this legal?**  
A: Arbitrage trading is legal. Users responsible for compliance with local regulations.

**Q: What are the risks?**  
A: All trading carries risk of loss. Smart contract risks, MEV risks, gas costs. Start small, test thoroughly. See disclaimer in README.

---

## 📚 Additional Resources

### Documentation
- **README.md** - Complete system overview
- **QUICKSTART.md** - 15-minute local setup
- **ORACLE_CLOUD_DEPLOYMENT.md** - Detailed Oracle deployment
- **OPERATIONS_GUIDE.md** - System operations manual
- **MAINNET_MODES.md** - PAPER vs LIVE mode guide

### Guides
- **INSTALLATION_COMPLETE.md** - Installation reference
- **DASHBOARD_GUIDE.md** - Dashboard user guide
- **SECURITY_SUMMARY.md** - Security features
- **TROUBLESHOOTING.md** - Common issues

### Community
- **GitHub Issues** - Report bugs, ask questions
- **GitHub Discussions** - Community forum
- **GitHub Repository** - Source code, updates

---

## 🔒 Security Best Practices

1. **Use Dedicated Wallet**
   - Never use your main wallet
   - Create new wallet for TITAN only
   - Keep private key secure

2. **Start Small**
   - Test thoroughly in PAPER mode
   - Start with minimal funds in LIVE mode
   - Scale up gradually

3. **Monitor Regularly**
   - Check dashboard frequently
   - Review logs and metrics
   - Set up alerts if possible

4. **Keep Updated**
   - Pull latest changes from GitHub
   - Update dependencies regularly
   - Follow security advisories

5. **Secure Deployment**
   - Use strong SSH keys
   - Configure firewall properly
   - Enable fail2ban on cloud instance
   - Use HTTPS for dashboard (production)

---

## ⚠️ Disclaimer

- **Experimental software** - Use at your own risk
- **No guarantees** - No guarantee of profit or uptime
- **Financial risk** - Can lose money through gas costs and failed trades
- **Test thoroughly** - Always test in PAPER mode first
- **Professional audit** - Recommended before large-scale deployment
- **Legal compliance** - User responsible for regulatory compliance

By using this software, you acknowledge and accept all risks.

---

## 📄 License

MIT License - See LICENSE file in repository

---

**Built with ❤️ by the Titan Team**

⭐ **Star the repo if this guide helped you!**

[GitHub](https://github.com/vegas-max/Titan2.0) • [Documentation](https://github.com/vegas-max/Titan2.0/wiki) • [Issues](https://github.com/vegas-max/Titan2.0/issues)
