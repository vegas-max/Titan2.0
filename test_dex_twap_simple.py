"""
Simple tests for DEX TWAP Oracle Module (no pytest required)

Tests TWAP-fed DEX price retrieval with Chainlink fallback.
"""

from offchain.core.dex_twap_oracle import (
    set_dex_twap_price,
    get_dex_twap_price,
    onchain_dex_price,
    clear_twap_cache,
    get_twap_cache_size,
    get_all_twap_pairs
)

# Test token addresses
WMATIC = "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270"
USDC = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
USDT = "0xc2132D05D31c914a87C6611C10748AEb04B58e8F"
WETH = "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619"

def run_tests():
    """Run all tests"""
    passed = 0
    failed = 0
    
    print("\n=== DEX TWAP Oracle Tests ===\n")
    
    # Test 1: Set and get TWAP price
    clear_twap_cache()
    set_dex_twap_price(WMATIC, USDC, 137, 0.85)
    price = get_dex_twap_price(WMATIC, USDC, 137)
    if price == 0.85:
        print("✓ Test 1: Set and get TWAP price - PASSED")
        passed += 1
    else:
        print(f"✗ Test 1: Set and get TWAP price - FAILED (got {price}, expected 0.85)")
        failed += 1
    
    # Test 2: Order independence
    clear_twap_cache()
    set_dex_twap_price(WMATIC, USDC, 137, 0.85)
    price = get_dex_twap_price(USDC, WMATIC, 137)
    if price == 0.85:
        print("✓ Test 2: Order independence - PASSED")
        passed += 1
    else:
        print(f"✗ Test 2: Order independence - FAILED (got {price}, expected 0.85)")
        failed += 1
    
    # Test 3: Case insensitive addresses
    clear_twap_cache()
    set_dex_twap_price(WMATIC.upper(), USDC.lower(), 137, 0.85)
    price = get_dex_twap_price(WMATIC.lower(), USDC.upper(), 137)
    if price == 0.85:
        print("✓ Test 3: Case insensitive addresses - PASSED")
        passed += 1
    else:
        print(f"✗ Test 3: Case insensitive addresses - FAILED (got {price}, expected 0.85)")
        failed += 1
    
    # Test 4: Chain-specific prices
    clear_twap_cache()
    set_dex_twap_price(WETH, USDC, 1, 2000.0)    # Ethereum
    set_dex_twap_price(WETH, USDC, 137, 1999.5)  # Polygon
    price_eth = get_dex_twap_price(WETH, USDC, 1)
    price_polygon = get_dex_twap_price(WETH, USDC, 137)
    if price_eth == 2000.0 and price_polygon == 1999.5:
        print("✓ Test 4: Chain-specific prices - PASSED")
        passed += 1
    else:
        print(f"✗ Test 4: Chain-specific prices - FAILED")
        failed += 1
    
    # Test 5: Get nonexistent price
    clear_twap_cache()
    price = get_dex_twap_price(WMATIC, USDC, 137)
    if price is None:
        print("✓ Test 5: Get nonexistent price - PASSED")
        passed += 1
    else:
        print(f"✗ Test 5: Get nonexistent price - FAILED (got {price}, expected None)")
        failed += 1
    
    # Test 6: Multiple pairs
    clear_twap_cache()
    set_dex_twap_price(WMATIC, USDC, 137, 0.85)
    set_dex_twap_price(WMATIC, USDT, 137, 0.86)
    set_dex_twap_price(USDC, USDT, 137, 1.0001)
    p1 = get_dex_twap_price(WMATIC, USDC, 137)
    p2 = get_dex_twap_price(WMATIC, USDT, 137)
    p3 = get_dex_twap_price(USDC, USDT, 137)
    if p1 == 0.85 and p2 == 0.86 and p3 == 1.0001:
        print("✓ Test 6: Multiple pairs - PASSED")
        passed += 1
    else:
        print(f"✗ Test 6: Multiple pairs - FAILED")
        failed += 1
    
    # Test 7: Cache size
    clear_twap_cache()
    size = get_twap_cache_size()
    set_dex_twap_price(WMATIC, USDC, 137, 0.85)
    size1 = get_twap_cache_size()
    set_dex_twap_price(WMATIC, USDT, 137, 0.86)
    size2 = get_twap_cache_size()
    if size == 0 and size1 == 1 and size2 == 2:
        print("✓ Test 7: Cache size - PASSED")
        passed += 1
    else:
        print(f"✗ Test 7: Cache size - FAILED (sizes: {size}, {size1}, {size2})")
        failed += 1
    
    # Test 8: Clear cache
    clear_twap_cache()
    set_dex_twap_price(WMATIC, USDC, 137, 0.85)
    set_dex_twap_price(WMATIC, USDT, 137, 0.86)
    clear_twap_cache()
    size = get_twap_cache_size()
    price = get_dex_twap_price(WMATIC, USDC, 137)
    if size == 0 and price is None:
        print("✓ Test 8: Clear cache - PASSED")
        passed += 1
    else:
        print(f"✗ Test 8: Clear cache - FAILED")
        failed += 1
    
    # Test 9: Get all TWAP pairs
    clear_twap_cache()
    set_dex_twap_price(WMATIC, USDC, 137, 0.85)
    set_dex_twap_price(WETH, USDC, 1, 2000.0)
    all_pairs = get_all_twap_pairs()
    if len(all_pairs) == 2:
        print("✓ Test 9: Get all TWAP pairs - PASSED")
        passed += 1
    else:
        print(f"✗ Test 9: Get all TWAP pairs - FAILED (got {len(all_pairs)} pairs, expected 2)")
        failed += 1
    
    # Test 10: Get TWAP pairs filtered by chain
    clear_twap_cache()
    set_dex_twap_price(WMATIC, USDC, 137, 0.85)
    set_dex_twap_price(WMATIC, USDT, 137, 0.86)
    set_dex_twap_price(WETH, USDC, 1, 2000.0)
    polygon_pairs = get_all_twap_pairs(chain=137)
    ethereum_pairs = get_all_twap_pairs(chain=1)
    if len(polygon_pairs) == 2 and len(ethereum_pairs) == 1:
        print("✓ Test 10: Get TWAP pairs filtered by chain - PASSED")
        passed += 1
    else:
        print(f"✗ Test 10: Get TWAP pairs filtered by chain - FAILED")
        failed += 1
    
    # Test 11: onchain_dex_price with TWAP
    clear_twap_cache()
    set_dex_twap_price(WMATIC, USDC, 137, 0.85)
    price = onchain_dex_price(WMATIC, USDC, 137)
    if price == 0.85:
        print("✓ Test 11: onchain_dex_price with TWAP - PASSED")
        passed += 1
    else:
        print(f"✗ Test 11: onchain_dex_price with TWAP - FAILED (got {price}, expected 0.85)")
        failed += 1
    
    # Summary
    print(f"\n{'='*50}")
    print(f"Tests passed: {passed}/{passed + failed}")
    print(f"Tests failed: {failed}/{passed + failed}")
    print(f"{'='*50}\n")
    
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    if success:
        print("✅ All DEX TWAP Oracle tests passed!")
        exit(0)
    else:
        print("❌ Some tests failed")
        exit(1)
