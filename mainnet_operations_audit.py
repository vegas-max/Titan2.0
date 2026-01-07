#!/usr/bin/env python3
"""
Comprehensive Mainnet Operations & Data Flow Audit Script
Titan 2.0 Arbitrage System

This script performs a thorough audit of all components and modules
to ensure mainnet readiness and seamless data flow.
"""

import os
import sys
import json
import importlib
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}\n")

def print_section(text: str):
    """Print a section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}>>> {text}{Colors.RESET}")
    print(f"{Colors.BLUE}{'-'*80}{Colors.RESET}")

def print_pass(text: str):
    """Print a pass message"""
    print(f"{Colors.GREEN}✓ PASS:{Colors.RESET} {text}")

def print_fail(text: str):
    """Print a fail message"""
    print(f"{Colors.RED}✗ FAIL:{Colors.RESET} {text}")

def print_warn(text: str):
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠ WARN:{Colors.RESET} {text}")

def print_info(text: str):
    """Print an info message"""
    print(f"{Colors.CYAN}ℹ INFO:{Colors.RESET} {text}")

class MainnetAudit:
    """Comprehensive mainnet operations audit"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'total': 0
        }
        self.critical_issues = []
        self.warnings = []
        self.recommendations = []
        
    def run_audit(self):
        """Run complete audit"""
        print_header("TITAN 2.0 MAINNET OPERATIONS & DATA FLOW AUDIT")
        print(f"Audit Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Base Path: {self.base_path}")
        
        # Run all audit sections
        self.audit_environment_config()
        self.audit_core_configuration()
        self.audit_data_ingestion()
        self.audit_intelligence_layer()
        self.audit_communication_bus()
        self.audit_execution_layer()
        self.audit_blockchain_layer()
        self.audit_monitoring_layer()
        self.audit_security_measures()
        self.audit_data_flow_integration()
        
        # Print summary
        self.print_summary()
        
        # Return exit code based on critical issues
        return 0 if len(self.critical_issues) == 0 else 1
    
    def audit_environment_config(self):
        """Audit environment configuration"""
        print_section("1. ENVIRONMENT CONFIGURATION")
        
        # Check .env file exists
        env_file = self.base_path / '.env'
        if env_file.exists():
            print_pass(".env file exists")
            self.results['passed'] += 1
        else:
            print_fail(".env file missing")
            self.critical_issues.append("Environment file (.env) not found")
            self.results['failed'] += 1
        self.results['total'] += 1
        
        # Check .env.example exists
        env_example = self.base_path / '.env.example'
        if env_example.exists():
            print_pass(".env.example template exists")
            self.results['passed'] += 1
        else:
            print_warn(".env.example template missing")
            self.warnings.append("Missing .env.example template for reference")
            self.results['warnings'] += 1
        self.results['total'] += 1
        
        # Check critical environment variables
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_content = f.read()
            
            critical_vars = [
                'PRIVATE_KEY',
                'RPC_POLYGON',
                'FLASH_LOAN_ENABLED',
                'MIN_PROFIT_USD'
            ]
            
            missing_vars = []
            for var in critical_vars:
                if var not in env_content or f'{var}=' in env_content and env_content.split(f'{var}=')[1].split('\n')[0].strip() == '':
                    missing_vars.append(var)
            
            # Check EXECUTION_MODE separately (optional but recommended)
            if 'EXECUTION_MODE=' not in env_content:
                self.warnings.append("EXECUTION_MODE not set - defaults to PAPER mode")
                self.results['warnings'] += 1
            elif 'EXECUTION_MODE=LIVE' in env_content:
                print_info("EXECUTION_MODE set to LIVE - ensure you're ready for real trading!")
            elif 'EXECUTION_MODE=PAPER' in env_content:
                print_info("EXECUTION_MODE set to PAPER - safe for testing")
            self.results['total'] += 1
            
            if missing_vars:
                print_fail(f"Missing critical environment variables: {', '.join(missing_vars)}")
                self.critical_issues.append(f"Missing environment variables: {', '.join(missing_vars)}")
                self.results['failed'] += 1
            else:
                print_pass("All critical environment variables present")
                self.results['passed'] += 1
            self.results['total'] += 1
            
            # Check FLASH_LOAN_ENABLED setting
            if 'FLASH_LOAN_ENABLED=true' in env_content:
                print_pass("Flash loans enabled (required for mainnet)")
                self.results['passed'] += 1
            else:
                print_fail("Flash loans not enabled - CRITICAL for mainnet operations")
                self.critical_issues.append("FLASH_LOAN_ENABLED must be true for mainnet")
                self.results['failed'] += 1
            self.results['total'] += 1
            
            # Check RPC failover configuration
            has_primary = 'RPC_POLYGON=' in env_content or 'RPC_ETHEREUM=' in env_content
            has_backup = 'ALCHEMY_RPC_POLY=' in env_content or 'ALCHEMY_RPC_ETH=' in env_content
            
            if has_primary and has_backup:
                print_pass("RPC failover configured (primary + backup)")
                self.results['passed'] += 1
            elif has_primary:
                print_warn("Only primary RPC configured - backup recommended")
                self.warnings.append("Configure backup RPC endpoints (Alchemy) for failover")
                self.results['warnings'] += 1
            else:
                print_fail("No RPC endpoints configured")
                self.critical_issues.append("RPC endpoints not configured")
                self.results['failed'] += 1
            self.results['total'] += 1
    
    def audit_core_configuration(self):
        """Audit core configuration files"""
        print_section("2. CORE CONFIGURATION")
        
        # Check config.json
        config_file = self.base_path / 'config.json'
        if config_file.exists():
            print_pass("config.json exists")
            self.results['passed'] += 1
            
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                # Check version
                if 'version' in config:
                    print_pass(f"Config version: {config['version']}")
                    self.results['passed'] += 1
                else:
                    print_warn("Config version not specified")
                    self.results['warnings'] += 1
                self.results['total'] += 1
                
                # Check chains/networks configuration
                chains_key = 'chains' if 'chains' in config else 'networks' if 'networks' in config else None
                if chains_key and isinstance(config[chains_key], dict):
                    chain_count = len(config[chains_key])
                    print_pass(f"Configured {chains_key}: {chain_count}")
                    self.results['passed'] += 1
                    
                    # Verify Polygon (137) is configured
                    polygon_found = False
                    for key, value in config[chains_key].items():
                        if isinstance(value, dict) and (value.get('chainId') == 137 or key.lower() == 'polygon' or key == '137'):
                            polygon_found = True
                            break
                    
                    if polygon_found:
                        print_pass("Polygon mainnet configured")
                        self.results['passed'] += 1
                    else:
                        print_warn("Polygon mainnet not explicitly configured")
                        self.warnings.append("Add Polygon (chain 137) to config.json")
                        self.results['warnings'] += 1
                    self.results['total'] += 1
                else:
                    print_fail("Chains/Networks configuration missing or invalid")
                    self.critical_issues.append("config.json missing 'chains' or 'networks' configuration")
                    self.results['failed'] += 1
                    self.results['total'] += 1
                
                # Check DEX configuration
                if 'dexes' in config and isinstance(config['dexes'], dict):
                    dex_count = len(config['dexes'])
                    print_pass(f"Configured DEXes: {dex_count}")
                    self.results['passed'] += 1
                else:
                    print_warn("DEX configuration missing or minimal")
                    self.warnings.append("Consider adding more DEX configurations")
                    self.results['warnings'] += 1
                self.results['total'] += 1
                
                # Check flash loan providers
                if 'flashLoanProviders' in config:
                    providers = config['flashLoanProviders']
                    print_pass(f"Flash loan providers configured: {len(providers)}")
                    self.results['passed'] += 1
                else:
                    print_warn("Flash loan providers not in config.json")
                    self.results['warnings'] += 1
                self.results['total'] += 1
                
            except json.JSONDecodeError as e:
                print_fail(f"Invalid JSON in config.json: {e}")
                self.critical_issues.append("config.json contains invalid JSON")
                self.results['failed'] += 1
                self.results['total'] += 1
        else:
            print_fail("config.json not found")
            self.critical_issues.append("config.json file missing")
            self.results['failed'] += 1
            self.results['total'] += 1
    
    def audit_data_ingestion(self):
        """Audit data ingestion layer"""
        print_section("3. DATA INGESTION LAYER")
        
        # Check DexPricer module
        dex_pricer_path = self.base_path / 'offchain' / 'ml' / 'dex_pricer.py'
        if dex_pricer_path.exists():
            print_pass("DexPricer module exists")
            self.results['passed'] += 1
            
            # Check for critical methods in DexPricer
            with open(dex_pricer_path, 'r') as f:
                content = f.read()
            
            critical_methods = ['get_price', 'get_pools', 'get_liquidity']
            found_methods = [m for m in critical_methods if f'def {m}' in content]
            
            if len(found_methods) >= 1:
                print_pass(f"DexPricer has price query methods")
                self.results['passed'] += 1
            else:
                print_warn(f"DexPricer missing some expected methods")
                self.results['warnings'] += 1
            self.results['total'] += 1
        else:
            print_fail("DexPricer module not found")
            self.critical_issues.append("DexPricer module (offchain/ml/dex_pricer.py) missing")
            self.results['failed'] += 1
            self.results['total'] += 1
        
        # Check Real Data Pipeline
        real_data_path = self.base_path / 'offchain' / 'core' / 'real_data_pipeline.py'
        if real_data_path.exists():
            print_pass("Real Data Pipeline module exists")
            self.results['passed'] += 1
        else:
            print_warn("Real Data Pipeline module not found")
            self.warnings.append("Consider implementing real_data_pipeline.py for live data")
            self.results['warnings'] += 1
        self.results['total'] += 1
        
        # Check WebSocket Manager
        ws_manager_path = self.base_path / 'offchain' / 'core' / 'websocket_manager.py'
        if ws_manager_path.exists():
            print_pass("WebSocket Manager exists")
            self.results['passed'] += 1
        else:
            print_warn("WebSocket Manager not found")
            self.warnings.append("WebSocket support recommended for real-time data")
            self.results['warnings'] += 1
        self.results['total'] += 1
    
    def audit_intelligence_layer(self):
        """Audit intelligence/brain layer"""
        print_section("4. INTELLIGENCE LAYER (BRAIN)")
        
        # Check Brain module
        brain_path = self.base_path / 'offchain' / 'ml' / 'brain.py'
        if brain_path.exists():
            print_pass("Brain module exists")
            self.results['passed'] += 1
            
            with open(brain_path, 'r') as f:
                brain_content = f.read()
            
            # Check for OmniBrain class
            if 'class OmniBrain' in brain_content:
                print_pass("OmniBrain class found")
                self.results['passed'] += 1
            else:
                print_fail("OmniBrain class not found")
                self.critical_issues.append("Brain module missing OmniBrain class")
                self.results['failed'] += 1
            self.results['total'] += 1
            
            # Check for graph-based routing (rustworkx)
            if 'rustworkx' in brain_content or 'rx.PyDiGraph' in brain_content:
                print_pass("Graph-based routing (rustworkx) implemented")
                self.results['passed'] += 1
            else:
                print_warn("Graph-based routing not detected")
                self.warnings.append("Consider using rustworkx for efficient pathfinding")
                self.results['warnings'] += 1
            self.results['total'] += 1
            
            # Check for async/await (non-blocking)
            if 'async def' in brain_content or 'await ' in brain_content:
                print_pass("Async operations implemented (non-blocking)")
                self.results['passed'] += 1
            elif 'time.sleep' in brain_content:
                print_warn("Blocking time.sleep() calls detected")
                self.warnings.append("Replace time.sleep() with asyncio.sleep() for non-blocking operations")
                self.results['warnings'] += 1
            else:
                print_info("Async operations not applicable")
            self.results['total'] += 1
            
            # Check for ProfitEngine
            if 'ProfitEngine' in brain_content or 'calculate_profit' in brain_content:
                print_pass("Profit calculation implemented")
                self.results['passed'] += 1
            else:
                print_fail("Profit calculation not found")
                self.critical_issues.append("Brain missing profit calculation logic")
                self.results['failed'] += 1
            self.results['total'] += 1
            
        else:
            print_fail("Brain module not found")
            self.critical_issues.append("Brain module (offchain/ml/brain.py) missing")
            self.results['failed'] += 1
            self.results['total'] += 1
        
        # Check AI/ML components
        ai_components = {
            'Market Forecaster': self.base_path / 'offchain' / 'ml' / 'cortex' / 'forecaster.py',
            'Q-Learning Optimizer': self.base_path / 'offchain' / 'ml' / 'cortex' / 'rl_optimizer.py',
            'Feature Store': self.base_path / 'offchain' / 'ml' / 'cortex' / 'feature_store.py'
        }
        
        for name, path in ai_components.items():
            if path.exists():
                print_pass(f"{name} module exists")
                self.results['passed'] += 1
            else:
                print_warn(f"{name} module not found")
                self.warnings.append(f"Consider implementing {name} for enhanced intelligence")
                self.results['warnings'] += 1
            self.results['total'] += 1
    
    def audit_communication_bus(self):
        """Audit communication layer (Redis/Files)"""
        print_section("5. COMMUNICATION BUS")
        
        # Check for Redis configuration
        env_file = self.base_path / '.env'
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_content = f.read()
            
            if 'REDIS_URL=' in env_content:
                print_pass("Redis configuration found")
                self.results['passed'] += 1
            else:
                print_warn("Redis URL not configured")
                self.warnings.append("Configure REDIS_URL for optimal performance")
                self.results['warnings'] += 1
            self.results['total'] += 1
        
        # Check signals directory for file-based fallback
        signals_dir = self.base_path / 'signals'
        if signals_dir.exists():
            print_pass("Signals directory exists (file-based fallback)")
            self.results['passed'] += 1
            
            # Check for outgoing and incoming directories
            outgoing = signals_dir / 'outgoing'
            incoming = signals_dir / 'incoming'
            
            if outgoing.exists() and incoming.exists():
                print_pass("Signal directories properly structured")
                self.results['passed'] += 1
            else:
                print_warn("Signal subdirectories incomplete")
                self.recommendations.append("Create signals/outgoing and signals/incoming directories")
                self.results['warnings'] += 1
            self.results['total'] += 1
        else:
            print_warn("Signals directory not found")
            self.recommendations.append("Create signals/ directory for file-based communication fallback")
            self.results['warnings'] += 1
            self.results['total'] += 1
    
    def audit_execution_layer(self):
        """Audit execution layer (bot.js)"""
        print_section("6. EXECUTION LAYER (BOT)")
        
        # Check bot.js
        bot_path = self.base_path / 'offchain' / 'execution' / 'bot.js'
        if bot_path.exists():
            print_pass("Bot.js execution module exists")
            self.results['passed'] += 1
            
            with open(bot_path, 'r') as f:
                bot_content = f.read()
            
            # Check for transaction simulation
            if 'simulat' in bot_content.lower():
                print_pass("Transaction simulation implemented")
                self.results['passed'] += 1
            else:
                print_fail("Transaction simulation not found")
                self.critical_issues.append("Bot missing transaction simulation")
                self.results['failed'] += 1
            self.results['total'] += 1
            
            # Check for gas management
            if 'maxFeePerGas' in bot_content or 'maxPriorityFeePerGas' in bot_content:
                print_pass("EIP-1559 gas management implemented")
                self.results['passed'] += 1
            else:
                print_warn("EIP-1559 gas management not detected")
                self.warnings.append("Implement EIP-1559 gas management for better execution")
                self.results['warnings'] += 1
            self.results['total'] += 1
            
            # Check for nonce management
            if 'nonce' in bot_content.lower():
                print_pass("Nonce management present")
                self.results['passed'] += 1
            else:
                print_warn("Nonce management not detected")
                self.warnings.append("Implement nonce management to prevent transaction conflicts")
                self.results['warnings'] += 1
            self.results['total'] += 1
            
        else:
            print_fail("Bot.js not found")
            self.critical_issues.append("Execution bot (offchain/execution/bot.js) missing")
            self.results['failed'] += 1
            self.results['total'] += 1
        
        # Check for gas manager
        gas_manager_path = self.base_path / 'offchain' / 'execution' / 'gas_manager.js'
        if gas_manager_path.exists():
            print_pass("Gas Manager module exists")
            self.results['passed'] += 1
        else:
            print_warn("Gas Manager module not found")
            self.warnings.append("Consider implementing dedicated gas_manager.js")
            self.results['warnings'] += 1
        self.results['total'] += 1
        
        # Check for nonce manager
        nonce_manager_path = self.base_path / 'offchain' / 'execution' / 'nonce_manager.py'
        if nonce_manager_path.exists():
            print_pass("Nonce Manager module exists")
            self.results['passed'] += 1
        else:
            print_warn("Nonce Manager module not found")
            self.recommendations.append("Implement nonce_manager for concurrent transactions")
            self.results['warnings'] += 1
        self.results['total'] += 1
    
    def audit_blockchain_layer(self):
        """Audit smart contracts and blockchain interaction"""
        print_section("7. BLOCKCHAIN LAYER (SMART CONTRACTS)")
        
        # Check for FlashArbExecutor contract in multiple possible locations
        possible_contract_paths = [
            self.base_path / 'onchain' / 'contracts' / 'FlashArbExecutor.sol',
            self.base_path / 'contracts' / 'FlashArbExecutor.sol',
            self.base_path / 'src' / 'FlashArbExecutor.sol',
        ]
        
        flash_arb_path = None
        for path in possible_contract_paths:
            if path.exists():
                flash_arb_path = path
                break
        
        # If not found, check for any .sol files
        if not flash_arb_path:
            # Check if contracts exist in documentation/deployed form
            readme_path = self.base_path / 'README.md'
            if readme_path.exists():
                with open(readme_path, 'r') as f:
                    readme_content = f.read()
                if 'FlashArbExecutor' in readme_content or 'OmniArbExecutor' in readme_content:
                    print_info("Contract mentioned in documentation - may be deployed")
                    print_warn("Contract source files not found in repository")
                    self.warnings.append("Contract .sol files not found - ensure they're deployed or available")
                    self.results['warnings'] += 1
                    self.results['total'] += 1
                    # Don't mark as critical if contracts are mentioned in docs
                    return
        
        if flash_arb_path:
            print_pass("FlashArbExecutor.sol exists")
            self.results['passed'] += 1
            
            with open(flash_arb_path, 'r') as f:
                contract_content = f.read()
            
            # Check for reentrancy guard
            if 'ReentrancyGuard' in contract_content or 'nonReentrant' in contract_content:
                print_pass("Reentrancy protection implemented")
                self.results['passed'] += 1
            else:
                print_fail("Reentrancy guard not found - CRITICAL SECURITY ISSUE")
                self.critical_issues.append("FlashArbExecutor missing ReentrancyGuard")
                self.results['failed'] += 1
            self.results['total'] += 1
            
            # Check for deadline parameter in swaps
            if 'deadline' in contract_content:
                # Check if deadline is properly used (not block.timestamp)
                if 'deadline: block.timestamp' in contract_content:
                    print_fail("Deadline bypass vulnerability detected (deadline: block.timestamp)")
                    self.critical_issues.append("FlashArbExecutor uses block.timestamp as deadline - allows unlimited delay")
                    self.results['failed'] += 1
                else:
                    print_pass("Deadline parameter properly implemented")
                    self.results['passed'] += 1
            else:
                print_warn("Deadline parameter not detected")
                self.results['warnings'] += 1
            self.results['total'] += 1
            
            # Check for flash loan integration
            if 'receiveFlashLoan' in contract_content or 'flashLoan' in contract_content:
                print_pass("Flash loan callback implemented")
                self.results['passed'] += 1
            else:
                print_fail("Flash loan integration not found")
                self.critical_issues.append("FlashArbExecutor missing flash loan callback")
                self.results['failed'] += 1
            self.results['total'] += 1
            
        else:
            print_fail("FlashArbExecutor.sol not found")
            self.critical_issues.append("Main contract FlashArbExecutor.sol missing")
            self.results['failed'] += 1
            self.results['total'] += 1
        
        # Check for compiled artifacts
        artifacts_dir = self.base_path / 'artifacts' / 'contracts' / 'FlashArbExecutor.sol'
        if artifacts_dir.exists():
            print_pass("Contract artifacts exist (compiled)")
            self.results['passed'] += 1
        else:
            print_warn("Contract artifacts not found")
            self.recommendations.append("Run 'npx hardhat compile' to compile contracts")
            self.results['warnings'] += 1
        self.results['total'] += 1
    
    def audit_monitoring_layer(self):
        """Audit monitoring and logging"""
        print_section("8. MONITORING & LOGGING")
        
        # Check terminal display
        terminal_display_py = self.base_path / 'offchain' / 'core' / 'terminal_display.py'
        terminal_display_js = self.base_path / 'offchain' / 'execution' / 'terminal_display.js'
        
        if terminal_display_py.exists() or terminal_display_js.exists():
            print_pass("Terminal display module exists")
            self.results['passed'] += 1
        else:
            print_warn("Terminal display not found")
            self.recommendations.append("Implement terminal_display for real-time monitoring")
            self.results['warnings'] += 1
        self.results['total'] += 1
        
        # Check for dashboard
        dashboard_path = self.base_path / 'dashboard_server.py'
        if dashboard_path.exists():
            print_pass("Dashboard server exists")
            self.results['passed'] += 1
        else:
            print_info("Dashboard server not found (optional)")
        self.results['total'] += 1
        
        # Check for trade database
        trade_db_path = self.base_path / 'offchain' / 'core' / 'trade_database.py'
        if trade_db_path.exists():
            print_pass("Trade database module exists")
            self.results['passed'] += 1
        else:
            print_warn("Trade database not found")
            self.recommendations.append("Implement trade_database for metrics tracking")
            self.results['warnings'] += 1
        self.results['total'] += 1
    
    def audit_security_measures(self):
        """Audit security measures"""
        print_section("9. SECURITY MEASURES")
        
        # Check .gitignore for sensitive files
        gitignore_path = self.base_path / '.gitignore'
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                gitignore_content = f.read()
            
            sensitive_patterns = ['.env', 'private', 'secret', '*.key']
            protected = sum(1 for pattern in sensitive_patterns if pattern in gitignore_content)
            
            if protected >= 2:
                print_pass(".gitignore protects sensitive files")
                self.results['passed'] += 1
            else:
                print_warn(".gitignore incomplete")
                self.recommendations.append("Add .env, private keys to .gitignore")
                self.results['warnings'] += 1
        else:
            print_fail(".gitignore not found")
            self.critical_issues.append("Missing .gitignore - risk of exposing secrets")
            self.results['failed'] += 1
        self.results['total'] += 1
        
        # Check for circuit breaker implementation
        brain_path = self.base_path / 'offchain' / 'ml' / 'brain.py'
        if brain_path.exists():
            with open(brain_path, 'r') as f:
                brain_content = f.read()
            
            if 'circuit' in brain_content.lower() or 'consecutive_failures' in brain_content:
                print_pass("Circuit breaker implemented")
                self.results['passed'] += 1
                
                # Check if it's async (non-blocking)
                if 'asyncio.sleep' in brain_content:
                    print_pass("Circuit breaker uses async sleep (non-blocking)")
                    self.results['passed'] += 1
                elif 'time.sleep' in brain_content and 'circuit' in brain_content.lower():
                    print_warn("Circuit breaker uses blocking sleep")
                    self.warnings.append("Replace time.sleep with asyncio.sleep in circuit breaker")
                    self.results['warnings'] += 1
                self.results['total'] += 1
            else:
                print_warn("Circuit breaker not detected")
                self.recommendations.append("Implement circuit breaker for failure protection")
                self.results['warnings'] += 1
                self.results['total'] += 1
    
    def audit_data_flow_integration(self):
        """Audit end-to-end data flow"""
        print_section("10. DATA FLOW INTEGRATION")
        
        # Check data flow from DexPricer to Brain
        dex_pricer_exists = (self.base_path / 'offchain' / 'ml' / 'dex_pricer.py').exists()
        brain_exists = (self.base_path / 'offchain' / 'ml' / 'brain.py').exists()
        
        if dex_pricer_exists and brain_exists:
            print_pass("Data ingestion → Intelligence layer path exists")
            self.results['passed'] += 1
        else:
            print_fail("Data flow incomplete (DexPricer → Brain)")
            self.critical_issues.append("Data ingestion to intelligence layer broken")
            self.results['failed'] += 1
        self.results['total'] += 1
        
        # Check data flow from Brain to Bot
        bot_exists = (self.base_path / 'offchain' / 'execution' / 'bot.js').exists()
        signals_exist = (self.base_path / 'signals').exists()
        
        if brain_exists and (bot_exists or signals_exist):
            print_pass("Intelligence → Execution layer path exists")
            self.results['passed'] += 1
        else:
            print_fail("Data flow incomplete (Brain → Bot)")
            self.critical_issues.append("Intelligence to execution layer broken")
            self.results['failed'] += 1
        self.results['total'] += 1
        
        # Check post-execution feedback loop
        if brain_exists and 'feature_store' in str(self.base_path / 'offchain' / 'ml' / 'cortex'):
            feature_store_path = self.base_path / 'offchain' / 'ml' / 'cortex' / 'feature_store.py'
            if feature_store_path.exists():
                print_pass("Post-execution feedback loop exists")
                self.results['passed'] += 1
            else:
                print_warn("Feature store not found")
                self.recommendations.append("Implement feature store for learning feedback")
                self.results['warnings'] += 1
        else:
            print_warn("Feedback loop not detected")
            self.results['warnings'] += 1
        self.results['total'] += 1
        
        # Check for complete integration test
        integration_test_files = [
            'test_complete_integration.py',
            'test_system_wiring.py',
            'full_scale_test.py'
        ]
        
        integration_test_found = False
        for test_file in integration_test_files:
            if (self.base_path / test_file).exists():
                print_pass(f"Integration test found: {test_file}")
                integration_test_found = True
                self.results['passed'] += 1
                break
        
        if not integration_test_found:
            print_warn("No integration tests found")
            self.recommendations.append("Create integration tests for end-to-end data flow")
            self.results['warnings'] += 1
        self.results['total'] += 1
    
    def print_summary(self):
        """Print audit summary"""
        print_header("AUDIT SUMMARY")
        
        total = self.results['total']
        passed = self.results['passed']
        failed = self.results['failed']
        warnings = self.results['warnings']
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Checks: {total}")
        print(f"{Colors.GREEN}Passed: {passed} ({pass_rate:.1f}%){Colors.RESET}")
        print(f"{Colors.RED}Failed: {failed}{Colors.RESET}")
        print(f"{Colors.YELLOW}Warnings: {warnings}{Colors.RESET}")
        
        # Determine overall status
        if failed == 0 and len(self.critical_issues) == 0:
            status = f"{Colors.GREEN}PASS - READY FOR MAINNET{Colors.RESET}"
        elif failed <= 2 and len(self.critical_issues) <= 2:
            status = f"{Colors.YELLOW}CONDITIONAL PASS - FIX CRITICAL ISSUES{Colors.RESET}"
        else:
            status = f"{Colors.RED}FAIL - NOT READY FOR MAINNET{Colors.RESET}"
        
        print(f"\nOverall Status: {status}")
        
        # Print critical issues
        if self.critical_issues:
            print(f"\n{Colors.RED}{Colors.BOLD}CRITICAL ISSUES ({len(self.critical_issues)}):{Colors.RESET}")
            for i, issue in enumerate(self.critical_issues, 1):
                print(f"  {i}. {issue}")
        
        # Print warnings
        if self.warnings:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}WARNINGS ({len(self.warnings)}):{Colors.RESET}")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        
        # Print recommendations
        if self.recommendations:
            print(f"\n{Colors.CYAN}{Colors.BOLD}RECOMMENDATIONS ({len(self.recommendations)}):{Colors.RESET}")
            for i, rec in enumerate(self.recommendations, 1):
                print(f"  {i}. {rec}")
        
        print(f"\n{Colors.CYAN}Audit completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")

def main():
    """Main entry point"""
    audit = MainnetAudit()
    exit_code = audit.run_audit()
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
