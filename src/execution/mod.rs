pub mod dispatcher;

pub use dispatcher::{
    TarResult, 
    RouteExecutionGate, 
    ExecutionGate,
    DispatchDecision,
    dispatch_route,
    ROUTES_EVALUATED,
    ROUTES_BLOCKED,
    ROUTES_EXECUTED,
};

// ExecutionResult type
#[derive(Debug, Clone)]
pub struct ExecutionResult {
    pub success: bool,
    pub actual_profit_usd: f64,
    pub actual_gas_usd: f64,
    pub tx_hash: Option<String>,
    pub error: Option<String>,
}

impl ExecutionResult {
    pub fn new_success(profit: f64, gas: f64, tx_hash: String) -> Self {
        Self {
            success: true,
            actual_profit_usd: profit,
            actual_gas_usd: gas,
            tx_hash: Some(tx_hash),
            error: None,
        }
    }

    pub fn new_failure(error: String) -> Self {
        Self {
            success: false,
            actual_profit_usd: 0.0,
            actual_gas_usd: 0.0,
            tx_hash: None,
            error: Some(error),
        }
    }
}

// ExecutionEngine type
#[derive(Debug)]
pub struct ExecutionEngine {
    route_gate: RouteExecutionGate,
    exec_gate: ExecutionGate,
    total_executed: u64,
    total_blocked: u64,
}

impl ExecutionEngine {
    pub fn new() -> Self {
        Self {
            route_gate: RouteExecutionGate {
                enabled: true,
                min_profit_threshold: 0.01,
            },
            exec_gate: ExecutionGate {
                enabled: true,
                max_gas_price: 100_000_000_000, // 100 gwei
            },
            total_executed: 0,
            total_blocked: 0,
        }
    }

    pub fn dispatch(&mut self, tar: &TarResult) -> DispatchDecision {
        let decision = dispatch_route(tar, &self.route_gate, &self.exec_gate);
        match &decision {
            DispatchDecision::Execute => self.total_executed += 1,
            DispatchDecision::Skip(_) => self.total_blocked += 1,
        }
        decision
    }

    pub fn print_stats(&self) {
        println!("=== Execution Engine Stats ===");
        println!("Total Executed: {}", self.total_executed);
        println!("Total Blocked: {}", self.total_blocked);
        // Note: Prometheus counters are thread-safe and may include metrics from other engine instances
        println!("Routes Evaluated: {}", ROUTES_EVALUATED.get());
        println!("Routes Blocked: {}", ROUTES_BLOCKED.get());
        println!("Routes Executed: {}", ROUTES_EXECUTED.get());
        println!("==============================");
    }
}

impl Default for ExecutionEngine {
    fn default() -> Self {
        Self::new()
    }
}
