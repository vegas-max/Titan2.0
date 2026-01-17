#!/usr/bin/env python3
"""
Quick verification script for Titan 2.0 execution paths
Run this to verify all critical paths are operational
"""

import os
import sys

def check_file(filepath, description=""):
    """Check if a critical file exists"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {filepath:50} {description}")
    return exists

def main():
    print("=" * 80)
    print("TITAN 2.0 - EXECUTION PATH VERIFICATION")
    print("=" * 80)
    print()
    
    print("### Critical Entry Points")
    print("-" * 80)
    checks = []
    checks.append(check_file("mainnet_orchestrator.py", "[PRIMARY ENTRY]"))
    checks.append(check_file("arm_brain.py", "[ARM OPTIMIZED]"))
    checks.append(check_file("production_deployment.py", "[VALIDATION]"))
    checks.append(check_file("comprehensive_simulation.py", "[SIMULATION]"))
    
    print()
    print("### Core Brain Components")
    print("-" * 80)
    checks.append(check_file("offchain/ml/brain.py", "[CORE ENGINE]"))
    checks.append(check_file("offchain/ml/dex_pricer.py", "[PRICE QUERIES]"))
    checks.append(check_file("offchain/core/config.py", "[CONFIGURATION]"))
    checks.append(check_file("offchain/core/token_discovery.py", "[TOKEN LOADING]"))
    
    print()
    print("### Execution Layer")
    print("-" * 80)
    checks.append(check_file("offchain/execution/bot.js", "[MAIN BOT]"))
    checks.append(check_file("execution/arbitrage_engine.js", "[CONTRACT SELECTION]"))
    checks.append(check_file("offchain/execution/gas_manager.js", "[GAS MANAGEMENT]"))
    
    print()
    print("### Routing & Bridges")
    print("-" * 80)
    checks.append(check_file("routing/bridge_manager.py", "[BRIDGE ROUTING]"))
    checks.append(check_file("routing/lifi_wrapper.py", "[LIFI INTEGRATION]"))
    checks.append(check_file("routing/bridge_aggregator.py", "[BRIDGE AGGREGATOR]"))
    
    print()
    print("### ML/AI Components (Optional)")
    print("-" * 80)
    checks.append(check_file("offchain/ml/cortex/forecaster.py", "[ML FORECASTING]"))
    checks.append(check_file("offchain/ml/cortex/rl_optimizer.py", "[RL OPTIMIZATION]"))
    
    print()
    print("### Signal Directories")
    print("-" * 80)
    checks.append(check_file("signals/", "[SIGNALS DIR]"))
    checks.append(check_file("signals/processed/", "[PROCESSED SIGNALS]"))
    
    print()
    print("### Documentation")
    print("-" * 80)
    checks.append(check_file("COMPREHENSIVE_EXECUTION_PATHS_DIAGRAM.md", "[FULL DIAGRAM]"))
    checks.append(check_file("EXECUTION_PATHS_SUMMARY.md", "[EXEC SUMMARY]"))
    checks.append(check_file("DATA_FLOW_VISUALIZATION.md", "[DATA FLOW]"))
    
    print()
    print("=" * 80)
    success_count = sum(checks)
    total_count = len(checks)
    percentage = (success_count / total_count * 100) if total_count > 0 else 0
    
    print(f"VERIFICATION RESULTS: {success_count}/{total_count} checks passed ({percentage:.1f}%)")
    print("=" * 80)
    
    if success_count == total_count:
        print()
        print("✅ ALL CRITICAL FILES PRESENT - SYSTEM READY")
        print()
        return 0
    else:
        print()
        print(f"⚠️  {total_count - success_count} files missing - review required")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
