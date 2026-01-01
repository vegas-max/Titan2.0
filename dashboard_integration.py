#!/usr/bin/env python3
"""
TITAN Dashboard Integration Module
===================================

Connects the TITAN system (brain.py and bot.js) to the interactive dashboard
by publishing real-time data to Redis for dashboard consumption.

This module acts as a bridge between TITAN's operations and the dashboard server.
"""

import os
import sys
import json
import time
import asyncio
from datetime import datetime
from pathlib import Path

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("WARNING: redis not installed. Install with: pip install redis")
    sys.exit(1)

from dotenv import load_dotenv
load_dotenv()


class DashboardIntegration:
    """
    Integration layer between TITAN system and dashboard.
    Monitors TITAN operations and publishes to Redis for dashboard display.
    """
    
    def __init__(self):
        self.redis_client = None
        self.running = True
        
        # Connect to Redis
        self._connect_redis()
    
    def _connect_redis(self):
        """Connect to Redis"""
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            print("✓ Connected to Redis")
        except Exception as e:
            print(f"ERROR: Failed to connect to Redis: {e}")
            print("Make sure Redis is running: redis-server")
            sys.exit(1)
    
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
            
            # Publish to dashboard channel
            self.redis_client.publish(
                'dashboard:market_opportunity',
                json.dumps(opportunity)
            )
            
            # Store latest
            self.redis_client.setex(
                f"dashboard:opp:{opportunity['id']}",
                300,  # 5 minute TTL
                json.dumps(opportunity)
            )
            
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
            
            # Publish to dashboard channel
            self.redis_client.publish(
                'dashboard:executable_tx',
                json.dumps(tx)
            )
            
            # Add to executable queue
            self.redis_client.lpush(
                'dashboard:executable_queue',
                json.dumps(tx)
            )
            
            # Trim queue to last 50
            self.redis_client.ltrim('dashboard:executable_queue', 0, 49)
            
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
            
            # Publish to dashboard channel
            self.redis_client.publish(
                'dashboard:execution_result',
                json.dumps(result)
            )
            
            # Add to execution history
            self.redis_client.lpush(
                'dashboard:execution_history',
                json.dumps(result)
            )
            
            # Trim history to last 100
            self.redis_client.ltrim('dashboard:execution_history', 0, 99)
            
            # Remove from executable queue if present
            queue = self.redis_client.lrange('dashboard:executable_queue', 0, -1)
            for item in queue:
                tx = json.loads(item)
                if tx.get('id') == result.get('id'):
                    self.redis_client.lrem('dashboard:executable_queue', 1, item)
                    break
            
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
            # Publish metrics update
            self.redis_client.publish(
                'dashboard:metrics_update',
                json.dumps(metrics)
            )
            
            # Store current metrics
            self.redis_client.set(
                'dashboard:current_metrics',
                json.dumps(metrics)
            )
            
        except Exception as e:
            print(f"Error updating metrics: {e}")
    
    def listen_for_controls(self, callback):
        """
        Listen for control messages from dashboard
        
        Args:
            callback: Function to call with control action
                      callback(action: str) where action is one of:
                      - "pause_scanning"
                      - "resume_scanning"
                      - "emergency_stop"
        """
        try:
            pubsub = self.redis_client.pubsub()
            pubsub.subscribe('system_control')
            
            print("✓ Listening for dashboard control messages...")
            
            for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        action = data.get('action')
                        if action:
                            callback(action)
                    except Exception as e:
                        print(f"Error processing control message: {e}")
                        
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
