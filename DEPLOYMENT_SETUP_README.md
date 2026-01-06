# 🚀 TITAN 2.0 Deployment Setup Scripts

This directory contains scripts and guides to help you set up TITAN 2.0 with all the necessary prerequisites.

## 📋 Quick Start

### For Google Colab (Easiest - No Installation)

**Recommended for beginners and testing!**

1. **Read the step-by-step guide first:**
   - Open [GOOGLE_COLAB_STEP_BY_STEP.md](GOOGLE_COLAB_STEP_BY_STEP.md)
   - Follow each step carefully

2. **Gather your prerequisites:**
   - Use [DEPLOYMENT_PREREQUISITES_CHECKLIST.md](DEPLOYMENT_PREREQUISITES_CHECKLIST.md) as a reference
   - Fill in your API keys, private key, etc.

3. **Launch Google Colab:**
   - **Windows:** Double-click `LAUNCH_GOOGLE_COLAB.bat`
   - **Linux/Mac:** Run `./launch_google_colab.sh`
   - Or manually upload `Titan_Google_Colab.ipynb` to https://colab.research.google.com/

### For Local Installation (Linux/Mac)

**For users who want to run TITAN locally:**

1. **Run the interactive setup wizard:**
   ```bash
   ./deployment_prerequisites_setup.sh
   ```

2. **Follow the prompts:**
   - Enter your API keys when prompted
   - Provide your wallet private key (securely hidden)
   - Configure optional features
   - Script will generate `.env` file automatically

3. **Install and start TITAN:**
   ```bash
   ./setup.sh
   make start
   ```

### For Local Installation (Windows)

**For Windows users:**

1. **Option A: Use WSL (Recommended)**
   - Install WSL: `wsl --install` in PowerShell (as Admin)
   - Restart computer
   - Follow Linux/Mac instructions above

2. **Option B: Use Google Colab**
   - Double-click `LAUNCH_GOOGLE_COLAB.bat`
   - Follow the Colab guide

3. **Option C: Manual Setup**
   - Double-click `SETUP_DEPLOYMENT_PREREQUISITES.bat`
   - Choose manual editing option
   - Edit `.env` file with your values

## 📚 Documentation Files

### Setup Scripts

| File | Purpose | Platform |
|------|---------|----------|
| `deployment_prerequisites_setup.sh` | Interactive wizard for collecting prerequisites | Linux/Mac/WSL |
| `SETUP_DEPLOYMENT_PREREQUISITES.bat` | Windows launcher script | Windows |
| `launch_google_colab.sh` | Opens Google Colab in browser | Linux/Mac |
| `LAUNCH_GOOGLE_COLAB.bat` | Opens Google Colab in browser | Windows |

### Documentation

| File | Purpose | When to Use |
|------|---------|-------------|
| `GOOGLE_COLAB_STEP_BY_STEP.md` | **⭐ Detailed step-by-step walkthrough** | First time using Colab |
| `GOOGLE_COLAB_GUIDE.md` | Complete Colab guide | Reference for Colab features |
| `DEPLOYMENT_PREREQUISITES_CHECKLIST.md` | **Quick reference card** | Print/keep open during setup |
| `README.md` | Main project documentation | Overview and all features |
| `QUICKSTART.md` | 15-minute setup guide | Local installation |

## 🎯 Which Path Should I Choose?

### Choose Google Colab if:
- ✅ You're new to TITAN
- ✅ You want to test without installing anything
- ✅ You don't have a server or computer that runs 24/7
- ✅ You want to configure cloud deployment

### Choose Local Installation if:
- ✅ You have a computer/server that runs 24/7
- ✅ You're comfortable with terminal/command line
- ✅ You want full control over the environment
- ✅ You're deploying to production

### Choose Oracle Cloud if:
- ✅ You want free 24/7 hosting (Always Free tier)
- ✅ You're ready for production deployment
- ✅ You've tested in Colab/locally first

## 📝 Prerequisites Needed

### Required (Must Have)

1. **Wallet Private Key** (64 hex characters)
   - Use a DEDICATED wallet (NOT your main wallet)
   - For testing: Any test wallet
   - For production: Wallet with minimal funds for gas

2. **Infura Project ID**
   - Sign up free: https://infura.io
   - Create a project
   - Copy the Project ID

### Recommended (Optional but Helpful)

3. **Alchemy API Key** - Backup RPC provider
   - Sign up free: https://alchemy.com

4. **Li.Fi API Key** - Cross-chain bridges
   - Get free key: https://li.fi

5. **CoinGecko API Key** - Price feeds
   - Get free key: https://www.coingecko.com/en/api

### Advanced (For Production)

6. **BloxRoute Auth** - MEV protection
7. **1inch API Key** - DEX aggregation
8. **0x API Key** - Swap aggregation

## 🔒 Security Best Practices

### DO ✅
- Use a dedicated wallet (NOT your main wallet)
- Keep your private key secure
- Start with PAPER mode for testing
- Use minimal funds in LIVE mode
- Never commit `.env` to version control
- Double-check all values before saving

### DON'T ❌
- Share your private key with anyone
- Use your main wallet
- Start with LIVE mode
- Skip testing in PAPER mode
- Commit `.env` file to Git
- Use large amounts of money for testing

## 🚀 Next Steps After Setup

### 1. Test in PAPER Mode
- Run the system for 15-30 minutes
- Monitor opportunities and executions
- Check success rate and profitability
- Verify all components working

### 2. Review Results
- Check dashboard metrics
- Analyze execution history
- Review gas costs
- Understand profit potential

### 3. Deploy to Production (Optional)
- Use Oracle Cloud Free Tier (recommended)
- Or run locally on dedicated server
- Start with PAPER mode even in production
- Gradually transition to LIVE mode with minimal funds

## 📖 Support & Resources

### Getting Help
- **Step-by-step guide:** GOOGLE_COLAB_STEP_BY_STEP.md
- **Quick reference:** DEPLOYMENT_PREREQUISITES_CHECKLIST.md
- **Complete docs:** README.md
- **GitHub Issues:** https://github.com/vegas-max/Titan2.0/issues

### Community
- **Discussions:** https://github.com/vegas-max/Titan2.0/discussions
- **Repository:** https://github.com/vegas-max/Titan2.0

## ⚠️ Important Notes

### Google Colab Limitations
- Sessions timeout after 12 hours of inactivity
- Not suitable for production 24/7 operations
- Perfect for testing and learning
- Can configure cloud deployment from Colab

### System Requirements
- **For Colab:** Just a web browser
- **For Local:** 4GB+ RAM, stable internet
- **For Production:** 8GB+ RAM, 24/7 uptime

### Cost Considerations
- **Colab:** Free (with limitations)
- **Local:** Electricity + internet costs
- **Oracle Cloud Free Tier:** $0/month forever (4 vCPU, 24GB RAM)
- **Other Clouds:** $25-50/month typically

## 🎉 Quick Start Summary

**Absolute Beginner (No Installation):**
1. Read: GOOGLE_COLAB_STEP_BY_STEP.md
2. Use: DEPLOYMENT_PREREQUISITES_CHECKLIST.md for reference
3. Run: LAUNCH_GOOGLE_COLAB.bat (Windows) or ./launch_google_colab.sh (Mac/Linux)

**Intermediate (Local Setup):**
1. Run: ./deployment_prerequisites_setup.sh
2. Install: ./setup.sh
3. Start: make start

**Advanced (Production):**
1. Test in Colab first
2. Configure deployment via dashboard
3. Deploy to Oracle Cloud Free Tier
4. Monitor and scale gradually

---

**Built with ❤️ by the Titan Team**

⭐ **Star the repo if these guides helped you!** ⭐

[GitHub](https://github.com/vegas-max/Titan2.0) • [Documentation](https://github.com/vegas-max/Titan2.0/wiki) • [Issues](https://github.com/vegas-max/Titan2.0/issues)
