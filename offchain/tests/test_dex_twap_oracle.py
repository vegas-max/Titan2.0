"""
Tests for DEX TWAP Oracle Module

Tests TWAP-fed DEX price retrieval with Chainlink fallback.
"""

import pytest
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


class TestDexTwapOracle:
    """Test suite for DEX TWAP Oracle"""

    def setup_method(self):
        """Clear cache before each test"""
        clear_twap_cache()

    def teardown_method(self):
        """Clear cache after each test"""
        clear_twap_cache()

    def test_set_and_get_twap_price(self):
        """Test basic TWAP price storage and retrieval"""
        set_dex_twap_price(WMATIC, USDC, 137, 0.85)
        price = get_dex_twap_price(WMATIC, USDC, 137)
        
        assert price == 0.85

    def test_price_retrieval_order_independent(self):
        """Test that token order doesn't matter for retrieval"""
        set_dex_twap_price(WMATIC, USDC, 137, 0.85)
        
        # Should work with reversed order
        price = get_dex_twap_price(USDC, WMATIC, 137)
        assert price == 0.85

    def test_price_storage_order_independent(self):
        """Test that token order doesn't matter for storage"""
        set_dex_twap_price(WMATIC, USDC, 137, 0.85)
        set_dex_twap_price(USDC, WMATIC, 137, 0.87)
        
        # Second call should overwrite first (same pair)
        price = get_dex_twap_price(WMATIC, USDC, 137)
        assert price == 0.87

    def test_case_insensitive_addresses(self):
        """Test that address case doesn't matter"""
        set_dex_twap_price(WMATIC.upper(), USDC.lower(), 137, 0.85)
        price = get_dex_twap_price(WMATIC.lower(), USDC.upper(), 137)
        
        assert price == 0.85

    def test_chain_specific_prices(self):
        """Test that prices are chain-specific"""
        set_dex_twap_price(WETH, USDC, 1, 2000.0)    # Ethereum
        set_dex_twap_price(WETH, USDC, 137, 1999.5)  # Polygon
        
        price_eth = get_dex_twap_price(WETH, USDC, 1)
        price_polygon = get_dex_twap_price(WETH, USDC, 137)
        
        assert price_eth == 2000.0
        assert price_polygon == 1999.5

    def test_get_nonexistent_price(self):
        """Test retrieving a price that doesn't exist"""
        price = get_dex_twap_price(WMATIC, USDC, 137)
        assert price is None

    def test_multiple_pairs(self):
        """Test storing multiple token pairs"""
        set_dex_twap_price(WMATIC, USDC, 137, 0.85)
        set_dex_twap_price(WMATIC, USDT, 137, 0.86)
        set_dex_twap_price(USDC, USDT, 137, 1.0001)
        
        assert get_dex_twap_price(WMATIC, USDC, 137) == 0.85
        assert get_dex_twap_price(WMATIC, USDT, 137) == 0.86
        assert get_dex_twap_price(USDC, USDT, 137) == 1.0001

    def test_cache_size(self):
        """Test cache size tracking"""
        assert get_twap_cache_size() == 0
        
        set_dex_twap_price(WMATIC, USDC, 137, 0.85)
        assert get_twap_cache_size() == 1
        
        set_dex_twap_price(WMATIC, USDT, 137, 0.86)
        assert get_twap_cache_size() == 2
        
        # Updating existing pair shouldn't increase size
        set_dex_twap_price(WMATIC, USDC, 137, 0.87)
        assert get_twap_cache_size() == 2

    def test_clear_cache(self):
        """Test cache clearing"""
        set_dex_twap_price(WMATIC, USDC, 137, 0.85)
        set_dex_twap_price(WMATIC, USDT, 137, 0.86)
        
        assert get_twap_cache_size() == 2
        
        clear_twap_cache()
        assert get_twap_cache_size() == 0
        assert get_dex_twap_price(WMATIC, USDC, 137) is None

    def test_get_all_twap_pairs(self):
        """Test retrieving all TWAP pairs"""
        set_dex_twap_price(WMATIC, USDC, 137, 0.85)
        set_dex_twap_price(WETH, USDC, 1, 2000.0)
        
        all_pairs = get_all_twap_pairs()
        assert len(all_pairs) == 2

    def test_get_twap_pairs_filtered_by_chain(self):
        """Test retrieving TWAP pairs for specific chain"""
        set_dex_twap_price(WMATIC, USDC, 137, 0.85)
        set_dex_twap_price(WMATIC, USDT, 137, 0.86)
        set_dex_twap_price(WETH, USDC, 1, 2000.0)
        
        polygon_pairs = get_all_twap_pairs(chain=137)
        ethereum_pairs = get_all_twap_pairs(chain=1)
        
        assert len(polygon_pairs) == 2
        assert len(ethereum_pairs) == 1

    def test_onchain_dex_price_with_twap(self):
        """Test onchain_dex_price returns TWAP when available"""
        set_dex_twap_price(WMATIC, USDC, 137, 0.85)
        
        price = onchain_dex_price(WMATIC, USDC, 137)
        assert price == 0.85

    def test_onchain_dex_price_without_twap(self):
        """Test onchain_dex_price fallback when TWAP unavailable"""
        # Don't set TWAP, should try Chainlink fallback
        price = onchain_dex_price(WMATIC, USDC, 137)
        # May return None if Chainlink not available in test environment
        # Just ensure it doesn't crash
        assert price is None or isinstance(price, (int, float))

    def test_zero_price(self):
        """Test that zero prices are allowed (could indicate no liquidity)"""
        set_dex_twap_price(WMATIC, USDC, 137, 0.0)
        price = get_dex_twap_price(WMATIC, USDC, 137)
        
        assert price == 0.0

    def test_negative_price_allowed(self):
        """Test that negative prices are stored (could be used for inverted pairs)"""
        set_dex_twap_price(WMATIC, USDC, 137, -0.85)
        price = get_dex_twap_price(WMATIC, USDC, 137)
        
        assert price == -0.85

    def test_large_price_values(self):
        """Test handling of large price values"""
        large_price = 1e18
        set_dex_twap_price(WMATIC, USDC, 137, large_price)
        price = get_dex_twap_price(WMATIC, USDC, 137)
        
        assert price == large_price

    def test_very_small_price_values(self):
        """Test handling of very small price values"""
        small_price = 1e-18
        set_dex_twap_price(WMATIC, USDC, 137, small_price)
        price = get_dex_twap_price(WMATIC, USDC, 137)
        
        assert price == small_price


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
    print("\n✅ DEX TWAP Oracle tests completed")
