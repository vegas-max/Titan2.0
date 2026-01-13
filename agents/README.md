# Agents System

## Overview

The `agents` directory contains the autonomous agent framework for Titan. This system provides intelligent automation, self-management capabilities, and example implementations for building custom agents.

## Purpose

The agents system provides:
- **Autonomous operation** without manual intervention
- **Self-healing capabilities** for automatic error recovery
- **Intelligent decision-making** using AI/ML
- **Extensible framework** for building custom agents

## Project Structure

```
agents/
├── __init__.py                  # Package initialization
├── core/                        # Core agent framework
├── specialized/                 # Specialized agent implementations
├── super_agent_manager.py       # Super Agent orchestration system
├── demo.py                      # Agent demonstration examples
├── examples.py                  # Example agent implementations
└── README.md                   # This file
```

## Components

### super_agent_manager.py

The Super Agent Manager orchestrates the entire Titan system:
- **Auto-start** Brain and Bot components
- **Health monitoring** with automatic restart on failure
- **Resource management** and optimization
- **Graceful shutdown** and cleanup

**Key Features:**
- Manages child processes
- Monitors system health
- Handles failures automatically
- Logs all activities

### core/

Core agent framework components:
- Base agent classes
- Agent communication protocols
- Decision-making frameworks
- State management

### specialized/

Specialized agent implementations:
- Scanner agents (opportunity detection)
- Executor agents (trade execution)
- Monitor agents (system health)
- Optimizer agents (parameter tuning)

### demo.py

Demonstration of agent capabilities:
- Simple agent examples
- Integration patterns
- Best practices
- Common use cases

### examples.py

Complete working examples:
- Custom agent implementations
- Integration with Titan components
- Advanced agent patterns
- Real-world scenarios

## Quick Start

### Running the Super Agent

The Super Agent automatically manages the entire Titan system:

```bash
# Start Super Agent
./start_super_agent.sh

# Or on Windows
start_super_agent.bat

# Or manually
python3 agents/super_agent_manager.py
```

The Super Agent will:
1. ✅ Start Redis (if needed)
2. ✅ Launch the Brain (AI engine)
3. ✅ Launch the Bot (executor)
4. ✅ Monitor all components
5. ✅ Restart on failures
6. ✅ Handle graceful shutdown

### Running Agent Demos

```bash
# Run demonstrations
python3 agents/demo.py

# Run examples
python3 agents/examples.py
```

## Super Agent Features

### Auto-Start Management

The Super Agent starts all required components in the correct order:
```python
# Automatic component startup
1. Check Redis availability
2. Start Brain process
3. Wait for Brain initialization
4. Start Bot process
5. Begin health monitoring
```

### Health Monitoring

Continuous health checks with automatic recovery:
- **Brain health**: Checks for activity and responsiveness
- **Bot health**: Monitors execution status
- **Process health**: Ensures processes are running
- **Auto-restart**: Restarts failed components

### Resource Optimization

Intelligent resource management:
- Memory usage monitoring
- CPU utilization tracking
- Automatic resource adjustment
- Performance optimization

### Graceful Shutdown

Clean shutdown of all components:
```python
# Shutdown sequence
1. Stop accepting new signals
2. Wait for pending operations
3. Shutdown Bot gracefully
4. Shutdown Brain gracefully
5. Cleanup resources
```

## Building Custom Agents

### Basic Agent Template

```python
from agents.core.base_agent import BaseAgent

class MyCustomAgent(BaseAgent):
    def __init__(self, config):
        super().__init__("MyAgent", config)
        self.running = False
    
    async def start(self):
        """Start the agent"""
        self.running = True
        await self.run_loop()
    
    async def run_loop(self):
        """Main agent loop"""
        while self.running:
            # Agent logic here
            await self.process_task()
            await asyncio.sleep(self.config['interval'])
    
    async def process_task(self):
        """Process a single task"""
        # Implement your logic
        pass
    
    async def stop(self):
        """Stop the agent gracefully"""
        self.running = False
        await self.cleanup()
```

### Using the Agent

```python
# Create and start agent
agent = MyCustomAgent(config={
    'interval': 5,  # seconds
    'enabled': True
})

await agent.start()
```

## Agent Communication

Agents communicate via multiple channels:

### Redis PubSub
```python
# Subscribe to channel
await agent.subscribe('agent_channel')

# Publish message
await agent.publish('agent_channel', {
    'type': 'notification',
    'data': {...}
})
```

### Direct Messaging
```python
# Send message to specific agent
await agent.send_message('scanner_agent', {
    'command': 'scan_network',
    'network': 'polygon'
})
```

### Shared State
```python
# Read shared state
state = await agent.get_state('opportunities')

# Update shared state
await agent.set_state('opportunities', new_data)
```

## Agent Types

### Scanner Agents

Continuously scan for opportunities:
- Multi-chain monitoring
- DEX price tracking
- Event detection
- Opportunity publishing

### Executor Agents

Execute trading strategies:
- Signal processing
- Transaction building
- Execution coordination
- Result tracking

### Monitor Agents

System health and performance:
- Component status
- Resource usage
- Error detection
- Alert generation

### Optimizer Agents

System optimization:
- Parameter tuning
- Performance analysis
- Resource allocation
- Strategy adjustment

## Configuration

Agent configuration via JSON files:

```json
{
  "super_agent": {
    "enabled": true,
    "health_check_interval": 30,
    "restart_delay": 10,
    "max_restart_attempts": 3
  },
  "scanner_agent": {
    "enabled": true,
    "scan_interval": 3,
    "networks": ["polygon", "arbitrum", "optimism"]
  },
  "executor_agent": {
    "enabled": true,
    "max_concurrent": 5,
    "timeout": 60
  }
}
```

Load configuration:
```python
import json

with open('config/agent_config.json') as f:
    config = json.load(f)

agent = MyAgent(config['my_agent'])
```

## Logging

Agents use structured logging:

```python
# In agent code
self.logger.info("Agent started", extra={
    'agent_name': self.name,
    'config': self.config
})

self.logger.warning("High memory usage detected", extra={
    'memory_mb': current_memory,
    'threshold_mb': threshold
})

self.logger.error("Failed to process task", extra={
    'task_id': task.id,
    'error': str(error)
})
```

## Monitoring

Monitor agent activity:

```bash
# View Super Agent logs
tail -f logs/super_agent.log

# View all agent logs
tail -f logs/agents/*.log

# Monitor via systemd (if installed)
sudo journalctl -u titan-super-agent -f
```

## Advanced Features

### State Persistence

Agents can persist state across restarts:

```python
class StatefulAgent(BaseAgent):
    async def save_state(self):
        """Save agent state to disk"""
        state = {
            'last_scan': self.last_scan_time,
            'processed_ids': list(self.processed_ids)
        }
        await self.write_state(state)
    
    async def restore_state(self):
        """Restore agent state from disk"""
        state = await self.read_state()
        if state:
            self.last_scan_time = state['last_scan']
            self.processed_ids = set(state['processed_ids'])
```

### Agent Coordination

Multiple agents working together:

```python
class CoordinatorAgent(BaseAgent):
    def __init__(self, config):
        super().__init__("Coordinator", config)
        self.worker_agents = []
    
    async def coordinate(self):
        """Distribute work to worker agents"""
        tasks = await self.get_pending_tasks()
        
        for task, agent in zip(tasks, self.worker_agents):
            await agent.assign_task(task)
```

## Further Documentation Needed

- [ ] Complete API reference for all agent classes
- [ ] Agent lifecycle management best practices
- [ ] Advanced agent coordination patterns
- [ ] Performance tuning for multi-agent systems
- [ ] Security considerations for agent communication
- [ ] Deployment strategies for production agent systems

## Best Practices

1. **Keep agents focused** - One responsibility per agent
2. **Handle errors gracefully** - Implement proper error handling
3. **Log important events** - Use structured logging
4. **Monitor resource usage** - Track memory and CPU
5. **Test thoroughly** - Unit and integration tests
6. **Document behavior** - Clear documentation for each agent

## Troubleshooting

### Super Agent Won't Start

**Check:**
1. Redis is running: `redis-cli ping`
2. Ports are available (6379, 8080, etc.)
3. Python dependencies installed
4. .env file configured

### Agent Crashes Repeatedly

**Solutions:**
1. Check logs for error details
2. Reduce concurrent operations
3. Increase restart delay
4. Fix underlying issue causing crash

### Agents Not Communicating

**Solutions:**
1. Verify Redis connection
2. Check channel names match
3. Ensure agents are subscribed
4. Review message format

## Contributing

When creating new agents:
1. Extend `BaseAgent` class
2. Implement required methods
3. Add configuration schema
4. Write unit tests
5. Document agent purpose and usage
6. Add to agent registry

## Examples

See these files for examples:
- `demo.py` - Simple demonstrations
- `examples.py` - Complete implementations
- `core/` - Framework components
- `specialized/` - Production agents

## License

The agents system is part of the Titan 2.0 project and follows the same MIT License.

## Support

For agent-related issues:
- Check logs for detailed error messages
- Verify Redis connectivity
- Review agent configuration
- Test with demo agents first

See main README.md for general support information.
