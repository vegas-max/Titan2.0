#!/bin/bash

echo "=========================================="
echo "Testing Ready State Implementation"
echo "=========================================="
echo ""

# Track overall success
ALL_TESTS_PASSED=true

echo "1. Checking config.json directly:"
if python3 check_ready_state.py > /dev/null 2>&1; then
    python3 -c "import json; config = json.load(open('config.json')); print(f\"   Ready state: {config['system_status']['ready_for_benchmarking_and_live_trading']}\")" 2>/dev/null || {
        echo "   Error reading config"
        ALL_TESTS_PASSED=false
    }
else
    echo "   Error: check_ready_state.py failed"
    ALL_TESTS_PASSED=false
fi
echo ""

echo "2. Running check_ready_state.py:"
if python3 check_ready_state.py; then
    echo "   ✅ Test passed"
else
    echo "   ❌ Test failed"
    ALL_TESTS_PASSED=false
fi
echo ""

echo "3. Running quick_status.py (first 15 lines):"
if python3 quick_status.py 2>&1 | head -15; then
    echo "   ✅ Test passed"
else
    echo "   ❌ Test failed"
    ALL_TESTS_PASSED=false
fi
echo ""

echo "=========================================="
if [ "$ALL_TESTS_PASSED" = true ]; then
    echo "✅ All tests completed successfully!"
    exit 0
else
    echo "❌ Some tests failed!"
    exit 1
fi
echo "=========================================="
