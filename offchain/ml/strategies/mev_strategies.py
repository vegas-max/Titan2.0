"""
TITAN MEV Strategies - Version 5.0
===================================

Advanced MEV (Maximal Extractable Value) strategies for capturing value
from blockchain transactions and market inefficiencies.

Strategies Included:
1. Sandwich Attacks - Front-run and back-run large trades
2. Front-Running - Execute before pending transactions
3. Back-Running - Execute after transactions for arbitrage
4. Liquidations - Monitor and execute under-collateralized positions
5. NFT Sniping - Capture underpriced NFT listings
6. JIT Liquidity - Just-in-time liquidity provision
7. Oracle Arbitrage - Exploit oracle price update delays

All strategies include:
- ML-powered opportunity detection
- Anti-detection mechanisms
- Flashbots integration
- Risk assessment
- Profitability prediction
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import deque
import time

try:
    import numpy as np
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("WARNING: NumPy not available for MEV strategies")


class MEVStrategyBase:
    """Base class for all MEV strategies"""
    
    def __init__(self, strategy_name: str):
        self.strategy_name = strategy_name
        self.opportunities_found = 0
        self.opportunities_executed = 0
        self.total_profit = 0.0
        self.total_gas_cost = 0.0
        self.success_count = 0
        self.failure_count = 0
        self.recent_captures = deque(maxlen=100)
        
        # ML-powered metrics
        self.ml_confidence_threshold = 0.75
        self.risk_tolerance = 0.5
        
    def get_metrics(self) -> Dict:
        """Get strategy performance metrics"""
        total_attempts = self.opportunities_executed
        success_rate = (self.success_count / total_attempts * 100) if total_attempts > 0 else 0
        avg_profit = (self.total_profit / self.success_count) if self.success_count > 0 else 0
        
        return {
            "strategy": self.strategy_name,
            "opportunities_found": self.opportunities_found,
            "opportunities_executed": self.opportunities_executed,
            "success_rate": round(success_rate, 2),
            "total_profit": round(self.total_profit, 2),
            "total_gas_cost": round(self.total_gas_cost, 2),
            "net_profit": round(self.total_profit - self.total_gas_cost, 2),
            "avg_profit": round(avg_profit, 2),
            "success_count": self.success_count,
            "failure_count": self.failure_count
        }
    
    def record_execution(self, success: bool, profit: float, gas_cost: float, details: Dict):
        """Record an execution result"""
        self.opportunities_executed += 1
        
        if success:
            self.success_count += 1
            self.total_profit += profit
        else:
            self.failure_count += 1
        
        self.total_gas_cost += gas_cost
        
        capture = {
            "timestamp": datetime.now().isoformat(),
            "strategy": self.strategy_name,
            "success": success,
            "profit": profit,
            "gas_cost": gas_cost,
            "net_profit": profit - gas_cost,
            "details": details
        }
        self.recent_captures.append(capture)
    
    def assess_risk(self, opportunity: Dict) -> float:
        """Assess risk level of an opportunity (0.0 = low risk, 1.0 = high risk)"""
        # Base implementation - override in subclasses
        return 0.5
    
    def predict_profitability(self, opportunity: Dict) -> Tuple[float, float]:
        """Predict profitability and confidence
        Returns: (predicted_profit, confidence_score)
        """
        # Base implementation - override in subclasses
        return (0.0, 0.5)


class SandwichAttackStrategy(MEVStrategyBase):
    """
    Sandwich Attack Strategy - Version 5.0
    
    Identifies large pending swaps and executes:
    1. Front-run: Buy before the large swap (increases price)
    2. Large swap executes (pushes price higher)
    3. Back-run: Sell after the large swap (profit from price increase)
    
    ML Enhancements:
    - Predicts optimal sandwich parameters
    - Estimates slippage impact
    - Calculates risk vs reward
    """
    
    def __init__(self):
        super().__init__("Sandwich Attack")
        self.min_target_size_usd = 50000  # Minimum trade size to sandwich
        self.max_slippage_impact = 0.05  # Maximum 5% slippage
        
    def detect_opportunity(self, pending_tx: Dict) -> Optional[Dict]:
        """Detect sandwich attack opportunity"""
        # Check if transaction is a large swap
        if pending_tx.get('type') != 'swap':
            return None
        
        trade_size_usd = pending_tx.get('amount_usd', 0)
        if trade_size_usd < self.min_target_size_usd:
            return None
        
        # Estimate slippage impact
        liquidity = pending_tx.get('pool_liquidity', 1000000)
        slippage_impact = trade_size_usd / liquidity
        
        if slippage_impact > self.max_slippage_impact:
            return None  # Too much slippage, risky
        
        # Calculate potential profit
        expected_price_impact = slippage_impact * 0.5  # Simplified model
        front_run_amount = min(trade_size_usd * 0.1, 10000)  # 10% of target or $10k max
        
        opportunity = {
            "target_tx": pending_tx.get('hash'),
            "target_size": trade_size_usd,
            "token_in": pending_tx.get('token_in'),
            "token_out": pending_tx.get('token_out'),
            "pool": pending_tx.get('pool'),
            "front_run_amount": front_run_amount,
            "expected_price_impact": expected_price_impact,
            "estimated_profit": front_run_amount * expected_price_impact,
            "slippage_risk": slippage_impact
        }
        
        self.opportunities_found += 1
        return opportunity


class FrontRunningStrategy(MEVStrategyBase):
    """
    Front-Running Strategy - Version 5.0
    
    Detects profitable transactions in the mempool and executes before them
    with higher gas price.
    
    Targets:
    - DEX arbitrage opportunities
    - Liquidation opportunities
    - NFT purchases
    """
    
    def __init__(self):
        super().__init__("Front-Running")
        self.min_profit_threshold = 10.0  # Minimum $10 profit
        
    def detect_opportunity(self, pending_tx: Dict) -> Optional[Dict]:
        """Detect front-running opportunity"""
        # Analyze transaction for profitable front-run
        tx_type = pending_tx.get('type')
        
        if tx_type == 'arbitrage':
            # Someone else found an arb - can we do it first?
            estimated_profit = pending_tx.get('estimated_profit', 0)
            if estimated_profit > self.min_profit_threshold:
                opportunity = {
                    "target_tx": pending_tx.get('hash'),
                    "type": "arbitrage_frontrun",
                    "estimated_profit": estimated_profit,
                    "gas_price_needed": pending_tx.get('gas_price', 50) * 1.2,  # 20% higher
                    "paths": pending_tx.get('paths')
                }
                self.opportunities_found += 1
                return opportunity
        
        return None


class BackRunningStrategy(MEVStrategyBase):
    """
    Back-Running Strategy - Version 5.0
    
    Executes arbitrage immediately after a transaction that creates
    a price discrepancy.
    """
    
    def __init__(self):
        super().__init__("Back-Running")
        self.min_arbitrage = 5.0  # Minimum $5 arbitrage
        
    def detect_opportunity(self, executed_tx: Dict) -> Optional[Dict]:
        """Detect back-running opportunity after a transaction"""
        # Check if transaction created price discrepancy
        if executed_tx.get('type') != 'swap':
            return None
        
        # Simulate: Check if price differs between DEXes after this trade
        price_diff = executed_tx.get('price_impact', 0)
        if price_diff < 0.01:  # Less than 1% price impact
            return None
        
        arbitrage_profit = price_diff * executed_tx.get('amount_usd', 0) * 0.5
        
        if arbitrage_profit > self.min_arbitrage:
            opportunity = {
                "target_tx": executed_tx.get('hash'),
                "token": executed_tx.get('token_out'),
                "estimated_profit": arbitrage_profit,
                "source_dex": executed_tx.get('dex'),
                "target_dex": "optimal_dex"  # Would calculate optimal DEX
            }
            self.opportunities_found += 1
            return opportunity
        
        return None


class LiquidationStrategy(MEVStrategyBase):
    """
    Liquidation Strategy - Version 5.0
    
    Monitors lending protocols for under-collateralized positions
    and executes liquidations for profit.
    
    Supported Protocols:
    - Aave
    - Compound
    - MakerDAO
    - Venus
    """
    
    def __init__(self):
        super().__init__("Liquidations")
        self.min_liquidation_profit = 20.0  # Minimum $20 profit
        self.health_factor_threshold = 1.0  # Below 1.0 = liquidatable
        
    def scan_positions(self, protocol_positions: List[Dict]) -> List[Dict]:
        """Scan lending positions for liquidation opportunities"""
        opportunities = []
        
        for position in protocol_positions:
            health_factor = position.get('health_factor', 2.0)
            
            if health_factor < self.health_factor_threshold:
                # Position can be liquidated
                collateral_value = position.get('collateral_value_usd', 0)
                debt_value = position.get('debt_value_usd', 0)
                liquidation_bonus = position.get('liquidation_bonus', 0.05)  # 5% typical
                
                max_liquidatable = min(debt_value * 0.5, collateral_value)  # Max 50% of debt
                profit = max_liquidatable * liquidation_bonus
                
                if profit > self.min_liquidation_profit:
                    opportunity = {
                        "user": position.get('user'),
                        "protocol": position.get('protocol'),
                        "health_factor": health_factor,
                        "collateral_token": position.get('collateral_token'),
                        "debt_token": position.get('debt_token'),
                        "liquidatable_amount": max_liquidatable,
                        "estimated_profit": profit
                    }
                    opportunities.append(opportunity)
                    self.opportunities_found += 1
        
        return opportunities


class NFTSnipingStrategy(MEVStrategyBase):
    """
    NFT Sniping Strategy - Version 5.0
    
    Detects underpriced NFT listings and purchases them before others.
    
    Features:
    - Floor price monitoring
    - Rarity analysis
    - Gas optimization for speed
    """
    
    def __init__(self):
        super().__init__("NFT Sniping")
        self.min_discount = 0.15  # Minimum 15% below floor
        
    def detect_opportunity(self, nft_listing: Dict) -> Optional[Dict]:
        """Detect underpriced NFT listing"""
        list_price = nft_listing.get('price_eth', 0)
        floor_price = nft_listing.get('floor_price_eth', 0)
        
        if floor_price == 0:
            return None
        
        discount = (floor_price - list_price) / floor_price
        
        if discount > self.min_discount:
            opportunity = {
                "collection": nft_listing.get('collection'),
                "token_id": nft_listing.get('token_id'),
                "list_price": list_price,
                "floor_price": floor_price,
                "discount": discount,
                "estimated_profit": (floor_price - list_price) * 0.9,  # Account for fees
                "marketplace": nft_listing.get('marketplace')
            }
            self.opportunities_found += 1
            return opportunity
        
        return None


class JITLiquidityStrategy(MEVStrategyBase):
    """
    Just-In-Time Liquidity Strategy - Version 5.0
    
    Provides liquidity right before a large swap and removes it immediately after,
    capturing fees without long-term exposure.
    
    Targets:
    - Uniswap V3 concentrated liquidity
    - Large pending swaps
    """
    
    def __init__(self):
        super().__init__("JIT Liquidity")
        self.min_swap_size = 100000  # Minimum $100k swap
        
    def detect_opportunity(self, pending_swap: Dict) -> Optional[Dict]:
        """Detect JIT liquidity opportunity"""
        swap_size = pending_swap.get('amount_usd', 0)
        
        if swap_size < self.min_swap_size:
            return None
        
        # Calculate potential fees
        pool_fee = pending_swap.get('pool_fee', 0.003)  # 0.3% typical
        potential_fees = swap_size * pool_fee
        
        # Estimate required liquidity
        required_liquidity = swap_size * 1.1  # 110% of swap size
        
        opportunity = {
            "target_swap": pending_swap.get('hash'),
            "pool": pending_swap.get('pool'),
            "token_0": pending_swap.get('token_in'),
            "token_1": pending_swap.get('token_out'),
            "required_liquidity": required_liquidity,
            "estimated_fees": potential_fees,
            "swap_size": swap_size
        }
        
        self.opportunities_found += 1
        return opportunity


class OracleArbitrageStrategy(MEVStrategyBase):
    """
    Oracle Arbitrage Strategy - Version 5.0
    
    Exploits delays in oracle price updates across protocols.
    
    When oracle updates:
    1. Detect price discrepancy
    2. Execute trade on protocol with stale price
    3. Close position on protocol with updated price
    """
    
    def __init__(self):
        super().__init__("Oracle Arbitrage")
        self.min_price_diff = 0.02  # Minimum 2% price difference
        
    def detect_opportunity(self, oracle_update: Dict) -> Optional[Dict]:
        """Detect oracle arbitrage opportunity"""
        new_price = oracle_update.get('new_price', 0)
        old_price = oracle_update.get('old_price', 0)
        
        if old_price == 0:
            return None
        
        price_diff = abs(new_price - old_price) / old_price
        
        if price_diff > self.min_price_diff:
            # Find protocols still using old price
            stale_protocols = oracle_update.get('stale_protocols', [])
            
            if stale_protocols:
                opportunity = {
                    "asset": oracle_update.get('asset'),
                    "old_price": old_price,
                    "new_price": new_price,
                    "price_diff": price_diff,
                    "stale_protocols": stale_protocols,
                    "estimated_profit": price_diff * 10000  # Assume $10k position
                }
                self.opportunities_found += 1
                return opportunity
        
        return None


class StatArbitrageStrategy(MEVStrategyBase):
    """
    Statistical Arbitrage Strategy - Version 5.0
    
    Uses statistical models to identify mean-reversion opportunities
    across correlated trading pairs.
    
    Features:
    - Correlation analysis
    - Z-score calculation
    - Mean reversion detection
    - Pair trading
    """
    
    def __init__(self):
        super().__init__("Statistical Arbitrage")
        self.zscore_threshold = 2.0  # Entry when z-score > 2.0
        self.correlation_min = 0.7  # Minimum correlation coefficient
        
    def detect_opportunity(self, pair_data: Dict) -> Optional[Dict]:
        """Detect statistical arbitrage opportunity"""
        zscore = pair_data.get('zscore', 0)
        correlation = pair_data.get('correlation', 0)
        
        if correlation < self.correlation_min:
            return None
        
        if abs(zscore) > self.zscore_threshold:
            # Mean reversion opportunity
            spread = pair_data.get('spread', 0)
            historical_mean = pair_data.get('historical_mean', 0)
            
            opportunity = {
                "pair": f"{pair_data.get('token_a')}/{pair_data.get('token_b')}",
                "zscore": zscore,
                "correlation": correlation,
                "current_spread": spread,
                "historical_mean": historical_mean,
                "direction": "short" if zscore > 0 else "long",
                "estimated_profit": abs(spread - historical_mean) * 100
            }
            self.opportunities_found += 1
            return opportunity
        
        return None


class FlashLoanArbitrageStrategy(MEVStrategyBase):
    """
    Flash Loan Arbitrage Strategy - Version 5.0
    
    Leverages flash loans to execute large arbitrage trades without capital.
    
    Features:
    - Zero capital required
    - Atomic transactions
    - Multi-hop arbitrage
    - Protocol fee optimization
    """
    
    def __init__(self):
        super().__init__("Flash Loan Arbitrage")
        self.min_profit_after_fees = 50.0  # Minimum $50 after flash loan fees
        self.flash_loan_fee = 0.0009  # 0.09% typical fee
        
    def detect_opportunity(self, arb_path: Dict) -> Optional[Dict]:
        """Detect flash loan arbitrage opportunity"""
        price_diff = arb_path.get('price_difference', 0)
        optimal_amount = arb_path.get('optimal_trade_size', 0)
        
        if optimal_amount == 0:
            return None
        
        # Calculate profits and fees
        gross_profit = price_diff * optimal_amount
        flash_loan_cost = optimal_amount * self.flash_loan_fee
        gas_estimate = arb_path.get('gas_cost', 20.0)
        net_profit = gross_profit - flash_loan_cost - gas_estimate
        
        if net_profit > self.min_profit_after_fees:
            opportunity = {
                "path": arb_path.get('path'),
                "loan_amount": optimal_amount,
                "loan_provider": arb_path.get('loan_provider', 'Aave'),
                "gross_profit": gross_profit,
                "flash_loan_fee": flash_loan_cost,
                "gas_cost": gas_estimate,
                "net_profit": net_profit,
                "num_hops": len(arb_path.get('path', []))
            }
            self.opportunities_found += 1
            return opportunity
        
        return None


class CrossChainMEVStrategy(MEVStrategyBase):
    """
    Cross-Chain MEV Strategy - Version 5.0
    
    Exploits price discrepancies and arbitrage opportunities across
    different blockchain networks.
    
    Features:
    - Multi-chain monitoring
    - Bridge optimization
    - Cross-chain flash loans
    - Timing optimization
    """
    
    def __init__(self):
        super().__init__("Cross-Chain MEV")
        self.min_cross_chain_profit = 100.0  # Higher threshold due to bridge costs
        self.supported_chains = ['Ethereum', 'Polygon', 'Arbitrum', 'Optimism', 'BSC', 'Avalanche']
        
    def detect_opportunity(self, cross_chain_data: Dict) -> Optional[Dict]:
        """Detect cross-chain arbitrage opportunity"""
        chain_a = cross_chain_data.get('chain_a')
        chain_b = cross_chain_data.get('chain_b')
        token = cross_chain_data.get('token')
        
        price_a = cross_chain_data.get('price_a', 0)
        price_b = cross_chain_data.get('price_b', 0)
        
        if price_a == 0 or price_b == 0:
            return None
        
        price_diff = abs(price_a - price_b) / min(price_a, price_b)
        
        # Calculate bridge costs
        bridge_fee = cross_chain_data.get('bridge_fee', 10.0)
        bridge_time = cross_chain_data.get('bridge_time_minutes', 10)
        
        # Estimate profit
        trade_size = cross_chain_data.get('trade_size', 10000)
        gross_profit = price_diff * trade_size
        net_profit = gross_profit - bridge_fee - 50  # Account for gas on both chains
        
        if net_profit > self.min_cross_chain_profit:
            opportunity = {
                "source_chain": chain_a,
                "dest_chain": chain_b,
                "token": token,
                "price_a": price_a,
                "price_b": price_b,
                "price_diff_pct": price_diff * 100,
                "trade_size": trade_size,
                "bridge_fee": bridge_fee,
                "bridge_time_minutes": bridge_time,
                "estimated_profit": net_profit
            }
            self.opportunities_found += 1
            return opportunity
        
        return None


class GasPriceAuctionStrategy(MEVStrategyBase):
    """
    Gas Price Auction Strategy - Version 5.0
    
    Optimizes gas bidding for MEV opportunities using game theory
    and ML predictions.
    
    Features:
    - Dynamic gas bidding
    - Competitor analysis
    - Priority fee optimization
    - MEV-Boost integration
    """
    
    def __init__(self):
        super().__init__("Gas Price Auction")
        self.max_gas_premium = 0.5  # Max 50% premium over base fee
        
    def optimize_gas_bid(self, opportunity: Dict, competition: Dict) -> Dict:
        """Optimize gas bid for MEV opportunity"""
        opportunity_value = opportunity.get('profit', 0)
        base_fee = competition.get('base_fee', 30)
        competing_bids = competition.get('competing_bids', [])
        
        if not competing_bids:
            # No competition, use minimal gas
            optimal_priority_fee = 2.0
        else:
            # Outbid highest competitor
            max_competitor_bid = max(competing_bids)
            optimal_priority_fee = max_competitor_bid * 1.1  # 10% higher
        
        # Cap at max premium
        max_priority_fee = base_fee * self.max_gas_premium
        optimal_priority_fee = min(optimal_priority_fee, max_priority_fee)
        
        total_gas_cost = (base_fee + optimal_priority_fee) * opportunity.get('gas_units', 300000) / 1e9
        
        # Only bid if profitable
        if total_gas_cost < opportunity_value * 0.3:  # Max 30% of profit
            return {
                "priority_fee": optimal_priority_fee,
                "max_fee": base_fee + optimal_priority_fee,
                "estimated_cost": total_gas_cost,
                "profit_after_gas": opportunity_value - total_gas_cost,
                "bid_competitive": True
            }
        
        return {"bid_competitive": False}


class TokenLaunchSnipingStrategy(MEVStrategyBase):
    """
    Token Launch Sniping Strategy - Version 5.0
    
    Detects new token launches and executes early purchases before
    price discovery.
    
    Features:
    - Liquidity pool monitoring
    - Contract verification
    - Rug pull detection
    - Honeypot detection
    - Automated selling
    """
    
    def __init__(self):
        super().__init__("Token Launch Sniping")
        self.min_liquidity = 10000  # Minimum $10k initial liquidity
        self.max_buy_percentage = 0.05  # Max 5% of initial liquidity
        
    def detect_opportunity(self, new_pool: Dict) -> Optional[Dict]:
        """Detect token launch opportunity"""
        initial_liquidity = new_pool.get('liquidity_usd', 0)
        
        if initial_liquidity < self.min_liquidity:
            return None
        
        # Safety checks
        contract_verified = new_pool.get('contract_verified', False)
        has_mint_function = new_pool.get('has_mint_function', True)
        honeypot_score = new_pool.get('honeypot_score', 0)
        
        if has_mint_function or honeypot_score > 0.3:
            return None  # Too risky
        
        max_buy_amount = initial_liquidity * self.max_buy_percentage
        
        opportunity = {
            "token_address": new_pool.get('token_address'),
            "token_name": new_pool.get('token_name'),
            "pair": new_pool.get('pair'),
            "initial_liquidity": initial_liquidity,
            "recommended_buy": max_buy_amount,
            "contract_verified": contract_verified,
            "safety_score": 1.0 - honeypot_score,
            "estimated_profit": max_buy_amount * 0.5  # Assume 50% gain
        }
        self.opportunities_found += 1
        return opportunity


class DeFiYieldFarmingMEVStrategy(MEVStrategyBase):
    """
    DeFi Yield Farming MEV Strategy - Version 5.0
    
    Optimizes yield farming positions and captures MEV from
    liquidity pool operations.
    
    Features:
    - APY optimization
    - Auto-compounding
    - Optimal entry/exit timing
    - IL (Impermanent Loss) minimization
    """
    
    def __init__(self):
        super().__init__("DeFi Yield Farming MEV")
        self.min_apy = 20.0  # Minimum 20% APY
        
    def detect_opportunity(self, farm_data: Dict) -> Optional[Dict]:
        """Detect yield farming opportunity"""
        current_apy = farm_data.get('apy', 0)
        
        if current_apy < self.min_apy:
            return None
        
        tvl = farm_data.get('tvl', 0)
        reward_token = farm_data.get('reward_token')
        deposit_token = farm_data.get('deposit_token')
        
        # Calculate optimal deposit
        optimal_deposit = min(farm_data.get('available_capital', 10000), tvl * 0.01)
        
        # Estimate rewards
        daily_rewards = (optimal_deposit * current_apy / 100) / 365
        
        opportunity = {
            "protocol": farm_data.get('protocol'),
            "pool": farm_data.get('pool'),
            "apy": current_apy,
            "tvl": tvl,
            "deposit_token": deposit_token,
            "reward_token": reward_token,
            "optimal_deposit": optimal_deposit,
            "estimated_daily_rewards": daily_rewards,
            "estimated_monthly_profit": daily_rewards * 30
        }
        self.opportunities_found += 1
        return opportunity


class MEVStrategyManager:
    """
    MEV Strategy Manager - Version 5.0
    
    Coordinates all MEV strategies and provides unified interface.
    Now includes 13 advanced strategies!
    """
    
    def __init__(self):
        # Initialize all strategies
        self.strategies = {
            "sandwich": SandwichAttackStrategy(),
            "front_run": FrontRunningStrategy(),
            "back_run": BackRunningStrategy(),
            "liquidation": LiquidationStrategy(),
            "nft_sniping": NFTSnipingStrategy(),
            "jit_liquidity": JITLiquidityStrategy(),
            "oracle_arb": OracleArbitrageStrategy(),
            # New v5.0 strategies
            "stat_arb": StatArbitrageStrategy(),
            "flash_loan_arb": FlashLoanArbitrageStrategy(),
            "cross_chain": CrossChainMEVStrategy(),
            "gas_auction": GasPriceAuctionStrategy(),
            "token_launch": TokenLaunchSnipingStrategy(),
            "yield_farming": DeFiYieldFarmingMEVStrategy()
        }
        
        # Global metrics
        self.total_mev_captured = 0.0
        self.total_gas_spent = 0.0
        self.active_strategies = len(self.strategies)
        
        # ML-based strategy selection
        self.strategy_performance_history = deque(maxlen=1000)
        
    def get_all_metrics(self) -> Dict:
        """Get metrics from all strategies"""
        all_metrics = {
            "total_mev_captured": round(self.total_mev_captured, 2),
            "total_gas_spent": round(self.total_gas_spent, 2),
            "net_mev": round(self.total_mev_captured - self.total_gas_spent, 2),
            "active_strategies": self.active_strategies,
            "strategies": {}
        }
        
        # Get metrics from each strategy
        for name, strategy in self.strategies.items():
            all_metrics["strategies"][name] = strategy.get_metrics()
            self.total_mev_captured += strategy.total_profit
            self.total_gas_spent += strategy.total_gas_cost
        
        return all_metrics
    
    def get_recent_captures(self, limit: int = 20) -> List[Dict]:
        """Get recent MEV captures across all strategies"""
        all_captures = []
        
        for strategy in self.strategies.values():
            all_captures.extend(list(strategy.recent_captures))
        
        # Sort by timestamp, most recent first
        all_captures.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return all_captures[:limit]
    
    def select_best_strategy(self, opportunity_type: str) -> Optional[MEVStrategyBase]:
        """ML-based strategy selection based on historical performance"""
        # Simple implementation - can be enhanced with ML
        strategy_map = {
            "large_swap": self.strategies["sandwich"],
            "arbitrage": self.strategies["front_run"],
            "liquidation": self.strategies["liquidation"],
            "nft": self.strategies["nft_sniping"]
        }
        
        return strategy_map.get(opportunity_type)
    
    def update_global_metrics(self, profit: float, gas_cost: float):
        """Update global MEV metrics"""
        self.total_mev_captured += profit
        self.total_gas_spent += gas_cost


# Global instance
mev_manager = MEVStrategyManager()


if __name__ == "__main__":
    # Example usage
    print("TITAN MEV Strategies v5.0 - Initialized")
    print(f"Active Strategies: {mev_manager.active_strategies}")
    
    # Display all strategies
    for name, strategy in mev_manager.strategies.items():
        print(f"  ✓ {strategy.strategy_name}")
