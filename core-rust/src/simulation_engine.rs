use ethers::prelude::*;
use std::sync::Arc;
use anyhow::Result;
use log::{warn, debug};

abigen!(
    ERC20,
    r#"[
        function balanceOf(address owner) external view returns (uint256)
        function decimals() external view returns (uint8)
    ]"#,
);

abigen!(
    UniswapV3QuoterV2,
    r#"[
        function quoteExactInputSingle(address tokenIn, address tokenOut, uint256 amountIn, uint24 fee, uint160 sqrtPriceLimitX96) external returns (uint256 amountOut)
    ]"#,
);

/// Titan Simulation Engine - Validates liquidity and simulates trades
pub struct TitanSimulationEngine {
    chain_id: u64,
    provider: Arc<Provider<Http>>,
}

impl TitanSimulationEngine {
    /// Create a new simulation engine
    pub fn new(chain_id: u64, provider: Arc<Provider<Http>>) -> Self {
        Self {
            chain_id,
            provider,
        }
    }

    /// Get total value locked (TVL) for a lender
    pub async fn get_lender_tvl(
        &self,
        token_address: Address,
        lender_address: Address,
    ) -> Result<U256> {
        let token = ERC20::new(token_address, Arc::clone(&self.provider));
        
        match token.balance_of(lender_address).call().await {
            Ok(balance) => {
                debug!("TVL for token {:?} at lender {:?}: {}", token_address, lender_address, balance);
                Ok(balance)
            }
            Err(e) => {
                warn!("Failed to get TVL: {}", e);
                Ok(U256::zero())
            }
        }
    }

    /// Get price impact by simulating a swap on Uniswap V3
    pub async fn get_price_impact(
        &self,
        token_in: Address,
        token_out: Address,
        amount: U256,
        fee: u32,
        quoter_address: Address,
    ) -> Result<U256> {
        let quoter = UniswapV3QuoterV2::new(quoter_address, Arc::clone(&self.provider));
        
        match quoter.quote_exact_input_single(token_in, token_out, amount, fee, U256::zero()).call().await {
            Ok(amount_out) => {
                debug!("Price impact simulation: {} in -> {} out", amount, amount_out);
                Ok(amount_out)
            }
            Err(e) => {
                warn!("Price impact simulation failed: {}", e);
                Ok(U256::zero())
            }
        }
    }

    /// Check if provider is connected
    pub async fn is_connected(&self) -> bool {
        self.provider.get_block_number().await.is_ok()
    }

    /// Get current block number
    pub async fn get_block_number(&self) -> Result<u64> {
        let block = self.provider.get_block_number().await?;
        Ok(block.as_u64())
    }
}

/// Standalone function for provider TVL checking (backward compatibility)
pub async fn get_provider_tvl(
    token_address: Address,
    lender_address: Address,
    provider: Arc<Provider<Http>>,
) -> Result<U256> {
    let token = ERC20::new(token_address, provider);
    
    match token.balance_of(lender_address).call().await {
        Ok(balance) => Ok(balance),
        Err(_) => Ok(U256::zero()),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_simulation_engine_creation() {
        // This test requires a real RPC endpoint
        // Skip in CI/CD environments
        if std::env::var("RPC_POLYGON").is_err() {
            return;
        }

        let rpc_url = std::env::var("RPC_POLYGON").unwrap();
        let provider = Provider::<Http>::try_from(rpc_url).unwrap();
        let provider = Arc::new(provider);

        let engine = TitanSimulationEngine::new(137, provider);
        assert_eq!(engine.chain_id, 137);
    }
}
