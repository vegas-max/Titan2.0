"""
offchain/core/profit_engine.py
================================

Standalone profit-calculation module for cyclic flash-loan arbitrage.
This module has no heavy external dependencies so it can be imported in
tests and off-chain monitoring scripts without pulling in the full AI stack.

Supported models
----------------
Two-token cyclic arb (A → B → A):
    B     = A_in  · P_A/B · (1 − f_AB) · (1 − s_AB)
    A_out = B     · P_B/A · (1 − f_BA) · (1 − s_BA)
    Profit = A_out − A_in·(1+f_flash) − Gas_inA − Bribe_inA

Three-token triangular arb (A → B → C → A):
    B     = A_in · P_A/B · (1 − f_AB) · (1 − s_AB)
    C     = B    · P_B/C · (1 − f_BC) · (1 − s_BC)
    A_out = C    · P_C/A · (1 − f_CA) · (1 − s_CA)
    Profit = A_out − A_in·(1+f_flash) − Gas_inA − Bribe_inA

Execute only if:
    A_out > A_in·(1+f_flash) + Gas_inA + Bribe_inA

Fee and slippage are applied **multiplicatively** per leg — never combined
additively — to correctly model each swap's independent cost structure.

When using on-chain AMM quotes (getAmountOut / quoteExactInputSingle),
pool fees and price impact are already embedded in the quoted output;
use calculate_enhanced_profit() in that case.
"""

from decimal import Decimal, getcontext

getcontext().prec = 28


class ProfitEngine:
    """
    Implements the Titan Master Profit Equation for cyclic flash-loan arbitrage.

    Two-token cyclic arb (A → B → A):
        B     = A_in  · P_A/B · (1 − f_AB) · (1 − s_AB)
        A_out = B     · P_B/A · (1 − f_BA) · (1 − s_BA)
        Profit = A_out − A_in·(1 + f_flash) − Gas_inA − Bribe_inA

    Three-token triangular arb (A → B → C → A):
        B     = A_in · P_A/B · (1 − f_AB) · (1 − s_AB)
        C     = B    · P_B/C · (1 − f_BC) · (1 − s_BC)
        A_out = C    · P_C/A · (1 − f_CA) · (1 − s_CA)
        Profit = A_out − A_in·(1 + f_flash) − Gas_inA − Bribe_inA

    Execute only if:
        A_out > A_in·(1 + f_flash) + Gas_inA + Bribe_inA

    Fee and slippage are applied multiplicatively per leg — never combined
    additively — to correctly model each swap's independent cost structure.
    When using on-chain AMM quotes (getAmountOut / quoteExactInputSingle),
    pool fees and price impact are already embedded in the quoted output;
    use calculate_enhanced_profit() in that case.
    """

    def __init__(self, default_flash_fee=Decimal("0.0")):
        self.flash_fee = Decimal(str(default_flash_fee))  # Balancer V3 = 0%, Aave V3 = 0.0005

    def calculate_arb_profit(self, a_in, legs, gas_in_a, bribe_in_a=Decimal("0")):
        """
        Calculates net profit for a multi-leg cyclic arbitrage using raw prices.

        Each leg applies DEX protocol fee and slippage multiplicatively:
            out = in · price · (1 − fee) · (1 − slippage)

        Args:
            a_in (Decimal): Flash-loan principal in token A units.
            legs (list[dict]): Ordered list of swap legs.  Each dict must contain:
                - 'price'    (Decimal): Exchange rate for this leg (tokens_out / tokens_in).
                - 'fee'      (Decimal): DEX protocol fee fraction, e.g. Decimal("0.003").
                - 'slippage' (Decimal): Estimated slippage fraction, e.g. Decimal("0.001").
            gas_in_a  (Decimal): Estimated gas cost denominated in token A.
            bribe_in_a (Decimal): Optional MEV relay / block-builder bribe in token A.

        Returns:
            dict with keys:
                a_out            – gross output after all swaps
                flash_repayment  – A_in · (1 + f_flash)
                gas_in_a         – gas cost passed in
                bribe_in_a       – bribe cost passed in
                net_profit       – A_out − repayment − gas − bribe
                is_profitable    – True iff A_out > repayment + gas + bribe
        """
        current = Decimal(str(a_in))
        for leg in legs:
            price    = Decimal(str(leg['price']))
            fee      = Decimal(str(leg['fee']))
            slippage = Decimal(str(leg['slippage']))
            current  = current * price * (1 - fee) * (1 - slippage)

        a_out           = current
        flash_repayment = Decimal(str(a_in)) * (1 + self.flash_fee)
        gas             = Decimal(str(gas_in_a))
        bribe           = Decimal(str(bribe_in_a))
        net_profit      = a_out - flash_repayment - gas - bribe

        return {
            "a_out":           a_out,
            "flash_repayment": flash_repayment,
            "gas_in_a":        gas,
            "bribe_in_a":      bribe,
            "net_profit":      net_profit,
            "is_profitable":   a_out > flash_repayment + gas + bribe,
        }

    def calculate_enhanced_profit(self, amount, amount_out, bridge_fee_usd, gas_cost_usd,
                                   bribe_usd=Decimal("0")):
        """
        Calculates net profit when amount_out comes from on-chain AMM quotes
        (getAmountOut / quoteExactInputSingle).  Pool fees and price impact are
        already embedded in amount_out, so only the flash-loan premium, gas,
        bridge fee, and optional bribe are deducted here.

        Args:
            amount       (Decimal): Flash-loan principal (token A, USD-normalised).
            amount_out   (Decimal): Actual output after all on-chain swap simulations.
            bridge_fee_usd (Decimal): Cross-chain bridge fee in USD (0 for single-chain).
            gas_cost_usd (Decimal): Estimated gas cost in USD.
            bribe_usd    (Decimal): Optional MEV relay / builder bribe in USD.
        """
        gross_revenue_usd = Decimal(str(amount_out))
        loan_cost_usd     = Decimal(str(amount))
        flash_fee_cost    = loan_cost_usd * self.flash_fee
        total_operational_costs = (Decimal(str(bridge_fee_usd))
                                   + Decimal(str(gas_cost_usd))
                                   + Decimal(str(bribe_usd))
                                   + flash_fee_cost)

        net_profit = gross_revenue_usd - loan_cost_usd - total_operational_costs

        return {
            "net_profit":    net_profit,
            "gross_spread":  gross_revenue_usd - loan_cost_usd,
            "total_fees":    total_operational_costs,
            "is_profitable": gross_revenue_usd > loan_cost_usd + total_operational_costs,
        }
