"""
WebSocket Manager for Real-Time DEX Data
Manages WebSocket connections to DEX subgraphs and pool data streaming
"""

import asyncio
import json
import logging
import os
from typing import Dict, Callable, List, Any
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger("WebSocketManager")

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    logger.warning("⚠️  websockets not available. Install with: pip install websockets")
class WebSocketManager:
    """
    Manages WebSocket connections to multiple DEX endpoints for real-time data
    """
    
    def __init__(self, config: Dict):
        """
        Initialize WebSocket manager
        
        Args:
            config: Configuration dictionary with dex_endpoints
        """
        self.config = config
        self.connections = {}
        self.callbacks = defaultdict(list)
        self.running = False
        self.reconnect_delay = 5  # seconds
        self.max_reconnect_attempts = 10
        
        # Track connection health
        self.connection_health = {}
        self.last_message_time = {}
        
    async def connect(self, dex_name: str, chain: str):
        """
        Connect to a DEX WebSocket endpoint
        
        Args:
            dex_name: Name of DEX (e.g., 'uniswap_v3', 'sushiswap', 'quickswap')
            chain: Chain name (e.g., 'polygon', 'ethereum')
        """
        if not WEBSOCKETS_AVAILABLE:
            logger.error("websockets library not available")
            return False
            
        try:
            # Get WebSocket URL from config
            ws_url = self.config.get('dex_endpoints', {}).get(dex_name, {}).get(chain, {}).get('ws')
            
            if not ws_url:
                logger.warning(f"No WebSocket URL configured for {dex_name} on {chain}")
                return False
            
            logger.info(f"🔌 Connecting to {dex_name} on {chain}: {ws_url}")
            
            connection_key = f"{dex_name}:{chain}"
            
            # Connect to WebSocket
            websocket = await websockets.connect(ws_url)
            self.connections[connection_key] = websocket
            self.connection_health[connection_key] = "connected"
            self.last_message_time[connection_key] = datetime.now()
            
            logger.info(f"✅ Connected to {dex_name} on {chain}")
            
            # Start listening for messages
            asyncio.create_task(self._listen(connection_key, websocket))
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to {dex_name} on {chain}: {e}")
            return False
    
    async def _listen(self, connection_key: str, websocket):
        """
        Listen for messages on a WebSocket connection
        
        Args:
            connection_key: Unique key for this connection
            websocket: WebSocket connection
        """
        reconnect_attempts = 0
        
        while self.running and reconnect_attempts < self.max_reconnect_attempts:
            try:
                async for message in websocket:
                    self.last_message_time[connection_key] = datetime.now()
                    
                    try:
                        data = json.loads(message)
                        
                        # Call registered callbacks
                        for callback in self.callbacks.get(connection_key, []):
                            try:
                                callback(data)
                            except Exception as e:
                                logger.error(f"Error in callback for {connection_key}: {e}")
                    
                    except json.JSONDecodeError as e:
                        logger.warning(f"Invalid JSON from {connection_key}: {e}")
                        
            except websockets.exceptions.ConnectionClosed:
                logger.warning(f"Connection closed for {connection_key}, attempting to reconnect...")
                self.connection_health[connection_key] = "reconnecting"
                
                # Wait before reconnecting
                await asyncio.sleep(self.reconnect_delay)
                reconnect_attempts += 1
                
                # Try to reconnect
                dex_name, chain = connection_key.split(':')
                if await self.connect(dex_name, chain):
                    reconnect_attempts = 0  # Reset counter on successful reconnect
                    
            except Exception as e:
                logger.error(f"Error listening to {connection_key}: {e}")
                await asyncio.sleep(self.reconnect_delay)
                reconnect_attempts += 1
        
        if reconnect_attempts >= self.max_reconnect_attempts:
            logger.error(f"Max reconnection attempts reached for {connection_key}")
            self.connection_health[connection_key] = "failed"
    
    def subscribe_pool_updates(self, connection_key: str, pool_addresses: List[str]):
        """
        Subscribe to updates for specific pools
        
        Args:
            connection_key: Connection identifier (dex:chain)
            pool_addresses: List of pool addresses to monitor
        """
        websocket = self.connections.get(connection_key)
        if not websocket:
            logger.error(f"No connection found for {connection_key}")
            return
        
        # Subscribe to pool updates (GraphQL subscription)
        subscription = {
            "id": "1",
            "type": "start",
            "payload": {
                "query": """
                    subscription {
                        pools(where: {id_in: $pool_ids}) {
                            id
                            token0 { symbol decimals }
                            token1 { symbol decimals }
                            reserve0
                            reserve1
                            reserveUSD
                            volumeUSD
                            txCount
                        }
                    }
                """,
                "variables": {
                    "pool_ids": pool_addresses
                }
            }
        }
        
        try:
            asyncio.create_task(websocket.send(json.dumps(subscription)))
            logger.info(f"📊 Subscribed to {len(pool_addresses)} pools on {connection_key}")
        except Exception as e:
            logger.error(f"Failed to subscribe to pools on {connection_key}: {e}")
    
    def register_callback(self, connection_key: str, callback: Callable[[Dict], None]):
        """
        Register a callback for messages from a specific connection
        
        Args:
            connection_key: Connection identifier (dex:chain)
            callback: Function to call with message data
        """
        self.callbacks[connection_key].append(callback)
        logger.info(f"Registered callback for {connection_key}")
    
    async def start(self):
        """Start the WebSocket manager"""
        self.running = True
        logger.info("🚀 WebSocket Manager started")
    
    async def stop(self):
        """Stop the WebSocket manager and close all connections"""
        self.running = False
        
        for connection_key, websocket in self.connections.items():
            try:
                await websocket.close()
                logger.info(f"Closed connection to {connection_key}")
            except Exception as e:
                logger.error(f"Error closing connection to {connection_key}: {e}")
        
        self.connections.clear()
        logger.info("🛑 WebSocket Manager stopped")
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get status of all connections
        
        Returns:
            Dictionary with connection health information
        """
        status = {}
        for connection_key, health in self.connection_health.items():
            last_msg = self.last_message_time.get(connection_key)
            status[connection_key] = {
                'health': health,
                'last_message': last_msg.isoformat() if last_msg else None,
                'seconds_since_last_message': (datetime.now() - last_msg).total_seconds() if last_msg else None
            }
        return status
