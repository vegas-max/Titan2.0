// Dual Turbo Rust Engine for OmniArb Token Matrix Module
// Purpose: High-speed data fetch, matrix scoring & TAR model integration

pub mod matrix_parser;
pub mod tar_scorer;
pub mod data_fetcher;
pub mod model_bridge;

pub use matrix_parser::{load_token_matrix, TokenEntry};
pub use tar_scorer::calculate_tar_score;
pub use data_fetcher::{fetch_live_quotes, QuoteInfo};
pub use model_bridge::{run_tar_onnx, run_flanker};
