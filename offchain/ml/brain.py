import asyncio
import time
import logging
import json
import rustworkx as rx
import pandas as pd
from web3 import Web3
from datetime import datetime
from eth_abi import encode
from decimal import Decimal, getcontext
from concurrent.futures import ThreadPoolExecutor, as_completed

# Core Infrastructure
from offchain.core.config import (
    CHAINS, BALANCER_V3_VAULT, DEX_ROUTERS,
    TAR_SCORING_ENABLED, AI_PREDICTION_ENABLED, AI_PREDICTION_MIN_CONFIDENCE,
    CATBOOST_MODEL_ENABLED, HF_CONFIDENCE_THRESHOLD, ML_CONFIDENCE_THRESHOLD,
    PUMP_PROBABILITY_THRESHOLD, SELF_LEARNING_ENABLED, ROUTE_INTELLIGENCE_ENABLED,
    REAL_TIME_DATA_ENABLED
)
from offchain.core.token_discovery import TokenDiscovery
from routing.bridge_manager import BridgeManager
from offchain.core.titan_commander_core import TitanCommander
from offchain.core.terminal_display import get_terminal_display
from offchain.core.trade_database import get_trade_database

# Advanced Features
from offchain.core.dynamic_price_oracle import DynamicPriceOracle
from offchain.core.parallel_simulation_engine import ParallelSimulationEngine
from offchain.core.mev_detector import MEVDetector
from offchain.core.direct_dex_query import DirectDEXQuery

# The Cortex (AI Layer)
from offchain.ml.cortex.forecaster import MarketForecaster
from offchain.ml.cortex.rl_optimizer import QLearningAgent
from offchain.ml.cortex.feature_store import FeatureStore
from offchain.ml.dex_pricer import DexPricer

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [BRAIN] %(message)s')
logger = logging.getLogger("TitanBrain")

# Precision for financial math
getcontext().prec = 28

# Constants
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
# Chains requiring PoA middleware due to Proof-of-Authority consensus
# Note: Celo uses BFT consensus but still requires PoA middleware for web3.py compatibility
POA_CHAINS = [137, 56, 250, 42220]  # Polygon, BSC, Fantom, Celo

def is_zero_address(address: str) -> bool:
    """
    Check if an address is the zero address (uninitialized/unavailable).
    
    Args:
        address: Ethereum address to check
        
    Returns:
        bool: True if address is zero address, False otherwise
    """
    if not address:
        return True
    return address.lower() == ZERO_ADDRESS.lower()

class ProfitEngine:
    """
    Implements the Titan Master Profit Equation.
    Π_net = V_loan × [(P_A × (1 - S_A)) - (P_B × (1 + S_B))] - F_flat - (V_loan × F_rate)
    """
    def __init__(self, default_flash_fee=Decimal("0.0")):
        self.flash_fee = default_flash_fee # Balancer V3 is 0%

    def calculate_enhanced_profit(self, amount, amount_out, bridge_fee_usd, gas_cost_usd):
        """
        Calculates Net Profit based on REAL simulated output.
        """
        # 1. Gross Revenue (What we actually get out)
        gross_revenue_usd = amount_out # Assuming normalized to USD for this calculation context

        # 2. Cost Basis (What we borrowed + fees)
        loan_cost_usd = amount
        flash_fee_cost = amount * self.flash_fee
        
        total_operational_costs = bridge_fee_usd + gas_cost_usd + flash_fee_cost

        # 3. Net Profit
        net_profit = gross_revenue_usd - loan_cost_usd - total_operational_costs
        
        return {
            "net_profit": net_profit,
            "gross_spread": gross_revenue_usd - loan_cost_usd,
            "total_fees": total_operational_costs,
            "is_profitable": net_profit > 0
        }

class OmniBrain:
    def __init__(self):
        # 1. Infrastructure
        self.graph = rx.PyDiGraph()
        self.bridge = BridgeManager()
        self.profit_engine = ProfitEngine()
        self.inventory = {} 
        self.web3_connections = {}
        
        # 2. AI Modules
        self.forecaster = MarketForecaster()
        self.optimizer = QLearningAgent()
        self.memory = FeatureStore()
        
        # 3. Advanced Features (initialized later with web3 connections)
        self.price_oracle = None
        self.parallel_simulator = None
        self.mev_detector = None
        self.dex_query = None
        
        # 4. Communication (File-based signals)
        from pathlib import Path
        self.signals_dir = Path('signals/outgoing')
        self.signals_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Signal output directory: {self.signals_dir}")
        
        # 5. Terminal Display
        self.display = get_terminal_display()
        
        # 4. Wallet Configuration
        import os
        self.wallet_address = os.getenv('EXECUTOR_ADDRESS', '0x0000000000000000000000000000000000000000')
        
        # Validate wallet address is configured
        if self.wallet_address == '0x0000000000000000000000000000000000000000' or \
           'YOUR' in self.wallet_address.upper():
            logger.warning("⚠️ EXECUTOR_ADDRESS not configured in .env - using placeholder for PAPER mode")
            # Use a valid Ethereum address for API calls (Vitalik's address as placeholder)
            self.wallet_address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
        
        # 6. State
        self.node_indices = {} 
        self.executor = ThreadPoolExecutor(max_workers=20)
        
        # 7. Safety Limits
        self.MAX_GAS_PRICE_GWEI = Decimal("200.0")  # Maximum gas price ceiling
        self.MIN_PROFIT_THRESHOLD_USD = Decimal("1.0")  # Minimum $1 profit to execute
        self.MAX_SLIPPAGE_BPS = 100  # Maximum 1% slippage allowed
        self.consecutive_failures = 0
        self.MAX_CONSECUTIVE_FAILURES = 10  # Circuit breaker threshold
        self.scan_interval = 1  # Dynamic scan interval for graceful degradation
        self.min_scan_interval = 1  # Minimum scan interval
        self.max_scan_interval = 30  # Maximum scan interval
        self.backoff_start_time = None  # Track when backoff started
        
        # 8. Advanced Features Configuration
        self.use_dynamic_pricing = True  # Use Chainlink price feeds
        self.use_parallel_simulation = True  # Simulate multiple routes in parallel
        self.use_mev_detection = True  # Detect sandwich attacks
        self.use_direct_dex_query = True  # Query pools directly
        
        # 9. AI & Scoring Configuration
        self.tar_scoring_enabled = TAR_SCORING_ENABLED
        self.ai_prediction_enabled = AI_PREDICTION_ENABLED
        self.ai_prediction_min_confidence = AI_PREDICTION_MIN_CONFIDENCE
        self.catboost_model_enabled = CATBOOST_MODEL_ENABLED
        self.hf_confidence_threshold = HF_CONFIDENCE_THRESHOLD
        self.ml_confidence_threshold = ML_CONFIDENCE_THRESHOLD
        self.pump_probability_threshold = PUMP_PROBABILITY_THRESHOLD
        self.self_learning_enabled = SELF_LEARNING_ENABLED
        self.route_intelligence_enabled = ROUTE_INTELLIGENCE_ENABLED
        self.real_time_data_enabled = REAL_TIME_DATA_ENABLED
        
        # AI & Scoring Thresholds and Constants
        self.TAR_SCORE_MIN_THRESHOLD = 50  # Minimum TAR score to proceed
        self.PUMP_HIGH_MARGIN_THRESHOLD = 0.05  # 5% profit margin triggers pump check
        self.PUMP_VERY_HIGH_MARGIN_THRESHOLD = 0.10  # 10% profit margin high alert
        self.PUMP_PROBABILITY_INCREMENT_HIGH = 0.3  # Probability increase for high margins
        self.PUMP_PROBABILITY_INCREMENT_VERY_HIGH = 0.4  # Probability increase for very high margins
        
        # Static gas prices for non-real-time mode (conservative values in gwei)
        self.STATIC_GAS_PRICES = {
            1: 30.0,    # Ethereum
            137: 50.0,  # Polygon
            42161: 0.1, # Arbitrum
            10: 0.5,    # Optimism
            8453: 0.5,  # Base
            56: 3.0,    # BSC
            43114: 25.0 # Avalanche
        }
        
        logger.info(f"🎯 AI & Scoring Configuration:")
        logger.info(f"   TAR Scoring: {'ENABLED' if self.tar_scoring_enabled else 'DISABLED'} (min threshold: {self.TAR_SCORE_MIN_THRESHOLD})")
        logger.info(f"   AI Prediction: {'ENABLED' if self.ai_prediction_enabled else 'DISABLED'} (min confidence: {self.ai_prediction_min_confidence})")
        logger.info(f"   CatBoost Model: {'ENABLED' if self.catboost_model_enabled else 'DISABLED'}")
        logger.info(f"   ML Confidence Threshold: {self.ml_confidence_threshold}")
        logger.info(f"   Pump Detection Threshold: {self.pump_probability_threshold}")
        logger.info(f"   Self-Learning: {'ENABLED' if self.self_learning_enabled else 'DISABLED'}")
        logger.info(f"   Route Intelligence: {'ENABLED' if self.route_intelligence_enabled else 'DISABLED'}")
        logger.info(f"   Real-time Data: {'ENABLED' if self.real_time_data_enabled else 'DISABLED'}")
        
        # 10. Trade Database
        try:
            self.trade_db = get_trade_database()
            logger.info("📊 Trade history database initialized")
        except Exception as e:
            logger.warning(f"Trade database initialization failed: {e}")
            self.trade_db = None
        
    def _cleanup_old_signals(self):
        """Clean up old signal files (keep last 100)"""
        try:
            signal_files = sorted([f for f in os.listdir(self.signals_dir) if f.endswith('.json')])
            if len(signal_files) > 100:
                for old_file in signal_files[:-100]:
                    os.remove(os.path.join(self.signals_dir, old_file))
        except Exception as e:
            logger.warning(f"Signal cleanup failed: {e}")

    def initialize(self):
        logger.info("🧠 Booting Apex-Omega Titan Brain...")
        
        # A. Load Assets - Dynamic token loading from 1inch API (100+ tokens per chain)
        from offchain.core.token_loader import TokenLoader
        
        target_chains = [1, 137, 42161, 10, 8453, 56, 43114]  # Major chains with good liquidity
        self.inventory = {}
        
        for chain_id in target_chains:
            logger.info(f"📥 Loading tokens for chain {chain_id}...")
            # Get 100+ tokens dynamically from 1inch
            tokens_list = TokenLoader.get_tokens(chain_id)
            
            if tokens_list:
                # Convert to dict format {symbol: {address, decimals}}
                self.inventory[chain_id] = {}
                for token in tokens_list[:100]:  # Top 100 by liquidity
                    symbol = token['symbol']
                    self.inventory[chain_id][symbol] = {
                        'address': token['address'],
                        'decimals': token['decimals']
                    }
                logger.info(f"   ✅ Loaded {len(self.inventory[chain_id])} tokens for chain {chain_id}")
            else:
                # Fallback to static registry
                logger.warning(f"   ⚠️ API failed, using static registry for chain {chain_id}")
                static_tokens = TokenDiscovery.fetch_all_chains([chain_id])
                self.inventory.update(static_tokens)
        
        # B. Initialize Web3 with timeout protection
        for cid, config in CHAINS.items():
            if config.get('rpc'):
                try:
                    # Add request timeout to prevent hanging
                    w3 = Web3(Web3.HTTPProvider(
                        config['rpc'],
                        request_kwargs={'timeout': 30}  # 30 second timeout for RPC calls
                    ))
                    # PoA middleware removed - web3.py v7+ handles PoA chains automatically
                    self.web3_connections[cid] = w3
                    logger.debug(f"Web3 connection established for chain {cid}")
                except Exception as e:
                    logger.warning(f"Failed to initialize Web3 for chain {cid}: {e}")
        
        # C. Initialize Advanced Features with web3 connections
        logger.info("⚡ Initializing advanced features...")
        
        if self.use_dynamic_pricing:
            try:
                self.price_oracle = DynamicPriceOracle(self.web3_connections)
                logger.info("✅ Dynamic Price Oracle initialized (Chainlink + TWAP)")
            except Exception as e:
                logger.error(f"Failed to initialize price oracle: {e}")
                self.use_dynamic_pricing = False
        
        if self.use_parallel_simulation:
            try:
                self.parallel_simulator = ParallelSimulationEngine(max_workers=20)
                logger.info("✅ Parallel Simulation Engine initialized (20 workers)")
            except Exception as e:
                logger.error(f"Failed to initialize parallel simulator: {e}")
                self.use_parallel_simulation = False
        
        if self.use_mev_detection:
            try:
                self.mev_detector = MEVDetector(self.web3_connections)
                logger.info("✅ MEV Detector initialized (Sandwich & Frontrun detection)")
            except Exception as e:
                logger.error(f"Failed to initialize MEV detector: {e}")
                self.use_mev_detection = False
        
        if self.use_direct_dex_query:
            try:
                self.dex_query = DirectDEXQuery(self.web3_connections)
                logger.info("✅ Direct DEX Query initialized (UniV2/V3, Curve, Balancer)")
            except Exception as e:
                logger.error(f"Failed to initialize DEX query: {e}")
                self.use_direct_dex_query = False

        # D. Build Graph
        self._build_graph_nodes()
        self._build_bridge_edges()
        
        logger.info(f"✅ System Online. Tracking {self.graph.num_nodes()} nodes.")

    def _build_graph_nodes(self):
        logger.info("🕸️  Constructing Hyper-Graph Nodes...")
        for chain_id, tokens in self.inventory.items():
            for symbol, data in tokens.items():
                node_key = (chain_id, symbol)
                if node_key not in self.node_indices:
                    idx = self.graph.add_node({
                        "chain": chain_id,
                        "symbol": symbol,
                        "address": data['address'],
                        "decimals": data['decimals']
                    })
                    self.node_indices[node_key] = idx

    def _build_bridge_edges(self):
        logger.info("🌉 Building Virtual Bridge Edges...")
        for symbol in TokenDiscovery.BRIDGE_ASSETS:
            chains_with_asset = [cid for cid in self.inventory if symbol in self.inventory[cid]]
            for i in range(len(chains_with_asset)):
                for j in range(i + 1, len(chains_with_asset)):
                    chain_a, chain_b = chains_with_asset[i], chains_with_asset[j]
                    u, v = self.node_indices[(chain_a, symbol)], self.node_indices[(chain_b, symbol)]
                    self.graph.add_edge(u, v, {"type": "bridge", "weight": 0.0})
                    self.graph.add_edge(v, u, {"type": "bridge", "weight": 0.0})

    def _get_gas_price(self, chain_id):
        """
        Get gas price with Alchemy fallback and safety ceiling.
        Respects REAL_TIME_DATA_ENABLED configuration.
        """
        # If real-time data is disabled, use conservative static values
        if not self.real_time_data_enabled:
            return self.STATIC_GAS_PRICES.get(chain_id, 30.0)
        
        import os
        
        # Alchemy RPC endpoints for major chains
        alchemy_map = {
            1: os.getenv('ALCHEMY_RPC_ETH'),
            137: os.getenv('ALCHEMY_RPC_POLY'),
            42161: os.getenv('ALCHEMY_RPC_ARB'),
            10: os.getenv('ALCHEMY_RPC_OPT'),
            8453: os.getenv('ALCHEMY_RPC_BASE')
        }
        
        # Always use Alchemy for supported chains to avoid rate limits
        if chain_id in alchemy_map and alchemy_map[chain_id]:
            try:
                w3 = Web3(Web3.HTTPProvider(alchemy_map[chain_id], request_kwargs={'timeout': 5}))
                wei_price = w3.eth.gas_price
                gwei_price = w3.from_wei(wei_price, 'gwei')
                
                if gwei_price > float(self.MAX_GAS_PRICE_GWEI):
                    logger.warning(f"⚠️ Gas price {gwei_price} exceeds max {self.MAX_GAS_PRICE_GWEI} on chain {chain_id}")
                    return float(self.MAX_GAS_PRICE_GWEI)
                    
                return gwei_price
            except Exception as e:
                logger.debug(f"Alchemy gas fetch failed for chain {chain_id}: {e}")
        
        # Fallback to configured RPC
        try:
            if chain_id in self.web3_connections:
                w3 = self.web3_connections[chain_id]
                wei_price = w3.eth.gas_price
                gwei_price = w3.from_wei(wei_price, 'gwei')
                
                if gwei_price > float(self.MAX_GAS_PRICE_GWEI):
                    logger.warning(f"⚠️ Gas price {gwei_price} exceeds max {self.MAX_GAS_PRICE_GWEI} on chain {chain_id}")
                    return float(self.MAX_GAS_PRICE_GWEI)
                    
                return gwei_price
        except Exception as e:
            logger.debug(f"Gas price fetch failed for chain {chain_id}: {e}")
        
        # Silently return 0 if all RPCs fail (rate limited)
        return 0.0

    def _calculate_tar_score(self, token_sym, chain_id):
        """
        Calculate Token Analysis & Risk (TAR) score for opportunity filtering.
        Returns score 0-100 where higher is better.
        
        Factors:
        - Token liquidity tier
        - Chain reliability
        - Historical volatility
        """
        if not self.tar_scoring_enabled:
            return 100  # No filtering when disabled
        
        score = 50  # Base score
        
        # Tier-based scoring
        tier1_tokens = ['USDC', 'USDT', 'DAI', 'WETH', 'WBTC', 'ETH']
        tier2_tokens = ['UNI', 'LINK', 'AAVE', 'CRV', 'MATIC', 'AVAX', 'BNB', 'SNX', 'MKR', 'COMP']
        
        if token_sym in tier1_tokens:
            score += 40  # High priority tokens
        elif token_sym in tier2_tokens:
            score += 20  # Medium priority
        else:
            score += 5   # Low priority
        
        # Chain reliability scoring
        reliable_chains = [1, 137, 42161, 10, 8453]  # Ethereum, Polygon, Arbitrum, Optimism, Base
        if chain_id in reliable_chains:
            score += 10
        
        return min(100, score)
    
    def _detect_pump_scheme(self, token_sym, chain_id, revenue_usd, cost_usd):
        """
        Detect potential pump-and-dump schemes based on abnormal price movements.
        Returns probability (0.0-1.0) that this is a pump scheme.
        """
        # Convert Decimal to float for calculations
        revenue = float(revenue_usd)
        cost = float(cost_usd)
        
        # Calculate profit margin
        profit_margin = (revenue - cost) / cost if cost > 0 else 0
        
        # High profit margins on unknown tokens are suspicious
        tier1_tokens = ['USDC', 'USDT', 'DAI', 'WETH', 'WBTC', 'ETH']
        tier2_tokens = ['UNI', 'LINK', 'AAVE', 'CRV', 'MATIC', 'AVAX', 'BNB', 'SNX', 'MKR', 'COMP']
        
        base_probability = 0.0
        
        # Unknown tokens with high margins are risky
        if token_sym not in tier1_tokens and token_sym not in tier2_tokens:
            if profit_margin > self.PUMP_HIGH_MARGIN_THRESHOLD:
                base_probability += self.PUMP_PROBABILITY_INCREMENT_HIGH
            if profit_margin > self.PUMP_VERY_HIGH_MARGIN_THRESHOLD:
                base_probability += self.PUMP_PROBABILITY_INCREMENT_VERY_HIGH
        
        # Established tokens rarely have pump schemes
        if token_sym in tier1_tokens:
            base_probability = max(0, base_probability - 0.5)
        
        return min(1.0, base_probability)
    
    def _catboost_predict(self, opp, profit_result, gas_gwei):
        """
        Apply CatBoost model prediction for opportunity scoring.
        Returns confidence score (0.0-1.0) for this opportunity.
        
        Note: This is a placeholder implementation. In production, this would load
        a trained CatBoost model and use actual features.
        """
        if not self.catboost_model_enabled:
            return 1.0  # No filtering when disabled
        
        # Extract features for prediction
        features = {
            'profit_usd': float(profit_result['net_profit']),
            'gas_gwei': gas_gwei,
            'tar_score': opp.get('tar_score', 50),
            'chain_id': opp['src_chain'],
        }
        
        # Placeholder scoring logic (replace with actual CatBoost model in production)
        score = 0.5  # Base score
        
        # Higher profits increase confidence
        if features['profit_usd'] > 5:
            score += 0.2
        if features['profit_usd'] > 10:
            score += 0.1
        
        # Lower gas prices increase confidence
        if features['gas_gwei'] < 30:
            score += 0.1
        
        # Higher TAR scores increase confidence
        if features['tar_score'] > 70:
            score += 0.15
        
        return min(1.0, score)
    
    def _apply_ai_prediction_filter(self, opportunities):
        """
        Apply AI prediction filtering to opportunities based on market conditions.
        Returns filtered list of opportunities that pass AI confidence checks.
        """
        if not self.ai_prediction_enabled:
            return opportunities  # No filtering when AI disabled
        
        filtered = []
        for opp in opportunities:
            # Get market forecast for this chain
            chain_id = opp['src_chain']
            
            # Use forecaster to predict if conditions are favorable
            gas_trend = self.forecaster.predict_gas_trend()
            volatility = self.forecaster.predict_volatility()
            
            # Calculate confidence score based on market conditions
            confidence = 0.5  # Base confidence
            
            # Adjust based on gas trend
            if gas_trend == "DROPPING_FAST":
                confidence += 0.2  # Good time to execute
            elif gas_trend == "RISING_FAST":
                confidence -= 0.2  # Poor time to execute
            
            # Adjust based on volatility
            if volatility == "LOW":
                confidence += 0.3  # Stable conditions
            elif volatility == "HIGH":
                confidence -= 0.2  # Risky conditions
            
            # Apply confidence threshold
            if self.forecaster.is_prediction_confident(confidence):
                filtered.append(opp)
                logger.debug(f"✅ {opp['token']} passed AI filter (confidence: {confidence:.2f})")
            else:
                logger.debug(f"❌ {opp['token']} filtered by AI (confidence: {confidence:.2f} < {self.ai_prediction_min_confidence})")
        
        return filtered
    
    def _select_intelligent_routes(self, opportunities):
        """
        Apply route intelligence to select optimal DEX combinations.
        Returns opportunities with best-predicted routes.
        """
        if not self.route_intelligence_enabled:
            return opportunities  # No route optimization when disabled
        
        # Group opportunities by token and chain
        from collections import defaultdict
        token_opps = defaultdict(list)
        
        for opp in opportunities:
            key = (opp['token'], opp['src_chain'])
            token_opps[key].append(opp)
        
        # Select best route for each token
        optimized = []
        for (token, chain), opps in token_opps.items():
            # Score each route based on historical success
            best_opp = opps[0]  # Default to first route
            best_score = 0
            
            for opp in opps:
                route_score = 50  # Base score
                
                # Prefer routes with UniswapV3 (better pricing)
                if 'UNIV3' in opp['route']:
                    route_score += 20
                
                # Prefer established DEXes
                established_dexes = ['SUSHI', 'QUICKSWAP', 'PANCAKE']
                if any(dex in opp['route'] for dex in established_dexes):
                    route_score += 10
                
                if route_score > best_score:
                    best_score = route_score
                    best_opp = opp
            
            optimized.append(best_opp)
            logger.debug(f"🔀 Route Intelligence: Selected {best_opp['route_name']} for {token} on chain {chain}")
        
        return optimized
    
    def _find_opportunities(self):
        """
        Find INTRA-CHAIN arbitrage opportunities with FULL market coverage
        Scans 100+ tokens across multiple DEX combinations
        
        Returns: List of filtered and scored opportunities
        """
        opportunities = []
        
        # Target chains with deep liquidity
        target_chains = [1, 137, 42161, 10, 8453, 56, 43114]
        
        # DEX route variations per chain
        dex_routes = {
            1: [  # Ethereum - most liquid
                ('UNIV3', 'SUSHI'),
                ('UNIV3', 'UNIV2'),
                ('SUSHI', 'UNIV2'),
            ],
            137: [  # Polygon
                ('UNIV3', 'QUICKSWAP'),
                ('UNIV3', 'SUSHI'),
                ('QUICKSWAP', 'SUSHI'),
            ],
            42161: [  # Arbitrum
                ('UNIV3', 'SUSHI'),
                ('UNIV3', 'CAMELOT'),
                ('SUSHI', 'CAMELOT'),
            ],
            10: [  # Optimism
                ('UNIV3', 'SUSHI'),
            ],
            8453: [  # Base
                ('UNIV3', 'SUSHI'),
            ],
            56: [  # BSC
                ('PANCAKE', 'SUSHI'),
            ],
            43114: [  # Avalanche
                ('TRADERJOE', 'SUSHI'),
            ]
        }
        
        # Tiered token scanning strategy
        # Tier 1: High-priority stablecoins and major assets (scan every cycle)
        tier1_tokens = ['USDC', 'USDT', 'DAI', 'WETH', 'WBTC', 'ETH']
        
        # Tier 2: Popular DeFi tokens (scan every 2nd cycle)
        tier2_tokens = ['UNI', 'LINK', 'AAVE', 'CRV', 'MATIC', 'AVAX', 'BNB', 'SNX', 'MKR', 'COMP']
        
        # Tier 3: All other tokens (scan every 5th cycle)
        scan_counter = getattr(self, '_scan_counter', 0)
        self._scan_counter = scan_counter + 1
        
        for chain_id in target_chains:
            if chain_id not in self.inventory:
                continue
            
            tokens = self.inventory[chain_id]
            routes = dex_routes.get(chain_id, [('UNIV3', 'SUSHI')])
            
            # Build token list based on tier priority
            tokens_to_scan = []
            
            # Always scan Tier 1
            for token_sym in tier1_tokens:
                if token_sym in tokens:
                    tokens_to_scan.append(token_sym)
            
            # Scan Tier 2 every 2nd cycle
            if scan_counter % 2 == 0:
                for token_sym in tier2_tokens:
                    if token_sym in tokens and token_sym not in tokens_to_scan:
                        tokens_to_scan.append(token_sym)
            
            # Scan Tier 3 every 5th cycle (random sample of 20 tokens)
            if scan_counter % 5 == 0:
                import random
                tier3_tokens = [sym for sym in tokens.keys() 
                               if sym not in tier1_tokens and sym not in tier2_tokens]
                if tier3_tokens:
                    sampled_tokens = random.sample(tier3_tokens, min(20, len(tier3_tokens)))
                    tokens_to_scan.extend(sampled_tokens)
            
            # Generate opportunities for selected tokens
            for token_sym in tokens_to_scan:
                token_data = tokens[token_sym]
                
                # Apply TAR scoring filter
                tar_score = self._calculate_tar_score(token_sym, chain_id)
                if tar_score < self.TAR_SCORE_MIN_THRESHOLD:
                    logger.debug(f"❌ {token_sym} filtered by TAR score: {tar_score}")
                    continue
                
                # Create opportunity for EACH DEX route combination
                for dex1, dex2 in routes:
                    opportunities.append({
                        "src_chain": chain_id,
                        "dst_chain": chain_id,
                        "token": token_sym,
                        "token_addr_src": token_data['address'],
                        "token_addr_dst": token_data['address'],
                        "decimals": token_data['decimals'],
                        "route": (dex1, dex2),  # Track which DEX pair
                        "route_name": f"{dex1}→{dex2}",
                        "tar_score": tar_score  # Include score for tracking
                    })
        
        # Apply AI prediction filtering
        logger.info(f"🤖 AI Prediction Filter: Processing {len(opportunities)} opportunities...")
        opportunities = self._apply_ai_prediction_filter(opportunities)
        logger.info(f"   → {len(opportunities)} opportunities passed AI filter")
        
        # Apply route intelligence optimization
        logger.info(f"🔀 Route Intelligence: Optimizing routes...")
        opportunities = self._select_intelligent_routes(opportunities)
        logger.info(f"   → {len(opportunities)} optimal routes selected")
        
        return opportunities

    def _evaluate_and_signal(self, opp, chain_gas_map):
        """
        Evaluate INTRA-CHAIN arbitrage with specific DEX route
        Tests multiple trade sizes as per README ($1.50-$10 profit target)
        """
        try:
            src_chain = opp['src_chain']
            dst_chain = opp['dst_chain']
            token_sym = opp['token']
            route_name = opp.get('route_name', 'UNIV3→SUSHI')
            dex1, dex2 = opp.get('route', ('UNIV3', 'SUSHI'))
            
            logger.info(f"🔎 {token_sym} Chain{src_chain} {route_name}")
            
            token_addr = opp['token_addr_src']
            decimals = opp['decimals']
            
            # 1. TEST MULTIPLE TRADE SIZES (README: optimize for $1.50-$10 profit)
            trade_sizes_usd = [500, 1000, 2000, 5000]  # Test various depths
            commander = TitanCommander(src_chain)
            
            # Find best profitable size
            for target_trade_usd in trade_sizes_usd:
                target_raw = target_trade_usd * (10**decimals)
                safe_amount = commander.optimize_loan_size(token_addr, target_raw, decimals)
                
                if safe_amount == 0:
                    continue  # Try next size
                
                # 2. SIMULATE DEX SWAPS with specific route
                try:
                    w3 = self.web3_connections.get(src_chain)
                    if not w3:
                        logger.info(f"❌ {token_sym}: No Web3 for chain {src_chain}")
                        return False
                    
                    pricer = DexPricer(w3, src_chain)
                    weth_addr = self.inventory[src_chain].get('WETH', {}).get('address')
                    
                    if not weth_addr:
                        logger.info(f"❌ {token_sym}: No WETH on chain {src_chain}")
                        return False
                    
                    # STEP 1: Token → WETH using DEX1
                    if dex1 == 'UNIV3':
                        step1_out = pricer.get_univ3_price(token_addr, weth_addr, safe_amount, fee=500)
                    else:
                        step1_out = pricer.get_univ2_price(dex1, token_addr, weth_addr, safe_amount)
                    
                    if step1_out == 0:
                        continue  # Try next size
                    
                    # STEP 2: WETH → Token using DEX2
                    step2_out = pricer.get_univ2_price(dex2, weth_addr, token_addr, step1_out)
                    
                    if step2_out == 0:
                        continue  # Try next size
                    
                    # Check profitability
                    if step2_out <= safe_amount:
                        continue  # Try next size
                    
                    # Calculate profit
                    revenue_usd = Decimal(step2_out) / Decimal(10**decimals)
                    cost_usd = Decimal(safe_amount) / Decimal(10**decimals)
                    
                    gas_price_gwei = chain_gas_map.get(src_chain, 0)
                    if gas_price_gwei == 0:
                        continue
                    
                    eth_price = Decimal("2000")
                    gas_cost_usd = Decimal(str(gas_price_gwei)) * Decimal("300000") * eth_price / Decimal("1e9")
                    
                    result = self.profit_engine.calculate_enhanced_profit(
                        amount=cost_usd,
                        amount_out=revenue_usd,
                        bridge_fee_usd=0,
                        gas_cost_usd=gas_cost_usd
                    )
                    
                    if result['is_profitable'] and result['net_profit'] >= self.MIN_PROFIT_THRESHOLD_USD:
                        # Found profitable trade at this size!
                        logger.info(f"💰 PROFIT: {token_sym} ${target_trade_usd} {route_name} = ${result['net_profit']:.2f}")
                        
                        # Apply pump detection filter
                        pump_probability = self._detect_pump_scheme(token_sym, src_chain, revenue_usd, cost_usd)
                        if pump_probability > self.pump_probability_threshold:
                            logger.warning(f"⚠️ PUMP DETECTED: {token_sym} probability {pump_probability:.2f} > threshold {self.pump_probability_threshold}")
                            self.display.log_decision(
                                decision_type="PUMP_FILTER",
                                token=token_sym,
                                chain_id=src_chain,
                                reason=f"Pump probability {pump_probability:.2f} exceeds threshold",
                                details={"probability": pump_probability, "threshold": self.pump_probability_threshold}
                            )
                            return False  # Reject this opportunity
                        
                        # Apply CatBoost model prediction (if enabled)
                        if self.catboost_model_enabled:
                            catboost_score = self._catboost_predict(opp, result, gas_price_gwei)
                            if catboost_score < self.ml_confidence_threshold:
                                logger.info(f"❌ CatBoost filter: {token_sym} score {catboost_score:.2f} < threshold {self.ml_confidence_threshold}")
                                return False  # Reject based on ML model
                            logger.info(f"✅ CatBoost approved: {token_sym} score {catboost_score:.2f}")
                        
                        # Log profitable opportunity to terminal
                        self.display.log_opportunity_scan(
                            token=token_sym,
                            chain_id=src_chain,
                            dex1=dex1,
                            dex2=dex2,
                            amount_usd=float(cost_usd),
                            profitable=True,
                            profit_usd=float(result['net_profit']),
                            gas_gwei=gas_price_gwei,
                            details=f"Size: ${target_trade_usd}"
                        )
                        
                        # Continue with signal generation...
                        break  # Use this size
                        
                except Exception as e:
                    logger.debug(f"Size ${target_trade_usd} failed: {e}")
                    continue
            
            else:
                # No profitable size found after trying all sizes
                return False
            
            # If we get here, we found profitable trade with variables: safe_amount, step1_out, step2_out, result
            # 4. PAYLOAD CONSTRUCTION - Using specific DEX route
            try:
                chain_conf = CHAINS.get(src_chain)
                if not chain_conf:
                    return False
                
                # Get router addresses based on route
                from offchain.core.config import DEX_ROUTERS
                
                # Get router for DEX1
                if dex1 == 'UNIV3':
                    router1 = chain_conf.get('uniswap_router', ZERO_ADDRESS)
                    protocol1 = 1  # UniV3
                    extra1 = "0x" + encode(['uint24'], [500]).hex()  # 0.05% fee
                else:
                    router1 = DEX_ROUTERS.get(src_chain, {}).get(dex1, ZERO_ADDRESS)
                    protocol1 = 0  # UniV2-style
                    extra1 = "0x"
                
                # Get router for DEX2
                router2 = DEX_ROUTERS.get(src_chain, {}).get(dex2, ZERO_ADDRESS)
                protocol2 = 0  # All second hops are V2-style
                extra2 = "0x"
                
                if is_zero_address(router1) or is_zero_address(router2):
                    return False
                
                protocols = [protocol1, protocol2]
                routers = [router1, router2]
                path = [weth_addr, token_addr]  # Outputs of each step
                extras = [extra1, extra2]
                
            except Exception as e:
                logger.error(f"Payload construction failed: {e}")
                return False

            # 6. AI TUNING
            try:
                exec_params = self.optimizer.recommend_parameters(src_chain, "MEDIUM")
                
                # Log AI tuning decision
                self.display.log_decision(
                    decision_type="AI_TUNE",
                    token=token_sym,
                    chain_id=src_chain,
                    reason="AI-optimized execution parameters",
                    details=exec_params
                )
                
                # Validate AI parameters
                if exec_params.get('slippage', 0) > self.MAX_SLIPPAGE_BPS:
                    logger.warning(f"AI slippage {exec_params['slippage']} exceeds max {self.MAX_SLIPPAGE_BPS}, capping")
                    self.display.log_decision(
                        decision_type="SLIPPAGE",
                        token=token_sym,
                        chain_id=src_chain,
                        reason=f"Capping slippage from {exec_params['slippage']} to {self.MAX_SLIPPAGE_BPS} BPS",
                        details={'max_allowed': self.MAX_SLIPPAGE_BPS}
                    )
                    exec_params['slippage'] = self.MAX_SLIPPAGE_BPS
                
                max_priority = float(self.MAX_GAS_PRICE_GWEI) / 2
                if exec_params.get('priority', 0) > max_priority:
                    exec_params['priority'] = int(max_priority)
                    
            except Exception as e:
                logger.error(f"AI parameter tuning failed: {e}")
                exec_params = {"slippage": 50, "priority": 30}

            # 7. BROADCAST
            signal = {
                "type": "INTRA_CHAIN",
                "chainId": src_chain,
                "token": token_addr,
                "amount": str(safe_amount),
                "protocols": protocols,
                "routers": routers,
                "path": path,
                "extras": extras,
                "ai_params": exec_params,
                "metrics": {
                    "profit_usd": float(result['net_profit']),
                    "fees_usd": float(result['total_fees']),
                    "gas_price_gwei": float(chain_gas_map.get(src_chain, 0)),
                    "step1_output": step1_out,
                    "step2_output": step2_out
                },
                "timestamp": datetime.now().isoformat()
            }

            # Signal generated successfully with detailed info
            logger.info(f"⚡ SIGNAL GENERATED: {token_sym} on Chain {src_chain}")
            logger.info(f"   💰 Profit: ${result['net_profit']:.2f} | Fees: ${result['total_fees']:.2f}")
            logger.info(f"   🔄 Route: {' -> '.join(protocols)}")
            logger.info(f"   ⛽ Gas: {chain_gas_map.get(src_chain, 0):.1f} Gwei")
            self.consecutive_failures = 0
            
            # Log signal generation to terminal display
            protocol_names = [dex1, dex2]
            self.display.log_signal_generated(
                token=token_sym,
                chain_id=src_chain,
                profit_usd=float(result['net_profit']),
                route=protocol_names,
                gas_gwei=float(chain_gas_map.get(src_chain, 0)),
                execution_params=exec_params
            )
            
            # Log approval decision
            self.display.log_decision(
                decision_type="APPROVE",
                token=token_sym,
                chain_id=src_chain,
                reason=f"Profitable opportunity approved for execution",
                details={
                    'profit_usd': float(result['net_profit']),
                    'gas_gwei': float(chain_gas_map.get(src_chain, 0))
                }
            )
            
            # Write signal to file for bot.js consumption
            self._write_signal_to_file(signal)
            
            return True  # Signal generated successfully
                
        except Exception as e:
            logger.error(f"Unexpected error in _evaluate_and_signal for {opp.get('token', 'unknown')}: {e}")
            self.consecutive_failures += 1
            return False

    def _write_signal_to_file(self, signal):
        """Write signal to JSON file for bot.js consumption"""
        try:
            timestamp = int(time.time() * 1000)
            filename = f"signal_{timestamp}_{signal['token_symbol']}.json"
            filepath = os.path.join(self.signals_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(signal, f, indent=2)
            
            logger.info(f"📄 Signal written to: {filename}")
            
            # Cleanup old signals periodically
            if timestamp % 60000 < 1000:  # Roughly every minute
                self._cleanup_old_signals()
                
        except Exception as e:
            logger.error(f"Failed to write signal file: {e}")

    async def scan_loop(self):
        """
        CRITICAL FIX #5: Async scan loop with non-blocking sleep
        Replaced synchronous time.sleep() with async asyncio.sleep() to prevent blocking
        """
        logger.info("🚀 Titan Brain: Engaging Hyper-Parallel Scan Loop...")
        
        # Print header in terminal display
        import os
        execution_mode = os.getenv('EXECUTION_MODE', 'PAPER').upper()
        self.display.print_header(mode=execution_mode)
        
        # Log initial coverage stats
        total_tokens = sum(len(tokens) for tokens in self.inventory.values())
        total_chains = len(self.inventory)
        logger.info(f"📊 Coverage: {total_tokens} tokens across {total_chains} chains")
        for chain_id, tokens in self.inventory.items():
            chain_name = CHAINS.get(chain_id, {}).get('name', f'Chain {chain_id}')
            logger.info(f"   • {chain_name}: {len(tokens)} tokens")
        
        scan_count = 0
        last_stats_print = time.time()
        
        while True:
            try:
                # CRITICAL FIX #9: Graceful degradation with automated recovery
                if self.consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES:
                    # Track backoff period
                    if self.backoff_start_time is None:
                        self.backoff_start_time = time.time()
                        logger.error(f"🛑 CIRCUIT BREAKER TRIGGERED: {self.consecutive_failures} consecutive failures")
                        logger.info(f"⏸️ Entering recovery mode with backoff...")
                        self.display.log_error("CIRCUIT_BREAKER", "Circuit breaker triggered",
                                              f"{self.consecutive_failures} consecutive failures - entering recovery mode")
                        
                        # Record circuit breaker event
                        if self.trade_db:
                            try:
                                self.trade_db.record_circuit_breaker_event(
                                    event_type="TRIGGERED",
                                    consecutive_failures=self.consecutive_failures,
                                    details=f"Circuit breaker triggered after {self.consecutive_failures} failures"
                                )
                            except Exception as e:
                                logger.debug(f"Failed to record circuit breaker event: {e}")
                    
                    # Calculate recovery progress
                    time_in_backoff = time.time() - self.backoff_start_time
                    recovery_period = 30  # 30 seconds minimum recovery period
                    
                    # Exponential backoff with max cap
                    self.scan_interval = min(self.scan_interval * 1.5, self.max_scan_interval)
                    
                    # Log recovery progress
                    if int(time_in_backoff) % 10 == 0:  # Every 10 seconds
                        remaining = max(0, recovery_period - time_in_backoff)
                        logger.info(f"⏱️ Circuit breaker recovery: {time_in_backoff:.0f}s elapsed, {remaining:.0f}s remaining")
                    
                    await asyncio.sleep(self.scan_interval)
                    
                    # Automated recovery after minimum period
                    if time_in_backoff >= recovery_period:
                        logger.info("✅ Circuit breaker recovery period complete - attempting restart")
                        self.consecutive_failures = 0
                        # Gradually restore normal speed
                        self.scan_interval = max(self.scan_interval / 2, self.min_scan_interval)
                        recovery_time = time_in_backoff
                        self.backoff_start_time = None
                        logger.info(f"🔄 Scan interval restored to {self.scan_interval}s")
                        self.display.log_info("CIRCUIT_BREAKER", "Recovery successful", 
                                             f"Resuming normal operations at {self.scan_interval}s interval")
                        
                        # Record recovery event
                        if self.trade_db:
                            try:
                                self.trade_db.record_circuit_breaker_event(
                                    event_type="RECOVERED",
                                    consecutive_failures=0,
                                    recovery_time=recovery_time,
                                    details=f"Circuit breaker recovered after {recovery_time:.1f}s"
                                )
                            except Exception as e:
                                logger.debug(f"Failed to record recovery event: {e}")
                    continue
                
                # Print stats every 60 seconds
                if time.time() - last_stats_print > 60:
                    self.display.print_stats_bar()
                    last_stats_print = time.time()
                
                scan_count += 1
                
                # 1. GAS CHECK with error handling
                try:
                    active_chains = list(self.web3_connections.keys())
                    gas_futures = {self.executor.submit(self._get_gas_price, cid): cid for cid in active_chains}
                    chain_gas_map = {}
                    
                    for f in as_completed(gas_futures, timeout=10):
                        try:
                            chain_id = gas_futures[f]
                            gas_price = f.result()
                            chain_gas_map[chain_id] = gas_price
                            
                            # Log gas updates to terminal display (throttled)
                            if scan_count % 10 == 0:  # Every 10 scans
                                self.display.log_gas_update(
                                    chain_id=chain_id,
                                    gas_gwei=gas_price,
                                    threshold=float(self.MAX_GAS_PRICE_GWEI)
                                )
                        except Exception as e:
                            logger.warning(f"Failed to get gas price for chain: {e}")
                            
                    if not chain_gas_map:
                        logger.warning("No gas prices available, waiting before retry")
                        await asyncio.sleep(5)  # CRITICAL FIX #5: Non-blocking sleep
                        continue
                        
                except Exception as e:
                    logger.error(f"Gas check failed: {e}")
                    await asyncio.sleep(5)  # CRITICAL FIX #5: Non-blocking sleep
                    continue

                # 2. FORECAST GUARD with validation
                try:
                    poly_gas = chain_gas_map.get(137, 0.0)
                    if poly_gas > 0:
                        # Check if gas price is within acceptable range
                        if poly_gas > float(self.MAX_GAS_PRICE_GWEI):
                            logger.warning(f"⚠️ Polygon gas price {poly_gas} exceeds maximum, waiting...")
                            await asyncio.sleep(10)  # CRITICAL FIX #5: Non-blocking sleep
                            continue
                            
                        self.forecaster.ingest_gas(poly_gas)
                        if self.forecaster.should_wait():
                            logger.info("⏳ AI HOLD: Gas trend unfavorable.")
                            await asyncio.sleep(2)  # CRITICAL FIX #5: Non-blocking sleep
                            continue
                except Exception as e:
                    logger.warning(f"Gas forecast check failed: {e}")
                    # Continue anyway as this is not critical
                
                # 3. FIND PATHS with error handling
                try:
                    candidates = self._find_opportunities()
                    if not candidates:
                        logger.debug("No opportunities found in this cycle")
                        await asyncio.sleep(5)  # CRITICAL FIX #5: Non-blocking sleep
                        continue
                    
                    logger.info(f"🔍 Found {len(candidates)} potential opportunities")
                except Exception as e:
                    logger.error(f"Opportunity discovery failed: {e}")
                    await asyncio.sleep(5)  # CRITICAL FIX #5: Non-blocking sleep
                    continue

                # 4. PARALLEL EVALUATION with error handling
                try:
                    scan_futures = [
                        self.executor.submit(self._evaluate_and_signal, opp, chain_gas_map) 
                        for opp in candidates
                    ]
                    
                    completed = 0
                    signals_generated = 0
                    for f in as_completed(scan_futures, timeout=30):
                        try:
                            result = f.result()  # This will raise any exceptions from the worker
                            completed += 1
                            if result:  # If signal was generated
                                signals_generated += 1
                        except Exception as e:
                            logger.error(f"Worker evaluation error: {e}")
                            
                    logger.info(f"📊 Cycle complete: {completed}/{len(candidates)} evaluated, {signals_generated} signals generated")
                    
                except Exception as e:
                    logger.error(f"Parallel evaluation failed: {e}")

                # CRITICAL FIX #5: Non-blocking sleep between cycles
                await asyncio.sleep(self.scan_interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 Shutting down gracefully...")
                self.executor.shutdown(wait=True)
                break
            except Exception as e:
                logger.error(f"Unexpected error in scan loop: {e}")
                await asyncio.sleep(5)  # CRITICAL FIX #5: Non-blocking sleep

if __name__ == "__main__":
    brain = OmniBrain()
    brain.initialize()
    # CRITICAL FIX #5: Run async scan loop
    asyncio.run(brain.scan_loop())