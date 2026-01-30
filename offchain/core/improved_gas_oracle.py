#!/usr/bin/env python3
"""
Improved Gas Price Oracle for Titan2.0
Fetches gas prices from multiple providers in parallel with intelligent fallback
Replaces the inefficient sequential retry mechanism
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Optional, List, Any
from dataclasses import dataclass
from datetime import datetime

from offchain.core.unified_price_fetcher import (
    get_price_fetcher,
    DataSource
)

logger = logging.getLogger(__name__)


@dataclass
class GasPrice:
    """Gas price data structure"""
    safe: float
    propose: float
    fast: float
    source: str
    timestamp: datetime
    chain_id: int
    
    def is_valid(self) -> bool:
        """Check if gas price data is valid (at least one value > 0)"""
        # At least one gas price should be valid (not all zeros)
        return self.safe > 0 or self.propose > 0 or self.fast > 0


class ImprovedGasOracle:
    """
    Improved gas price oracle with:
    - Parallel provider queries (no sequential retries)
    - Intelligent provider fallback
    - Automatic caching
    - Provider health tracking
    """
    
    def __init__(self, timeout: float = 3.0):
        self.timeout = timeout
        self.fetcher = get_price_fetcher()
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Provider configurations for different chains
        self.providers = {
            137: [  # Polygon
                ("Owlracle", self._fetch_owlracle),
                ("Polygonscan", self._fetch_polygonscan),
                ("BlockNative", self._fetch_blocknative),
            ],
            1: [  # Ethereum
                ("EthGasStation", self._fetch_ethgasstation),
                ("Etherscan", self._fetch_etherscan),
                ("BlockNative", self._fetch_blocknative),
            ],
            56: [  # BSC
                ("BscScan", self._fetch_bscscan),
            ],
            42161: [  # Arbitrum
                ("Arbiscan", self._fetch_arbiscan),
            ]
        }
        
        logger.info("🔧 Improved Gas Oracle initialized")
    
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_gas_prices(
        self,
        chain_id: int,
        force_refresh: bool = False
    ) -> Optional[GasPrice]:
        """
        Get gas prices for a chain with parallel provider queries
        
        Args:
            chain_id: Chain ID
            force_refresh: Skip cache and fetch fresh data
        
        Returns:
            GasPrice object or None if all providers fail
        """
        await self._ensure_session()
        
        # Check if we have providers for this chain
        if chain_id not in self.providers:
            logger.warning(f"⚠️ No gas price providers configured for chain {chain_id}")
            return None
        
        # Define fetch function that queries all providers in parallel
        async def fetch_gas_price_parallel():
            providers = self.providers[chain_id]
            
            # Fetch from all providers in parallel with timeout
            result, provider_name = await self.fetcher.fetch_parallel_with_fallback(
                providers=providers,
                timeout=self.timeout
            )
            
            if result is None:
                logger.error(f"❌ All gas price providers failed for chain {chain_id}")
                return None
            
            # Add metadata
            result["source"] = provider_name
            result["timestamp"] = datetime.now()
            result["chain_id"] = chain_id
            
            return result
        
        # Use unified fetcher with caching
        gas_data, from_cache = await self.fetcher.fetch_with_cache(
            source_type=DataSource.GAS_PRICE,
            params={"chain_id": chain_id},
            fetch_func=fetch_gas_price_parallel,
            force_refresh=force_refresh
        )
        
        if gas_data is None:
            return None
        
        # Convert to GasPrice object
        gas_price = GasPrice(
            safe=gas_data.get("safe", 0.0),
            propose=gas_data.get("propose", 0.0),
            fast=gas_data.get("fast", 0.0),
            source=gas_data.get("source", "unknown"),
            timestamp=gas_data.get("timestamp", datetime.now()),
            chain_id=gas_data.get("chain_id", chain_id)
        )
        
        # Validate gas prices
        if not gas_price.is_valid():
            logger.warning(f"⚠️ Invalid gas prices (all zeros) for chain {chain_id}")
            return None
        
        cache_indicator = "📦" if from_cache else "🌐"
        logger.info(
            f"{cache_indicator} Gas prices for chain {chain_id}: "
            f"Safe={gas_price.safe:.2f}, Propose={gas_price.propose:.2f}, "
            f"Fast={gas_price.fast:.2f} (source: {gas_price.source})"
        )
        
        return gas_price
    
    # Provider-specific fetch methods
    
    async def _fetch_owlracle(self) -> Optional[Dict[str, float]]:
        """Fetch from Owlracle API"""
        try:
            url = "https://api.owlracle.info/v4/poly/gas"
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.debug(f"Owlracle returned status {response.status}")
                    return None
                
                data = await response.json()
                
                # Owlracle response format
                speeds = data.get("speeds", [])
                if not speeds or len(speeds) < 3:
                    logger.debug("Owlracle returned incomplete data")
                    return None
                
                return {
                    "safe": float(speeds[0].get("gasPrice", 0)),
                    "propose": float(speeds[1].get("gasPrice", 0)),
                    "fast": float(speeds[2].get("gasPrice", 0))
                }
        except Exception as e:
            logger.debug(f"Owlracle fetch error: {e}")
            return None
    
    async def _fetch_polygonscan(self) -> Optional[Dict[str, float]]:
        """Fetch from Polygonscan API"""
        try:
            # Note: Requires API key from environment
            import os
            api_key = os.getenv("POLYGONSCAN_API_KEY", "")
            
            if not api_key:
                logger.debug("Polygonscan API key not configured")
                return None
            
            url = f"https://api.polygonscan.com/api?module=gastracker&action=gasoracle&apikey={api_key}"
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.debug(f"Polygonscan returned status {response.status}")
                    return None
                
                data = await response.json()
                
                if data.get("status") != "1":
                    logger.debug(f"Polygonscan API error: {data.get('message')}")
                    return None
                
                result = data.get("result", {})
                
                return {
                    "safe": float(result.get("SafeGasPrice", 0)),
                    "propose": float(result.get("ProposeGasPrice", 0)),
                    "fast": float(result.get("FastGasPrice", 0))
                }
        except Exception as e:
            logger.debug(f"Polygonscan fetch error: {e}")
            return None
    
    async def _fetch_blocknative(self) -> Optional[Dict[str, float]]:
        """Fetch from BlockNative Gas Platform"""
        try:
            url = "https://api.blocknative.com/gasprices/blockprices"
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.debug(f"BlockNative returned status {response.status}")
                    return None
                
                data = await response.json()
                
                block_prices = data.get("blockPrices", [])
                if not block_prices:
                    logger.debug("BlockNative returned no data")
                    return None
                
                prices = block_prices[0].get("estimatedPrices", [])
                if len(prices) < 3:
                    logger.debug("BlockNative returned incomplete data")
                    return None
                
                return {
                    "safe": float(prices[0].get("maxFeePerGas", 0)),
                    "propose": float(prices[1].get("maxFeePerGas", 0)),
                    "fast": float(prices[2].get("maxFeePerGas", 0))
                }
        except Exception as e:
            logger.debug(f"BlockNative fetch error: {e}")
            return None
    
    async def _fetch_ethgasstation(self) -> Optional[Dict[str, float]]:
        """Fetch from ETH Gas Station"""
        try:
            url = "https://ethgasstation.info/api/ethgasAPI.json"
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.debug(f"EthGasStation returned status {response.status}")
                    return None
                
                data = await response.json()
                
                return {
                    "safe": float(data.get("safeLow", 0)) / 10,
                    "propose": float(data.get("average", 0)) / 10,
                    "fast": float(data.get("fast", 0)) / 10
                }
        except Exception as e:
            logger.debug(f"EthGasStation fetch error: {e}")
            return None
    
    async def _fetch_etherscan(self) -> Optional[Dict[str, float]]:
        """Fetch from Etherscan API"""
        try:
            import os
            api_key = os.getenv("ETHERSCAN_API_KEY", "")
            
            if not api_key:
                logger.debug("Etherscan API key not configured")
                return None
            
            url = f"https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={api_key}"
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.debug(f"Etherscan returned status {response.status}")
                    return None
                
                data = await response.json()
                
                if data.get("status") != "1":
                    logger.debug(f"Etherscan API error: {data.get('message')}")
                    return None
                
                result = data.get("result", {})
                
                return {
                    "safe": float(result.get("SafeGasPrice", 0)),
                    "propose": float(result.get("ProposeGasPrice", 0)),
                    "fast": float(result.get("FastGasPrice", 0))
                }
        except Exception as e:
            logger.debug(f"Etherscan fetch error: {e}")
            return None
    
    async def _fetch_bscscan(self) -> Optional[Dict[str, float]]:
        """Fetch from BscScan API"""
        try:
            import os
            api_key = os.getenv("BSCSCAN_API_KEY", "")
            
            if not api_key:
                logger.debug("BscScan API key not configured")
                return None
            
            url = f"https://api.bscscan.com/api?module=gastracker&action=gasoracle&apikey={api_key}"
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.debug(f"BscScan returned status {response.status}")
                    return None
                
                data = await response.json()
                
                if data.get("status") != "1":
                    logger.debug(f"BscScan API error: {data.get('message')}")
                    return None
                
                result = data.get("result", {})
                
                return {
                    "safe": float(result.get("SafeGasPrice", 0)),
                    "propose": float(result.get("ProposeGasPrice", 0)),
                    "fast": float(result.get("FastGasPrice", 0))
                }
        except Exception as e:
            logger.debug(f"BscScan fetch error: {e}")
            return None
    
    async def _fetch_arbiscan(self) -> Optional[Dict[str, float]]:
        """Fetch from Arbiscan API"""
        try:
            import os
            api_key = os.getenv("ARBISCAN_API_KEY", "")
            
            if not api_key:
                logger.debug("Arbiscan API key not configured")
                return None
            
            url = f"https://api.arbiscan.io/api?module=gastracker&action=gasoracle&apikey={api_key}"
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.debug(f"Arbiscan returned status {response.status}")
                    return None
                
                data = await response.json()
                
                if data.get("status") != "1":
                    logger.debug(f"Arbiscan API error: {data.get('message')}")
                    return None
                
                result = data.get("result", {})
                
                return {
                    "safe": float(result.get("SafeGasPrice", 0)),
                    "propose": float(result.get("ProposeGasPrice", 0)),
                    "fast": float(result.get("FastGasPrice", 0))
                }
        except Exception as e:
            logger.debug(f"Arbiscan fetch error: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get oracle statistics"""
        return self.fetcher.get_stats()


# Singleton instance
_gas_oracle: Optional[ImprovedGasOracle] = None


async def get_gas_oracle() -> ImprovedGasOracle:
    """Get or create singleton gas oracle instance"""
    global _gas_oracle
    if _gas_oracle is None:
        _gas_oracle = ImprovedGasOracle()
    return _gas_oracle


# Example usage / test
if __name__ == "__main__":
    import asyncio
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    async def test_gas_oracle():
        oracle = await get_gas_oracle()
        
        print("\n=== Test 1: Fetch Polygon Gas Prices ===")
        gas_price = await oracle.get_gas_prices(137)
        if gas_price:
            print(f"Chain: {gas_price.chain_id}")
            print(f"Safe: {gas_price.safe} Gwei")
            print(f"Propose: {gas_price.propose} Gwei")
            print(f"Fast: {gas_price.fast} Gwei")
            print(f"Source: {gas_price.source}")
            print(f"Valid: {gas_price.is_valid()}")
        
        print("\n=== Test 2: Fetch Again (Should be cached) ===")
        gas_price2 = await oracle.get_gas_prices(137)
        if gas_price2:
            print(f"Source: {gas_price2.source}")
        
        print("\n=== Test 3: Statistics ===")
        stats = oracle.get_stats()
        print(f"Cache stats: {stats['cache']}")
        print(f"Provider stats: {stats.get('providers', {})}")
        
        await oracle.close()
    
    asyncio.run(test_gas_oracle())
