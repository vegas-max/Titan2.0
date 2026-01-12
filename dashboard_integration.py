#!/usr/bin/env python3
"""
TITAN Dashboard Integration Module
===================================

Connects the TITAN system (brain.py and bot.js) to the interactive dashboard
by publishing real-time data to SQLite cache and JSON files for dashboard consumption.

This module acts as a bridge between TITAN's operations and the dashboard server.
"""

import os
import sys
import json
import time
import asyncio
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

# Import cache manager
try:
    from offchain.core.cache_manager import get_cache_manager
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    print("WARNING: cache_manager not available")


class DashboardIntegration:
    """
    Integration layer between TITAN system and dashboard.
    Monitors TITAN operations and publishes to cache and files for dashboard display.
    """
    
    def __init__(self):
        self.cache = None
        self.running = True
        
        # Setup data directories
        self.data_dir = Path(__file__).parent / "data" / "dashboard"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Connect to cache
        self._connect_cache()
    
    def _connect_cache(self):
        """Connect to cache manager"""
        try:
            if CACHE_AVAILABLE:
                self.cache = get_cache_manager()
                print("✓ Connected to cache manager")
            else:
                print("⚠️  Cache manager not available, using file-only mode")
        except Exception as e:
            print(f"ERROR: Failed to initialize cache: {e}")
    
    def publish_market_opportunity(self, opportunity: dict):
        """
        Publish a market opportunity to dashboard
        
        Args:
            opportunity: Dict with keys:
                - chain: str
                - token_pair: str
                - strategy: str
                - profit_usd: float
                - gas_cost: float
                - net_profit: float
                - executable: bool
                - dex_a: str
                - dex_b: str
                - spread_bps: float
        """
        try:
            opportunity['timestamp'] = datetime.now().isoformat()
            opportunity['id'] = f"opp_{int(time.time() * 1000000)}"
            
            # Write to file
            opp_file = self.data_dir / "opportunities" / f"{opportunity['id']}.json"
            opp_file.parent.mkdir(parents=True, exist_ok=True)
            with open(opp_file, 'w') as f:
                json.dump(opportunity, f, indent=2)
            
            # Cache latest opportunity
            if self.cache:
                self.cache.set(f"opp:{opportunity['id']}", opportunity, ttl=300)
                self.cache.set_metric("latest_opportunity", opportunity)
            
            # Keep only last 100 opportunity files
            opp_files = sorted(list((self.data_dir / "opportunities").glob("*.json")))
            if len(opp_files) > 100:
                for old_file in opp_files[:-100]:
                    old_file.unlink()
            
        except Exception as e:
            print(f"Error publishing market opportunity: {e}")
    
    def publish_executable_tx(self, tx: dict):
        """
        Publish an executable transaction to dashboard
        
        Args:
            tx: Dict with opportunity data plus:
                - status: "PENDING"
                - queued_at: ISO timestamp
        """
        try:
            tx['queued_at'] = datetime.now().isoformat()
            tx['id'] = tx.get('id') or f"tx_{int(time.time() * 1000000)}"
            tx['status'] = 'PENDING'
            
            # Write to file
            tx_file = self.data_dir / "pending_txs" / f"{tx['id']}.json"
            tx_file.parent.mkdir(parents=True, exist_ok=True)
            with open(tx_file, 'w') as f:
                json.dump(tx, f, indent=2)
            
            # Cache in metrics
            if self.cache:
                self.cache.set(f"tx:{tx['id']}", tx, ttl=600)
                # Maintain a list of pending tx IDs
                pending = self.cache.get_metric("pending_txs") or []
                pending.append(tx['id'])
                # Keep only last 50
                pending = pending[-50:]
                self.cache.set_metric("pending_txs", pending)
            
        except Exception as e:
            print(f"Error publishing executable tx: {e}")
    
    def publish_execution_result(self, result: dict):
        """
        Publish a transaction execution result to dashboard
        
        Args:
            result: Dict with keys:
                - id: str (matching the executable tx id)
                - status: "SUCCESS" or "FAILED"
                - executed_at: ISO timestamp
                - tx_hash: str
                - gas_used: int
                - actual_profit: float
        """
        try:
            result['executed_at'] = datetime.now().isoformat()
            
            # Write to file
            result_file = self.data_dir / "execution_history" / f"{result['id']}.json"
            result_file.parent.mkdir(parents=True, exist_ok=True)
            with open(result_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            # Remove pending tx file if exists
            pending_file = self.data_dir / "pending_txs" / f"{result['id']}.json"
            if pending_file.exists():
                pending_file.unlink()
            
            # Update cache
            if self.cache:
                # Add to execution history
                history = self.cache.get_metric("execution_history") or []
                history.append(result)
                # Keep only last 100
                history = history[-100:]
                self.cache.set_metric("execution_history", history)
                
                # Remove from pending list
                pending = self.cache.get_metric("pending_txs") or []
                if result.get('id') in pending:
                    pending.remove(result.get('id'))
                    self.cache.set_metric("pending_txs", pending)
            
            # Keep only last 100 execution files
            exec_files = sorted(list((self.data_dir / "execution_history").glob("*.json")))
            if len(exec_files) > 100:
                for old_file in exec_files[:-100]:
                    old_file.unlink()
            
        except Exception as e:
            print(f"Error publishing execution result: {e}")
    
    def update_metrics(self, metrics: dict):
        """
        Update system metrics for dashboard
        
        Args:
            metrics: Dict with keys:
                - status: str ("OPERATIONAL", "DEGRADED", "CRITICAL")
                - uptime: int (seconds)
                - total_scans: int
                - opportunities_found: int
                - txs_executed: int
                - total_profit: float
                - total_gas: float
                - net_profit: float
                - success_rate: float
                - avg_profit_per_tx: float
                - current_gas_price: float
        """
        try:
            metrics['updated_at'] = datetime.now().isoformat()
            
            # Write to file
            metrics_file = self.data_dir / "current_metrics.json"
            with open(metrics_file, 'w') as f:
                json.dump(metrics, f, indent=2)
            
            # Update cache
            if self.cache:
                self.cache.set_metric("system_metrics", metrics)
            
        except Exception as e:
            print(f"Error updating metrics: {e}")
    
    def listen_for_controls(self, callback):
        """
        Listen for control messages from dashboard (file-based)
        
        Args:
            callback: Function to call with control action
                      callback(action: str) where action is one of:
                      - "pause_scanning"
                      - "resume_scanning"
                      - "emergency_stop"
        """
        try:
            control_file = self.data_dir / "controls" / "pending_action.json"
            control_file.parent.mkdir(parents=True, exist_ok=True)
            
            print("✓ Listening for dashboard control messages (file-based)...")
            
            last_mtime = 0
            while self.running:
                try:
                    if control_file.exists():
                        mtime = control_file.stat().st_mtime
                        if mtime > last_mtime:
                            last_mtime = mtime
                            with open(control_file, 'r') as f:
                                data = json.load(f)
                            
                            action = data.get('action')
                            if action:
                                callback(action)
                            
                            # Remove processed control file
                            control_file.unlink()
                    
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error processing control message: {e}")
                    time.sleep(1)
                        
        except KeyboardInterrupt:
            print("\nStopping control listener...")
        except Exception as e:
            print(f"Error in control listener: {e}")


def example_usage():
    """Example of how to integrate with TITAN system"""
    
    integration = DashboardIntegration()
    
    # Example: Publish a market opportunity
    integration.publish_market_opportunity({
        "chain": "Polygon",
        "token_pair": "USDC/USDT",
        "strategy": "Flash Arbitrage",
        "profit_usd": 15.50,
        "gas_cost": 2.30,
        "net_profit": 13.20,
        "executable": True,
        "dex_a": "Uniswap V3",
        "dex_b": "Curve",
        "spread_bps": 42.5
    })
    
    # Example: Publish an executable transaction
    integration.publish_executable_tx({
        "chain": "Polygon",
        "token_pair": "USDC/USDT",
        "strategy": "Flash Arbitrage",
        "profit_usd": 15.50,
        "gas_cost": 2.30,
        "net_profit": 13.20,
        "executable": True,
        "dex_a": "Uniswap V3",
        "dex_b": "Curve",
        "spread_bps": 42.5
    })
    
    # Example: Publish execution result
    integration.publish_execution_result({
        "id": "tx_123456789",
        "chain": "Polygon",
        "token_pair": "USDC/USDT",
        "strategy": "Flash Arbitrage",
        "profit_usd": 15.50,
        "gas_cost": 2.30,
        "status": "SUCCESS",
        "tx_hash": "0xabc123def456...",
        "gas_used": 320000,
        "actual_profit": 13.15
    })
    
    # Example: Update metrics
    integration.update_metrics({
        "status": "OPERATIONAL",
        "uptime": 3600,
        "total_scans": 15000,
        "opportunities_found": 250,
        "txs_executed": 42,
        "total_profit": 525.30,
        "total_gas": 95.20,
        "net_profit": 430.10,
        "success_rate": 85.7,
        "avg_profit_per_tx": 12.51,
        "current_gas_price": 45.2
    })
    
    # Example: Listen for control messages
    def handle_control(action):
        print(f"Received control action: {action}")
        if action == "pause_scanning":
            print("Pausing scanning...")
            # Implement pause logic
        elif action == "resume_scanning":
            print("Resuming scanning...")
            # Implement resume logic
        elif action == "emergency_stop":
            print("EMERGENCY STOP!")
            # Implement emergency stop logic
    
    # This will block and listen for controls
    # integration.listen_for_controls(handle_control)


if __name__ == "__main__":
    print("TITAN Dashboard Integration Module")
    print("===================================\n")
    
    if len(sys.argv) > 1 and sys.argv[1] == "example":
        print("Running example usage...\n")
        example_usage()
        print("\n✓ Example completed")
    else:
        print("This module is designed to be imported and used within TITAN system.")
        print("\nUsage:")
        print("  from dashboard_integration import DashboardIntegration")
        print("  integration = DashboardIntegration()")
        print("  integration.publish_market_opportunity({...})")
        print("\nRun example:")
        print("  python3 dashboard_integration.py example")
