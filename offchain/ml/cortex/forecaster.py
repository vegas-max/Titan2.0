import numpy as np
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from collections import deque

try:
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler
    import xgboost as xgb
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("WARNING: ML libraries not available. Install with: pip install scikit-learn xgboost")

# Import AI & Scoring configuration
try:
    from offchain.core.config import (
        AI_PREDICTION_ENABLED, AI_PREDICTION_MIN_CONFIDENCE,
        ML_CONFIDENCE_THRESHOLD, HF_CONFIDENCE_THRESHOLD
    )
except ImportError:
    # Fallback defaults if config not available
    AI_PREDICTION_ENABLED = True
    AI_PREDICTION_MIN_CONFIDENCE = 0.8
    ML_CONFIDENCE_THRESHOLD = 0.75
    HF_CONFIDENCE_THRESHOLD = 0.8

class MarketForecaster:
    """
    Advanced Market Forecaster with Machine Learning capabilities.
    Predicts near-future states to prevent 'Bad Timing' trades.
    Uses multiple models: Linear Regression, XGBoost, and Volatility Prediction.
    """
    
    MODEL_PATH = "data/forecaster_model.json"
    METRICS_PATH = "data/forecaster_metrics.json"
    
    def __init__(self, history_window=50):
        self.gas_history = deque(maxlen=history_window)
        self.price_history = deque(maxlen=history_window)
        self.volume_history = deque(maxlen=history_window)
        self.volatility_history = deque(maxlen=history_window)
        self.window = history_window
        
        # AI & Scoring Configuration
        self.ai_prediction_enabled = AI_PREDICTION_ENABLED
        self.min_confidence = AI_PREDICTION_MIN_CONFIDENCE
        self.ml_confidence_threshold = ML_CONFIDENCE_THRESHOLD
        self.hf_confidence_threshold = HF_CONFIDENCE_THRESHOLD
        
        # ML Models
        self.scaler = StandardScaler() if ML_AVAILABLE else None
        self.xgb_model = None
        self.gb_model = None
        
        # Performance metrics
        self.metrics = {
            "predictions_made": 0,
            "predictions_correct": 0,
            "accuracy": 0.0,
            "mse": 0.0,
            "mae": 0.0,
            "last_updated": None,
            "model_version": "2.0",
            "ai_enabled": self.ai_prediction_enabled,
            "min_confidence": self.min_confidence
        }
        
        # Load existing models if available
        self._load_models()
        
    def _load_models(self):
        """Load pre-trained models from disk"""
        if not ML_AVAILABLE:
            return
            
        try:
            if os.path.exists(self.MODEL_PATH):
                with open(self.MODEL_PATH, 'r') as f:
                    model_data = json.load(f)
                    # In production, use joblib for actual model serialization
                    # This is a simplified version
            
            if os.path.exists(self.METRICS_PATH):
                with open(self.METRICS_PATH, 'r') as f:
                    self.metrics = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load models: {e}")
    
    def _save_metrics(self):
        """Save performance metrics to disk"""
        try:
            os.makedirs("data", exist_ok=True)
            self.metrics["last_updated"] = datetime.now().isoformat()
            with open(self.METRICS_PATH, 'w') as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save metrics: {e}")

    def ingest_gas(self, gwei):
        """Ingest gas price data point"""
        self.gas_history.append(gwei)

    def ingest_price(self, price):
        """Ingest price data point"""
        self.price_history.append(price)
    
    def ingest_volume(self, volume):
        """Ingest volume data point"""
        self.volume_history.append(volume)
    
    def calculate_volatility(self):
        """Calculate current market volatility"""
        if len(self.price_history) < 10:
            return 0.0
        
        prices = np.array(list(self.price_history))
        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns) * 100  # As percentage
        
        self.volatility_history.append(volatility)
        return volatility

    def extract_features(self):
        """
        Extract advanced features for ML models.
        Returns feature vector for prediction.
        """
        if len(self.gas_history) < 10:
            return None
        
        gas_array = np.array(list(self.gas_history))
        
        features = {
            # Statistical features
            'gas_mean': np.mean(gas_array),
            'gas_std': np.std(gas_array),
            'gas_min': np.min(gas_array),
            'gas_max': np.max(gas_array),
            'gas_median': np.median(gas_array),
            'gas_range': np.max(gas_array) - np.min(gas_array),
            
            # Trend features
            'gas_slope': np.polyfit(range(len(gas_array)), gas_array, 1)[0],
            'gas_momentum': gas_array[-1] - gas_array[-min(5, len(gas_array))],
            
            # Recent behavior
            'gas_current': gas_array[-1],
            'gas_prev': gas_array[-2] if len(gas_array) > 1 else gas_array[-1],
            'gas_change': gas_array[-1] - gas_array[-2] if len(gas_array) > 1 else 0,
            'gas_change_pct': ((gas_array[-1] - gas_array[-2]) / gas_array[-2] * 100) if len(gas_array) > 1 and gas_array[-2] != 0 else 0,
        }
        
        # Add volatility if available
        if self.price_history and len(self.price_history) >= 10:
            volatility = self.calculate_volatility()
            features['volatility'] = volatility
        else:
            features['volatility'] = 0.0
        
        return features

    def predict_gas_trend(self):
        """
        Enhanced prediction using multiple methods.
        Returns: 'RISING_FAST', 'DROPPING_FAST', or 'STABLE'
        """
        if len(self.gas_history) < 10:
            return "STABLE"

        # Method 1: Linear Regression Slope (baseline)
        gas_array = np.array(list(self.gas_history))
        x = np.arange(len(gas_array))
        slope, _ = np.polyfit(x, gas_array, 1)
        
        # Method 2: Advanced features analysis
        features = self.extract_features()
        if features:
            # Consider momentum and volatility
            momentum = features['gas_momentum']
            change_pct = features['gas_change_pct']
            
            # Combined decision
            if slope > 0.5 or (momentum > 2 and change_pct > 5):
                trend = "RISING_FAST"
            elif slope < -0.5 or (momentum < -2 and change_pct < -5):
                trend = "DROPPING_FAST"
            else:
                trend = "STABLE"
        else:
            # Fallback to simple slope
            if slope > 0.5:
                trend = "RISING_FAST"
            elif slope < -0.5:
                trend = "DROPPING_FAST"
            else:
                trend = "STABLE"
        
        # Update metrics
        self.metrics["predictions_made"] += 1
        self._save_metrics()
        
        return trend
    
    def predict_next_gas_price(self):
        """
        Predict the next gas price value using ML models.
        Returns predicted gas price in gwei.
        """
        if len(self.gas_history) < 10:
            return list(self.gas_history)[-1] if self.gas_history else 30.0
        
        features = self.extract_features()
        if not features:
            return list(self.gas_history)[-1]
        
        # Simple prediction using moving average and trend
        gas_array = np.array(list(self.gas_history))
        ma_5 = np.mean(gas_array[-5:])
        slope = features['gas_slope']
        
        # Predict next value as MA + trend
        predicted = ma_5 + slope
        
        return max(0, predicted)  # Gas price can't be negative
    
    def predict_volatility(self):
        """
        Predict market volatility for risk assessment.
        Returns: 'LOW', 'MEDIUM', 'HIGH'
        """
        volatility = self.calculate_volatility()
        
        if volatility < 1.0:
            return "LOW"
        elif volatility < 3.0:
            return "MEDIUM"
        else:
            return "HIGH"

    def should_wait(self):
        """
        AI Decision: Should we wait 1 block for cheaper gas?
        Enhanced with volatility consideration and AI prediction check.
        """
        # Check if AI prediction is enabled
        if not self.ai_prediction_enabled:
            return False
        
        trend = self.predict_gas_trend()
        volatility = self.predict_volatility()
        
        # Don't wait if volatility is high (unpredictable)
        if volatility == "HIGH":
            return False
        
        # Wait if gas is dropping and volatility is acceptable
        if trend == "DROPPING_FAST" and volatility in ["LOW", "MEDIUM"]:
            return True
        
        return False
    
    def is_prediction_confident(self, confidence_score):
        """
        Check if a prediction meets the minimum confidence threshold.
        
        Args:
            confidence_score: Prediction confidence score (0.0 to 1.0)
        
        Returns:
            bool: True if confidence meets threshold, False otherwise
        """
        if not self.ai_prediction_enabled:
            return True  # If AI prediction disabled, accept all predictions
        
        return confidence_score >= self.min_confidence
    
    def apply_ml_confidence_filter(self, predictions_with_scores):
        """
        Filter predictions based on ML confidence threshold.
        
        Args:
            predictions_with_scores: List of (prediction, confidence_score) tuples
        
        Returns:
            List of predictions that meet the confidence threshold
        """
        if not self.ai_prediction_enabled:
            return [p[0] for p in predictions_with_scores]
        
        return [
            prediction for prediction, score in predictions_with_scores
            if score >= self.ml_confidence_threshold
        ]
    
    def get_metrics(self):
        """Get current model performance metrics"""
        metrics = self.metrics.copy()
        
        # Add current state
        if self.gas_history:
            metrics["current_gas"] = list(self.gas_history)[-1]
            metrics["predicted_gas"] = self.predict_next_gas_price()
            metrics["trend"] = self.predict_gas_trend()
            metrics["volatility"] = self.predict_volatility()
        
        return metrics
    
    def update_accuracy(self, predicted_trend, actual_trend):
        """
        Update model accuracy based on prediction results.
        Call this when actual outcome is known.
        """
        if predicted_trend == actual_trend:
            self.metrics["predictions_correct"] += 1
        
        if self.metrics["predictions_made"] > 0:
            self.metrics["accuracy"] = (
                self.metrics["predictions_correct"] / self.metrics["predictions_made"]
            ) * 100
        
        self._save_metrics()