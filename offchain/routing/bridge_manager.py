"""
Bridge Manager - Wrapper for bridge functionality
Combines BridgeAggregator and BridgeOracle

Enhanced with centralized token configuration for cross-chain token resolution
"""
from offchain.routing.bridge_aggregator import BridgeAggregator
from offchain.ml.bridge_oracle import BridgeOracle
from offchain.core.token_config import (
    get_token_id_from_address,
    get_canonical_token_address,
    UniversalTokenIds,
    get_all_token_addresses,
    TokenType
)

class BridgeManager:
    """
    Unified bridge management interface with token registry awareness
    """
    
    def __init__(self):
        self.aggregator = BridgeAggregator()
        self.oracle = BridgeOracle()
    
    def get_best_route(self, src_chain, dst_chain, token, amount, user):
        """
        Get best bridge route with token type awareness
        
        Args:
            src_chain: Source chain ID
            dst_chain: Destination chain ID
            token: Token address on source chain
            amount: Amount to bridge
            user: User address
            
        Returns:
            Best bridge route
        """
        # Enhance with token registry info if available
        token_info = get_token_id_from_address(src_chain, token)
        if token_info:
            token_id, token_type = token_info
            # Get destination token address for same token ID
            dst_token = get_canonical_token_address(dst_chain, token_id)
            if dst_token:
                # Include destination token info in route planning
                route = self.aggregator.get_best_route(src_chain, dst_chain, token, amount, user)
                if route:
                    route['token_id'] = token_id
                    route['dst_token'] = dst_token
                return route
        
        return self.aggregator.get_best_route(src_chain, dst_chain, token, amount, user)
    
    def get_route(self, src_chain, dst_chain, token, amount, user):
        """Alias for get_best_route - used by Brain for backward compatibility"""
        return self.get_best_route(src_chain, dst_chain, token, amount, user)
    
    def estimate_fee(self, from_chain, to_chain, token, amount):
        """
        Estimate bridge fee with token type consideration
        """
        return self.oracle.estimate_bridge_fee(from_chain, to_chain, token, amount)
    
    def is_profitable(self, from_chain, to_chain, token, amount, expected_diff):
        """
        Check if bridge is profitable
        """
        return self.oracle.is_bridge_profitable(from_chain, to_chain, token, amount, expected_diff)
    
    def get_equivalent_token(self, src_chain, dst_chain, token_address):
        """
        Find the equivalent token on destination chain
        
        Args:
            src_chain: Source chain ID
            dst_chain: Destination chain ID
            token_address: Token address on source chain
            
        Returns:
            Equivalent token address on destination chain or None
        """
        token_info = get_token_id_from_address(src_chain, token_address)
        if token_info:
            token_id, _ = token_info
            return get_canonical_token_address(dst_chain, token_id)
        return None
    
    def is_bridgeable_token(self, chain_id, token_address):
        """
        Check if a token can be bridged (exists in universal token set)
        
        Args:
            chain_id: Chain ID
            token_address: Token address
            
        Returns:
            bool: True if token is bridgeable
        """
        token_info = get_token_id_from_address(chain_id, token_address)
        if token_info:
            token_id, _ = token_info
            # Universal tokens are bridgeable
            return token_id <= UniversalTokenIds.WETH
        return False
