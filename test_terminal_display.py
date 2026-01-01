#!/usr/bin/env python3
"""
Test script for terminal display functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from offchain.core.terminal_display import get_terminal_display
import time

def test_terminal_display():
    """Test all terminal display features"""
    
    display = get_terminal_display()
    
    print("\n" + "="*80)
    print("Testing Terminal Display Module")
    print("="*80 + "\n")
    
    # Test 1: Header
    print("Test 1: Header Display")
    display.print_header("PAPER")
    time.sleep(1)
    
    # Test 2: Opportunity Scanning
    print("\nTest 2: Opportunity Scanning")
    display.log_opportunity_scan(
        token="USDC",
        chain_id=137,
        dex1="UNIV3",
        dex2="SUSHI",
        amount_usd=1000,
        profitable=False,
        gas_gwei=25.5
    )
    time.sleep(0.5)
    
    display.log_opportunity_scan(
        token="WETH",
        chain_id=1,
        dex1="UNIV3",
        dex2="SUSHI",
        amount_usd=2000,
        profitable=True,
        profit_usd=15.50,
        gas_gwei=45.2,
        details="Size: $2000"
    )
    time.sleep(1)
    
    # Test 3: Decision Logging
    print("\nTest 3: Decision Logging")
    display.log_decision(
        decision_type="AI_TUNE",
        token="USDC",
        chain_id=137,
        reason="AI-optimized execution parameters",
        details={'slippage': 50, 'priority': 30}
    )
    time.sleep(0.5)
    
    display.log_decision(
        decision_type="APPROVE",
        token="WETH",
        chain_id=1,
        reason="Profitable opportunity approved",
        details={'profit_usd': 15.50, 'gas_gwei': 45.2}
    )
    time.sleep(1)
    
    # Test 4: Signal Generation
    print("\nTest 4: Signal Generation")
    display.log_signal_generated(
        token="WETH",
        chain_id=1,
        profit_usd=15.50,
        route=["UNIV3", "SUSHI"],
        gas_gwei=45.2,
        execution_params={'slippage': 50, 'priority': 30}
    )
    time.sleep(1)
    
    # Test 5: Gas Updates
    print("\nTest 5: Gas Price Updates")
    display.log_gas_update(chain_id=137, gas_gwei=25.5, threshold=50.0)
    display.log_gas_update(chain_id=1, gas_gwei=150.0, threshold=100.0)
    time.sleep(1)
    
    # Test 6: Stats Bar
    print("\nTest 6: Stats Bar")
    # Simulate some activity
    display.stats['opportunities_scanned'] = 150
    display.stats['opportunities_profitable'] = 12
    display.stats['opportunities_signaled'] = 8
    display.stats['executions_attempted'] = 8
    display.stats['executions_successful'] = 7
    display.stats['executions_failed'] = 1
    display.stats['total_profit_usd'] = 125.50
    display.print_stats_bar()
    time.sleep(1)
    
    # Test 7: Warnings and Errors
    print("\nTest 7: Warnings and Errors")
    display.log_warning("BRAIN", "Gas price approaching threshold")
    display.log_error("BRAIN", "Failed to fetch price", "API rate limit exceeded")
    time.sleep(1)
    
    # Test 8: Info messages
    print("\nTest 8: Info Messages")
    display.log_info("System initialized successfully")
    time.sleep(1)
    
    print("\n" + "="*80)
    print("✅ All Terminal Display Tests Passed!")
    print("="*80 + "\n")

if __name__ == "__main__":
    test_terminal_display()
