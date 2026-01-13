# Running CI/CD Operations in Codespace

This guide demonstrates how to run all CI/CD pipeline operations locally in GitHub Codespaces.

## Overview

GitHub Codespaces provides a cloud-based development environment where you can run all CI/CD operations that would normally run in GitHub Actions workflows.

## Prerequisites

The Codespace is automatically configured with:
- Node.js 22
- Python 3.11
- Rust (latest)
- Go 1.21
- All necessary tools

## Quick Start

1. **Open in Codespaces:**
   ```
   Click "Code" → "Open with Codespaces" → "New codespace"
   ```

2. **Wait for automatic setup** (3-5 minutes):
   - Dependencies are installed automatically
   - Environment is configured
   - Scripts are made executable

3. **Verify setup:**
   ```bash
   make check-prereqs
   ```

## Running CI/CD Operations

### 1. Install Dependencies (CI Step 1)

This is what the CI workflow does:

```bash
# Install Node.js dependencies
npm ci

# Install Python dependencies
pip3 install -r requirements.txt
```

Or use the make target:
```bash
make install
```

### 2. Run System Audit (CI Step 2)

```bash
make audit
```

Or directly:
```bash
python3 audit_system.py
```

### 3. Run Tests

Run all tests:
```bash
make test
```

Run specific test suites:
```bash
# Python tests
python3 test_phase1.py

# Rust tests (if applicable)
make test-rust

# Go tests (if applicable)
make test-go
```

### 4. Build Operations

Build all components:
```bash
make build-core
```

Build specific components:
```bash
# Build Rust core
make build-rust

# Build Go core
make build-go
```

### 5. Lint Code

```bash
make lint
```

Or manually:
```bash
# JavaScript linting
npx eslint execution/*.js scripts/*.js --fix

# Python linting
python3 -m pylint core/ ml/ routing/ --exit-zero
```

### 6. Run Health Checks

```bash
make health
```

Or directly:
```bash
./health-check.sh
```

## Reproducing CI Workflow

To exactly reproduce what runs in CI:

```bash
# 1. Clean slate
make clean

# 2. Install dependencies (as CI does)
npm ci
pip install -r requirements.txt

# 3. Run audit (as CI does)
python audit_system.py

# 4. Run tests (optional in CI)
make test
```

## Available Make Commands

View all available commands:
```bash
make help
```

Common commands:
- `make setup` - Complete automated setup
- `make install` - Install all dependencies
- `make build` - Build all components
- `make test` - Run tests
- `make audit` - Run system audit
- `make health` - Check system health
- `make clean` - Clean build artifacts
- `make lint` - Run linters

## Running Development Operations

### Start the System

```bash
# Start in development mode
make start

# Start in mainnet paper mode
make start-mainnet-paper

# Start in mainnet live mode (WARNING: Real money!)
make start-mainnet-live
```

### Monitor Logs

```bash
# View brain logs
make logs-brain

# View bot logs
make logs-bot
```

### Stop the System

```bash
make stop
```

## Debugging CI Failures

If a CI workflow fails:

1. **Check the workflow file:**
   ```bash
   cat .github/workflows/ci.yml
   ```

2. **Run the exact same commands locally:**
   ```bash
   # Example: If "Run system audit" fails
   python audit_system.py
   ```

3. **Check environment variables:**
   ```bash
   # Verify .env file exists and is configured
   ls -la .env
   ```

4. **Check dependencies:**
   ```bash
   # Verify all dependencies are installed
   npm ls
   pip list
   ```

## Accessing Services

When running services in Codespaces, ports are automatically forwarded:

| Port | Service | Access |
|------|---------|--------|
| 3000 | Dashboard | Auto-forwarded |
| 3001 | Web Dashboard | Auto-forwarded |
| 8000 | API Server | Auto-forwarded |
| 8080 | Monitoring | Auto-forwarded |

Click on the "Ports" tab in VSCode to see forwarded ports and access URLs.

## Environment Configuration

1. **Edit .env file:**
   ```bash
   nano .env
   ```

2. **Add required keys:**
   ```env
   PRIVATE_KEY=0xYOUR_PRIVATE_KEY
   RPC_ETHEREUM=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
   RPC_POLYGON=https://polygon-mainnet.infura.io/v3/YOUR_PROJECT_ID
   LIFI_API_KEY=your_lifi_api_key
   ```

## Troubleshooting

### Dependencies Fail to Install

```bash
# Clear npm cache
npm cache clean --force
npm ci

# Reinstall Python dependencies
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

### Tests Fail

```bash
# Check test output
make test 2>&1 | tee test-output.txt

# Run specific test
python3 test_specific.py
```

### Build Fails

```bash
# Clean build artifacts
make clean

# Rebuild
make build-core
```

### Permission Issues

```bash
# Make scripts executable
chmod +x setup.sh start.sh health-check.sh
```

## Advanced: Custom CI Workflows

### Running Release Workflow Operations

```bash
# View release workflow
cat .github/workflows/release.yml

# Build for release
npm run build
```

### Running Rust Workflow Operations

```bash
# View Rust workflow
cat .github/workflows/rust.yml

# Run Rust CI operations
cd core-rust
cargo build --verbose
cargo test --verbose
```

## Best Practices

1. **Always start with clean dependencies:**
   ```bash
   make clean
   npm ci
   pip install -r requirements.txt
   ```

2. **Run audit before making changes:**
   ```bash
   make audit
   ```

3. **Test incrementally:**
   ```bash
   # Test after each change
   make test
   ```

4. **Use make targets for consistency:**
   ```bash
   # Prefer this
   make build-rust
   
   # Over manual commands
   cd core-rust && cargo build --release
   ```

5. **Check git status regularly:**
   ```bash
   git status
   git diff
   ```

## Resources

- [Main README](../README.md)
- [Codespace Configuration](./README.md)
- [GitHub Actions Workflows](../.github/workflows/)
- [Makefile](../Makefile)

## Support

If you encounter issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review CI workflow logs on GitHub
3. Compare local environment with CI environment
4. Consult the main documentation

---

**Note:** Running operations in Codespaces uses your GitHub Codespaces quota. Free tier includes 60 hours/month.
