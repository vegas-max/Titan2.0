#!/usr/bin/env python3
"""
Optimized Aggregator Manager for Titan2.0
Improves DEX aggregator quote fetching with:
- Smart aggregator pre-filtering by chain
- Request deduplication
- Optimized caching with normalized keys
- Batch quote fetching where supported
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from offchain.core.unified_price_fetcher import (
    get_price_fetcher,
    DataSource
)

logger = logging.getLogger(__name__)


class Aggregator(Enum):
    """Supported DEX aggregators"""
    ONEINCH = "1inch"
    ZEROX = "0x"
    COWSWAP = "cowswap"
    OPENOCEAN = "openocean"
    KYBERSWAP = "kyberswap"
    RANGO = "rango"
    JUPITER = "jupiter"
    LIFI = "lifi"


@dataclass
class AggregatorConfig:
    """Aggregator configuration"""
    name: str
    supported_chains: List[int]
    min_trade_size_usd: float = 0
    max_trade_size_usd: float = float('inf')
    supports_cross_chain: bool = False
    api_endpoint: str = ""


@dataclass
class Quote:
    """DEX quote data structure"""
    aggregator: str
    from_token: str
    to_token: str
    from_amount: str
    to_amount: str
    gas_estimate: int
    price_impact: float
    route: List[str]
    chain_id: int
    timestamp: float
    
    def get_rate(self) -> float:
        """Calculate exchange rate"""
        try:
            return float(self.to_amount) / float(self.from_amount)
        except (ValueError, ZeroDivisionError):
            return 0.0


class OptimizedAggregatorManager:
    """
    Optimized aggregator manager with:
    - Chain-aware aggregator filtering
    - Parallel quote fetching
    - Request deduplication
    - Intelligent caching
    """
    
    def __init__(self):
        self.fetcher = get_price_fetcher()
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Aggregator configurations
        self.aggregators: Dict[Aggregator, AggregatorConfig] = {
            Aggregator.ONEINCH: AggregatorConfig(
                name="1inch",
                supported_chains=[1, 56, 137, 42161, 10, 8453, 43114],
                api_endpoint="https://api.1inch.dev/swap/v5.2"
            ),
            Aggregator.ZEROX: AggregatorConfig(
                name="0x",
                supported_chains=[1, 56, 137, 42161, 10, 8453],
                api_endpoint="https://api.0x.org"
            ),
            Aggregator.COWSWAP: AggregatorConfig(
                name="CoW Swap",
                supported_chains=[1, 100],  # Ethereum, Gnosis
                min_trade_size_usd=1000,  # MEV protection premium
                api_endpoint="https://api.cow.fi"
            ),
            Aggregator.OPENOCEAN: AggregatorConfig(
                name="OpenOcean",
                supported_chains=[1, 56, 137, 42161, 10, 8453, 43114, 250],
                api_endpoint="https://open-api.openocean.finance/v3"
            ),
            Aggregator.KYBERSWAP: AggregatorConfig(
                name="KyberSwap",
                supported_chains=[1, 56, 137, 42161, 10, 8453, 43114],
                api_endpoint="https://aggregator-api.kyberswap.com"
            ),
            Aggregator.JUPITER: AggregatorConfig(
                name="Jupiter",
                supported_chains=[101],  # Solana (custom chain ID representation)
                api_endpoint="https://quote-api.jup.ag/v6"
            ),
            Aggregator.RANGO: AggregatorConfig(
                name="Rango",
                supported_chains=list(range(1, 100)),  # 70+ chains
                supports_cross_chain=True,
                api_endpoint="https://api.rango.exchange"
            ),
            Aggregator.LIFI: AggregatorConfig(
                name="LiFi",
                supported_chains=list(range(1, 100)),  # Many chains
                supports_cross_chain=True,
                api_endpoint="https://li.quest/v1"
            )
        }
        
        logger.info("🔧 Optimized Aggregator Manager initialized")
    
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def get_compatible_aggregators(
        self,
        chain_id: int,
        trade_size_usd: float = 0,
        is_cross_chain: bool = False
    ) -> List[Aggregator]:
        """
        Get list of compatible aggregators for a trade
        
        Args:
            chain_id: Chain ID
            trade_size_usd: Trade size in USD
            is_cross_chain: Whether this is a cross-chain trade
        
        Returns:
            List of compatible aggregators
        """
        compatible = []
        
        for agg, config in self.aggregators.items():
            # Check chain support
            if chain_id not in config.supported_chains:
                continue
            
            # Check cross-chain requirement
            if is_cross_chain and not config.supports_cross_chain:
                continue
            
            # Check trade size limits
            if trade_size_usd < config.min_trade_size_usd:
                continue
            if trade_size_usd > config.max_trade_size_usd:
                continue
            
            compatible.append(agg)
        
        logger.info(
            f"🔍 Found {len(compatible)} compatible aggregators for "
            f"chain {chain_id}, size ${trade_size_usd:.2f}"
        )
        
        return compatible
    
    async def get_best_quote(
        self,
        from_token: str,
        to_token: str,
        amount: str,
        chain_id: int,
        trade_size_usd: float = 0,
        is_cross_chain: bool = False,
        force_refresh: bool = False
    ) -> Optional[Quote]:
        """
        Get best quote from compatible aggregators
        
        Args:
            from_token: Source token address
            to_token: Destination token address
            amount: Amount to swap (in wei/smallest unit)
            chain_id: Chain ID
            trade_size_usd: Trade size in USD for filtering
            is_cross_chain: Whether this is a cross-chain trade
            force_refresh: Skip cache
        
        Returns:
            Best Quote or None
        """
        await self._ensure_session()
        
        # Get compatible aggregators
        compatible_aggs = self.get_compatible_aggregators(
            chain_id=chain_id,
            trade_size_usd=trade_size_usd,
            is_cross_chain=is_cross_chain
        )
        
        if not compatible_aggs:
            logger.warning(f"⚠️ No compatible aggregators for chain {chain_id}")
            return None
        
        # Define fetch function for parallel queries
        async def fetch_quotes_parallel():
            # Create provider list for parallel fetching
            providers = [
                (agg.value, lambda a=agg: self._fetch_quote(
                    aggregator=a,
                    from_token=from_token,
                    to_token=to_token,
                    amount=amount,
                    chain_id=chain_id
                ))
                for agg in compatible_aggs
            ]
            
            # Fetch all quotes in parallel
            tasks = []
            for agg_name, fetch_func in providers:
                task = asyncio.create_task(fetch_func())
                tasks.append((agg_name, task))
            
            # Collect all successful quotes
            quotes = []
            for agg_name, task in tasks:
                try:
                    quote = await task
                    if quote:
                        quotes.append(quote)
                except Exception as e:
                    logger.debug(f"Aggregator {agg_name} failed: {e}")
            
            # Return best quote (highest output amount)
            if not quotes:
                return None
            
            best_quote = max(quotes, key=lambda q: float(q.to_amount))
            logger.info(
                f"✅ Best quote from {best_quote.aggregator}: "
                f"{best_quote.from_amount} → {best_quote.to_amount} "
                f"(rate: {best_quote.get_rate():.6f})"
            )
            
            return best_quote
        
        # Use unified fetcher with caching
        quote, from_cache = await self.fetcher.fetch_with_cache(
            source_type=DataSource.DEX_QUOTE,
            params={
                "from_token": from_token.lower(),
                "to_token": to_token.lower(),
                "amount": amount,
                "chain_id": chain_id
            },
            fetch_func=fetch_quotes_parallel,
            force_refresh=force_refresh
        )
        
        cache_indicator = "📦" if from_cache else "🌐"
        if quote:
            logger.info(f"{cache_indicator} Quote retrieved: {quote.aggregator}")
        
        return quote
    
    async def _fetch_quote(
        self,
        aggregator: Aggregator,
        from_token: str,
        to_token: str,
        amount: str,
        chain_id: int
    ) -> Optional[Quote]:
        """
        Fetch quote from specific aggregator
        
        Args:
            aggregator: Aggregator to query
            from_token: Source token
            to_token: Destination token
            amount: Amount in smallest unit
            chain_id: Chain ID
        
        Returns:
            Quote or None
        """
        # Mock implementation - in production, call actual aggregator APIs
        # This would be implemented per aggregator with their specific API formats
        
        logger.debug(f"Fetching quote from {aggregator.value}")
        
        # Simulate API call
        await asyncio.sleep(0.1)
        
        # Mock quote data
        import time
        return Quote(
            aggregator=aggregator.value,
            from_token=from_token,
            to_token=to_token,
            from_amount=amount,
            to_amount=str(int(amount) * 0.99),  # Mock 1% slippage
            gas_estimate=150000,
            price_impact=0.01,
            route=[from_token, to_token],
            chain_id=chain_id,
            timestamp=time.time()
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get manager statistics"""
        return self.fetcher.get_stats()


# Singleton instance
_aggregator_manager: Optional[OptimizedAggregatorManager] = None


async def get_aggregator_manager() -> OptimizedAggregatorManager:
    """Get or create singleton aggregator manager"""
    global _aggregator_manager
    if _aggregator_manager is None:
        _aggregator_manager = OptimizedAggregatorManager()
    return _aggregator_manager


# Example usage / test
if __name__ == "__main__":
    import asyncio
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    async def test_aggregator_manager():
        manager = await get_aggregator_manager()
        
        print("\n=== Test 1: Get Compatible Aggregators ===")
        aggs = manager.get_compatible_aggregators(
            chain_id=137,  # Polygon
            trade_size_usd=500
        )
        print(f"Compatible aggregators: {[a.value for a in aggs]}")
        
        print("\n=== Test 2: Get Best Quote ===")
        quote = await manager.get_best_quote(
            from_token="0x0000000000000000000000000000000000000001",
            to_token="0x0000000000000000000000000000000000000002",
            amount="1000000000000000000",
            chain_id=137,
            trade_size_usd=100
        )
        
        if quote:
            print(f"Aggregator: {quote.aggregator}")
            print(f"From: {quote.from_amount}")
            print(f"To: {quote.to_amount}")
            print(f"Rate: {quote.get_rate()}")
        
        print("\n=== Test 3: Cached Quote ===")
        quote2 = await manager.get_best_quote(
            from_token="0x0000000000000000000000000000000000000001",
            to_token="0x0000000000000000000000000000000000000002",
            amount="1000000000000000000",
            chain_id=137,
            trade_size_usd=100
        )
        
        print("\n=== Test 4: Statistics ===")
        stats = manager.get_stats()
        print(f"Cache hit rate: {stats['cache']['hit_rate']}")
        
        await manager.close()
    
    asyncio.run(test_aggregator_manager())
