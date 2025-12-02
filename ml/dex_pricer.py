import logging
from web3 import Web3
from core.config import DEX_ROUTERS, CHAINS

# Setup Logging
logger = logging.getLogger("DexPricer")

# === ABIS ===
# Uniswap V2 / Sushi / QuickSwap (getAmountsOut)
UNIV2_ABI = '[{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"}]'

# Uniswap V3 Quoter (quoteExactInputSingle)
UNIV3_ABI = '[{"inputs":[{"components":[{"internalType":"address","name":"tokenIn","type":"address"},{"internalType":"address","name":"tokenOut","type":"address"},{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint24","name":"fee","type":"uint24"},{"internalType":"uint160","name":"sqrtPriceLimitX96","type":"uint160"}],"internalType":"struct IQuoterV2.QuoteExactInputSingleParams","name":"params","type":"tuple"}],"name":"quoteExactInputSingle","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint160","name":"sqrtPriceX96After","type":"uint160"},{"internalType":"uint32","name":"initializedTicksCrossed","type":"uint32"},{"internalType":"uint256","name":"gasEstimate","type":"uint256"}],"stateMutability":"nonpayable","type":"function"}]'

# Curve (get_dy)
CURVE_ABI = '[{"stateMutability":"view","type":"function","name":"get_dy","inputs":[{"name":"i","type":"int128"},{"name":"j","type":"int128"},{"name":"dx","type":"uint256"}],"outputs":[{"name":"","type":"uint256"}]}]'

class DexPricer:
    def __init__(self, w3: Web3, chain_id: int):
        self.w3 = w3
        self.chain_id = chain_id
        self.config = CHAINS.get(chain_id)

    def get_univ3_price(self, token_in, token_out, amount, fee=500):
        """Queries Uniswap V3 Quoter"""
        # Note: Router in config is SwapRouter, we need Quoter address.
        # For Titan, we use a known Quoter map or lookup.
        # Hardcoding Polygon QuoterV2 for example (Move to config in prod)
        quoter_addr = "0x61fFE014bA17989E743c5F6cB21bF9697530B21e" 
        
        try:
            contract = self.w3.eth.contract(address=quoter_addr, abi=UNIV3_ABI)
            # params: tokenIn, tokenOut, amount, fee, sqrtPriceLimitX96
            quote = contract.functions.quoteExactInputSingle(
                (token_in, token_out, int(amount), fee, 0)
            ).call()
            return quote[0] # amountOut
        except Exception as e:
            return 0

    def get_curve_price(self, pool_address, i, j, amount):
        """Queries Curve Pool"""
        try:
            contract = self.w3.eth.contract(address=pool_address, abi=CURVE_ABI)
            return contract.functions.get_dy(i, j, int(amount)).call()
        except Exception:
            return 0

    def get_univ2_price(self, router_key, token_in, token_out, amount):
        """Queries UniV2 Forks (QuickSwap, Sushi, etc.)"""
        router_addr = DEX_ROUTERS.get(router_key)
        if not router_addr: return 0
        
        try:
            contract = self.w3.eth.contract(address=router_addr, abi=UNIV2_ABI)
            amounts = contract.functions.getAmountsOut(int(amount), [token_in, token_out]).call()
            return amounts[-1]
        except Exception:
            return 0

    def find_best_price(self, token_in, token_out, amount):
        """
        Scans all configured DEXs on this chain for the best return.
        """
        results = {}
        
        # 1. Check Uniswap V3
        v3_out = self.get_univ3_price(token_in, token_out, amount)
        results['UNIV3'] = v3_out

        # 2. Check Curve (If router configured)
        # Note: Curve routing is complex; this checks a specific pool if known
        # For generic scanning, use get_best_rate from API or dedicated registry
        
        # 3. Check Tier 2 DEXs (QuickSwap, Sushi, etc.)
        if self.chain_id == 137: # Polygon
            results['QUICKSWAP'] = self.get_univ2_price('QUICKSWAP', token_in, token_out, amount)
            results['SUSHI'] = self.get_univ2_price('SUSHI', token_in, token_out, amount)
            results['APE'] = self.get_univ2_price('APE', token_in, token_out, amount)

        # Find Winner
        best_dex = max(results, key=results.get)
        best_amount = results[best_dex]
        
        return {
            "dex": best_dex,
            "amount_out": best_amount,
            "all_quotes": results
        }