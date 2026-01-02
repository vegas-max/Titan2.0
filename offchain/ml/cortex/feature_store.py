import pandas as pd
import numpy as np
import time
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

class FeatureStore:
    """
    Enhanced Feature Store - The Memory of the Titan.
    Logs market states, bridge fees, and trade outcomes for training.
    Provides feature engineering and data analytics capabilities.
    """
    DATA_PATH = "data/history.csv"
    SUMMARY_PATH = "data/feature_summary.json"
    
    def __init__(self):
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Initialize file if missing
        if not os.path.exists(self.DATA_PATH):
            df = pd.DataFrame(columns=[
                "timestamp", "chain_id", "token_symbol", 
                "dex_price", "bridge_fee_usd", "gas_price_gwei",
                "volatility_index", "volume_24h", "liquidity_usd",
                "spread_bps", "slippage_bps", "execution_time_ms",
                "outcome_label", "profit_usd", "success"
            ])
            df.to_csv(self.DATA_PATH, index=False)
        
        # Statistics cache
        self.stats_cache = {
            "total_observations": 0,
            "profitable_trades": 0,
            "unprofitable_trades": 0,
            "avg_profit": 0.0,
            "avg_gas_cost": 0.0,
            "best_chain": None,
            "best_token": None,
            "last_updated": None
        }
        self._update_stats_cache()

    def log_observation(self, chain_id, token, price, fee, gas, vol, 
                       volume=0, liquidity=0, spread=0, slippage=0):
        """
        Saves an enhanced market snapshot with additional features.
        
        Args:
            chain_id: Blockchain ID
            token: Token symbol
            price: Current DEX price
            fee: Bridge fee in USD
            gas: Gas price in gwei
            vol: Volatility index
            volume: 24h trading volume
            liquidity: Total liquidity in USD
            spread: Spread in basis points
            slippage: Expected slippage in basis points
        """
        new_row = {
            "timestamp": time.time(),
            "chain_id": chain_id,
            "token_symbol": token,
            "dex_price": price,
            "bridge_fee_usd": fee,
            "gas_price_gwei": gas,
            "volatility_index": vol,
            "volume_24h": volume,
            "liquidity_usd": liquidity,
            "spread_bps": spread,
            "slippage_bps": slippage,
            "execution_time_ms": None,
            "outcome_label": None,  # Unknown yet
            "profit_usd": None,
            "success": None
        }
        
        # Append efficiently
        df = pd.DataFrame([new_row])
        df.to_csv(self.DATA_PATH, mode='a', header=False, index=False)
        
        # Update statistics
        self.stats_cache["total_observations"] += 1

    def update_outcome(self, timestamp, profit_realized, execution_time_ms=None, success=True):
        """
        Updates the outcome label after execution.
        
        Args:
            timestamp: Original observation timestamp
            profit_realized: Actual profit/loss in USD
            execution_time_ms: Time taken to execute in milliseconds
            success: Whether execution was successful
        """
        try:
            # Read the CSV
            df = pd.read_csv(self.DATA_PATH)
            
            # Find the closest row to the timestamp
            if len(df) > 0 and 'timestamp' in df.columns:
                df['time_diff'] = abs(df['timestamp'] - timestamp)
                closest_idx = df['time_diff'].idxmin()
                
                # Update the row
                df.at[closest_idx, 'outcome_label'] = 1 if profit_realized > 0 else 0
                df.at[closest_idx, 'profit_usd'] = profit_realized
                df.at[closest_idx, 'success'] = success
                if execution_time_ms:
                    df.at[closest_idx, 'execution_time_ms'] = execution_time_ms
                
                # Remove temporary column and save
                df = df.drop('time_diff', axis=1)
                df.to_csv(self.DATA_PATH, index=False)
                
                # Update stats
                if profit_realized > 0:
                    self.stats_cache["profitable_trades"] += 1
                else:
                    self.stats_cache["unprofitable_trades"] += 1
                
                self._update_stats_cache()
        except Exception as e:
            print(f"Warning: Could not update outcome: {e}")
    
    def _update_stats_cache(self):
        """Update cached statistics from data"""
        try:
            if not os.path.exists(self.DATA_PATH):
                return
            
            df = pd.read_csv(self.DATA_PATH)
            
            if len(df) == 0:
                return
            
            # Calculate statistics
            self.stats_cache["total_observations"] = len(df)
            
            # Filter for completed trades (those with outcome labels)
            completed = df[df['outcome_label'].notna()]
            
            if len(completed) > 0:
                self.stats_cache["profitable_trades"] = len(completed[completed['outcome_label'] == 1])
                self.stats_cache["unprofitable_trades"] = len(completed[completed['outcome_label'] == 0])
                
                # Calculate average profit
                profit_data = completed[completed['profit_usd'].notna()]
                if len(profit_data) > 0:
                    self.stats_cache["avg_profit"] = profit_data['profit_usd'].mean()
                
                # Find best performing chain
                chain_profits = completed.groupby('chain_id')['profit_usd'].sum()
                if len(chain_profits) > 0:
                    self.stats_cache["best_chain"] = int(chain_profits.idxmax())
                
                # Find best performing token
                token_profits = completed.groupby('token_symbol')['profit_usd'].sum()
                if len(token_profits) > 0:
                    self.stats_cache["best_token"] = token_profits.idxmax()
            
            # Calculate average gas cost
            if 'gas_price_gwei' in df.columns:
                self.stats_cache["avg_gas_cost"] = df['gas_price_gwei'].mean()
            
            self.stats_cache["last_updated"] = datetime.now().isoformat()
            
            # Save summary
            self._save_summary()
            
        except Exception as e:
            print(f"Warning: Could not update stats: {e}")
    
    def _save_summary(self):
        """Save summary statistics to file"""
        try:
            with open(self.SUMMARY_PATH, 'w') as f:
                json.dump(self.stats_cache, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save summary: {e}")
    
    def get_summary(self):
        """Get summary statistics"""
        return self.stats_cache.copy()
    
    def get_training_data(self, lookback_hours=24):
        """
        Get training data for ML models.
        
        Args:
            lookback_hours: How many hours of history to retrieve
            
        Returns:
            DataFrame with features and labels
        """
        try:
            df = pd.read_csv(self.DATA_PATH)
            
            if len(df) == 0:
                return pd.DataFrame()
            
            # Filter by time window
            cutoff_time = time.time() - (lookback_hours * 3600)
            df = df[df['timestamp'] >= cutoff_time]
            
            # Only return completed observations with outcomes
            df = df[df['outcome_label'].notna()]
            
            return df
            
        except Exception as e:
            print(f"Warning: Could not get training data: {e}")
            return pd.DataFrame()
    
    def get_feature_importance(self):
        """
        Calculate which features are most correlated with profitable outcomes.
        Returns dictionary of feature importances.
        """
        try:
            df = self.get_training_data(lookback_hours=168)  # Last week
            
            if len(df) < 10:
                return {}
            
            # Calculate correlations with outcome
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            feature_cols = [col for col in numeric_cols if col not in ['timestamp', 'outcome_label', 'profit_usd']]
            
            importance = {}
            for col in feature_cols:
                try:
                    corr = df[col].corr(df['outcome_label'])
                    if not np.isnan(corr):
                        importance[col] = abs(corr)
                except:
                    pass
            
            # Sort by importance
            importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
            
            return importance
            
        except Exception as e:
            print(f"Warning: Could not calculate feature importance: {e}")
            return {}
    
    def get_performance_by_chain(self):
        """Get performance metrics grouped by chain"""
        try:
            df = self.get_training_data(lookback_hours=168)
            
            if len(df) == 0:
                return {}
            
            chain_stats = df.groupby('chain_id').agg({
                'profit_usd': ['count', 'sum', 'mean'],
                'outcome_label': 'mean',  # Success rate
                'gas_price_gwei': 'mean'
            }).to_dict('index')
            
            # Format output
            formatted = {}
            for chain_id, stats in chain_stats.items():
                formatted[str(chain_id)] = {
                    'trade_count': stats[('profit_usd', 'count')],
                    'total_profit': stats[('profit_usd', 'sum')],
                    'avg_profit': stats[('profit_usd', 'mean')],
                    'success_rate': stats[('outcome_label', 'mean')] * 100,
                    'avg_gas': stats[('gas_price_gwei', 'mean')]
                }
            
            return formatted
            
        except Exception as e:
            print(f"Warning: Could not get chain performance: {e}")
            return {}
    
    def get_performance_by_token(self):
        """Get performance metrics grouped by token"""
        try:
            df = self.get_training_data(lookback_hours=168)
            
            if len(df) == 0:
                return {}
            
            token_stats = df.groupby('token_symbol').agg({
                'profit_usd': ['count', 'sum', 'mean'],
                'outcome_label': 'mean',
                'volatility_index': 'mean'
            }).to_dict('index')
            
            # Format output
            formatted = {}
            for token, stats in token_stats.items():
                formatted[token] = {
                    'trade_count': stats[('profit_usd', 'count')],
                    'total_profit': stats[('profit_usd', 'sum')],
                    'avg_profit': stats[('profit_usd', 'mean')],
                    'success_rate': stats[('outcome_label', 'mean')] * 100,
                    'avg_volatility': stats[('volatility_index', 'mean')]
                }
            
            return formatted
            
        except Exception as e:
            print(f"Warning: Could not get token performance: {e}")
            return {}
    
    def cleanup_old_data(self, days_to_keep=30):
        """Remove data older than specified days"""
        try:
            df = pd.read_csv(self.DATA_PATH)
            
            cutoff_time = time.time() - (days_to_keep * 24 * 3600)
            df = df[df['timestamp'] >= cutoff_time]
            
            df.to_csv(self.DATA_PATH, index=False)
            
            print(f"Cleaned up data older than {days_to_keep} days")
            
        except Exception as e:
            print(f"Warning: Could not cleanup old data: {e}")