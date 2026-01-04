pub mod config;
pub mod enum_matrix;
pub mod simulation_engine;
pub mod commander;
pub mod http_server;
pub mod omniarb;

// Re-export main types
pub use config::{Config, ChainConfig, BALANCER_V3_VAULT};
pub use enum_matrix::{ChainId, ProviderManager};
pub use simulation_engine::{TitanSimulationEngine, get_provider_tvl};
pub use commander::TitanCommander;
pub use http_server::{start_server, create_router, AppState};
pub use omniarb::{load_token_matrix, calculate_tar_score, fetch_live_quotes, run_tar_onnx, run_flanker, TokenEntry, QuoteInfo};

// Python bindings
use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;

/// Python wrapper for Config
#[pyclass]
struct PyConfig {
    inner: Config,
}

#[pymethods]
impl PyConfig {
    #[new]
    fn new() -> PyResult<Self> {
        let config = Config::from_env()
            .map_err(|e| PyValueError::new_err(format!("Failed to load config: {}", e)))?;
        Ok(PyConfig { inner: config })
    }

    fn get_chain_name(&self, chain_id: u64) -> Option<String> {
        self.inner.get_chain(chain_id).map(|c| c.name.clone())
    }

    fn is_supported(&self, chain_id: u64) -> bool {
        self.inner.is_chain_supported(chain_id)
    }

    fn get_balancer_vault(&self) -> String {
        BALANCER_V3_VAULT.to_string()
    }
}

/// Python wrapper for ChainId
#[pyclass]
struct PyChainId;

#[pymethods]
impl PyChainId {
    #[staticmethod]
    fn ethereum() -> u64 {
        ChainId::Ethereum as u64
    }

    #[staticmethod]
    fn polygon() -> u64 {
        ChainId::Polygon as u64
    }

    #[staticmethod]
    fn arbitrum() -> u64 {
        ChainId::Arbitrum as u64
    }

    #[staticmethod]
    fn optimism() -> u64 {
        ChainId::Optimism as u64
    }

    #[staticmethod]
    fn base() -> u64 {
        ChainId::Base as u64
    }

    #[staticmethod]
    fn from_u64(value: u64) -> PyResult<String> {
        ChainId::from_u64(value)
            .map(|c| c.name().to_string())
            .ok_or_else(|| PyValueError::new_err(format!("Unknown chain ID: {}", value)))
    }
}

/// Python module initialization
#[pymodule]
fn titan_core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyConfig>()?;
    m.add_class::<PyChainId>()?;
    
    // Add constants
    m.add("BALANCER_V3_VAULT", BALANCER_V3_VAULT)?;
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    
    Ok(())
}
