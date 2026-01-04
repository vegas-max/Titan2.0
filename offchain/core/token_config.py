"""
Centralized Token Configuration System

This module provides a single source of truth for token addresses, IDs, and types
across all supported chains. It enables consistent token handling throughout the system.

Token ID Convention:
- 0-10: Universal tokens (consistent across chains)
- 11-50: Chain-specific tokens
- 51-255: Available for expansion
"""

from enum import IntEnum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


class TokenType(IntEnum):
    """Token Type enum (matches Solidity enum)"""
    CANONICAL = 0  # Native to the chain
    BRIDGED = 1    # Bridged version (e.g., USDC.e)
    WRAPPED = 2    # Wrapped native (WETH, WMATIC, etc.)


class UniversalTokenIds(IntEnum):
    """Universal token IDs (consistent across chains)"""
    WNATIVE = 0   # Wrapped native token
    USDC = 1      # USD Coin
    USDT = 2      # Tether USD
    DAI = 3       # Dai Stablecoin
    WBTC = 4      # Wrapped Bitcoin
    WETH = 5      # Wrapped Ether (for non-Ethereum chains)


class ChainTokenIds(IntEnum):
    """Chain-specific token IDs (11-50)"""
    UNI = 11
    LINK = 12
    AAVE = 13
    CRV = 14
    SUSHI = 15
    BAL = 16
    QUICK = 17    # QuickSwap (Polygon)
    GHST = 18     # Aavegotchi (Polygon)
    OP = 19       # Optimism
    ARB = 20      # Arbitrum
    AVAX = 21     # Avalanche
    FTM = 22      # Fantom


@dataclass
class TokenConfig:
    """Token configuration data class"""
    id: int
    type: TokenType
    address: str


# Token configurations per chain
CHAIN_CONFIGS: Dict[int, Dict[str, List[TokenConfig]]] = {
    # Ethereum (Chain ID 1)
    1: {
        "tokens": [
            TokenConfig(id=UniversalTokenIds.WETH, type=TokenType.WRAPPED, address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
            TokenConfig(id=UniversalTokenIds.USDC, type=TokenType.CANONICAL, address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"),
            TokenConfig(id=UniversalTokenIds.USDT, type=TokenType.CANONICAL, address="0xdAC17F958D2ee523a2206206994597C13D831ec7"),
            TokenConfig(id=UniversalTokenIds.DAI, type=TokenType.CANONICAL, address="0x6B175474E89094C44Da98b954EedeAC495271d0F"),
            TokenConfig(id=UniversalTokenIds.WBTC, type=TokenType.CANONICAL, address="0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"),
            TokenConfig(id=ChainTokenIds.UNI, type=TokenType.CANONICAL, address="0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"),
            TokenConfig(id=ChainTokenIds.LINK, type=TokenType.CANONICAL, address="0x514910771AF9Ca656af840dff83E8264EcF986CA"),
            TokenConfig(id=ChainTokenIds.AAVE, type=TokenType.CANONICAL, address="0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9"),
        ]
    },
    
    # Polygon (Chain ID 137)
    137: {
        "tokens": [
            TokenConfig(id=UniversalTokenIds.WNATIVE, type=TokenType.WRAPPED, address="0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270"),  # WMATIC
            TokenConfig(id=UniversalTokenIds.USDC, type=TokenType.CANONICAL, address="0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"),
            TokenConfig(id=UniversalTokenIds.USDC, type=TokenType.BRIDGED, address="0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"),  # USDC.e
            TokenConfig(id=UniversalTokenIds.USDT, type=TokenType.CANONICAL, address="0xc2132D05D31c914a87C6611C10748AEb04B58e8F"),
            TokenConfig(id=UniversalTokenIds.DAI, type=TokenType.CANONICAL, address="0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063"),
            TokenConfig(id=UniversalTokenIds.WBTC, type=TokenType.CANONICAL, address="0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6"),
            TokenConfig(id=UniversalTokenIds.WETH, type=TokenType.BRIDGED, address="0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619"),
            TokenConfig(id=ChainTokenIds.QUICK, type=TokenType.CANONICAL, address="0xB5C064F955D8e7F38fE0460C556a72987494eE17"),
            TokenConfig(id=ChainTokenIds.GHST, type=TokenType.CANONICAL, address="0x385Eeac5cB85A38A9a07A70c73e0a3271CfB54A7"),
        ]
    },
    
    # Arbitrum (Chain ID 42161)
    42161: {
        "tokens": [
            TokenConfig(id=UniversalTokenIds.WETH, type=TokenType.WRAPPED, address="0x82aF49447D8a07e3bd95BD0d56f35241523fBab1"),
            TokenConfig(id=UniversalTokenIds.USDC, type=TokenType.CANONICAL, address="0xaf88d065e77c8cC2239327C5EDb3A432268e5831"),
            TokenConfig(id=UniversalTokenIds.USDC, type=TokenType.BRIDGED, address="0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8"),  # USDC.e
            TokenConfig(id=UniversalTokenIds.USDT, type=TokenType.CANONICAL, address="0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9"),
            TokenConfig(id=UniversalTokenIds.DAI, type=TokenType.CANONICAL, address="0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1"),
            TokenConfig(id=UniversalTokenIds.WBTC, type=TokenType.CANONICAL, address="0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f"),
            TokenConfig(id=ChainTokenIds.ARB, type=TokenType.CANONICAL, address="0x912CE59144191C1204E64559FE8253a0e49E6548"),
        ]
    },
    
    # Optimism (Chain ID 10)
    10: {
        "tokens": [
            TokenConfig(id=UniversalTokenIds.WETH, type=TokenType.WRAPPED, address="0x4200000000000000000000000000000000000006"),
            TokenConfig(id=UniversalTokenIds.USDC, type=TokenType.CANONICAL, address="0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85"),
            TokenConfig(id=UniversalTokenIds.USDC, type=TokenType.BRIDGED, address="0x7F5c764cBc14f9669B88837ca1490cCa17c31607"),  # USDC.e
            TokenConfig(id=UniversalTokenIds.USDT, type=TokenType.CANONICAL, address="0x94b008aA00579c1307B0EF2c499aD98a8ce58e58"),
            TokenConfig(id=UniversalTokenIds.DAI, type=TokenType.CANONICAL, address="0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1"),
            TokenConfig(id=UniversalTokenIds.WBTC, type=TokenType.CANONICAL, address="0x68f180fcCe6836688e9084f035309E29Bf0A2095"),
            TokenConfig(id=ChainTokenIds.OP, type=TokenType.CANONICAL, address="0x4200000000000000000000000000000000000042"),
        ]
    },
    
    # Base (Chain ID 8453)
    8453: {
        "tokens": [
            TokenConfig(id=UniversalTokenIds.WETH, type=TokenType.WRAPPED, address="0x4200000000000000000000000000000000000006"),
            TokenConfig(id=UniversalTokenIds.USDC, type=TokenType.CANONICAL, address="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"),
            TokenConfig(id=UniversalTokenIds.USDC, type=TokenType.BRIDGED, address="0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA"),  # USDbC
            TokenConfig(id=UniversalTokenIds.DAI, type=TokenType.CANONICAL, address="0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb"),
        ]
    }
}


def get_chain_tokens(chain_id: int) -> List[TokenConfig]:
    """
    Get all tokens for a specific chain
    
    Args:
        chain_id: EIP-155 Chain ID
        
    Returns:
        List of token configurations
    """
    config = CHAIN_CONFIGS.get(chain_id, {})
    return config.get("tokens", [])


def get_token_address(chain_id: int, token_id: int, token_type: TokenType = TokenType.CANONICAL) -> Optional[str]:
    """
    Get token address by ID and type
    
    Args:
        chain_id: EIP-155 Chain ID
        token_id: Token ID (0-255)
        token_type: Token type (CANONICAL, BRIDGED, WRAPPED)
        
    Returns:
        Token address or None if not found
    """
    tokens = get_chain_tokens(chain_id)
    for token in tokens:
        if token.id == token_id and token.type == token_type:
            return token.address
    return None


def get_token_id_from_address(chain_id: int, address: str) -> Optional[Tuple[int, TokenType]]:
    """
    Get token ID and type from address
    
    Args:
        chain_id: EIP-155 Chain ID
        address: Token address
        
    Returns:
        Tuple of (id, type) or None if not found
    """
    tokens = get_chain_tokens(chain_id)
    normalized_address = address.lower()
    for token in tokens:
        if token.address.lower() == normalized_address:
            return (token.id, token.type)
    return None


def get_all_token_addresses(chain_id: int, token_id: int) -> List[Tuple[str, TokenType]]:
    """
    Get all addresses for a token ID (all types)
    
    Args:
        chain_id: EIP-155 Chain ID
        token_id: Token ID
        
    Returns:
        List of (address, type) tuples
    """
    tokens = get_chain_tokens(chain_id)
    return [(token.address, token.type) for token in tokens if token.id == token_id]


def is_token_registered(chain_id: int, address: str) -> bool:
    """
    Check if a token is registered
    
    Args:
        chain_id: EIP-155 Chain ID
        address: Token address
        
    Returns:
        True if token is registered
    """
    return get_token_id_from_address(chain_id, address) is not None


def get_token_symbol(token_id: int) -> Optional[str]:
    """
    Get token symbol from universal/chain token IDs
    
    Args:
        token_id: Token ID
        
    Returns:
        Token symbol or None
    """
    # Universal tokens
    for name, member in UniversalTokenIds.__members__.items():
        if member.value == token_id:
            return name
    # Chain-specific tokens
    for name, member in ChainTokenIds.__members__.items():
        if member.value == token_id:
            return name
    return None


def get_supported_chains() -> List[int]:
    """
    Get all supported chain IDs
    
    Returns:
        List of chain IDs
    """
    return list(CHAIN_CONFIGS.keys())


def get_canonical_token_address(chain_id: int, token_id: int) -> Optional[str]:
    """
    Get the canonical token address for a token ID (preferred over bridged)
    
    Args:
        chain_id: EIP-155 Chain ID
        token_id: Token ID
        
    Returns:
        Canonical token address or first available address
    """
    addresses = get_all_token_addresses(chain_id, token_id)
    
    # Prefer CANONICAL, then WRAPPED, then BRIDGED
    for addr, token_type in addresses:
        if token_type == TokenType.CANONICAL:
            return addr
    
    for addr, token_type in addresses:
        if token_type == TokenType.WRAPPED:
            return addr
    
    # Return any available
    if addresses:
        return addresses[0][0]
    
    return None
