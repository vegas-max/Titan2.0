/// Arbitrage trade profit calculator using pure floating-point math.
///
/// This module computes projected USDC profit for a flash-loan-backed
/// two-step arbitrage route without requiring on-chain U256 arithmetic.
pub struct ArbTrade {
    /// Total Value Locked in the pool (USD)
    pub tvl_pool: f64,
    /// Price of Token A denominated in USDC
    pub token_a_price_usdc: f64,
    /// Slippage impact fraction, e.g. 0.001 = 0.1%
    pub slippage_impact: f64,
    /// Protocol fee fraction, e.g. 0.003 = 0.3%
    pub protocol_fee: f64,
}

/// Assumed price appreciation of Token A between buy and sell legs (10% gain).
const ARB_GAIN_FACTOR: f64 = 1.1;

impl ArbTrade {
    /// Calculate the projected net USDC profit for this arbitrage trade.
    ///
    /// Flash loan amount is capped at the lesser of $50,000 or 10% of TVL.
    ///
    /// Returns the net profit in USDC.
    pub fn calculate_execution(&self) -> f64 {
        // Flash loan amount = min($50k, 10% of TVL)
        let flash_loan_usd = 50_000.0_f64.min(self.tvl_pool * 0.10);

        // Step 1: Convert USDC to Token A (result in Token A units)
        let step_1_in_tokens = flash_loan_usd / self.token_a_price_usdc;
        let step_1_out_tokens = step_1_in_tokens * (1.0 - self.slippage_impact);

        // Step 2: Sell Token A back to USDC at ARB_GAIN_FACTOR price appreciation,
        //         minus slippage and protocol fee (result in Token A units)
        let step_2_in_tokens = step_1_out_tokens;
        let step_2_out_tokens =
            step_2_in_tokens * ARB_GAIN_FACTOR * (1.0 - self.slippage_impact - self.protocol_fee);

        // Convert Token A profit back to USDC and subtract the initial loan amount
        step_2_out_tokens * self.token_a_price_usdc - flash_loan_usd
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_profit_positive_large_tvl() {
        let trade = ArbTrade {
            tvl_pool: 1_000_000.0,
            token_a_price_usdc: 1.0,
            slippage_impact: 0.001,
            protocol_fee: 0.003,
        };
        let profit = trade.calculate_execution();
        assert!(profit > 0.0, "expected positive profit, got {profit}");
    }

    #[test]
    fn test_flash_loan_capped_at_50k() {
        // With a very large TVL the flash loan is capped at $50,000
        let trade = ArbTrade {
            tvl_pool: 10_000_000.0,
            token_a_price_usdc: 1.0,
            slippage_impact: 0.0,
            protocol_fee: 0.0,
        };
        // With zero fees a 10% gain on $50k should give exactly $5,000 profit
        let profit = trade.calculate_execution();
        assert!(
            (profit - 5_000.0).abs() < 1e-6,
            "expected ~$5000 profit, got {profit}"
        );
    }

    #[test]
    fn test_flash_loan_ten_percent_of_small_tvl() {
        // With a small TVL the flash loan is 10% of TVL = $1,000
        let trade = ArbTrade {
            tvl_pool: 10_000.0,
            token_a_price_usdc: 1.0,
            slippage_impact: 0.0,
            protocol_fee: 0.0,
        };
        // 10% gain on $1,000 → $100 profit
        let profit = trade.calculate_execution();
        assert!(
            (profit - 100.0).abs() < 1e-6,
            "expected ~$100 profit, got {profit}"
        );
    }

    #[test]
    fn test_high_fees_reduce_profit() {
        let low_fee = ArbTrade {
            tvl_pool: 1_000_000.0,
            token_a_price_usdc: 1.0,
            slippage_impact: 0.001,
            protocol_fee: 0.001,
        };
        let high_fee = ArbTrade {
            tvl_pool: 1_000_000.0,
            token_a_price_usdc: 1.0,
            slippage_impact: 0.005,
            protocol_fee: 0.01,
        };
        assert!(
            low_fee.calculate_execution() > high_fee.calculate_execution(),
            "lower fees should yield higher profit"
        );
    }
}
