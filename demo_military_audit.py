#!/usr/bin/env python3
"""
Demo script to showcase the Military Audit System in action
This creates a simulated environment to demonstrate the validation flow
"""

import os
import sys
import time
from colorama import Fore, Style, init

init(autoreset=True)

def print_banner():
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{'TITAN 2.0 - MILITARY AUDIT SYSTEM DEMO'.center(80)}")
    print(f"{'='*80}{Style.RESET_ALL}\n")

def print_section(title):
    print(f"\n{Fore.YELLOW}{'─'*80}")
    print(f"{title}")
    print(f"{'─'*80}{Style.RESET_ALL}\n")

def simulate_gate(gate_num, gate_name, will_pass=True):
    """Simulate a validation gate"""
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"GATE {gate_num}/8: {gate_name}".center(80))
    print(f"{'='*80}{Style.RESET_ALL}\n")
    
    # Simulate running tests
    tests = [
        ("Configuration file exists", True),
        ("Module imports successfully", True),
        ("Dependencies installed", will_pass),
        ("Benchmark tests", will_pass)
    ]
    
    for test_name, passes in tests:
        time.sleep(0.3)  # Simulate test execution
        if passes:
            print(f"{Fore.GREEN}✓ {test_name}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ {test_name}{Style.RESET_ALL}")
    
    time.sleep(0.5)
    
    if will_pass:
        print(f"\n{Fore.GREEN}{'='*80}")
        print(f"{'✓ GATE PASSED - PROCEED TO NEXT MODULE'.center(80)}")
        print(f"{'='*80}{Style.RESET_ALL}\n")
        time.sleep(0.5)
        return True
    else:
        print(f"\n{Fore.RED}{'='*80}")
        print(f"{'🛑 GATE FAILED - HARD STOP'.center(80)}")
        print(f"{'='*80}{Style.RESET_ALL}\n")
        print(f"{Fore.RED}Module '{gate_name}' failed validation.{Style.RESET_ALL}")
        print(f"{Fore.RED}Fix all errors before proceeding to next module.{Style.RESET_ALL}\n")
        return False

def demo_successful_audit():
    """Demonstrate a successful audit run"""
    print_section("SCENARIO 1: Successful Full Audit")
    
    print(f"{Fore.YELLOW}This demonstrates all gates passing successfully.{Style.RESET_ALL}\n")
    time.sleep(1)
    
    gates = [
        "Configuration Module",
        "Core Infrastructure",
        "RPC Connections",
        "DEX Integration",
        "ML/AI Components",
        "Execution Engine",
        "Security Systems",
        "System Integration"
    ]
    
    for i, gate_name in enumerate(gates, 1):
        if not simulate_gate(i, gate_name, will_pass=True):
            return False
    
    # Final success
    print(f"\n{Fore.GREEN}{'='*80}")
    print(f"{'✓ ALL GATES PASSED'.center(80)}")
    print(f"{'SYSTEM IS FULLY VALIDATED AND READY FOR OPERATION'.center(80)}")
    print(f"{'='*80}{Style.RESET_ALL}\n")
    
    return True

def demo_failed_audit():
    """Demonstrate an audit with a failure"""
    print_section("SCENARIO 2: Failed Audit (Hard Stop at Gate 3)")
    
    print(f"{Fore.YELLOW}This demonstrates what happens when a gate fails.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Notice how the audit STOPS immediately - remaining gates are not run.{Style.RESET_ALL}\n")
    time.sleep(2)
    
    # Gate 1: Pass
    simulate_gate(1, "Configuration Module", will_pass=True)
    
    # Gate 2: Pass
    simulate_gate(2, "Core Infrastructure", will_pass=True)
    
    # Gate 3: FAIL - Hard stop
    simulate_gate(3, "RPC Connections", will_pass=False)
    
    print(f"\n{Fore.RED}{'='*80}")
    print(f"{'AUDIT STOPPED - REMAINING GATES NOT RUN'.center(80)}")
    print(f"{'='*80}{Style.RESET_ALL}\n")
    
    print(f"{Fore.YELLOW}To proceed:{Style.RESET_ALL}")
    print(f"  1. Fix the RPC connection issues")
    print(f"  2. Re-run the audit")
    print(f"  3. Only after ALL gates pass can you start the system\n")
    
    return False

def show_usage():
    """Show usage examples"""
    print_section("HOW TO USE THE MILITARY AUDIT SYSTEM")
    
    print(f"{Fore.CYAN}Command Line Usage:{Style.RESET_ALL}\n")
    
    print(f"  {Fore.GREEN}# Run the audit manually{Style.RESET_ALL}")
    print(f"  make military-audit")
    print(f"  # or")
    print(f"  python3 military_audit.py\n")
    
    print(f"  {Fore.GREEN}# Build with validation{Style.RESET_ALL}")
    print(f"  make validated-build\n")
    
    print(f"  {Fore.GREEN}# Start system (includes pre-start validation){Style.RESET_ALL}")
    print(f"  make start\n")
    
    print(f"{Fore.CYAN}What Each Command Does:{Style.RESET_ALL}\n")
    
    print(f"  {Fore.YELLOW}military-audit:{Style.RESET_ALL}")
    print(f"    - Runs all 8 validation gates sequentially")
    print(f"    - Tests each module for functionality and performance")
    print(f"    - Reports detailed pass/fail status\n")
    
    print(f"  {Fore.YELLOW}validated-build:{Style.RESET_ALL}")
    print(f"    - Runs military audit FIRST")
    print(f"    - Only proceeds with build if audit passes")
    print(f"    - Installs dependencies and builds components")
    print(f"    - Runs post-build validation\n")
    
    print(f"  {Fore.YELLOW}start (with validation):{Style.RESET_ALL}")
    print(f"    - Checks if system was recently validated")
    print(f"    - Runs fresh audit if validation expired")
    print(f"    - Only starts system if validated\n")
    
    print(f"{Fore.CYAN}Key Benefits:{Style.RESET_ALL}\n")
    print(f"  ✓ Catches configuration errors before they cause problems")
    print(f"  ✓ Ensures all dependencies are properly installed")
    print(f"  ✓ Validates network connectivity and RPC access")
    print(f"  ✓ Confirms security measures are in place")
    print(f"  ✓ Prevents wasted time on incomplete setups\n")

def main():
    print_banner()
    
    print(f"{Fore.CYAN}This demo shows how the Military Audit System works.{Style.RESET_ALL}")
    print(f"{Fore.CYAN}The audit validates each module sequentially with HARD STOPS on failure.{Style.RESET_ALL}\n")
    
    time.sleep(2)
    
    # Show successful audit
    demo_successful_audit()
    
    time.sleep(2)
    
    # Show failed audit
    demo_failed_audit()
    
    time.sleep(1)
    
    # Show usage
    show_usage()
    
    # Footer
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{'For full documentation, see:'.center(80)}")
    print(f"{'MILITARY_AUDIT_SYSTEM.md'.center(80)}")
    print(f"{'='*80}{Style.RESET_ALL}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Demo interrupted{Style.RESET_ALL}\n")
        sys.exit(0)
