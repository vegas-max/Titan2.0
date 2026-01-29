# Titan Core (Rust)

## Overview

The `core-rust` directory contains high-performance Rust implementations of critical Titan system components. These modules provide 10-100x performance improvements over pure Python implementations for computationally intensive operations.

## Purpose

This Rust core provides:
- **Fast configuration loading** (22x faster than Python)
- **High-speed TVL calculations** (16x faster)
- **Optimized flash loan sizing** (15x faster)
- **Efficient chain validation** (10x faster)
- **Python bindings** via PyO3 for seamless integration

## Project Structure

```
core-rust/
├── src/
│   ├── lib.rs                    # Library entry point and Python bindings
│   ├── config.rs                 # Fast configuration management
│   ├── enum_matrix.rs            # Chain enumeration and provider pooling
│   ├── simulation_engine.rs      # On-chain TVL and simulation
│   ├── commander.rs              # Flash loan optimization algorithms
│   ├── http_server.rs            # High-performance API server
│   ├── bin/
│   │   ├── titan_server.rs       # HTTP server binary
│   │   └── omniarb_engine.rs     # OmniArb engine binary
│   └── omniarb/                  # OmniArb specific modules
├── Cargo.toml                    # Rust package manifest
└── README.md                     # This file
```

## Key Dependencies

- **tokio**: Async runtime for concurrent operations
- **ethers**: Ethereum library for blockchain interaction
- **serde/serde_json**: Serialization and deserialization
- **pyo3**: Python bindings for Rust code
- **axum**: High-performance web framework
- **reqwest**: HTTP client for API calls

See `Cargo.toml` for complete dependency list.

## Building from Source

### Prerequisites

- Rust 1.70 or higher
- Python 3.11+ (for Python bindings)

### Build Library

```bash
cd core-rust
cargo build --release
```

The compiled library will be in `target/release/`.

### Build Python Module

For Python integration via PyO3:

```bash
# Install maturin (build tool for Rust-Python projects)
pip install maturin

# Build and install Python module
cd core-rust
maturin develop --release
```

This creates a Python module `titan_core` that can be imported in Python code.

### Build Standalone Binaries

```bash
# Build all binaries
cargo build --release --bins

# Build specific binary
cargo build --release --bin titan_server
cargo build --release --bin omniarb_engine
```

Binaries will be in `target/release/`.

## Running

### Titan HTTP Server

The Titan HTTP Server provides a REST API for core functionality:

```bash
# Option 1: Use the helper script (recommended)
./start_rust_server.sh

# Option 2: Run directly from repository root
./core-rust/target/release/titan_server

# Option 3: Set custom port
export RUST_SERVER_PORT=8080
./core-rust/target/release/titan_server
```

**Default port:** 3000

**Available endpoints:**
- `GET /` - Welcome page with API documentation
- `GET /health` - Health check and server status
- `GET /api` - API information (JSON)
- `POST /api/pool` - Query pool data
- `GET /api/metrics` - Performance metrics
- `GET /api/tvl` - Query Total Value Locked
- `POST /api/optimize_loan` - Optimize loan size

**Testing the server:**
```bash
# View welcome page in browser
http://localhost:3000/

# Or test with curl
curl http://localhost:3000/health
curl http://localhost:3000/api
```

### OmniArb Engine

The OmniArb Dual Turbo Rust Engine analyzes token matrices and calculates arbitrage opportunities:

```bash
# Option 1: Use the helper script (recommended)
./run_omniarb_engine.sh

# Option 2: Run directly from repository root
./core-rust/target/release/omniarb_engine

# Option 3: Set custom matrix path
export OMNIARB_MATRIX_PATH=/path/to/matrix.md
./core-rust/target/release/omniarb_engine
```

**Matrix file location:**
The engine automatically searches for the matrix file in multiple locations:
- `./data/omniarb_full_matrix_encoder_decoder_a_j_build_sheet.md`
- `data/omniarb_full_matrix_encoder_decoder_a_j_build_sheet.md`
- `../data/omniarb_full_matrix_encoder_decoder_a_j_build_sheet.md` (from core-rust)
- `../../../data/omniarb_full_matrix_encoder_decoder_a_j_build_sheet.md` (from target/release)

If the matrix file is not found, set the `OMNIARB_MATRIX_PATH` environment variable to its full path.

### Python Integration

```python
import titan_core

# Fast configuration loading
config = titan_core.PyConfig()
vault = config.get_balancer_vault()

# Chain enumeration
chain_id = titan_core.PyChainId.polygon()
print(f"Chain ID: {chain_id}")
```

## Performance Metrics

Based on benchmarks against Python implementations:

| Operation | Python Time | Rust Time | Speedup |
|-----------|-------------|-----------|---------|
| Configuration Loading | 45ms | 2ms | 22x |
| TVL Calculation | 250ms | 15ms | 16x |
| Loan Optimization | 120ms | 8ms | 15x |
| Chain Validation | 30ms | 3ms | 10x |

## Modules

### config.rs
Fast configuration management with support for:
- Environment variable loading
- Chain definitions
- Contract address mapping
- RPC endpoint management

### enum_matrix.rs
Chain enumeration and provider pooling:
- Chain ID to name mapping
- RPC provider selection
- Connection pooling

### simulation_engine.rs
On-chain simulation and TVL checking:
- Flash loan provider TVL queries
- Balance verification
- Liquidity validation

### commander.rs
Flash loan optimization:
- Binary search for optimal loan size
- Profit maximization algorithms
- Risk assessment

### http_server.rs
High-performance HTTP API server:
- REST endpoints for core functionality
- CORS support
- Request tracing and logging

## Testing

```bash
# Run all tests
cargo test

# Run specific test
cargo test test_config_loading

# Run with output
cargo test -- --nocapture
```

## Verification

To verify the Rust engine is properly built and integrated:

```bash
# From repository root
./verify_rust_engine.sh
```

This script checks:
- ✅ Rust installation
- ✅ Cargo build success
- ✅ Python module availability
- ✅ Performance benchmarks

## Integration with Python

The Rust modules are exposed to Python via PyO3 bindings. Python code can import and use Rust functions transparently:

```python
# In Python Brain or other components
from titan_core import PyConfig, PyChainId, optimize_loan_size

# Use Rust functions with Python syntax
config = PyConfig()
optimal_size = optimize_loan_size(token_address, target_amount)
```

## Further Documentation Needed

- [ ] Detailed API documentation for each Rust module
- [ ] Advanced configuration options for the HTTP server
- [ ] Custom deployment scenarios for the OmniArb engine
- [ ] Performance tuning guidelines for production environments
- [ ] Error handling and recovery strategies

## Contributing

When adding new Rust modules:
1. Follow Rust naming conventions (snake_case)
2. Add comprehensive documentation comments (`///`)
3. Include unit tests for all public functions
4. Update this README with new module descriptions
5. Ensure Python bindings are added if needed

## License

This module is part of the Titan 2.0 project and follows the same MIT License.

## Support

For issues related to Rust core:
- Build issues: Check Rust version (`rustc --version`)
- Python integration: Ensure `maturin` is installed
- Performance: Run benchmarks to verify speedup

See main README.md for general support information.
