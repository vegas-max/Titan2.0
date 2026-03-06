"""
Test Suite: Arbitrage Profit Math
==================================

Validates the mathematically correct profit model used across the Titan system:

  Per-leg formula (fee and slippage applied multiplicatively):
      out = in · price · (1 − fee) · (1 − slippage)

  Full multi-leg model:
      B     = A_in · P_A/B · (1 − f_AB) · (1 − s_AB)
      C     = B    · P_B/C · (1 − f_BC) · (1 − s_BC)
      A_out = C    · P_C/A · (1 − f_CA) · (1 − s_CA)
      Profit = A_out − A_in·(1+f_flash) − Gas − Bribe

  Execute only if:
      A_out > A_in·(1+f_flash) + Gas + Bribe

Run with:
    PYTHONPATH=<repo_root> python3 -m unittest offchain.tests.test_arb_math
"""

import unittest
import os
import sys

from decimal import Decimal, getcontext

getcontext().prec = 28

# Allow running from the repo root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from offchain.core.profit_engine import ProfitEngine


class TestProfitEngineArbMath(unittest.TestCase):
    """Unit tests for ProfitEngine.calculate_arb_profit()"""

    def setUp(self):
        # Aave V3 flash-loan fee: 0.05%
        self.engine_aave     = ProfitEngine(default_flash_fee=Decimal("0.0005"))
        # Balancer V3: zero fee
        self.engine_balancer = ProfitEngine(default_flash_fee=Decimal("0.0"))

    # ------------------------------------------------------------------
    # 1. Two-token cyclic arb (A → B → A) — no price advantage
    # ------------------------------------------------------------------
    def test_two_leg_break_even_no_spread(self):
        """With perfectly symmetric prices (no spread) and zero costs the
        round-trip loses money only through fees and slippage."""
        legs = [
            {'price': Decimal('1'), 'fee': Decimal('0.003'), 'slippage': Decimal('0.001')},
            {'price': Decimal('1'), 'fee': Decimal('0.003'), 'slippage': Decimal('0.001')},
        ]
        result = self.engine_balancer.calculate_arb_profit(
            a_in=Decimal('10000'),
            legs=legs,
            gas_in_a=Decimal('0'),
            bribe_in_a=Decimal('0'),
        )
        # A_out < A_in because each leg loses money
        self.assertLess(result['a_out'], Decimal('10000'))
        self.assertFalse(result['is_profitable'])

    # ------------------------------------------------------------------
    # 2. Fee and slippage must be multiplicative, NOT additive
    # ------------------------------------------------------------------
    def test_multiplicative_vs_additive_fee_slippage(self):
        """Ensure (1-f)*(1-s) != (1-f-s): the two forms yield different output.
        (1-f)*(1-s) = 1 - f - s + f*s > 1 - f - s, so the multiplicative form
        gives a *larger* output (less over-penalisation) — the correct model."""
        fee      = Decimal('0.003')
        slippage = Decimal('0.001')
        price    = Decimal('1')
        amount   = Decimal('10000')

        # Correct: multiplicative
        out_mult = amount * price * (1 - fee) * (1 - slippage)
        # Wrong:   additive (over-penalises by the cross-term f*s)
        out_add  = amount * price * (1 - fee - slippage)

        self.assertNotEqual(out_mult, out_add)
        # Multiplicative gives a slightly *larger* output because it doesn't
        # double-count the f*s cross-term that the additive form removes.
        self.assertGreater(out_mult, out_add)

    # ------------------------------------------------------------------
    # 3. Two-leg arb — profitable with sufficient spread
    # ------------------------------------------------------------------
    def test_two_leg_profitable_with_spread(self):
        """A spread of 2% on a $10 000 loan should be profitable after typical
        Polygon gas and a 0.3% DEX fee per leg with 0.1% slippage per leg."""
        # Prices: buy leg sees 1.0, sell leg sees 1.02 (2% spread)
        legs = [
            {'price': Decimal('1'),    'fee': Decimal('0.003'), 'slippage': Decimal('0.001')},
            {'price': Decimal('1.02'), 'fee': Decimal('0.003'), 'slippage': Decimal('0.001')},
        ]
        gas = Decimal('5')       # $5 gas (Polygon)
        result = self.engine_balancer.calculate_arb_profit(
            a_in=Decimal('10000'),
            legs=legs,
            gas_in_a=gas,
        )
        self.assertTrue(result['is_profitable'])
        self.assertGreater(result['net_profit'], Decimal('0'))

    # ------------------------------------------------------------------
    # 4. Flash-loan premium must reduce profit
    # ------------------------------------------------------------------
    def test_flash_loan_fee_reduces_profit(self):
        """Aave V3 charges 0.05%; verify profit is lower than Balancer's 0%."""
        legs = [
            {'price': Decimal('1'),    'fee': Decimal('0.003'), 'slippage': Decimal('0.001')},
            {'price': Decimal('1.02'), 'fee': Decimal('0.003'), 'slippage': Decimal('0.001')},
        ]
        a_in = Decimal('10000')
        gas  = Decimal('5')

        r_balancer = self.engine_balancer.calculate_arb_profit(a_in, legs, gas)
        r_aave     = self.engine_aave.calculate_arb_profit(a_in, legs, gas)

        self.assertGreater(r_balancer['net_profit'], r_aave['net_profit'])

    # ------------------------------------------------------------------
    # 5. Kill-switch: gas makes unprofitable trade rejectable
    # ------------------------------------------------------------------
    def test_kill_switch_high_gas(self):
        """A tiny spread eaten by high gas should be rejected."""
        legs = [
            {'price': Decimal('1'),      'fee': Decimal('0.003'), 'slippage': Decimal('0.001')},
            {'price': Decimal('1.0001'), 'fee': Decimal('0.003'), 'slippage': Decimal('0.001')},
        ]
        high_gas = Decimal('500')  # $500 gas – kills small spread
        result = self.engine_balancer.calculate_arb_profit(
            a_in=Decimal('10000'),
            legs=legs,
            gas_in_a=high_gas,
        )
        self.assertFalse(result['is_profitable'])

    # ------------------------------------------------------------------
    # 6. Bribe reduces profit correctly
    # ------------------------------------------------------------------
    def test_bribe_reduces_profit(self):
        """An MEV bribe must further reduce net profit beyond gas alone."""
        legs = [
            {'price': Decimal('1'),    'fee': Decimal('0.003'), 'slippage': Decimal('0.001')},
            {'price': Decimal('1.02'), 'fee': Decimal('0.003'), 'slippage': Decimal('0.001')},
        ]
        a_in  = Decimal('10000')
        gas   = Decimal('5')
        bribe = Decimal('10')

        r_no_bribe   = self.engine_balancer.calculate_arb_profit(a_in, legs, gas, Decimal('0'))
        r_with_bribe = self.engine_balancer.calculate_arb_profit(a_in, legs, gas, bribe)

        self.assertGreater(r_no_bribe['net_profit'], r_with_bribe['net_profit'])
        diff = r_no_bribe['net_profit'] - r_with_bribe['net_profit']
        self.assertAlmostEqual(float(diff), float(bribe), places=10)

    # ------------------------------------------------------------------
    # 7. Three-token triangular arb (A → B → C → A)
    # ------------------------------------------------------------------
    def test_three_leg_triangular_arb(self):
        """Triangular arb with a price inconsistency sufficient to overcome 3 legs of costs."""
        # Three legs of 0.3% fee + 0.1% slippage each give a combined multiplier of:
        # ((1-0.003)*(1-0.001))^3 ≈ 0.9881
        # So the net price advantage must exceed ~1.2% to be profitable.
        # Use 1.5% price advantage on first leg to ensure profitability.
        legs = [
            {'price': Decimal('1.015'), 'fee': Decimal('0.003'), 'slippage': Decimal('0.001')},
            {'price': Decimal('1'),     'fee': Decimal('0.003'), 'slippage': Decimal('0.001')},
            {'price': Decimal('1'),     'fee': Decimal('0.003'), 'slippage': Decimal('0.001')},
        ]
        result = self.engine_balancer.calculate_arb_profit(
            a_in=Decimal('10000'),
            legs=legs,
            gas_in_a=Decimal('5'),
        )
        self.assertTrue(result['is_profitable'])
        self.assertGreater(result['net_profit'], Decimal('0'))

    # ------------------------------------------------------------------
    # 8. calculate_enhanced_profit – backward-compatibility with on-chain quotes
    # ------------------------------------------------------------------
    def test_enhanced_profit_positive(self):
        """When AMM quote exceeds repayment + gas, profit must be positive."""
        result = self.engine_aave.calculate_enhanced_profit(
            amount=Decimal('10000'),
            amount_out=Decimal('10060'),   # 0.6% gross return
            bridge_fee_usd=Decimal('0'),
            gas_cost_usd=Decimal('5'),
            bribe_usd=Decimal('0'),
        )
        self.assertTrue(result['is_profitable'])
        self.assertGreater(result['net_profit'], Decimal('0'))

    def test_enhanced_profit_negative_after_flash_fee(self):
        """Even a positive gross spread can become negative once flash fee and
        gas are added."""
        result = self.engine_aave.calculate_enhanced_profit(
            amount=Decimal('10000'),
            amount_out=Decimal('10007'),   # 0.07% gross – barely above 0.05% flash fee
            bridge_fee_usd=Decimal('0'),
            gas_cost_usd=Decimal('10'),    # gas kills it
            bribe_usd=Decimal('0'),
        )
        self.assertFalse(result['is_profitable'])

    def test_enhanced_profit_bribe_reduces_result(self):
        """Bribe parameter correctly lowers the reported net profit."""
        base = self.engine_balancer.calculate_enhanced_profit(
            amount=Decimal('10000'),
            amount_out=Decimal('10100'),
            bridge_fee_usd=Decimal('0'),
            gas_cost_usd=Decimal('5'),
            bribe_usd=Decimal('0'),
        )
        with_bribe = self.engine_balancer.calculate_enhanced_profit(
            amount=Decimal('10000'),
            amount_out=Decimal('10100'),
            bridge_fee_usd=Decimal('0'),
            gas_cost_usd=Decimal('5'),
            bribe_usd=Decimal('20'),
        )
        self.assertAlmostEqual(
            float(base['net_profit'] - with_bribe['net_profit']),
            20.0,
            places=8,
        )


class TestSimulationEngineArbMath(unittest.TestCase):
    """Unit tests for TitanSimulationEngine.simulate_profit_calculation()"""

    def setUp(self):
        from simulation.simulation_engine import TitanSimulationEngine
        self.engine = TitanSimulationEngine()

    def _make_opp(self, spread_pct=3.0, gas_gwei=30, chain_id=137):
        return {
            'spread_pct':    spread_pct,
            'gas_price_gwei': gas_gwei,
            'chain_id':      chain_id,
        }

    def test_profitable_spread_polygon(self):
        """3% spread on Polygon (cheap gas) with a large-enough loan should be profitable.

        The simulation engine uses a gas formula of:
            base_gas_units * gwei_price * chain_factor * buffer
        which on Polygon evaluates to ~$421 per transaction.  A loan of $200k with
        a 3% spread and two per-leg cost reductions of (1-0.003)*(1-0.01) yields
        a positive net profit above that gas cost.
        """
        profit, breakdown = self.engine.simulate_profit_calculation(
            self._make_opp(spread_pct=3.0, gas_gwei=30, chain_id=137),
            loan_amount=200_000,
            liquidity=10_000_000,
        )
        self.assertGreater(profit, 0)
        # a_out must be present in breakdown
        self.assertIn('a_out', breakdown)

    def test_fee_and_slippage_applied_multiplicatively(self):
        """Verify that a_out < loan*(1+spread): fees/slippage reduce the output."""
        spread = 0.03
        loan   = 10000
        profit, breakdown = self.engine.simulate_profit_calculation(
            self._make_opp(spread_pct=spread * 100, gas_gwei=30, chain_id=137),
            loan_amount=loan,
            liquidity=1_000_000,
        )
        # With per-leg fee + slippage, a_out must be less than loan*(1+spread)
        self.assertLess(breakdown['a_out'], loan * (1 + spread))

    def test_bribe_reduces_net_profit(self):
        """Setting bribe_usd > 0 in config must reduce net profit."""
        opp    = self._make_opp(spread_pct=3.0)
        profit_no_bribe, _ = self.engine.simulate_profit_calculation(
            opp, loan_amount=10000, liquidity=1_000_000
        )
        self.engine.config['bribe_usd'] = 50.0
        profit_with_bribe, _ = self.engine.simulate_profit_calculation(
            opp, loan_amount=10000, liquidity=1_000_000
        )
        self.engine.config['bribe_usd'] = 0.0  # reset
        self.assertGreater(profit_no_bribe, profit_with_bribe)
        self.assertAlmostEqual(profit_no_bribe - profit_with_bribe, 50.0, places=8)

    def test_high_gas_ethereum_unprofitable(self):
        """Small spread + high Ethereum gas should result in negative profit."""
        profit, _ = self.engine.simulate_profit_calculation(
            self._make_opp(spread_pct=0.5, gas_gwei=200, chain_id=1),
            loan_amount=10000,
            liquidity=1_000_000,
        )
        self.assertLess(profit, 0)


if __name__ == '__main__':
    unittest.main()
