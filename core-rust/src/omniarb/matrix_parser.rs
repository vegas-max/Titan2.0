use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::Path;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TokenEntry {
    pub chain_origin: u64,
    pub chain_dest: u64,
    pub native_token: String,
    pub dex_origin: String,
    pub dex_dest: String,
    pub bridge_protocol: String,
    pub liquidity_score: f64,
    pub fee_tier: f64,
}

/// Load token matrix from markdown CSV file
/// 
/// # Arguments
/// * `path` - Path to the matrix file
/// 
/// # Returns
/// Vector of TokenEntry structs
pub fn load_token_matrix(path: &str) -> Result<Vec<TokenEntry>, String> {
    let file = File::open(Path::new(path))
        .map_err(|e| format!("Failed to open matrix file: {}", e))?;
    
    let reader = BufReader::new(file);
    let mut entries = Vec::new();
    let mut in_data_section = false;

    for line in reader.lines() {
        let line = line.map_err(|e| format!("Failed to read line: {}", e))?;
        let trimmed = line.trim();
        
        // Skip empty lines
        if trimmed.is_empty() {
            continue;
        }
        
        // Look for the data section
        if trimmed.contains("## Data Entries") {
            in_data_section = true;
            continue;
        }
        
        // Skip until we reach data section
        if !in_data_section {
            continue;
        }
        
        // Skip header line and markdown comments
        if trimmed.starts_with('#') || trimmed.starts_with("chain_origin") {
            continue;
        }
        
        // Parse CSV data
        let fields: Vec<&str> = trimmed.split(',').collect();
        if fields.len() == 8 {
            // Parse with error checking
            let chain_origin = fields[0].parse().unwrap_or_else(|e| {
                eprintln!("Warning: Invalid chain_origin '{}': {}", fields[0], e);
                0
            });
            let chain_dest = fields[1].parse().unwrap_or_else(|e| {
                eprintln!("Warning: Invalid chain_dest '{}': {}", fields[1], e);
                0
            });
            let liquidity_score = fields[6].parse().unwrap_or_else(|e| {
                eprintln!("Warning: Invalid liquidity_score '{}': {}", fields[6], e);
                0.0
            });
            let fee_tier = fields[7].parse().unwrap_or_else(|e| {
                eprintln!("Warning: Invalid fee_tier '{}': {}", fields[7], e);
                0.0
            });
            
            let entry = TokenEntry {
                chain_origin,
                chain_dest,
                native_token: fields[2].to_string(),
                dex_origin: fields[3].to_string(),
                dex_dest: fields[4].to_string(),
                bridge_protocol: fields[5].to_string(),
                liquidity_score,
                fee_tier,
            };
            entries.push(entry);
        }
    }
    
    if entries.is_empty() {
        return Err("No valid entries found in matrix file".to_string());
    }
    
    Ok(entries)
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_token_entry_creation() {
        let entry = TokenEntry {
            chain_origin: 1,
            chain_dest: 137,
            native_token: "USDC".to_string(),
            dex_origin: "UNISWAP_V3".to_string(),
            dex_dest: "QUICKSWAP".to_string(),
            bridge_protocol: "LIFI".to_string(),
            liquidity_score: 95.0,
            fee_tier: 0.3,
        };
        
        assert_eq!(entry.chain_origin, 1);
        assert_eq!(entry.native_token, "USDC");
    }
}
