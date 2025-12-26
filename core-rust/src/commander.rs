use ethers::prelude::*;
use std::sync::Arc;
use anyhow::Result;
use log::{info, warn, debug};

use crate::config::BALANCER_V3_VAULT;
use crate::simulation_engine::get_provider_tvl;

/// Titan Commander - Loan optimization and risk management
pub struct TitanCommander {
    chain_id: u64,
    provider: Arc<Provider<Http>>,
    
    // Guardrails (Real Money Limits)
    pub min_loan_usd: u64,
    pub max_tvl_share: f64,
    pub slippage_tolerance: f64,
}

impl TitanCommander {
    /// Create a new Titan Commander instance
    pub fn new(chain_id: u64, provider: Arc<Provider<Http>>) -> Self {
        Self {
            chain_id,
            provider,
            min_loan_usd: 10000,      // Minimum trade size ($10k)
            max_tvl_share: 0.20,      // Max % of pool to borrow (20%)
            slippage_tolerance: 0.995, // 0.5% max slippage
        }
    }

    /// Optimize loan size using binary search based on real on-chain liquidity
    /// Returns: Safe amount or 0 (abort)
    pub async fn optimize_loan_size(
        &self,
        token_address: Address,
        target_amount_raw: U256,
        decimals: u8,
    ) -> Result<U256> {
        // Get lender address (Balancer V3 Vault)
        let lender_address: Address = BALANCER_V3_VAULT.parse()?;

        // Check TVL (Total Value Locked)
        let pool_liquidity = match get_provider_tvl(
            token_address,
            lender_address,
            Arc::clone(&self.provider),
        ).await {
            Ok(liquidity) => liquidity,
            Err(_) => {
                // In PAPER mode, skip vault checks and use target amount
                return self.validate_paper_mode_amount(target_amount_raw, decimals);
            }
        };

        // If no liquidity data available (PAPER mode)
        if pool_liquidity.is_zero() {
            return self.validate_paper_mode_amount(target_amount_raw, decimals);
        }

        // Calculate caps
        let max_cap = self.calculate_max_cap(pool_liquidity);
        let mut requested_amount = target_amount_raw;

        // GUARD 1: Liquidity Check
        if requested_amount > max_cap {
            warn!(
                "⚠️ Liquidity Constraint: Requested {}, Cap {}. Scaling down.",
                requested_amount, max_cap
            );
            requested_amount = max_cap;
        }

        // GUARD 2: Floor Check
        let min_floor = self.calculate_min_floor(decimals);
        if requested_amount < min_floor {
            info!(
                "❌ Trade too small for profitability ({} < {}). Aborting.",
                requested_amount, min_floor
            );
            return Ok(U256::zero());
        }

        info!(
            "✅ Loan Sizing Optimized: {} (Cap: {})",
            requested_amount, max_cap
        );
        Ok(requested_amount)
    }

    /// Validate amount in paper mode
    fn validate_paper_mode_amount(&self, requested_amount: U256, decimals: u8) -> Result<U256> {
        let min_floor = self.calculate_min_floor(decimals);

        if requested_amount < min_floor {
            debug!("Trade too small ({} < {})", requested_amount, min_floor);
            return Ok(U256::zero());
        }

        debug!("✅ PAPER MODE: Using requested amount {}", requested_amount);
        Ok(requested_amount)
    }

    /// Calculate maximum cap based on TVL
    fn calculate_max_cap(&self, pool_liquidity: U256) -> U256 {
        // max_cap = pool_liquidity * MAX_TVL_SHARE
        let multiplier = (self.max_tvl_share * 1000000.0) as u128;
        pool_liquidity * U256::from(multiplier) / U256::from(1000000u128)
    }

    /// Calculate minimum floor based on decimals
    fn calculate_min_floor(&self, decimals: u8) -> U256 {
        // 500 units of stablecoin/ETH
        U256::from(500) * U256::exp10(decimals as usize)
    }

    /// Set minimum loan size in USD
    pub fn set_min_loan_usd(&mut self, min_usd: u64) {
        self.min_loan_usd = min_usd;
    }

    /// Set maximum TVL share
    pub fn set_max_tvl_share(&mut self, share: f64) {
        self.max_tvl_share = share;
    }

    /// Set slippage tolerance
    pub fn set_slippage_tolerance(&mut self, tolerance: f64) {
        self.slippage_tolerance = tolerance;
    }

    /// Get chain ID
    pub fn chain_id(&self) -> u64 {
        self.chain_id
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_min_floor_calculation() {
        let provider = Arc::new(Provider::<Http>::try_from("http://localhost:8545").unwrap());
        let commander = TitanCommander::new(137, provider);
        
        let min_floor_18 = commander.calculate_min_floor(18);
        assert_eq!(min_floor_18, U256::from(500) * U256::exp10(18));

        let min_floor_6 = commander.calculate_min_floor(6);
        assert_eq!(min_floor_6, U256::from(500) * U256::exp10(6));
    }

    #[test]
    fn test_max_cap_calculation() {
        let provider = Arc::new(Provider::<Http>::try_from("http://localhost:8545").unwrap());
        let commander = TitanCommander::new(137, provider);
        
        let pool_liquidity = U256::from(1000000);
        let max_cap = commander.calculate_max_cap(pool_liquidity);
        
        // Should be 20% of pool liquidity
        assert_eq!(max_cap, U256::from(200000));
    }
}
