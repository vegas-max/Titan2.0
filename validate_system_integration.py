#!/usr/bin/env python3
"""
TITAN 2.0 - Complete System-Wide Validation and Integration
=============================================================

This script validates the entire Titan system end-to-end:
- RPC endpoints and connectivity
- API keys and external services
- Import statements and dependencies
- On-chain data access
- Address validation (no zero addresses/placeholders)
- Function return values
- Class initialization
- Module communication
- Complete flow from boot to execution
"""

import os
import sys
import json
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Tuple
from decimal import Decimal
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

class SystemValidator:
    """Comprehensive system validation"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.successes = []
        self.env_loaded = False
        
    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{text.center(80)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        
    def print_success(self, text: str):
        """Print success message"""
        print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")
        self.successes.append(text)
        
    def print_warning(self, text: str):
        """Print warning message"""
        print(f"{Fore.YELLOW}⚠️  {text}{Style.RESET_ALL}")
        self.warnings.append(text)
        
    def print_error(self, text: str):
        """Print error message"""
        print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")
        self.errors.append(text)
        
    def print_info(self, text: str):
        """Print info message"""
        print(f"{Fore.BLUE}ℹ️  {text}{Style.RESET_ALL}")
    
    # ========================
    # Phase 1: Environment & RPC
    # ========================
    
    def validate_environment(self) -> bool:
        """Validate .env file and load environment variables"""
        self.print_header("PHASE 1: Environment & Configuration Validation")
        
        # Check if .env exists
        env_path = Path('.env')
        if not env_path.exists():
            self.print_warning(".env file not found - using environment variables only")
            self.print_info("For full functionality, copy .env.example to .env and configure")
        else:
            self.print_success(".env file found")
            
        # Load .env
        try:
            from dotenv import load_dotenv
            load_dotenv()
            self.env_loaded = True
            self.print_success("Environment variables loaded")
        except Exception as e:
            self.print_error(f"Failed to load environment: {e}")
            return False
            
        # Validate critical environment variables
        critical_vars = {
            'EXECUTION_MODE': os.getenv('EXECUTION_MODE', 'PAPER'),
            'MIN_PROFIT_USD': os.getenv('MIN_PROFIT_USD', '5.00'),
            'MAX_BASE_FEE_GWEI': os.getenv('MAX_BASE_FEE_GWEI', '200'),
        }
        
        for var, value in critical_vars.items():
            if value:
                self.print_success(f"{var} = {value}")
            else:
                self.print_warning(f"{var} not set, using defaults")
                
        return True
    
    def validate_rpc_endpoints(self) -> bool:
        """Validate RPC endpoint configuration"""
        self.print_header("PHASE 1: RPC Endpoint Validation")
        
        required_chains = {
            1: ('Ethereum', 'RPC_ETHEREUM'),
            137: ('Polygon', 'RPC_POLYGON'),
            42161: ('Arbitrum', 'RPC_ARBITRUM'),
            10: ('Optimism', 'RPC_OPTIMISM'),
            8453: ('Base', 'RPC_BASE'),
        }
        
        for chain_id, (name, env_var) in required_chains.items():
            rpc_url = os.getenv(env_var)
            if rpc_url and 'YOUR' not in rpc_url.upper():
                self.print_success(f"{name} RPC configured: {rpc_url[:50]}...")
            else:
                self.print_warning(f"{name} RPC not configured ({env_var})")
                
        return True
    
    def test_web3_connectivity(self) -> bool:
        """Test Web3 connections to configured chains"""
        self.print_header("PHASE 1: Web3 Connectivity Test")
        
        try:
            from web3 import Web3
            
            # Test Polygon (most common for testing)
            polygon_rpc = os.getenv('RPC_POLYGON')
            if polygon_rpc and 'YOUR' not in polygon_rpc.upper():
                try:
                    w3 = Web3(Web3.HTTPProvider(polygon_rpc))
                    if w3.is_connected():
                        block = w3.eth.block_number
                        self.print_success(f"Polygon connected - Latest block: {block}")
                    else:
                        self.print_warning("Polygon RPC configured but not responding")
                except Exception as e:
                    self.print_warning(f"Polygon connection failed: {str(e)[:100]}")
            else:
                self.print_info("Polygon RPC not configured - skipping connectivity test")
                
        except ImportError:
            self.print_error("web3 package not installed - run: pip install web3")
            return False
            
        return True
    
    # ========================
    # Phase 2: API Keys
    # ========================
    
    def validate_api_keys(self) -> bool:
        """Validate external API keys"""
        self.print_header("PHASE 2: API Key Validation")
        
        api_keys = {
            'LIFI_API_KEY': 'Li.Fi (Bridge Aggregation)',
            'COINGECKO_API_KEY': 'CoinGecko (Price Feeds)',
            'ONEINCH_API_KEY': '1inch (DEX Aggregation)',
            'ZEROX_API_KEY': '0x Protocol',
            'BLOXROUTE_AUTH': 'BloxRoute (MEV Protection)',
        }
        
        for key, description in api_keys.items():
            value = os.getenv(key)
            if value and 'YOUR' not in value.upper() and len(value) > 10:
                self.print_success(f"{description}: Configured")
            else:
                if key == 'LIFI_API_KEY':
                    self.print_warning(f"{description}: Not configured (recommended for cross-chain)")
                else:
                    self.print_info(f"{description}: Optional, not configured")
                    
        return True
    
    # ========================
    # Phase 3: Python Imports
    # ========================
    
    def validate_python_imports(self) -> bool:
        """Validate all Python dependencies can be imported"""
        self.print_header("PHASE 3: Python Import Validation")
        
        required_imports = [
            ('web3', 'Web3 library'),
            ('pandas', 'Pandas data analysis'),
            ('numpy', 'NumPy numerical computing'),
            ('rustworkx', 'Graph algorithms (rustworkx)'),
            ('redis', 'Redis client'),
            ('aiohttp', 'Async HTTP client'),
            ('eth_abi', 'Ethereum ABI encoding'),
            ('colorama', 'Terminal colors'),
        ]
        
        for module, description in required_imports:
            try:
                __import__(module)
                self.print_success(f"{description} ({module})")
            except ImportError:
                self.print_error(f"{description} ({module}) - Install with: pip install {module}")
                
        # Test core module imports
        core_modules = [
            ('offchain.core.config', 'Core configuration'),
            ('offchain.core.token_discovery', 'Token discovery'),
            ('offchain.ml.brain', 'OmniBrain'),
            ('offchain.ml.dex_pricer', 'DEX pricer'),
        ]
        
        for module, description in core_modules:
            try:
                __import__(module)
                self.print_success(f"{description} ({module})")
            except Exception as e:
                self.print_error(f"{description} ({module}) failed: {str(e)[:100]}")
                
        return True
    
    # ========================
    # Phase 4: Configuration Validation
    # ========================
    
    def validate_config(self) -> bool:
        """Validate configuration files and addresses"""
        self.print_header("PHASE 4: Configuration Validation")
        
        try:
            from offchain.core.config import CHAINS, BALANCER_V3_VAULT, DEX_ROUTERS
            
            # Validate Balancer V3 Vault address
            if BALANCER_V3_VAULT and BALANCER_V3_VAULT != "0x0000000000000000000000000000000000000000":
                self.print_success(f"Balancer V3 Vault: {BALANCER_V3_VAULT}")
            else:
                self.print_error("Balancer V3 Vault address is zero or not configured")
                
            # Validate chain configurations
            self.print_info(f"Configured chains: {len(CHAINS)}")
            
            zero_address_count = 0
            for chain_id, chain_config in CHAINS.items():
                chain_name = chain_config.get('name', f'Chain {chain_id}')
                
                # Check for zero addresses (indicating unavailable protocols)
                for key, value in chain_config.items():
                    if key.endswith('_router') or key.endswith('_pool'):
                        if value == "0x0000000000000000000000000000000000000000":
                            zero_address_count += 1
                            
            if zero_address_count > 0:
                self.print_info(f"Found {zero_address_count} unavailable protocols (zero addresses) - this is expected")
                
            self.print_success("Configuration loaded successfully")
                
        except Exception as e:
            self.print_error(f"Configuration validation failed: {e}")
            return False
            
        return True
    
    # ========================
    # Phase 5: Address Validation
    # ========================
    
    def validate_addresses(self) -> bool:
        """Validate no critical placeholder addresses"""
        self.print_header("PHASE 5: Address Validation")
        
        # Check wallet configuration
        executor_addr = os.getenv('EXECUTOR_ADDRESS')
        execution_mode = os.getenv('EXECUTION_MODE', 'PAPER').upper()
        
        if execution_mode == 'LIVE':
            if not executor_addr or executor_addr == '0x0000000000000000000000000000000000000000':
                self.print_error("EXECUTOR_ADDRESS required for LIVE mode")
            else:
                self.print_success(f"Executor address: {executor_addr}")
                
            private_key = os.getenv('PRIVATE_KEY')
            if not private_key or len(private_key) != 66:
                self.print_error("Valid PRIVATE_KEY required for LIVE mode")
            else:
                self.print_success("Private key configured (length valid)")
        else:
            self.print_info("PAPER mode - wallet validation skipped")
            
        return True
    
    # ========================
    # Phase 6: Class Initialization
    # ========================
    
    def test_class_initialization(self) -> bool:
        """Test that core classes can be initialized"""
        self.print_header("PHASE 6: Class Initialization Test")
        
        # Test ProfitEngine
        try:
            from offchain.ml.brain import ProfitEngine
            engine = ProfitEngine()
            result = engine.calculate_enhanced_profit(
                Decimal("1000"),
                Decimal("1010"),
                Decimal("2"),
                Decimal("3")
            )
            if result['is_profitable']:
                self.print_success(f"ProfitEngine initialized and working - Test profit: ${result['net_profit']}")
            else:
                self.print_warning("ProfitEngine initialized but test calculation shows no profit")
        except Exception as e:
            self.print_error(f"ProfitEngine initialization failed: {e}")
            
        # Test MarketForecaster
        try:
            from offchain.ml.cortex.forecaster import MarketForecaster
            forecaster = MarketForecaster()
            self.print_success("MarketForecaster initialized")
        except Exception as e:
            self.print_error(f"MarketForecaster initialization failed: {e}")
            
        # Test QLearningAgent
        try:
            from offchain.ml.cortex.rl_optimizer import QLearningAgent
            agent = QLearningAgent()
            self.print_success("QLearningAgent initialized")
        except Exception as e:
            self.print_error(f"QLearningAgent initialization failed: {e}")
            
        return True
    
    # ========================
    # Phase 7: Signal Communication
    # ========================
    
    def test_signal_communication(self) -> bool:
        """Test signal file communication"""
        self.print_header("PHASE 7: Signal Communication Test")
        
        # Check signal directories
        signals_dir = Path('signals/outgoing')
        processed_dir = Path('signals/processed')
        
        if signals_dir.exists():
            self.print_success(f"Signal output directory exists: {signals_dir}")
        else:
            signals_dir.mkdir(parents=True, exist_ok=True)
            self.print_success(f"Created signal output directory: {signals_dir}")
            
        if processed_dir.exists():
            self.print_success(f"Processed signal directory exists: {processed_dir}")
        else:
            processed_dir.mkdir(parents=True, exist_ok=True)
            self.print_success(f"Created processed signal directory: {processed_dir}")
            
        # Test signal creation
        try:
            test_signal = {
                "chainId": 137,
                "token": "USDC",
                "amount": "1000000",
                "expected_profit": 10.50,
                "timestamp": time.time()
            }
            
            test_file = signals_dir / f"test_signal_{int(time.time())}.json"
            with open(test_file, 'w') as f:
                json.dump(test_signal, f, indent=2)
                
            self.print_success("Test signal created successfully")
            
            # Clean up test signal
            test_file.unlink()
            self.print_success("Test signal cleaned up")
            
        except Exception as e:
            self.print_error(f"Signal communication test failed: {e}")
            return False
            
        return True
    
    # ========================
    # Phase 8: Terminal Display
    # ========================
    
    def test_terminal_display(self) -> bool:
        """Test terminal display functionality"""
        self.print_header("PHASE 8: Terminal Display Test")
        
        try:
            from offchain.core.terminal_display import get_terminal_display
            display = get_terminal_display()
            
            # Test basic display methods
            display.log_opportunity_scan("USDC", 137, "UniV3", "Sushi", 1000, False, 0, 25.0)
            display.log_decision("APPROVE", "USDC", 137, "Test decision")
            
            self.print_success("Terminal display working")
            
        except Exception as e:
            self.print_error(f"Terminal display test failed: {e}")
            return False
            
        return True
    
    # ========================
    # Summary
    # ========================
    
    def print_summary(self):
        """Print validation summary"""
        self.print_header("VALIDATION SUMMARY")
        
        total = len(self.successes) + len(self.warnings) + len(self.errors)
        
        print(f"\n{Fore.GREEN}✅ Successes: {len(self.successes)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚠️  Warnings: {len(self.warnings)}{Style.RESET_ALL}")
        print(f"{Fore.RED}❌ Errors: {len(self.errors)}{Style.RESET_ALL}")
        print(f"\n📊 Total Checks: {total}\n")
        
        if self.errors:
            print(f"{Fore.RED}CRITICAL ERRORS FOUND:{Style.RESET_ALL}")
            for error in self.errors:
                print(f"  • {error}")
            print(f"\n{Fore.RED}⚠️  System may not function correctly. Please fix errors above.{Style.RESET_ALL}\n")
            return False
        elif self.warnings:
            print(f"{Fore.YELLOW}WARNINGS FOUND:{Style.RESET_ALL}")
            for warning in self.warnings:
                print(f"  • {warning}")
            print(f"\n{Fore.YELLOW}⚠️  System will function but some features may be limited.{Style.RESET_ALL}\n")
            return True
        else:
            print(f"{Fore.GREEN}🎉 ALL VALIDATIONS PASSED!{Style.RESET_ALL}")
            print(f"{Fore.GREEN}✅ System is properly configured and ready to run.{Style.RESET_ALL}\n")
            return True
    
    def run_all(self) -> bool:
        """Run all validation phases"""
        print(f"\n{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}TITAN 2.0 - COMPLETE SYSTEM VALIDATION{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}\n")
        
        # Run all phases
        self.validate_environment()
        self.validate_rpc_endpoints()
        self.test_web3_connectivity()
        self.validate_api_keys()
        self.validate_python_imports()
        self.validate_config()
        self.validate_addresses()
        self.test_class_initialization()
        self.test_signal_communication()
        self.test_terminal_display()
        
        # Print summary
        return self.print_summary()


def main():
    """Main entry point"""
    validator = SystemValidator()
    success = validator.run_all()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
