"""
APEX-OMEGA TITAN: Agent System Package
=======================================

Creative super agent system for managing and running the Titan repository.

This package provides:
- Multi-agent coordination
- Intelligent task scheduling
- Self-healing capabilities
- Automated system management
"""

__version__ = "1.0.0"
__author__ = "APEX-OMEGA TITAN Team"

from agents.core import (
    BaseAgent,
    AgentStatus,
    AgentPriority,
    AgentCapability,
    AgentConfig,
    Task,
    AgentRegistry,
    TaskScheduler
)

__all__ = [
    'BaseAgent',
    'AgentStatus',
    'AgentPriority',
    'AgentCapability',
    'AgentConfig',
    'Task',
    'AgentRegistry',
    'TaskScheduler'
]
