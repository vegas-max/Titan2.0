// Dual Turbo Rust Engine for OmniArb Token Matrix Module
// Purpose: High-speed data fetch, matrix scoring & TAR model integration

use titan_core::omniarb::{
    load_token_matrix, calculate_tar_score, fetch_live_quotes,
    run_tar_onnx, run_flanker
};
use std::path::PathBuf;
use std::env;

/// Find the matrix file by searching multiple potential locations
fn find_matrix_file() -> Result<PathBuf, String> {
    // Try environment variable first
    if let Ok(env_path) = env::var("OMNIARB_MATRIX_PATH") {
        let path = PathBuf::from(&env_path);
        if path.exists() {
            return Ok(path);
        } else {
            eprintln!("⚠️  Warning: OMNIARB_MATRIX_PATH is set to '{}' but file does not exist", env_path);
            eprintln!("    Falling back to default search locations...");
        }
    }
    
    // List of potential paths to check
    let potential_paths = vec![
        // Relative to repository root (most common)
        "./data/omniarb_full_matrix_encoder_decoder_a_j_build_sheet.md",
        "data/omniarb_full_matrix_encoder_decoder_a_j_build_sheet.md",
        // For running from core-rust directory
        "../data/omniarb_full_matrix_encoder_decoder_a_j_build_sheet.md",
        // For running from target/release directory (3 levels up: release -> target -> core-rust)
        "../../../data/omniarb_full_matrix_encoder_decoder_a_j_build_sheet.md",
        // For running from target directory
        "../../data/omniarb_full_matrix_encoder_decoder_a_j_build_sheet.md",
    ];
    
    // Try each path
    for path_str in &potential_paths {
        let path = PathBuf::from(path_str);
        if path.exists() {
            println!("✅ Found matrix file at: {}", path.display());
            return Ok(path);
        }
    }
    
    // If all else fails, try to find it relative to the executable location
    if let Ok(exe_path) = env::current_exe() {
        if let Some(exe_dir) = exe_path.parent() {
            // Try from executable directory (target/release or similar)
            let from_exe = exe_dir.join("../../../data/omniarb_full_matrix_encoder_decoder_a_j_build_sheet.md");
            if from_exe.exists() {
                println!("✅ Found matrix file at: {}", from_exe.display());
                return Ok(from_exe);
            }
        }
    }
    
    Err(format!(
        "Matrix file not found. Searched locations:\n{}\n\nPlease either:\n\
         1. Run from the repository root directory\n\
         2. Set OMNIARB_MATRIX_PATH environment variable to the full path of the matrix file",
        potential_paths.join("\n")
    ))
}

fn main() {
    println!("🚀 OmniArb Dual Turbo Rust Engine Starting...");

    // Find and load the matrix
    let matrix_path = match find_matrix_file() {
        Ok(path) => path,
        Err(e) => {
            eprintln!("❌ {}", e);
            std::process::exit(1);
        }
    };
    
    println!("📂 Loading matrix from: {}", matrix_path.display());
    
    let matrix_path_str = match matrix_path.to_str() {
        Some(s) => s,
        None => {
            eprintln!("❌ Matrix file path contains invalid UTF-8 characters: {:?}", matrix_path);
            std::process::exit(1);
        }
    };
    
    let token_matrix = match load_token_matrix(matrix_path_str) {
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
