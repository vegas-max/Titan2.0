#!/usr/bin/env python3
"""
APEX-OMEGA TITAN: Super Agent Demo
===================================

Quick demonstration of the super agent system capabilities.
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.super_agent_manager import SuperAgentManager


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(text.center(70))
    print("=" * 70 + "\n")


def demo():
    """Run a quick demo of the super agent system"""
    print_header("🤖 APEX-OMEGA TITAN: SUPER AGENT DEMO")
    
    print("This demo showcases the key capabilities of the Super Agent System.")
    print("\nInitializing Super Agent Manager...")
    
    # Create manager
    manager = SuperAgentManager()
    
    # Initialize
    if not manager.initialize():
        print("❌ Failed to initialize")
        return
    
    print("\n✅ Super Agent System initialized successfully!")
    
    # Demo 1: Health Check
    print_header("DEMO 1: System Health Check")
    print("Performing comprehensive system health check...")
    result = manager.run_health_check()
    
    if result:
        print(f"\n📊 Overall Status: {result.get('overall_status', 'unknown').upper()}")
        print("\n📋 Component Details:")
        for component, status in result.get('checks', {}).items():
            status_symbol = "✅" if status.get('status') == 'healthy' else "⚠️"
            print(f"  {status_symbol} {component.replace('_', ' ').title()}: {status.get('status', 'unknown')}")
            if 'version' in status:
                print(f"     Version: {status['version']}")
    
    time.sleep(2)
    
    # Demo 2: Agent Status
    print_header("DEMO 2: Agent Status")
    print("Displaying current agent status...")
    manager.show_status()
    
    time.sleep(2)
    
    # Demo 3: Build Project
    print_header("DEMO 3: Project Build")
    print("Attempting to build the project...")
    print("(This may fail if dependencies are not installed)")
    
    build_result = manager.build_project()
    if build_result:
        print(f"\n📦 Build Status: {build_result.get('status', 'unknown').upper()}")
    
    time.sleep(2)
    
    # Demo 4: Capabilities Overview
    print_header("DEMO 4: Available Capabilities")
    
    print("The Super Agent System provides the following capabilities:\n")
    
    capabilities = [
        ("🔍 System Health Check", "Monitor Node.js, Python, Redis, and disk space"),
        ("🚀 Start/Stop System", "Control TITAN components (brain, executor, API)"),
        ("🔄 Restart System", "Gracefully restart all components"),
        ("🧪 Run Tests", "Execute Hardhat and Python test suites"),
        ("🔨 Build Project", "Compile smart contracts"),
        ("📊 Monitor Performance", "Track CPU, memory, and processes"),
        ("🔧 Self-Heal", "Automatic failure detection and recovery"),
        ("⚙️ Optimize Resources", "Resource allocation optimization"),
    ]
    
    for name, description in capabilities:
        print(f"  {name}")
        print(f"     {description}\n")
    
    time.sleep(2)
    
    # Demo 5: Usage Examples
    print_header("DEMO 5: Quick Usage Examples")
    
    print("Interactive Mode:")
    print("  ./start_super_agent.sh")
    print("  🤖 super-agent> health")
    print("  🤖 super-agent> start paper")
    print("  🤖 super-agent> status\n")
    
    print("Command-Line Mode:")
    print("  ./start_super_agent.sh once health")
    print("  ./start_super_agent.sh once start paper")
    print("  ./start_super_agent.sh once test\n")
    
    print("Daemon Mode:")
    print("  ./start_super_agent.sh daemon")
    print("  (Runs in background)\n")
    
    time.sleep(2)
    
    # Wrap up
    print_header("DEMO COMPLETE")
    
    print("The Super Agent System is ready to manage your TITAN repository!")
    print("\n📚 For more information:")
    print("  - Full Guide: SUPER_AGENT_GUIDE.md")
    print("  - Quick Reference: SUPER_AGENT_QUICKREF.md")
    print("  - Examples: agents/examples.py")
    
    print("\n🚀 To get started, run:")
    print("  ./start_super_agent.sh\n")
    
    # Cleanup
    manager.shutdown()
    
    print_header("Thank you for using APEX-OMEGA TITAN Super Agent System!")


if __name__ == "__main__":
    try:
        demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        sys.exit(1)
