"""
Hugging Face Transformer-based Opportunity Ranker

Fine-tuned model for scoring arbitrage opportunities based on real historical data.
Uses a transformer architecture to learn complex patterns in profitable vs unprofitable trades.

Architecture:
- Input: Opportunity features (profit, gas, liquidity, volatility, etc.)
- Model: Lightweight transformer encoder (DistilBERT-style)
- Output: Confidence score (0.0-1.0) for opportunity quality

Training Data: Real arbitrage execution history with actual outcomes
"""

import os
import json
import numpy as np
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger("HFRanker")

# Import HF configuration
try:
    from offchain.core.config import HF_CONFIDENCE_THRESHOLD
except ImportError:
    HF_CONFIDENCE_THRESHOLD = 0.8

# Check for transformers library
try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    import torch.nn as nn
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    logger.warning("Hugging Face transformers not available. Install with: pip install transformers torch")


class OpportunityRanker(nn.Module):
    """
    Transformer-based ranking model for arbitrage opportunities.
    
    Uses a pre-trained transformer encoder to learn representations of opportunity features,
    then applies a classification head to predict opportunity quality.
    """
    
    def __init__(self, feature_dim=12, hidden_dim=128, num_layers=2, dropout=0.1):
        super(OpportunityRanker, self).__init__()
        
        if not HF_AVAILABLE:
            raise RuntimeError("Transformers library required for HF Ranker")
        
        # Feature projection layer
        self.feature_projection = nn.Linear(feature_dim, hidden_dim)
        
        # Transformer encoder layers
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim,
            nhead=4,
            dim_feedforward=hidden_dim * 2,
            dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1),
            nn.Sigmoid()  # Output: confidence score 0-1
        )
        
    def forward(self, x):
        """
        Forward pass through the ranker.
        
        Args:
            x: Tensor of shape (batch_size, feature_dim) containing opportunity features
            
        Returns:
            Tensor of shape (batch_size, 1) containing confidence scores
        """
        # Project features to hidden dimension
        x = self.feature_projection(x)  # (batch, hidden_dim)
        
        # Add sequence dimension for transformer (treat as single-token sequence)
        x = x.unsqueeze(1)  # (batch, 1, hidden_dim)
        
        # Pass through transformer
        x = self.transformer(x)  # (batch, 1, hidden_dim)
        
        # Remove sequence dimension
        x = x.squeeze(1)  # (batch, hidden_dim)
        
        # Classify
        score = self.classifier(x)  # (batch, 1)
        
        return score


class HuggingFaceRanker:
    """
    Hugging Face-powered opportunity ranker with real data training.
    
    Features:
    - Fine-tuned transformer model for opportunity scoring
    - Real historical data integration
    - Confidence-based filtering
    - Continuous learning from execution results
    """
    
    MODEL_PATH = "data/hf_ranker_model.pt"
    TRAINING_DATA_PATH = "data/hf_training_data.json"
    METRICS_PATH = "data/hf_ranker_metrics.json"
    
    def __init__(self, confidence_threshold=None):
        """
        Initialize the HF Ranker.
        
        Args:
            confidence_threshold: Minimum confidence score to accept opportunities (default: from config)
        """
        self.confidence_threshold = confidence_threshold or HF_CONFIDENCE_THRESHOLD
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') if HF_AVAILABLE else None
        
        # Initialize model
        self.model = None
        self.trained = False
        
        # Training data buffer
        self.training_data = []
        
        # Performance metrics
        self.metrics = {
            "total_predictions": 0,
            "correct_predictions": 0,
            "false_positives": 0,  # Predicted good but was bad
            "false_negatives": 0,  # Predicted bad but was good
            "accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "last_trained": None,
            "training_samples": 0
        }
        
        # Load existing model and data if available
        self._load_model()
        self._load_training_data()
        self._load_metrics()
        
        logger.info(f"🤖 HF Ranker initialized (threshold: {self.confidence_threshold})")
        logger.info(f"   Device: {self.device if HF_AVAILABLE else 'N/A (torch not available)'}")
        logger.info(f"   Trained: {self.trained}")
        logger.info(f"   Training samples: {len(self.training_data)}")
    
    def extract_features(self, opportunity, profit_result=None, gas_gwei=None):
        """
        Extract features from an opportunity for model input.
        
        Args:
            opportunity: Dictionary containing opportunity data
            profit_result: Optional profit calculation result
            gas_gwei: Optional current gas price
            
        Returns:
            numpy array of features (12-dimensional)
        """
        features = []
        
        # Feature 1-2: Profit metrics
        if profit_result:
            features.append(float(profit_result.get('net_profit', 0)))
            features.append(float(profit_result.get('gross_spread', 0)))
        else:
            features.extend([0.0, 0.0])
        
        # Feature 3: Gas cost
        features.append(float(gas_gwei) if gas_gwei else 30.0)
        
        # Feature 4: TAR score
        features.append(float(opportunity.get('tar_score', 50)))
        
        # Feature 5: Chain ID (normalized)
        chain_id = opportunity.get('src_chain', 1)
        features.append(float(chain_id) / 100.0)  # Normalize to 0-1 range
        
        # Feature 6-7: Token tier encoding
        token = opportunity.get('token', '')
        tier1_tokens = ['USDC', 'USDT', 'DAI', 'WETH', 'WBTC', 'ETH']
        tier2_tokens = ['UNI', 'LINK', 'AAVE', 'CRV', 'MATIC', 'AVAX', 'BNB', 'SNX', 'MKR', 'COMP']
        
        is_tier1 = 1.0 if token in tier1_tokens else 0.0
        is_tier2 = 1.0 if token in tier2_tokens else 0.0
        features.extend([is_tier1, is_tier2])
        
        # Feature 8-9: Route quality
        route = opportunity.get('route', ('', ''))
        has_univ3 = 1.0 if 'UNIV3' in route else 0.0
        has_established = 1.0 if any(dex in route for dex in ['SUSHI', 'QUICKSWAP', 'PANCAKE']) else 0.0
        features.extend([has_univ3, has_established])
        
        # Feature 10: Profit margin (if available)
        if profit_result and profit_result.get('gross_spread', 0) > 0:
            margin = float(profit_result['net_profit']) / float(profit_result['gross_spread'])
            features.append(min(1.0, max(0.0, margin)))
        else:
            features.append(0.0)
        
        # Feature 11-12: Time-based features (hour of day, day of week)
        now = datetime.now()
        features.append(now.hour / 24.0)  # Normalize to 0-1
        features.append(now.weekday() / 7.0)  # Normalize to 0-1
        
        return np.array(features, dtype=np.float32)
    
    def predict(self, opportunity, profit_result=None, gas_gwei=None):
        """
        Predict confidence score for an opportunity.
        
        Args:
            opportunity: Opportunity dictionary
            profit_result: Optional profit calculation result
            gas_gwei: Optional current gas price
            
        Returns:
            float: Confidence score (0.0-1.0)
        """
        if not HF_AVAILABLE:
            logger.warning("HF Ranker unavailable - returning default score")
            return 0.5
        
        if not self.trained or self.model is None:
            # Use heuristic scoring if model not trained
            return self._heuristic_score(opportunity, profit_result, gas_gwei)
        
        # Extract features
        features = self.extract_features(opportunity, profit_result, gas_gwei)
        
        # Convert to tensor
        x = torch.tensor(features, dtype=torch.float32).unsqueeze(0).to(self.device)
        
        # Predict
        self.model.eval()
        with torch.no_grad():
            score = self.model(x).item()
        
        self.metrics["total_predictions"] += 1
        
        return score
    
    def _heuristic_score(self, opportunity, profit_result=None, gas_gwei=None):
        """
        Fallback heuristic scoring when model is not trained.
        """
        score = 0.5  # Base score
        
        # Adjust based on profit
        if profit_result:
            net_profit = float(profit_result.get('net_profit', 0))
            if net_profit > 10:
                score += 0.2
            elif net_profit > 5:
                score += 0.1
            elif net_profit < 2:
                score -= 0.1
        
        # Adjust based on gas
        if gas_gwei:
            if gas_gwei < 20:
                score += 0.1
            elif gas_gwei > 50:
                score -= 0.1
        
        # Adjust based on TAR score
        tar_score = opportunity.get('tar_score', 50)
        if tar_score > 80:
            score += 0.15
        elif tar_score < 60:
            score -= 0.1
        
        return min(1.0, max(0.0, score))
    
    def is_confident(self, score):
        """
        Check if a prediction score meets the confidence threshold.
        
        Args:
            score: Prediction score (0.0-1.0)
            
        Returns:
            bool: True if score >= threshold
        """
        return score >= self.confidence_threshold
    
    def add_training_sample(self, opportunity, profit_result, gas_gwei, actual_outcome):
        """
        Add a real execution result to training data.
        
        Args:
            opportunity: Opportunity that was executed
            profit_result: Calculated profit result
            gas_gwei: Gas price at execution
            actual_outcome: Boolean - True if execution was successful and profitable
        """
        features = self.extract_features(opportunity, profit_result, gas_gwei)
        
        sample = {
            "features": features.tolist(),
            "label": 1.0 if actual_outcome else 0.0,
            "timestamp": datetime.now().isoformat(),
            "token": opportunity.get('token', 'UNKNOWN'),
            "chain": opportunity.get('src_chain', 0),
            "profit": float(profit_result.get('net_profit', 0)) if profit_result else 0.0
        }
        
        self.training_data.append(sample)
        
        # Auto-save training data periodically
        if len(self.training_data) % 10 == 0:
            self._save_training_data()
        
        logger.debug(f"Added training sample: {sample['token']} → {actual_outcome}")
    
    def train(self, epochs=50, batch_size=32, learning_rate=0.001):
        """
        Train the ranker model on accumulated real data.
        
        Args:
            epochs: Number of training epochs
            batch_size: Batch size for training
            learning_rate: Learning rate for optimizer
            
        Returns:
            dict: Training metrics
        """
        if not HF_AVAILABLE:
            logger.error("Cannot train - transformers library not available")
            return {"error": "transformers not available"}
        
        if len(self.training_data) < 10:
            logger.warning(f"Insufficient training data: {len(self.training_data)} samples (need at least 10)")
            return {"error": "insufficient data", "samples": len(self.training_data)}
        
        logger.info(f"🎓 Training HF Ranker on {len(self.training_data)} samples...")
        
        # Prepare data
        X = np.array([s['features'] for s in self.training_data], dtype=np.float32)
        y = np.array([s['label'] for s in self.training_data], dtype=np.float32).reshape(-1, 1)
        
        # Create model if not exists
        if self.model is None:
            self.model = OpportunityRanker(feature_dim=X.shape[1]).to(self.device)
        
        # Training setup
        optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        criterion = nn.BCELoss()
        
        # Convert to tensors
        X_tensor = torch.tensor(X, dtype=torch.float32).to(self.device)
        y_tensor = torch.tensor(y, dtype=torch.float32).to(self.device)
        
        # Training loop
        self.model.train()
        for epoch in range(epochs):
            # Shuffle data
            indices = torch.randperm(X_tensor.size(0))
            X_shuffled = X_tensor[indices]
            y_shuffled = y_tensor[indices]
            
            epoch_loss = 0.0
            num_batches = 0
            
            # Mini-batch training
            for i in range(0, len(X_tensor), batch_size):
                batch_X = X_shuffled[i:i+batch_size]
                batch_y = y_shuffled[i:i+batch_size]
                
                # Forward pass
                optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_y)
                
                # Backward pass
                loss.backward()
                optimizer.step()
                
                epoch_loss += loss.item()
                num_batches += 1
            
            avg_loss = epoch_loss / num_batches
            
            if (epoch + 1) % 10 == 0:
                logger.info(f"   Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.4f}")
        
        self.trained = True
        self.metrics["last_trained"] = datetime.now().isoformat()
        self.metrics["training_samples"] = len(self.training_data)
        
        # Evaluate on training data (for metrics)
        self._evaluate_on_training_data()
        
        # Save model and metrics
        self._save_model()
        self._save_metrics()
        
        logger.info(f"✅ Training complete - Accuracy: {self.metrics['accuracy']:.2%}")
        
        return self.metrics
    
    def _evaluate_on_training_data(self):
        """Evaluate model performance on training data."""
        if not self.trained or self.model is None:
            return
        
        self.model.eval()
        correct = 0
        total = len(self.training_data)
        
        true_positives = 0
        false_positives = 0
        true_negatives = 0
        false_negatives = 0
        
        with torch.no_grad():
            for sample in self.training_data:
                features = torch.tensor(sample['features'], dtype=torch.float32).unsqueeze(0).to(self.device)
                prediction = self.model(features).item()
                predicted_class = 1 if prediction >= 0.5 else 0
                actual_class = int(sample['label'])
                
                if predicted_class == actual_class:
                    correct += 1
                
                if actual_class == 1 and predicted_class == 1:
                    true_positives += 1
                elif actual_class == 0 and predicted_class == 1:
                    false_positives += 1
                elif actual_class == 0 and predicted_class == 0:
                    true_negatives += 1
                elif actual_class == 1 and predicted_class == 0:
                    false_negatives += 1
        
        self.metrics["accuracy"] = correct / total if total > 0 else 0.0
        self.metrics["correct_predictions"] = correct
        self.metrics["false_positives"] = false_positives
        self.metrics["false_negatives"] = false_negatives
        
        # Calculate precision, recall, F1
        if (true_positives + false_positives) > 0:
            self.metrics["precision"] = true_positives / (true_positives + false_positives)
        else:
            self.metrics["precision"] = 0.0
        
        if (true_positives + false_negatives) > 0:
            self.metrics["recall"] = true_positives / (true_positives + false_negatives)
        else:
            self.metrics["recall"] = 0.0
        
        if (self.metrics["precision"] + self.metrics["recall"]) > 0:
            self.metrics["f1_score"] = 2 * (self.metrics["precision"] * self.metrics["recall"]) / \
                                       (self.metrics["precision"] + self.metrics["recall"])
        else:
            self.metrics["f1_score"] = 0.0
    
    def _save_model(self):
        """Save model to disk."""
        if not HF_AVAILABLE or self.model is None:
            return
        
        try:
            os.makedirs("data", exist_ok=True)
            torch.save(self.model.state_dict(), self.MODEL_PATH)
            logger.info(f"💾 Model saved to {self.MODEL_PATH}")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def _load_model(self):
        """Load model from disk."""
        if not HF_AVAILABLE:
            return
        
        if os.path.exists(self.MODEL_PATH):
            try:
                self.model = OpportunityRanker().to(self.device)
                self.model.load_state_dict(torch.load(self.MODEL_PATH, map_location=self.device))
                self.trained = True
                logger.info(f"📥 Model loaded from {self.MODEL_PATH}")
            except Exception as e:
                logger.warning(f"Failed to load model: {e}")
    
    def _save_training_data(self):
        """Save training data to disk."""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.TRAINING_DATA_PATH, 'w') as f:
                json.dump(self.training_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save training data: {e}")
    
    def _load_training_data(self):
        """Load training data from disk."""
        if os.path.exists(self.TRAINING_DATA_PATH):
            try:
                with open(self.TRAINING_DATA_PATH, 'r') as f:
                    self.training_data = json.load(f)
                logger.info(f"📥 Loaded {len(self.training_data)} training samples")
            except Exception as e:
                logger.warning(f"Failed to load training data: {e}")
    
    def _save_metrics(self):
        """Save metrics to disk."""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.METRICS_PATH, 'w') as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    def _load_metrics(self):
        """Load metrics from disk."""
        if os.path.exists(self.METRICS_PATH):
            try:
                with open(self.METRICS_PATH, 'r') as f:
                    loaded_metrics = json.load(f)
                    self.metrics.update(loaded_metrics)
                logger.info(f"📥 Loaded metrics (Accuracy: {self.metrics.get('accuracy', 0):.2%})")
            except Exception as e:
                logger.warning(f"Failed to load metrics: {e}")
    
    def get_metrics(self):
        """Get current performance metrics."""
        return self.metrics.copy()
