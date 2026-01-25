use crate::omniarb::matrix_parser::TokenEntry;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// QuoteInfo using integer micro-units for precision
/// All percentages are in basis points (1/10000)
/// All USD values are in micro-dollars (1/1000000)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QuoteInfo {
    /// Spread percentage in basis points (1 bp = 0.01%)
    pub spread_bps: u64,
    /// Slippage estimate in basis points
    pub slippage_bps: u64,
    /// Gas cost in micro-USD (USD * 1e6)
    pub gas_cost_micro_usd: u64,
    /// Available liquidity in micro-USD
    pub liquidity_micro_usd: u128,
    /// Decimal precision for normalization
    pub token0_decimals: u8,
    pub token1_decimals: u8,
}

/// Fetch live bridge quotes for token matrix entries
/// 
/// In production, this would query real bridge APIs (LiFi, Socket, etc.)
/// For now, returns simulated quotes based on market conditions
/// 
/// # Arguments
/// * `token_matrix` - Vector of token entries
/// 
/// # Returns
/// Vector of quote information matching each entry
pub fn fetch_live_quotes(token_matrix: &[TokenEntry]) -> Vec<QuoteInfo> {
    token_matrix
        .iter()
        .map(|entry| simulate_bridge_quote(entry))
        .collect()
}

/// Simulate bridge quote based on entry parameters
/// 
/// This is a placeholder for real API integration
/// In production, would make actual HTTP calls to:
/// - LiFi API: https://li.quest/v1/quote
/// - Socket API: https://api.socket.tech/v2/quote
/// - Across API: https://across.to/api/suggested-fees
/// 
/// IMPORTANT: Uses integer math to avoid precision loss
fn simulate_bridge_quote(entry: &TokenEntry) -> QuoteInfo {
    // Convert liquidity_score and fee_tier to integer basis points
    // liquidity_score is 0-100, fee_tier is decimal percentage
    let liquidity_score_bps = (entry.liquidity_score * 100.0) as u64; // 0-10000 bps
    let fee_tier_bps = (entry.fee_tier * 100.0) as u64; // percentage to bps
    
    // Base spread calculation in basis points
    // base_spread = (liquidity/100 * 2) - fee_tier converted to bps
    let base_spread_bps = ((liquidity_score_bps * 2) / 100).saturating_sub(fee_tier_bps);
    
    // Add variance based on token and bridge (use integer multipliers)
    let token_factor_bps = get_token_volatility_bps(&entry.native_token);
    let bridge_factor_bps = get_bridge_efficiency_bps(&entry.bridge_protocol);
    
    // Multiply and scale: (spread * factor1 * factor2) / (10000 * 10000)
    let spread_bps = ((base_spread_bps as u128 * token_factor_bps as u128 * bridge_factor_bps as u128) 
                      / (10000 * 10000)) as u64;
    
    // Slippage in basis points (inversely proportional to liquidity)
    // slippage = ((100 - liquidity_score) / 100 * 2) * 10000 bps
    let slippage_bps = ((10000 - liquidity_score_bps) * 2 * 10000) / 10000;
    
    // Gas costs in micro-USD (USD * 1e6)
    let gas_cost_micro_usd = estimate_gas_cost_micro_usd(entry.chain_dest);
    
    // Available liquidity in micro-USD
    // liquidity_score (0-100) * 10000 USD = up to 1M USD
    let liquidity_micro_usd = (entry.liquidity_score * 10000.0 * 1_000_000.0) as u128;
    
    QuoteInfo {
        spread_bps,
        slippage_bps,
        gas_cost_micro_usd,
        liquidity_micro_usd,
        token0_decimals: 18, // Default to 18, should be fetched from chain
        token1_decimals: 18,
    }
}

/// Get token volatility factor in basis points (10000 = 1.0x)
fn get_token_volatility_bps(token: &str) -> u64 {
    let stable_tokens = ["USDC", "USDT", "DAI"];
    let low_vol_tokens = ["ETH", "WETH", "WBTC"];
    
    if stable_tokens.contains(&token) {
        10000 // Stablecoins - 1.0x (low volatility)
    } else if low_vol_tokens.contains(&token) {
        11000 // Major tokens - 1.1x (moderate volatility)
    } else {
        13000 // Alt tokens - 1.3x (higher volatility)
    }
}

/// Get bridge efficiency factor in basis points (10000 = 1.0x)
fn get_bridge_efficiency_bps(bridge: &str) -> u64 {
    let efficient_bridges = ["STARGATE", "ACROSS", "CCIP"];
    let standard_bridges = ["HOP", "SYNAPSE", "LIFI"];
    
    if efficient_bridges.contains(&bridge) {
        11500 // Premium bridges - 1.15x (better rates)
    } else if standard_bridges.contains(&bridge) {
        10000 // Standard bridges - 1.0x
    } else {
        9000 // Other bridges - 0.9x (less efficient)
    }
}

/// Estimate gas cost in micro-USD (USD * 1e6) for precision
fn estimate_gas_cost_micro_usd(chain_id: u64) -> u64 {
    // Gas costs by chain in micro-USD (1 USD = 1,000,000 micro-USD)
    let gas_costs: HashMap<u64, u64> = [
        (1, 15_000_000),      // Ethereum - $15 expensive
        (137, 500_000),       // Polygon - $0.50 cheap
        (42161, 800_000),     // Arbitrum - $0.80 cheap
        (10, 1_000_000),      // Optimism - $1.00 cheap
        (8453, 500_000),      // Base - $0.50 cheap
        (56, 300_000),        // BSC - $0.30 very cheap
        (43114, 2_000_000),   // Avalanche - $2.00 moderate
    ]
    .iter()
    .cloned()
    .collect();
    
    *gas_costs.get(&chain_id).unwrap_or(&5_000_000) // Default $5
}

/// Async version for real API integration (future enhancement)
/// 
/// This would be used when integrating with actual bridge APIs
#[allow(dead_code)]
async fn fetch_real_bridge_quote(
    _entry: &TokenEntry,
    _api_key: Option<&str>,
) -> Result<QuoteInfo, String> {
    // Placeholder for real implementation
    // Would use reqwest to query bridge APIs
    Err("Real API integration not implemented yet".to_string())
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_fetch_quotes() {
        let entries = vec![
            TokenEntry {
                chain_origin: 1,
                chain_dest: 137,
                native_token: "USDC".to_string(),
                dex_origin: "UNISWAP_V3".to_string(),
                dex_dest: "QUICKSWAP".to_string(),
                bridge_protocol: "STARGATE".to_string(),
                liquidity_score: 95.0,
                fee_tier: 0.3,
            },
        ];
        
        let quotes = fetch_live_quotes(&entries);
        assert_eq!(quotes.len(), 1);
        assert!(quotes[0].spread_bps < 100000); // Reasonable spread (< 1000%)
        assert!(quotes[0].slippage_bps < 100000); // Reasonable slippage
        assert!(quotes[0].gas_cost_micro_usd > 0); // Has gas cost
        assert!(quotes[0].liquidity_micro_usd > 0); // Has liquidity
    }
}
