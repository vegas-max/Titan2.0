#!/usr/bin/env python3
"""
APEX-OMEGA TITAN: Agent Registry
=================================

Central registry for managing all agents in the system.
"""

import logging
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime
import queue

from agents.core.agent_base import BaseAgent, Task, AgentStatus, AgentPriority


class AgentRegistry:
    """Central registry for all system agents"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue = queue.PriorityQueue()
        self.logger = logging.getLogger("AgentRegistry")
        self.lock = threading.RLock()
        self.running = False
        
    def register_agent(self, agent: BaseAgent) -> bool:
        """Register a new agent"""
        with self.lock:
            if agent.agent_id in self.agents:
                self.logger.warning(f"Agent {agent.agent_id} already registered")
                return False
            
            self.agents[agent.agent_id] = agent
            self.logger.info(f"Registered agent: {agent.agent_id} ({agent.agent_type})")
            return True
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent"""
        with self.lock:
            if agent_id not in self.agents:
                self.logger.warning(f"Agent {agent_id} not found")
                return False
            
            agent = self.agents[agent_id]
            agent.shutdown()
            del self.agents[agent_id]
            self.logger.info(f"Unregistered agent: {agent_id}")
            return True
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by ID"""
        with self.lock:
            return self.agents.get(agent_id)
    
    def get_agents_by_type(self, agent_type: str) -> List[BaseAgent]:
        """Get all agents of a specific type"""
        with self.lock:
            return [
                agent for agent in self.agents.values()
                if agent.agent_type == agent_type
            ]
    
    def get_all_agents(self) -> List[BaseAgent]:
        """Get all registered agents"""
        with self.lock:
            return list(self.agents.values())
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific agent"""
        agent = self.get_agent(agent_id)
        if agent:
            return agent.heartbeat()
        return None
    
    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        with self.lock:
            return {
                "total_agents": len(self.agents),
                "agents": {
                    agent_id: agent.heartbeat()
                    for agent_id, agent in self.agents.items()
                },
                "timestamp": datetime.now().isoformat()
            }
    
    def submit_task(self, task: Task, target_agent_id: Optional[str] = None):
        """Submit a task to the queue"""
        # Priority queue uses tuples: (priority, counter, task)
        # Lower priority number = higher priority
        self.task_queue.put((task.priority.value, id(task), task, target_agent_id))
        self.logger.info(f"Task {task.task_id} submitted with priority {task.priority.value}")
    
    def assign_task(self, task: Task, agent_id: str) -> bool:
        """Assign a task directly to a specific agent"""
        agent = self.get_agent(agent_id)
        if not agent:
            self.logger.error(f"Agent {agent_id} not found")
            return False
        
        if agent.status not in [AgentStatus.IDLE, AgentStatus.RUNNING]:
            self.logger.warning(f"Agent {agent_id} is not ready (status: {agent.status.value})")
            return False
        
        try:
            task.started_at = datetime.now()
            result = agent.execute_task(task)
            task.completed_at = datetime.now()
            task.result = result
            agent.record_success()
            self.logger.info(f"Task {task.task_id} completed by {agent_id}")
            return True
        except Exception as e:
            task.error = str(e)
            agent.record_failure()
            self.logger.error(f"Task {task.task_id} failed on {agent_id}: {e}")
            return False
    
    def start(self):
        """Start the registry and task dispatcher"""
        self.running = True
        self.logger.info("Agent registry started")
    
    def stop(self):
        """Stop the registry"""
        self.running = False
        with self.lock:
            for agent in self.agents.values():
                agent.shutdown()
        self.logger.info("Agent registry stopped")


class TaskScheduler:
    """Schedules and distributes tasks to agents"""
    
    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        self.logger = logging.getLogger("TaskScheduler")
        self.running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        
    def start(self):
        """Start the task scheduler"""
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._schedule_loop, daemon=True)
        self.scheduler_thread.start()
        self.logger.info("Task scheduler started")
    
    def stop(self):
        """Stop the task scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        self.logger.info("Task scheduler stopped")
    
    def _schedule_loop(self):
        """Main scheduling loop"""
        while self.running:
            try:
                # Get next task from queue (with timeout to allow clean shutdown)
                try:
                    priority, _, task, target_agent_id = self.registry.task_queue.get(timeout=1)
                except queue.Empty:
                    continue
                
                # Find available agent
                if target_agent_id:
                    # Specific agent requested
                    agent = self.registry.get_agent(target_agent_id)
                    if agent and agent.status == AgentStatus.IDLE:
                        self._execute_task_async(agent, task)
                    else:
                        # Put task back in queue if agent not available
                        self.registry.task_queue.put((priority, id(task), task, target_agent_id))
                else:
                    # Find any available agent
                    agent = self._find_available_agent()
                    if agent:
                        self._execute_task_async(agent, task)
                    else:
                        # Put task back in queue
                        self.registry.task_queue.put((priority, id(task), task, None))
                        
            except Exception as e:
                self.logger.error(f"Error in scheduling loop: {e}")
    
    def _find_available_agent(self) -> Optional[BaseAgent]:
        """Find an available agent"""
        agents = self.registry.get_all_agents()
        for agent in agents:
            if agent.status == AgentStatus.IDLE:
                return agent
        return None
    
    def _execute_task_async(self, agent: BaseAgent, task: Task):
        """Execute task asynchronously"""
        def execute():
            try:
                task.started_at = datetime.now()
                agent.set_status(AgentStatus.RUNNING)
                result = agent.execute_task(task)
                task.completed_at = datetime.now()
                task.result = result
                agent.record_success()
                agent.set_status(AgentStatus.IDLE)
                self.logger.info(f"Task {task.task_id} completed by {agent.agent_id}")
            except Exception as e:
                task.error = str(e)
                agent.record_failure()
                agent.set_status(AgentStatus.ERROR)
                self.logger.error(f"Task {task.task_id} failed: {e}")
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
