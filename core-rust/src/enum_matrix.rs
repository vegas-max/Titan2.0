use ethers::prelude::*;
use std::sync::Arc;
use std::collections::HashMap;
use anyhow::Result;

/// Chain ID enumeration
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
#[repr(u64)]
pub enum ChainId {
    Ethereum = 1,
    Polygon = 137,
    Arbitrum = 42161,
    Optimism = 10,
    Base = 8453,
    Bsc = 56,
    Avalanche = 43114,
    Fantom = 250,
    Linea = 59144,
    Scroll = 534352,
    Mantle = 5000,
    ZkSync = 324,
    Celo = 42220,
    OpBnb = 204,
}

impl ChainId {
    /// Convert u64 to ChainId
    pub fn from_u64(value: u64) -> Option<Self> {
        match value {
            1 => Some(ChainId::Ethereum),
            137 => Some(ChainId::Polygon),
            42161 => Some(ChainId::Arbitrum),
            10 => Some(ChainId::Optimism),
            8453 => Some(ChainId::Base),
            56 => Some(ChainId::Bsc),
            43114 => Some(ChainId::Avalanche),
            250 => Some(ChainId::Fantom),
            59144 => Some(ChainId::Linea),
            534352 => Some(ChainId::Scroll),
            5000 => Some(ChainId::Mantle),
            324 => Some(ChainId::ZkSync),
            42220 => Some(ChainId::Celo),
            204 => Some(ChainId::OpBnb),
            _ => None,
        }
    }

    /// Get chain name
    pub fn name(&self) -> &'static str {
        match self {
            ChainId::Ethereum => "ethereum",
            ChainId::Polygon => "polygon",
            ChainId::Arbitrum => "arbitrum",
            ChainId::Optimism => "optimism",
            ChainId::Base => "base",
            ChainId::Bsc => "bsc",
            ChainId::Avalanche => "avalanche",
            ChainId::Fantom => "fantom",
            ChainId::Linea => "linea",
            ChainId::Scroll => "scroll",
            ChainId::Mantle => "mantle",
            ChainId::ZkSync => "zksync",
            ChainId::Celo => "celo",
            ChainId::OpBnb => "opbnb",
        }
    }

    /// Get all supported chain IDs
    pub fn all() -> Vec<ChainId> {
        vec![
            ChainId::Ethereum,
            ChainId::Polygon,
            ChainId::Arbitrum,
            ChainId::Optimism,
            ChainId::Base,
            ChainId::Bsc,
            ChainId::Avalanche,
            ChainId::Fantom,
            ChainId::Linea,
            ChainId::Scroll,
            ChainId::Mantle,
            ChainId::ZkSync,
            ChainId::Celo,
            ChainId::OpBnb,
        ]
    }
}

/// Provider manager for managing Web3 connections
pub struct ProviderManager {
    providers: HashMap<u64, Arc<Provider<Http>>>,
}

impl ProviderManager {
    /// Create a new provider manager
    pub fn new() -> Self {
        Self {
            providers: HashMap::new(),
        }
    }

    /// Get provider for a specific chain
    pub async fn get_provider(&mut self, chain_id: u64, rpc_url: &str) -> Result<Arc<Provider<Http>>> {
        if let Some(provider) = self.providers.get(&chain_id) {
            return Ok(Arc::clone(provider));
        }

        let provider = Provider::<Http>::try_from(rpc_url)?;
        let provider = Arc::new(provider);
        self.providers.insert(chain_id, Arc::clone(&provider));

        Ok(provider)
    }

    /// Test connection to a specific chain
    pub async fn test_connection(&mut self, chain_id: u64, rpc_url: &str) -> Result<bool> {
        let provider = self.get_provider(chain_id, rpc_url).await?;
        
        match provider.get_block_number().await {
            Ok(block_number) => {
                println!("✅ Chain {}: Connected | Block: {}", chain_id, block_number);
                Ok(true)
            }
            Err(e) => {
                eprintln!("❌ Chain {}: Connection failed | Error: {}", chain_id, e);
                Ok(false)
            }
        }
    }

    /// Get all providers
    pub fn get_all_providers(&self) -> &HashMap<u64, Arc<Provider<Http>>> {
        &self.providers
    }

    /// Close all connections
    pub fn close_all(&mut self) {
        self.providers.clear();
    }
}

impl Default for ProviderManager {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_chain_id_conversion() {
        assert_eq!(ChainId::from_u64(1), Some(ChainId::Ethereum));
        assert_eq!(ChainId::from_u64(137), Some(ChainId::Polygon));
        assert_eq!(ChainId::from_u64(999999), None);
    }

    #[test]
    fn test_chain_names() {
        assert_eq!(ChainId::Ethereum.name(), "ethereum");
        assert_eq!(ChainId::Polygon.name(), "polygon");
        assert_eq!(ChainId::Arbitrum.name(), "arbitrum");
    }

    #[test]
    fn test_all_chains() {
        let chains = ChainId::all();
        assert_eq!(chains.len(), 14);
        assert!(chains.contains(&ChainId::Ethereum));
        assert!(chains.contains(&ChainId::Polygon));
    }
}
