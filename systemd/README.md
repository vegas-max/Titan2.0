# Systemd Service Files for Titan

This directory contains systemd service files for running Titan as a system service on Linux.

## Files

- `titan-redis.service.template` - Redis service template
- `titan-super-agent.service.template` - Super Agent system template (recommended for auto-management)
- `titan-brain.service.template` - Brain (AI engine) service template
- `titan-executor.service.template` - Executor (trading bot) service template

## Automatic Installation

The deployment script (`deploy_oracle_cloud.sh`) will automatically:
1. Copy these templates
2. Replace placeholders with actual values
3. Install to `/etc/systemd/system/`
4. Enable services to start on boot

## Manual Installation

If you need to install manually:

```bash
# Replace placeholders in templates
CURRENT_USER=$(whoami)
CURRENT_DIR=$(pwd)

sed "s|REPLACE_WITH_USER|$CURRENT_USER|g; s|REPLACE_WITH_WORKDIR|$CURRENT_DIR|g" \
    systemd/titan-super-agent.service.template > systemd/titan-super-agent.service

sed "s|REPLACE_WITH_USER|$CURRENT_USER|g; s|REPLACE_WITH_WORKDIR|$CURRENT_DIR|g" \
    systemd/titan-brain.service.template > systemd/titan-brain.service

sed "s|REPLACE_WITH_USER|$CURRENT_USER|g; s|REPLACE_WITH_WORKDIR|$CURRENT_DIR|g" \
    systemd/titan-executor.service.template > systemd/titan-executor.service

# Copy to systemd directory
sudo cp systemd/titan-redis.service.template /etc/systemd/system/titan-redis.service
sudo cp systemd/titan-super-agent.service /etc/systemd/system/
sudo cp systemd/titan-brain.service /etc/systemd/system/
sudo cp systemd/titan-executor.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Option 1: Enable Super Agent (Recommended - manages all components automatically)
sudo systemctl enable titan-redis titan-super-agent
sudo systemctl start titan-redis
sudo systemctl start titan-super-agent

# Option 2: Enable individual services (Alternative approach)
# sudo systemctl enable titan-redis titan-brain titan-executor
# sudo systemctl start titan-redis
# sudo systemctl start titan-brain
# sudo systemctl start titan-executor
```

## Managing Services

### Super Agent (Recommended)

```bash
# Start Super Agent (automatically manages brain and executor)
sudo systemctl start titan-super-agent

# Stop Super Agent
sudo systemctl stop titan-super-agent

# Restart Super Agent
sudo systemctl restart titan-super-agent

# Check status
sudo systemctl status titan-super-agent

# View logs
sudo journalctl -u titan-super-agent -f
```

### Individual Services (Alternative)

```bash
# Start services
sudo systemctl start titan-brain titan-executor

# Stop services
sudo systemctl stop titan-executor titan-brain

# Restart services
sudo systemctl restart titan-brain titan-executor

# Check status
sudo systemctl status titan-brain titan-executor

# View logs
sudo journalctl -u titan-brain -f
sudo journalctl -u titan-executor -f

# Disable auto-start
sudo systemctl disable titan-brain titan-executor
```

## Memory Limits

The service files include memory limits to prevent OOM (Out of Memory) errors:

- **Brain**: 4GB (can be reduced to 700MB for lightweight mode)
- **Executor**: 2GB (can be reduced to 250MB for lightweight mode)

To adjust for low-memory instances, edit the service files before installation:

```bash
# For 1GB RAM instance
MemoryLimit=700M  # in titan-brain.service
MemoryLimit=250M  # in titan-executor.service
```

## Logs

Logs are sent to systemd journal. View them with:

```bash
# All Titan logs
sudo journalctl -u titan-* -f

# Specific service
sudo journalctl -u titan-brain -f

# Last 100 lines
sudo journalctl -u titan-brain -n 100

# Since specific time
sudo journalctl -u titan-brain --since "1 hour ago"
```

## Troubleshooting

If services fail to start:

1. Check service status:
   ```bash
   sudo systemctl status titan-brain
   ```

2. Check logs for errors:
   ```bash
   sudo journalctl -u titan-brain -n 50
   ```

3. Verify Redis is running:
   ```bash
   sudo systemctl status titan-redis
   redis-cli ping  # Should return PONG
   ```

4. Check file permissions:
   ```bash
   ls -la ~/Titan2.0/offchain/ml/brain.py
   ls -la ~/Titan2.0/offchain/execution/bot.js
   ```

5. Verify .env file exists:
   ```bash
   ls -la ~/Titan2.0/.env
   ```
