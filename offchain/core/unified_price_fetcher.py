#!/usr/bin/env python3
"""
Unified Price Fetcher for Titan2.0
Optimized price and gas data fetching with:
- Request deduplication (in-flight tracking)
- Intelligent parallel fetching
- Adaptive caching with LRU eviction
- Normalized cache keys
- Multi-provider fallback with parallel queries
"""

import asyncio
import time
import logging
import hashlib
import json
from typing import Dict, Any, Optional, List, Tuple, Callable
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class DataSource(Enum):
    """Data source types"""
    GAS_PRICE = "gas_price"
    DEX_QUOTE = "dex_quote"
    TOKEN_PRICE = "token_price"
    POOL_STATE = "pool_state"


@dataclass
class FetchRequest:
    """Normalized fetch request"""
    source_type: DataSource
    params: Dict[str, Any]
    timestamp: float
    
    def get_cache_key(self) -> str:
        """Generate normalized cache key"""
        # Sort params for consistent hashing
        sorted_params = dict(sorted(self.params.items()))
        param_str = json.dumps(sorted_params, sort_keys=True, separators=(',', ':'))
        key_hash = hashlib.sha256(param_str.encode()).hexdigest()[:16]
        return f"{self.source_type.value}:{key_hash}"


@dataclass
class CachedData:
    """Cached data with metadata"""
    data: Any
    timestamp: float
    ttl: int
    volatility: float = 1.0  # 1.0 = normal, >1.0 = high volatility (shorter TTL)
    
    def is_valid(self) -> bool:
        """Check if cache entry is still valid"""
        effective_ttl = self.ttl / self.volatility
        age = time.time() - self.timestamp
        return age < effective_ttl


class LRUCache:
    """LRU Cache with size limit and TTL support"""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.cache: OrderedDict[str, CachedData] = OrderedDict()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expired": 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache (LRU)"""
        if key not in self.cache:
            self.stats["misses"] += 1
            return None
        
        cached = self.cache[key]
        
        # Check if expired
        if not cached.is_valid():
            del self.cache[key]
            self.stats["expired"] += 1
            self.stats["misses"] += 1
            return None
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        self.stats["hits"] += 1
        return cached.data
    
    def set(self, key: str, data: Any, ttl: int = 60, volatility: float = 1.0):
        """Set value in cache with TTL"""
        # Evict oldest entry if at capacity
        if key not in self.cache and len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)  # Remove oldest (FIFO from front)
            self.stats["evictions"] += 1
        
        # Add/update entry
        self.cache[key] = CachedData(
            data=data,
            timestamp=time.time(),
            ttl=ttl,
            volatility=volatility
        )
        
        # Move to end if updating
        if key in self.cache:
            self.cache.move_to_end(key)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0
        
        return {
            **self.stats,
            "size": len(self.cache),
            "hit_rate": f"{hit_rate:.2f}%"
        }


class RequestDeduplicator:
    """Deduplicates concurrent identical requests"""
    
    def __init__(self):
        self.in_flight: Dict[str, asyncio.Future] = {}
        self.lock = asyncio.Lock()
        self.stats = {
            "deduplicated": 0,
            "unique_requests": 0
        }
    
    async def fetch_or_wait(
        self, 
        key: str, 
        fetch_func: Callable, 
        *args, 
        **kwargs
    ) -> Any:
        """
        Fetch data or wait for in-flight request
        
        Args:
            key: Request identifier
            fetch_func: Async function to call if not in-flight
            *args, **kwargs: Arguments for fetch_func
        
        Returns:
            Fetched data
        """
        async with self.lock:
            # Check if request is already in flight
            if key in self.in_flight:
                self.stats["deduplicated"] += 1
                logger.debug(f"Deduplicating request: {key}")
                # Wait for existing request
                return await self.in_flight[key]
            
            # Create new future for this request
            future = asyncio.create_task(self._execute_fetch(key, fetch_func, *args, **kwargs))
            self.in_flight[key] = future
            self.stats["unique_requests"] += 1
        
        try:
            result = await future
            return result
        finally:
            # Remove from in-flight when done
            async with self.lock:
                if key in self.in_flight:
                    del self.in_flight[key]
    
    async def _execute_fetch(self, key: str, fetch_func: Callable, *args, **kwargs) -> Any:
        """Execute the actual fetch"""
        try:
            return await fetch_func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Fetch error for {key}: {e}")
            raise


class UnifiedPriceFetcher:
    """
    Unified price fetching service with:
    - Request deduplication
    - LRU caching with adaptive TTLs
    - Parallel provider queries
    - Intelligent fallback mechanisms
    """
    
    def __init__(self, cache_size: int = 10000):
        self.cache = LRUCache(max_size=cache_size)
        self.deduplicator = RequestDeduplicator()
        self.provider_stats: Dict[str, Dict[str, Any]] = {}
        
        # Adaptive TTL settings (in seconds)
        self.default_ttls = {
            DataSource.GAS_PRICE: 30,      # Gas prices change frequently
            DataSource.DEX_QUOTE: 60,       # DEX quotes moderately stable
            DataSource.TOKEN_PRICE: 120,    # Token prices relatively stable
            DataSource.POOL_STATE: 12       # Pool state tied to blocks
        }
        
        logger.info("🚀 Unified Price Fetcher initialized")
    
    def _update_provider_stats(self, provider: str, success: bool, latency: float):
        """Update provider performance statistics"""
        if provider not in self.provider_stats:
            self.provider_stats[provider] = {
                "requests": 0,
                "successes": 0,
                "failures": 0,
                "avg_latency": 0,
                "last_success": None,
                "last_failure": None
            }
        
        stats = self.provider_stats[provider]
        stats["requests"] += 1
        
        if success:
            stats["successes"] += 1
            stats["last_success"] = datetime.now()
            # Update average latency (exponential moving average)
            alpha = 0.3
            stats["avg_latency"] = alpha * latency + (1 - alpha) * stats["avg_latency"]
        else:
            stats["failures"] += 1
            stats["last_failure"] = datetime.now()
    
    def _get_provider_priority(self, provider: str) -> float:
        """
        Calculate provider priority score (higher is better)
        Based on success rate and latency
        """
        if provider not in self.provider_stats:
            return 1.0  # Neutral priority for new providers
        
        stats = self.provider_stats[provider]
        if stats["requests"] == 0:
            return 1.0
        
        # Success rate (0-1)
        success_rate = stats["successes"] / stats["requests"]
        
        # Latency penalty (lower latency = higher score)
        latency_score = 1.0 / (1.0 + stats["avg_latency"] / 1000.0)  # Normalize by 1s
        
        # Recent failures penalty
        recency_penalty = 1.0
        if stats["last_failure"]:
            seconds_since_failure = (datetime.now() - stats["last_failure"]).total_seconds()
            if seconds_since_failure < 60:  # Last minute
                recency_penalty = 0.5
        
        return success_rate * latency_score * recency_penalty
    
    async def fetch_with_cache(
        self,
        source_type: DataSource,
        params: Dict[str, Any],
        fetch_func: Callable,
        ttl: Optional[int] = None,
        force_refresh: bool = False
    ) -> Tuple[Optional[Any], bool]:
        """
        Fetch data with caching and deduplication
        
        Args:
            source_type: Type of data being fetched
            params: Normalized parameters
            fetch_func: Async function to fetch data
            ttl: Cache TTL override
            force_refresh: Skip cache and fetch fresh data
        
        Returns:
            Tuple of (data, from_cache)
        """
        request = FetchRequest(
            source_type=source_type,
            params=params,
            timestamp=time.time()
        )
        cache_key = request.get_cache_key()
        
        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_data, True
        
        # Fetch with deduplication
        logger.debug(f"Cache miss: {cache_key}, fetching...")
        data = await self.deduplicator.fetch_or_wait(cache_key, fetch_func)
        
        # Cache the result
        if data is not None:
            effective_ttl = ttl or self.default_ttls.get(source_type, 60)
            self.cache.set(cache_key, data, ttl=effective_ttl)
        
        return data, False
    
    async def fetch_parallel_with_fallback(
        self,
        providers: List[Tuple[str, Callable]],
        timeout: float = 5.0
    ) -> Tuple[Optional[Any], Optional[str]]:
        """
        Fetch from multiple providers in parallel with intelligent fallback
        
        Args:
            providers: List of (provider_name, fetch_function) tuples
            timeout: Timeout for each provider (seconds)
        
        Returns:
            Tuple of (data, provider_name) or (None, None)
        """
        if not providers:
            return None, None
        
        # Sort providers by priority
        sorted_providers = sorted(
            providers,
            key=lambda p: self._get_provider_priority(p[0]),
            reverse=True
        )
        
        # Create tasks for all providers
        tasks = []
        for provider_name, fetch_func in sorted_providers:
            task = asyncio.create_task(
                self._fetch_with_timeout(provider_name, fetch_func, timeout)
            )
            tasks.append((provider_name, task))
        
        # Wait for first successful result
        for provider_name, task in tasks:
            try:
                result = await task
                if result is not None:
                    # Cancel remaining tasks
                    for other_name, other_task in tasks:
                        if other_name != provider_name and not other_task.done():
                            other_task.cancel()
                    
                    logger.info(f"✅ Fetched from provider: {provider_name}")
                    return result, provider_name
            except asyncio.TimeoutError:
                logger.warning(f"⏱️ Provider {provider_name} timed out")
                continue
            except Exception as e:
                logger.warning(f"❌ Provider {provider_name} failed: {e}")
                continue
        
        logger.error("❌ All providers failed")
        return None, None
    
    async def _fetch_with_timeout(
        self,
        provider_name: str,
        fetch_func: Callable,
        timeout: float
    ) -> Optional[Any]:
        """
        Fetch with timeout and stat tracking
        
        Args:
            provider_name: Name of the provider
            fetch_func: Async fetch function
            timeout: Timeout in seconds
        
        Returns:
            Fetched data or None
        """
        start_time = time.time()
        
        try:
            result = await asyncio.wait_for(fetch_func(), timeout=timeout)
            latency = (time.time() - start_time) * 1000  # milliseconds
            self._update_provider_stats(provider_name, success=True, latency=latency)
            return result
        except asyncio.TimeoutError:
            latency = timeout * 1000
            self._update_provider_stats(provider_name, success=False, latency=latency)
            raise
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            self._update_provider_stats(provider_name, success=False, latency=latency)
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        return {
            "cache": self.cache.get_stats(),
            "deduplication": self.deduplicator.stats,
            "providers": self.provider_stats
        }


# Singleton instance
_price_fetcher: Optional[UnifiedPriceFetcher] = None


def get_price_fetcher() -> UnifiedPriceFetcher:
    """Get or create singleton price fetcher instance"""
    global _price_fetcher
    if _price_fetcher is None:
        _price_fetcher = UnifiedPriceFetcher()
    return _price_fetcher


# Example usage
if __name__ == "__main__":
    import asyncio
    
    logging.basicConfig(level=logging.DEBUG)
    
    async def mock_fetch_gas_price():
        """Mock gas price fetch"""
        await asyncio.sleep(0.5)
        return {"safe": 30, "standard": 50, "fast": 100}
    
    async def test_unified_fetcher():
        fetcher = get_price_fetcher()
        
        # Test 1: Basic caching
        print("\n=== Test 1: Basic Caching ===")
        data1, from_cache1 = await fetcher.fetch_with_cache(
            DataSource.GAS_PRICE,
            {"chain_id": 137},
            mock_fetch_gas_price
        )
        print(f"First fetch: {data1}, from_cache={from_cache1}")
        
        data2, from_cache2 = await fetcher.fetch_with_cache(
            DataSource.GAS_PRICE,
            {"chain_id": 137},
            mock_fetch_gas_price
        )
        print(f"Second fetch: {data2}, from_cache={from_cache2}")
        
        # Test 2: Request deduplication
        print("\n=== Test 2: Request Deduplication ===")
        tasks = [
            fetcher.fetch_with_cache(
                DataSource.GAS_PRICE,
                {"chain_id": 1},
                mock_fetch_gas_price
            )
            for _ in range(5)
        ]
        results = await asyncio.gather(*tasks)
        print(f"5 concurrent requests executed")
        
        # Test 3: Stats
        print("\n=== Test 3: Statistics ===")
        stats = fetcher.get_stats()
        print(json.dumps(stats, indent=2, default=str))
    
    asyncio.run(test_unified_fetcher())
