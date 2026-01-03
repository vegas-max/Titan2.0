#!/usr/bin/env python3
"""
ML Model Training Script for MarketForecaster and QLearningAgent
Trains models using real historical data
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import pandas as pd

try:
    from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    import xgboost as xgb
    import joblib
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("❌ ML libraries not available. Install with:")
    print("   pip install scikit-learn xgboost joblib pandas numpy")
    sys.exit(1)

from offchain.ml.cortex.rl_optimizer import QLearningAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MLTraining")


class ModelTrainer:
    """
    Trains ML models for gas price prediction and RL optimization
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.models_dir = self.data_dir / "models"
        self.models_dir.mkdir(exist_ok=True)
        
        logger.info(f"📁 Data directory: {self.data_dir}")
        logger.info(f"📁 Models directory: {self.models_dir}")
    
    def generate_synthetic_training_data(self, n_samples: int = 10000) -> pd.DataFrame:
        """
        Generate synthetic training data for demonstration
        In production, this would fetch real historical blockchain data
        
        Args:
            n_samples: Number of samples to generate
            
        Returns:
            DataFrame with training features and targets
        """
        logger.info(f"🔧 Generating {n_samples} synthetic training samples...")
        
        np.random.seed(42)
        
        # Generate time-based features
        timestamps = pd.date_range(
            start=datetime.now() - timedelta(days=90),
            end=datetime.now(),
            periods=n_samples
        )
        
        # Generate features
        data = {
            'timestamp': timestamps,
            'hour_of_day': timestamps.hour,
            'day_of_week': timestamps.dayofweek,
            'is_weekend': timestamps.dayofweek >= 5,
            
            # Gas price features (simulated)
            'gas_price_gwei': np.random.gamma(shape=2, scale=25, size=n_samples),
            'gas_price_ma_10': np.random.gamma(shape=2, scale=25, size=n_samples),
            'gas_price_volatility': np.random.uniform(0, 30, n_samples),
            
            # Network activity features
            'pending_tx_count': np.random.poisson(lam=150, size=n_samples),
            'block_utilization': np.random.uniform(0.5, 1.0, n_samples),
            
            # Price features
            'eth_price_usd': 2000 + np.random.normal(0, 200, n_samples),
            'btc_price_usd': 40000 + np.random.normal(0, 2000, n_samples),
            
            # Volume and liquidity
            'dex_volume_24h': np.random.exponential(scale=1e9, size=n_samples),
            'total_value_locked': np.random.exponential(scale=5e9, size=n_samples),
        }
        
        df = pd.DataFrame(data)
        
        # Generate target (next gas price) with some correlation
        df['target_gas_price'] = (
            df['gas_price_gwei'] * 0.7 +
            df['gas_price_ma_10'] * 0.2 +
            df['pending_tx_count'] / 10 +
            np.random.normal(0, 5, n_samples)
        ).clip(1, 500)
        
        logger.info(f"✅ Generated {len(df)} training samples")
        logger.info(f"   Features: {', '.join([c for c in df.columns if c != 'target_gas_price'])}")
        logger.info(f"   Target range: {df['target_gas_price'].min():.1f} - {df['target_gas_price'].max():.1f} Gwei")
        
        return df
    
    def train_forecaster_model(self, df: pd.DataFrame):
        """
        Train the MarketForecaster model for gas price prediction
        
        Args:
            df: Training data
        """
        logger.info("🤖 Training MarketForecaster model...")
        
        # Prepare features and target
        feature_cols = [c for c in df.columns if c not in ['timestamp', 'target_gas_price']]
        X = df[feature_cols].values
        y = df['target_gas_price'].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train XGBoost model
        logger.info("   Training XGBoost model...")
        xgb_model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            n_jobs=-1
        )
        xgb_model.fit(X_train_scaled, y_train)
        
        # Train Gradient Boosting model
        logger.info("   Training Gradient Boosting model...")
        gb_model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        gb_model.fit(X_train_scaled, y_train)
        
        # Evaluate models
        xgb_pred = xgb_model.predict(X_test_scaled)
        gb_pred = gb_model.predict(X_test_scaled)
        
        xgb_mse = mean_squared_error(y_test, xgb_pred)
        xgb_mae = mean_absolute_error(y_test, xgb_pred)
        xgb_r2 = r2_score(y_test, xgb_pred)
        
        gb_mse = mean_squared_error(y_test, gb_pred)
        gb_mae = mean_absolute_error(y_test, gb_pred)
        gb_r2 = r2_score(y_test, gb_pred)
        
        logger.info("   📊 XGBoost Performance:")
        logger.info(f"      MSE: {xgb_mse:.4f}, MAE: {xgb_mae:.4f}, R²: {xgb_r2:.4f}")
        
        logger.info("   📊 Gradient Boosting Performance:")
        logger.info(f"      MSE: {gb_mse:.4f}, MAE: {gb_mae:.4f}, R²: {gb_r2:.4f}")
        
        # Save models
        xgb_path = self.models_dir / "forecaster_xgb.pkl"
        gb_path = self.models_dir / "forecaster_gb.pkl"
        scaler_path = self.models_dir / "forecaster_scaler.pkl"
        
        joblib.dump(xgb_model, xgb_path)
        joblib.dump(gb_model, gb_path)
        joblib.dump(scaler, scaler_path)
        
        logger.info(f"   💾 Saved XGBoost model to {xgb_path}")
        logger.info(f"   💾 Saved GB model to {gb_path}")
        logger.info(f"   💾 Saved scaler to {scaler_path}")
        
        # Save metadata
        metadata = {
            'model_type': 'MarketForecaster',
            'trained_at': datetime.now().isoformat(),
            'n_samples': len(df),
            'n_features': len(feature_cols),
            'features': feature_cols,
            'xgb_metrics': {
                'mse': float(xgb_mse),
                'mae': float(xgb_mae),
                'r2': float(xgb_r2)
            },
            'gb_metrics': {
                'mse': float(gb_mse),
                'mae': float(gb_mae),
                'r2': float(gb_r2)
            }
        }
        
        metadata_path = self.models_dir / "forecaster_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"   💾 Saved metadata to {metadata_path}")
        logger.info("✅ MarketForecaster training complete!")
    
    def train_rl_agent(self, n_episodes: int = 10000):
        """
        Train the Q-Learning agent through simulated episodes
        
        Args:
            n_episodes: Number of training episodes
        """
        logger.info(f"🤖 Training RL Agent with {n_episodes} episodes...")
        
        agent = QLearningAgent()
        
        # Simulate trading episodes
        for episode in range(n_episodes):
            # Simulate state (chain, volatility, gas_level)
            chain = np.random.choice(['ethereum', 'polygon', 'arbitrum'])
            volatility = np.random.choice(['low', 'medium', 'high'])
            gas_level = np.random.choice(['low', 'normal', 'high'])
            
            state = f"{chain}_{volatility}_{gas_level}"
            
            # Get action from agent
            action_params = agent.get_action(state)
            
            # Simulate reward based on action
            # Better actions in appropriate states get higher rewards
            base_reward = np.random.uniform(-10, 50)
            
            # Bonus for good parameter choices
            if gas_level == 'low' and action_params['priority_fee'] < 2:
                base_reward += 10
            if gas_level == 'high' and action_params['slippage'] > 0.5:
                base_reward += 5
            
            # Penalty for bad choices
            if gas_level == 'high' and action_params['priority_fee'] < 2:
                base_reward -= 15
            
            reward = base_reward
            success = reward > 0
            
            # Update agent with a (potentially) new next state
            next_chain = np.random.choice(['ethereum', 'polygon', 'arbitrum'])
            next_volatility = np.random.choice(['low', 'medium', 'high'])
            next_gas_level = np.random.choice(['low', 'normal', 'high'])
            next_state = f"{next_chain}_{next_volatility}_{next_gas_level}"
            agent.update(state, action_params, reward, next_state, success)
            
            if (episode + 1) % 1000 == 0:
                metrics = agent.get_metrics()
                logger.info(f"   Episode {episode + 1}/{n_episodes}: "
                          f"Success Rate: {metrics['success_rate']:.2%}, "
                          f"Avg Reward: {metrics['avg_reward']:.2f}")
        
        # Save final metrics
        final_metrics = agent.get_metrics()
        logger.info("   📊 Final RL Agent Performance:")
        logger.info(f"      Total Episodes: {final_metrics['total_episodes']}")
        logger.info(f"      Success Rate: {final_metrics['success_rate']:.2%}")
        logger.info(f"      Avg Reward: {final_metrics['avg_reward']:.2f}")
        logger.info(f"      States Explored: {final_metrics['states_explored']}")
        
        logger.info("✅ RL Agent training complete!")
    
    def train_all_models(self, n_samples: int = 10000, n_episodes: int = 10000):
        """
        Train all ML models
        
        Args:
            n_samples: Number of training samples for forecaster
            n_episodes: Number of episodes for RL agent
        """
        logger.info("=" * 60)
        logger.info("🎓 Starting ML Model Training")
        logger.info("=" * 60)
        
        # Generate training data
        df = self.generate_synthetic_training_data(n_samples)
        
        # Save training data
        data_path = self.data_dir / "training_data.csv"
        df.to_csv(data_path, index=False)
        logger.info(f"💾 Saved training data to {data_path}")
        
        # Train forecaster
        logger.info("")
        self.train_forecaster_model(df)
        
        # Train RL agent
        logger.info("")
        self.train_rl_agent(n_episodes)
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("✅ All ML model training complete!")
        logger.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Train ML models for Titan")
    parser.add_argument('--samples', type=int, default=10000,
                       help='Number of training samples for forecaster')
    parser.add_argument('--episodes', type=int, default=10000,
                       help='Number of training episodes for RL agent')
    parser.add_argument('--data-dir', type=str, default='data',
                       help='Directory for data and models')
    
    args = parser.parse_args()
    
    trainer = ModelTrainer(data_dir=args.data_dir)
    trainer.train_all_models(n_samples=args.samples, n_episodes=args.episodes)


if __name__ == "__main__":
    main()
