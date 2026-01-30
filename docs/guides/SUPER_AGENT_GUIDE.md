# 🤖 APEX-OMEGA TITAN: Super Agent System

## Overview

The **Super Agent System** is a creative, autonomous agent framework designed to manage and run the APEX-OMEGA TITAN repository. It provides intelligent automation, self-healing capabilities, and coordinated multi-agent task execution.

## 🌟 Key Features

### Multi-Agent Architecture
- **Orchestrator Agent**: Main coordinator managing all system components
- **Developer Agent**: Code analysis, bug detection, and auto-fixing (planned)
- **Tester Agent**: Automated testing and quality assurance (planned)
- **Deployer Agent**: Contract deployment and environment management (planned)
- **Monitor Agent**: Performance monitoring and alerting (planned)

### Core Capabilities
- ✅ **System Health Monitoring**: Automated health checks for all components
- ✅ **Intelligent Task Scheduling**: Priority-based task queue with concurrent execution
- ✅ **Self-Healing**: Automatic detection and recovery from failures
- ✅ **Resource Management**: Optimized resource allocation and scaling
- ✅ **Automated Testing**: Integrated test execution for Hardhat and Python
- ✅ **Build Automation**: Automated compilation and build processes including Rust engine
- ✅ **Boot-time Initialization**: Automatic build and startup on system boot
- ✅ **Interactive Control**: CLI interface for manual management

## 🚀 Quick Start

### Installation

The super agent system is integrated into the TITAN repository. No additional installation required.

### Boot-Time Auto-Start (Recommended for Production)

For automatic startup on system boot with full build:

```bash
# Option 1: Use the boot script (simplest)
./boot_super_agent.sh

# Option 2: Install as systemd service (Linux only)
# See systemd/README.md for detailed instructions
sudo systemctl enable titan-super-agent
sudo systemctl start titan-super-agent
```

The super agent will automatically:
1. Build the Rust engine (if Rust/Cargo is available)
2. Install Node.js dependencies (if needed)
3. Compile smart contracts
4. Run health checks
5. Start system components (if configured)
6. Monitor and self-heal continuously

### Basic Usage

#### 1. Start the Super Agent System (Interactive Mode)

```bash
python3 agents/super_agent_manager.py --mode interactive
```

#### 2. Available Commands

Once in interactive mode:

```
🤖 super-agent> help          # Show available commands
🤖 super-agent> status        # Display system status
🤖 super-agent> health        # Run health check
🤖 super-agent> start paper   # Start Titan in paper mode
🤖 super-agent> start live    # Start Titan in live mode
🤖 super-agent> stop          # Stop Titan system
🤖 super-agent> test all      # Run all tests
🤖 super-agent> build         # Build the project
🤖 super-agent> quit          # Exit
```

### Command-Line Mode

Execute a single action and exit:

```bash
# Run health check
python3 agents/super_agent_manager.py --mode once --action health

# Start Titan in paper mode
python3 agents/super_agent_manager.py --mode once --action start --system-mode paper

# Run tests
python3 agents/super_agent_manager.py --mode once --action test

# Build project
python3 agents/super_agent_manager.py --mode once --action build

# Show status
python3 agents/super_agent_manager.py --mode once --action status
```

### Daemon Mode

Run as a background service:

```bash
# Start in daemon mode
python3 agents/super_agent_manager.py --mode daemon &

# Stop (send SIGTERM)
kill -TERM <pid>
```

## 📋 Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   Super Agent Manager                       │
│                                                             │
│  ┌─────────────────┐         ┌───────────────────────┐    │
│  │  Agent Registry │◄────────┤   Task Scheduler      │    │
│  └────────┬────────┘         └───────────────────────┘    │
│           │                                                 │
│           │ Manages                                         │
│           ▼                                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  Agent Pool                          │  │
│  │                                                      │  │
│  │  ┌─────────────────┐  ┌──────────────────────┐     │  │
│  │  │  Orchestrator   │  │   Developer Agent    │     │  │
│  │  │     Agent       │  │    (Planned)         │     │  │
│  │  └─────────────────┘  └──────────────────────┘     │  │
│  │                                                      │  │
│  │  ┌─────────────────┐  ┌──────────────────────┐     │  │
│  │  │  Tester Agent   │  │   Deployer Agent     │     │  │
│  │  │   (Planned)     │  │    (Planned)         │     │  │
│  │  └─────────────────┘  └──────────────────────┘     │  │
│  │                                                      │  │
│  │  ┌─────────────────┐                                │  │
│  │  │  Monitor Agent  │                                │  │
│  │  │   (Planned)     │                                │  │
│  │  └─────────────────┘                                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### File Structure

```
agents/
├── core/
│   ├── __init__.py           # Core module exports
│   ├── agent_base.py         # Base agent classes and interfaces
│   └── agent_registry.py     # Agent registry and task scheduler
├── specialized/
│   ├── orchestrator_agent.py # Main orchestrator agent
│   ├── developer_agent.py    # Code development agent (planned)
│   ├── tester_agent.py       # Testing agent (planned)
│   ├── deployer_agent.py     # Deployment agent (planned)
│   └── monitor_agent.py      # Monitoring agent (planned)
└── super_agent_manager.py    # Main entry point

config/
└── agent_config.json         # Agent configuration
```

## 🎯 Agent Capabilities

### Orchestrator Agent (Implemented)

The orchestrator is the main coordinator with these capabilities:

#### System Management
- **system_health_check**: Comprehensive health monitoring
  - Node.js version check
  - Python version check
  - Redis connectivity
  - Disk space monitoring

- **start_system**: Start Titan components
  - Brain (AI engine)
  - Executor (Trading bot)
  - API server (optional)
  - Configurable mode (paper/live)

- **stop_system**: Graceful shutdown
  - Component-specific or full shutdown
  - Timeout-based forceful termination

- **restart_system**: Complete system restart
  - Graceful stop followed by start
  - Configurable delay between operations

#### Build & Test
- **build_project**: Complete project build
  - Rust engine compilation (if available)
  - Python bindings via maturin (if available)
  - Automatic dependency installation
  - Hardhat smart contract compilation
  - Artifact generation
  - Comprehensive error reporting
  
- **build_rust_engine**: Dedicated Rust engine build
  - Cargo-based compilation
  - Release mode optimization
  - Python wheel generation
  - Automatic installation
  - Graceful fallback if Rust not available

- **run_tests**: Execute test suites
  - Hardhat tests
  - Python tests
  - Comprehensive reporting

#### Operations
- **monitor_performance**: Real-time metrics
  - CPU usage
  - Memory consumption
  - Active processes

- **self_heal**: Automatic recovery
  - Health check execution
  - Failure detection
  - Component restart

#### Advanced (Planned)
- **deploy**: Contract deployment
- **auto_scale**: Resource scaling
- **optimize_resources**: Performance optimization

### Developer Agent (Planned)

Will provide:
- Code analysis and linting
- Bug detection
- Automatic fixes for common issues
- Code generation
- Refactoring suggestions

### Tester Agent (Planned)

Will provide:
- Automated test execution
- Coverage analysis
- Performance testing
- Security testing
- Regression detection

### Deployer Agent (Planned)

Will provide:
- Multi-network deployment
- Environment configuration
- Rollback capabilities
- Deployment validation

### Monitor Agent (Planned)

Will provide:
- Real-time performance metrics
- Anomaly detection
- Alert management
- Log aggregation and analysis

## ⚙️ Configuration

### Agent Configuration File

Location: `config/agent_config.json`

#### Global Settings

```json
{
  "global": {
    "log_level": "INFO",
    "task_timeout": 300,
    "max_retries": 3,
    "retry_delay": 5,
    "enable_self_healing": true,
    "enable_auto_optimization": true,
    "enable_learning": true
  }
}
```

#### Agent-Specific Settings

Each agent can be configured individually:

```json
{
  "agents": {
    "orchestrator": {
      "enabled": true,
      "max_concurrent_tasks": 10,
      "heartbeat_interval": 30,
      "auto_restart_on_failure": true,
      "max_restart_attempts": 3,
      "capabilities": [
        "system_health_check",
        "start_system",
        "stop_system",
        "restart_system",
        "run_tests",
        "build_project",
        "build_rust_engine",
        "deploy",
        "monitor_performance",
        "auto_scale",
        "self_heal",
        "optimize_resources"
      ]
    }
  }
}
```

#### Boot-Time Configuration

Configure automatic build and startup behavior:

```json
{
  "system": {
    "default_mode": "paper",
    "auto_start_on_boot": true,
    "run_build_on_boot": true,
    "graceful_shutdown_timeout": 30,
    "health_check_interval": 300
  }
}
```

**Key Settings:**
- `auto_start_on_boot`: Enable automatic system startup when super agent boots
- `run_build_on_boot`: Automatically build Rust engine and contracts on initialization
- `default_mode`: Default system mode (paper or live)
- `graceful_shutdown_timeout`: Time to wait for graceful shutdown before force kill
- `health_check_interval`: Interval between automated health checks (seconds)

### Environment Variables

The system respects these environment variables:

- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
- Standard TITAN `.env` variables for system operation

## 📊 Task Management

### Task Priority Levels

1. **CRITICAL** (1): Highest priority, immediate execution
2. **HIGH** (2): Important tasks, executed quickly
3. **MEDIUM** (3): Normal priority tasks
4. **LOW** (4): Background tasks
5. **BACKGROUND** (5): Lowest priority, executed when idle

### Task Lifecycle

```
Created → Queued → Assigned → Running → Completed
                                    ↓
                                 Failed ────→ Retry (if configured)
```

### Example Task Creation

```python
from agents.core.agent_base import Task, AgentPriority
from agents.specialized.orchestrator_agent import OrchestratorCapability

task = Task(
    task_id="health_check_001",
    task_type=OrchestratorCapability.SYSTEM_HEALTH_CHECK,
    priority=AgentPriority.HIGH,
    payload={},
    timeout=60
)
```

## 🔧 Development Guide

### Creating a New Agent

1. **Create agent class** inheriting from `BaseAgent`:

```python
from agents.core.agent_base import BaseAgent, Task, AgentStatus

class MyCustomAgent(BaseAgent):
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, "custom", config)
    
    def initialize(self) -> bool:
        # Setup logic
        return True
    
    def execute_task(self, task: Task) -> Dict[str, Any]:
        # Task execution logic
        return {"status": "success"}
    
    def shutdown(self) -> bool:
        # Cleanup logic
        return True
```

2. **Register agent** with the registry:

```python
agent = MyCustomAgent("custom-001", {})
agent.initialize()
registry.register_agent(agent)
```

3. **Submit tasks**:

```python
task = Task(
    task_id="task_001",
    task_type="my_custom_task",
    priority=AgentPriority.MEDIUM,
    payload={"param": "value"}
)
registry.submit_task(task, target_agent_id="custom-001")
```

### Adding New Capabilities

1. Define capability constant
2. Implement handler method
3. Add to task_handlers dictionary
4. Update configuration

## 📈 Monitoring & Logging

### Log Locations

- Console: Real-time output
- File: `logs/super_agent_YYYYMMDD.log`

### Log Levels

```python
# Debug: Detailed diagnostic information
logger.debug("Detailed state information")

# Info: General informational messages
logger.info("System started successfully")

# Warning: Warning messages
logger.warning("Component taking longer than expected")

# Error: Error messages
logger.error("Failed to execute task")
```

### Status Monitoring

Check agent status programmatically:

```python
status = registry.get_all_status()
print(f"Total agents: {status['total_agents']}")

for agent_id, agent_status in status['agents'].items():
    print(f"{agent_id}: {agent_status['status']}")
```

## 🔐 Security Considerations

### Current Security Features

- Agent isolation
- Task validation
- Resource limits
- Graceful error handling

### Planned Security Enhancements

- Authentication and authorization
- API key management
- Rate limiting
- Audit logging
- Encrypted configuration

## 🧪 Testing

### Running Tests

The super agent system can execute tests for you:

```bash
# All tests
python3 agents/super_agent_manager.py --mode once --action test

# Specific test suite
🤖 super-agent> test hardhat
🤖 super-agent> test python
```

### Agent System Tests

Create tests for the agent system:

```python
# test_agents.py
from agents.core.agent_registry import AgentRegistry
from agents.specialized.orchestrator_agent import OrchestratorAgent

def test_orchestrator_initialization():
    agent = OrchestratorAgent()
    assert agent.initialize() == True
    assert agent.status == AgentStatus.IDLE

def test_health_check():
    agent = OrchestratorAgent()
    agent.initialize()
    
    task = Task(
        task_id="test_health",
        task_type=OrchestratorCapability.SYSTEM_HEALTH_CHECK,
        priority=AgentPriority.HIGH,
        payload={}
    )
    
    result = agent.execute_task(task)
    assert result['overall_status'] in ['healthy', 'degraded']
```

## 🎓 Best Practices

### Agent Design

1. **Single Responsibility**: Each agent should have a clear, focused purpose
2. **Idempotency**: Operations should be safe to retry
3. **Error Handling**: Always handle exceptions gracefully
4. **Logging**: Log important state changes and errors
5. **Resource Cleanup**: Always implement proper shutdown procedures

### Task Design

1. **Atomic Operations**: Tasks should be self-contained
2. **Timeout Awareness**: Set appropriate timeouts
3. **Priority Management**: Use appropriate priority levels
4. **Payload Validation**: Validate task payloads before execution

### System Management

1. **Regular Health Checks**: Monitor system health periodically
2. **Graceful Shutdowns**: Always use proper shutdown procedures
3. **Log Monitoring**: Regularly review logs for issues
4. **Configuration Backups**: Keep configuration backups

## 🚧 Roadmap

### Phase 1: Foundation (✅ Complete)
- [x] Core agent framework
- [x] Agent registry and task scheduler
- [x] Orchestrator agent with basic capabilities
- [x] Interactive CLI interface
- [x] Health monitoring
- [x] System start/stop control

### Phase 2: Intelligence (Planned)
- [ ] Developer agent implementation
- [ ] Tester agent implementation
- [ ] Advanced self-healing
- [ ] Performance optimization
- [ ] Learning capabilities

### Phase 3: Automation (Planned)
- [ ] Deployer agent implementation
- [ ] Monitor agent implementation
- [ ] Automated CI/CD integration
- [ ] Alert management
- [ ] Advanced analytics

### Phase 4: Enhancement (Future)
- [ ] Web dashboard
- [ ] API endpoints
- [ ] Multi-repository support
- [ ] Cloud integration
- [ ] Advanced ML-driven optimization

## 💡 Use Cases

### 1. Automated Development Workflow

```bash
# Start the system
🤖 super-agent> start paper

# Run tests automatically
🤖 super-agent> test all

# Build and verify
🤖 super-agent> build
```

### 2. Continuous Monitoring

```bash
# Run in daemon mode with periodic health checks
python3 agents/super_agent_manager.py --mode daemon
```

### 3. Emergency Recovery

```bash
# Quick health check and auto-heal
🤖 super-agent> health
🤖 super-agent> restart paper
```

### 4. Scheduled Tasks

Integrate with cron for scheduled operations:

```bash
# Health check every hour
0 * * * * cd /path/to/Titan2.0 && python3 agents/super_agent_manager.py --mode once --action health >> /var/log/titan_health.log 2>&1
```

## 📞 Support

For issues or questions about the super agent system:

1. Check the logs in `logs/super_agent_*.log`
2. Review configuration in `config/agent_config.json`
3. Run health check: `health` command
4. Check GitHub issues

## 📄 License

This super agent system is part of the APEX-OMEGA TITAN project and is licensed under the MIT License.

---

**Built with ❤️ for autonomous repository management**
