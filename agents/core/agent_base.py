#!/usr/bin/env python3
"""
APEX-OMEGA TITAN: Agent Base Framework
======================================

Base classes and interfaces for the creative super agent system.
"""

import os
import sys
import time
import logging
import json
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class AgentStatus(Enum):
    """Agent status enumeration"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    RECOVERING = "recovering"


class AgentPriority(Enum):
    """Task priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


class Task:
    """Represents a task for an agent to execute"""
    
    def __init__(
        self,
        task_id: str,
        task_type: str,
        priority: AgentPriority,
        payload: Dict[str, Any],
        timeout: int = 300
    ):
        self.task_id = task_id
        self.task_type = task_type
        self.priority = priority
        self.payload = payload
        self.timeout = timeout
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "priority": self.priority.value,
            "payload": self.payload,
            "timeout": self.timeout,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error
        }


class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, agent_id: str, agent_type: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.config = config
        self.status = AgentStatus.IDLE
        self.logger = logging.getLogger(f"Agent.{agent_id}")
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.started_at: Optional[datetime] = None
        self.last_heartbeat: Optional[datetime] = None
        
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the agent. Returns True if successful."""
        pass
    
    @abstractmethod
    def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute a specific task. Returns result dictionary."""
        pass
    
    @abstractmethod
    def shutdown(self) -> bool:
        """Gracefully shutdown the agent. Returns True if successful."""
        pass
    
    def heartbeat(self) -> Dict[str, Any]:
        """Send heartbeat signal with agent status"""
        self.last_heartbeat = datetime.now()
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status.value,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "uptime_seconds": self._get_uptime(),
            "last_heartbeat": self.last_heartbeat.isoformat()
        }
    
    def _get_uptime(self) -> Optional[float]:
        """Calculate agent uptime in seconds"""
        if self.started_at:
            return (datetime.now() - self.started_at).total_seconds()
        return None
    
    def set_status(self, status: AgentStatus):
        """Update agent status"""
        self.logger.info(f"Status change: {self.status.value} -> {status.value}")
        self.status = status
    
    def record_success(self):
        """Record successful task completion"""
        self.tasks_completed += 1
    
    def record_failure(self):
        """Record failed task"""
        self.tasks_failed += 1


class AgentCapability(ABC):
    """Base class for agent capabilities"""
    
    def __init__(self, name: str):
        self.name = name
        self.enabled = True
        
    @abstractmethod
    def can_handle(self, task_type: str) -> bool:
        """Check if this capability can handle the given task type"""
        pass
    
    @abstractmethod
    def execute(self, task: Task) -> Dict[str, Any]:
        """Execute the task using this capability"""
        pass


class AgentConfig:
    """Configuration management for agents"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__),
            "../../config/agent_config.json"
        )
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = self._get_default_config()
            self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_agent_config(self, agent_type: str) -> Dict[str, Any]:
        """Get configuration for a specific agent type"""
        return self.config.get("agents", {}).get(agent_type, {})
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "version": "1.0.0",
            "agents": {
                "orchestrator": {
                    "enabled": True,
                    "max_concurrent_tasks": 10,
                    "heartbeat_interval": 30
                },
                "developer": {
                    "enabled": True,
                    "auto_fix_enabled": True,
                    "max_concurrent_tasks": 5
                },
                "tester": {
                    "enabled": True,
                    "auto_test_on_commit": True,
                    "max_concurrent_tasks": 3
                },
                "deployer": {
                    "enabled": True,
                    "auto_deploy": False,
                    "require_approval": True
                },
                "monitor": {
                    "enabled": True,
                    "monitoring_interval": 60,
                    "alert_threshold": 0.8
                }
            },
            "global": {
                "log_level": "INFO",
                "task_timeout": 300,
                "max_retries": 3
            }
        }
