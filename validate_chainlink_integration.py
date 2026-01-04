"""
Comprehensive integration validation for chainlink oracle feeds
This script validates that the new module integrates properly with the existing codebase
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_imports():
    """Test that all imports work correctly"""
    print("=" * 60)
    print("Testing Imports")
    print("=" * 60)
    
    try:
        from offchain.core import chainlink_oracle_feeds
        print("✓ chainlink_oracle_feeds imports successfully")
    except ImportError as e:
        print(f"✗ Failed to import chainlink_oracle_feeds: {e}")
        return False
    
    try:
        from offchain.core.dynamic_price_oracle import DynamicPriceOracle
        print("✓ DynamicPriceOracle imports successfully")
    except ImportError as e:
        print(f"✗ Failed to import DynamicPriceOracle: {e}")
        return False
    
    return True

def test_backward_compatibility():
    """Test that existing DynamicPriceOracle functionality still works"""
    print("\n" + "=" * 60)
    print("Testing Backward Compatibility")
    print("=" * 60)
    
    try:
        from offchain.core.dynamic_price_oracle import DynamicPriceOracle
        
        # Check that the class can be instantiated with empty web3 connections
        oracle = DynamicPriceOracle({})
        print("✓ DynamicPriceOracle can be instantiated")
        
        # Check that original methods still exist
        assert hasattr(oracle, 'get_chainlink_feeds'), "Missing get_chainlink_feeds method"
        assert hasattr(oracle, 'get_token_price_usd'), "Missing get_token_price_usd method"
        assert hasattr(oracle, 'clear_cache'), "Missing clear_cache method"
        print("✓ All original methods present")
        
        # Check that new method exists
        assert hasattr(oracle, 'get_price_with_enhanced_fallback'), "Missing new method"
        print("✓ New enhanced fallback method present")
        
        return True
    except Exception as e:
        print(f"✗ Backward compatibility test failed: {e}")
        return False

def test_module_structure():
    """Test that the new module has the expected structure"""
    print("\n" + "=" * 60)
    print("Testing Module Structure")
    print("=" * 60)
    
    try:
        from offchain.core import chainlink_oracle_feeds
        
        # Check key constants
        required_constants = [
            'RPC_MAP', 'CHAINLINK_FEEDS', 'CHAINLINK_AGGREGATOR_ABI',
            'CHAIN_NAME_TO_ID', 'COINGECKO_ID_MAP'
        ]
        
        for const in required_constants:
            assert hasattr(chainlink_oracle_feeds, const), f"Missing constant: {const}"
            print(f"✓ {const} present")
        
        # Check key functions
        required_functions = [
            'get_web3_for_chain', 'chainlink_price_usd', 'get_offchain_price',
            'get_price_usd', 'get_price_usd_by_chain_id', 'get_available_feeds',
            'is_chainlink_feed_available'
        ]
        
        for func in required_functions:
            assert hasattr(chainlink_oracle_feeds, func), f"Missing function: {func}"
            print(f"✓ {func}() present")
        
        return True
    except Exception as e:
        print(f"✗ Module structure test failed: {e}")
        return False

def test_data_integrity():
    """Test that the data structures are properly configured"""
    print("\n" + "=" * 60)
    print("Testing Data Integrity")
    print("=" * 60)
    
    try:
        from offchain.core import chainlink_oracle_feeds
        
        # Verify chain feeds
        expected_chains = ["ethereum", "polygon", "arbitrum", "optimism", "base", "bsc", "avalanche", "fantom"]
        for chain in expected_chains:
            assert chain in chainlink_oracle_feeds.CHAINLINK_FEEDS, f"Missing chain: {chain}"
            feeds = chainlink_oracle_feeds.CHAINLINK_FEEDS[chain]
            assert len(feeds) > 0, f"No feeds for {chain}"
            print(f"✓ {chain}: {len(feeds)} feeds")
        
        # Verify chain ID mappings
        for chain in expected_chains:
            assert chain in chainlink_oracle_feeds.CHAIN_NAME_TO_ID, f"Missing chain ID mapping: {chain}"
            chain_id = chainlink_oracle_feeds.CHAIN_NAME_TO_ID[chain]
            assert isinstance(chain_id, int), f"Chain ID for {chain} is not an integer"
            print(f"✓ {chain} -> {chain_id}")
        
        return True
    except Exception as e:
        print(f"✗ Data integrity test failed: {e}")
        return False

def test_integration_with_dynamic_oracle():
    """Test that DynamicPriceOracle properly integrates with chainlink_oracle_feeds"""
    print("\n" + "=" * 60)
    print("Testing Integration with DynamicPriceOracle")
    print("=" * 60)
    
    try:
        from offchain.core.dynamic_price_oracle import DynamicPriceOracle
        from offchain.core import chainlink_oracle_feeds
        
        # Check if the integration is detected
        oracle = DynamicPriceOracle({})
        
        # The oracle should have the enhanced fallback method
        assert hasattr(oracle, 'get_price_with_enhanced_fallback')
        print("✓ Enhanced fallback method available in DynamicPriceOracle")
        
        # Check that chainlink_oracle_feeds is properly imported in dynamic_price_oracle
        import offchain.core.dynamic_price_oracle as dpo_module
        assert hasattr(dpo_module, 'CHAINLINK_ORACLE_AVAILABLE')
        print(f"✓ Chainlink oracle availability flag: {dpo_module.CHAINLINK_ORACLE_AVAILABLE}")
        
        return True
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("\n" + "=" * 60)
    print("COMPREHENSIVE INTEGRATION VALIDATION")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Module Structure", test_module_structure),
        ("Data Integrity", test_data_integrity),
        ("Backward Compatibility", test_backward_compatibility),
        ("Integration with DynamicPriceOracle", test_integration_with_dynamic_oracle),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓✓✓ ALL VALIDATION TESTS PASSED ✓✓✓")
        print("The chainlink oracle feeds module is fully integrated!")
        return 0
    else:
        print(f"\n✗✗✗ {total - passed} TEST(S) FAILED ✗✗✗")
        return 1

if __name__ == "__main__":
    sys.exit(main())
