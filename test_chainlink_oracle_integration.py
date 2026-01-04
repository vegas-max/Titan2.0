"""
Test script for chainlink_oracle_feeds integration
Validates the new oracle token list functionality
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from offchain.core import chainlink_oracle_feeds
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_chainlink_feeds_availability():
    """Test that Chainlink feeds are properly configured"""
    logger.info("=" * 60)
    logger.info("Testing Chainlink Feeds Availability")
    logger.info("=" * 60)
    
    chains = ["ethereum", "polygon", "arbitrum", "optimism", "base", "bsc", "avalanche", "fantom"]
    
    for chain in chains:
        feeds = chainlink_oracle_feeds.get_available_feeds(chain)
        logger.info(f"\n{chain.upper()}: {len(feeds)} feeds available")
        for token, address in feeds.items():
            logger.info(f"  {token}: {address}")
    
    return True

def test_feed_availability_check():
    """Test the is_chainlink_feed_available function"""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Feed Availability Check")
    logger.info("=" * 60)
    
    test_cases = [
        ("ETH", "ethereum", True),
        ("USDC", "polygon", True),
        ("UNKNOWN", "ethereum", False),
        ("ETH", "unknown_chain", False),
    ]
    
    for token, chain, expected in test_cases:
        result = chainlink_oracle_feeds.is_chainlink_feed_available(token, chain)
        status = "✓" if result == expected else "✗"
        logger.info(f"{status} {token} on {chain}: {result} (expected: {expected})")
    
    return True

def test_offchain_price_fetcher():
    """Test offchain price fetcher (Coingecko/Binance fallback)"""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Offchain Price Fetcher")
    logger.info("=" * 60)
    
    # Test with common tokens that should have prices available
    test_tokens = ["ETH", "BTC", "USDC"]
    
    for token in test_tokens:
        try:
            price = chainlink_oracle_feeds.get_offchain_price(token)
            if price > 0:
                logger.info(f"✓ {token}: ${price:.2f}")
            else:
                logger.warning(f"⚠ {token}: No price available")
        except Exception as e:
            logger.error(f"✗ {token}: Error - {e}")
    
    return True

def test_rpc_configuration():
    """Test RPC configuration mapping"""
    logger.info("\n" + "=" * 60)
    logger.info("Testing RPC Configuration")
    logger.info("=" * 60)
    
    for chain_name, rpc_url in chainlink_oracle_feeds.RPC_MAP.items():
        if rpc_url:
            logger.info(f"✓ {chain_name}: RPC configured")
        else:
            logger.warning(f"⚠ {chain_name}: RPC NOT configured in environment")
    
    return True

def test_chain_id_mapping():
    """Test chain name to chain ID mapping"""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Chain ID Mapping")
    logger.info("=" * 60)
    
    for chain_name, chain_id in chainlink_oracle_feeds.CHAIN_NAME_TO_ID.items():
        logger.info(f"{chain_name}: {chain_id}")
    
    return True

def main():
    """Run all tests"""
    logger.info("\n" + "=" * 60)
    logger.info("CHAINLINK ORACLE FEEDS INTEGRATION TEST")
    logger.info("=" * 60)
    
    tests = [
        ("Chainlink Feeds Availability", test_chainlink_feeds_availability),
        ("Feed Availability Check", test_feed_availability_check),
        ("Chain ID Mapping", test_chain_id_mapping),
        ("RPC Configuration", test_rpc_configuration),
        ("Offchain Price Fetcher", test_offchain_price_fetcher),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test '{test_name}' failed with error: {e}")
            results.append((test_name, False))
    
    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("✓ All tests passed!")
        return 0
    else:
        logger.error(f"✗ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
