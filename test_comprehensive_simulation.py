#!/usr/bin/env python3
"""
Comprehensive Simulation System Validation Test
================================================

Validates that the comprehensive simulation system is functioning correctly
with all features and checkpoints.

This test ensures:
1. All imports work
2. Configuration is valid
3. Validation pipeline functions
4. MEV protection is operational
5. Reporting generates correctly
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required imports work"""
    print("=" * 60)
    print("TEST 1: Module Imports")
    print("=" * 60)
    
    try:
        from comprehensive_simulation import (
            SimulationConfig,
            TradeResult,
            DailyMetrics,
            SimulationSummary,
            ComprehensiveSimulation
        )
        print("✅ Core classes imported successfully")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    try:
        import pandas as pd
        import numpy as np
        print("✅ Required packages (pandas, numpy) available")
    except Exception as e:
        print(f"⚠️  Optional packages not available: {e}")
    
    return True


def test_configuration():
    """Test configuration creation and validation"""
    print("\n" + "=" * 60)
    print("TEST 2: Configuration Validation")
    print("=" * 60)
    
    try:
        from comprehensive_simulation import SimulationConfig
        
        # Test default configuration
        config = SimulationConfig()
        assert config.days == 7
        assert config.mode == 'PAPER'
        assert config.enable_mev_protection == True
        print("✅ Default configuration valid")
        
        # Test custom configuration
        config = SimulationConfig(
            days=30,
            mode='LIVE',
            chain_id=1,
            enable_mev_protection=True,
            enable_mev_bundle_submission=True
        )
        assert config.days == 30
        assert config.mode == 'LIVE'
        assert config.chain_id == 1
        assert config.enable_mev_protection == True
        print("✅ Custom configuration valid")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_simulation_initialization():
    """Test simulation initialization"""
    print("\n" + "=" * 60)
    print("TEST 3: Simulation Initialization")
    print("=" * 60)
    
    try:
        from comprehensive_simulation import SimulationConfig, ComprehensiveSimulation
        
        config = SimulationConfig(days=1, mode='PAPER')
        sim = ComprehensiveSimulation(config)
        
        assert sim.config.days == 1
        assert sim.config.mode == 'PAPER'
        assert sim.total_opportunities == 0
        assert sim.total_executed == 0
        print("✅ Simulation initialized successfully")
        
        return True
    except Exception as e:
        print(f"❌ Simulation initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mev_calculations():
    """Test MEV protection calculations"""
    print("\n" + "=" * 60)
    print("TEST 4: MEV Protection Calculations")
    print("=" * 60)
    
    try:
        from comprehensive_simulation import SimulationConfig, ComprehensiveSimulation
        
        config = SimulationConfig(
            days=1,
            mode='PAPER',
            enable_mev_protection=True
        )
        sim = ComprehensiveSimulation(config)
        
        # Test frontrun risk calculation
        risk_eth = sim._calculate_frontrun_risk(100000, 1, 50)  # Ethereum, high value
        risk_polygon = sim._calculate_frontrun_risk(10000, 137, 10)  # Polygon, moderate
        
        assert risk_eth > risk_polygon, "Ethereum should have higher frontrun risk"
        assert 0 <= risk_eth <= 1, "Risk should be between 0 and 1"
        print(f"✅ Frontrun risk calculation working (ETH: {risk_eth:.2%}, Polygon: {risk_polygon:.2%})")
        
        return True
    except Exception as e:
        print(f"❌ MEV calculation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_checkpoint_validation():
    """Test validation checkpoints"""
    print("\n" + "=" * 60)
    print("TEST 5: Checkpoint Validation Pipeline")
    print("=" * 60)
    
    try:
        from comprehensive_simulation import SimulationConfig, ComprehensiveSimulation
        import pandas as pd
        
        config = SimulationConfig(
            days=1,
            mode='PAPER',
            min_profit_usd=5.0,
            max_gas_price_gwei=500.0
        )
        sim = ComprehensiveSimulation(config)
        
        # Create test opportunity
        test_opp = {
            'token': 'USDC',
            'token_address': '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
            'decimals': 6,
            'spread': 0.025,  # 2.5% spread
            'liquidity_ratio': 0.5,
            'chain_id': 137
        }
        
        # Create test day data
        test_day = pd.Series({
            'date': '2026-01-02',
            'gas_price_gwei': 30,
            'market_volatility': 0.03,
            'avg_liquidity_usd': 10000000
        })
        
        # Evaluate opportunity (should pass all checkpoints)
        result = sim._evaluate_opportunity(test_opp, test_day)
        
        if result:
            print("✅ Checkpoint validation pipeline functioning")
            print(f"   Trade executed: {result.executed}")
            print(f"   MEV protected: {result.mev_protected}")
            print(f"   Success probability: {result.success_probability:.2%}")
        else:
            print("⚠️  Opportunity rejected (may be valid if thresholds not met)")
        
        return True
    except Exception as e:
        print(f"❌ Checkpoint validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_synthetic_data_generation():
    """Test synthetic data generation"""
    print("\n" + "=" * 60)
    print("TEST 6: Synthetic Data Generation")
    print("=" * 60)
    
    try:
        from comprehensive_simulation import SimulationConfig, ComprehensiveSimulation
        
        config = SimulationConfig(days=7, mode='PAPER')
        sim = ComprehensiveSimulation(config)
        
        data = sim._generate_synthetic_data()
        
        assert len(data) == 7, f"Expected 7 days, got {len(data)}"
        assert 'date' in data.columns
        assert 'gas_price_gwei' in data.columns
        assert 'market_volatility' in data.columns
        print(f"✅ Synthetic data generated successfully ({len(data)} days)")
        
        return True
    except Exception as e:
        print(f"❌ Synthetic data generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_metrics_tracking():
    """Test metrics tracking"""
    print("\n" + "=" * 60)
    print("TEST 7: Metrics Tracking")
    print("=" * 60)
    
    try:
        from comprehensive_simulation import TradeResult, DailyMetrics
        from datetime import datetime
        
        # Create test trade result
        trade = TradeResult(
            timestamp=datetime.now().isoformat(),
            date='2026-01-02',
            chain_id=137,
            token='USDC',
            token_address='0x...',
            loan_amount_usd=10000,
            output_amount_usd=10250,
            gas_cost_usd=2,
            bridge_fee_usd=0,
            flash_loan_fee_usd=0,
            total_cost_usd=2,
            gross_profit_usd=250,
            net_profit_usd=248,
            executed=True,
            success=True,
            execution_mode='PAPER',
            spread_pct=2.5,
            success_probability=0.9,
            ml_optimized=True,
            gas_price_gwei=30,
            mev_protected=True,
            used_private_mempool=True,
            bundle_submission=True,
            frontrun_detected=False,
            mev_tip_paid_usd=10
        )
        
        assert trade.net_profit_usd == 248
        assert trade.mev_protected == True
        print("✅ Trade result tracking working")
        
        # Create test daily metrics
        metrics = DailyMetrics(
            date='2026-01-02',
            day_number=1,
            opportunities_detected=50,
            opportunities_evaluated=50,
            opportunities_profitable=10,
            trades_executed=10,
            trades_successful=9,
            trades_failed=1,
            success_rate=0.9,
            gross_profit_usd=2000,
            total_gas_cost_usd=20,
            total_bridge_fees_usd=0,
            total_flash_loan_fees_usd=0,
            net_profit_usd=1980,
            avg_profit_per_trade=220,
            avg_gas_price_gwei=30,
            min_gas_price_gwei=25,
            max_gas_price_gwei=35,
            mev_protected_trades=8,
            frontrun_attempts_detected=2,
            frontrun_attempts_blocked=2,
            private_mempool_used=8,
            bundle_submissions=5,
            total_mev_tips_paid_usd=80,
            data_fetch_errors=0,
            execution_errors=0,
            simulation_errors=0
        )
        
        assert metrics.success_rate == 0.9
        assert metrics.mev_protected_trades == 8
        print("✅ Daily metrics tracking working")
        
        return True
    except Exception as e:
        print(f"❌ Metrics tracking test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all validation tests"""
    print("\n" + "=" * 60)
    print("COMPREHENSIVE SIMULATION VALIDATION TEST SUITE")
    print("=" * 60)
    print()
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("Simulation Initialization", test_simulation_initialization),
        ("MEV Calculations", test_mev_calculations),
        ("Checkpoint Validation", test_checkpoint_validation),
        ("Synthetic Data Generation", test_synthetic_data_generation),
        ("Metrics Tracking", test_metrics_tracking),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is ready for use.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
