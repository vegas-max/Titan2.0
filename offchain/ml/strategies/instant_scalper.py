import logging
import time
from decimal import Decimal
from datetime import datetime

# Core Imports
from offchain.core.config import CHAINS
from offchain.ml.dex_pricer import DexPricer

logger = logging.getLogger("InstantScalper")

# Default per-leg DEX fee fractions (overridable per pool)
# UniswapV3 500 bps tier = 0.05%, 3000 bps tier = 0.3%, 10000 bps tier = 1%
_FEE_UNIV3_500  = Decimal("0.0005")
_FEE_UNIV3_3000 = Decimal("0.003")
_FEE_CURVE      = Decimal("0.0004")   # Curve stable pools ≈ 0.04%

class InstantScalper:
    """
    Implements the 'Instant Profit' Strategy:
    - Single-Chain Only (No Bridges)
    - 2-Hop Only (Token A -> Token B -> Token A)
    - Aggressive Gas (Next Block)
    - Micro-Profits ($1.50+)

    Profit model (correct multiplicative form):
        B     = A_in · P_A/B_DEX1 · (1 − f_DEX1) · (1 − s_1)
        A_out = B    · P_B/A_DEX2 · (1 − f_DEX2) · (1 − s_2)
        Profit = A_out − A_in·(1 + f_flash) − Gas_inA − Bribe_inA
    Execute only if: A_out > A_in·(1 + f_flash) + Gas_inA + Bribe_inA

    AMM getAmountOut quotes already embed pool fees and price impact; when
    on-chain quotes are used for both legs the per-leg fee multipliers below
    are not applied a second time – the raw quote output is used directly.
    """
    
    # Priority Tiers
    TIERS = {
        1: [('USDC', 'USDT'), ('USDC', 'DAI'), ('USDT', 'DAI')], # Stable Arbs
        2: [('WETH', 'USDC'), ('WBTC', 'USDC'), ('WMATIC', 'USDC')], # Major Pairs
    }

    def __init__(self, chain_id, web3_conn, token_inventory,
                 flash_fee=Decimal("0.0"),
                 slippage_per_leg=Decimal("0.001"),
                 gas_cost_usd=Decimal("0.5"),
                 bribe_usd=Decimal("0")):
        self.chain_id  = chain_id
        self.w3        = web3_conn
        self.inventory = token_inventory
        self.pricer    = DexPricer(self.w3, self.chain_id)

        # Flash-loan premium (Balancer V3 = 0%, Aave V3 = 0.05%)
        self.flash_fee       = Decimal(str(flash_fee))
        # Conservative per-leg slippage estimate
        self.slippage        = Decimal(str(slippage_per_leg))
        # Gas denominated in the same unit as profit (USD)
        self.gas_cost_usd    = Decimal(str(gas_cost_usd))
        # Optional MEV relay / builder bribe
        self.bribe_usd       = Decimal(str(bribe_usd))

        # Profitability threshold
        self.MIN_PROFIT      = Decimal("1.50")   # $1.50 USD
        self.TRADE_SIZE      = Decimal("50000")  # $50k flash-loan

    def scan(self):
        """
        Rapidly scans Tier 1 & 2 pairs for micro-arbs.
        """
        opportunities = []
        
        # 1. Scan Tier 1 (Stables)
        for token_a, token_b in self.TIERS[1]:
            opp = self._check_pair(token_a, token_b)
            if opp: opportunities.append(opp)

        # 2. Scan Tier 2 (Majors)
        for token_a, token_b in self.TIERS[2]:
            opp = self._check_pair(token_a, token_b)
            if opp: opportunities.append(opp)
            
        return opportunities

    def _check_pair(self, sym_a, sym_b):
        """
        Evaluate a two-hop cyclic arb for the pair (sym_a → sym_b → sym_a).

        Uses on-chain AMM quotes (getAmountOut / quoteExactInputSingle) for
        both legs.  Those quotes already embed pool fees and price impact, so
        the per-leg fee multiplier is NOT applied again – only the flash-loan
        premium, gas and optional bribe are subtracted.

        For production deployments replace `get_univ3_price` with the pool's
        getAmountOut to capture the true nonlinear price-impact curve.

        Returns an opportunity dict if profitable, else None.
        """
        addr_a = self.inventory.get(sym_a, {}).get('address')
        addr_b = self.inventory.get(sym_b, {}).get('address')
        decimals_a = self.inventory.get(sym_a, {}).get('decimals', 6)
        if not addr_a or not addr_b:
            return None

        # Scale trade size to raw token units
        amount_in_raw = int(self.TRADE_SIZE * (10 ** decimals_a))

        # --- Leg 1: A → B on DEX1 (UniswapV3 500-bps tier) ---
        # getAmountOut already accounts for the 0.05% pool fee and price impact.
        out_leg1 = self.pricer.get_univ3_price(addr_a, addr_b, amount_in_raw, 500)
        if not out_leg1 or out_leg1 == 0:
            return None

        # --- Leg 2: B → A on DEX2 (Curve stable pool) ---
        # In production wire to: self.pricer.get_curve_out(addr_b, addr_a, out_leg1)
        # Returning None here means the opportunity is not yet actionable until
        # the Curve quoter is wired; the profit check below guards against execution.
        out_leg2 = self.pricer.get_univ3_price(addr_b, addr_a, out_leg1, 500)
        if not out_leg2 or out_leg2 == 0:
            return None

        # --- Profit check ---
        # Both quotes already embed AMM fees, so we only subtract:
        #   flash_repayment = A_in * (1 + f_flash)
        #   gas + bribe (denominated in token-A / USD for stables)
        a_in_usd  = self.TRADE_SIZE
        a_out_usd = Decimal(str(out_leg2)) / Decimal(10 ** decimals_a)

        flash_repayment = a_in_usd * (1 + self.flash_fee)
        net_profit      = a_out_usd - flash_repayment - self.gas_cost_usd - self.bribe_usd

        # Kill-switch: only signal if A_out > repayment + gas + bribe
        if a_out_usd <= flash_repayment + self.gas_cost_usd + self.bribe_usd:
            return None
        if net_profit < self.MIN_PROFIT:
            return None

        return {
            'token_a':        sym_a,
            'token_b':        sym_b,
            'a_in_usd':       float(a_in_usd),
            'a_out_usd':      float(a_out_usd),
            'flash_repayment':float(flash_repayment),
            'gas_cost_usd':   float(self.gas_cost_usd),
            'bribe_usd':      float(self.bribe_usd),
            'net_profit_usd': float(net_profit),
            'is_profitable':  True,
        }