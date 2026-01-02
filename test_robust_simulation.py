#!/usr/bin/env python3
"""
Test script for the robust 90-day simulation.
Quick validation that the system can run.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all imports work"""
    print("Testing imports...")
    
    try:
        from run_robust_90day_live_simulation import RobustLiveSimulation, SimulationMetrics
        print("✅ Main simulation imports successful")
    except Exception as e:
        print(f"❌ Main simulation import failed: {e}")
        return False
    
    try:
        from offchain.ml.brain import OmniBrain, ProfitEngine
        print("✅ Brain imports successful")
    except Exception as e:
        print(f"⚠️  Brain import failed (expected if not configured): {e}")
    
    try:
        from simulation.historical_data_fetcher import HistoricalDataFetcher
        print("✅ Data fetcher imports successful")
    except Exception as e:
        print(f"❌ Data fetcher import failed: {e}")
        return False
    
    return True


def test_metrics():
    """Test metrics tracking"""
    print("\nTesting metrics...")
    
    from run_robust_90day_live_simulation import SimulationMetrics
    
    metrics = SimulationMetrics()
    metrics.total_opportunities = 100
    metrics.executed_trades = 50
    metrics.successful_trades = 45
    metrics.total_profit_usd = 1000.0
    
    result = metrics.to_dict()
    
    assert result['total_opportunities'] == 100
    assert result['executed_trades'] == 50
    assert result['successful_trades'] == 45
    assert result['success_rate'] == 0.9
    
    print("✅ Metrics tracking works correctly")
    return True


def test_synthetic_data():
    """Test synthetic data generation"""
    print("\nTesting synthetic data generation...")
    
    from run_robust_90day_live_simulation import RobustLiveSimulation
    
    try:
        sim = RobustLiveSimulation(mode='PAPER', chain_id=137)
        data = sim._generate_synthetic_data(7)
        
        assert len(data) == 7
        assert 'date' in data.columns
        assert 'gas_price_gwei' in data.columns
        
        print(f"✅ Generated {len(data)} days of synthetic data")
        return True
    except Exception as e:
        print(f"❌ Synthetic data generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("ROBUST SIMULATION TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Metrics", test_metrics),
        ("Synthetic Data", test_synthetic_data),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(r for _, r in results)
    
    if all_passed:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
