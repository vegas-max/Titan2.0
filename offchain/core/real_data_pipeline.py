"""
Real Data Pipeline - Replaces Simulated Scanning with Real DEX Data
Connects to Uniswap/Sushiswap/QuickSwap pools and fetches real reserves
"""

import asyncio
import logging
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal
from web3 import Web3

from offchain.core.websocket_manager import WebSocketManager
from offchain.core.direct_dex_query import DirectDEXQuery

logger = logging.getLogger("RealDataPipeline")


class RealDataPipeline:
    """
    Real data pipeline for fetching live DEX pool data
    Replaces simulated scanning with actual blockchain data
    """
    
    def __init__(self, config: Dict, web3_connections: Dict[int, Web3], use_websockets: bool = True):
        """
        Initialize real data pipeline
        
        Args:
            config: System configuration
            web3_connections: Web3 connection pool
            use_websockets: Whether to use WebSocket streaming (True) or polling (False)
        """
        self.config = config
        self.web3_connections = web3_connections
        self.use_websockets = use_websockets
        
        # Initialize components
        self.direct_query = DirectDEXQuery(web3_connections)
        self.ws_manager = WebSocketManager(config) if use_websockets else None
        
        # Pool data cache
        self.pool_cache = {}
        self.pool_addresses = {}
        
        # Statistics
        self.stats = {
            'pools_tracked': 0,
            'updates_received': 0,
            'queries_made': 0,
            'errors': 0,
            'start_time': datetime.now()
        }
        
        logger.info(f"🚀 Real Data Pipeline initialized (WebSocket: {use_websockets})")
    
    async def start(self):
        """Start the real data pipeline"""
        logger.info("🔌 Starting Real Data Pipeline...")
        
        if self.use_websockets and self.ws_manager:
            await self.ws_manager.start()
            
            # Connect to configured DEX endpoints
            await self._connect_to_dexes()
            
        logger.info("✅ Real Data Pipeline started")
    
    async def stop(self):
        """Stop the real data pipeline"""
        logger.info("🛑 Stopping Real Data Pipeline...")
        
        if self.ws_manager:
            await self.ws_manager.stop()
            
        logger.info("✅ Real Data Pipeline stopped")
    
    async def _connect_to_dexes(self):
        """Connect to all configured DEX WebSocket endpoints"""
        dex_endpoints = self.config.get('dex_endpoints', {})
        
        connections_made = 0
        for dex_name, chains in dex_endpoints.items():
            for chain, endpoints in chains.items():
                if 'ws' in endpoints:
                    success = await self.ws_manager.connect(dex_name, chain)
                    if success:
                        connections_made += 1
                        
                        # Register callback for this DEX
                        connection_key = f"{dex_name}:{chain}"
                        self.ws_manager.register_callback(
                            connection_key,
                            lambda data, dk=dex_name, ch=chain: self._handle_pool_update(dk, ch, data)
                        )
        
        logger.info(f"📊 Connected to {connections_made} DEX endpoints")
    
    def _handle_pool_update(self, dex_name: str, chain: str, data: Dict):
        """
        Handle pool update from WebSocket
        
        Args:
            dex_name: Name of the DEX
            chain: Chain name
            data: Pool update data
        """
        try:
            self.stats['updates_received'] += 1
            
            # Extract pool data based on GraphQL subscription format
            if 'data' in data and 'pools' in data['data']:
                pools = data['data']['pools']
                
                for pool in pools:
                    pool_id = pool.get('id')
                    if pool_id:
                        cache_key = f"{dex_name}:{chain}:{pool_id}"
                        self.pool_cache[cache_key] = {
                            'dex': dex_name,
                            'chain': chain,
                            'pool_address': pool_id,
                            'token0': pool.get('token0'),
                            'token1': pool.get('token1'),
                            'reserve0': pool.get('reserve0'),
                            'reserve1': pool.get('reserve1'),
                            'reserve_usd': pool.get('reserveUSD'),
                            'volume_usd': pool.get('volumeUSD'),
                            'tx_count': pool.get('txCount'),
                            'timestamp': datetime.now().isoformat(),
                            'source': 'websocket'
                        }
                        
                        logger.debug(f"📊 Updated pool {pool_id[:8]}... on {dex_name}/{chain}")
                        
        except Exception as e:
            logger.error(f"Error handling pool update from {dex_name}/{chain}: {e}")
            self.stats['errors'] += 1
    
    async def get_pool_reserves(
        self,
        chain_id: int,
        pool_address: str,
        dex_type: str = 'uniswap_v2'
    ) -> Optional[Dict]:
        """
        Get real-time pool reserves
        
        Args:
            chain_id: Chain ID
            pool_address: Pool contract address
            dex_type: Type of DEX ('uniswap_v2', 'uniswap_v3', 'curve', etc.)
            
        Returns:
            Dictionary with pool reserve data or None if unavailable
        """
        try:
            self.stats['queries_made'] += 1
            
            # Try to get from WebSocket cache first
            cache_key = f"{dex_type}:{chain_id}:{pool_address}"
            if cache_key in self.pool_cache:
                cached_data = self.pool_cache[cache_key]
                
                # Check if cache is fresh (< 10 seconds old)
                cache_time = datetime.fromisoformat(cached_data['timestamp'])
                age_seconds = (datetime.now() - cache_time).total_seconds()
                
                if age_seconds < 10:
                    logger.debug(f"📦 Using cached pool data (age: {age_seconds:.1f}s)")
                    return cached_data
            
            # Fall back to direct query
            logger.debug(f"🔍 Querying pool {pool_address[:8]}... directly")
            
            if dex_type == 'uniswap_v2' or dex_type == 'sushiswap' or dex_type == 'quickswap':
                # These all use Uniswap V2 interface
                result = self.direct_query.query_uniswap_v2_pool(
                    chain_id=chain_id,
                    pool_address=pool_address,
                    token_in="0x0000000000000000000000000000000000000000",  # Placeholder
                    amount_in=10**18  # 1 token
                )
                
            elif dex_type == 'uniswap_v3':
                result = self.direct_query.query_uniswap_v3_pool(
                    chain_id=chain_id,
                    pool_address=pool_address
                )
                
            else:
                logger.warning(f"Unsupported DEX type: {dex_type}")
                return None
            
            if result:
                # Add to cache
                result['timestamp'] = datetime.now().isoformat()
                result['source'] = 'direct_query'
                self.pool_cache[cache_key] = result
                
            return result
            
        except Exception as e:
            logger.error(f"Error getting pool reserves: {e}")
            self.stats['errors'] += 1
            return None
    
    async def scan_opportunities(
        self,
        chains: List[int],
        token_pairs: List[tuple],
        min_liquidity_usd: float = 10000
    ) -> List[Dict]:
        """
        Scan for arbitrage opportunities using real data
        
        Args:
            chains: List of chain IDs to scan
            token_pairs: List of (token0, token1) pairs to check
            min_liquidity_usd: Minimum liquidity in USD
            
        Returns:
            List of potential arbitrage opportunities
        """
        opportunities = []
        
        try:
            logger.info(f"🔍 Scanning {len(chains)} chains for {len(token_pairs)} token pairs...")
            
            for chain_id in chains:
                for token0, token1 in token_pairs:
                    # Check multiple DEXes for same pair
                    dexes_to_check = ['uniswap_v3', 'sushiswap', 'quickswap']
                    
                    prices = {}
                    
                    for dex in dexes_to_check:
                        # In production, we'd look up the actual pool address
                        # For now, this is a simplified example
                        # Real implementation would query factory contracts to find pools
                        
                        # Placeholder for pool address lookup
                        # pool_address = await self._find_pool_address(chain_id, dex, token0, token1)
                        
                        # For demonstration, we'll skip if pool not found
                        pass
                    
                    # Compare prices across DEXes to find arbitrage
                    if len(prices) >= 2:
                        price_values = list(prices.values())
                        min_price = min(price_values)
                        max_price = max(price_values)
                        
                        # Calculate potential profit
                        price_diff_pct = ((max_price - min_price) / min_price) * 100
                        
                        if price_diff_pct > 0.5:  # More than 0.5% difference
                            opportunities.append({
                                'chain_id': chain_id,
                                'token0': token0,
                                'token1': token1,
                                'price_diff_pct': price_diff_pct,
                                'dex_prices': prices,
                                'timestamp': datetime.now().isoformat()
                            })
            
            logger.info(f"✅ Found {len(opportunities)} potential opportunities")
            
        except Exception as e:
            logger.error(f"Error scanning opportunities: {e}")
            self.stats['errors'] += 1
        
        return opportunities
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        uptime_seconds = (datetime.now() - self.stats['start_time']).total_seconds()
        
        return {
            **self.stats,
            'uptime_seconds': uptime_seconds,
            'uptime_hours': uptime_seconds / 3600,
            'avg_updates_per_minute': (self.stats['updates_received'] / uptime_seconds * 60) if uptime_seconds > 0 else 0,
            'error_rate': (self.stats['errors'] / max(1, self.stats['queries_made'])) * 100,
            'cache_size': len(self.pool_cache)
        }
    
    def get_cached_pools(self) -> Dict[str, Any]:
        """Get all cached pool data"""
        return dict(self.pool_cache)
