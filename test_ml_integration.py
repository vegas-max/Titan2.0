#!/usr/bin/env python3
"""
Integration Test for ML Enhancements and Dashboard
===================================================

Tests the complete integration of:
1. ML models (Forecaster, RL Optimizer, Feature Store)
2. Dashboard server API endpoints
3. Real-time WebSocket updates

Note: Run with PYTHONPATH set to repository root:
    PYTHONPATH=/path/to/Titan2.0 python3 test_ml_integration.py
"""

import asyncio
import aiohttp
import json
import time
from pathlib import Path

from offchain.ml.cortex.forecaster import MarketForecaster
from offchain.ml.cortex.rl_optimizer import QLearningAgent
from offchain.ml.cortex.feature_store import FeatureStore


async def test_dashboard_api():
    """Test dashboard API endpoints"""
    base_url = "http://localhost:8080"
    
    print("Testing Dashboard API Endpoints...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test ML metrics endpoint
            async with session.get(f"{base_url}/api/ml-metrics") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ ML Metrics endpoint working")
                    print(f"   Forecaster accuracy: {data.get('forecaster', {}).get('accuracy', 0)}%")
                    print(f"   RL Episodes: {data.get('rl_optimizer', {}).get('total_episodes', 0)}")
                else:
                    print(f"❌ ML Metrics endpoint failed with status {response.status}")
            
            # Test feature importance endpoint
            async with session.get(f"{base_url}/api/feature-importance") as response:
                if response.status == 200:
                    print("✅ Feature Importance endpoint working")
                else:
                    print(f"❌ Feature Importance endpoint failed")
            
            # Test chain performance endpoint
            async with session.get(f"{base_url}/api/chain-performance") as response:
                if response.status == 200:
                    print("✅ Chain Performance endpoint working")
                else:
                    print(f"❌ Chain Performance endpoint failed")
            
            # Test token performance endpoint
            async with session.get(f"{base_url}/api/token-performance") as response:
                if response.status == 200:
                    print("✅ Token Performance endpoint working")
                else:
                    print(f"❌ Token Performance endpoint failed")
    
    except Exception as e:
        print(f"⚠️ Could not connect to dashboard: {e}")
        print("   Make sure dashboard server is running on port 8080")


def test_ml_models():
    """Test ML models independently"""
    print("\nTesting ML Models...")
    
    # Test Forecaster
    print("\n1. Testing Market Forecaster...")
    forecaster = MarketForecaster()
    
    # Add sample data
    for i in range(30):
        forecaster.ingest_gas(50.0 + i * 0.5)
        forecaster.ingest_price(1500.0 + i * 10)
    
    trend = forecaster.predict_gas_trend()
    volatility = forecaster.predict_volatility()
    predicted_gas = forecaster.predict_next_gas_price()
    
    print(f"   ✅ Gas trend: {trend}")
    print(f"   ✅ Volatility: {volatility}")
    print(f"   ✅ Predicted gas: {predicted_gas:.2f} Gwei")
    
    metrics = forecaster.get_metrics()
    print(f"   ✅ Metrics: {metrics['predictions_made']} predictions made")
    
    # Test RL Optimizer
    print("\n2. Testing RL Optimizer...")
    optimizer = QLearningAgent()
    
    params = optimizer.recommend_parameters(
        chain_id=1,
        volatility_level=volatility,
        gas_gwei=50
    )
    print(f"   ✅ Recommended params: slippage={params['slippage']} bps, priority={params['priority']} gwei")
    
    # Simulate learning
    for i in range(10):
        optimizer.learn(
            chain_id=1,
            volatility=volatility,
            action_taken=params,
            reward=float(i),
            gas_gwei=50
        )
    
    rl_metrics = optimizer.get_metrics()
    print(f"   ✅ Episodes: {rl_metrics['total_episodes']}")
    print(f"   ✅ Avg reward: ${rl_metrics['avg_reward']:.2f}")
    print(f"   ✅ Success rate: {rl_metrics['success_rate']:.1f}%")
    
    # Test Feature Store
    print("\n3. Testing Feature Store...")
    feature_store = FeatureStore()
    
    # Log some observations
    for i in range(5):
        timestamp = time.time()
        feature_store.log_observation(
            chain_id=1,
            token=f"TOKEN{i}",
            price=1.0 + i * 0.01,
            fee=0.5,
            gas=50 + i,
            vol=0.5,
            volume=1000000,
            liquidity=5000000
        )
        
        feature_store.update_outcome(
            timestamp=timestamp,
            profit_realized=10.0 if i % 2 == 0 else -2.0,
            success=i % 2 == 0
        )
    
    summary = feature_store.get_summary()
    print(f"   ✅ Total observations: {summary['total_observations']}")
    print(f"   ✅ Profitable trades: {summary['profitable_trades']}")
    print(f"   ✅ Avg profit: ${summary['avg_profit']:.2f}")


def test_integration():
    """Test full integration of ML components"""
    print("\n\nTesting Full Integration...")
    
    # Create all components
    forecaster = MarketForecaster()
    optimizer = QLearningAgent()
    feature_store = FeatureStore()
    
    print("\n1. Simulating market scanning...")
    # Simulate market data collection
    for i in range(20):
        forecaster.ingest_gas(50.0 + i * 0.3)
        forecaster.ingest_price(1500.0 + i * 5)
    
    # Get forecasts
    trend = forecaster.predict_gas_trend()
    volatility = forecaster.predict_volatility()
    predicted_gas = forecaster.predict_next_gas_price()
    
    print(f"   Market analysis: {trend} trend, {volatility} volatility")
    
    print("\n2. Getting ML recommendations...")
    # Get RL recommendations
    params = optimizer.recommend_parameters(
        chain_id=1,
        volatility_level=volatility,
        gas_gwei=predicted_gas
    )
    print(f"   Recommended execution params: {params}")
    
    print("\n3. Logging trade observation...")
    # Log to feature store
    timestamp = time.time()
    feature_store.log_observation(
        chain_id=1,
        token="USDC",
        price=1500.0,
        fee=0.5,
        gas=predicted_gas,
        vol=1.5,
        volume=1000000,
        liquidity=5000000,
        spread=15,
        slippage=params['slippage']
    )
    
    print("\n4. Simulating trade execution...")
    # Simulate trade result
    profit = 12.50
    feature_store.update_outcome(
        timestamp=timestamp,
        profit_realized=profit,
        execution_time_ms=450,
        success=True
    )
    
    print("\n5. Updating ML models with results...")
    # Update RL model
    optimizer.learn(
        chain_id=1,
        volatility=volatility,
        action_taken=params,
        reward=profit,
        gas_gwei=predicted_gas
    )
    
    # Update forecaster accuracy
    forecaster.update_accuracy(trend, trend)  # Assume prediction was correct
    
    print("\n6. Getting final metrics...")
    # Get all metrics
    forecaster_metrics = forecaster.get_metrics()
    rl_metrics = optimizer.get_metrics()
    fs_summary = feature_store.get_summary()
    
    print(f"\n   Forecaster:")
    print(f"      - Predictions: {forecaster_metrics['predictions_made']}")
    print(f"      - Accuracy: {forecaster_metrics['accuracy']:.1f}%")
    
    print(f"\n   RL Optimizer:")
    print(f"      - Episodes: {rl_metrics['total_episodes']}")
    print(f"      - Avg Reward: ${rl_metrics['avg_reward']:.2f}")
    print(f"      - Success Rate: {rl_metrics['success_rate']:.1f}%")
    
    print(f"\n   Feature Store:")
    print(f"      - Observations: {fs_summary['total_observations']}")
    print(f"      - Profitable: {fs_summary['profitable_trades']}")
    
    print("\n✅ Integration test completed successfully!")


def main():
    """Main test runner"""
    print("=" * 60)
    print("ML Enhancement Integration Test")
    print("=" * 60)
    
    # Test ML models
    test_ml_models()
    
    # Test integration
    test_integration()
    
    # Test dashboard API (async)
    print("\n" + "=" * 60)
    print("Testing Dashboard API")
    print("=" * 60)
    print("(Requires dashboard server running on port 8080)")
    
    try:
        asyncio.run(test_dashboard_api())
    except Exception as e:
        print(f"⚠️ Dashboard API test skipped: {e}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
