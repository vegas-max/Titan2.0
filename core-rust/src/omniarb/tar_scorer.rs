use crate::omniarb::matrix_parser::TokenEntry;
use crate::omniarb::data_fetcher::QuoteInfo;

// Token tier classifications
const TIER_1_TOKENS: &[&str] = &["USDC", "USDT", "DAI", "ETH", "WETH", "WBTC"];
const TIER_2_TOKENS: &[&str] = &["MATIC", "AVAX", "BNB", "OP", "ARB", "LINK"];

// Bridge tier classifications
const TIER_1_BRIDGES: &[&str] = &["STARGATE", "ACROSS", "CCIP", "LIFI"];
const TIER_2_BRIDGES: &[&str] = &["HOP", "SYNAPSE", "SOCKET", "LAYERZERO"];

/// Calculate TAR (Token Analysis & Risk) Score
/// 
/// Score components:
/// - T (Token Quality): Based on liquidity and token reputation (0-35 points)
/// - A (Arbitrage Efficiency): Based on fee tiers and spread potential (0-35 points)
/// - R (Risk Assessment): Based on bridge reliability and slippage (0-30 points)
/// 
/// # Arguments
/// * `entry` - Token matrix entry
/// * `quote` - Live quote information
/// 
/// # Returns
/// TAR score (0-100, higher is better)
pub fn calculate_tar_score(entry: &TokenEntry, quote: &QuoteInfo) -> f64 {
    let mut score = 0.0;
    
    // T - Token Quality (0-35 points)
    let token_score = calculate_token_quality(&entry.native_token, entry.liquidity_score);
    score += token_score;
    
    // A - Arbitrage Efficiency (0-35 points)
    let arb_score = calculate_arbitrage_efficiency(entry.fee_tier, quote.spread_percentage);
    score += arb_score;
    
    // R - Risk Assessment (0-30 points)
    let risk_score = calculate_risk_score(&entry.bridge_protocol, quote.slippage_estimate);
    score += risk_score;
    
    // Cap at 100
    score.min(100.0)
}

fn calculate_token_quality(token: &str, liquidity_score: f64) -> f64 {
    let mut score = 0.0;
    
    // High-value stable tokens
    if TIER_1_TOKENS.contains(&token) {
        score += 20.0; // Premium tokens
    } else if TIER_2_TOKENS.contains(&token) {
        score += 12.0; // Good tokens
    } else {
        score += 5.0;  // Other tokens
    }
    
    // Liquidity component (0-15 points)
    score += (liquidity_score / 100.0) * 15.0;
    
    score
}

fn calculate_arbitrage_efficiency(fee_tier: f64, spread_percentage: f64) -> f64 {
    let mut score = 0.0;
    
    // Lower fees are better (0-15 points)
    if fee_tier < 0.15 {
        score += 15.0;
    } else if fee_tier < 0.30 {
        score += 10.0;
    } else if fee_tier < 0.50 {
        score += 5.0;
    }
    
    // Higher spread is better (0-20 points)
    if spread_percentage > 2.0 {
        score += 20.0;
    } else if spread_percentage > 1.0 {
        score += 15.0;
    } else if spread_percentage > 0.5 {
        score += 10.0;
    } else if spread_percentage > 0.2 {
        score += 5.0;
    }
    
    score
}

fn calculate_risk_score(bridge: &str, slippage: f64) -> f64 {
    let mut score = 0.0;
    
    // Bridge reliability (0-15 points)
    if TIER_1_BRIDGES.contains(&bridge) {
        score += 15.0;
    } else if TIER_2_BRIDGES.contains(&bridge) {
        score += 10.0;
    } else {
        score += 5.0;
    }
    
    // Slippage penalty (0-15 points)
    if slippage < 0.5 {
        score += 15.0;
    } else if slippage < 1.0 {
        score += 10.0;
    } else if slippage < 2.0 {
        score += 5.0;
    }
    
    score
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_tar_score_calculation() {
        let entry = TokenEntry {
            chain_origin: 1,
            chain_dest: 137,
            native_token: "USDC".to_string(),
            dex_origin: "UNISWAP_V3".to_string(),
            dex_dest: "QUICKSWAP".to_string(),
            bridge_protocol: "STARGATE".to_string(),
            liquidity_score: 95.0,
            fee_tier: 0.1,
        };
        
        let quote = QuoteInfo {
            spread_percentage: 1.5,
            slippage_estimate: 0.3,
            gas_cost_usd: 5.0,
            available_liquidity: 1000000.0,
        };
        
        let score = calculate_tar_score(&entry, &quote);
        assert!(score > 70.0); // Should be a high score with these parameters
        assert!(score <= 100.0);
    }
}
