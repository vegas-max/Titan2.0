use lazy_static::lazy_static;
use prometheus::{IntCounter, register_int_counter};

// Metrics
lazy_static! {
    pub static ref ROUTES_EVALUATED: IntCounter = 
        register_int_counter!("routes_evaluated", "Number of routes evaluated").unwrap();
    pub static ref ROUTES_BLOCKED: IntCounter = 
        register_int_counter!("routes_blocked", "Number of routes blocked").unwrap();
    pub static ref ROUTES_EXECUTED: IntCounter = 
        register_int_counter!("routes_executed", "Number of routes executed").unwrap();
}

// Type definitions
#[derive(Debug, Clone)]
pub struct TarResult {
    pub score: f64,
    pub confidence: f64,
}

#[derive(Debug, Clone)]
pub struct RouteExecutionGate {
    pub enabled: bool,
    pub min_profit_threshold: f64,
}

#[derive(Debug, Clone)]
pub struct ExecutionGate {
    pub enabled: bool,
    pub max_gas_price: u64,
}

#[derive(Debug, Clone)]
pub enum ExecutionDecision {
    Rejected(String),
    BuildOnly,
    SendPrivate,
}

#[derive(Debug, Clone)]
pub enum DispatchDecision {
    Execute,
    Skip(String),
}

// Helper function
pub fn record_rejection(reason: &str) {
    println!("Route rejected: {}", reason);
    // Additional logging or metrics can be added here
}

// Main dispatcher function
pub fn dispatch_route(
    tar: &TarResult,
    route_gate: &RouteExecutionGate,
    exec_gate: &ExecutionGate,
) -> DispatchDecision {
    ROUTES_EVALUATED.inc();

    // Check route gate
    if !route_gate.enabled {
        let reason = "Route gate disabled";
        ROUTES_BLOCKED.inc();
        record_rejection(reason);
        return DispatchDecision::Skip(reason.to_string());
    }

    // Check minimum profit threshold
    if tar.score < route_gate.min_profit_threshold {
        let reason = "Below minimum profit threshold";
        ROUTES_BLOCKED.inc();
        record_rejection(reason);
        return DispatchDecision::Skip(reason.to_string());
    }

    // Check execution decision
    let exec_decision = evaluate_execution(exec_gate);
    match exec_decision {
        ExecutionDecision::Rejected(reason) => {
            ROUTES_BLOCKED.inc();
            record_rejection(&reason);
            DispatchDecision::Skip(reason)
        }
        ExecutionDecision::BuildOnly => {
            // Build transaction for simulation/testing (still counts as executed for metrics)
            ROUTES_EXECUTED.inc();
            DispatchDecision::Execute
        }
        ExecutionDecision::SendPrivate => {
            // Execute via private mempool
            ROUTES_EXECUTED.inc();
            DispatchDecision::Execute
        }
    }
}

fn evaluate_execution(exec_gate: &ExecutionGate) -> ExecutionDecision {
    if !exec_gate.enabled {
        ExecutionDecision::Rejected("Execution gate disabled".to_string())
    } else {
        ExecutionDecision::SendPrivate
    }
}
