#!/usr/bin/env python3
"""
APEX-OMEGA TITAN: Orchestrator Agent
=====================================

Main orchestrator agent that coordinates all other agents.
"""

import os
import sys
import time
import logging
import subprocess
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from agents.core.agent_base import BaseAgent, Task, AgentStatus, AgentPriority, AgentConfig


class OrchestratorCapability:
    """Capabilities of the orchestrator agent"""
    
    SYSTEM_HEALTH_CHECK = "system_health_check"
    START_SYSTEM = "start_system"
    STOP_SYSTEM = "stop_system"
    RESTART_SYSTEM = "restart_system"
    RUN_TESTS = "run_tests"
    BUILD_PROJECT = "build_project"
    DEPLOY = "deploy"
    MONITOR_PERFORMANCE = "monitor_performance"
    AUTO_SCALE = "auto_scale"
    SELF_HEAL = "self_heal"
    OPTIMIZE_RESOURCES = "optimize_resources"


class OrchestratorAgent(BaseAgent):
    """Main orchestrator agent for managing the entire system"""
    
    def __init__(self, agent_id: str = "orchestrator-main", config: Optional[Dict[str, Any]] = None):
        if config is None:
            agent_config = AgentConfig()
            config = agent_config.get_agent_config("orchestrator")
        
        super().__init__(agent_id, "orchestrator", config)
        self.project_root = Path(__file__).parent.parent.parent
        self.processes: Dict[str, subprocess.Popen] = {}
        
    def initialize(self) -> bool:
        """Initialize the orchestrator agent"""
        self.logger.info("🚀 Initializing Orchestrator Agent...")
        self.started_at = datetime.now()
        self.set_status(AgentStatus.IDLE)
        
        # Verify project structure
        if not self._verify_project_structure():
            self.logger.error("Project structure verification failed")
            return False
        
        self.logger.info("✅ Orchestrator Agent initialized successfully")
        return True
    
    def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute a task"""
        self.logger.info(f"Executing task: {task.task_type}")
        
        task_handlers = {
            OrchestratorCapability.SYSTEM_HEALTH_CHECK: self._health_check,
            OrchestratorCapability.START_SYSTEM: self._start_system,
            OrchestratorCapability.STOP_SYSTEM: self._stop_system,
            OrchestratorCapability.RESTART_SYSTEM: self._restart_system,
            OrchestratorCapability.RUN_TESTS: self._run_tests,
            OrchestratorCapability.BUILD_PROJECT: self._build_project,
            OrchestratorCapability.DEPLOY: self._deploy,
            OrchestratorCapability.MONITOR_PERFORMANCE: self._monitor_performance,
            OrchestratorCapability.AUTO_SCALE: self._auto_scale,
            OrchestratorCapability.SELF_HEAL: self._self_heal,
            OrchestratorCapability.OPTIMIZE_RESOURCES: self._optimize_resources,
        }
        
        handler = task_handlers.get(task.task_type)
        if not handler:
            raise ValueError(f"Unknown task type: {task.task_type}")
        
        return handler(task.payload)
    
    def shutdown(self) -> bool:
        """Shutdown the orchestrator agent"""
        self.logger.info("🛑 Shutting down Orchestrator Agent...")
        
        # Stop all running processes
        for process_name, process in self.processes.items():
            self.logger.info(f"Stopping process: {process_name}")
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
        
        self.set_status(AgentStatus.STOPPED)
        self.logger.info("✅ Orchestrator Agent shutdown complete")
        return True
    
    def _verify_project_structure(self) -> bool:
        """Verify project structure is valid"""
        required_files = [
            "package.json",
            "hardhat.config.js",
            "requirements.txt",
        ]
        
        required_dirs = [
            "contracts",
            "execution",
            "ml",
            "core",
        ]
        
        for file in required_files:
            file_path = self.project_root / file
            if not file_path.exists():
                self.logger.warning(f"Missing required file: {file}")
                return False
        
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                self.logger.warning(f"Missing required directory: {dir_name}")
                return False
        
        return True
    
    def _health_check(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Perform system health check"""
        self.logger.info("🔍 Performing system health check...")
        
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }
        
        # Check Node.js
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            health_status["checks"]["nodejs"] = {
                "status": "healthy" if result.returncode == 0 else "unhealthy",
                "version": result.stdout.strip()
            }
        except Exception as e:
            health_status["checks"]["nodejs"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check Python
        try:
            result = subprocess.run(
                ["python3", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            health_status["checks"]["python"] = {
                "status": "healthy" if result.returncode == 0 else "unhealthy",
                "version": result.stdout.strip()
            }
        except Exception as e:
            health_status["checks"]["python"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check Redis (if configured)
        try:
            result = subprocess.run(
                ["redis-cli", "ping"],
                capture_output=True,
                text=True,
                timeout=5
            )
            health_status["checks"]["redis"] = {
                "status": "healthy" if result.stdout.strip() == "PONG" else "unhealthy",
                "response": result.stdout.strip()
            }
        except Exception as e:
            health_status["checks"]["redis"] = {
                "status": "unavailable",
                "error": str(e)
            }
        
        # Check disk space
        try:
            result = subprocess.run(
                ["df", "-h", str(self.project_root)],
                capture_output=True,
                text=True,
                timeout=5
            )
            health_status["checks"]["disk_space"] = {
                "status": "healthy",
                "info": result.stdout.strip().split('\n')[-1]
            }
        except Exception as e:
            health_status["checks"]["disk_space"] = {
                "status": "unknown",
                "error": str(e)
            }
        
        # Overall status
        all_healthy = all(
            check.get("status") in ["healthy", "unavailable"]
            for check in health_status["checks"].values()
        )
        health_status["overall_status"] = "healthy" if all_healthy else "degraded"
        
        self.logger.info(f"✅ Health check complete: {health_status['overall_status']}")
        return health_status
    
    def _start_system(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Start the Titan system"""
        self.logger.info("🚀 Starting Titan system...")
        
        mode = payload.get("mode", "paper")  # paper or live
        components = payload.get("components", ["brain", "executor"])
        
        results = {}
        
        # Start components
        for component in components:
            if component == "brain":
                results["brain"] = self._start_brain(mode)
            elif component == "executor":
                results["executor"] = self._start_executor(mode)
            elif component == "api":
                results["api"] = self._start_api()
        
        return {
            "status": "started",
            "mode": mode,
            "components": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def _start_brain(self, mode: str) -> Dict[str, Any]:
        """Start the AI brain component"""
        try:
            cmd = ["python3", "ml/brain.py"]
            if mode:
                cmd.extend(["--mode", mode])
            
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes["brain"] = process
            return {"status": "started", "pid": process.pid}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _start_executor(self, mode: str) -> Dict[str, Any]:
        """Start the executor component"""
        try:
            cmd = ["node", "execution/bot.js"]
            
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes["executor"] = process
            return {"status": "started", "pid": process.pid}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _start_api(self) -> Dict[str, Any]:
        """Start the API server"""
        # Placeholder for API server startup
        return {"status": "not_implemented"}
    
    def _stop_system(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Stop the Titan system"""
        self.logger.info("🛑 Stopping Titan system...")
        
        components = payload.get("components", list(self.processes.keys()))
        results = {}
        
        for component in components:
            if component in self.processes:
                process = self.processes[component]
                try:
                    process.terminate()
                    process.wait(timeout=10)
                    results[component] = {"status": "stopped"}
                except subprocess.TimeoutExpired:
                    process.kill()
                    results[component] = {"status": "killed"}
                except Exception as e:
                    results[component] = {"status": "error", "error": str(e)}
                finally:
                    del self.processes[component]
        
        return {
            "status": "stopped",
            "components": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def _restart_system(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Restart the Titan system"""
        self.logger.info("🔄 Restarting Titan system...")
        
        # Stop first
        stop_result = self._stop_system(payload)
        
        # Wait a bit
        time.sleep(2)
        
        # Start again
        start_result = self._start_system(payload)
        
        return {
            "status": "restarted",
            "stop_result": stop_result,
            "start_result": start_result,
            "timestamp": datetime.now().isoformat()
        }
    
    def _run_tests(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Run system tests"""
        self.logger.info("🧪 Running tests...")
        
        test_type = payload.get("test_type", "all")
        results = {}
        
        if test_type in ["all", "hardhat"]:
            try:
                result = subprocess.run(
                    ["npx", "hardhat", "test"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                results["hardhat"] = {
                    "passed": result.returncode == 0,
                    "output": result.stdout[-500:] if len(result.stdout) > 500 else result.stdout
                }
            except Exception as e:
                results["hardhat"] = {"passed": False, "error": str(e)}
        
        if test_type in ["all", "python"]:
            try:
                result = subprocess.run(
                    ["python3", "test_phase1.py"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                results["python"] = {
                    "passed": result.returncode == 0,
                    "output": result.stdout[-500:] if len(result.stdout) > 500 else result.stdout
                }
            except Exception as e:
                results["python"] = {"passed": False, "error": str(e)}
        
        all_passed = all(result.get("passed", False) for result in results.values())
        
        return {
            "status": "passed" if all_passed else "failed",
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def _build_project(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Build the project"""
        self.logger.info("🔨 Building project...")
        
        try:
            result = subprocess.run(
                ["npx", "hardhat", "compile"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                "status": "success" if result.returncode == 0 else "failed",
                "output": result.stdout[-500:] if len(result.stdout) > 500 else result.stdout,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _deploy(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy contracts"""
        self.logger.info("🚀 Deploying contracts...")
        
        network = payload.get("network", "localhost")
        
        # This is a placeholder - actual deployment would require more setup
        return {
            "status": "not_implemented",
            "network": network,
            "message": "Deployment requires manual configuration",
            "timestamp": datetime.now().isoformat()
        }
    
    def _monitor_performance(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor system performance"""
        # Placeholder for performance monitoring
        return {
            "status": "monitoring",
            "metrics": {
                "cpu_usage": "N/A",
                "memory_usage": "N/A",
                "active_processes": len(self.processes)
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _auto_scale(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Auto-scale system resources"""
        # Placeholder for auto-scaling logic
        return {
            "status": "not_implemented",
            "message": "Auto-scaling requires cloud infrastructure setup",
            "timestamp": datetime.now().isoformat()
        }
    
    def _self_heal(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Perform self-healing operations"""
        self.logger.info("🔧 Performing self-healing...")
        
        # Check system health
        health = self._health_check({})
        
        actions_taken = []
        
        # Example self-healing: restart unhealthy components
        if health["overall_status"] == "degraded":
            for component, status in health["checks"].items():
                if status.get("status") == "unhealthy":
                    actions_taken.append(f"Detected unhealthy {component}")
                    # Add restart logic here if needed
        
        return {
            "status": "completed",
            "health_status": health["overall_status"],
            "actions_taken": actions_taken,
            "timestamp": datetime.now().isoformat()
        }
    
    def _optimize_resources(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize system resources"""
        # Placeholder for resource optimization
        return {
            "status": "not_implemented",
            "message": "Resource optimization requires implementation",
            "timestamp": datetime.now().isoformat()
        }
