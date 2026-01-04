#!/usr/bin/env python3
"""
APEX-OMEGA TITAN: Super Agent Examples
=======================================

Example usage scenarios for the super agent system.
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
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.core.agent_base import Task, AgentPriority, AgentStatus
from agents.core.agent_registry import AgentRegistry, TaskScheduler
from agents.specialized.orchestrator_agent import OrchestratorAgent, OrchestratorCapability


def example_1_simple_health_check():
    """Example 1: Simple health check"""
    print("\n" + "=" * 70)
    print("Example 1: Simple Health Check")
    print("=" * 70)
    
    # Create registry
    registry = AgentRegistry()
    registry.start()
    
    # Create and register orchestrator
    orchestrator = OrchestratorAgent()
    orchestrator.initialize()
    registry.register_agent(orchestrator)
    
    # Create health check task
    task = Task(
        task_id="health_check_example",
        task_type=OrchestratorCapability.SYSTEM_HEALTH_CHECK,
        priority=AgentPriority.HIGH,
        payload={}
    )
    
    # Execute task
    registry.assign_task(task, "orchestrator-main")
    
    # Display results
    if task.result:
        print(f"\nHealth Check Result: {task.result.get('overall_status')}")
        print("\nComponent Status:")
        for component, status in task.result.get('checks', {}).items():
            print(f"  {component}: {status.get('status', 'unknown')}")
    
    # Cleanup
    registry.stop()


def example_2_multi_task_execution():
    """Example 2: Execute multiple tasks"""
    print("\n" + "=" * 70)
    print("Example 2: Multi-Task Execution")
    print("=" * 70)
    
    # Setup
    registry = AgentRegistry()
    scheduler = TaskScheduler(registry)
    registry.start()
    scheduler.start()
    
    orchestrator = OrchestratorAgent()
    orchestrator.initialize()
    registry.register_agent(orchestrator)
    
    # Create multiple tasks
    tasks = [
        Task(
            task_id="task_1_health",
            task_type=OrchestratorCapability.SYSTEM_HEALTH_CHECK,
            priority=AgentPriority.HIGH,
            payload={}
        ),
        Task(
            task_id="task_2_build",
            task_type=OrchestratorCapability.BUILD_PROJECT,
            priority=AgentPriority.MEDIUM,
            payload={}
        ),
    ]
    
    # Submit tasks to queue
    for task in tasks:
        registry.submit_task(task, target_agent_id="orchestrator-main")
    
    # Wait for completion
    print("\nTasks submitted, waiting for completion...")
    time.sleep(10)
    
    # Display results
    for task in tasks:
        print(f"\nTask: {task.task_id}")
        print(f"  Status: {'Completed' if task.result else 'Pending'}")
        if task.result:
            print(f"  Result: {task.result.get('status', 'N/A')}")
    
    # Cleanup
    scheduler.stop()
    registry.stop()


def example_3_agent_monitoring():
    """Example 3: Monitor agent status"""
    print("\n" + "=" * 70)
    print("Example 3: Agent Status Monitoring")
    print("=" * 70)
    
    # Setup
    registry = AgentRegistry()
    registry.start()
    
    orchestrator = OrchestratorAgent()
    orchestrator.initialize()
    registry.register_agent(orchestrator)
    
    # Execute a task
    task = Task(
        task_id="monitoring_example",
        task_type=OrchestratorCapability.SYSTEM_HEALTH_CHECK,
        priority=AgentPriority.HIGH,
        payload={}
    )
    registry.assign_task(task, "orchestrator-main")
    
    # Get agent status
    status = registry.get_agent_status("orchestrator-main")
    
    print("\nAgent Status:")
    print(f"  ID: {status.get('agent_id')}")
    print(f"  Type: {status.get('agent_type')}")
    print(f"  Status: {status.get('status')}")
    print(f"  Tasks Completed: {status.get('tasks_completed')}")
    print(f"  Tasks Failed: {status.get('tasks_failed')}")
    
    # Get all agents status
    all_status = registry.get_all_status()
    print(f"\nTotal Agents: {all_status.get('total_agents')}")
    
    # Cleanup
    registry.stop()


def example_4_error_handling():
    """Example 4: Error handling"""
    print("\n" + "=" * 70)
    print("Example 4: Error Handling")
    print("=" * 70)
    
    # Setup
    registry = AgentRegistry()
    registry.start()
    
    orchestrator = OrchestratorAgent()
    orchestrator.initialize()
    registry.register_agent(orchestrator)
    
    # Create task with invalid type (will fail)
    task = Task(
        task_id="error_example",
        task_type="invalid_task_type",
        priority=AgentPriority.MEDIUM,
        payload={}
    )
    
    # Try to execute
    try:
        registry.assign_task(task, "orchestrator-main")
    except Exception as e:
        print(f"\nExpected error caught: {type(e).__name__}")
        print(f"Error message: {str(e)}")
    
    # Check agent status
    status = registry.get_agent_status("orchestrator-main")
    print(f"\nAgent still operational: {status.get('status')}")
    print(f"Failed tasks count: {status.get('tasks_failed')}")
    
    # Cleanup
    registry.stop()


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("APEX-OMEGA TITAN: Super Agent Examples")
    print("=" * 70)
    
    examples = [
        example_1_simple_health_check,
        example_2_multi_task_execution,
        example_3_agent_monitoring,
        example_4_error_handling,
    ]
    
    for i, example in enumerate(examples, 1):
        try:
            example()
            print(f"\n✅ Example {i} completed successfully")
        except Exception as e:
            print(f"\n❌ Example {i} failed: {e}")
        
        if i < len(examples):
            print("\nPress Enter to continue...")
            input()
    
    print("\n" + "=" * 70)
    print("All examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
