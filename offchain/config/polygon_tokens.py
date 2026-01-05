"""
Polygon Token Universe - Production Ready Configuration
Auto-generated from POLYGON_TOKEN_UNIVERSE.md
Last Updated: 2026-01-05

Complete, verified Polygon mainnet token universe with:
- EIP-55 checksummed addresses
- Clear wrapped vs bridged logic
- Stablecoin core + liquidity kings
- DEX-native + Curve/Balancer aware
- Ready to drop into token_universe.json or Python/TS module
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class TokenPriority(Enum):
    """Token priority levels"""
    CRITICAL = 1  # Core stablecoins, WMATIC, WETH, WBTC
    HIGH = 2      # Major DeFi tokens with proven liquidity


class TokenCategory(Enum):
    """Token category for routing optimization"""
    STABLECOIN = "stablecoin"
    GAS_TOKEN = "gas_token"
    WRAPPED_MAJOR = "wrapped_major"
    DEX_NATIVE = "dex_native"
    DEFI_BLUE_CHIP = "defi_blue_chip"
    ALTCOIN = "altcoin"
    LIQUID_STAKING = "liquid_staking"
    ECOSYSTEM = "ecosystem"


@dataclass
class PolygonToken:
    """Polygon token configuration"""
    id: int
    symbol: str
    name: str
    address: str  # EIP-55 checksummed
    decimals: int
    type: str  # native_wrapped, bridged, native, hybrid, derivative
    priority: TokenPriority
    flashloan_safe: bool
    chainlink_oracle: Optional[str] = None
    category: Optional[TokenCategory] = None


# Complete Polygon token universe - 29 tokens
POLYGON_TOKENS: List[PolygonToken] = [
    # Core stablecoins (Priority 1)
    PolygonToken(
        id=0, symbol="WMATIC", name="Wrapped POL",
        address="0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",
        decimals=18, type="native_wrapped", priority=TokenPriority.CRITICAL,
        flashloan_safe=True, category=TokenCategory.GAS_TOKEN,
        chainlink_oracle="0xAB594600376Ec9fD91F8e885dADF0CE036862dE0"
    ),
    PolygonToken(
        id=1, symbol="USDC", name="USD Coin (Bridged)",
        address="0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
        decimals=6, type="bridged", priority=TokenPriority.CRITICAL,
        flashloan_safe=True, category=TokenCategory.STABLECOIN,
        chainlink_oracle="0xfE4A8cc5b5B2366C1B58Bea3858e81843581b2F7"
    ),
    PolygonToken(
        id=2, symbol="USDC.e", name="USD Coin (Native)",
        address="0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359",
        decimals=6, type="native", priority=TokenPriority.CRITICAL,
        flashloan_safe=True, category=TokenCategory.STABLECOIN,
        chainlink_oracle="0xfE4A8cc5b5B2366C1B58Bea3858e81843581b2F7"
    ),
    PolygonToken(
        id=3, symbol="USDT", name="Tether USD",
        address="0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
        decimals=6, type="bridged", priority=TokenPriority.CRITICAL,
        flashloan_safe=True, category=TokenCategory.STABLECOIN,
        chainlink_oracle="0x0A6513e40db6EB1b165753AD52E80663aeA50545"
    ),
    PolygonToken(
        id=4, symbol="DAI", name="Dai Stablecoin",
        address="0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063",
        decimals=18, type="bridged", priority=TokenPriority.CRITICAL,
        flashloan_safe=True, category=TokenCategory.STABLECOIN,
        chainlink_oracle="0x4746DeC9e833A82EC7C2C1356372CcF2cfcD2F3D"
    ),
    PolygonToken(
        id=5, symbol="WETH", name="Wrapped Ether",
        address="0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619",
        decimals=18, type="bridged", priority=TokenPriority.CRITICAL,
        flashloan_safe=True, category=TokenCategory.WRAPPED_MAJOR,
        chainlink_oracle="0xF9680D99D6C9589e2a93a78A04A279e509205945"
    ),
    PolygonToken(
        id=6, symbol="WBTC", name="Wrapped Bitcoin",
        address="0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6",
        decimals=8, type="bridged", priority=TokenPriority.CRITICAL,
        flashloan_safe=True, category=TokenCategory.WRAPPED_MAJOR,
        chainlink_oracle="0xc907E116054Ad103354f2D350FD2514433D57F6f"
    ),
    PolygonToken(
        id=7, symbol="FRAX", name="Frax",
        address="0x45c32fA6DF82ead1e2EF74d17b76547EDdFaFF89",
        decimals=18, type="hybrid", priority=TokenPriority.CRITICAL,
        flashloan_safe=True, category=TokenCategory.STABLECOIN
    ),
    
    # DEX-native governance (Priority 1)
    PolygonToken(
        id=8, symbol="QUICK", name="QuickSwap",
        address="0xB5C064F955D8e7F38fE0460C556a72987494eE17",
        decimals=18, type="native", priority=TokenPriority.CRITICAL,
        flashloan_safe=True, category=TokenCategory.DEX_NATIVE
    ),
    PolygonToken(
        id=9, symbol="SUSHI", name="SushiSwap",
        address="0x0b3F868E0BE5597D5DB7fEB59E1CADBb0fdDa50a",
        decimals=18, type="bridged", priority=TokenPriority.CRITICAL,
        flashloan_safe=True, category=TokenCategory.DEX_NATIVE,
        chainlink_oracle="0x49B0c695039243BBfEb8EcD054EB70061fd54aa0"
    ),
    PolygonToken(
        id=10, symbol="BAL", name="Balancer",
        address="0x9a71012B13CA4d3D0Cdc72A177DF3ef03b0E76A3",
        decimals=18, type="bridged", priority=TokenPriority.CRITICAL,
        flashloan_safe=True, category=TokenCategory.DEX_NATIVE
    ),
    
    # Major DeFi protocols (Priority 1)
    PolygonToken(
        id=11, symbol="AAVE", name="Aave",
        address="0xD6DF932A45C0f255f85145f286eA0b292B21C90B",
        decimals=18, type="bridged", priority=TokenPriority.CRITICAL,
        flashloan_safe=True, category=TokenCategory.DEFI_BLUE_CHIP,
        chainlink_oracle="0x72484B12719E23115761D5DA1646945632979bB6"
    ),
    PolygonToken(
        id=12, symbol="CRV", name="Curve DAO Token",
        address="0x172370d5Cd63279eFa6d502DAB29171933a610AF",
        decimals=18, type="bridged", priority=TokenPriority.CRITICAL,
        flashloan_safe=True, category=TokenCategory.DEFI_BLUE_CHIP,
        chainlink_oracle="0x336584C8E6Dc19637A5b36206B1c79923111b405"
    ),
    PolygonToken(
        id=13, symbol="UNI", name="Uniswap",
        address="0xb33EaAd8d922B1083446DC23f610c2567fB5180f",
        decimals=18, type="bridged", priority=TokenPriority.CRITICAL,
        flashloan_safe=True, category=TokenCategory.DEFI_BLUE_CHIP
    ),
    PolygonToken(
        id=14, symbol="LINK", name="Chainlink",
        address="0x53E0bca35eC356BD5ddDFebbD1Fc0fD03FaBad39",
        decimals=18, type="bridged", priority=TokenPriority.CRITICAL,
        flashloan_safe=True, category=TokenCategory.DEFI_BLUE_CHIP,
        chainlink_oracle="0xd9FFdb71EbE7496cC440152d43986Aae0AB76665"
    ),
    
    # High-volume altcoins (Priority 2)
    PolygonToken(
        id=15, symbol="COMP", name="Compound",
        address="0x8505b9d2254A7Ae468c0E9dd10Ccea3A837aef5c",
        decimals=18, type="bridged", priority=TokenPriority.HIGH,
        flashloan_safe=True, category=TokenCategory.ALTCOIN
    ),
    PolygonToken(
        id=16, symbol="SNX", name="Synthetix",
        address="0x50B728D8D964fd00C2d0AAD81718b71311feF68a",
        decimals=18, type="bridged", priority=TokenPriority.HIGH,
        flashloan_safe=True, category=TokenCategory.ALTCOIN
    ),
    PolygonToken(
        id=17, symbol="LDO", name="Lido DAO",
        address="0xC3C7d422809852031b44ab29EEC9F1EfF2A58756",
        decimals=18, type="bridged", priority=TokenPriority.HIGH,
        flashloan_safe=True, category=TokenCategory.ALTCOIN
    ),
    PolygonToken(
        id=18, symbol="MANA", name="Decentraland",
        address="0xA1c57f48F0Deb89f569dFbE6E2B7f46D33606fD4",
        decimals=18, type="bridged", priority=TokenPriority.HIGH,
        flashloan_safe=True, category=TokenCategory.ALTCOIN,
        chainlink_oracle="0xA1CbF3Fe43BC3501e3Fc4b573e822c70e76A7512"
    ),
    PolygonToken(
        id=19, symbol="ENJ", name="Enjin Coin",
        address="0x7eC26842F195c852Fa843bB9f6D8B583a274a157",
        decimals=18, type="bridged", priority=TokenPriority.HIGH,
        flashloan_safe=True, category=TokenCategory.ALTCOIN
    ),
    PolygonToken(
        id=20, symbol="REN", name="Ren",
        address="0x19782D3Dc4701cEeeDcD90f0993f0A9126ed89d0",
        decimals=18, type="bridged", priority=TokenPriority.HIGH,
        flashloan_safe=False, category=TokenCategory.ALTCOIN
    ),
    PolygonToken(
        id=21, symbol="BAT", name="Basic Attention Token",
        address="0x3Cef98bb43d732E2F285eE605a8158cDE967D219",
        decimals=18, type="bridged", priority=TokenPriority.HIGH,
        flashloan_safe=True, category=TokenCategory.ALTCOIN
    ),
    
    # Liquid staking derivatives (Priority 2)
    PolygonToken(
        id=22, symbol="stMATIC", name="Staked MATIC (Lido)",
        address="0x3A58a54C066FdC0f2D55FC9C89F0415C92eBf3C4",
        decimals=18, type="derivative", priority=TokenPriority.HIGH,
        flashloan_safe=False, category=TokenCategory.LIQUID_STAKING
    ),
    PolygonToken(
        id=23, symbol="MaticX", name="Stader Staked MATIC",
        address="0xfa68FB4628DFF1028CFEc22b4162FCcd0d45efb6",
        decimals=18, type="derivative", priority=TokenPriority.HIGH,
        flashloan_safe=False, category=TokenCategory.LIQUID_STAKING
    ),
    
    # Specialized stablecoins (Priority 2)
    PolygonToken(
        id=24, symbol="MAI", name="Mai Stablecoin",
        address="0xa3Fa99A148fA48D14Ed51d610c367C61876997F1",
        decimals=18, type="native", priority=TokenPriority.HIGH,
        flashloan_safe=True, category=TokenCategory.STABLECOIN
    ),
    PolygonToken(
        id=25, symbol="USDD", name="Decentralized USD",
        address="0xFFA4D863C96e743A2e1513824EA006B8D0353C57",
        decimals=18, type="bridged", priority=TokenPriority.HIGH,
        flashloan_safe=True, category=TokenCategory.STABLECOIN
    ),
    PolygonToken(
        id=26, symbol="agEUR", name="Angle Protocol EUR",
        address="0xE0B52e49357Fd4DAf2c15e02058DCE6BC0057db4",
        decimals=18, type="native", priority=TokenPriority.HIGH,
        flashloan_safe=True, category=TokenCategory.STABLECOIN
    ),
    
    # Polygon-native ecosystem (Priority 2)
    PolygonToken(
        id=27, symbol="GHST", name="Aavegotchi",
        address="0x385Eeac5cB85A38A9a07A70c73e0a3271CfB54A7",
        decimals=18, type="native", priority=TokenPriority.HIGH,
        flashloan_safe=True, category=TokenCategory.ECOSYSTEM
    ),
    PolygonToken(
        id=28, symbol="SAND", name="The Sandbox",
        address="0xBbba073C31bF03b8ACf7c28EF0738DeCF3695683",
        decimals=18, type="bridged", priority=TokenPriority.HIGH,
        flashloan_safe=True, category=TokenCategory.ECOSYSTEM,
        chainlink_oracle="0x3D49406EDd4D52Fb7FFd25485f32E073b529C924"
    ),
]


# Helper functions
def get_token_by_symbol(symbol: str) -> Optional[PolygonToken]:
    """Get token by symbol"""
    for token in POLYGON_TOKENS:
        if token.symbol == symbol:
            return token
    return None


def get_token_by_address(address: str) -> Optional[PolygonToken]:
    """Get token by address (case-insensitive)"""
    normalized = address.lower()
    for token in POLYGON_TOKENS:
        if token.address.lower() == normalized:
            return token
    return None


def get_tokens_by_priority(priority: TokenPriority) -> List[PolygonToken]:
    """Get all tokens of a specific priority"""
    return [t for t in POLYGON_TOKENS if t.priority == priority]


def get_tokens_by_category(category: TokenCategory) -> List[PolygonToken]:
    """Get all tokens of a specific category"""
    return [t for t in POLYGON_TOKENS if t.category == category]


def get_flashloan_safe_tokens() -> List[PolygonToken]:
    """Get all flashloan-safe tokens"""
    return [t for t in POLYGON_TOKENS if t.flashloan_safe]


def get_stablecoins() -> List[PolygonToken]:
    """Get all stablecoins"""
    return get_tokens_by_category(TokenCategory.STABLECOIN)


def get_critical_tokens() -> List[PolygonToken]:
    """Get all critical priority tokens"""
    return get_tokens_by_priority(TokenPriority.CRITICAL)


def get_tokens_with_oracles() -> List[PolygonToken]:
    """Get all tokens with Chainlink oracles"""
    return [t for t in POLYGON_TOKENS if t.chainlink_oracle is not None]


# DEX mapping
DEX_PREFERRED_TOKENS: Dict[str, List[str]] = {
    "quickswap": ["WMATIC", "USDC", "USDT", "DAI", "WETH", "WBTC", "QUICK"],
    "sushiswap": ["WMATIC", "USDC", "USDT", "DAI", "WETH", "WBTC", "SUSHI"],
    "curve": ["USDC", "USDT", "DAI", "FRAX", "MAI", "agEUR", "stMATIC", "WMATIC"],
    "balancer": ["WMATIC", "USDC", "DAI", "WETH", "WBTC", "BAL", "MaticX"],
}


# Statistics
TOTAL_TOKENS = len(POLYGON_TOKENS)
CRITICAL_COUNT = len(get_critical_tokens())
HIGH_PRIORITY_COUNT = len(get_tokens_by_priority(TokenPriority.HIGH))
FLASHLOAN_SAFE_COUNT = len(get_flashloan_safe_tokens())
ORACLE_COUNT = len(get_tokens_with_oracles())


# Export all public APIs
__all__ = [
    "TokenPriority",
    "TokenCategory",
    "PolygonToken",
    "POLYGON_TOKENS",
    "get_token_by_symbol",
    "get_token_by_address",
    "get_tokens_by_priority",
    "get_tokens_by_category",
    "get_flashloan_safe_tokens",
    "get_stablecoins",
    "get_critical_tokens",
    "get_tokens_with_oracles",
    "DEX_PREFERRED_TOKENS",
    "TOTAL_TOKENS",
    "CRITICAL_COUNT",
    "HIGH_PRIORITY_COUNT",
    "FLASHLOAN_SAFE_COUNT",
    "ORACLE_COUNT",
]
