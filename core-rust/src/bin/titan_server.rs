use titan_core::{Config, start_server};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};
use std::collections::HashMap;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize tracing
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "titan_server=info,tower_http=info".into()),
        )
        .with(tracing_subscriber::fmt::layer())
        .init();

    // Load configuration
    let config = match Config::from_env() {
        Ok(cfg) => cfg,
        Err(e) => {
            tracing::warn!("Could not load config from environment: {}, creating minimal config", e);
            // Create a minimal working config
            Config {
                chains: HashMap::new(),
                dex_routers: HashMap::new(),
                intent_based_bridges: HashMap::new(),
                lifi_supported_chains: vec![1, 137, 42161],
            }
        }
    };

    // Get port from environment or use default
    let port = std::env::var("RUST_SERVER_PORT")
        .ok()
        .and_then(|p| p.parse().ok())
        .unwrap_or(3000);

    tracing::info!("🚀 Starting Titan Rust HTTP Server on port {}", port);

    // Start the HTTP server
    start_server(config, port).await?;

    Ok(())
}
