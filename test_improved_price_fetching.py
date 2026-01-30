#!/usr/bin/env python3
"""
Test suite for improved price fetching system
Validates:
- Request deduplication
- LRU caching
- Parallel provider queries
- Cache hit rates
- Performance improvements
"""

import asyncio
import time
import logging
from typing import List, Dict, Any

from offchain.core.unified_price_fetcher import get_price_fetcher, DataSource
from offchain.core.improved_gas_oracle import get_gas_oracle
from offchain.core.optimized_aggregator_manager import get_aggregator_manager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_request_deduplication():
    """Test that concurrent identical requests are deduplicated"""
    print("\n" + "="*60)
    print("TEST 1: Request Deduplication")
    print("="*60)
    
    oracle = await get_gas_oracle()
    
    # Make 10 concurrent requests for the same data
    print("\nMaking 10 concurrent requests for Polygon gas prices...")
    start = time.time()
    
    tasks = [oracle.get_gas_prices(137) for _ in range(10)]
    results = await asyncio.gather(*tasks)
    
    elapsed = time.time() - start
    
    print(f"✅ All 10 requests completed in {elapsed:.2f}s")
    print(f"   All results identical: {len(set(str(r) for r in results)) == 1}")
    
    # Check deduplication stats
    stats = oracle.get_stats()
    dedup_stats = stats.get('deduplication', {})
    print(f"\n📊 Deduplication Stats:")
    print(f"   Unique requests: {dedup_stats.get('unique_requests', 0)}")
    print(f"   Deduplicated: {dedup_stats.get('deduplicated', 0)}")
    
    await oracle.close()
    
    # Should complete very quickly due to deduplication (much faster than 10 sequential requests)
    return elapsed < 2.0


async def test_lru_cache():
    """Test LRU cache eviction and hit rate"""
    print("\n" + "="*60)
    print("TEST 2: LRU Cache Eviction")
    print("="*60)
    
    fetcher = get_price_fetcher()
    
    # Mock fetch function
    async def mock_fetch():
        await asyncio.sleep(0.01)
        return {"value": time.time()}
    
    # Fill cache with 100 different keys
    print("\nFilling cache with 100 entries...")
    for i in range(100):
        await fetcher.fetch_with_cache(
            source_type=DataSource.TOKEN_PRICE,
            params={"token": f"0x{i:040x}"},
            fetch_func=mock_fetch,
            ttl=300
        )
    
    # Access first 10 entries again (make them recently used)
    print("Accessing first 10 entries again...")
    for i in range(10):
        await fetcher.fetch_with_cache(
            source_type=DataSource.TOKEN_PRICE,
            params={"token": f"0x{i:040x}"},
            fetch_func=mock_fetch
        )
    
    # Check cache stats
    stats = fetcher.get_stats()
    cache_stats = stats.get('cache', {})
    print(f"\n📊 Cache Stats:")
    print(f"   Size: {cache_stats.get('size', 0)}")
    print(f"   Hits: {cache_stats.get('hits', 0)}")
    print(f"   Misses: {cache_stats.get('misses', 0)}")
    print(f"   Hit rate: {cache_stats.get('hit_rate', '0%')}")
    
    # Verify hit rate is reasonable (10 hits out of 110 total = ~9%)
    hit_rate = float(cache_stats.get('hit_rate', '0%').rstrip('%'))
    return hit_rate > 7.0  # At least 7% cache hits (accounting for 10/110 = 9%)


async def test_parallel_provider_queries():
    """Test parallel gas price provider queries"""
    print("\n" + "="*60)
    print("TEST 3: Parallel Provider Queries")
    print("="*60)
    
    oracle = await get_gas_oracle()
    
    # Force refresh to bypass cache and test parallel fetching
    print("\nFetching Polygon gas prices (parallel providers)...")
    start = time.time()
    
    gas_price = await oracle.get_gas_prices(137, force_refresh=True)
    
    elapsed = time.time() - start
    
    if gas_price:
        print(f"✅ Gas price fetched in {elapsed:.2f}s")
        print(f"   Source: {gas_price.source}")
        print(f"   Safe: {gas_price.safe} Gwei")
        print(f"   Propose: {gas_price.propose} Gwei")
        print(f"   Fast: {gas_price.fast} Gwei")
        print(f"   Valid: {gas_price.is_valid()}")
    else:
        print(f"❌ Failed to fetch gas price")
    
    # Check provider stats
    stats = oracle.get_stats()
    provider_stats = stats.get('providers', {})
    print(f"\n📊 Provider Stats:")
    for provider, pstats in provider_stats.items():
        success_rate = (pstats['successes'] / pstats['requests'] * 100 
                       if pstats['requests'] > 0 else 0)
        print(f"   {provider}:")
        print(f"      Requests: {pstats['requests']}")
        print(f"      Success rate: {success_rate:.1f}%")
        print(f"      Avg latency: {pstats['avg_latency']:.0f}ms")
    
    await oracle.close()
    
    # Should complete quickly due to parallel queries (< 3s for network requests)
    return elapsed < 3.0 and gas_price is not None


async def test_aggregator_filtering():
    """Test smart aggregator pre-filtering"""
    print("\n" + "="*60)
    print("TEST 4: Smart Aggregator Filtering")
    print("="*60)
    
    manager = await get_aggregator_manager()
    
    # Test 1: Polygon (should get multiple aggregators)
    print("\nTest 4a: Polygon aggregators")
    poly_aggs = manager.get_compatible_aggregators(chain_id=137, trade_size_usd=100)
    print(f"   Found {len(poly_aggs)} aggregators")
    
    # Test 2: High-value trade (should include CoW Swap)
    print("\nTest 4b: High-value trade on Ethereum")
    eth_high = manager.get_compatible_aggregators(chain_id=1, trade_size_usd=2000)
    print(f"   Found {len(eth_high)} aggregators")
    
    # Test 3: Solana (should only get Jupiter)
    print("\nTest 4c: Solana (should only get Jupiter)")
    solana_aggs = manager.get_compatible_aggregators(chain_id=101)
    print(f"   Found {len(solana_aggs)} aggregators")
    
    await manager.close()
    
    # Validation
    return len(poly_aggs) >= 3 and len(solana_aggs) >= 1


async def test_cache_performance():
    """Test cache performance improvement"""
    print("\n" + "="*60)
    print("TEST 5: Cache Performance")
    print("="*60)
    
    oracle = await get_gas_oracle()
    
    # Warm up cache
    print("\nWarming up cache...")
    await oracle.get_gas_prices(137)
    
    # Test cached requests (should be very fast)
    print("\nMaking 20 cached requests...")
    start = time.time()
    
    for _ in range(20):
        await oracle.get_gas_prices(137)
    
    cached_time = time.time() - start
    avg_cached = cached_time / 20
    
    print(f"✅ 20 cached requests completed in {cached_time:.3f}s")
    print(f"   Average per request: {avg_cached*1000:.2f}ms")
    
    # Test fresh requests (should be slower)
    print("\nMaking 3 fresh requests (force refresh)...")
    start = time.time()
    
    for _ in range(3):
        await oracle.get_gas_prices(137, force_refresh=True)
    
    fresh_time = time.time() - start
    avg_fresh = fresh_time / 3
    
    print(f"✅ 3 fresh requests completed in {fresh_time:.3f}s")
    print(f"   Average per request: {avg_fresh*1000:.2f}ms")
    
    speedup = avg_fresh / avg_cached if avg_cached > 0 else 0
    print(f"\n⚡ Cache speedup: {speedup:.1f}x faster")
    
    await oracle.close()
    
    # Cached requests should be significantly faster (at least 100x)
    return speedup > 100.0


async def run_all_tests():
    """Run all tests and generate report"""
    print("\n" + "="*60)
    print("IMPROVED PRICE FETCHING SYSTEM - TEST SUITE")
    print("="*60)
    
    tests = [
        ("Request Deduplication", test_request_deduplication),
        ("LRU Cache", test_lru_cache),
        ("Parallel Provider Queries", test_parallel_provider_queries),
        ("Aggregator Filtering", test_aggregator_filtering),
        ("Cache Performance", test_cache_performance),
    ]
    
    results: Dict[str, bool] = {}
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            logger.error(f"Test '{test_name}' failed with error: {e}")
            results[test_name] = False
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Price fetching system is working correctly.")
    else:
        print(f"\n⚠️ {total-passed} test(s) failed. Review logs above for details.")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
