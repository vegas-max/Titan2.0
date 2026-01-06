#!/usr/bin/env python3
"""
APEX-OMEGA TITAN: Super Agent Manager
======================================

Main entry point for the creative super agent system.
This manages and coordinates all agents in the repository.
"""

# Configure UTF-8 encoding for Windows console output
# This must be done before any imports that might trigger logging
import sys
import os

if sys.platform == 'win32':
    # Set environment variable for Python IO encoding
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # Reconfigure stdout and stderr to use UTF-8 encoding
    # This allows emoji and other Unicode characters to be displayed correctly
    # on Windows systems where the default console encoding is cp1252
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    else:
        # Fallback for older Python versions
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import time
import signal
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.core.agent_base import Task, AgentPriority, AgentConfig, AgentStatus
from agents.core.agent_registry import AgentRegistry, TaskScheduler
from agents.specialized.orchestrator_agent import OrchestratorAgent, OrchestratorCapability


class SuperAgentManager:
    """Main manager for the creative super agent system"""
    
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger("SuperAgentManager")
        self.registry = AgentRegistry()
        self.scheduler = TaskScheduler(self.registry)
        self.running = False
        self.config = AgentConfig()
        
    def setup_logging(self):
        """Setup logging configuration"""
        # Ensure logs directory exists first
        (project_root / 'logs').mkdir(exist_ok=True)
        
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # Create handlers with explicit UTF-8 encoding to support emoji on Windows
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setStream(sys.stdout)  # Use the reconfigured stdout
        
        file_handler = logging.FileHandler(
            project_root / 'logs' / f'super_agent_{datetime.now().strftime("%Y%m%d")}.log',
            mode='a',
            encoding='utf-8'  # Explicitly set UTF-8 encoding for file handler
        )
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s',
            handlers=[stream_handler, file_handler]
        )
    
    def initialize(self) -> bool:
        """Initialize the super agent system"""
        self.logger.info("=" * 70)
        self.logger.info("🚀 APEX-OMEGA TITAN: SUPER AGENT SYSTEM")
        self.logger.info("=" * 70)
        self.logger.info("Initializing creative super agent system...")
        
        # Create and register orchestrator agent
        orchestrator = OrchestratorAgent()
        if not orchestrator.initialize():
            self.logger.error("Failed to initialize orchestrator agent")
            return False
        
        if not self.registry.register_agent(orchestrator):
            self.logger.error("Failed to register orchestrator agent")
            return False
        
        # Start the registry and scheduler
        self.registry.start()
        self.scheduler.start()
        
        self.running = True
        self.logger.info("✅ Super agent system initialized successfully")
        
        # Check if auto-build on boot is enabled
        system_config = self.config.config.get("system", {})
        if system_config.get("run_build_on_boot", False):
            self.logger.info("🔨 Auto-build on boot is enabled, building project...")
            self.build_project()
        
        self.logger.info("=" * 70)
        return True
    
    def run_health_check(self):
        """Run a system health check"""
        self.logger.info("🔍 Running system health check...")
        
        task = Task(
            task_id=f"health_check_{int(time.time())}",
            task_type=OrchestratorCapability.SYSTEM_HEALTH_CHECK,
            priority=AgentPriority.HIGH,
            payload={}
        )
        
        self.registry.assign_task(task, "orchestrator-main")
        
        if task.result:
            self.logger.info(f"Health check result: {task.result.get('overall_status')}")
            for check_name, check_result in task.result.get('checks', {}).items():
                status = check_result.get('status', 'unknown')
                self.logger.info(f"  - {check_name}: {status}")
        
        return task.result
    
    def start_system(self, mode: str = "paper", components: Optional[list] = None):
        """Start the Titan system"""
        self.logger.info(f"🚀 Starting Titan system in {mode.upper()} mode...")
        
        if components is None:
            components = ["brain", "executor"]
        
        task = Task(
            task_id=f"start_system_{int(time.time())}",
            task_type=OrchestratorCapability.START_SYSTEM,
            priority=AgentPriority.HIGH,
            payload={
                "mode": mode,
                "components": components
            }
        )
        
        self.registry.assign_task(task, "orchestrator-main")
        
        if task.result:
            self.logger.info(f"System start result: {task.result.get('status')}")
            for component, result in task.result.get('components', {}).items():
                self.logger.info(f"  - {component}: {result.get('status')}")
        
        return task.result
    
    def stop_system(self, components: Optional[list] = None):
        """Stop the Titan system"""
        self.logger.info("🛑 Stopping Titan system...")
        
        task = Task(
            task_id=f"stop_system_{int(time.time())}",
            task_type=OrchestratorCapability.STOP_SYSTEM,
            priority=AgentPriority.HIGH,
            payload={"components": components} if components else {}
        )
        
        self.registry.assign_task(task, "orchestrator-main")
        
        if task.result:
            self.logger.info(f"System stop result: {task.result.get('status')}")
        
        return task.result
    
    def run_tests(self, test_type: str = "all"):
        """Run system tests"""
        self.logger.info(f"🧪 Running {test_type} tests...")
        
        task = Task(
            task_id=f"run_tests_{int(time.time())}",
            task_type=OrchestratorCapability.RUN_TESTS,
            priority=AgentPriority.MEDIUM,
            payload={"test_type": test_type}
        )
        
        self.registry.assign_task(task, "orchestrator-main")
        
        if task.result:
            self.logger.info(f"Test result: {task.result.get('status')}")
        
        return task.result
    
    def build_project(self):
        """Build the project"""
        self.logger.info("🔨 Building project...")
        
        task = Task(
            task_id=f"build_project_{int(time.time())}",
            task_type=OrchestratorCapability.BUILD_PROJECT,
            priority=AgentPriority.MEDIUM,
            payload={}
        )
        
        self.registry.assign_task(task, "orchestrator-main")
        
        if task.result:
            self.logger.info(f"Build result: {task.result.get('status')}")
        
        return task.result
    
    def show_status(self):
        """Show system status"""
        self.logger.info("=" * 70)
        self.logger.info("📊 SYSTEM STATUS")
        self.logger.info("=" * 70)
        
        status = self.registry.get_all_status()
        
        self.logger.info(f"Total Agents: {status['total_agents']}")
        self.logger.info("")
        
        for agent_id, agent_status in status['agents'].items():
            self.logger.info(f"Agent: {agent_id}")
            self.logger.info(f"  Type: {agent_status['agent_type']}")
            self.logger.info(f"  Status: {agent_status['status']}")
            self.logger.info(f"  Tasks Completed: {agent_status['tasks_completed']}")
            self.logger.info(f"  Tasks Failed: {agent_status['tasks_failed']}")
            if agent_status.get('uptime_seconds'):
                uptime_hours = agent_status['uptime_seconds'] / 3600
                self.logger.info(f"  Uptime: {uptime_hours:.2f} hours")
            self.logger.info("")
        
        self.logger.info("=" * 70)
    
    def interactive_mode(self):
        """Run in interactive mode"""
        self.logger.info("🎮 Entering interactive mode...")
        self.logger.info("Type 'help' for available commands, 'quit' to exit")
        
        while self.running:
            try:
                command = input("\n🤖 super-agent> ").strip().lower()
                
                if command == "quit" or command == "exit":
                    break
                elif command == "help":
                    self._show_help()
                elif command == "status":
                    self.show_status()
                elif command == "health":
                    self.run_health_check()
                elif command.startswith("start"):
                    parts = command.split()
                    mode = parts[1] if len(parts) > 1 else "paper"
                    self.start_system(mode)
                elif command == "stop":
                    self.stop_system()
                elif command.startswith("test"):
                    parts = command.split()
                    test_type = parts[1] if len(parts) > 1 else "all"
                    self.run_tests(test_type)
                elif command == "build":
                    self.build_project()
                else:
                    self.logger.warning(f"Unknown command: {command}")
                    
            except KeyboardInterrupt:
                self.logger.info("\nInterrupted by user")
                break
            except Exception as e:
                self.logger.error(f"Error executing command: {e}")
    
    def _show_help(self):
        """Show help information"""
        help_text = """
Available Commands:
-------------------
  status          - Show system status and agent information
  health          - Run system health check
  start [mode]    - Start Titan system (mode: paper or live)
  stop            - Stop Titan system
  test [type]     - Run tests (type: all, hardhat, python)
  build           - Build the project
  help            - Show this help message
  quit/exit       - Exit the super agent system
        """
        print(help_text)
    
    def shutdown(self):
        """Shutdown the super agent system"""
        self.logger.info("=" * 70)
        self.logger.info("🛑 Shutting down super agent system...")
        
        # Stop scheduler
        self.scheduler.stop()
        
        # Stop registry and all agents
        self.registry.stop()
        
        self.running = False
        self.logger.info("✅ Super agent system shutdown complete")
        self.logger.info("=" * 70)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="APEX-OMEGA TITAN Super Agent Manager"
    )
    parser.add_argument(
        "--mode",
        choices=["interactive", "daemon", "once"],
        default="interactive",
        help="Run mode: interactive, daemon, or once"
    )
    parser.add_argument(
        "--action",
        choices=["health", "start", "stop", "test", "build", "status"],
        help="Action to perform in 'once' mode"
    )
    parser.add_argument(
        "--system-mode",
        choices=["paper", "live"],
        default="paper",
        help="System mode for start action"
    )
    
    args = parser.parse_args()
    
    # Create super agent manager
    manager = SuperAgentManager()
    
    # Setup signal handlers
    def signal_handler(sig, frame):
        manager.logger.info("\nReceived shutdown signal")
        manager.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize
    if not manager.initialize():
        manager.logger.error("Failed to initialize super agent system")
        return 1
    
    # Run based on mode
    try:
        if args.mode == "interactive":
            manager.interactive_mode()
        elif args.mode == "daemon":
            manager.logger.info("Running in daemon mode (Ctrl+C to stop)...")
            while manager.running:
                time.sleep(1)
        elif args.mode == "once":
            if args.action == "health":
                manager.run_health_check()
            elif args.action == "start":
                manager.start_system(args.system_mode)
            elif args.action == "stop":
                manager.stop_system()
            elif args.action == "test":
                manager.run_tests()
            elif args.action == "build":
                manager.build_project()
            elif args.action == "status":
                manager.show_status()
            else:
                manager.logger.error("Action required for 'once' mode")
                return 1
    finally:
        manager.shutdown()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
