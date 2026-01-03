import random
import json
import os
import numpy as np
from datetime import datetime
from collections import deque

# Import AI & Scoring configuration
try:
    from offchain.core.config import (
        SELF_LEARNING_ENABLED, ROUTE_INTELLIGENCE_ENABLED,
        ML_CONFIDENCE_THRESHOLD
    )
except ImportError:
    # Fallback defaults if config not available
    SELF_LEARNING_ENABLED = True
    ROUTE_INTELLIGENCE_ENABLED = True
    ML_CONFIDENCE_THRESHOLD = 0.75

class QLearningAgent:
    """
    Enhanced Reinforcement Learning Agent with Experience Replay.
    Tunes execution parameters using Q-Learning with memory buffer.
    
    State: (Chain, Volatility, Gas Level)
    Action: (Slippage Tolerance, Priority Fee)
    Reward: Profit - GasCost (or -penalty if reverted)
    """
    
    Q_TABLE_PATH = "data/q_table.json"
    METRICS_PATH = "data/rl_metrics.json"
    REPLAY_BUFFER_PATH = "data/replay_buffer.json"
    
    # Configurable gas price thresholds (in Gwei)
    GAS_LOW_THRESHOLD = 20
    GAS_NORMAL_THRESHOLD = 50
    
    def __init__(self, buffer_size=10000):
        # AI & Scoring Configuration
        self.self_learning_enabled = SELF_LEARNING_ENABLED
        self.route_intelligence_enabled = ROUTE_INTELLIGENCE_ENABLED
        self.ml_confidence_threshold = ML_CONFIDENCE_THRESHOLD
        
        self.q_table = self.load_q_table()
        # Learning rate is kept constant; when self_learning_enabled is False,
        # Q-table updates are skipped entirely instead of zeroing the learning rate
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.1  # Exploration rate
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        
        # Experience Replay Buffer
        self.replay_buffer = deque(maxlen=buffer_size)
        self._load_replay_buffer()
        
        # Performance Metrics
        self.metrics = {
            "total_episodes": 0,
            "total_rewards": 0.0,
            "avg_reward": 0.0,
            "best_reward": 0.0,
            "worst_reward": 0.0,
            "epsilon": self.epsilon,
            "states_explored": 0,
            "actions_taken": 0,
            "successful_trades": 0,
            "failed_trades": 0,
            "success_rate": 0.0,
            "last_updated": None,
            "self_learning_enabled": self.self_learning_enabled,
            "route_intelligence_enabled": self.route_intelligence_enabled
        }
        self._load_metrics()

    def load_q_table(self):
        """Load Q-table from disk"""
        if os.path.exists(self.Q_TABLE_PATH):
            try:
                with open(self.Q_TABLE_PATH, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load Q-table: {e}")
        return {}
    
    def _save_q_table(self):
        """Save Q-table to disk"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.Q_TABLE_PATH, 'w') as f:
                json.dump(self.q_table, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save Q-table: {e}")
    
    def _load_replay_buffer(self):
        """Load replay buffer from disk"""
        if os.path.exists(self.REPLAY_BUFFER_PATH):
            try:
                with open(self.REPLAY_BUFFER_PATH, 'r') as f:
                    buffer_data = json.load(f)
                    self.replay_buffer.extend(buffer_data[-1000:])  # Load last 1000
            except Exception as e:
                print(f"Warning: Could not load replay buffer: {e}")
    
    def _save_replay_buffer(self):
        """Save replay buffer to disk (last 1000 experiences)"""
        try:
            os.makedirs("data", exist_ok=True)
            # Only save recent experiences to avoid huge files
            buffer_list = list(self.replay_buffer)[-1000:]
            with open(self.REPLAY_BUFFER_PATH, 'w') as f:
                json.dump(buffer_list, f)
        except Exception as e:
            print(f"Warning: Could not save replay buffer: {e}")
    
    def _load_metrics(self):
        """Load metrics from disk"""
        if os.path.exists(self.METRICS_PATH):
            try:
                with open(self.METRICS_PATH, 'r') as f:
                    loaded_metrics = json.load(f)
                    self.metrics.update(loaded_metrics)
                    self.epsilon = self.metrics.get("epsilon", self.epsilon)
            except Exception as e:
                print(f"Warning: Could not load metrics: {e}")
    
    def _save_metrics(self):
        """Save metrics to disk"""
        try:
            os.makedirs("data", exist_ok=True)
            self.metrics["last_updated"] = datetime.now().isoformat()
            self.metrics["epsilon"] = self.epsilon
            with open(self.METRICS_PATH, 'w') as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save metrics: {e}")

    def get_state_key(self, chain_id, volatility_level, gas_level="NORMAL"):
        """
        Enhanced state representation with gas level.
        gas_level: 'LOW', 'NORMAL', 'HIGH'
        """
        return f"{chain_id}_{volatility_level}_{gas_level}"
    
    def _discretize_gas(self, gas_gwei):
        """Convert gas price to discrete level"""
        if gas_gwei < self.GAS_LOW_THRESHOLD:
            return "LOW"
        elif gas_gwei < self.GAS_NORMAL_THRESHOLD:
            return "NORMAL"
        else:
            return "HIGH"

    def recommend_parameters(self, chain_id, volatility_level, gas_gwei=30):
        """
        Returns optimal {slippage_bps, priority_fee} using epsilon-greedy policy.
        Enhanced with gas awareness.
        """
        gas_level = self._discretize_gas(gas_gwei)
        state = self.get_state_key(chain_id, volatility_level, gas_level)
        
        # Track new states
        if state not in self.q_table:
            self.metrics["states_explored"] += 1
        
        # Epsilon-greedy exploration
        if random.random() < self.epsilon or state not in self.q_table:
            # Explore: Try new settings
            action = {
                "slippage": random.choice([10, 50, 100, 150]),  # 0.1%, 0.5%, 1.0%, 1.5%
                "priority": random.choice([20, 30, 50, 75, 100])  # Gwei
            }
        else:
            # Exploit: Use best known settings
            best_action = max(self.q_table[state], key=self.q_table[state].get)
            # Parse action string "50_50" -> dict
            s, p = best_action.split("_")
            action = {"slippage": int(s), "priority": int(p)}
        
        self.metrics["actions_taken"] += 1
        return action

    def learn(self, chain_id, volatility, action_taken, reward, gas_gwei=30, next_state_data=None):
        """
        Enhanced Q-Learning with experience replay.
        Respects self_learning_enabled flag - if disabled, only updates metrics.
        
        Args:
            chain_id: Chain identifier
            volatility: Volatility level
            action_taken: Action dict with slippage and priority
            reward: Profit USD (positive) or -GasSpent USD (negative)
            gas_gwei: Current gas price
            next_state_data: Optional next state info for temporal difference learning
        """
        gas_level = self._discretize_gas(gas_gwei)
        state = self.get_state_key(chain_id, volatility, gas_level)
        action_key = f"{action_taken['slippage']}_{action_taken['priority']}"
        
        # Store experience in replay buffer (always track experiences)
        experience = {
            "state": state,
            "action": action_key,
            "reward": reward,
            "timestamp": datetime.now().isoformat()
        }
        self.replay_buffer.append(experience)
        
        # Only update Q-table if self-learning is enabled
        if self.self_learning_enabled:
            # Initialize state if new
            if state not in self.q_table:
                self.q_table[state] = {}
            if action_key not in self.q_table[state]:
                self.q_table[state][action_key] = 0.0

            # Q-Learning Update
            old_value = self.q_table[state][action_key]
            next_max = max(self.q_table[state].values()) if self.q_table[state] else 0
            
            # Temporal Difference Learning
            new_value = old_value + self.learning_rate * (
                reward + self.discount_factor * next_max - old_value
            )
            self.q_table[state][action_key] = new_value
            
            # Decay epsilon (explore less over time) - only when learning
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay
        
        # Always update metrics and state tracking
        self._update_metrics_without_learning(reward)
        
        # Periodically save (always save to maintain state consistency)
        if self.metrics["total_episodes"] % 10 == 0:
            if self.self_learning_enabled:
                self._save_q_table()
            self._save_metrics()
            self._save_replay_buffer()
    
    def _update_metrics_without_learning(self, reward):
        """
        Update performance metrics without modifying Q-table.
        Used when self-learning is disabled to track performance without updating the model.
        """
        self.metrics["total_episodes"] += 1
        self.metrics["total_rewards"] += reward
        self.metrics["avg_reward"] = self.metrics["total_rewards"] / self.metrics["total_episodes"]
        
        if reward > self.metrics["best_reward"]:
            self.metrics["best_reward"] = reward
        if reward < self.metrics["worst_reward"]:
            self.metrics["worst_reward"] = reward
        
        if reward > 0:
            self.metrics["successful_trades"] += 1
        else:
            self.metrics["failed_trades"] += 1
        
        total_trades = self.metrics["successful_trades"] + self.metrics["failed_trades"]
        if total_trades > 0:
            self.metrics["success_rate"] = (self.metrics["successful_trades"] / total_trades) * 100
    
    def batch_replay_learning(self, batch_size=32):
        """
        Learn from random samples in replay buffer.
        Improves learning stability and efficiency.
        """
        if len(self.replay_buffer) < batch_size:
            return
        
        # Sample random batch
        batch = random.sample(list(self.replay_buffer), batch_size)
        
        for experience in batch:
            state = experience["state"]
            action = experience["action"]
            reward = experience["reward"]
            
            if state not in self.q_table:
                self.q_table[state] = {}
            if action not in self.q_table[state]:
                self.q_table[state][action] = 0.0
            
            # Q-Learning update
            old_value = self.q_table[state][action]
            next_max = max(self.q_table[state].values()) if self.q_table[state] else 0
            
            new_value = old_value + self.learning_rate * (
                reward + self.discount_factor * next_max - old_value
            )
            self.q_table[state][action] = new_value
        
        # Save after batch learning
        self._save_q_table()
    
    def get_metrics(self):
        """Get current RL agent performance metrics"""
        metrics = self.metrics.copy()
        metrics["q_table_size"] = len(self.q_table)
        metrics["replay_buffer_size"] = len(self.replay_buffer)
        metrics["current_epsilon"] = self.epsilon
        return metrics
    
    def get_best_actions_per_state(self, top_n=5):
        """
        Get the best performing actions for each state.
        Useful for visualization and analysis.
        """
        best_actions = {}
        
        for state, actions in self.q_table.items():
            if actions:
                sorted_actions = sorted(actions.items(), key=lambda x: x[1], reverse=True)[:top_n]
                best_actions[state] = [
                    {"action": action, "q_value": q_val}
                    for action, q_val in sorted_actions
                ]
        
        return best_actions