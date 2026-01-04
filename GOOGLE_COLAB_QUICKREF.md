# 🚀 TITAN Google Colab - Quick Reference

One-page reference for using TITAN 2.0 with Google Colab.

## ⚡ Quick Start

### Windows
```batch
LAUNCH_GOOGLE_COLAB.bat
```

### Linux/Mac
```bash
./launch_google_colab.sh
```

### Manual
1. Go to https://colab.research.google.com/
2. Upload `Titan_Google_Colab.ipynb`
3. Run cells in order

---

## 📋 Setup Checklist

Before starting, have ready:

- [ ] Google Account
- [ ] Wallet Private Key (dedicated wallet)
- [ ] Infura Project ID (https://infura.io)
- [ ] Alchemy API Key (optional, https://alchemy.com)
- [ ] Li.Fi API Key (optional, https://li.fi)

---

## 🔧 Configuration

### Execution Modes

**PAPER Mode** (Recommended)
- Simulated trading
- No real funds needed
- Perfect for testing
- All features work

**LIVE Mode** (Advanced)
- Real blockchain execution
- Requires gas funds
- Start with minimal amounts
- Use only after thorough testing

### Required Settings

```
EXECUTION_MODE=PAPER
PRIVATE_KEY=your_64_char_hex_key
INFURA_PROJECT_ID=your_infura_id
```

### Optional Settings

```
ALCHEMY_API_KEY=your_alchemy_key
LIFI_API_KEY=your_lifi_key
ENABLE_CROSS_CHAIN=false
ENABLE_MEV_PROTECTION=false
```

---

## 🎛️ Dashboard Access

### Local (Colab Only)
- Dashboard runs on port 8080
- Limited to Colab session

### Public URL (ngrok)
1. Run the ngrok cell in notebook
2. Get public URL from output
3. Access from anywhere
4. URL expires with session

### Features

- Real-time market opportunities
- Transaction execution monitor
- Performance analytics
- ML model metrics
- **Cloud deployment configuration** ⭐

---

## ☁️ Cloud Deployment

### Why Deploy?

Colab is for testing. Production needs:
- 24/7 uptime
- No session timeouts
- Dedicated resources
- Better performance

### Oracle Cloud Free Tier (Recommended)

**Specs:**
- 4 vCPU (Ampere ARM)
- 24GB RAM
- 200GB storage
- **Free forever**

**Steps:**
1. Open dashboard
2. Go to **Deployment** tab
3. Select **Oracle Cloud Free Tier**
4. Configure settings
5. Generate script
6. Download and run on Oracle instance

**Time:** ~30 minutes total

### Other Providers

Dashboard supports:
- AWS EC2 (~$30/month)
- Google Cloud (~$25/month)
- Azure VM (~$30/month)

---

## 🔍 Common Issues

### Dependencies fail
```bash
!apt-get update
!pip install --upgrade pip
!pip install -r requirements.txt
```

### Redis not working
- Redis is optional
- System uses file-based signals
- Skip Redis cell if fails

### Dashboard not accessible
- Use ngrok cell for public URL
- Check firewall settings
- Try restarting dashboard cell

### Private key error
- Remove `0x` prefix
- Must be 64 hex characters
- Use dedicated wallet

### Session timeout
- Normal after 12 hours
- Save configuration
- Re-run cells to restart
- Deploy to cloud for 24/7

---

## 📊 Monitoring

### Check System Status

View in dashboard:
- Opportunities found
- Executions attempted
- Success rate
- Profit/loss
- Gas costs

### Check Logs

In Colab cells:
- Brain logs (opportunity detection)
- Bot logs (execution)
- Dashboard logs (server status)

---

## 🛑 Stop System

Run the stop cell in notebook:
```bash
!pkill -f mainnet_orchestrator.py
!pkill -f bot.js
!pkill -f dashboard_server.py
!redis-cli shutdown
```

---

## 📚 Full Documentation

- **[GOOGLE_COLAB_GUIDE.md](GOOGLE_COLAB_GUIDE.md)** - Complete guide
- **[README.md](README.md)** - Full system documentation
- **[ORACLE_CLOUD_DEPLOYMENT.md](ORACLE_CLOUD_DEPLOYMENT.md)** - Cloud deployment
- **[OPERATIONS_GUIDE.md](OPERATIONS_GUIDE.md)** - System operations

---

## ⚠️ Important Notes

### Security
- Use dedicated wallet (not main wallet)
- Never share private keys
- Start with PAPER mode
- Test thoroughly before LIVE mode

### Limitations
- 12-hour session timeout
- Shared Colab resources
- Not for production 24/7
- Use cloud deployment for production

### Best Practices
- Always start with PAPER mode
- Configure cloud deployment
- Monitor regularly
- Keep API keys secure
- Backup important data

---

## 🎯 Recommended Workflow

1. **Test in Colab** (1-2 hours)
   - Run PAPER mode
   - Learn the system
   - Monitor dashboard
   - Understand features

2. **Configure Deployment** (15 minutes)
   - Use dashboard deployment tab
   - Select Oracle Free Tier
   - Generate deployment script
   - Review configuration

3. **Deploy to Cloud** (30 minutes)
   - Create Oracle Cloud instance
   - Run deployment script
   - Start services
   - Access dashboard from anywhere

4. **Production Operation** (ongoing)
   - Monitor via cloud dashboard
   - Start with PAPER mode
   - Gradually test LIVE mode
   - Scale up carefully

---

## 📞 Support

- **Issues:** https://github.com/vegas-max/Titan2.0/issues
- **Discussions:** https://github.com/vegas-max/Titan2.0/discussions
- **Docs:** See repository README.md

---

## 🔒 Disclaimer

- Experimental software
- Use at own risk
- No profit guarantees
- Test thoroughly
- Start small
- Professional audit recommended

---

**Built with ❤️ by the Titan Team**

⭐ Star the repo: https://github.com/vegas-max/Titan2.0
