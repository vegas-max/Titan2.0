#!/usr/bin/env python3
"""
Comprehensive demo of the unified terminal display
Simulates a complete system operation with opportunities, decisions, and executions
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from offchain.core.terminal_display import get_terminal_display
import time

def demo_full_system():
    """Demonstrate complete system operation"""
    
    display = get_terminal_display()
    
    # Print header
    display.print_header("PAPER")
    
    print("Simulating Titan arbitrage system operation...\n")
    time.sleep(1)
    
    # Initialize stats
    display.stats['opportunities_scanned'] = 0
    display.stats['opportunities_profitable'] = 0
    display.stats['opportunities_signaled'] = 0
    
    # Simulate opportunity scanning cycle
    print("=" * 80)
    print("SCANNING PHASE - Looking for arbitrage opportunities")
    print("=" * 80 + "\n")
    time.sleep(1)
    
    # Scan 1: Not profitable
    display.log_opportunity_scan(
        token="DAI", chain_id=137, dex1="UNIV3", dex2="QUICKSWAP",
        amount_usd=500, profitable=False, gas_gwei=28.5
    )
    time.sleep(0.3)
    
    # Scan 2: Not profitable
    display.log_opportunity_scan(
        token="USDT", chain_id=1, dex1="UNIV3", dex2="SUSHI",
        amount_usd=1000, profitable=False, gas_gwei=55.2
    )
    time.sleep(0.3)
    
    # Scan 3: Profitable!
    display.log_opportunity_scan(
        token="WETH", chain_id=42161, dex1="UNIV3", dex2="SUSHI",
        amount_usd=2000, profitable=True, profit_usd=8.50, 
        gas_gwei=0.8, details="Size: $2000"
    )
    time.sleep(0.5)
    
    # Decision phase
    print("\n" + "=" * 80)
    print("DECISION PHASE - Analyzing profitable opportunity")
    print("=" * 80 + "\n")
    time.sleep(1)
    
    # Gas check decision
    display.log_decision(
        decision_type="GAS_CHECK",
        token="WETH",
        chain_id=42161,
        reason="Gas price within acceptable range",
        details={'current': 0.8, 'threshold': 50.0}
    )
    time.sleep(0.5)
    
    # AI parameter tuning
    display.log_decision(
        decision_type="AI_TUNE",
        token="WETH",
        chain_id=42161,
        reason="Optimizing execution parameters with ML",
        details={'slippage': 45, 'priority': 25, 'confidence': 0.85}
    )
    time.sleep(0.5)
    
    # Approval decision
    display.log_decision(
        decision_type="APPROVE",
        token="WETH",
        chain_id=42161,
        reason="Profitable trade approved for execution",
        details={'net_profit': 8.50, 'roi': 0.425}
    )
    time.sleep(0.5)
    
    # Signal generation
    print("\n" + "=" * 80)
    print("SIGNAL GENERATION - Creating execution signal")
    print("=" * 80 + "\n")
    time.sleep(1)
    
    display.log_signal_generated(
        token="WETH",
        chain_id=42161,
        profit_usd=8.50,
        route=["UNIV3", "SUSHI"],
        gas_gwei=0.8,
        execution_params={'slippage': 45, 'priority': 25, 'deadline': 120}
    )
    time.sleep(1)
    
    # More scans
    print("\n" + "=" * 80)
    print("CONTINUED SCANNING - Monitoring for more opportunities")
    print("=" * 80 + "\n")
    time.sleep(1)
    
    for i in range(5):
        tokens = ["USDC", "DAI", "USDT", "LINK", "UNI"]
        chains = [137, 1, 10, 8453, 42161]
        display.log_opportunity_scan(
            token=tokens[i], chain_id=chains[i], 
            dex1="UNIV3", dex2="SUSHI",
            amount_usd=500 + i*200, profitable=False,
            gas_gwei=20 + i*5
        )
        time.sleep(0.2)
    
    # Another profitable opportunity
    display.log_opportunity_scan(
        token="USDC", chain_id=137, dex1="UNIV3", dex2="QUICKSWAP",
        amount_usd=1500, profitable=True, profit_usd=12.30,
        gas_gwei=32.1, details="Size: $1500"
    )
    time.sleep(0.5)
    
    # Decision for second opportunity
    display.log_decision(
        decision_type="AI_TUNE",
        token="USDC",
        chain_id=137,
        reason="ML-optimized parameters",
        details={'slippage': 50, 'priority': 30}
    )
    time.sleep(0.3)
    
    display.log_decision(
        decision_type="APPROVE",
        token="USDC",
        chain_id=137,
        reason="Approved for execution",
        details={'net_profit': 12.30}
    )
    time.sleep(0.3)
    
    display.log_signal_generated(
        token="USDC",
        chain_id=137,
        profit_usd=12.30,
        route=["UNIV3", "QUICKSWAP"],
        gas_gwei=32.1,
        execution_params={'slippage': 50, 'priority': 30}
    )
    time.sleep(1)
    
    # Print stats
    print("\n" + "=" * 80)
    print("SYSTEM STATISTICS")
    print("=" * 80 + "\n")
    
    display.stats['opportunities_scanned'] = 11
    display.stats['opportunities_profitable'] = 2
    display.stats['opportunities_signaled'] = 2
    display.stats['executions_attempted'] = 2
    display.stats['executions_successful'] = 2
    display.stats['paper_trades'] = 2
    display.stats['total_profit_usd'] = 20.80
    
    display.print_stats_bar()
    time.sleep(1)
    
    # Gas updates
    print("\n" + "=" * 80)
    print("GAS PRICE MONITORING")
    print("=" * 80 + "\n")
    time.sleep(0.5)
    
    display.log_gas_update(chain_id=1, gas_gwei=55.2, threshold=100.0)
    display.log_gas_update(chain_id=137, gas_gwei=32.1, threshold=50.0)
    display.log_gas_update(chain_id=42161, gas_gwei=0.8, threshold=10.0)
    time.sleep(1)
    
    # Warnings
    print("\n" + "=" * 80)
    print("SYSTEM MONITORING")
    print("=" * 80 + "\n")
    time.sleep(0.5)
    
    display.log_warning("BRAIN", "High scan rate detected, throttling recommended")
    time.sleep(0.3)
    display.log_info("ML Model updated with latest market data")
    time.sleep(0.3)
    display.log_info("Signal written to: signals/outgoing/signal_1735714506_WETH.json")
    
    print("\n" + "=" * 80)
    print("✅ DEMO COMPLETE - Terminal display fully operational!")
    print("=" * 80 + "\n")
    
    print("The terminal display provides:")
    print("  ✓ Real-time opportunity scanning with profit estimates")
    print("  ✓ System decision logic (gas checks, AI tuning, approvals)")
    print("  ✓ Detailed signal generation information")
    print("  ✓ Comprehensive statistics tracking")
    print("  ✓ Gas price monitoring across chains")
    print("  ✓ Clear warnings and status messages")
    print("\nAll information is color-coded and timestamped for easy monitoring.\n")

if __name__ == "__main__":
    demo_full_system()
