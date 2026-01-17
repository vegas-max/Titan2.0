"""
APEX-OMEGA TITAN: SYSTEM WIRING & INTEGRATION MANAGER
======================================================

This module manages the complete wiring and integration of all Titan components
for mainnet operations. It ensures:

1. All components are properly initialized
2. Communication channels are established
3. Data flows correctly between components
4. Failsafe mechanisms are in place
5. Monitoring and logging are configured

SYSTEM ARCHITECTURE:
===================

┌─────────────────────────────────────────────────────────────────────┐
│                     APEX-OMEGA TITAN MAINNET SYSTEM                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ LAYER 1: DATA INGESTION (Python)                              │ │
│  ├───────────────────────────────────────────────────────────────┤ │
│  │  • OmniBrain (offchain/ml/brain.py)                           │ │
│  │    - Multi-chain RPC connections                              │ │
│  │    - Real-time price data                                     │ │
│  │    - Gas price monitoring                                     │ │
│  │    - Liquidity discovery                                      │ │
│  │    - Token inventory (100+ per chain)                         │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                              ↓                                        │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ LAYER 2: ARBITRAGE CALCULATION (Python)                       │ │
│  ├───────────────────────────────────────────────────────────────┤ │
│  │  • ProfitEngine (offchain/ml/brain.py)                        │ │
│  │    - Master profit equation                                   │ │
│  │    - Multi-hop route optimization                             │ │
│  │    - Cross-chain bridge integration                           │ │
│  │  • TitanCommander (offchain/core/titan_commander_core.py)     │ │
│  │    - Loan size optimization                                   │ │
│  │    - TVL safety checks                                        │ │
│  │    - Slippage simulation                                      │ │
│  │  • DexPricer (offchain/ml/dex_pricer.py)                      │ │
│  │    - Real-time price quotes                                   │ │
│  │    - Route discovery                                          │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                              ↓                                        │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ LAYER 3: SIGNAL GENERATION (File-based IPC)                   │ │
│  ├───────────────────────────────────────────────────────────────┤ │
│  │  • signals/outgoing/ (JSON files)                             │ │
│  │    - Arbitrage opportunities                                  │ │
│  │    - Execution parameters                                     │ │
│  │    - Risk metadata                                            │ │
│  │  • signals/processed/ (Archive)                               │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                              ↓                                        │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ LAYER 4: EXECUTION ENGINE (JavaScript)                        │ │
│  ├───────────────────────────────────────────────────────────────┤ │
│  │  • TitanBot (offchain/execution/bot.js)                       │ │
│  │    - Signal file monitoring                                   │ │
│  │    - Execution mode routing (PAPER/LIVE)                      │ │
│  │  • GasManager (offchain/execution/gas_manager.js)             │ │
│  │    - EIP-1559 optimization                                    │ │
│  │  • AggregatorSelector (offchain/execution/aggregator_selector.js) │ │
│  │    - Multi-aggregator routing                                 │ │
│  │  • LifiManager (offchain/execution/lifi_manager.js)           │ │
│  │    - Cross-chain execution                                    │ │
│  │  • BloxRouteManager (offchain/execution/bloxroute_manager.js) │ │
│  │    - MEV protection                                           │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                              ↓                                        │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ LAYER 5: ML TRAINING (Python)                                 │ │
│  ├───────────────────────────────────────────────────────────────┤ │
│  │  • MarketForecaster (ml/cortex/forecaster.py)                 │ │
│  │    - Gas price prediction                                     │ │
│  │    - Volatility forecasting                                   │ │
│  │  • QLearningAgent (ml/cortex/rl_optimizer.py)                 │ │
│  │    - Strategy optimization                                    │ │
│  │    - Risk parameter tuning                                    │ │
│  │  • FeatureStore (ml/cortex/feature_store.py)                  │ │
│  │    - Historical data storage                                  │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

DATA FLOW:
=========

1. OmniBrain scans multiple chains for arbitrage opportunities
2. ProfitEngine calculates net profit for each opportunity
3. TitanCommander optimizes loan sizes and validates safety
4. Signal files are written to signals/outgoing/ with execution params
5. TitanBot monitors signal directory and picks up new files
6. AggregatorSelector routes execution to optimal DEX aggregator
7. GasManager optimizes transaction fees
8. Execution happens (PAPER = simulated, LIVE = real blockchain)
9. Results feed back to ML training loop
10. MarketForecaster/QLearning update models based on outcomes

COMMUNICATION:
=============

Python ←→ JavaScript: File-based (JSON signals)
  - Advantage: No Redis dependency, simple, reliable
  - signals/outgoing/: Pending execution
  - signals/processed/: Completed trades

SAFETY MECHANISMS:
=================

1. Circuit Breakers: Stop after N consecutive failures
2. Gas Price Limits: Max gas price ceiling per chain
3. TVL Caps: Max % of pool liquidity to borrow
4. Slippage Limits: Max acceptable slippage per trade
5. Profit Thresholds: Min profit required to execute
6. Rate Limiting: Max trades per minute/hour
7. Wallet Balance Checks: Ensure sufficient gas funds (LIVE mode)

"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("SystemWiring")

class SystemIntegrationManager:
    """
    Manages the complete integration and wiring of all Titan components.
    Ensures proper initialization, communication, and monitoring.
    """
    
    def __init__(self):
        self.mode = os.getenv('EXECUTION_MODE', 'PAPER').upper()
        self.config = self._load_configuration()
        self.config_file = Path('config.json')
        self.status = {
            'initialized': False,
            'components': {},
            'communication_channels': {},
            'monitoring_enabled': False
        }
    
    def _load_configuration(self) -> Dict:
        """Load system configuration from environment"""
        return {
            'execution_mode': self.mode,
            'chains_enabled': self._get_enabled_chains(),
            'features': {
                'cross_chain': os.getenv('ENABLE_CROSS_CHAIN', 'false').lower() == 'true',
                'mev_protection': os.getenv('ENABLE_MEV_PROTECTION', 'false').lower() == 'true',
                'ml_training': os.getenv('ENABLE_REALTIME_TRAINING', 'true').lower() == 'true',
            },
            'limits': {
                'max_gas_gwei': float(os.getenv('MAX_BASE_FEE_GWEI', '500')),
                'min_profit_usd': float(os.getenv('MIN_PROFIT_USD', '1.0')),
                'max_slippage_bps': int(os.getenv('MAX_SLIPPAGE_BPS', '100')),
            },
            'directories': {
                'signals_outgoing': Path('signals/outgoing'),
                'signals_processed': Path('signals/processed'),
                'logs': Path('logs'),
            }
        }
    
    def _get_enabled_chains(self) -> List[int]:
        """Get list of enabled chain IDs based on RPC configuration"""
        enabled = []
        chain_map = {
            1: 'RPC_ETHEREUM',
            137: 'RPC_POLYGON',
            42161: 'RPC_ARBITRUM',
            10: 'RPC_OPTIMISM',
            8453: 'RPC_BASE',
            56: 'RPC_BSC',
            43114: 'RPC_AVALANCHE',
            250: 'RPC_FANTOM',
        }
        
        for chain_id, env_var in chain_map.items():
            rpc = os.getenv(env_var)
            if rpc and 'YOUR_' not in rpc.upper():
                enabled.append(chain_id)
        
        return enabled
    
    def validate_environment(self):
        """
        Validate environment configuration.
        Returns: (is_valid, list_of_warnings)
        """
        warnings = []
        
        # Check execution mode
        if self.mode not in ['PAPER', 'LIVE']:
            warnings.append(f"Invalid EXECUTION_MODE: {self.mode} (must be PAPER or LIVE)")
        
        # Check RPC endpoints
        if not self.config['chains_enabled']:
            warnings.append("No RPC endpoints configured! Check .env file")
        
        # Check wallet config (only for LIVE mode)
        if self.mode == 'LIVE':
            private_key = os.getenv('PRIVATE_KEY')
            executor_addr = os.getenv('EXECUTOR_ADDRESS')
            
            if not private_key or 'YOUR_' in private_key.upper():
                warnings.append("PRIVATE_KEY not configured (required for LIVE mode)")
            
            if not executor_addr or 'YOUR_' in executor_addr.upper():
                warnings.append("EXECUTOR_ADDRESS not configured (required for LIVE mode)")
        
        # Check directories
        for name, path in self.config['directories'].items():
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                warnings.append(f"Created missing directory: {path}")
        
        is_valid = len([w for w in warnings if 'not configured' in w.lower()]) == 0
        return is_valid, warnings
    
    def initialize_components(self) -> Dict[str, bool]:
        """
        Initialize all system components.
        Returns: Status of each component initialization
        """
        logger.info("🔧 Initializing system components...")
        
        component_status = {}
        
        # 1. Check Python Brain
        try:
            from offchain.ml.brain import OmniBrain
            component_status['OmniBrain'] = True
            logger.info("   ✅ OmniBrain module loaded")
        except ImportError as e:
            component_status['OmniBrain'] = False
            logger.error(f"   ❌ OmniBrain import failed: {e}")
        
        # 2. Check ML Cortex
        try:
            from offchain.ml.cortex.forecaster import MarketForecaster
            from offchain.ml.cortex.rl_optimizer import QLearningAgent
            component_status['ML_Cortex'] = True
            logger.info("   ✅ ML Cortex loaded")
        except ImportError as e:
            component_status['ML_Cortex'] = False
            logger.warning(f"   ⚠️  ML Cortex import warning: {e}")
        
        # 3. Check Titan Commander
        try:
            from offchain.core.titan_commander_core import TitanCommander
            component_status['TitanCommander'] = True
            logger.info("   ✅ TitanCommander loaded")
        except ImportError as e:
            component_status['TitanCommander'] = False
            logger.error(f"   ❌ TitanCommander import failed: {e}")
        
        # 4. Check JavaScript Bot
        bot_path = Path('offchain/execution/bot.js')
        component_status['TitanBot'] = bot_path.exists()
        if component_status['TitanBot']:
            logger.info("   ✅ TitanBot found")
        else:
            logger.error("   ❌ TitanBot not found")
        
        # 5. Check Execution Managers
        execution_modules = [
            'gas_manager.js',
            'aggregator_selector.js',
            'lifi_manager.js',
        ]
        all_present = all((Path('offchain/execution') / mod).exists() for mod in execution_modules)
        component_status['ExecutionManagers'] = all_present
        if all_present:
            logger.info("   ✅ Execution managers found")
        else:
            logger.warning("   ⚠️  Some execution managers missing")
        
        self.status['components'] = component_status
        return component_status
    
    def setup_communication_channels(self) -> bool:
        """
        Set up communication channels between components.
        Returns: True if successful
        """
        logger.info("📡 Setting up communication channels...")
        
        try:
            # Create signal directories
            for name, path in self.config['directories'].items():
                if 'signal' in name:
                    path.mkdir(parents=True, exist_ok=True)
            
            # Verify read/write access
            test_signal = self.config['directories']['signals_outgoing'] / 'test.json'
            test_signal.write_text(json.dumps({'test': True}))
            test_signal.unlink()
            
            logger.info("   ✅ Signal file communication channels ready")
            self.status['communication_channels']['signals'] = True
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Communication channel setup failed: {e}")
            self.status['communication_channels']['signals'] = False
            return False
    
    def print_system_status(self):
        """Print comprehensive system status"""
        print("\n" + "="*70)
        print("  🚀 APEX-OMEGA TITAN: SYSTEM STATUS")
        print("="*70)
        print(f"  Execution Mode: {self.mode}")
        print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check ready state from config.json
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                ready_state = config_data.get('system_status', {}).get('ready_for_benchmarking_and_live_trading', False)
                ready_icon = "✅" if ready_state else "❌"
                print(f"  Ready for Benchmarking & Live Trading: {ready_icon} {ready_state}")
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"  Ready for Benchmarking & Live Trading: ⚠️  Unknown (Error: {e})")
        
        print("")
        
        print("  🔧 COMPONENT STATUS")
        print("  " + "-"*66)
        for component, status in self.status['components'].items():
            icon = "✅" if status else "❌"
            print(f"  {icon} {component}")
        print("")
        
        print("  🌐 ENABLED CHAINS")
        print("  " + "-"*66)
        chain_names = {
            1: 'Ethereum', 137: 'Polygon', 42161: 'Arbitrum',
            10: 'Optimism', 8453: 'Base', 56: 'BSC',
            43114: 'Avalanche', 250: 'Fantom'
        }
        for chain_id in self.config['chains_enabled']:
            print(f"  ✅ {chain_names.get(chain_id, f'Chain {chain_id}')}")
        print("")
        
        print("  🎯 FEATURES")
        print("  " + "-"*66)
        for feature, enabled in self.config['features'].items():
            icon = "✅" if enabled else "⚪"
            print(f"  {icon} {feature.replace('_', ' ').title()}")
        print("")
        
        print("  🛡️  SAFETY LIMITS")
        print("  " + "-"*66)
        print(f"  Max Gas Price: {self.config['limits']['max_gas_gwei']} gwei")
        print(f"  Min Profit: ${self.config['limits']['min_profit_usd']}")
        print(f"  Max Slippage: {self.config['limits']['max_slippage_bps']/100}%")
        print("")
        
        print("="*70)
        print("")
    
    def run_diagnostics(self) -> bool:
        """
        Run complete system diagnostics.
        Returns: True if system is ready for operation
        """
        logger.info("🔍 Running system diagnostics...\n")
        
        # 1. Validate environment
        is_valid, warnings = self.validate_environment()
        if warnings:
            logger.warning("Environment validation warnings:")
            for warning in warnings:
                logger.warning(f"  ⚠️  {warning}")
        
        # 2. Initialize components
        self.initialize_components()
        
        # 3. Setup communication
        comm_ok = self.setup_communication_channels()
        
        # 4. Print status
        self.print_system_status()
        
        # 5. Determine if system is ready
        critical_components = ['OmniBrain', 'TitanCommander', 'TitanBot']
        all_critical_ok = all(
            self.status['components'].get(comp, False) 
            for comp in critical_components
        )
        
        system_ready = is_valid and all_critical_ok and comm_ok
        
        if system_ready:
            logger.info("✅ System diagnostics PASSED - Ready for operation")
        else:
            logger.error("❌ System diagnostics FAILED - Check errors above")
        
        return system_ready

def main():
    """Run system diagnostics"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    manager = SystemIntegrationManager()
    
    # Run diagnostics
    ready = manager.run_diagnostics()
    
    # Exit with appropriate code
    sys.exit(0 if ready else 1)

if __name__ == "__main__":
    main()
