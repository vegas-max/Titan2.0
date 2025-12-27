# 🤖 Super Agent Quick Reference

## Quick Start Commands

### Linux/macOS

```bash
# Interactive mode
./start_super_agent.sh

# Daemon mode (background)
./start_super_agent.sh daemon

# One-time commands
./start_super_agent.sh once health
./start_super_agent.sh once start paper
./start_super_agent.sh once test
./start_super_agent.sh once build
```

### Windows

```batch
REM Interactive mode
start_super_agent.bat

REM Background mode
start_super_agent.bat daemon

REM One-time commands
start_super_agent.bat once health
start_super_agent.bat once start paper
start_super_agent.bat once test
start_super_agent.bat once build
```

## Interactive Commands

```
help          - Show available commands
status        - Display system and agent status
health        - Run comprehensive health check
start paper   - Start Titan in paper trading mode
start live    - Start Titan in live trading mode
stop          - Stop all Titan components
test all      - Run all test suites
test hardhat  - Run Hardhat tests only
test python   - Run Python tests only
build         - Compile smart contracts
quit          - Exit super agent system
```

## Common Workflows

### Daily Startup

```bash
./start_super_agent.sh
🤖 super-agent> health
🤖 super-agent> start paper
```

### Pre-Deployment

```bash
./start_super_agent.sh once test
./start_super_agent.sh once build
./start_super_agent.sh once health
```

### Monitoring

```bash
# Start daemon for continuous monitoring
./start_super_agent.sh daemon

# Check status periodically
./start_super_agent.sh once status
```

## Health Check Components

The health check verifies:
- ✅ Node.js installation and version
- ✅ Python installation and version
- ✅ Redis connectivity (if configured)
- ✅ Disk space availability
- ✅ System resources

## Log Locations

- **Interactive**: Console output
- **Daemon**: `logs/super_agent_daemon.log`
- **Daily logs**: `logs/super_agent_YYYYMMDD.log`

## Configuration

Edit `config/agent_config.json` to customize:
- Agent capabilities
- Task limits
- Timeouts
- Monitoring thresholds
- Auto-restart behavior

## Troubleshooting

### Agent won't start
```bash
# Check Python version (3.11+ required)
python3 --version

# Check logs
tail -f logs/super_agent_*.log

# Run health check
./start_super_agent.sh once health
```

### Components won't start
```bash
# Check system health
🤖 super-agent> health

# Try stopping and restarting
🤖 super-agent> stop
🤖 super-agent> start paper
```

### Tests failing
```bash
# Run specific test suite
🤖 super-agent> test hardhat
🤖 super-agent> test python

# Check build status
🤖 super-agent> build
```

## Advanced Usage

### Python API

```python
from agents.core.agent_registry import AgentRegistry
from agents.specialized.orchestrator_agent import OrchestratorAgent
from agents.core.agent_base import Task, AgentPriority

# Create registry
registry = AgentRegistry()

# Create and register agent
orchestrator = OrchestratorAgent()
orchestrator.initialize()
registry.register_agent(orchestrator)

# Submit task
task = Task(
    task_id="custom_task_001",
    task_type="system_health_check",
    priority=AgentPriority.HIGH,
    payload={}
)
registry.assign_task(task, "orchestrator-main")

# Check result
print(task.result)
```

### Scheduled Tasks (Cron)

```bash
# Health check every hour
0 * * * * cd /path/to/Titan2.0 && ./start_super_agent.sh once health >> /var/log/titan_health.log 2>&1

# Daily build at 2 AM
0 2 * * * cd /path/to/Titan2.0 && ./start_super_agent.sh once build >> /var/log/titan_build.log 2>&1

# Test suite every 4 hours
0 */4 * * * cd /path/to/Titan2.0 && ./start_super_agent.sh once test >> /var/log/titan_test.log 2>&1
```

## Environment Variables

```bash
# Set log level
export LOG_LEVEL=DEBUG

# Then start agent
./start_super_agent.sh
```

## Status Indicators

- 🟢 **idle**: Agent ready for tasks
- 🔵 **running**: Agent executing task
- 🟡 **paused**: Agent paused
- 🔴 **error**: Agent encountered error
- ⚫ **stopped**: Agent shut down
- 🟠 **recovering**: Agent self-healing

## Quick Diagnostics

```bash
# Full system check
./start_super_agent.sh once health

# View all agent status
./start_super_agent.sh once status

# Check logs
tail -n 100 logs/super_agent_$(date +%Y%m%d).log

# Check daemon status
ps aux | grep super_agent_manager
```

## Support

For detailed documentation, see [SUPER_AGENT_GUIDE.md](SUPER_AGENT_GUIDE.md)

---

**Quick tip**: Start with `./start_super_agent.sh` for interactive exploration!
