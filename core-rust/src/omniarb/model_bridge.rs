use crate::omniarb::matrix_parser::TokenEntry;
use crate::omniarb::data_fetcher::QuoteInfo;

/// Run TAR ONNX model prediction
/// 
/// In production, this would load and run an actual ONNX model
/// For now, returns a simulated ML prediction based on features
/// 
/// # Arguments
/// * `entry` - Token matrix entry
/// * `quote` - Live quote information
/// 
/// # Returns
/// ML model prediction score (0-100)
pub fn run_tar_onnx(entry: &TokenEntry, quote: &QuoteInfo) -> f64 {
    // Simulate ONNX model inference
    // In production, would use tract or ort crate to run actual ONNX model
    
    // Extract features
    let features = extract_features(entry, quote);
    
    // Simple weighted model (placeholder for real ONNX)
    let prediction = features.liquidity_score * 0.3
        + features.spread_score * 0.3
        + features.bridge_score * 0.2
        + features.token_score * 0.2;
    
    prediction.min(100.0).max(0.0)
}

/// Run Flanker model prediction
/// 
/// Flanker model provides alternative risk assessment
/// In production, would be a separate ONNX model
/// 
/// # Arguments
/// * `entry` - Token matrix entry
/// * `quote` - Live quote information
/// 
/// # Returns
/// Flanker model prediction score (0-100)
pub fn run_flanker(entry: &TokenEntry, quote: &QuoteInfo) -> f64 {
    // Simulate Flanker model inference
    let features = extract_features(entry, quote);
    
    // Flanker focuses more on risk and volatility
    let prediction = features.bridge_score * 0.4
        + features.liquidity_score * 0.3
        + (100.0 - features.slippage_penalty) * 0.2
        + features.gas_efficiency * 0.1;
    
    prediction.min(100.0).max(0.0)
}

struct ModelFeatures {
    liquidity_score: f64,
    spread_score: f64,
    bridge_score: f64,
    token_score: f64,
    slippage_penalty: f64,
    gas_efficiency: f64,
}

fn extract_features(entry: &TokenEntry, quote: &QuoteInfo) -> ModelFeatures {
    // Liquidity score (normalized)
    let liquidity_score = entry.liquidity_score;
    
    // Spread score (0-100)
    let spread_score = (quote.spread_percentage * 20.0).min(100.0);
    
    // Bridge reliability score
    let bridge_score = get_bridge_score(&entry.bridge_protocol);
    
    // Token quality score
    let token_score = get_token_score(&entry.native_token);
    
    // Slippage penalty (inverse)
    let slippage_penalty = quote.slippage_estimate * 50.0;
    
    // Gas efficiency (inverse of cost, normalized)
    let gas_efficiency = (20.0 - quote.gas_cost_usd.min(20.0)) / 20.0 * 100.0;
    
    ModelFeatures {
        liquidity_score,
        spread_score,
        bridge_score,
        token_score,
        slippage_penalty,
        gas_efficiency,
    }
}

fn get_bridge_score(bridge: &str) -> f64 {
    match bridge {
        "STARGATE" | "ACROSS" | "CCIP" => 90.0,
        "HOP" | "SYNAPSE" | "LIFI" | "SOCKET" => 75.0,
        "LAYERZERO" | "CELER" => 65.0,
        _ => 50.0,
    }
}

fn get_token_score(token: &str) -> f64 {
    match token {
        "USDC" | "USDT" | "DAI" => 95.0,
        "ETH" | "WETH" | "WBTC" => 90.0,
        "MATIC" | "AVAX" | "BNB" | "OP" | "ARB" => 80.0,
        "LINK" | "UNI" | "AAVE" => 75.0,
        _ => 60.0,
    }
}

/// Load ONNX model from file (future enhancement)
/// 
/// This would be used when integrating actual ONNX models
#[allow(dead_code)]
fn load_onnx_model(_model_path: &str) -> Result<(), String> {
    // Placeholder for real ONNX integration
    // Would use tract or ort crate
    Err("ONNX integration not implemented yet".to_string())
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_tar_onnx() {
        let entry = TokenEntry {
            chain_origin: 1,
            chain_dest: 137,
            native_token: "USDC".to_string(),
            dex_origin: "UNISWAP_V3".to_string(),
            dex_dest: "QUICKSWAP".to_string(),
            bridge_protocol: "STARGATE".to_string(),
            liquidity_score: 95.0,
            fee_tier: 0.3,
        };
        
        let quote = QuoteInfo {
            spread_percentage: 1.5,
            slippage_estimate: 0.3,
            gas_cost_usd: 5.0,
            available_liquidity: 1000000.0,
        };
        
        let prediction = run_tar_onnx(&entry, &quote);
        assert!(prediction >= 0.0 && prediction <= 100.0);
    }
    
    #[test]
    fn test_flanker() {
        let entry = TokenEntry {
            chain_origin: 1,
            chain_dest: 137,
            native_token: "ETH".to_string(),
            dex_origin: "UNISWAP_V3".to_string(),
            dex_dest: "QUICKSWAP".to_string(),
            bridge_protocol: "ACROSS".to_string(),
            liquidity_score: 88.0,
            fee_tier: 0.15,
        };
        
        let quote = QuoteInfo {
            spread_percentage: 1.2,
            slippage_estimate: 0.5,
            gas_cost_usd: 8.0,
            available_liquidity: 500000.0,
        };
        
        let prediction = run_flanker(&entry, &quote);
        assert!(prediction >= 0.0 && prediction <= 100.0);
    }
}
