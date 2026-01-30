#!/bin/bash
# Build and run the OmniArb Dual Turbo Rust Engine

set -e

echo "======================================"
echo "  OmniArb Rust Engine Builder"
echo "======================================"
echo ""

cd "$(dirname "$0")/core-rust"

echo "🔨 Building OmniArb Rust Engine..."
cargo build --release --bin omniarb_engine

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo ""
    echo "🚀 Running OmniArb engine..."
    echo ""
    cd ..
    ./core-rust/target/release/omniarb_engine
else
    echo "❌ Build failed!"
    exit 1
fi
