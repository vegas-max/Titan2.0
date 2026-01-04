// Dual Turbo Rust Engine for OmniArb Token Matrix Module
// Purpose: High-speed data fetch, matrix scoring & TAR model integration

use titan_core::omniarb::{
    load_token_matrix, calculate_tar_score, fetch_live_quotes,
    run_tar_onnx, run_flanker
};

fn main() {
    println!("🚀 OmniArb Dual Turbo Rust Engine Starting...");

    // Load the matrix
    let matrix_path = "./data/omniarb_full_matrix_encoder_decoder_a_j_build_sheet.md";
    let token_matrix = match load_token_matrix(matrix_path) {
        Ok(matrix) => matrix,
        Err(e) => {
            eprintln!("❌ Matrix load failed: {}", e);
            std::process::exit(1);
        }
    };
    println!("✅ Token matrix loaded: {} entries", token_matrix.len());

    // Fetch bridge/live data
    let live_quotes = fetch_live_quotes(&token_matrix);
    println!("🌐 Bridge quotes fetched: {}", live_quotes.len());

    // Calculate TAR Score for each path
    let scored_routes: Vec<_> = token_matrix.iter().zip(live_quotes.iter())
        .map(|(entry, quote)| {
            let score = calculate_tar_score(entry, quote);
            let model_pred_tar = run_tar_onnx(entry, quote);
            let model_pred_flank = run_flanker(entry, quote);

            (entry.clone(), score, model_pred_tar, model_pred_flank)
        })
        .collect();

    // Filter top opportunities by TAR score >= 85.0
    let mut top_opportunities: Vec<_> = scored_routes.into_iter()
        .filter(|(_, score, _, _)| *score >= 85.0)
        .collect();

    top_opportunities.sort_by(|a, b| {
        // Use total_cmp for safe NaN handling
        b.1.total_cmp(&a.1)
    });

    println!("\n🔥 Top Arbitrage Routes (TAR Score >= 85):");
    println!("{:-<120}", "");
    println!("{:<15} {:<15} {:<10} {:<15} {:<15} {:<10} {:<10} {:<10}", 
        "Origin Chain", "Dest Chain", "Token", "Bridge", "TAR Score", "ONNX", "Flanker", "Liquidity");
    println!("{:-<120}", "");
    
    for (entry, score, tar_ml, flank_ml) in top_opportunities.iter().take(10) {
        println!("{:<15} {:<15} {:<10} {:<15} {:<10.2} {:<10.2} {:<10.2} {:<10.0}",
            format!("Chain-{}", entry.chain_origin),
            format!("Chain-{}", entry.chain_dest),
            entry.native_token,
            entry.bridge_protocol,
            score,
            tar_ml,
            flank_ml,
            entry.liquidity_score
        );
    }
    
    println!("\n📊 Summary Statistics:");
    println!("   Total routes analyzed: {}", token_matrix.len());
    println!("   High-quality routes (TAR >= 85): {}", 
        top_opportunities.len());
    println!("   Average TAR score (top routes): {:.2}", 
        if !top_opportunities.is_empty() {
            top_opportunities.iter().map(|(_, s, _, _)| s).sum::<f64>() / top_opportunities.len() as f64
        } else {
            0.0
        });
    
    println!("\n✨ OmniArb Dual Turbo Rust Engine Complete!");
}

// Note: All required submodules implement their corresponding structs & parsing logic
// Example: TokenEntry, QuoteInfo, and the `calculate_tar_score` logic using T/A/R weights
// Uses Serde for CSV/JSON parsing
// ONNX Runtime integration available via model_bridge module
