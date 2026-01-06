use axum::{
    extract::{State, Query},
    http::StatusCode,
    response::{IntoResponse, Json},
    routing::{get, post},
    Router,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::RwLock;
use tower_http::cors::CorsLayer;
use tracing::{info, error};
use ethers::prelude::*;

use crate::config::{Config, BALANCER_V3_VAULT};
use crate::enum_matrix::ProviderManager;
use crate::simulation_engine::get_provider_tvl;
use crate::commander::TitanCommander;

/// Server state shared across handlers
#[derive(Clone)]
pub struct AppState {
    pub config: Arc<Config>,
    pub provider_manager: Arc<RwLock<ProviderManager>>,
}

/// Health check response
#[derive(Serialize)]
pub struct HealthResponse {
    pub status: String,
    pub version: String,
    pub uptime_seconds: u64,
    pub rust_engine: bool,
}

/// Pool query request
#[derive(Deserialize)]
pub struct PoolQueryRequest {
    pub chain_id: u64,
    pub pool_address: String,
    pub dex_type: String,
}

/// Pool query response
#[derive(Serialize)]
pub struct PoolQueryResponse {
    pub pool_address: String,
    pub reserves: Option<Reserves>,
    pub error: Option<String>,
}

#[derive(Serialize)]
pub struct Reserves {
    pub reserve0: String,
    pub reserve1: String,
    pub token0: String,
    pub token1: String,
}

/// Performance metrics response
#[derive(Serialize)]
pub struct MetricsResponse {
    pub queries_total: u64,
    pub queries_success: u64,
    pub queries_failed: u64,
    pub avg_response_time_ms: f64,
    pub uptime_seconds: u64,
}

/// TVL query request
#[derive(Deserialize)]
pub struct TvlQueryRequest {
    pub chain_id: u64,
    pub token_address: String,
    pub lender_address: Option<String>,
}

/// TVL query response
#[derive(Serialize)]
pub struct TvlQueryResponse {
    pub tvl: String,
    pub chain_id: u64,
    pub token_address: String,
    pub lender_address: String,
    pub success: bool,
    pub error: Option<String>,
}

/// Loan optimization request
#[derive(Deserialize)]
pub struct LoanOptimizeRequest {
    pub chain_id: u64,
    pub token_address: String,
    pub target_amount: String,
    pub decimals: u8,
}

/// Loan optimization response
#[derive(Serialize)]
pub struct LoanOptimizeResponse {
    pub optimized_amount: String,
    pub chain_id: u64,
    pub success: bool,
    pub error: Option<String>,
}

/// Health check endpoint
async fn health_check() -> impl IntoResponse {
    let response = HealthResponse {
        status: "healthy".to_string(),
        version: env!("CARGO_PKG_VERSION").to_string(),
        uptime_seconds: 0, // TODO: Track actual uptime
        rust_engine: true,
    };
    
    Json(response)
}

/// Pool data query endpoint
async fn query_pool(
    State(_state): State<AppState>,
    Json(request): Json<PoolQueryRequest>,
) -> impl IntoResponse {
    info!(
        "Querying pool {} on chain {} ({})",
        request.pool_address, request.chain_id, request.dex_type
    );
    
    // TODO: Implement actual pool querying logic
    // For now, return a placeholder response
    
    let response = PoolQueryResponse {
        pool_address: request.pool_address.clone(),
        reserves: None,
        error: Some(format!(
            "Pool querying for DEX '{}' on chain {} is not implemented yet; this endpoint currently returns a placeholder response.",
            request.dex_type, request.chain_id
        )),
    };
    
    (StatusCode::NOT_IMPLEMENTED, Json(response))
}

/// Metrics endpoint
async fn metrics() -> impl IntoResponse {
    let response = MetricsResponse {
        queries_total: 0,
        queries_success: 0,
        queries_failed: 0,
        avg_response_time_ms: 0.0,
        uptime_seconds: 0,
    };
    
    Json(response)
}

/// TVL query endpoint - Get Total Value Locked for a token
async fn query_tvl(
    State(state): State<AppState>,
    Query(request): Query<TvlQueryRequest>,
) -> impl IntoResponse {
    info!(
        "Querying TVL for token {} on chain {}",
        request.token_address, request.chain_id
    );
    
    // Get chain config
    let chain_config = match state.config.get_chain(request.chain_id) {
        Some(config) => config,
        None => {
            let response = TvlQueryResponse {
                tvl: "0".to_string(),
                chain_id: request.chain_id,
                token_address: request.token_address.clone(),
                lender_address: "".to_string(),
                success: false,
                error: Some(format!("Chain {} not supported", request.chain_id)),
            };
            return (StatusCode::BAD_REQUEST, Json(response));
        }
    };
    
    // Use provided lender address or default to Balancer V3 Vault
    let lender_address = request.lender_address.unwrap_or_else(|| BALANCER_V3_VAULT.to_string());
    
    // Parse addresses
    let token_addr = match request.token_address.parse::<Address>() {
        Ok(addr) => addr,
        Err(e) => {
            let response = TvlQueryResponse {
                tvl: "0".to_string(),
                chain_id: request.chain_id,
                token_address: request.token_address.clone(),
                lender_address: lender_address.clone(),
                success: false,
                error: Some(format!("Invalid token address: {}", e)),
            };
            return (StatusCode::BAD_REQUEST, Json(response));
        }
    };
    
    let lender_addr = match lender_address.parse::<Address>() {
        Ok(addr) => addr,
        Err(e) => {
            let response = TvlQueryResponse {
                tvl: "0".to_string(),
                chain_id: request.chain_id,
                token_address: request.token_address.clone(),
                lender_address: lender_address.clone(),
                success: false,
                error: Some(format!("Invalid lender address: {}", e)),
            };
            return (StatusCode::BAD_REQUEST, Json(response));
        }
    };
    
    // Create provider
    let provider = match Provider::<Http>::try_from(&chain_config.rpc) {
        Ok(p) => Arc::new(p),
        Err(e) => {
            let response = TvlQueryResponse {
                tvl: "0".to_string(),
                chain_id: request.chain_id,
                token_address: request.token_address.clone(),
                lender_address: lender_address.clone(),
                success: false,
                error: Some(format!("Failed to create provider: {}", e)),
            };
            return (StatusCode::INTERNAL_SERVER_ERROR, Json(response));
        }
    };
    
    // Query TVL
    match get_provider_tvl(token_addr, lender_addr, provider).await {
        Ok(tvl) => {
            let response = TvlQueryResponse {
                tvl: tvl.to_string(),
                chain_id: request.chain_id,
                token_address: request.token_address.clone(),
                lender_address: lender_address.clone(),
                success: true,
                error: None,
            };
            (StatusCode::OK, Json(response))
        }
        Err(e) => {
            error!("TVL query failed: {}", e);
            let response = TvlQueryResponse {
                tvl: "0".to_string(),
                chain_id: request.chain_id,
                token_address: request.token_address.clone(),
                lender_address: lender_address.clone(),
                success: false,
                error: Some(format!("TVL query failed: {}", e)),
            };
            (StatusCode::INTERNAL_SERVER_ERROR, Json(response))
        }
    }
}

/// Loan optimization endpoint - Optimize loan size based on liquidity
async fn optimize_loan(
    State(state): State<AppState>,
    Json(request): Json<LoanOptimizeRequest>,
) -> impl IntoResponse {
    info!(
        "Optimizing loan for token {} on chain {}, target: {}",
        request.token_address, request.chain_id, request.target_amount
    );
    
    // Get chain config
    let chain_config = match state.config.get_chain(request.chain_id) {
        Some(config) => config,
        None => {
            let response = LoanOptimizeResponse {
                optimized_amount: "0".to_string(),
                chain_id: request.chain_id,
                success: false,
                error: Some(format!("Chain {} not supported", request.chain_id)),
            };
            return (StatusCode::BAD_REQUEST, Json(response));
        }
    };
    
    // Parse token address
    let token_addr = match request.token_address.parse::<Address>() {
        Ok(addr) => addr,
        Err(e) => {
            let response = LoanOptimizeResponse {
                optimized_amount: "0".to_string(),
                chain_id: request.chain_id,
                success: false,
                error: Some(format!("Invalid token address: {}", e)),
            };
            return (StatusCode::BAD_REQUEST, Json(response));
        }
    };
    
    // Parse target amount
    let target_amount = match request.target_amount.parse::<U256>() {
        Ok(amount) => amount,
        Err(e) => {
            let response = LoanOptimizeResponse {
                optimized_amount: "0".to_string(),
                chain_id: request.chain_id,
                success: false,
                error: Some(format!("Invalid target amount: {}", e)),
            };
            return (StatusCode::BAD_REQUEST, Json(response));
        }
    };
    
    // Create provider
    let provider = match Provider::<Http>::try_from(&chain_config.rpc) {
        Ok(p) => Arc::new(p),
        Err(e) => {
            let response = LoanOptimizeResponse {
                optimized_amount: "0".to_string(),
                chain_id: request.chain_id,
                success: false,
                error: Some(format!("Failed to create provider: {}", e)),
            };
            return (StatusCode::INTERNAL_SERVER_ERROR, Json(response));
        }
    };
    
    // Create commander and optimize
    let commander = TitanCommander::new(request.chain_id, provider);
    
    match commander.optimize_loan_size(token_addr, target_amount, request.decimals).await {
        Ok(optimized) => {
            let response = LoanOptimizeResponse {
                optimized_amount: optimized.to_string(),
                chain_id: request.chain_id,
                success: true,
                error: None,
            };
            (StatusCode::OK, Json(response))
        }
        Err(e) => {
            error!("Loan optimization failed: {}", e);
            let response = LoanOptimizeResponse {
                optimized_amount: "0".to_string(),
                chain_id: request.chain_id,
                success: false,
                error: Some(format!("Loan optimization failed: {}", e)),
            };
            (StatusCode::INTERNAL_SERVER_ERROR, Json(response))
        }
    }
}

/// Build and configure the HTTP server router
pub fn create_router(state: AppState) -> Router {
    Router::new()
        .route("/health", get(health_check))
        .route("/api/pool", post(query_pool))
        .route("/api/metrics", get(metrics))
        .route("/api/tvl", get(query_tvl))
        .route("/api/optimize_loan", post(optimize_loan))
        .layer(CorsLayer::permissive())
        .with_state(state)
}

/// Start the HTTP server
pub async fn start_server(config: Config, port: u16) -> Result<(), Box<dyn std::error::Error>> {
    info!("🚀 Starting Titan Rust HTTP Server on port {}", port);
    
    // Initialize provider manager
    let provider_manager = ProviderManager::new();
    
    // Create shared state
    let state = AppState {
        config: Arc::new(config),
        provider_manager: Arc::new(RwLock::new(provider_manager)),
    };
    
    // Build router
    let app = create_router(state);
    
    // Bind to address
    let addr = format!("0.0.0.0:{}", port);
    let listener = tokio::net::TcpListener::bind(&addr).await?;
    
    info!("✅ Rust HTTP Server listening on {}", addr);
    
    // Start server
    axum::serve(listener, app).await?;
    
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_config_default() {
        let config = Config::default();
        assert!(config.chains.is_empty() || config.chains.len() >= 5);
    }
    
    #[test]
    fn test_provider_manager_creation() {
        let _provider_manager = ProviderManager::new();
        // Just verify it can be created
    }
    
    #[test]
    fn test_router_creation() {
        let config = Config::default();
        let provider_manager = ProviderManager::new();
        
        let state = AppState {
            config: Arc::new(config),
            provider_manager: Arc::new(RwLock::new(provider_manager)),
        };
        
        let _app = create_router(state);
        // Just verify router can be created
    }
}
