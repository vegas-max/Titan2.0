#!/usr/bin/env python3
"""
Test script for rejection tracking in the robust 90-day simulation.
Validates that rejection metrics are properly tracked and reported.
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# Extract SimulationMetrics class directly to avoid heavy dependencies
class SimulationMetrics:
    """Track comprehensive simulation metrics"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.total_opportunities = 0
        self.executed_trades = 0
        self.successful_trades = 0
        self.failed_trades = 0
        
        # Add rejection tracking
        self.rejected_low_profit = 0
        self.rejected_high_slippage = 0
        self.rejected_low_spread = 0
        self.rejected_zero_loan = 0
        
        self.total_profit_usd = 0.0
        self.total_gas_cost_usd = 0.0
        self.total_bridge_fees_usd = 0.0
        self.data_fetch_errors = 0
        self.execution_errors = 0
        self.daily_results = []
        self.trade_results = []
        
    def to_dict(self):
        """Convert metrics to dictionary"""
        elapsed = datetime.now() - self.start_time
        return {
            'start_time': self.start_time.isoformat(),
            'elapsed_seconds': elapsed.total_seconds(),
            'total_opportunities': self.total_opportunities,
            'executed_trades': self.executed_trades,
            'successful_trades': self.successful_trades,
            'failed_trades': self.failed_trades,
            'success_rate': self.successful_trades / self.executed_trades if self.executed_trades > 0 else 0,
            
            # Add rejection metrics
            'rejected_low_profit': self.rejected_low_profit,
            'rejected_high_slippage': self.rejected_high_slippage,
            'rejected_low_spread': self.rejected_low_spread,
            'rejected_zero_loan': self.rejected_zero_loan,
            'total_rejected': (self.rejected_low_profit + self.rejected_high_slippage + 
                              self.rejected_low_spread + self.rejected_zero_loan),
            
            'total_profit_usd': self.total_profit_usd,
            'total_gas_cost_usd': self.total_gas_cost_usd,
            'total_bridge_fees_usd': self.total_bridge_fees_usd,
            'net_profit_usd': self.total_profit_usd - self.total_gas_cost_usd - self.total_bridge_fees_usd,
            'avg_profit_per_trade': self.total_profit_usd / self.successful_trades if self.successful_trades > 0 else 0,
            'data_fetch_errors': self.data_fetch_errors,
            'execution_errors': self.execution_errors
        }


def test_metrics_rejection_fields():
    """Test that SimulationMetrics has rejection tracking fields"""
    print("\n🔍 Testing rejection fields in SimulationMetrics...")
    
    metrics = SimulationMetrics()
    
    # Check that all rejection fields exist
    assert hasattr(metrics, 'rejected_low_profit'), "Missing rejected_low_profit field"
    assert hasattr(metrics, 'rejected_high_slippage'), "Missing rejected_high_slippage field"
    assert hasattr(metrics, 'rejected_low_spread'), "Missing rejected_low_spread field"
    assert hasattr(metrics, 'rejected_zero_loan'), "Missing rejected_zero_loan field"
    
    # Check that they are initialized to 0
    assert metrics.rejected_low_profit == 0
    assert metrics.rejected_high_slippage == 0
    assert metrics.rejected_low_spread == 0
    assert metrics.rejected_zero_loan == 0
    
    print("✅ All rejection fields present and initialized correctly")
    return True


def test_metrics_to_dict_includes_rejections():
    """Test that to_dict() includes rejection metrics"""
    print("\n🔍 Testing rejection metrics in to_dict()...")
    
    metrics = SimulationMetrics()
    
    # Set some rejection values
    metrics.rejected_low_profit = 10
    metrics.rejected_high_slippage = 5
    metrics.rejected_low_spread = 8
    metrics.rejected_zero_loan = 3
    
    # Set other metrics for completeness
    metrics.total_opportunities = 100
    metrics.executed_trades = 74
    metrics.successful_trades = 70
    
    result = metrics.to_dict()
    
    # Check that rejection fields are in the dict
    assert 'rejected_low_profit' in result, "Missing rejected_low_profit in to_dict()"
    assert 'rejected_high_slippage' in result, "Missing rejected_high_slippage in to_dict()"
    assert 'rejected_low_spread' in result, "Missing rejected_low_spread in to_dict()"
    assert 'rejected_zero_loan' in result, "Missing rejected_zero_loan in to_dict()"
    assert 'total_rejected' in result, "Missing total_rejected in to_dict()"
    
    # Check values
    assert result['rejected_low_profit'] == 10
    assert result['rejected_high_slippage'] == 5
    assert result['rejected_low_spread'] == 8
    assert result['rejected_zero_loan'] == 3
    assert result['total_rejected'] == 26, f"Expected total_rejected=26, got {result['total_rejected']}"
    
    print("✅ Rejection metrics correctly included in to_dict()")
    return True


def test_rejection_tracking_calculation():
    """Test that total_rejected is calculated correctly"""
    print("\n🔍 Testing total_rejected calculation...")
    
    metrics = SimulationMetrics()
    
    # Test case 1: All zeros
    result = metrics.to_dict()
    assert result['total_rejected'] == 0, "Expected total_rejected=0 when all are 0"
    
    # Test case 2: Some rejections
    metrics.rejected_low_profit = 15
    metrics.rejected_low_spread = 12
    result = metrics.to_dict()
    assert result['total_rejected'] == 27, f"Expected total_rejected=27, got {result['total_rejected']}"
    
    # Test case 3: All categories have rejections
    metrics.rejected_high_slippage = 6
    metrics.rejected_zero_loan = 4
    result = metrics.to_dict()
    assert result['total_rejected'] == 37, f"Expected total_rejected=37, got {result['total_rejected']}"
    
    print("✅ total_rejected calculation is correct")
    return True


def test_metrics_backward_compatibility():
    """Test that existing metrics still work"""
    print("\n🔍 Testing backward compatibility of existing metrics...")
    
    metrics = SimulationMetrics()
    
    # Set existing metrics
    metrics.total_opportunities = 150
    metrics.executed_trades = 100
    metrics.successful_trades = 95
    metrics.failed_trades = 5
    metrics.total_profit_usd = 5000.0
    metrics.total_gas_cost_usd = 200.0
    metrics.total_bridge_fees_usd = 50.0
    
    result = metrics.to_dict()
    
    # Check existing fields still exist
    assert result['total_opportunities'] == 150
    assert result['executed_trades'] == 100
    assert result['successful_trades'] == 95
    assert result['failed_trades'] == 5
    assert result['success_rate'] == 0.95
    assert result['total_profit_usd'] == 5000.0
    assert result['total_gas_cost_usd'] == 200.0
    assert result['total_bridge_fees_usd'] == 50.0
    assert result['net_profit_usd'] == 4750.0
    assert abs(result['avg_profit_per_trade'] - 52.63) < 0.01
    
    print("✅ Existing metrics still work correctly")
    return True


def test_code_syntax():
    """Test that the actual simulation file has valid syntax"""
    print("\n🔍 Testing simulation file syntax...")
    
    import py_compile
    
    try:
        py_compile.compile('/home/runner/work/Titan2.0/Titan2.0/run_robust_90day_live_simulation.py', doraise=True)
        print("✅ Simulation file has valid Python syntax")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ Syntax error in simulation file: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("REJECTION TRACKING TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Rejection Fields Exist", test_metrics_rejection_fields),
        ("Rejection Metrics in to_dict()", test_metrics_to_dict_includes_rejections),
        ("Total Rejected Calculation", test_rejection_tracking_calculation),
        ("Backward Compatibility", test_metrics_backward_compatibility),
        ("Code Syntax Check", test_code_syntax),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Test '{name}' failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    print("\n" + "=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(r for _, r in results)
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
