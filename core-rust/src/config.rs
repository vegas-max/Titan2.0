use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::env;

/// Balancer V3 Vault address (deterministic across all chains)
pub const BALANCER_V3_VAULT: &str = "0xbA1333333333a1BA1108E8412f11850A5C319bA9";

/// Chain configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChainConfig {
    pub name: String,
    pub rpc: String,
    pub wss: Option<String>,
    pub aave_pool: String,
    pub uniswap_router: String,
    pub curve_router: String,
    pub native: String,
}

/// DEX Router configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DexRouters {
    pub routers: HashMap<String, String>,
}

/// Intent-based bridge configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BridgeConfig {
    pub name: String,
    pub typical_time_seconds: u32,
    pub max_time_seconds: u32,
    pub fee_range_bps: Vec<u32>,
    pub description: String,
}

/// Main configuration manager
pub struct Config {
    pub chains: HashMap<u64, ChainConfig>,
    pub dex_routers: HashMap<u64, DexRouters>,
    pub intent_based_bridges: HashMap<String, BridgeConfig>,
    pub lifi_supported_chains: Vec<u64>,
}

impl Config {
    /// Load configuration from environment variables
    pub fn from_env() -> Result<Self, anyhow::Error> {
        dotenv::dotenv().ok();

        let chains = Self::load_chains()?;
        let dex_routers = Self::load_dex_routers();
        let intent_based_bridges = Self::load_bridges();
        let lifi_supported_chains = vec![
            1, 137, 42161, 10, 8453, 56, 43114, 250, 59144, 534352, 5000, 324, 81457, 42220, 204,
        ];

        Ok(Config {
            chains,
            dex_routers,
            intent_based_bridges,
            lifi_supported_chains,
        })
    }

    fn load_chains() -> Result<HashMap<u64, ChainConfig>, anyhow::Error> {
        let mut chains = HashMap::new();

        // Ethereum Mainnet
        chains.insert(
            1,
            ChainConfig {
                name: "ethereum".to_string(),
                rpc: env::var("RPC_ETHEREUM").unwrap_or_default(),
                wss: env::var("WSS_ETHEREUM").ok(),
                aave_pool: "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2".to_string(),
                uniswap_router: "0xE592427A0AEce92De3Edee1F18E0157C05861564".to_string(),
                curve_router: "0x99a58482BD75cbab83b27EC03CA68fF489b5788f".to_string(),
                native: "ETH".to_string(),
            },
        );

        // Polygon
        chains.insert(
            137,
            ChainConfig {
                name: "polygon".to_string(),
                rpc: env::var("RPC_POLYGON").unwrap_or_default(),
                wss: env::var("WSS_POLYGON").ok(),
                aave_pool: "0x794a61358D6845594F94dc1DB02A252b5b4814aD".to_string(),
                uniswap_router: "0xE592427A0AEce92De3Edee1F18E0157C05861564".to_string(),
                curve_router: "0x445FE580eF8d70FF569aB36e80c647af338db351".to_string(),
                native: "MATIC".to_string(),
            },
        );

        // Arbitrum
        chains.insert(
            42161,
            ChainConfig {
                name: "arbitrum".to_string(),
                rpc: env::var("RPC_ARBITRUM").unwrap_or_default(),
                wss: env::var("WSS_ARBITRUM").ok(),
                aave_pool: "0x794a61358D6845594F94dc1DB02A252b5b4814aD".to_string(),
                uniswap_router: "0xE592427A0AEce92De3Edee1F18E0157C05861564".to_string(),
                curve_router: "0x0000000000000000000000000000000000000000".to_string(),
                native: "ETH".to_string(),
            },
        );

        // Optimism
        chains.insert(
            10,
            ChainConfig {
                name: "optimism".to_string(),
                rpc: env::var("RPC_OPTIMISM").unwrap_or_default(),
                wss: env::var("WSS_OPTIMISM").ok(),
                aave_pool: "0x794a61358D6845594F94dc1DB02A252b5b4814aD".to_string(),
                uniswap_router: "0xE592427A0AEce92De3Edee1F18E0157C05861564".to_string(),
                curve_router: "0x0000000000000000000000000000000000000000".to_string(),
                native: "ETH".to_string(),
            },
        );

        // Base
        chains.insert(
            8453,
            ChainConfig {
                name: "base".to_string(),
                rpc: env::var("RPC_BASE").unwrap_or_default(),
                wss: env::var("WSS_BASE").ok(),
                aave_pool: "0x0000000000000000000000000000000000000000".to_string(),
                uniswap_router: "0x2626664c2603336E57B271c5C0b26F421741e481".to_string(),
                curve_router: "0x0000000000000000000000000000000000000000".to_string(),
                native: "ETH".to_string(),
            },
        );

        Ok(chains)
    }

    fn load_dex_routers() -> HashMap<u64, DexRouters> {
        let mut dex_routers = HashMap::new();

        // Ethereum DEX routers
        let mut eth_routers = HashMap::new();
        eth_routers.insert("UNIV2".to_string(), "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D".to_string());
        eth_routers.insert("SUSHI".to_string(), "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F".to_string());
        dex_routers.insert(1, DexRouters { routers: eth_routers });

        // Polygon DEX routers
        let mut poly_routers = HashMap::new();
        poly_routers.insert("QUICKSWAP".to_string(), "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff".to_string());
        poly_routers.insert("SUSHI".to_string(), "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506".to_string());
        dex_routers.insert(137, DexRouters { routers: poly_routers });

        dex_routers
    }

    fn load_bridges() -> HashMap<String, BridgeConfig> {
        let mut bridges = HashMap::new();

        bridges.insert(
            "across".to_string(),
            BridgeConfig {
                name: "Across Protocol".to_string(),
                typical_time_seconds: 30,
                max_time_seconds: 180,
                fee_range_bps: vec![5, 30],
                description: "Fastest intent-based bridge using solver network".to_string(),
            },
        );

        bridges.insert(
            "stargate".to_string(),
            BridgeConfig {
                name: "Stargate Finance".to_string(),
                typical_time_seconds: 60,
                max_time_seconds: 300,
                fee_range_bps: vec![6, 50],
                description: "Fast and reliable LayerZero-based bridge".to_string(),
            },
        );

        bridges.insert(
            "hop".to_string(),
            BridgeConfig {
                name: "Hop Protocol".to_string(),
                typical_time_seconds: 120,
                max_time_seconds: 600,
                fee_range_bps: vec![10, 100],
                description: "Popular bridge with good liquidity".to_string(),
            },
        );

        bridges
    }

    /// Get chain configuration by chain ID
    pub fn get_chain(&self, chain_id: u64) -> Option<&ChainConfig> {
        self.chains.get(&chain_id)
    }

    /// Check if chain is supported
    pub fn is_chain_supported(&self, chain_id: u64) -> bool {
        self.chains.contains_key(&chain_id)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_config_creation() {
        let config = Config::from_env().unwrap();
        assert!(config.chains.len() >= 5);
        assert_eq!(BALANCER_V3_VAULT, "0xbA1333333333a1BA1108E8412f11850A5C319bA9");
    }

    #[test]
    fn test_chain_support() {
        let config = Config::from_env().unwrap();
        assert!(config.is_chain_supported(1)); // Ethereum
        assert!(config.is_chain_supported(137)); // Polygon
        assert!(!config.is_chain_supported(999999)); // Invalid chain
    }
}
