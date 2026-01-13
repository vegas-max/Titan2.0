# 🎯 Getting Started with Titan 2.0

Welcome to Titan 2.0! This guide will help you get up and running quickly.

## 📌 Choose Your Path

Not sure where to start? Pick the option that best fits your needs:

### 🌐 **Option 1: Try in Browser (Easiest - No Installation)**
Perfect for: First-time users who want to see Titan in action immediately

**Steps:**
1. Open [GOOGLE_COLAB_STEP_BY_STEP.md](GOOGLE_COLAB_STEP_BY_STEP.md)
2. Click the "Open in Colab" button
3. Follow the step-by-step instructions

**Time:** 10-15 minutes | **Difficulty:** ⭐ Easy

---

### 💻 **Option 2: Local Installation (Recommended)**
Perfect for: Developers who want full control and customization

**Prerequisites:**
- Node.js 18+ ([Download](https://nodejs.org/))
- Python 3.11+ ([Download](https://python.org/))
- Git ([Download](https://git-scm.com/))

**Quick Setup:**
```bash
# 1. Clone the repository
git clone https://github.com/vegas-max/Titan2.0.git
cd Titan2.0

# 2. Run the automated setup script
./setup.sh

# 3. Start Titan
./start.sh
```

**Time:** 15-20 minutes | **Difficulty:** ⭐⭐ Moderate

📖 **Detailed Instructions:** See [SETUP.md](SETUP.md) for step-by-step local installation

---

### ☁️ **Option 3: Cloud Deployment (Oracle Free Tier)**
Perfect for: Users who want a production-ready deployment in the cloud

**Steps:**
1. Create an Oracle Cloud account (free tier)
2. Follow [ORACLE_QUICKSTART.md](ORACLE_QUICKSTART.md)
3. Deploy with one command: `./deploy_oracle_cloud.sh`

**Time:** 20-30 minutes | **Difficulty:** ⭐⭐⭐ Advanced

---

### 🚀 **Option 4: One-Click Install (Windows Users)**
Perfect for: Windows users who want the simplest installation

**Steps:**
1. Download the repository
2. Double-click `install_and_run_titan.bat`
3. Follow the on-screen prompts

**Time:** 10-15 minutes | **Difficulty:** ⭐ Easy

📖 **More Details:** See [ONE_CLICK_INSTALL.md](ONE_CLICK_INSTALL.md)

---

## 📚 What's Next?

After installation, check out:

1. **[QUICKSTART.md](QUICKSTART.md)** - Quick overview of basic operations
2. **[OPERATIONS_GUIDE.md](OPERATIONS_GUIDE.md)** - Complete operations manual
3. **[MAINNET_MODES.md](MAINNET_MODES.md)** - Understanding paper vs live trading
4. **[README.md](README.md)** - Comprehensive documentation (4000+ lines)

## 🆘 Need Help?

- **Common Issues:** See [ORACLE_TROUBLESHOOTING.md](ORACLE_TROUBLESHOOTING.md)
- **Configuration:** See [Configuration Section](README.md#️-configuration)
- **Security:** See [SECURITY_SUMMARY.md](SECURITY_SUMMARY.md)

## ⚠️ Important Notes

- **Always start in PAPER mode** (simulated trading) before using real funds
- **Review security settings** before deploying to mainnet
- **Test thoroughly** in testnet/paper mode first
- **Never commit API keys** or private keys to version control

## 📊 System Requirements

### Minimum:
- **CPU:** 2 cores
- **RAM:** 4GB
- **Storage:** 10GB
- **Network:** Stable internet connection

### Recommended:
- **CPU:** 4+ cores
- **RAM:** 8GB+
- **Storage:** 20GB+ SSD
- **Network:** High-speed internet (1Gbps+)

## 🎯 Quick Commands Reference

```bash
# Check system status
./health-check.sh

# Start Titan
./start.sh

# Stop Titan (emergency)
./emergency_shutdown.sh

# View logs
tail -f logs/titan.log

# Run simulation
./run_simulation.sh
```

## 🔗 Useful Links

- [Full Documentation](README.md)
- [Architecture Overview](README.md#️-system-architecture)
- [API Documentation](offchain/README.md)
- [Security Audit](AUDIT_REPORT.md)
- [Release Notes](RELEASE_NOTES.md)

---

**Ready to dive deeper?** Head to [README.md](README.md) for the complete documentation.

**Questions?** Open an issue on [GitHub](https://github.com/vegas-max/Titan2.0/issues).
