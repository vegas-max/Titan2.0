"""
Direct DEX Pool Query Module
Query pool state directly without aggregators for maximum precision and speed
Supports: Uniswap V2/V3, Curve, Balancer, QuickSwap
"""

import logging
from web3 import Web3
from typing import Dict, Optional, Tuple, List
from decimal import Decimal, getcontext
from eth_abi import decode

logger = logging.getLogger("DirectDEXQuery")
getcontext().prec = 28

# ABIs for direct pool queries
UNIV2_PAIR_ABI = [
    {
        "inputs": [],
        "name": "getReserves",
        "outputs": [
            {"name": "reserve0", "type": "uint112"},
            {"name": "reserve1", "type": "uint112"},
            {"name": "blockTimestampLast", "type": "uint32"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "token0",
        "outputs": [{"name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "token1",
        "outputs": [{"name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    }
]

UNIV3_POOL_ABI = [
    {
        "inputs": [],
        "name": "slot0",
        "outputs": [
            {"name": "sqrtPriceX96", "type": "uint160"},
            {"name": "tick", "type": "int24"},
            {"name": "observationIndex", "type": "uint16"},
            {"name": "observationCardinality", "type": "uint16"},
            {"name": "observationCardinalityNext", "type": "uint16"},
            {"name": "feeProtocol", "type": "uint8"},
            {"name": "unlocked", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "liquidity",
        "outputs": [{"name": "", "type": "uint128"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "fee",
        "outputs": [{"name": "", "type": "uint24"}],
        "stateMutability": "view",
        "type": "function"
    }
]

CURVE_POOL_ABI = [
    {
        "inputs": [{"name": "i", "type": "uint256"}],
        "name": "balances",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "i", "type": "int128"},
            {"name": "j", "type": "int128"},
            {"name": "dx", "type": "uint256"}
        ],
        "name": "get_dy",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "A",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

BALANCER_VAULT_ABI = [
    {
        "inputs": [{"name": "poolId", "type": "bytes32"}],
        "name": "getPoolTokens",
        "outputs": [
            {"name": "tokens", "type": "address[]"},
            {"name": "balances", "type": "uint256[]"},
            {"name": "lastChangeBlock", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]


class DirectDEXQuery:
    """
    Direct DEX pool state queries without aggregators
    """
    
    def __init__(self, web3_connections: Dict[int, Web3]):
        self.web3 = web3_connections
        self.pool_cache = {}
        self.cache_duration = 5  # Cache pool state for 5 seconds
        
    def query_uniswap_v2_pool(
        self,
        chain_id: int,
        pool_address: str,
        token_in: str,
        amount_in: int
    ) -> Optional[Dict]:
        """
        Query Uniswap V2 (and forks) pool directly
        
        Args:
            chain_id: Chain ID
            pool_address: Pool/Pair address
            token_in: Input token address
            amount_in: Amount to swap
            
        Returns:
            Dictionary with reserves, price, and estimated output
        """
        try:
            w3 = self.web3.get(chain_id)
            if not w3:
                return None
            
            # Create contract instance
            pair_contract = w3.eth.contract(
                address=Web3.to_checksum_address(pool_address),
                abi=UNIV2_PAIR_ABI
            )
            
            # Get reserves
            reserves = pair_contract.functions.getReserves().call()
            reserve0 = reserves[0]
            reserve1 = reserves[1]
            
            # Get token addresses
            token0 = pair_contract.functions.token0().call()
            token1 = pair_contract.functions.token1().call()
            
            # Determine which token is which
            if token_in.lower() == token0.lower():
                reserve_in = reserve0
                reserve_out = reserve1
            elif token_in.lower() == token1.lower():
                reserve_in = reserve1
                reserve_out = reserve0
            else:
                logger.error(f"Token {token_in} not in pool {pool_address}")
                return None
            
            # Calculate output using constant product formula
            # amount_out = (amount_in * 997 * reserve_out) / (reserve_in * 1000 + amount_in * 997)
            # 997/1000 = 0.3% fee
            
            amount_in_with_fee = amount_in * 997
            numerator = amount_in_with_fee * reserve_out
            denominator = (reserve_in * 1000) + amount_in_with_fee
            amount_out = numerator // denominator
            
            # Calculate price
            price = Decimal(reserve_out) / Decimal(reserve_in)
            
            # Calculate price impact
            price_impact = (Decimal(amount_in) / Decimal(reserve_in)) * Decimal('100')
            
            logger.info(f"📊 UniV2 Pool {pool_address[:8]}...")
            logger.info(f"   Reserves: {reserve_in / 1e18:.2f} / {reserve_out / 1e18:.2f}")
            logger.info(f"   Price: {price}")
            logger.info(f"   Impact: {price_impact}%")
            logger.info(f"   Output: {amount_out}")
            
            return {
                'pool_address': pool_address,
                'pool_type': 'uniswap_v2',
                'reserve_in': reserve_in,
                'reserve_out': reserve_out,
                'price': float(price),
                'amount_out': amount_out,
                'price_impact': float(price_impact),
                'fee': 0.003  # 0.3%
            }
            
        except Exception as e:
            logger.error(f"Failed to query Uniswap V2 pool: {e}")
            return None
    
    def query_uniswap_v3_pool(
        self,
        chain_id: int,
        pool_address: str
    ) -> Optional[Dict]:
        """
        Query Uniswap V3 pool state
        
        Args:
            chain_id: Chain ID
            pool_address: Pool address
            
        Returns:
            Dictionary with pool state
        """
        try:
            w3 = self.web3.get(chain_id)
            if not w3:
                return None
            
            # Create contract instance
            pool_contract = w3.eth.contract(
                address=Web3.to_checksum_address(pool_address),
                abi=UNIV3_POOL_ABI
            )
            
            # Get slot0 (current price)
            slot0 = pool_contract.functions.slot0().call()
            sqrt_price_x96 = slot0[0]
            current_tick = slot0[1]
            
            # Get liquidity
            liquidity = pool_contract.functions.liquidity().call()
            
            # Get fee tier
            fee = pool_contract.functions.fee().call()
            
            # Calculate actual price from sqrtPriceX96
            # price = (sqrtPriceX96 / 2^96) ^ 2
            price = (Decimal(sqrt_price_x96) / Decimal(2 ** 96)) ** 2
            
            logger.info(f"📊 UniV3 Pool {pool_address[:8]}...")
            logger.info(f"   Price: {price}")
            logger.info(f"   Liquidity: {liquidity}")
            logger.info(f"   Fee: {fee / 10000}%")
            logger.info(f"   Tick: {current_tick}")
            
            return {
                'pool_address': pool_address,
                'pool_type': 'uniswap_v3',
                'sqrt_price_x96': sqrt_price_x96,
                'tick': current_tick,
                'liquidity': liquidity,
                'fee': fee,
                'price': float(price)
            }
            
        except Exception as e:
            logger.error(f"Failed to query Uniswap V3 pool: {e}")
            return None
    
    def query_curve_pool(
        self,
        chain_id: int,
        pool_address: str,
        token_in_index: int,
        token_out_index: int,
        amount_in: int
    ) -> Optional[Dict]:
        """
        Query Curve pool directly
        
        Args:
            chain_id: Chain ID
            pool_address: Pool address
            token_in_index: Index of input token in pool
            token_out_index: Index of output token in pool
            amount_in: Amount to swap
            
        Returns:
            Dictionary with pool state and quote
        """
        try:
            w3 = self.web3.get(chain_id)
            if not w3:
                return None
            
            # Create contract instance
            pool_contract = w3.eth.contract(
                address=Web3.to_checksum_address(pool_address),
                abi=CURVE_POOL_ABI
            )
            
            # Get balances
            balance_in = pool_contract.functions.balances(token_in_index).call()
            balance_out = pool_contract.functions.balances(token_out_index).call()
            
            # Get amplification coefficient
            try:
                amp = pool_contract.functions.A().call()
            except:
                amp = 0  # Some pools don't expose this
            
            # Get quote for swap
            amount_out = pool_contract.functions.get_dy(
                token_in_index,
                token_out_index,
                amount_in
            ).call()
            
            # Calculate price
            price = Decimal(balance_out) / Decimal(balance_in)
            
            # Calculate price impact
            price_impact = (Decimal(amount_in) / Decimal(balance_in)) * Decimal('100')
            
            logger.info(f"📊 Curve Pool {pool_address[:8]}...")
            logger.info(f"   Balances: {balance_in / 1e18:.2f} / {balance_out / 1e18:.2f}")
            logger.info(f"   Amp: {amp}")
            logger.info(f"   Price: {price}")
            logger.info(f"   Impact: {price_impact}%")
            logger.info(f"   Output: {amount_out}")
            
            return {
                'pool_address': pool_address,
                'pool_type': 'curve',
                'balance_in': balance_in,
                'balance_out': balance_out,
                'amp': amp,
                'price': float(price),
                'amount_out': amount_out,
                'price_impact': float(price_impact),
                'fee': 0.0004  # 0.04% typical
            }
            
        except Exception as e:
            logger.error(f"Failed to query Curve pool: {e}")
            return None
    
    def query_balancer_pool(
        self,
        chain_id: int,
        vault_address: str,
        pool_id: str
    ) -> Optional[Dict]:
        """
        Query Balancer pool via Vault
        
        Args:
            chain_id: Chain ID
            vault_address: Balancer Vault address
            pool_id: Pool ID (bytes32)
            
        Returns:
            Dictionary with pool tokens and balances
        """
        try:
            w3 = self.web3.get(chain_id)
            if not w3:
                return None
            
            # Create vault contract instance
            vault_contract = w3.eth.contract(
                address=Web3.to_checksum_address(vault_address),
                abi=BALANCER_VAULT_ABI
            )
            
            # Get pool tokens and balances
            pool_data = vault_contract.functions.getPoolTokens(pool_id).call()
            
            tokens = pool_data[0]
            balances = pool_data[1]
            last_change_block = pool_data[2]
            
            logger.info(f"📊 Balancer Pool {pool_id[:8]}...")
            logger.info(f"   Tokens: {len(tokens)}")
            logger.info(f"   Balances: {[b / 1e18 for b in balances]}")
            logger.info(f"   Last Change: Block {last_change_block}")
            
            return {
                'pool_id': pool_id,
                'pool_type': 'balancer',
                'tokens': tokens,
                'balances': balances,
                'last_change_block': last_change_block,
                'fee': 0.001  # Varies by pool
            }
            
        except Exception as e:
            logger.error(f"Failed to query Balancer pool: {e}")
            return None
    
    def get_best_pool_for_pair(
        self,
        chain_id: int,
        token_in: str,
        token_out: str,
        amount_in: int,
        pools: List[Dict]
    ) -> Optional[Dict]:
        """
        Query multiple pools and find the best one for a swap
        
        Args:
            chain_id: Chain ID
            token_in: Input token address
            token_out: Output token address
            amount_in: Amount to swap
            pools: List of pool dictionaries with 'address' and 'type'
            
        Returns:
            Best pool with quote information
        """
        best_pool = None
        best_output = 0
        
        for pool_info in pools:
            pool_address = pool_info['address']
            pool_type = pool_info['type']
            
            result = None
            
            if pool_type == 'uniswap_v2':
                result = self.query_uniswap_v2_pool(
                    chain_id, pool_address, token_in, amount_in
                )
            elif pool_type == 'uniswap_v3':
                # For V3, need quoter contract (not implemented here)
                logger.warning("UniV3 quote requires quoter contract")
                continue
            elif pool_type == 'curve':
                # Need token indices (not provided here)
                logger.warning("Curve quote requires token indices")
                continue
            
            if result and result.get('amount_out', 0) > best_output:
                best_output = result['amount_out']
                best_pool = result
        
        if best_pool:
            logger.info(f"🎯 Best pool: {best_pool['pool_address'][:8]}... with output {best_output}")
        
        return best_pool
    
    def batch_query_pools(
        self,
        chain_id: int,
        queries: List[Dict]
    ) -> List[Optional[Dict]]:
        """
        Batch query multiple pools
        
        Args:
            chain_id: Chain ID
            queries: List of query dictionaries
            
        Returns:
            List of results
        """
        results = []
        
        for query in queries:
            pool_type = query['type']
            pool_address = query['address']
            
            if pool_type == 'uniswap_v2':
                result = self.query_uniswap_v2_pool(
                    chain_id,
                    pool_address,
                    query['token_in'],
                    query['amount_in']
                )
            elif pool_type == 'uniswap_v3':
                result = self.query_uniswap_v3_pool(chain_id, pool_address)
            elif pool_type == 'curve':
                result = self.query_curve_pool(
                    chain_id,
                    pool_address,
                    query.get('token_in_index', 0),
                    query.get('token_out_index', 1),
                    query['amount_in']
                )
            else:
                result = None
            
            results.append(result)
        
        return results
