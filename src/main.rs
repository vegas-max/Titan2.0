mod execution;

use execution::{ExecutionEngine, ExecutionResult, TarResult};
use std::sync::Arc;

fn main() {
    println!("Omni Scanner RS - Execution Engine");

    // Create execution engine
    let mut engine = ExecutionEngine::new();
    let stats_engine = Arc::new(ExecutionEngine::new());

    // Example: Process a route
    let tar = TarResult {
        score: 0.05,
        confidence: 0.9,
    };

    let decision = engine.dispatch(&tar);
    println!("Dispatch decision: {:?}", decision);

    // Example: Process execution results
    let result = ExecutionResult::new_success(
        100.50,
        5.25,
        "0x1234567890abcdef".to_string(),
    );

    if let Some(tx_hash) = &result.tx_hash {
        println!("Transaction executed: {}", tx_hash);
        println!("Profit: ${:.2}", result.actual_profit_usd);
    } else if let Some(error) = &result.error {
        println!("Execution failed: {}", error);
    }

    // Print statistics
    engine.print_stats();
    stats_engine.print_stats();

    println!("Execution engine initialized successfully");
}
