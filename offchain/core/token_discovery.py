"""
Token Discovery Module - Multi-chain token inventory and bridge-compatible asset detection

This module now integrates with the centralized token_config system for consistent
token management across the entire platform.
"""

from offchain.core.token_config import (
    CHAIN_CONFIGS,
    TokenType,
    UniversalTokenIds,
    ChainTokenIds,
    get_chain_tokens,
    get_token_address,
    get_canonical_token_address,
    get_all_token_addresses,
    is_token_registered
)


def _get_default_decimals(symbol: str) -> int:
    """Get default decimals for a token symbol"""
    if symbol in ["USDC", "USDT"]:
        return 6
    elif symbol in ["WBTC"]:
        return 8
    else:
        return 18


def _add_legacy_mappings(registry):
    """Add legacy token mappings for backward compatibility"""
    # Polygon specific
    if 137 in registry:
        if "WNATIVE" in registry[137]:
            # Alias WNATIVE as WMATIC on Polygon
            registry[137]["WMATIC"] = registry[137]["WNATIVE"].copy()
        # Add native MATIC placeholder
        registry[137]["MATIC"] = {
            "address": "0x0000000000000000000000000000000000001010",
            "decimals": 18,
            "native": True
        }


def _build_token_registry():
    """Build token registry from centralized configuration"""
    registry = {}
    
    for chain_id, config in CHAIN_CONFIGS.items():
        registry[chain_id] = {}
        tokens = config.get("tokens", [])
        
        for token in tokens:
            # Get symbol from token ID
            symbol = None
            for name, member in UniversalTokenIds.__members__.items():
                if member.value == token.id:
                    symbol = name
                    break
            if not symbol:
                for name, member in ChainTokenIds.__members__.items():
                    if member.value == token.id:
                        symbol = name
                        break
            
            if symbol:
                # Store canonical/wrapped tokens, prefer canonical
                if symbol not in registry[chain_id] or token.type == TokenType.CANONICAL:
                    registry[chain_id][symbol] = {
                        "address": token.address,
                        "decimals": _get_default_decimals(symbol),
                        "token_id": token.id,
                        "token_type": token.type
                    }
    
    # Add legacy mappings for backward compatibility
    _add_legacy_mappings(registry)
    
    return registry


class TokenDiscovery:
    """
    Manages token inventory across multiple chains and identifies bridge-compatible assets.
    Now enhanced with centralized token configuration system.
    """
    
    # Tokens that exist on multiple chains and can be bridged
    BRIDGE_ASSETS = [
        "USDC", "USDT", "DAI", "WETH", "WBTC", 
        "LINK", "UNI", "AAVE", "MATIC", "FRAX"
    ]
    
    # Build the registry at module load time using module-level function
    TOKEN_REGISTRY = _build_token_registry()
    
    @classmethod
    def fetch_all_chains(cls, chain_ids):
        """
        Fetches token inventory for specified chains.
        
        Args:
            chain_ids (list): List of chain IDs to fetch tokens for
            
        Returns:
            dict: Nested dictionary {chain_id: {symbol: {address, decimals}}}
        """
        inventory = {}
        
        for chain_id in chain_ids:
            if chain_id in cls.TOKEN_REGISTRY:
                inventory[chain_id] = cls.TOKEN_REGISTRY[chain_id]
            else:
                # Return empty dict for unconfigured chains
                inventory[chain_id] = {}
        
        return inventory
    
    @classmethod
    def get_token_address(cls, chain_id, symbol):
        """
        Get token address for a specific chain and symbol.
        
        Args:
            chain_id (int): Chain ID
            symbol (str): Token symbol (e.g., "USDC")
            
        Returns:
            str: Token address or None if not found
        """
        if chain_id in cls.TOKEN_REGISTRY:
            token_data = cls.TOKEN_REGISTRY[chain_id].get(symbol)
            if token_data:
                return token_data["address"]
        return None
    
    @classmethod
    def get_token_decimals(cls, chain_id, symbol):
        """
        Get token decimals for a specific chain and symbol.
        
        Args:
            chain_id (int): Chain ID
            symbol (str): Token symbol (e.g., "USDC")
            
        Returns:
            int: Token decimals or 18 (default) if not found
        """
        if chain_id in cls.TOKEN_REGISTRY:
            token_data = cls.TOKEN_REGISTRY[chain_id].get(symbol)
            if token_data:
                return token_data["decimals"]
        return 18  # Default to 18 decimals
    
    @classmethod
    def get_token_id(cls, chain_id, symbol):
        """
        Get token ID for registry-based encoding
        
        Args:
            chain_id (int): Chain ID
            symbol (str): Token symbol
            
        Returns:
            int: Token ID or None if not found
        """
        if chain_id in cls.TOKEN_REGISTRY:
            token_data = cls.TOKEN_REGISTRY[chain_id].get(symbol)
            if token_data and "token_id" in token_data:
                return token_data["token_id"]
        return None
    
    @classmethod
    def get_token_type(cls, chain_id, symbol):
        """
        Get token type for a specific token
        
        Args:
            chain_id (int): Chain ID
            symbol (str): Token symbol
            
        Returns:
            TokenType: Token type or None if not found
        """
        if chain_id in cls.TOKEN_REGISTRY:
            token_data = cls.TOKEN_REGISTRY[chain_id].get(symbol)
            if token_data and "token_type" in token_data:
                return token_data["token_type"]
        return None
    
    @classmethod
    def is_registered_token(cls, chain_id, address):
        """
        Check if a token address is in the centralized registry
        
        Args:
            chain_id (int): Chain ID
            address (str): Token address
            
        Returns:
            bool: True if registered, False otherwise
        """
        return is_token_registered(chain_id, address)
    
    @classmethod
    def get_all_token_variants(cls, chain_id, symbol):
        """
        Get all variants (CANONICAL, BRIDGED, WRAPPED) of a token
        
        Args:
            chain_id (int): Chain ID
            symbol (str): Token symbol
            
        Returns:
            list: List of (address, type) tuples
        """
        # Map symbol to token ID
        token_id = cls.get_token_id(chain_id, symbol)
        if token_id is not None:
            return get_all_token_addresses(chain_id, token_id)
        return []
