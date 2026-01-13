# GitHub Codespaces Configuration

This directory contains the configuration for running Titan 2.0 in GitHub Codespaces.

## What is GitHub Codespaces?

GitHub Codespaces provides a complete, configurable dev environment in the cloud. It allows you to code, build, test, and run Titan 2.0 directly in your browser without any local setup.

## Quick Start with Codespaces

1. **Open in Codespaces:**
   - Navigate to the repository on GitHub
   - Click the green "Code" button
   - Select "Open with Codespaces" → "New codespace"

2. **Wait for Setup:**
   - The container will build automatically
   - Dependencies will be installed
   - This takes 3-5 minutes on first run

3. **Configure Environment:**
   ```bash
   # Edit your .env file with your credentials
   nano .env
   ```

4. **Start Using Titan:**
   ```bash
   # View available commands
   make help
   
   # Check system health
   make health
   
   # Run tests
   make test
   
   # Start the system
   make start
   ```

## What Gets Installed

The Codespace automatically installs:

- **Node.js 22** - For JavaScript execution engine
- **Python 3.11** - For ML brain and orchestration
- **Rust** - For high-performance core library
- **Go 1.21** - For alternative core implementation
- **All dependencies** - From package.json and requirements.txt

## Configuration Files

- **devcontainer.json** - Main Codespace configuration
- **setup.sh** - Automated setup script

## Port Forwarding

The following ports are automatically forwarded:

| Port | Service | Description |
|------|---------|-------------|
| 3000 | Dashboard | Main operational dashboard |
| 3001 | Web Dashboard | Alternative web interface |
| 8000 | API Server | REST API endpoint |
| 8080 | Monitoring | System monitoring interface |
| 8545 | Local Blockchain | For testing (if needed) |

## VSCode Extensions

Pre-installed extensions:
- ESLint - JavaScript linting
- Python - Python IntelliSense
- Rust Analyzer - Rust language support
- Go - Go language support
- GitHub Copilot - AI pair programming
- Prettier - Code formatting

## Environment Variables

Create/edit `.env` file with:

```env
# Required
PRIVATE_KEY=0xYOUR_PRIVATE_KEY_HERE
RPC_ETHEREUM=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
RPC_POLYGON=https://polygon-mainnet.infura.io/v3/YOUR_PROJECT_ID
LIFI_API_KEY=your_lifi_api_key_here

# Optional
ALCHEMY_RPC_ETH=https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY
COINGECKO_API_KEY=your_coingecko_api_key
```

## Troubleshooting

### Dependencies Failed to Install

```bash
# Reinstall Node.js dependencies
npm ci

# Reinstall Python dependencies
pip3 install -r requirements.txt
```

### Ports Not Forwarding

1. Go to "Ports" tab in VSCode bottom panel
2. Right-click on the port
3. Select "Port Visibility" → "Public"

### Environment File Issues

```bash
# Recreate .env from example
cp .env.example .env
nano .env
```

### Build Failures

```bash
# Clean and rebuild
make clean
make build-core
```

## CI/CD Operations in Codespace

All CI/CD operations from `.github/workflows/` can be run locally in Codespace.

**See [CI_CD_OPERATIONS.md](./CI_CD_OPERATIONS.md) for a complete guide.**

### Quick CI/CD Commands

```bash
# Install dependencies (same as CI)
npm ci
pip install -r requirements.txt

# Run system audit (same as CI)
python audit_system.py

# Run tests
make test

# Build operations
make build-core
```

## Resources

- [GitHub Codespaces Documentation](https://docs.github.com/en/codespaces)
- [Titan 2.0 Getting Started](../GETTING_STARTED.md)
- [Quick Start Guide](../QUICKSTART.md)

## Performance Notes

- **CPU:** 2-4 cores (Free tier: 2 cores)
- **RAM:** 4-8 GB (Free tier: 4 GB)
- **Storage:** 32 GB SSD
- **Free Tier:** 60 hours/month for individual accounts

For better performance, consider upgrading to a larger Codespace machine type or running locally.
