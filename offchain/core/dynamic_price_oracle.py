"""
Dynamic Price Oracle
Real-time price feeds using Chainlink, DEX TWAPs, and fallback mechanisms
No hardcoded prices - all dynamic and on-chain

Enhanced with integrated chainlink_oracle_feeds module for comprehensive
multi-chain price data with Chainlink → Coingecko → Binance fallback.
"""

import logging
from web3 import Web3
from decimal import Decimal, getcontext
from typing import Dict, Optional, Tuple
import time
from eth_abi import encode

# Import enhanced Chainlink oracle feeds module
try:
    from offchain.core import chainlink_oracle_feeds
    CHAINLINK_ORACLE_AVAILABLE = True
except ImportError:
    CHAINLINK_ORACLE_AVAILABLE = False
    logging.warning("⚠️ chainlink_oracle_feeds module not available, using built-in feeds only")

logger = logging.getLogger("DynamicPriceOracle")
getcontext().prec = 28

# Chainlink Price Feed ABI (simplified)
CHAINLINK_AGGREGATOR_ABI = [
    {
        "inputs": [],
        "name": "latestRoundData",
        "outputs": [
            {"name": "roundId", "type": "uint80"},
            {"name": "answer", "type": "int256"},
            {"name": "startedAt", "type": "uint256"},
            {"name": "updatedAt", "type": "uint256"},
            {"name": "answeredInRound", "type": "uint80"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# Uniswap V3 Pool ABI (for TWAP)
UNIV3_POOL_ABI = [
    {
        "inputs": [{"name": "secondsAgos", "type": "uint32[]"}],
        "name": "observe",
        "outputs": [
            {"name": "tickCumulatives", "type": "int56[]"},
            {"name": "secondsPerLiquidityCumulativeX128s", "type": "uint160[]"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
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
    }
]


class DynamicPriceOracle:
    """
    Dynamic Price Oracle for real-time token pricing
    Priority: Chainlink > Uniswap V3 TWAP > Spot Price
    """
    
    def __init__(self, web3_connections: Dict[int, Web3]):
        self.web3 = web3_connections
        self.chainlink_feeds = self.get_chainlink_feeds()
        self.price_cache = {}
        self.cache_duration = 10  # Cache for 10 seconds
        
    def get_chainlink_feeds(self) -> Dict[int, Dict[str, str]]:
        """
        Chainlink price feed addresses per chain
        Returns: {chainId: {symbol: feed_address}}
        """
        return {
            1: {  # Ethereum
                'ETH/USD': '0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419',
                'BTC/USD': '0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c',
                'USDC/USD': '0x8fFfFfd4AfB6115b954Bd326cbe7B4BA576818f6',
                'USDT/USD': '0x3E7d1eAB13ad0104d2750B8863b489D65364e32D',
                'DAI/USD': '0xAed0c38402a5d19df6E4c03F4E2DceD6e29c1ee9',
                'LINK/USD': '0x2c1d072e956AFFC0D435Cb7AC38EF18d24d9127c',
                'AAVE/USD': '0x547a514d5e3769680Ce22B2361c10Ea13619e8a9',
            },
            137: {  # Polygon
                'MATIC/USD': '0xAB594600376Ec9fD91F8e885dADF0CE036862dE0',
                'ETH/USD': '0xF9680D99D6C9589e2a93a78A04A279e509205945',
                'BTC/USD': '0xc907E116054Ad103354f2D350FD2514433D57F6f',
                'USDC/USD': '0xfE4A8cc5b5B2366C1B58Bea3858e81843581b2F7',
                'USDT/USD': '0x0A6513e40db6EB1b165753AD52E80663aeA50545',
                'DAI/USD': '0x4746DeC9e833A82EC7C2C1356372CcF2cfcD2F3D',
                'LINK/USD': '0xd9FFdb71EbE7496cC440152d43986Aae0AB76665',
                'AAVE/USD': '0x72484B12719E23115761D5DA1646945632979bB6',
            },
            42161: {  # Arbitrum
                'ETH/USD': '0x639Fe6ab55C921f74e7fac1ee960C0B6293ba612',
                'BTC/USD': '0x6ce185860a4963106506C203335A2910413708e9',
                'USDC/USD': '0x50834F3163758fcC1Df9973b6e91f0F0F0434aD3',
                'USDT/USD': '0x3f3f5dF88dC9F13eac63DF89EC16ef6e7E25DdE7',
                'DAI/USD': '0xc5C8E77B397E531B8EC06BFb0048328B30E9eCfB',
                'LINK/USD': '0x86E53CF1B870786351Da77A57575e79CB55812CB',
            },
            10: {  # Optimism
                'ETH/USD': '0x13e3Ee699D1909E989722E753853AE30b17e08c5',
                'BTC/USD': '0xD702DD976Fb76Fffc2D3963D037dfDae5b04E593',
                'USDC/USD': '0x16a9FA2FDa030272Ce99B29CF780dFA30361E0f3',
                'USDT/USD': '0xECef79E109e997bCA29c1c0897ec9d7b03647F5E',
                'DAI/USD': '0x8dBa75e83DA73cc766A7e5a0ee71F656BAb470d6',
                'LINK/USD': '0xCc232dcFAAE6354cE191Bd574108c1aD03f86450',
            },
            8453: {  # Base
                'ETH/USD': '0x71041dddad3595F9CEd3DcCFBe3D1F4b0a16Bb70',
                'USDC/USD': '0x7e860098F58bBFC8648a4311b374B1D669a2bc6B',
            }
        }
    
    def get_price_from_chainlink(
        self,
        chain_id: int,
        token_symbol: str,
        base_currency: str = 'USD'
    ) -> Optional[Tuple[Decimal, int]]:
        """
        Get token price from Chainlink oracle
        Returns: (price, timestamp) or None if not available
        """
        try:
            feed_key = f"{token_symbol}/{base_currency}"
            feeds = self.chainlink_feeds.get(chain_id, {})
            feed_address = feeds.get(feed_key)
            
            if not feed_address:
                logger.debug(f"No Chainlink feed for {feed_key} on chain {chain_id}")
                return None
            
            w3 = self.web3.get(chain_id)
            if not w3:
                logger.error(f"No web3 connection for chain {chain_id}")
                return None
            
            # Create contract instance
            feed_contract = w3.eth.contract(
                address=Web3.to_checksum_address(feed_address),
                abi=CHAINLINK_AGGREGATOR_ABI
            )
            
            # Get latest round data
            round_data = feed_contract.functions.latestRoundData().call()
            decimals = feed_contract.functions.decimals().call()
            
            # Parse data
            answer = round_data[1]  # price
            updated_at = round_data[3]  # timestamp
            
            # Check if data is fresh (within 1 hour)
            if time.time() - updated_at > 3600:
                logger.warning(f"Chainlink data stale for {feed_key}: {time.time() - updated_at}s old")
                return None
            
            # Convert to Decimal with proper decimals
            price = Decimal(answer) / Decimal(10 ** decimals)
            
            logger.info(f"📊 Chainlink price for {feed_key}: ${price}")
            return (price, updated_at)
            
        except Exception as e:
            logger.error(f"Failed to get Chainlink price for {token_symbol}: {e}")
            return None
    
    def get_price_from_uniswap_v3_twap(
        self,
        chain_id: int,
        pool_address: str,
        twap_period: int = 600  # 10 minutes
    ) -> Optional[Decimal]:
        """
        Get TWAP (Time-Weighted Average Price) from Uniswap V3 pool
        Args:
            chain_id: Chain ID
            pool_address: Uniswap V3 pool address
            twap_period: TWAP period in seconds (default 10 minutes)
        Returns: Price as Decimal or None
        """
        try:
            w3 = self.web3.get(chain_id)
            if not w3:
                return None
            
            pool_contract = w3.eth.contract(
                address=Web3.to_checksum_address(pool_address),
                abi=UNIV3_POOL_ABI
            )
            
            # Get tick cumulatives for TWAP calculation
            # We need [twap_period seconds ago, now]
            seconds_agos = [twap_period, 0]
            observe_data = pool_contract.functions.observe(seconds_agos).call()
            
            tick_cumulatives = observe_data[0]
            
            # Calculate average tick over period
            tick_cumulative_delta = tick_cumulatives[1] - tick_cumulatives[0]
            time_delta = twap_period
            
            average_tick = tick_cumulative_delta / time_delta
            
            # Convert tick to price
            # price = 1.0001 ^ tick
            price = Decimal(1.0001) ** Decimal(average_tick)
            
            logger.info(f"📊 Uniswap V3 TWAP ({twap_period}s): {price}")
            return price
            
        except Exception as e:
            logger.error(f"Failed to get Uniswap V3 TWAP: {e}")
            return None
    
    def get_price_from_uniswap_v3_spot(
        self,
        chain_id: int,
        pool_address: str
    ) -> Optional[Decimal]:
        """
        Get spot price from Uniswap V3 pool
        Args:
            chain_id: Chain ID
            pool_address: Uniswap V3 pool address
        Returns: Current spot price as Decimal or None
        """
        try:
            w3 = self.web3.get(chain_id)
            if not w3:
                return None
            
            pool_contract = w3.eth.contract(
                address=Web3.to_checksum_address(pool_address),
                abi=UNIV3_POOL_ABI
            )
            
            # Get current slot0 data
            slot0 = pool_contract.functions.slot0().call()
            sqrt_price_x96 = slot0[0]
            
            # Convert sqrtPriceX96 to actual price
            # price = (sqrtPriceX96 / 2^96) ^ 2
            price = (Decimal(sqrt_price_x96) / Decimal(2 ** 96)) ** 2
            
            logger.info(f"📊 Uniswap V3 Spot Price: {price}")
            return price
            
        except Exception as e:
            logger.error(f"Failed to get Uniswap V3 spot price: {e}")
            return None
    
    def get_token_price_usd(
        self,
        chain_id: int,
        token_symbol: str,
        use_cache: bool = True
    ) -> Optional[Decimal]:
        """
        Get token price in USD with multi-tier fallback
        Priority: Chainlink > Cached > Uniswap V3 TWAP > Uniswap V3 Spot
        
        Args:
            chain_id: Chain ID
            token_symbol: Token symbol (e.g., 'ETH', 'USDC')
            use_cache: Whether to use cached price
            
        Returns: Price in USD as Decimal or None
        """
        cache_key = f"{chain_id}_{token_symbol}"
        
        # Check cache
        if use_cache and cache_key in self.price_cache:
            cached_price, cached_time = self.price_cache[cache_key]
            if time.time() - cached_time < self.cache_duration:
                logger.debug(f"Using cached price for {token_symbol}: ${cached_price}")
                return cached_price
        
        # Try Chainlink first (most reliable)
        chainlink_result = self.get_price_from_chainlink(chain_id, token_symbol)
        if chainlink_result:
            price, timestamp = chainlink_result
            self.price_cache[cache_key] = (price, time.time())
            return price
        
        # Try enhanced chainlink_oracle_feeds module with fallback support
        if CHAINLINK_ORACLE_AVAILABLE:
            try:
                price_float = chainlink_oracle_feeds.get_price_usd_by_chain_id(token_symbol, chain_id)
                if price_float > 0:
                    price = Decimal(str(price_float))
                    self.price_cache[cache_key] = (price, time.time())
                    logger.info(f"📊 Got price from enhanced oracle for {token_symbol}: ${price}")
                    return price
            except Exception as e:
                logger.debug(f"Enhanced oracle lookup failed for {token_symbol}: {e}")
        
        # Fallback to DEX TWAP (not implemented for all pairs yet)
        logger.warning(f"Chainlink price not available for {token_symbol}, using fallback methods")
        
        # For now, return None if all methods fail
        # In production, implement TWAP fallback with pool addresses
        return None
    
    def calculate_price_impact(
        self,
        chain_id: int,
        pool_address: str,
        amount_in: int,
        reserve0: int,
        reserve1: int
    ) -> Decimal:
        """
        Calculate price impact for a trade
        Args:
            chain_id: Chain ID
            pool_address: Pool address
            amount_in: Amount to trade
            reserve0: Reserve of token0
            reserve1: Reserve of token1
        Returns: Price impact as percentage (0-100)
        """
        try:
            # Calculate using constant product formula
            # impact = (amount_in / (reserve_in + amount_in)) * 100
            
            if reserve0 == 0 or reserve1 == 0:
                return Decimal('100')  # Max impact
            
            impact = (Decimal(amount_in) / (Decimal(reserve0) + Decimal(amount_in))) * Decimal('100')
            
            logger.info(f"💥 Price Impact: {impact}%")
            return impact
            
        except Exception as e:
            logger.error(f"Failed to calculate price impact: {e}")
            return Decimal('100')  # Return max impact on error
    
    def get_gas_price_oracle(self, chain_id: int) -> Optional[Dict[str, int]]:
        """
        Get current gas prices from network
        Returns: {
            'slow': slow_gas_price,
            'standard': standard_gas_price,
            'fast': fast_gas_price,
            'instant': instant_gas_price
        }
        """
        try:
            w3 = self.web3.get(chain_id)
            if not w3:
                return None
            
            # Get current gas price
            gas_price = w3.eth.gas_price
            
            # Estimate tiers (simple multipliers)
            return {
                'slow': int(gas_price * 0.8),
                'standard': int(gas_price),
                'fast': int(gas_price * 1.2),
                'instant': int(gas_price * 1.5)
            }
            
        except Exception as e:
            logger.error(f"Failed to get gas price oracle: {e}")
            return None
    
    def get_price_with_enhanced_fallback(
        self,
        chain_id: int,
        token_symbol: str
    ) -> Optional[Decimal]:
        """
        Get token price using enhanced chainlink_oracle_feeds module with full fallback chain.
        This method bypasses the cache and provides fresh data with comprehensive fallback:
        Chainlink (on-chain) → Coingecko (off-chain) → Binance (off-chain)
        
        Args:
            chain_id: Chain ID
            token_symbol: Token symbol (e.g., 'ETH', 'USDC')
            
        Returns: Price in USD as Decimal or None
        """
        if not CHAINLINK_ORACLE_AVAILABLE:
            logger.warning("Enhanced chainlink_oracle_feeds module not available")
            return self.get_token_price_usd(chain_id, token_symbol, use_cache=False)
        
        try:
            price_float = chainlink_oracle_feeds.get_price_usd_by_chain_id(token_symbol, chain_id)
            if price_float > 0:
                return Decimal(str(price_float))
        except Exception as e:
            logger.error(f"Enhanced oracle failed for {token_symbol} on chain {chain_id}: {e}")
        
        return None
    
    def clear_cache(self):
        """Clear price cache"""
        self.price_cache = {}
        logger.info("🧹 Price cache cleared")
