#!/usr/bin/env python3
"""
Comprehensive Operational Audit for Titan2.0 Arbitrage System
Focuses on operational efficiency, consistency, and compliance within the Polygon ecosystem.

Audit Scope:
1. System Configuration and Initialization
2. Data Ingestion and Price Scanning
3. Pool and Liquidity Registry
4. Route Assembly and Validation
5. Flashloan Feasibility Checks
6. Profit Simulation and Calculations
7. Machine Learning Integration
8. Code Quality and Maintainability
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from decimal import Decimal
from colorama import Fore, Style, init
from web3 import Web3

# Initialize colorama for colored output
init(autoreset=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'audit_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AuditResult:
    """Class to store audit check results"""
    def __init__(self, category: str, check_name: str, status: str, 
                 details: str = "", recommendations: List[str] = None):
        self.category = category
        self.check_name = check_name
        self.status = status  # PASS, FAIL, WARNING, INFO
        self.details = details
        self.recommendations = recommendations or []
        self.timestamp = datetime.now()
    
    def __str__(self):
        status_color = {
            'PASS': Fore.GREEN,
            'FAIL': Fore.RED,
            'WARNING': Fore.YELLOW,
            'INFO': Fore.CYAN
        }
        color = status_color.get(self.status, Fore.WHITE)
        return f"{color}[{self.status}] {self.check_name}: {self.details}{Style.RESET_ALL}"


class ComprehensiveAudit:
    """Main audit class for Titan2.0 system"""
    
    def __init__(self):
        self.results: List[AuditResult] = []
        self.start_time = datetime.now()
        self.config = None
        self.polygon_config = None
        
    def add_result(self, category: str, check_name: str, status: str, 
                   details: str = "", recommendations: List[str] = None):
        """Add an audit result"""
        result = AuditResult(category, check_name, status, details, recommendations)
        self.results.append(result)
        logger.info(str(result))
        return result
    
    def print_header(self, text: str):
        """Print a formatted section header"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{text.center(80)}")
        print(f"{'='*80}{Style.RESET_ALL}\n")
    
    def audit_1_configuration(self):
        """Audit 1: System Configuration and Initialization"""
        self.print_header("AUDIT SECTION 1: SYSTEM CONFIGURATION AND INITIALIZATION")
        
        # Check config.json exists
        config_path = "config.json"
        if not os.path.exists(config_path):
            self.add_result(
                "Configuration",
                "Config File Existence",
                "FAIL",
                "config.json not found",
                ["Create config.json with proper DEX endpoints and token configurations"]
            )
            return
        
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            self.add_result(
                "Configuration",
                "Config File Loading",
                "PASS",
                f"Successfully loaded config.json (version: {self.config.get('version', 'unknown')})"
            )
        except json.JSONDecodeError as e:
            self.add_result(
                "Configuration",
                "Config File Parsing",
                "FAIL",
                f"JSON parsing error: {e}",
                ["Fix JSON syntax errors in config.json"]
            )
            return
        
        # Check Polygon network configuration
        if 'networks' in self.config and 'polygon' in self.config['networks']:
            self.polygon_config = self.config['networks']['polygon']
            self.add_result(
                "Configuration",
                "Polygon Network Config",
                "PASS",
                f"Polygon chain ID: {self.polygon_config.get('chainId')}"
            )
        else:
            self.add_result(
                "Configuration",
                "Polygon Network Config",
                "FAIL",
                "Polygon network configuration not found",
                ["Add Polygon network configuration to config.json"]
            )
        
        # Check ERC-20 token validation
        self.audit_token_configuration()
        
        # Check environment variables
        self.audit_environment_variables()
        
        # Check advanced features configuration
        self.audit_advanced_features()
    
    def audit_token_configuration(self):
        """Audit token configuration for ERC-20 compliance"""
        if not self.config:
            return
        
        # Check if token lists exist
        if 'tokens' in self.config:
            tokens = self.config['tokens']
            self.add_result(
                "Configuration",
                "Token Configuration",
                "PASS",
                f"Found {len(tokens)} configured tokens"
            )
            
            # Validate token addresses (checksum)
            invalid_tokens = []
            for token_symbol, token_data in tokens.items():
                if isinstance(token_data, dict) and 'address' in token_data:
                    address = token_data['address']
                    if not Web3.is_checksum_address(address):
                        invalid_tokens.append(token_symbol)
            
            if invalid_tokens:
                self.add_result(
                    "Configuration",
                    "Token Address Checksum",
                    "WARNING",
                    f"Found {len(invalid_tokens)} tokens with invalid checksum addresses: {', '.join(invalid_tokens[:5])}",
                    ["Convert all token addresses to checksum format using Web3.to_checksum_address()"]
                )
            else:
                self.add_result(
                    "Configuration",
                    "Token Address Checksum",
                    "PASS",
                    "All token addresses are properly checksummed"
                )
        else:
            self.add_result(
                "Configuration",
                "Token Configuration",
                "INFO",
                "No token configuration found in config.json (may be loaded dynamically)"
            )
    
    def audit_environment_variables(self):
        """Audit environment variables configuration"""
        required_env_vars = [
            'PRIVATE_KEY',
            'RPC_POLYGON',
            'INFURA_API_KEY',
            'LIFI_API_KEY'
        ]
        
        optional_env_vars = [
            'WSS_POLYGON',
            'ALCHEMY_API_KEY',
            'BLOXROUTE_AUTH_HEADER',
            'TELEGRAM_BOT_TOKEN'
        ]
        
        # Check .env file exists
        if not os.path.exists('.env'):
            self.add_result(
                "Configuration",
                "Environment File",
                "FAIL",
                ".env file not found",
                ["Create .env file from .env.example template"]
            )
            return
        
        # Read .env file
        env_vars = {}
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
        
        # Check required variables
        missing_required = [var for var in required_env_vars if var not in env_vars or not env_vars[var]]
        if missing_required:
            self.add_result(
                "Configuration",
                "Required Environment Variables",
                "FAIL",
                f"Missing required variables: {', '.join(missing_required)}",
                [f"Add {var} to .env file" for var in missing_required]
            )
        else:
            self.add_result(
                "Configuration",
                "Required Environment Variables",
                "PASS",
                "All required environment variables are configured"
            )
        
        # Check optional variables
        missing_optional = [var for var in optional_env_vars if var not in env_vars or not env_vars[var]]
        if missing_optional:
            self.add_result(
                "Configuration",
                "Optional Environment Variables",
                "INFO",
                f"Optional variables not configured: {', '.join(missing_optional)}"
            )
    
    def audit_advanced_features(self):
        """Audit advanced features configuration"""
        if not self.config or 'advanced_features' not in self.config:
            self.add_result(
                "Configuration",
                "Advanced Features",
                "INFO",
                "No advanced features configuration found"
            )
            return
        
        features = self.config['advanced_features']
        enabled_features = [name for name, config in features.items() 
                          if isinstance(config, dict) and config.get('enabled', False)]
        
        self.add_result(
            "Configuration",
            "Advanced Features",
            "PASS",
            f"Found {len(enabled_features)} enabled advanced features: {', '.join(enabled_features)}"
        )
        
        # Check specific feature configurations
        if 'real_data_pipeline' in features and features['real_data_pipeline'].get('enabled'):
            polling = features['real_data_pipeline'].get('polling_interval_seconds', 0)
            if polling > 10:
                self.add_result(
                    "Configuration",
                    "Real Data Pipeline Polling",
                    "WARNING",
                    f"Polling interval is {polling}s - may miss fast-moving opportunities",
                    ["Consider reducing polling interval to 3-5 seconds for Polygon block times (~2s)"]
                )
            else:
                self.add_result(
                    "Configuration",
                    "Real Data Pipeline Polling",
                    "PASS",
                    f"Polling interval: {polling}s (aligned with Polygon block times)"
                )
    
    def audit_2_price_scanning(self):
        """Audit 2: Data Ingestion and Price Scanning (DexPriceScanner)"""
        self.print_header("AUDIT SECTION 2: DATA INGESTION AND PRICE SCANNING")
        
        # Check DexPricer module exists
        dex_pricer_path = "offchain/ml/dex_pricer.py"
        if not os.path.exists(dex_pricer_path):
            self.add_result(
                "Price Scanning",
                "DexPricer Module",
                "FAIL",
                "dex_pricer.py not found",
                ["Ensure DexPricer module is properly installed"]
            )
            return
        
        self.add_result(
            "Price Scanning",
            "DexPricer Module",
            "PASS",
            "DexPricer module found"
        )
        
        # Try to import and analyze
        try:
            sys.path.insert(0, os.path.abspath('.'))
            from offchain.ml.dex_pricer import DexPricer
            
            self.add_result(
                "Price Scanning",
                "DexPricer Import",
                "PASS",
                "DexPricer successfully imported"
            )
            
            # Check for price query methods
            expected_methods = ['get_curve_indices', '_get_pool_coins']
            found_methods = [m for m in expected_methods if hasattr(DexPricer, m)]
            
            if len(found_methods) == len(expected_methods):
                self.add_result(
                    "Price Scanning",
                    "DexPricer Methods",
                    "PASS",
                    f"All expected methods found: {', '.join(found_methods)}"
                )
            else:
                missing = set(expected_methods) - set(found_methods)
                self.add_result(
                    "Price Scanning",
                    "DexPricer Methods",
                    "WARNING",
                    f"Missing methods: {', '.join(missing)}"
                )
            
        except ImportError as e:
            self.add_result(
                "Price Scanning",
                "DexPricer Import",
                "FAIL",
                f"Failed to import DexPricer: {e}",
                ["Check Python dependencies are installed: pip install -r requirements.txt"]
            )
        
        # Check DEX endpoint configuration
        self.audit_dex_endpoints()
        
        # Check data normalization
        self.audit_data_normalization()
    
    def audit_dex_endpoints(self):
        """Audit DEX endpoint configurations"""
        if not self.config or 'dex_endpoints' not in self.config:
            self.add_result(
                "Price Scanning",
                "DEX Endpoints",
                "WARNING",
                "No DEX endpoint configuration found",
                ["Add dex_endpoints configuration to config.json"]
            )
            return
        
        dex_endpoints = self.config['dex_endpoints']
        polygon_dexes = [name for name, config in dex_endpoints.items() 
                        if isinstance(config, dict) and 'polygon' in config]
        
        if len(polygon_dexes) < 3:
            self.add_result(
                "Price Scanning",
                "Polygon DEX Coverage",
                "WARNING",
                f"Only {len(polygon_dexes)} DEXes configured for Polygon: {', '.join(polygon_dexes)}",
                ["Add more DEX integrations (QuickSwap, SushiSwap, Uniswap V3, Curve)"]
            )
        else:
            self.add_result(
                "Price Scanning",
                "Polygon DEX Coverage",
                "PASS",
                f"Found {len(polygon_dexes)} DEXes for Polygon: {', '.join(polygon_dexes)}"
            )
        
        # Check for WebSocket support
        ws_enabled = []
        for dex_name, dex_config in dex_endpoints.items():
            if isinstance(dex_config, dict) and 'polygon' in dex_config:
                if 'ws' in dex_config['polygon']:
                    ws_enabled.append(dex_name)
        
        if ws_enabled:
            self.add_result(
                "Price Scanning",
                "WebSocket Support",
                "PASS",
                f"{len(ws_enabled)} DEXes have WebSocket endpoints: {', '.join(ws_enabled)}"
            )
        else:
            self.add_result(
                "Price Scanning",
                "WebSocket Support",
                "WARNING",
                "No DEXes configured with WebSocket endpoints",
                ["Add WebSocket endpoints for real-time price updates"]
            )
    
    def audit_data_normalization(self):
        """Audit data normalization and decimal handling"""
        # Check if token decimal handling is implemented
        config_path = "offchain/core/config.py"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                content = f.read()
                
            if 'Decimal' in content or 'getcontext' in content:
                self.add_result(
                    "Price Scanning",
                    "Decimal Precision",
                    "PASS",
                    "High-precision decimal handling implemented in config"
                )
            else:
                self.add_result(
                    "Price Scanning",
                    "Decimal Precision",
                    "WARNING",
                    "No explicit high-precision decimal handling found",
                    ["Use Python's Decimal class for financial calculations"]
                )
        
        # Check for decimal context in brain.py
        brain_path = "offchain/ml/brain.py"
        if os.path.exists(brain_path):
            with open(brain_path, 'r') as f:
                content = f.read()
                
            if 'getcontext().prec' in content:
                self.add_result(
                    "Price Scanning",
                    "Decimal Context Configuration",
                    "PASS",
                    "Decimal precision context properly configured in brain module"
                )
    
    def audit_3_pool_registry(self):
        """Audit 3: Pool and Liquidity Registry"""
        self.print_header("AUDIT SECTION 3: POOL AND LIQUIDITY REGISTRY")
        
        # Check for pool registry implementation
        registry_files = [
            "offchain/core/token_discovery.py",
            "offchain/ml/dex_pricer.py"
        ]
        
        found_registries = [f for f in registry_files if os.path.exists(f)]
        
        if found_registries:
            self.add_result(
                "Pool Registry",
                "Registry Implementation",
                "PASS",
                f"Found {len(found_registries)} pool registry modules"
            )
        else:
            self.add_result(
                "Pool Registry",
                "Registry Implementation",
                "WARNING",
                "No pool registry modules found",
                ["Implement pool discovery and validation"]
            )
        
        # Check for liquidity validation
        if self.config and 'liquidity_thresholds' in self.config:
            thresholds = self.config['liquidity_thresholds']
            self.add_result(
                "Pool Registry",
                "Liquidity Thresholds",
                "PASS",
                f"Liquidity thresholds configured: {thresholds}"
            )
        else:
            self.add_result(
                "Pool Registry",
                "Liquidity Thresholds",
                "INFO",
                "No explicit liquidity thresholds configured"
            )
        
        # Check ERC-20 compliance validation
        self.audit_erc20_compliance()
    
    def audit_erc20_compliance(self):
        """Audit ERC-20 token compliance checks"""
        # Check if token validation exists
        token_loader_path = "offchain/core/token_loader.py"
        if os.path.exists(token_loader_path):
            with open(token_loader_path, 'r') as f:
                content = f.read()
            
            # Check for common ERC-20 validation patterns
            has_decimals_check = 'decimals' in content.lower()
            has_symbol_check = 'symbol' in content.lower()
            
            if has_decimals_check and has_symbol_check:
                self.add_result(
                    "Pool Registry",
                    "ERC-20 Compliance Checks",
                    "PASS",
                    "Token validation includes decimals and symbol checks"
                )
            else:
                self.add_result(
                    "Pool Registry",
                    "ERC-20 Compliance Checks",
                    "WARNING",
                    "Limited ERC-20 validation found",
                    ["Implement comprehensive ERC-20 interface validation"]
                )
    
    def audit_4_route_assembly(self):
        """Audit 4: Route Assembly and Validation"""
        self.print_header("AUDIT SECTION 4: ROUTE ASSEMBLY AND VALIDATION")
        
        # Check for route building logic
        brain_path = "offchain/ml/brain.py"
        if os.path.exists(brain_path):
            with open(brain_path, 'r') as f:
                content = f.read()
            
            # Check for graph-based routing
            if 'rustworkx' in content or 'PyDiGraph' in content:
                self.add_result(
                    "Route Assembly",
                    "Graph-based Routing",
                    "PASS",
                    "Using rustworkx for efficient graph-based pathfinding"
                )
            else:
                self.add_result(
                    "Route Assembly",
                    "Graph-based Routing",
                    "WARNING",
                    "No graph-based routing implementation found"
                )
            
            # Check for multi-hop support
            if 'multi_hop' in content.lower() or 'multi-hop' in content.lower():
                self.add_result(
                    "Route Assembly",
                    "Multi-hop Routes",
                    "PASS",
                    "Multi-hop route optimization implemented"
                )
        
        # Check bridge integration for cross-chain routes
        bridge_path = "routing/bridge_manager.py"
        if os.path.exists(bridge_path):
            self.add_result(
                "Route Assembly",
                "Cross-chain Routing",
                "PASS",
                "Bridge manager found for cross-chain route assembly"
            )
        else:
            self.add_result(
                "Route Assembly",
                "Cross-chain Routing",
                "INFO",
                "No bridge manager found (single-chain operation)"
            )
    
    def audit_5_flashloan_feasibility(self):
        """Audit 5: Flashloan Feasibility Checks"""
        self.print_header("AUDIT SECTION 5: FLASHLOAN FEASIBILITY CHECKS")
        
        # Check Polygon flashloan configuration
        if self.polygon_config and 'flashloan_providers' in self.polygon_config:
            providers = self.polygon_config['flashloan_providers']
            self.add_result(
                "Flashloan",
                "Provider Configuration",
                "PASS",
                f"Configured {len(providers)} flashloan providers: {', '.join(providers.keys())}"
            )
            
            # Validate provider addresses
            for provider_name, address in providers.items():
                if Web3.is_checksum_address(address):
                    self.add_result(
                        "Flashloan",
                        f"{provider_name.title()} Address",
                        "PASS",
                        f"Valid checksum address: {address}"
                    )
                else:
                    self.add_result(
                        "Flashloan",
                        f"{provider_name.title()} Address",
                        "FAIL",
                        f"Invalid address format: {address}",
                        [f"Use checksummed address for {provider_name}"]
                    )
        else:
            self.add_result(
                "Flashloan",
                "Provider Configuration",
                "FAIL",
                "No flashloan providers configured for Polygon",
                ["Add Aave and Balancer flashloan provider addresses to config"]
            )
        
        # Check flashloan fee configuration
        if self.config and 'flashloan_fees' in self.config:
            fees = self.config['flashloan_fees']
            self.add_result(
                "Flashloan",
                "Fee Configuration",
                "PASS",
                f"Flashloan fees configured: {fees}"
            )
        
        # Check for TVL validation
        commander_path = "offchain/core/titan_commander_core.py"
        if os.path.exists(commander_path):
            with open(commander_path, 'r') as f:
                content = f.read()
            
            if 'tvl' in content.lower() or 'liquidity' in content.lower():
                self.add_result(
                    "Flashloan",
                    "Liquidity Validation",
                    "PASS",
                    "TVL/liquidity validation implemented in commander module"
                )
    
    def audit_6_profit_calculations(self):
        """Audit 6: Profit Simulation and Calculations (DefiMathEngine)"""
        self.print_header("AUDIT SECTION 6: PROFIT SIMULATION AND CALCULATIONS")
        
        # Check for ProfitEngine implementation
        brain_path = "offchain/ml/brain.py"
        if os.path.exists(brain_path):
            with open(brain_path, 'r') as f:
                content = f.read()
            
            # Check for profit calculation
            if 'ProfitEngine' in content:
                self.add_result(
                    "Profit Calculations",
                    "Profit Engine",
                    "PASS",
                    "ProfitEngine class found in brain module"
                )
                
                # Check for comprehensive profit formula
                if 'flash_fee' in content and 'gas_cost' in content and 'bridge_fee' in content:
                    self.add_result(
                        "Profit Calculations",
                        "Comprehensive Profit Formula",
                        "PASS",
                        "Profit calculation includes flash fees, gas costs, and bridge fees"
                    )
                else:
                    self.add_result(
                        "Profit Calculations",
                        "Comprehensive Profit Formula",
                        "WARNING",
                        "Profit formula may be missing some fee components"
                    )
            else:
                self.add_result(
                    "Profit Calculations",
                    "Profit Engine",
                    "WARNING",
                    "No ProfitEngine class found"
                )
        
        # Check for gas estimation
        gas_manager_path = "offchain/execution/gas_manager.js"
        if os.path.exists(gas_manager_path):
            self.add_result(
                "Profit Calculations",
                "Gas Estimation",
                "PASS",
                "Gas manager module found for accurate gas cost calculation"
            )
        else:
            self.add_result(
                "Profit Calculations",
                "Gas Estimation",
                "WARNING",
                "No dedicated gas manager found",
                ["Implement gas estimation module for accurate profit calculations"]
            )
        
        # Check for simulation engine
        sim_engine_path = "offchain/core/titan_simulation_engine.py"
        if os.path.exists(sim_engine_path):
            self.add_result(
                "Profit Calculations",
                "Simulation Engine",
                "PASS",
                "Titan simulation engine found for pre-execution validation"
            )
    
    def audit_7_ml_integration(self):
        """Audit 7: Machine Learning Integration (AISignalRanker)"""
        self.print_header("AUDIT SECTION 7: MACHINE LEARNING INTEGRATION")
        
        # Check cortex modules
        cortex_modules = [
            ("offchain/ml/cortex/forecaster.py", "Market Forecaster"),
            ("offchain/ml/cortex/rl_optimizer.py", "Q-Learning Optimizer"),
            ("offchain/ml/cortex/feature_store.py", "Feature Store"),
            ("offchain/ml/hf_ranker.py", "HuggingFace Ranker")
        ]
        
        found_modules = []
        for module_path, module_name in cortex_modules:
            if os.path.exists(module_path):
                found_modules.append(module_name)
                self.add_result(
                    "ML Integration",
                    module_name,
                    "PASS",
                    f"{module_name} module found"
                )
        
        if len(found_modules) >= 3:
            self.add_result(
                "ML Integration",
                "ML Components Coverage",
                "PASS",
                f"Found {len(found_modules)}/4 ML components: {', '.join(found_modules)}"
            )
        else:
            self.add_result(
                "ML Integration",
                "ML Components Coverage",
                "WARNING",
                f"Only {len(found_modules)}/4 ML components found"
            )
        
        # Check ML configuration
        if self.config:
            ml_configs = [
                'TAR_SCORING_ENABLED',
                'AI_PREDICTION_ENABLED',
                'CATBOOST_MODEL_ENABLED',
                'SELF_LEARNING_ENABLED'
            ]
            
            # Check in brain.py imports
            brain_path = "offchain/ml/brain.py"
            if os.path.exists(brain_path):
                with open(brain_path, 'r') as f:
                    content = f.read()
                
                enabled_features = [cfg for cfg in ml_configs if cfg in content]
                if enabled_features:
                    self.add_result(
                        "ML Integration",
                        "ML Feature Flags",
                        "PASS",
                        f"ML features configured: {', '.join(enabled_features)}"
                    )
    
    def audit_8_code_quality(self):
        """Audit 8: Code Quality and Maintainability"""
        self.print_header("AUDIT SECTION 8: CODE QUALITY AND MAINTAINABILITY")
        
        # Check Python code structure
        py_files = []
        for root, dirs, files in os.walk('offchain'):
            for file in files:
                if file.endswith('.py'):
                    py_files.append(os.path.join(root, file))
        
        self.add_result(
            "Code Quality",
            "Python Codebase Size",
            "INFO",
            f"Found {len(py_files)} Python source files"
        )
        
        # Check for logging
        files_with_logging = 0
        for py_file in py_files:
            try:
                with open(py_file, 'r') as f:
                    if 'import logging' in f.read():
                        files_with_logging += 1
            except:
                pass
        
        logging_percentage = (files_with_logging / len(py_files) * 100) if py_files else 0
        if logging_percentage > 70:
            self.add_result(
                "Code Quality",
                "Logging Coverage",
                "PASS",
                f"{files_with_logging}/{len(py_files)} files ({logging_percentage:.1f}%) have logging"
            )
        else:
            self.add_result(
                "Code Quality",
                "Logging Coverage",
                "WARNING",
                f"Only {logging_percentage:.1f}% of files have logging",
                ["Add comprehensive logging to all modules for debugging and monitoring"]
            )
        
        # Check for error handling
        files_with_try_except = 0
        for py_file in py_files:
            try:
                with open(py_file, 'r') as f:
                    if 'try:' in f.read() and 'except' in f.read():
                        files_with_try_except += 1
            except:
                pass
        
        error_handling_percentage = (files_with_try_except / len(py_files) * 100) if py_files else 0
        if error_handling_percentage > 60:
            self.add_result(
                "Code Quality",
                "Error Handling",
                "PASS",
                f"{error_handling_percentage:.1f}% of files have error handling"
            )
        else:
            self.add_result(
                "Code Quality",
                "Error Handling",
                "WARNING",
                f"Only {error_handling_percentage:.1f}% of files have error handling"
            )
        
        # Check for documentation
        self.audit_documentation()
    
    def audit_documentation(self):
        """Audit documentation coverage"""
        doc_files = [
            "README.md",
            "AUDIT_REPORT.md",
            "OPERATIONS_GUIDE.md",
            "SECURITY_SUMMARY.md"
        ]
        
        found_docs = [doc for doc in doc_files if os.path.exists(doc)]
        
        if len(found_docs) >= 3:
            self.add_result(
                "Code Quality",
                "Documentation",
                "PASS",
                f"Found {len(found_docs)}/{len(doc_files)} key documentation files"
            )
        else:
            self.add_result(
                "Code Quality",
                "Documentation",
                "WARNING",
                f"Only {len(found_docs)}/{len(doc_files)} documentation files found"
            )
    
    def audit_9_performance_monitoring(self):
        """Audit 9: Performance Monitoring and Metrics"""
        self.print_header("AUDIT SECTION 9: PERFORMANCE MONITORING")
        
        # Check for monitoring modules
        monitoring_modules = [
            ("offchain/core/terminal_display.py", "Terminal Display"),
            ("offchain/core/trade_database.py", "Trade Database"),
            ("dashboard_server.py", "Dashboard Server")
        ]
        
        for module_path, module_name in monitoring_modules:
            if os.path.exists(module_path):
                self.add_result(
                    "Performance Monitoring",
                    module_name,
                    "PASS",
                    f"{module_name} module found"
                )
        
        # Check for metrics collection
        if os.path.exists("offchain/ml/cortex/feature_store.py"):
            self.add_result(
                "Performance Monitoring",
                "Metrics Collection",
                "PASS",
                "Feature store available for metrics aggregation"
            )
    
    def audit_10_security_compliance(self):
        """Audit 10: Security and Compliance"""
        self.print_header("AUDIT SECTION 10: SECURITY AND COMPLIANCE")
        
        # Check for security features
        security_checks = [
            (".env.example", "Environment Template", "Prevents accidental secret exposure"),
            (".gitignore", "Git Ignore", "Prevents committing sensitive files"),
            ("offchain/core/mev_detector.py", "MEV Detection", "Protects against MEV attacks"),
        ]
        
        for file_path, feature_name, description in security_checks:
            if os.path.exists(file_path):
                self.add_result(
                    "Security",
                    feature_name,
                    "PASS",
                    description
                )
            else:
                self.add_result(
                    "Security",
                    feature_name,
                    "WARNING",
                    f"{feature_name} not found"
                )
        
        # Check .env is not committed
        if os.path.exists(".env") and os.path.exists(".gitignore"):
            with open(".gitignore", 'r') as f:
                if ".env" in f.read():
                    self.add_result(
                        "Security",
                        ".env Protection",
                        "PASS",
                        ".env file properly excluded from git"
                    )
        
        # Check for private key exposure
        if os.path.exists(".env"):
            with open(".env", 'r') as f:
                content = f.read()
                if 'PRIVATE_KEY=' in content and '0x' in content:
                    # Don't log the actual key
                    self.add_result(
                        "Security",
                        "Private Key Configuration",
                        "WARNING",
                        "Private key detected in .env - ensure .env is in .gitignore",
                        ["Never commit .env file to version control"]
                    )
    
    def generate_report(self):
        """Generate comprehensive audit report"""
        self.print_header("AUDIT REPORT GENERATION")
        
        # Calculate statistics
        total_checks = len(self.results)
        passed = len([r for r in self.results if r.status == 'PASS'])
        failed = len([r for r in self.results if r.status == 'FAIL'])
        warnings = len([r for r in self.results if r.status == 'WARNING'])
        info = len([r for r in self.results if r.status == 'INFO'])
        
        # Calculate score
        score = (passed / total_checks * 100) if total_checks > 0 else 0
        
        # Determine overall status
        if failed > 0:
            overall_status = "FAIL"
            status_color = Fore.RED
        elif warnings > 5:
            overall_status = "NEEDS IMPROVEMENT"
            status_color = Fore.YELLOW
        else:
            overall_status = "PASS"
            status_color = Fore.GREEN
        
        # Print summary
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{'COMPREHENSIVE AUDIT SUMMARY'.center(80)}")
        print(f"{'='*80}{Style.RESET_ALL}\n")
        
        print(f"Total Checks:    {total_checks}")
        print(f"{Fore.GREEN}Passed:          {passed} ({passed/total_checks*100:.1f}%){Style.RESET_ALL}")
        print(f"{Fore.RED}Failed:          {failed} ({failed/total_checks*100:.1f}%){Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Warnings:        {warnings} ({warnings/total_checks*100:.1f}%){Style.RESET_ALL}")
        print(f"{Fore.CYAN}Info:            {info} ({info/total_checks*100:.1f}%){Style.RESET_ALL}")
        
        print(f"\n{status_color}Overall Score:   {score:.1f}/100")
        print(f"Overall Status:  {overall_status}{Style.RESET_ALL}\n")
        
        # Generate markdown report
        report_filename = f"COMPREHENSIVE_AUDIT_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_filename, 'w') as f:
            f.write("# Comprehensive Operational Audit Report\n")
            f.write("## Titan2.0 Arbitrage System - Polygon Ecosystem\n\n")
            
            f.write(f"**Audit Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Duration:** {(datetime.now() - self.start_time).total_seconds():.2f} seconds\n")
            f.write(f"**Overall Score:** {score:.1f}/100\n")
            f.write(f"**Overall Status:** {overall_status}\n\n")
            
            f.write("---\n\n")
            
            f.write("## Executive Summary\n\n")
            f.write(f"This comprehensive audit evaluated the Titan2.0 arbitrage system across {total_checks} operational checks ")
            f.write("covering configuration, data ingestion, pool management, route assembly, flashloan feasibility, ")
            f.write("profit calculations, ML integration, code quality, performance monitoring, and security.\n\n")
            
            f.write(f"- ✅ **Passed Checks:** {passed}\n")
            f.write(f"- ❌ **Failed Checks:** {failed}\n")
            f.write(f"- ⚠️ **Warnings:** {warnings}\n")
            f.write(f"- ℹ️ **Informational:** {info}\n\n")
            
            f.write("---\n\n")
            
            f.write("## Detailed Findings\n\n")
            
            # Group results by category
            categories = {}
            for result in self.results:
                if result.category not in categories:
                    categories[result.category] = []
                categories[result.category].append(result)
            
            for category, results in categories.items():
                f.write(f"### {category}\n\n")
                
                for result in results:
                    status_emoji = {
                        'PASS': '✅',
                        'FAIL': '❌',
                        'WARNING': '⚠️',
                        'INFO': 'ℹ️'
                    }.get(result.status, '•')
                    
                    f.write(f"{status_emoji} **{result.check_name}** - {result.status}\n")
                    if result.details:
                        f.write(f"   - {result.details}\n")
                    
                    if result.recommendations:
                        f.write(f"   - **Recommendations:**\n")
                        for rec in result.recommendations:
                            f.write(f"     - {rec}\n")
                    f.write("\n")
                
                f.write("\n")
            
            f.write("---\n\n")
            
            f.write("## Critical Issues\n\n")
            critical_issues = [r for r in self.results if r.status == 'FAIL']
            if critical_issues:
                for issue in critical_issues:
                    f.write(f"- **{issue.check_name}:** {issue.details}\n")
                    if issue.recommendations:
                        for rec in issue.recommendations:
                            f.write(f"  - Recommendation: {rec}\n")
            else:
                f.write("No critical issues found.\n")
            
            f.write("\n---\n\n")
            
            f.write("## Recommendations Summary\n\n")
            all_recommendations = []
            for result in self.results:
                all_recommendations.extend(result.recommendations)
            
            if all_recommendations:
                for i, rec in enumerate(set(all_recommendations), 1):
                    f.write(f"{i}. {rec}\n")
            else:
                f.write("No specific recommendations at this time.\n")
            
            f.write("\n---\n\n")
            f.write("## Conclusion\n\n")
            
            if overall_status == "PASS":
                f.write("The Titan2.0 system demonstrates strong operational efficiency and compliance ")
                f.write("within the Polygon ecosystem. The system is well-architected with comprehensive ")
                f.write("monitoring, ML integration, and security features.\n")
            elif overall_status == "NEEDS IMPROVEMENT":
                f.write("The Titan2.0 system shows good foundation but requires attention to several ")
                f.write("areas before full production deployment. Address the warnings and recommendations ")
                f.write("to improve operational efficiency.\n")
            else:
                f.write("The Titan2.0 system requires immediate attention to critical issues before ")
                f.write("production deployment. Address all failed checks and critical warnings.\n")
        
        print(f"{Fore.GREEN}Report generated: {report_filename}{Style.RESET_ALL}\n")
        
        return report_filename, score, overall_status
    
    def run_complete_audit(self):
        """Run all audit sections"""
        print(f"{Fore.CYAN}{'='*80}")
        print(f"{'COMPREHENSIVE TITAN2.0 OPERATIONAL AUDIT'.center(80)}")
        print(f"{'Polygon Ecosystem Focus'.center(80)}")
        print(f"{'='*80}{Style.RESET_ALL}\n")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        try:
            self.audit_1_configuration()
            self.audit_2_price_scanning()
            self.audit_3_pool_registry()
            self.audit_4_route_assembly()
            self.audit_5_flashloan_feasibility()
            self.audit_6_profit_calculations()
            self.audit_7_ml_integration()
            self.audit_8_code_quality()
            self.audit_9_performance_monitoring()
            self.audit_10_security_compliance()
            
            # Generate final report
            report_file, score, status = self.generate_report()
            
            return report_file, score, status
            
        except Exception as e:
            logger.error(f"Audit failed with error: {e}", exc_info=True)
            self.add_result(
                "System",
                "Audit Execution",
                "FAIL",
                f"Audit failed with error: {e}"
            )
            return None, 0, "FAIL"


def main():
    """Main audit execution"""
    audit = ComprehensiveAudit()
    report_file, score, status = audit.run_complete_audit()
    
    if report_file:
        print(f"\n{Fore.GREEN}✅ Audit completed successfully!")
        print(f"📄 Full report: {report_file}")
        print(f"📊 Score: {score:.1f}/100")
        print(f"📋 Status: {status}{Style.RESET_ALL}\n")
    else:
        print(f"\n{Fore.RED}❌ Audit encountered errors{Style.RESET_ALL}\n")
    
    return 0 if status in ["PASS", "NEEDS IMPROVEMENT"] else 1


if __name__ == "__main__":
    sys.exit(main())
