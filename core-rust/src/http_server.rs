use axum::{
    extract::{State},
    http::StatusCode,
    response::{IntoResponse, Json},
    routing::{get, post},
    Router,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::RwLock;
use tower_http::cors::CorsLayer;
use tracing::info;

use crate::config::Config;
use crate::enum_matrix::ProviderManager;

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

/// Build and configure the HTTP server router
pub fn create_router(state: AppState) -> Router {
    Router::new()
        .route("/health", get(health_check))
        .route("/api/pool", post(query_pool))
        .route("/api/metrics", get(metrics))
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
    use axum::body::Body;
    use axum::http::{Request, StatusCode};
    use tower::ServiceExt;
    
    #[tokio::test]
    async fn test_health_check() {
        let config = Config::default();
        let provider_manager = ProviderManager::new();
        
        let state = AppState {
            config: Arc::new(config),
            provider_manager: Arc::new(RwLock::new(provider_manager)),
        };
        
        let app = create_router(state);
        
        let response = app
            .oneshot(Request::builder().uri("/health").body(Body::empty()).unwrap())
            .await
            .unwrap();
        
        assert_eq!(response.status(), StatusCode::OK);
    }
}
