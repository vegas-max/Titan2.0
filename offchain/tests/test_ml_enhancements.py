"""
Test Suite for ML Model Enhancements
======================================

Tests the enhanced machine learning components including:
- Market Forecaster with advanced features
- RL Optimizer with experience replay
- Feature Store with analytics
"""

import unittest
import sys
import os
import json
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from offchain.ml.cortex.forecaster import MarketForecaster
from offchain.ml.cortex.rl_optimizer import QLearningAgent
from offchain.ml.cortex.feature_store import FeatureStore


class TestMarketForecaster(unittest.TestCase):
    """Test enhanced Market Forecaster functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.forecaster = MarketForecaster(history_window=50)
    
    def test_initialization(self):
        """Test forecaster initialization"""
        self.assertIsNotNone(self.forecaster)
        self.assertEqual(len(self.forecaster.gas_history), 0)
        self.assertEqual(self.forecaster.window, 50)
    
    def test_ingest_gas(self):
        """Test gas price ingestion"""
        self.forecaster.ingest_gas(50.0)
        self.assertEqual(len(self.forecaster.gas_history), 1)
        self.assertEqual(list(self.forecaster.gas_history)[0], 50.0)
    
    def test_ingest_price(self):
        """Test price data ingestion"""
        self.forecaster.ingest_price(1500.0)
        self.assertEqual(len(self.forecaster.price_history), 1)
    
    def test_calculate_volatility(self):
        """Test volatility calculation"""
        # Add some price data
        prices = [1000, 1010, 1005, 1020, 1015, 1030, 1025, 1040, 1035, 1050]
        for price in prices:
            self.forecaster.ingest_price(price)
        
        volatility = self.forecaster.calculate_volatility()
        self.assertIsInstance(volatility, float)
        self.assertGreaterEqual(volatility, 0)
    
    def test_extract_features(self):
        """Test feature extraction"""
        # Add enough gas data
        for i in range(20):
            self.forecaster.ingest_gas(50 + i)
        
        features = self.forecaster.extract_features()
        self.assertIsNotNone(features)
        self.assertIn('gas_mean', features)
        self.assertIn('gas_std', features)
        self.assertIn('gas_slope', features)
        self.assertIn('volatility', features)
    
    def test_predict_gas_trend_stable(self):
        """Test gas trend prediction for stable market"""
        # Stable gas prices
        for i in range(20):
            self.forecaster.ingest_gas(50.0)
        
        trend = self.forecaster.predict_gas_trend()
        self.assertEqual(trend, "STABLE")
    
    def test_predict_gas_trend_rising(self):
        """Test gas trend prediction for rising market"""
        # Rising gas prices
        for i in range(20):
            self.forecaster.ingest_gas(50.0 + i * 2)
        
        trend = self.forecaster.predict_gas_trend()
        self.assertEqual(trend, "RISING_FAST")
    
    def test_predict_gas_trend_dropping(self):
        """Test gas trend prediction for dropping market"""
        # Dropping gas prices
        for i in range(20):
            self.forecaster.ingest_gas(100.0 - i * 2)
        
        trend = self.forecaster.predict_gas_trend()
        self.assertEqual(trend, "DROPPING_FAST")
    
    def test_predict_next_gas_price(self):
        """Test next gas price prediction"""
        # Add gas data with upward trend
        for i in range(20):
            self.forecaster.ingest_gas(50.0 + i)
        
        predicted = self.forecaster.predict_next_gas_price()
        self.assertIsInstance(predicted, float)
        self.assertGreater(predicted, 0)
    
    def test_predict_volatility(self):
        """Test volatility prediction"""
        # Low volatility - stable prices
        for i in range(20):
            self.forecaster.ingest_price(1000.0 + (i % 2))
        
        volatility = self.forecaster.predict_volatility()
        self.assertIn(volatility, ["LOW", "MEDIUM", "HIGH"])
    
    def test_should_wait_dropping_fast(self):
        """Test wait decision for dropping gas"""
        # Dropping gas prices
        for i in range(20):
            self.forecaster.ingest_gas(100.0 - i * 2)
        
        # Add low volatility prices
        for i in range(20):
            self.forecaster.ingest_price(1000.0)
        
        should_wait = self.forecaster.should_wait()
        self.assertTrue(should_wait)
    
    def test_get_metrics(self):
        """Test metrics retrieval"""
        # Add some data
        for i in range(20):
            self.forecaster.ingest_gas(50.0 + i)
        
        metrics = self.forecaster.get_metrics()
        self.assertIsInstance(metrics, dict)
        self.assertIn('predictions_made', metrics)
        self.assertIn('current_gas', metrics)
    
    def test_update_accuracy(self):
        """Test accuracy tracking"""
        # Make some predictions first
        for i in range(20):
            self.forecaster.ingest_gas(50.0 + i)
        
        # Make prediction to increment predictions_made
        self.forecaster.predict_gas_trend()
        
        initial_accuracy = self.forecaster.metrics["accuracy"]
        
        # Update with correct predictions
        self.forecaster.update_accuracy("STABLE", "STABLE")
        self.forecaster.update_accuracy("RISING_FAST", "RISING_FAST")
        
        # Accuracy should be calculated now
        self.assertGreater(self.forecaster.metrics["predictions_made"], 0)
        self.assertGreaterEqual(self.forecaster.metrics["accuracy"], initial_accuracy)


class TestQLearningAgent(unittest.TestCase):
    """Test enhanced RL Optimizer with experience replay"""
    
    def setUp(self):
        """Set up test fixtures with temporary directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_data_path = QLearningAgent.Q_TABLE_PATH
        QLearningAgent.Q_TABLE_PATH = os.path.join(self.temp_dir, "q_table.json")
        QLearningAgent.METRICS_PATH = os.path.join(self.temp_dir, "rl_metrics.json")
        QLearningAgent.REPLAY_BUFFER_PATH = os.path.join(self.temp_dir, "replay_buffer.json")
        
        self.agent = QLearningAgent(buffer_size=100)
    
    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.temp_dir)
        QLearningAgent.Q_TABLE_PATH = self.original_data_path
    
    def test_initialization(self):
        """Test agent initialization"""
        self.assertIsNotNone(self.agent)
        self.assertEqual(self.agent.learning_rate, 0.1)
        self.assertEqual(self.agent.discount_factor, 0.95)
    
    def test_recommend_parameters(self):
        """Test parameter recommendation"""
        params = self.agent.recommend_parameters(
            chain_id=1,
            volatility_level="MEDIUM",
            gas_gwei=50
        )
        
        self.assertIn('slippage', params)
        self.assertIn('priority', params)
        self.assertIsInstance(params['slippage'], int)
        self.assertIsInstance(params['priority'], int)
    
    def test_learn(self):
        """Test learning from experience"""
        action = {'slippage': 50, 'priority': 50}
        
        # Learn from positive reward
        self.agent.learn(
            chain_id=1,
            volatility="MEDIUM",
            action_taken=action,
            reward=10.0,
            gas_gwei=50
        )
        
        self.assertEqual(self.agent.metrics["total_episodes"], 1)
        self.assertEqual(self.agent.metrics["successful_trades"], 1)
    
    def test_learn_negative_reward(self):
        """Test learning from failed trade"""
        action = {'slippage': 100, 'priority': 100}
        
        # Learn from negative reward
        self.agent.learn(
            chain_id=1,
            volatility="HIGH",
            action_taken=action,
            reward=-5.0,
            gas_gwei=150
        )
        
        self.assertEqual(self.agent.metrics["failed_trades"], 1)
    
    def test_experience_replay(self):
        """Test experience replay buffer"""
        # Add multiple experiences
        for i in range(10):
            action = {'slippage': 50, 'priority': 50}
            self.agent.learn(
                chain_id=1,
                volatility="LOW",
                action_taken=action,
                reward=float(i),
                gas_gwei=30
            )
        
        self.assertEqual(len(self.agent.replay_buffer), 10)
        
        # Test batch replay learning
        self.agent.batch_replay_learning(batch_size=5)
    
    def test_epsilon_decay(self):
        """Test exploration rate decay"""
        initial_epsilon = self.agent.epsilon
        
        # Learn multiple times
        for i in range(20):
            action = {'slippage': 50, 'priority': 50}
            self.agent.learn(
                chain_id=1,
                volatility="MEDIUM",
                action_taken=action,
                reward=1.0,
                gas_gwei=50
            )
        
        # Epsilon should have decayed
        self.assertLess(self.agent.epsilon, initial_epsilon)
        self.assertGreaterEqual(self.agent.epsilon, self.agent.epsilon_min)
    
    def test_get_metrics(self):
        """Test metrics retrieval"""
        metrics = self.agent.get_metrics()
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('total_episodes', metrics)
        self.assertIn('q_table_size', metrics)
        self.assertIn('replay_buffer_size', metrics)
    
    def test_get_best_actions(self):
        """Test best actions retrieval"""
        # Learn some actions
        for i in range(5):
            action = {'slippage': 50, 'priority': 50 + i * 10}
            self.agent.learn(
                chain_id=1,
                volatility="MEDIUM",
                action_taken=action,
                reward=float(i),
                gas_gwei=50
            )
        
        best_actions = self.agent.get_best_actions_per_state(top_n=3)
        self.assertIsInstance(best_actions, dict)
    
    def test_state_discretization(self):
        """Test gas level discretization"""
        low_gas = self.agent._discretize_gas(15)
        self.assertEqual(low_gas, "LOW")
        
        normal_gas = self.agent._discretize_gas(35)
        self.assertEqual(normal_gas, "NORMAL")
        
        high_gas = self.agent._discretize_gas(100)
        self.assertEqual(high_gas, "HIGH")


class TestFeatureStore(unittest.TestCase):
    """Test enhanced Feature Store with analytics"""
    
    def setUp(self):
        """Set up test fixtures with temporary directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_data_path = FeatureStore.DATA_PATH
        FeatureStore.DATA_PATH = os.path.join(self.temp_dir, "history.csv")
        FeatureStore.SUMMARY_PATH = os.path.join(self.temp_dir, "summary.json")
        
        self.store = FeatureStore()
    
    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.temp_dir)
        FeatureStore.DATA_PATH = self.original_data_path
    
    def test_initialization(self):
        """Test feature store initialization"""
        self.assertIsNotNone(self.store)
        self.assertTrue(os.path.exists(FeatureStore.DATA_PATH))
    
    def test_log_observation(self):
        """Test logging market observations"""
        self.store.log_observation(
            chain_id=1,
            token="USDC",
            price=1.0,
            fee=0.5,
            gas=50,
            vol=0.5,
            volume=1000000,
            liquidity=5000000,
            spread=10,
            slippage=5
        )
        
        self.assertEqual(self.store.stats_cache["total_observations"], 1)
    
    def test_update_outcome(self):
        """Test updating trade outcomes"""
        import time
        
        # Log observation
        timestamp = time.time()
        self.store.log_observation(
            chain_id=1,
            token="USDC",
            price=1.0,
            fee=0.5,
            gas=50,
            vol=0.5
        )
        
        # Update outcome
        self.store.update_outcome(
            timestamp=timestamp,
            profit_realized=10.0,
            execution_time_ms=500,
            success=True
        )
        
        self.assertEqual(self.store.stats_cache["profitable_trades"], 1)
    
    def test_get_summary(self):
        """Test summary statistics retrieval"""
        summary = self.store.get_summary()
        
        self.assertIsInstance(summary, dict)
        self.assertIn('total_observations', summary)
        self.assertIn('profitable_trades', summary)
    
    def test_get_training_data(self):
        """Test training data retrieval"""
        # Log some data
        for i in range(10):
            self.store.log_observation(
                chain_id=1,
                token=f"TOKEN{i}",
                price=1.0 + i * 0.01,
                fee=0.5,
                gas=50 + i,
                vol=0.5
            )
        
        training_data = self.store.get_training_data(lookback_hours=24)
        self.assertIsNotNone(training_data)
    
    def test_get_performance_by_chain(self):
        """Test chain performance analytics"""
        import time
        
        # Log some successful trades on different chains
        for chain_id in [1, 137, 42161]:
            timestamp = time.time()
            self.store.log_observation(
                chain_id=chain_id,
                token="USDC",
                price=1.0,
                fee=0.5,
                gas=50,
                vol=0.5
            )
            self.store.update_outcome(
                timestamp=timestamp,
                profit_realized=10.0,
                success=True
            )
        
        performance = self.store.get_performance_by_chain()
        self.assertIsInstance(performance, dict)
    
    def test_get_performance_by_token(self):
        """Test token performance analytics"""
        import time
        
        # Log trades for different tokens
        for token in ["USDC", "USDT", "DAI"]:
            timestamp = time.time()
            self.store.log_observation(
                chain_id=1,
                token=token,
                price=1.0,
                fee=0.5,
                gas=50,
                vol=0.5
            )
            self.store.update_outcome(
                timestamp=timestamp,
                profit_realized=5.0,
                success=True
            )
        
        performance = self.store.get_performance_by_token()
        self.assertIsInstance(performance, dict)
    
    def test_get_feature_importance(self):
        """Test feature importance calculation"""
        import time
        
        # Log observations with outcomes
        for i in range(20):
            timestamp = time.time()
            self.store.log_observation(
                chain_id=1,
                token="USDC",
                price=1.0,
                fee=0.5,
                gas=50 + i,
                vol=0.5 + i * 0.1,
                volume=1000000,
                liquidity=5000000
            )
            self.store.update_outcome(
                timestamp=timestamp,
                profit_realized=float(i),
                success=i > 10
            )
        
        importance = self.store.get_feature_importance()
        self.assertIsInstance(importance, dict)


class TestIntegration(unittest.TestCase):
    """Integration tests for ML components working together"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Configure paths
        QLearningAgent.Q_TABLE_PATH = os.path.join(self.temp_dir, "q_table.json")
        QLearningAgent.METRICS_PATH = os.path.join(self.temp_dir, "rl_metrics.json")
        QLearningAgent.REPLAY_BUFFER_PATH = os.path.join(self.temp_dir, "replay_buffer.json")
        FeatureStore.DATA_PATH = os.path.join(self.temp_dir, "history.csv")
        FeatureStore.SUMMARY_PATH = os.path.join(self.temp_dir, "summary.json")
        
        self.forecaster = MarketForecaster()
        self.optimizer = QLearningAgent()
        self.feature_store = FeatureStore()
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)
    
    def test_full_trading_cycle(self):
        """Test complete trading cycle with all ML components"""
        import time
        
        # 1. Market scanning - gather data
        for i in range(20):
            self.forecaster.ingest_gas(50.0 + i)
            self.forecaster.ingest_price(1500.0 + i * 10)
        
        # 2. Get ML recommendations
        trend = self.forecaster.predict_gas_trend()
        volatility = self.forecaster.predict_volatility()
        
        # 3. RL optimizer recommends parameters
        params = self.optimizer.recommend_parameters(
            chain_id=1,
            volatility_level=volatility,
            gas_gwei=self.forecaster.predict_next_gas_price()
        )
        
        # 4. Log observation
        timestamp = time.time()
        self.feature_store.log_observation(
            chain_id=1,
            token="USDC",
            price=1500.0,
            fee=0.5,
            gas=70.0,
            vol=1.5
        )
        
        # 5. Simulate trade execution
        profit = 10.0
        
        # 6. Update all components
        self.feature_store.update_outcome(
            timestamp=timestamp,
            profit_realized=profit,
            success=True
        )
        
        self.optimizer.learn(
            chain_id=1,
            volatility=volatility,
            action_taken=params,
            reward=profit,
            gas_gwei=70.0
        )
        
        # Verify all components updated
        self.assertGreater(self.optimizer.metrics["total_episodes"], 0)
        self.assertGreater(self.feature_store.stats_cache["profitable_trades"], 0)


if __name__ == '__main__':
    unittest.main()
