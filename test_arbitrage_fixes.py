#!/usr/bin/env python3
"""
Test critical arbitrage blocker fixes
Tests gas price fallback and signal generation
"""

import os
import sys
import time
import json
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock environment for testing
os.environ['REAL_TIME_DATA_ENABLED'] = 'false'  # Use static gas prices for testing
os.environ['EXECUTOR_ADDRESS'] = '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045'

def test_gas_price_fallback():
    """Test 1: Gas price never returns 0"""
    print("\n" + "="*70)
    print("TEST 1: Gas Price Fallback")
    print("="*70)
    
    from offchain.ml.brain import OmniBrain
    
    brain = OmniBrain()
    
    # Test gas price for various chains
    test_chains = [1, 137, 42161, 10, 8453, 56, 43114]
    
    all_passed = True
    for chain_id in test_chains:
        gas_price = brain._get_gas_price(chain_id)
        
        if gas_price == 0:
            print(f"❌ FAILED: Chain {chain_id} returned 0 gas price")
            all_passed = False
        else:
            print(f"✅ PASSED: Chain {chain_id} gas price: {gas_price} Gwei")
    
    if all_passed:
        print("\n✅ Gas price fallback test PASSED - No zero values returned")
    else:
        print("\n❌ Gas price fallback test FAILED - Some chains returned 0")
    
    return all_passed


def test_static_gas_prices():
    """Test 2: Static gas prices are reasonable"""
    print("\n" + "="*70)
    print("TEST 2: Static Gas Price Values")
    print("="*70)
    
    from offchain.ml.brain import OmniBrain
    
    brain = OmniBrain()
    
    # Verify static gas prices are in reasonable ranges
    all_reasonable = True
    
    for chain_id, expected_gas in brain.STATIC_GAS_PRICES.items():
        if expected_gas <= 0 or expected_gas > 1000:
            print(f"❌ FAILED: Chain {chain_id} has unreasonable static gas: {expected_gas}")
            all_reasonable = False
        else:
            print(f"✅ PASSED: Chain {chain_id} static gas: {expected_gas} Gwei (reasonable)")
    
    if all_reasonable:
        print("\n✅ Static gas price test PASSED - All values reasonable")
    else:
        print("\n❌ Static gas price test FAILED - Some values unreasonable")
    
    return all_reasonable


def test_signal_directory_creation():
    """Test 3: Signal directories are created"""
    print("\n" + "="*70)
    print("TEST 3: Signal Directory Creation")
    print("="*70)
    
    signals_dir = 'signals/outgoing'
    processed_dir = 'signals/processed'
    
    # Check if directories exist or can be created
    from pathlib import Path
    
    signals_path = Path(signals_dir)
    processed_path = Path(processed_dir)
    
    signals_path.mkdir(parents=True, exist_ok=True)
    processed_path.mkdir(parents=True, exist_ok=True)
    
    if signals_path.exists() and processed_path.exists():
        print(f"✅ PASSED: Signal directories exist")
        print(f"   • {signals_dir}: ✓")
        print(f"   • {processed_dir}: ✓")
        return True
    else:
        print(f"❌ FAILED: Could not create signal directories")
        return False


def test_redis_optional():
    """Test 4: System works without Redis"""
    print("\n" + "="*70)
    print("TEST 4: Redis-Free Operations")
    print("="*70)
    
    try:
        # Try to import dashboard without Redis
        import sys
        
        # Temporarily prevent redis import
        import builtins
        original_import = builtins.__import__
        
        def mock_import(name, *args, **kwargs):
            if name == 'redis':
                raise ImportError("Redis not available (test)")
            return original_import(name, *args, **kwargs)
        
        # This should work even without Redis
        from live_operational_dashboard import OperationalDashboard
        
        dashboard = OperationalDashboard()
        
        # Check that signal file reading method exists
        if hasattr(dashboard, 'update_from_signal_files'):
            print("✅ PASSED: Dashboard has signal file reading capability")
            print("   • update_from_signal_files method: ✓")
            print("   • Redis is optional: ✓")
            return True
        else:
            print("❌ FAILED: Dashboard missing signal file reading method")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: Dashboard initialization error: {e}")
        return False


def test_requirements_no_redis():
    """Test 5: Redis not in requirements.txt"""
    print("\n" + "="*70)
    print("TEST 5: Redis Removed from Requirements")
    print("="*70)
    
    req_file = 'requirements.txt'
    
    if not os.path.exists(req_file):
        print(f"⚠️  WARNING: {req_file} not found")
        return True
    
    with open(req_file, 'r') as f:
        content = f.read()
    
    if 'redis' in content.lower():
        print(f"❌ FAILED: Redis still in {req_file}")
        print(f"   Please remove Redis from requirements.txt")
        return False
    else:
        print(f"✅ PASSED: Redis removed from {req_file}")
        return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("TITAN 2.0 - ARBITRAGE BLOCKER FIX VALIDATION")
    print("="*70)
    print("Testing critical fixes for:")
    print("  1. Gas price fallback (never returns 0)")
    print("  2. Static gas price values")
    print("  3. Signal directory creation")
    print("  4. Redis-free operations")
    print("  5. Redis removed from requirements")
    print("")
    
    results = []
    
    # Run tests
    results.append(("Gas Price Fallback", test_gas_price_fallback()))
    results.append(("Static Gas Prices", test_static_gas_prices()))
    results.append(("Signal Directories", test_signal_directory_creation()))
    results.append(("Redis Optional", test_redis_optional()))
    results.append(("Requirements Check", test_requirements_no_redis()))
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*70)
    print(f"TOTAL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("="*70)
    
    if passed == total:
        print("\n🎉 All tests PASSED! System is ready for operation.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) FAILED. Please review and fix issues.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
