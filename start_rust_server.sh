#!/bin/bash
# Start Titan Rust HTTP Server

set -e

echo "🚀 Starting Titan Rust HTTP Server..."

# Navigate to Rust project directory
cd "$(dirname "$0")/core-rust"

# Set default port if not specified
export RUST_SERVER_PORT=${RUST_SERVER_PORT:-3000}

echo "📦 Building Rust server..."
cargo build --release --bin titan_server

echo "🔥 Starting server on port $RUST_SERVER_PORT..."
./target/release/titan_server
