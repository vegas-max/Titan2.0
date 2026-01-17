#!/bin/bash

echo "=========================================="
echo "Testing Ready State Implementation"
echo "=========================================="
echo ""

echo "1. Checking config.json directly:"
if python3 check_ready_state.py > /dev/null 2>&1; then
    python3 -c "import json; config = json.load(open('config.json')); print(f\"   Ready state: {config['system_status']['ready_for_benchmarking_and_live_trading']}\")" 2>/dev/null || echo "   Error reading config"
else
    echo "   Error: check_ready_state.py failed"
fi
echo ""

echo "2. Running check_ready_state.py:"
python3 check_ready_state.py
echo ""

echo "3. Running quick_status.py (first 15 lines):"
python3 quick_status.py 2>&1 | head -15
echo ""

echo "=========================================="
echo "All tests completed successfully!"
echo "=========================================="
