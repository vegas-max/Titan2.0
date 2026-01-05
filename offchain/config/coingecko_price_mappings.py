"""
CoinGecko Price Mapping Module for Polygon Token Universe
Provides USD price normalization via CoinGecko API integration

This module maps token addresses to CoinGecko IDs for real-time price feeds,
enabling accurate USD value calculations for arbitrage profit estimation.

Usage:
    from offchain.config.coingecko_price_mappings import get_coingecko_id, COINGECKO_ID_MAP
    
    token_address = "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270"
    cg_id = get_coingecko_id(token_address)  # Returns: 'matic-network'
"""

from typing import Dict, Optional

# Map token addresses (lowercase) to CoinGecko IDs for USD price normalization
# All addresses are checksummed originals but stored in lowercase for case-insensitive lookups
COINGECKO_ID_MAP: Dict[str, str] = {
    # Core Stablecoins
    "0x2791bca1f2de4661ed88a30c99a7a9449aa84174": "usd-coin",  # USDC (Bridged)
    "0x3c499c542cef5e3811e1192ce70d8cc03d5c3359": "usd-coin",  # USDC.e (Native)
    "0xc2132d05d31c914a87c6611c10748aeb04b58e8f": "tether",    # USDT
    "0x8f3cf7ad23cd3cadbd9735aff958023239c6a063": "dai",       # DAI
    "0x45c32fa6df82ead1e2ef74d17b76547eddfaff89": "frax",      # FRAX
    
    # Native Gas & Core Liquidity
    "0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270": "matic-network",      # WMATIC
    "0x7ceb23fd6bc0add59e62ac25578270cff1b9f619": "weth",               # WETH
    "0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6": "wrapped-bitcoin",    # WBTC
    
    # DEX-Native Governance Tokens
    "0xb5c064f955d8e7f38fe0460c556a72987494ee17": "quick",             # QUICK (QuickSwap)
    "0x0b3f868e0be5597d5db7feb59e1cadbb0fdda50a": "sushi",             # SUSHI (SushiSwap)
    "0x9a71012b13ca4d3d0cdc72a177df3ef03b0e76a3": "balancer",          # BAL (Balancer)
    
    # Major DeFi Protocols
    "0xd6df932a45c0f255f85145f286ea0b292b21c90b": "aave",              # AAVE
    "0x172370d5cd63279efa6d502dab29171933a610af": "curve-dao-token",   # CRV
    "0xb33eaad8d922b1083446dc23f610c2567fb5180f": "uniswap",           # UNI
    "0x53e0bca35ec356bd5dddfebbd1fc0fd03fabad39": "chainlink",         # LINK
    
    # High-Volume Altcoins
    "0x8505b9d2254a7ae468c0e9dd10ccea3a837aef5c": "compound-governance-token",  # COMP
    "0x50b728d8d964fd00c2d0aad81718b71311fef68a": "havven",                     # SNX
    "0xc3c7d422809852031b44ab29eec9f1eff2a58756": "lido-dao",                   # LDO
    "0xa1c57f48f0deb89f569dfbe6e2b7f46d33606fd4": "decentraland",               # MANA
    "0x7227e371540cf7b8e512544ba6871472031f3335": "enjincoin",                  # ENJ
    "0xdbf31df14b66535af65aac99c32e9ea844e14501": "republic-protocol",          # REN
    "0x0d8775f648430679a709e98d2b0cb6250d2887ef": "basic-attention-token",      # BAT
    
    # Liquid Staking Derivatives
    "0x3a58a54c066fdc0f2d55fc9c89f0415c92ebf3c4": "lido-staked-matic",  # stMATIC (Lido)
    "0xfa68fb4628dff1028cfec22b4162fccd0d45efb6": "stader-maticx",      # MaticX (Stader)
    
    # Specialized Stablecoins
    "0xa3fa99a148fa48d14ed51d610c367c61876997f1": "mimatic",     # MAI (QiDAO)
    "0xffa4d863c96e743a2e1513824ea006b8d0353c57": "usdd",        # USDD
    "0xe0b52e49357fd4daf2c15e02058dce6bc0057db4": "ageur",       # agEUR (Angle Protocol)
    
    # Polygon-Native Ecosystem
    "0x385eeac5cb85a38a9a07a70c73e0a3271cfb54a7": "aavegotchi",    # GHST (Aavegotchi)
    "0xbbba073c31bf03b8acf7c28ef0738decf3695683": "the-sandbox",   # SAND (The Sandbox)
}

# Reverse mapping: CoinGecko ID to token symbols (for reference)
COINGECKO_TO_SYMBOL: Dict[str, str] = {
    "matic-network": "WMATIC",
    "weth": "WETH",
    "usd-coin": "USDC/USDC.e",
    "tether": "USDT",
    "dai": "DAI",
    "wrapped-bitcoin": "WBTC",
    "chainlink": "LINK",
    "aave": "AAVE",
    "uniswap": "UNI",
    "quick": "QUICK",
    "sushi": "SUSHI",
    "curve-dao-token": "CRV",
    "balancer": "BAL",
    "the-sandbox": "SAND",
    "decentraland": "MANA",
    "frax": "FRAX",
    "compound-governance-token": "COMP",
    "havven": "SNX",
    "lido-dao": "LDO",
    "enjincoin": "ENJ",
    "republic-protocol": "REN",
    "basic-attention-token": "BAT",
    "lido-staked-matic": "stMATIC",
    "stader-maticx": "MaticX",
    "mimatic": "MAI",
    "usdd": "USDD",
    "ageur": "agEUR",
    "aavegotchi": "GHST",
}


def get_coingecko_id(token_address: str) -> Optional[str]:
    """
    Get CoinGecko ID for a given token address.
    
    Args:
        token_address: Token contract address (case-insensitive)
        
    Returns:
        CoinGecko ID string if found, None otherwise
        
    Example:
        >>> get_coingecko_id("0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270")
        'matic-network'
    """
    return COINGECKO_ID_MAP.get(token_address.lower())


def get_symbol_from_coingecko_id(coingecko_id: str) -> Optional[str]:
    """
    Get token symbol(s) from CoinGecko ID.
    
    Args:
        coingecko_id: CoinGecko ID string
        
    Returns:
        Token symbol(s) if found, None otherwise
        
    Example:
        >>> get_symbol_from_coingecko_id("matic-network")
        'WMATIC'
    """
    return COINGECKO_TO_SYMBOL.get(coingecko_id)


def get_all_coingecko_ids() -> list[str]:
    """
    Get list of all unique CoinGecko IDs in the mapping.
    
    Returns:
        List of CoinGecko ID strings
    """
    return list(set(COINGECKO_ID_MAP.values()))


def get_tokens_with_coingecko_support() -> list[str]:
    """
    Get list of all token addresses that have CoinGecko price support.
    
    Returns:
        List of token addresses (lowercase)
    """
    return list(COINGECKO_ID_MAP.keys())


# CoinGecko API endpoint templates
COINGECKO_API_BASE = "https://api.coingecko.com/api/v3"
COINGECKO_SIMPLE_PRICE_ENDPOINT = f"{COINGECKO_API_BASE}/simple/price"


def build_coingecko_price_url(token_addresses: list[str], vs_currencies: list[str] = ["usd"]) -> str:
    """
    Build CoinGecko API URL for fetching multiple token prices.
    
    Args:
        token_addresses: List of token addresses to fetch prices for
        vs_currencies: List of currencies to get prices in (default: ["usd"])
        
    Returns:
        CoinGecko API URL string
        
    Example:
        >>> url = build_coingecko_price_url(
        ...     ["0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270"],
        ...     ["usd"]
        ... )
        >>> print(url)
        https://api.coingecko.com/api/v3/simple/price?ids=matic-network&vs_currencies=usd
    """
    # Convert addresses to CoinGecko IDs
    cg_ids = []
    for addr in token_addresses:
        cg_id = get_coingecko_id(addr)
        if cg_id:
            cg_ids.append(cg_id)
    
    # Remove duplicates (e.g., USDC and USDC.e both map to 'usd-coin')
    cg_ids = list(set(cg_ids))
    
    # Build URL
    ids_param = ",".join(cg_ids)
    vs_param = ",".join(vs_currencies)
    
    return f"{COINGECKO_SIMPLE_PRICE_ENDPOINT}?ids={ids_param}&vs_currencies={vs_param}"


# Export all public functions and constants
__all__ = [
    "COINGECKO_ID_MAP",
    "COINGECKO_TO_SYMBOL",
    "COINGECKO_API_BASE",
    "COINGECKO_SIMPLE_PRICE_ENDPOINT",
    "get_coingecko_id",
    "get_symbol_from_coingecko_id",
    "get_all_coingecko_ids",
    "get_tokens_with_coingecko_support",
    "build_coingecko_price_url",
]
