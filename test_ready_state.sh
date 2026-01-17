#!/bin/bash

echo "=========================================="
echo "Testing Ready State Implementation"
echo "=========================================="
echo ""

# Track overall success
ALL_TESTS_PASSED=true

echo "1. Checking config.json directly:"
if python3 check_ready_state.py > /dev/null 2>&1; then
    # Use check_ready_state.py for validation, which is cleaner than inline Python
    READY_VALUE=$(python3 -c "import json; config = json.load(open('config.json')); print(config['system_status']['ready_for_benchmarking_and_live_trading'])" 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "   Ready state: $READY_VALUE"
    else
        echo "   Error reading config"
        ALL_TESTS_PASSED=false
    fi
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
# Run quick_status.py first, capture exit code, then display output
QUICK_STATUS_OUTPUT=$(python3 quick_status.py 2>&1)
QUICK_STATUS_EXIT=$?
echo "$QUICK_STATUS_OUTPUT" | head -15
if [ $QUICK_STATUS_EXIT -eq 0 ]; then
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
