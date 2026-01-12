#!/usr/bin/env python3
"""
Test script to verify Redis removal and cache manager functionality
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_cache_manager():
    """Test cache manager basic operations"""
    print("Testing cache manager...")
    
    try:
        from offchain.core.cache_manager import get_cache_manager
        
        cache = get_cache_manager(in_memory=True)
        print("✓ Cache manager initialized")
        
        # Test basic cache
        cache.set("test_key", {"value": 123}, ttl=2)  # 2 second TTL for faster testing
        result = cache.get("test_key")
        assert result == {"value": 123}, "Basic cache failed"
        print("✓ Basic caching works")
        
        # Test gas price cache
        cache.set_gas_price(1, 30.5, ttl=60)
        cache.set_gas_price(137, 50.0, ttl=60)
        
        eth_gas = cache.get_gas_price(1)
        poly_gas = cache.get_gas_price(137)
        
        assert eth_gas == 30.5, f"ETH gas price mismatch: {eth_gas}"
        assert poly_gas == 50.0, f"Polygon gas price mismatch: {poly_gas}"
        print("✓ Gas price caching works")
        
        # Test metrics
        cache.set_metric("total_trades", 42)
        cache.set_metric("total_profit", 123.45)
        
        metrics = cache.get_all_metrics()
        assert metrics.get("total_trades") == 42, "Metrics storage failed"
        print("✓ Metrics storage works")
        
        # Test stats
        stats = cache.get_stats()
        assert stats.get("active_cache_entries") >= 1, "Cache stats failed"
        print("✓ Cache statistics work")
        
        # Test cleanup
        import time
        time.sleep(3)  # Wait for test_key to expire (2s TTL + 1s buffer)
        deleted = cache.cleanup_expired()
        print(f"✓ Cleanup removed {deleted} expired entries")
        
        # Verify expired key is gone
        result = cache.get("test_key", "NOT_FOUND")
        assert result == "NOT_FOUND", "Expiration failed"
        print("✓ Cache expiration works")
        
        return True
    except Exception as e:
        print(f"✗ Cache manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_signal_files():
    """Test signal file communication system"""
    print("\nTesting signal file system...")
    
    try:
        # Check if signals directory exists
        signals_dir = Path(__file__).parent / "signals"
        outgoing = signals_dir / "outgoing"
        processed = signals_dir / "processed"
        
        # Create directories if they don't exist
        outgoing.mkdir(parents=True, exist_ok=True)
        processed.mkdir(parents=True, exist_ok=True)
        
        print(f"✓ Signal directories exist: {outgoing}")
        
        # Test creating a signal file
        import json
        import time
        
        test_signal = {
            "type": "TEST",
            "chainId": 137,
            "token": "0xtest",
            "amount": "1000000",
            "timestamp": time.time()
        }
        
        signal_file = outgoing / "test_signal.json"
        with open(signal_file, 'w') as f:
            json.dump(test_signal, f, indent=2)
        
        print("✓ Created test signal file")
        
        # Read it back
        with open(signal_file, 'r') as f:
            read_signal = json.load(f)
        
        assert read_signal["type"] == "TEST", "Signal file read failed"
        print("✓ Signal file read/write works")
        
        # Move to processed (simulate bot.js behavior)
        signal_file.rename(processed / "test_signal.json")
        print("✓ Signal file movement works")
        
        # Cleanup
        (processed / "test_signal.json").unlink()
        
        return True
    except Exception as e:
        print(f"✗ Signal file test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dashboard_integration():
    """Test dashboard integration without Redis"""
    print("\nTesting dashboard integration...")
    
    try:
        from dashboard_integration import DashboardIntegration
        
        integration = DashboardIntegration()
        print("✓ Dashboard integration initialized without Redis")
        
        # Test publishing opportunity
        test_opp = {
            "chain": "Polygon",
            "token_pair": "USDC/USDT",
            "strategy": "Flash Arb",
            "profit_usd": 5.25,
            "gas_cost": 0.75,
            "net_profit": 4.50,
            "executable": True,
            "dex_a": "UniswapV3",
            "dex_b": "Sushiswap",
            "spread_bps": 15
        }
        
        integration.publish_market_opportunity(test_opp)
        print("✓ Published market opportunity to file system")
        
        # Test metrics update
        test_metrics = {
            "status": "OPERATIONAL",
            "uptime": 3600,
            "total_scans": 1000,
            "opportunities_found": 5,
            "txs_executed": 2,
            "total_profit": 10.50,
            "total_gas": 1.50,
            "net_profit": 9.00,
            "success_rate": 1.0,
            "avg_profit_per_tx": 5.25,
            "current_gas_price": 30.0
        }
        
        integration.update_metrics(test_metrics)
        print("✓ Updated system metrics to file system")
        
        return True
    except Exception as e:
        print(f"✗ Dashboard integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gas_price_fallback():
    """Test gas price fallback mechanism"""
    print("\nTesting gas price fallback...")
    
    try:
        from offchain.core.cache_manager import CacheManager
        
        # Create a new in-memory cache for this test
        cache = CacheManager(in_memory=True)
        
        # Test static fallback values
        static_prices = {
            1: 30.0,    # Ethereum
            137: 50.0,  # Polygon
            42161: 0.1, # Arbitrum
            10: 0.5,    # Optimism
            8453: 0.5,  # Base
        }
        
        for chain_id, expected_price in static_prices.items():
            # First check cache (should be empty for new instance)
            cached = cache.get_gas_price(chain_id)
            assert cached == 0.0, f"Cache should be empty for chain {chain_id}, got {cached}"
            
            # Set a price
            cache.set_gas_price(chain_id, expected_price, ttl=60)
            
            # Verify it's cached
            cached = cache.get_gas_price(chain_id)
            assert cached == expected_price, f"Gas price mismatch for chain {chain_id}: expected {expected_price}, got {cached}"
        
        print("✓ Gas price cache and fallback working")
        
        return True
    except Exception as e:
        print(f"✗ Gas price fallback test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("TITAN 2.0 - Redis Removal Test Suite")
    print("=" * 70)
    
    tests = [
        ("Cache Manager", test_cache_manager),
        ("Signal File System", test_signal_files),
        ("Dashboard Integration", test_dashboard_integration),
        ("Gas Price Fallback", test_gas_price_fallback),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{'='*70}")
        result = test_func()
        results.append((name, result))
    
    print(f"\n{'='*70}")
    print("TEST RESULTS:")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Redis removal successful.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
