#!/usr/bin/env python3
"""
TITAN System Wiring with Interactive Dashboard
===============================================

Example of how to integrate the interactive dashboard with the TITAN system.
This shows how to wire brain.py and bot.js outputs to the dashboard.
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dashboard_integration import DashboardIntegration


class TitanDashboardBridge:
    """
    Bridge between TITAN system components and the interactive dashboard.
    Monitors TITAN operations and feeds data to the dashboard in real-time.
    """
    
    def __init__(self):
        self.integration = DashboardIntegration()
        self.running = True
        
        # System state
        self.start_time = datetime.now()
        self.total_scans = 0
        self.opportunities_found = 0
        self.txs_executed = 0
        self.successful_txs = 0
        self.total_profit = 0.0
        self.total_gas = 0.0
        
    def on_market_scan_complete(self, scan_results: list):
        """
        Called when brain.py completes a market scan
        
        Args:
            scan_results: List of opportunities found in scan
        """
        self.total_scans += 1
        
        for opportunity in scan_results:
            self.opportunities_found += 1
            
            # Publish to dashboard
            self.integration.publish_market_opportunity({
                "chain": opportunity.get("chain"),
                "token_pair": f"{opportunity.get('token_in')}/{opportunity.get('token_out')}",
                "strategy": opportunity.get("strategy", "Flash Arbitrage"),
                "profit_usd": opportunity.get("expected_profit", 0),
                "gas_cost": opportunity.get("estimated_gas_cost", 0),
                "net_profit": opportunity.get("net_profit", 0),
                "executable": opportunity.get("executable", False),
                "dex_a": opportunity.get("dex_sell", "Unknown"),
                "dex_b": opportunity.get("dex_buy", "Unknown"),
                "spread_bps": opportunity.get("spread_bps", 0)
            })
            
            # If executable, add to queue
            if opportunity.get("executable") and opportunity.get("net_profit", 0) > 5:
                self.integration.publish_executable_tx({
                    "chain": opportunity.get("chain"),
                    "token_pair": f"{opportunity.get('token_in')}/{opportunity.get('token_out')}",
                    "strategy": opportunity.get("strategy", "Flash Arbitrage"),
                    "profit_usd": opportunity.get("expected_profit", 0),
                    "gas_cost": opportunity.get("estimated_gas_cost", 0),
                    "net_profit": opportunity.get("net_profit", 0),
                    "executable": True,
                    "dex_a": opportunity.get("dex_sell", "Unknown"),
                    "dex_b": opportunity.get("dex_buy", "Unknown"),
                    "spread_bps": opportunity.get("spread_bps", 0)
                })
        
        # Update metrics
        self._update_metrics()
    
    def on_transaction_executed(self, tx_result: dict):
        """
        Called when bot.js executes a transaction
        
        Args:
            tx_result: Result of transaction execution
        """
        self.txs_executed += 1
        
        success = tx_result.get("status") == "SUCCESS"
        if success:
            self.successful_txs += 1
            self.total_profit += tx_result.get("actual_profit", 0)
        
        self.total_gas += tx_result.get("gas_cost", 0)
        
        # Publish to dashboard
        self.integration.publish_execution_result({
            "id": tx_result.get("id", f"tx_{int(datetime.now().timestamp() * 1000000)}"),
            "chain": tx_result.get("chain"),
            "token_pair": tx_result.get("token_pair"),
            "strategy": tx_result.get("strategy"),
            "profit_usd": tx_result.get("expected_profit", 0),
            "gas_cost": tx_result.get("gas_cost", 0),
            "status": tx_result.get("status"),
            "tx_hash": tx_result.get("tx_hash"),
            "gas_used": tx_result.get("gas_used"),
            "actual_profit": tx_result.get("actual_profit", 0),
            "dex_a": tx_result.get("dex_a", "Unknown"),
            "dex_b": tx_result.get("dex_b", "Unknown")
        })
        
        # Update metrics
        self._update_metrics()
    
    def on_gas_price_update(self, gas_price: float):
        """
        Called when gas price is updated
        
        Args:
            gas_price: Current gas price in Gwei
        """
        # Just update metrics with new gas price
        self._update_metrics(current_gas_price=gas_price)
    
    def _update_metrics(self, current_gas_price: float = None):
        """Update and publish system metrics to dashboard"""
        uptime = int((datetime.now() - self.start_time).total_seconds())
        success_rate = (self.successful_txs / self.txs_executed * 100) if self.txs_executed > 0 else 0
        avg_profit = (self.total_profit / self.txs_executed) if self.txs_executed > 0 else 0
        net_profit = self.total_profit - self.total_gas
        
        # Determine status
        if success_rate < 50 and self.txs_executed > 10:
            status = "CRITICAL"
        elif success_rate < 70 and self.txs_executed > 10:
            status = "DEGRADED"
        else:
            status = "OPERATIONAL"
        
        metrics = {
            "status": status,
            "uptime": uptime,
            "total_scans": self.total_scans,
            "opportunities_found": self.opportunities_found,
            "txs_executed": self.txs_executed,
            "total_profit": round(self.total_profit, 2),
            "total_gas": round(self.total_gas, 2),
            "net_profit": round(net_profit, 2),
            "success_rate": round(success_rate, 1),
            "avg_profit_per_tx": round(avg_profit, 2),
            "current_gas_price": current_gas_price or 0
        }
        
        self.integration.update_metrics(metrics)
    
    def handle_dashboard_control(self, action: str):
        """
        Handle control actions from dashboard
        
        Args:
            action: Control action ("pause_scanning", "resume_scanning", "emergency_stop")
        """
        print(f"📊 Dashboard control received: {action}")
        
        if action == "pause_scanning":
            print("⏸️  Pausing market scanning...")
            # Implement: Send signal to brain.py to pause scanning
            # This could be done via Redis, file flag, or other IPC mechanism
            
        elif action == "resume_scanning":
            print("▶️  Resuming market scanning...")
            # Implement: Send signal to brain.py to resume scanning
            
        elif action == "emergency_stop":
            print("🛑 EMERGENCY STOP ACTIVATED!")
            # Implement: Stop brain.py and bot.js
            # Clear executable queue
            # Alert operators
    
    def start_control_listener(self):
        """Start listening for dashboard controls (blocking)"""
        print("🎮 Starting dashboard control listener...")
        self.integration.listen_for_controls(self.handle_dashboard_control)


def example_integration():
    """
    Example of integrating the dashboard with a running TITAN system.
    This simulates how you would wire the real brain.py and bot.js outputs.
    """
    
    print("🚀 TITAN Dashboard Integration Example")
    print("=" * 60)
    print()
    
    # Create bridge
    bridge = TitanDashboardBridge()
    
    # Simulate brain.py finding opportunities
    print("1. Simulating market scan...")
    scan_results = [
        {
            "chain": "Polygon",
            "token_in": "USDC",
            "token_out": "USDT",
            "strategy": "Flash Arbitrage",
            "expected_profit": 15.50,
            "estimated_gas_cost": 2.30,
            "net_profit": 13.20,
            "executable": True,
            "dex_sell": "Uniswap V3",
            "dex_buy": "Curve",
            "spread_bps": 42.5
        },
        {
            "chain": "Arbitrum",
            "token_in": "WETH",
            "token_out": "USDC",
            "strategy": "Cross-DEX",
            "expected_profit": 8.20,
            "estimated_gas_cost": 1.80,
            "net_profit": 6.40,
            "executable": True,
            "dex_sell": "Camelot",
            "dex_buy": "Uniswap V3",
            "spread_bps": 28.3
        },
        {
            "chain": "Ethereum",
            "token_in": "USDC",
            "token_out": "DAI",
            "strategy": "Flash Arbitrage",
            "expected_profit": 45.00,
            "estimated_gas_cost": 12.00,
            "net_profit": 33.00,
            "executable": True,
            "dex_sell": "Uniswap V3",
            "dex_buy": "Curve",
            "spread_bps": 85.2
        }
    ]
    
    bridge.on_market_scan_complete(scan_results)
    print(f"   ✓ Published {len(scan_results)} opportunities to dashboard")
    
    # Simulate bot.js executing a transaction
    print("\n2. Simulating transaction execution...")
    tx_result = {
        "id": "tx_123456789",
        "chain": "Polygon",
        "token_pair": "USDC/USDT",
        "strategy": "Flash Arbitrage",
        "expected_profit": 15.50,
        "gas_cost": 2.30,
        "status": "SUCCESS",
        "tx_hash": "0xabc123def456789...",
        "gas_used": 320000,
        "actual_profit": 13.15,
        "dex_a": "Uniswap V3",
        "dex_b": "Curve"
    }
    
    bridge.on_transaction_executed(tx_result)
    print("   ✓ Published execution result to dashboard")
    
    # Update gas price
    print("\n3. Simulating gas price update...")
    bridge.on_gas_price_update(45.2)
    print("   ✓ Updated gas price metrics")
    
    print("\n" + "=" * 60)
    print("✓ Integration example completed")
    print("\nDashboard should now show:")
    print("  - 3 market opportunities")
    print("  - 2 executable transactions in queue")
    print("  - 1 completed execution")
    print("  - Updated system metrics")
    print("\nOpen dashboard at: http://localhost:8080")
    

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="TITAN Dashboard Integration")
    parser.add_argument('--example', action='store_true', help='Run integration example')
    parser.add_argument('--listen', action='store_true', help='Listen for dashboard controls')
    
    args = parser.parse_args()
    
    if args.example:
        example_integration()
    elif args.listen:
        bridge = TitanDashboardBridge()
        print("Listening for dashboard controls (press Ctrl+C to stop)...")
        try:
            bridge.start_control_listener()
        except KeyboardInterrupt:
            print("\n\n👋 Stopped control listener")
    else:
        print("TITAN Dashboard Integration")
        print("\nUsage:")
        print("  python3 dashboard_wiring_example.py --example")
        print("  python3 dashboard_wiring_example.py --listen")
        print("\nThis shows how to integrate the dashboard with brain.py and bot.js")
