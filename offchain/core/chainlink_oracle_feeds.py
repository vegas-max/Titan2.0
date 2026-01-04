"""
Chainlink Oracle Feeds Module
Enhanced Chainlink price feed integration with multi-tier fallback support.

This module provides:
- Comprehensive Chainlink price feed addresses for multiple chains
- Direct on-chain price fetching via Web3
- Multi-tier fallback: Chainlink → Coingecko → Binance
- Unified price fetcher interface

Integrated into Titan 2.0 architecture for reliable token pricing across all supported chains.
"""

import json
import os
from web3 import Web3
from dotenv import load_dotenv
import requests
import logging
from typing import Optional, Dict

load_dotenv()

logger = logging.getLogger("ChainlinkOracleFeeds")

#==============================================================================
# RPC Per Chain
#==============================================================================
RPC_MAP = {
    "polygon": os.getenv("POLYGON_RPC") or os.getenv("RPC_POLYGON"),
    "ethereum": os.getenv("ALCHEMY_RPC_ETH") or os.getenv("RPC_ETHEREUM"),
    "arbitrum": os.getenv("ALCHEMY_RPC_ARB") or os.getenv("RPC_ARBITRUM"),
    "optimism": os.getenv("ALCHEMY_RPC_OPT") or os.getenv("RPC_OPTIMISM"),
    "base": os.getenv("ALCHEMY_RPC_BASE") or os.getenv("RPC_BASE"),
    "bsc": os.getenv("RPC_BSC"),
    "avalanche": os.getenv("RPC_AVALANCHE"),
    "fantom": os.getenv("RPC_FANTOM"),
}

# Chain name to chain ID mapping
CHAIN_NAME_TO_ID = {
    "polygon": 137,
    "ethereum": 1,
    "arbitrum": 42161,
    "optimism": 10,
    "base": 8453,
    "bsc": 56,
    "avalanche": 43114,
    "fantom": 250,
}

#==============================================================================
# Chainlink Price Feed Addresses
#   Format: token_symbol -> chainlink aggregator address for USD
#   IMPORTANT: These are **mainnet** feed addresses
#==============================================================================

CHAINLINK_FEEDS = {
    "polygon": {
        "ETH": "0xF9680D99D6C9589e2a93a78A04A279e509205945",
        "USDC": "0xfE4A8cc5b5B2366C1B58Bea3858e81843581b2F7",
        "USDT": "0x0A6513e40db6EB1b165753AD52E80663aeA50545",
        "DAI": "0x4746DeC9e833A82EC7C2C1356372CcF2cfcD2F3D",
        "WBTC": "0xc907E116054Ad103354f2D350FD2514433D57F6f",
        "MATIC": "0xAB594600376Ec9fD91F8e885dADF0CE036862dE0",
        "LINK": "0xd9FFdb71EbE7496cC440152d43986Aae0AB76665",
        "AAVE": "0x72484B12719E23115761D5DA1646945632979bB6",
    },
    "ethereum": {
        "ETH": "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419",
        "USDC": "0x8fFfFfd4AfB6115b954Bd326cbe7B4BA576818f6",
        "USDT": "0x3E7d1eAB13ad0104d2750B8863b489D65364e32D",
        "DAI": "0xAed0c38402a5d19df6E4c03F4E2DceD6e29c1ee9",
        "WBTC": "0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c",
        "LINK": "0x2c1d072e956AFFC0D435Cb7AC38EF18d24d9127c",
        "AAVE": "0x547a514d5e3769680Ce22B2361c10Ea13619e8a9",
    },
    "arbitrum": {
        "ETH": "0x639Fe6ab55C921f74e7fac1ee960C0B6293ba612",
        "USDC": "0x50834F3163758fcC1Df9973b6e91f0F0F0434aD3",
        "USDT": "0x3f3f5dF88dC9F13eac63DF89EC16ef6e7E25DdE7",
        "WBTC": "0x6ce185860a4963106506C203335A2910413708e9",
        "DAI": "0xc5C8E77B397E531B8EC06BFb0048328B30E9eCfB",
        "LINK": "0x86E53CF1B870786351Da77A57575e79CB55812CB",
    },
    "optimism": {
        "ETH": "0x13e3Ee699D1909E989722E753853AE30b17e08c5",
        "USDC": "0x16a9FA2FDa030272Ce99B29CF780dFA30361E0f3",
        "USDT": "0xECef79E109e997bCA29c1c0897ec9d7b03647F5E",
        "WBTC": "0xD702DD976Fb76Fffc2D3963D037dfDae5b04E593",
        "DAI": "0x8dBa75e83DA73cc766A7e5a0ee71F656BAb470d6",
        "LINK": "0xCc232dcFAAE6354cE191Bd574108c1aD03f86450",
    },
    "base": {
        "ETH": "0x71041dddad3595F9CEd3DcCFBe3D1F4b0a16Bb70",
        "USDC": "0x7e860098F58bBFC8648a4311b374B1D669a2bc6B",
        # Additional Base feeds can be added as they become available
    },
    "bsc": {
        "BNB": "0x0567F2323251f0Aab15c8DfB1967E4e8A7D42aeE",
        "BUSD": "0xcBb98864Ef56E9042e7d2efef76141f15731B82f",
        "USDC": "0x51597f405303C4377E36123cBc172b13269EA163",
        "USDT": "0xB97Ad0E74fa7d920791E90258A6E2085088b4320",
        "ETH": "0x9ef1B8c0E4F7dc8bF5719Ea496883DC6401d5b2e",
        "WBTC": "0x264990fbd0A4796A3E3d8E37C4d5F87a3aCa5Ebf",
    },
    "avalanche": {
        "AVAX": "0x0A77230d17318075983913bC2145DB16C7366156",
        "USDC": "0xF096872672F44d6EBA71458D74fe67F9a77a23B9",
        "USDT": "0xEBE676ee90Fe1112671f19b6B7459bC678B67e8a",
        "ETH": "0x976B3D034E162d8bD72D6b9C989d545b839003b0",
        "WBTC": "0x2779D32d5166BAaa2B2b658333bA7e6Ec0C65743",
    },
    "fantom": {
        "FTM": "0xf4766552D15AE4d256Ad41B6cf2933482B0680dc",
        "USDC": "0x2553f4eeb82d5A26427b8d1106C51499CBa5D99c",
        # Additional Fantom feeds can be added as available
    }
}

#==============================================================================
# CHAINLINK ABI
#==============================================================================

CHAINLINK_AGGREGATOR_ABI = json.loads("""
[
  {
    "inputs": [],
    "name": "latestRoundData",
    "outputs": [
      { "internalType": "uint80", "name": "roundId", "type": "uint80" },
      { "internalType": "int256", "name": "answer", "type": "int256" },
      { "internalType": "uint256", "name": "startedAt", "type": "uint256" },
      { "internalType": "uint256", "name": "updatedAt", "type": "uint256" },
      { "internalType": "uint80", "name": "answeredInRound", "type": "uint80" }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "decimals",
    "outputs": [{ "internalType": "uint8", "name": "", "type": "uint8" }],
    "stateMutability": "view",
    "type": "function"
  }
]
""")

# API Configuration
API_TIMEOUT_SECONDS = int(os.getenv("ORACLE_API_TIMEOUT", "5"))

#==============================================================================
# External API Configuration
#==============================================================================

COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
BINANCE_API_URL = "https://api.binance.com/api/v3"

# Token symbol to CoinGecko ID mapping (for common tokens)
COINGECKO_ID_MAP = {
    "ETH": "ethereum",
    "WETH": "ethereum",
    "BTC": "bitcoin",
    "WBTC": "wrapped-bitcoin",
    "USDC": "usd-coin",
    "USDT": "tether",
    "DAI": "dai",
    "MATIC": "matic-network",
    "LINK": "chainlink",
    "AAVE": "aave",
    "BNB": "binancecoin",
    "AVAX": "avalanche-2",
    "FTM": "fantom",
    "BUSD": "binance-usd",
}

#==============================================================================
# ORACLE PRICE FETCHER
#==============================================================================

def get_web3_for_chain(chain: str) -> Web3:
    """
    Returns a Web3 instance for the given chain key.
    
    Args:
        chain: Chain name (e.g., "ethereum", "polygon")
        
    Returns:
        Web3 instance
        
    Raises:
        KeyError: If no RPC configured for chain
        ConnectionError: If connection to RPC fails
    """
    if chain not in RPC_MAP:
        raise KeyError(f"No RPC configured for chain: {chain}")
    rpc = RPC_MAP[chain]
    if not rpc:
        raise ValueError(f"RPC URL not configured in environment for chain: {chain}. Please set the appropriate environment variable.")
    web3 = Web3(Web3.HTTPProvider(rpc))
    if not web3.is_connected():
        raise ConnectionError(f"Failed to connect to RPC for chain: {chain}")
    return web3


def chainlink_price_usd(token_symbol: str, chain: str) -> float:
    """
    Fetches an on-chain Chainlink price feed for a given token & chain.
    Returns price in USD as float.
    
    Args:
        token_symbol: Token symbol (e.g., "ETH", "USDC")
        chain: Chain name (e.g., "ethereum", "polygon")
        
    Returns:
        Price in USD as float
        
    Raises:
        KeyError: If no Chainlink feed available for token/chain
        Exception: If price fetch fails
    """
    token_symbol = token_symbol.upper()
    if chain not in CHAINLINK_FEEDS or token_symbol not in CHAINLINK_FEEDS[chain]:
        raise KeyError(f"No Chainlink feed available for {token_symbol} on {chain}")

    feed_address = Web3.to_checksum_address(CHAINLINK_FEEDS[chain][token_symbol])
    web3 = get_web3_for_chain(chain)
    contract = web3.eth.contract(address=feed_address, abi=CHAINLINK_AGGREGATOR_ABI)
    
    # Get latest round data
    data = contract.functions.latestRoundData().call()
    decimals = contract.functions.decimals().call()
    
    # Extract price from answer (index 1)
    price = float(data[1]) / (10 ** decimals)
    
    logger.debug(f"📊 Chainlink price for {token_symbol} on {chain}: ${price:.2f}")
    return price


def get_offchain_price(token_symbol: str) -> float:
    """
    Fetch token price from offchain APIs (Coingecko → Binance fallback).
    
    Args:
        token_symbol: Token symbol (e.g., "ETH", "BTC")
        
    Returns:
        Price in USD as float, or 0.0 if unavailable
    """
    token_symbol = token_symbol.upper()
    
    # Try Coingecko first
    try:
        coingecko_id = COINGECKO_ID_MAP.get(token_symbol, token_symbol.lower())
        url = f"{COINGECKO_API_URL}/simple/price?ids={coingecko_id}&vs_currencies=usd"
        
        # Check for API key and validate format
        api_key = os.getenv("COINGECKO_API_KEY")
        headers = {}
        if api_key:
            # Basic validation: ensure API key is alphanumeric with hyphens
            if api_key and api_key.replace('-', '').replace('_', '').isalnum():
                headers["x-cg-pro-api-key"] = api_key
            else:
                logger.warning("CoinGecko API key format appears invalid, proceeding without it")
            
        r = requests.get(url, headers=headers, timeout=API_TIMEOUT_SECONDS)
        r.raise_for_status()
        data = r.json()
        
        price = float(data[coingecko_id]['usd'])
        logger.debug(f"📊 Coingecko price for {token_symbol}: ${price:.2f}")
        return price
    except Exception as e:
        logger.debug(f"Coingecko lookup failed for {token_symbol}: {e}")
        
    # Fallback to Binance with multiple pair attempts
    binance_pairs = [
        f"{token_symbol}USDT",
        f"{token_symbol}BUSD",
        f"{token_symbol}USD",
    ]
    
    for symbol in binance_pairs:
        try:
            url = f"{BINANCE_API_URL}/ticker/price?symbol={symbol}"
            r = requests.get(url, timeout=API_TIMEOUT_SECONDS)
            r.raise_for_status()
            price = float(r.json()['price'])
            logger.debug(f"📊 Binance price for {token_symbol} ({symbol}): ${price:.2f}")
            return price
        except Exception as e:
            logger.debug(f"Binance lookup failed for {symbol}: {e}")
            continue
        
    logger.warning(f"⚠️ Could not fetch price for {token_symbol} from any source")
    return 0.0


def get_price_usd(token_symbol: str, chain: str) -> float:
    """
    Unified price fetcher with fallback:
      1) Chainlink (on-chain, most reliable)
      2) Coingecko (off-chain REST API)
      3) Binance (off-chain REST API as last resort)
      
    Args:
        token_symbol: Token symbol (e.g., "ETH", "USDC")
        chain: Chain name (e.g., "ethereum", "polygon")
        
    Returns:
        Price in USD as float, or 0.0 if unavailable from all sources
    """
    # Try Chainlink first (most reliable)
    try:
        return chainlink_price_usd(token_symbol, chain)
    except Exception as e:
        logger.debug(f"Chainlink lookup failed for {token_symbol} on {chain}: {e}")
        
    # Fallback to off-chain APIs
    return get_offchain_price(token_symbol)


def get_price_usd_by_chain_id(token_symbol: str, chain_id: int) -> float:
    """
    Get token price in USD by chain ID (convenience wrapper).
    
    Args:
        token_symbol: Token symbol (e.g., "ETH", "USDC")
        chain_id: Chain ID (e.g., 1 for Ethereum, 137 for Polygon)
        
    Returns:
        Price in USD as float, or 0.0 if unavailable
    """
    # Convert chain ID to chain name
    chain_name = None
    for name, cid in CHAIN_NAME_TO_ID.items():
        if cid == chain_id:
            chain_name = name
            break
            
    if not chain_name:
        logger.warning(f"⚠️ Unknown chain ID: {chain_id}")
        return get_offchain_price(token_symbol)
        
    return get_price_usd(token_symbol, chain_name)


def get_available_feeds(chain: str) -> Dict[str, str]:
    """
    Get all available Chainlink price feeds for a specific chain.
    
    Args:
        chain: Chain name (e.g., "ethereum", "polygon")
        
    Returns:
        Dictionary mapping token symbols to feed addresses
    """
    return CHAINLINK_FEEDS.get(chain, {})


def is_chainlink_feed_available(token_symbol: str, chain: str) -> bool:
    """
    Check if a Chainlink feed is available for a token on a specific chain.
    
    Args:
        token_symbol: Token symbol (e.g., "ETH", "USDC")
        chain: Chain name (e.g., "ethereum", "polygon")
        
    Returns:
        True if feed is available, False otherwise
    """
    token_symbol = token_symbol.upper()
    return chain in CHAINLINK_FEEDS and token_symbol in CHAINLINK_FEEDS[chain]
