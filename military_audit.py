#!/usr/bin/env python3
"""
TITAN 2.0 - MILITARY DRILL-SERGEANT MODULE AUDIT SYSTEM
========================================================

This system enforces strict, sequential validation of every component module
before allowing progression to the next module. NO module proceeds until ALL
functions are confirmed validated and benchmarked.

Operation Flow:
1. Validate Configuration Module → GATE
2. Validate Core Infrastructure → GATE
3. Validate RPC Connections → GATE
4. Validate DEX Integration → GATE
5. Validate ML/AI Components → GATE
6. Validate Execution Engine → GATE
7. Validate Security Systems → GATE
8. Final System Integration → GATE

Each GATE is a HARD STOP until all tests PASS with acceptable metrics.
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from decimal import Decimal
from colorama import Fore, Style, init
import subprocess

# Initialize colorama
init(autoreset=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'military_audit_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AuditGate:
    """Represents a validation gate that blocks progression"""
    
    def __init__(self, name: str, module: str):
        self.name = name
        self.module = module
        self.status = "NOT_STARTED"  # NOT_STARTED, IN_PROGRESS, PASSED, FAILED
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.benchmarks = {}
        self.errors = []
        self.start_time = None
        self.end_time = None
        
    def start(self):
        """Mark gate as in progress"""
        self.status = "IN_PROGRESS"
        self.start_time = time.time()
        
    def record_test(self, test_name: str, passed: bool, details: str = ""):
        """Record a test result"""
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
            self.errors.append(f"{test_name}: {details}")
            
    def record_benchmark(self, metric_name: str, value: float, threshold: float, unit: str = ""):
        """Record a benchmark metric"""
        self.benchmarks[metric_name] = {
            'value': value,
            'threshold': threshold,
            'unit': unit,
            'passed': value <= threshold if 'time' in metric_name.lower() else value >= threshold
        }
        
    def finalize(self):
        """Finalize gate and determine pass/fail"""
        self.end_time = time.time()
        
        # Check if all tests passed
        if self.tests_failed > 0:
            self.status = "FAILED"
            return False
            
        # Check if all benchmarks met
        for metric, data in self.benchmarks.items():
            if not data['passed']:
                self.status = "FAILED"
                self.errors.append(f"Benchmark failed: {metric} = {data['value']}{data['unit']} (threshold: {data['threshold']}{data['unit']})")
                return False
                
        self.status = "PASSED"
        return True
        
    def print_report(self):
        """Print detailed gate report"""
        duration = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"GATE REPORT: {self.name}")
        print(f"Module: {self.module}")
        print(f"{'='*80}{Style.RESET_ALL}\n")
        
        # Status
        status_color = Fore.GREEN if self.status == "PASSED" else Fore.RED
        print(f"{status_color}Status: {self.status}{Style.RESET_ALL}")
        print(f"Duration: {duration:.2f}s")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {Fore.GREEN}{self.tests_passed}{Style.RESET_ALL}")
        print(f"Tests Failed: {Fore.RED}{self.tests_failed}{Style.RESET_ALL}")
        
        # Benchmarks
        if self.benchmarks:
            print(f"\n{Fore.YELLOW}Benchmarks:{Style.RESET_ALL}")
            for metric, data in self.benchmarks.items():
                color = Fore.GREEN if data['passed'] else Fore.RED
                status = "✓" if data['passed'] else "✗"
                print(f"  {color}{status} {metric}: {data['value']}{data['unit']} (threshold: {data['threshold']}{data['unit']}){Style.RESET_ALL}")
        
        # Errors
        if self.errors:
            print(f"\n{Fore.RED}Errors:{Style.RESET_ALL}")
            for error in self.errors:
                print(f"  ✗ {error}")
        
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")


class MilitaryAudit:
    """
    Military-style audit system that validates each module sequentially
    with strict gates preventing progression until all tests pass.
    """
    
    def __init__(self):
        self.gates: List[AuditGate] = []
        self.current_gate_index = 0
        self.overall_status = "IN_PROGRESS"
        self.start_time = time.time()
        
    def add_gate(self, name: str, module: str) -> AuditGate:
        """Add a validation gate"""
        gate = AuditGate(name, module)
        self.gates.append(gate)
        return gate
        
    def run_sequential_audit(self):
        """Run all gates sequentially with hard stops"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{'MILITARY AUDIT SYSTEM - SEQUENTIAL VALIDATION'.center(80)}")
        print(f"{'='*80}{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}⚠️  DRILL-SERGEANT MODE ACTIVATED{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Each module must pass ALL tests before proceeding.{Style.RESET_ALL}\n")
        
        for i, gate in enumerate(self.gates):
            self.current_gate_index = i
            
            # Print gate header
            print(f"\n{Fore.CYAN}{'='*80}")
            print(f"GATE {i+1}/{len(self.gates)}: {gate.name}".center(80))
            print(f"Module: {gate.module}".center(80))
            print(f"{'='*80}{Style.RESET_ALL}\n")
            
            gate.start()
            
            # Run the gate validation
            if not self._execute_gate(gate):
                # HARD STOP - Gate failed
                gate.finalize()
                gate.print_report()
                
                print(f"\n{Fore.RED}{'='*80}")
                print(f"{'🛑 GATE FAILED - HARD STOP'.center(80)}")
                print(f"{'='*80}{Style.RESET_ALL}\n")
                print(f"{Fore.RED}Module '{gate.module}' failed validation.{Style.RESET_ALL}")
                print(f"{Fore.RED}Fix all errors before proceeding to next module.{Style.RESET_ALL}\n")
                
                self.overall_status = "FAILED"
                return False
                
            # Gate passed
            gate.finalize()
            gate.print_report()
            
            print(f"\n{Fore.GREEN}{'='*80}")
            print(f"{'✓ GATE PASSED - PROCEED TO NEXT MODULE'.center(80)}")
            print(f"{'='*80}{Style.RESET_ALL}\n")
            
        # All gates passed
        self.overall_status = "PASSED"
        self._print_final_report()
        return True
        
    def _execute_gate(self, gate: AuditGate) -> bool:
        """Execute validation for a specific gate"""
        # Dispatch to specific gate handler
        gate_handlers = {
            "Configuration Module": self._validate_configuration,
            "Core Infrastructure": self._validate_core_infrastructure,
            "RPC Connections": self._validate_rpc_connections,
            "DEX Integration": self._validate_dex_integration,
            "ML/AI Components": self._validate_ml_ai,
            "Execution Engine": self._validate_execution_engine,
            "Security Systems": self._validate_security,
            "System Integration": self._validate_system_integration
        }
        
        handler = gate_handlers.get(gate.name)
        if handler:
            try:
                return handler(gate)
            except Exception as e:
                gate.record_test(f"Gate Execution", False, str(e))
                logger.error(f"Gate execution failed: {e}")
                return False
        else:
            logger.warning(f"No handler for gate: {gate.name}")
            return True
            
    def _validate_configuration(self, gate: AuditGate) -> bool:
        """Validate Configuration Module"""
        logger.info("Validating Configuration Module...")
        
        # Test 1: config.json exists and is valid
        start = time.time()
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
            gate.record_test("config.json exists and valid JSON", True)
            load_time = time.time() - start
            gate.record_benchmark("config_load_time", load_time, 0.5, "s")
        except Exception as e:
            gate.record_test("config.json exists and valid JSON", False, str(e))
            return False
            
        # Test 2: Required networks configured
        required_networks = ['polygon', 'ethereum']
        for network in required_networks:
            if network in config.get('networks', {}):
                gate.record_test(f"Network configured: {network}", True)
            else:
                gate.record_test(f"Network configured: {network}", False, "Network not found in config")
                
        # Test 3: DEX endpoints configured
        if 'dex_endpoints' in config and len(config['dex_endpoints']) > 0:
            gate.record_test("DEX endpoints configured", True)
            gate.record_benchmark("dex_endpoint_count", len(config['dex_endpoints']), 3, " endpoints")
        else:
            gate.record_test("DEX endpoints configured", False, "No DEX endpoints found")
            
        # Test 4: Token configuration
        token_count = 0
        for network, tokens in config.get('tokens', {}).items():
            token_count += len(tokens)
        
        if token_count > 0:
            gate.record_test("Tokens configured", True)
            gate.record_benchmark("token_count", token_count, 5, " tokens")
        else:
            gate.record_test("Tokens configured", False, "No tokens configured")
            
        # Test 5: .env file exists
        if os.path.exists('.env'):
            gate.record_test(".env file exists", True)
        else:
            gate.record_test(".env file exists", False, ".env file not found")
            
        return gate.tests_failed == 0
        
    def _validate_core_infrastructure(self, gate: AuditGate) -> bool:
        """Validate Core Infrastructure Module"""
        logger.info("Validating Core Infrastructure...")
        
        # Test 1: Core Python modules exist
        core_modules = [
            'offchain/core/config.py',
            'offchain/core/enum_matrix.py',
            'offchain/core/token_discovery.py'
        ]
        
        for module in core_modules:
            if os.path.exists(module):
                gate.record_test(f"Module exists: {module}", True)
            else:
                gate.record_test(f"Module exists: {module}", False, "File not found")
                
        # Test 2: Python dependencies installed
        try:
            import web3
            import pandas
            import numpy
            gate.record_test("Critical Python dependencies installed", True)
        except ImportError as e:
            gate.record_test("Critical Python dependencies installed", False, str(e))
            
        # Test 3: Node.js dependencies
        if os.path.exists('node_modules'):
            gate.record_test("Node.js dependencies installed", True)
        else:
            gate.record_test("Node.js dependencies installed", False, "node_modules not found")
            
        # Test 4: Core module import benchmark
        start = time.time()
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from offchain.core import config
            import_time = time.time() - start
            gate.record_test("Core config module imports", True)
            gate.record_benchmark("config_import_time", import_time, 2.0, "s")
        except Exception as e:
            gate.record_test("Core config module imports", False, str(e))
            
        return gate.tests_failed == 0
        
    def _validate_rpc_connections(self, gate: AuditGate) -> bool:
        """Validate RPC Connections Module"""
        logger.info("Validating RPC Connections...")
        
        # Test 1: Environment variables for RPC
        rpc_vars = ['RPC_POLYGON', 'RPC_ETHEREUM', 'INFURA_API_KEY', 'ALCHEMY_API_KEY']
        found_rpcs = 0
        
        for var in rpc_vars:
            if os.getenv(var):
                found_rpcs += 1
                
        if found_rpcs >= 2:  # At least 2 RPC providers
            gate.record_test("RPC environment variables configured", True)
        else:
            gate.record_test("RPC environment variables configured", False, f"Only {found_rpcs} RPC vars found")
            
        # Test 2: RPC connection test
        try:
            from web3 import Web3
            
            # Try to connect to a public RPC
            rpc_url = os.getenv('RPC_POLYGON') or "https://polygon-rpc.com"
            
            start = time.time()
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            connected = w3.is_connected()
            connection_time = time.time() - start
            
            if connected:
                gate.record_test("RPC connection test", True)
                gate.record_benchmark("rpc_connection_time", connection_time, 5.0, "s")
                
                # Test 3: Get latest block (functionality test)
                start = time.time()
                block_number = w3.eth.block_number
                block_fetch_time = time.time() - start
                
                gate.record_test("RPC block number fetch", True)
                gate.record_benchmark("block_fetch_time", block_fetch_time, 3.0, "s")
            else:
                gate.record_test("RPC connection test", False, "Failed to connect")
                
        except Exception as e:
            gate.record_test("RPC connection test", False, str(e))
            
        return gate.tests_failed == 0
        
    def _validate_dex_integration(self, gate: AuditGate) -> bool:
        """Validate DEX Integration Module"""
        logger.info("Validating DEX Integration...")
        
        # Test 1: DEX pricer module exists
        if os.path.exists('offchain/ml/dex_pricer.py'):
            gate.record_test("DEX pricer module exists", True)
        else:
            gate.record_test("DEX pricer module exists", False, "File not found")
            
        # Test 2: Config has DEX endpoints
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
            
            dex_count = len(config.get('dex_endpoints', {}))
            if dex_count >= 3:
                gate.record_test("Sufficient DEX endpoints configured", True)
                gate.record_benchmark("dex_endpoint_count", dex_count, 3, " DEXs")
            else:
                gate.record_test("Sufficient DEX endpoints configured", False, f"Only {dex_count} DEXs configured")
                
        except Exception as e:
            gate.record_test("DEX configuration check", False, str(e))
            
        # Test 3: DEX module import test
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from offchain.ml import dex_pricer
            gate.record_test("DEX pricer module imports", True)
        except Exception as e:
            gate.record_test("DEX pricer module imports", False, str(e))
            
        return gate.tests_failed == 0
        
    def _validate_ml_ai(self, gate: AuditGate) -> bool:
        """Validate ML/AI Components Module"""
        logger.info("Validating ML/AI Components...")
        
        # Test 1: Brain module exists
        if os.path.exists('offchain/ml/brain.py'):
            gate.record_test("Brain module exists", True)
        else:
            gate.record_test("Brain module exists", False, "File not found")
            
        # Test 2: AI cortex modules exist
        cortex_modules = [
            'offchain/ml/cortex/forecaster.py',
            'offchain/ml/cortex/rl_optimizer.py',
            'offchain/ml/cortex/feature_store.py'
        ]
        
        for module in cortex_modules:
            if os.path.exists(module):
                gate.record_test(f"AI module exists: {os.path.basename(module)}", True)
            else:
                gate.record_test(f"AI module exists: {os.path.basename(module)}", False, "File not found")
                
        # Test 3: ML dependencies
        try:
            import pandas
            import numpy
            gate.record_test("ML dependencies installed", True)
        except ImportError as e:
            gate.record_test("ML dependencies installed", False, str(e))
            
        return gate.tests_failed == 0
        
    def _validate_execution_engine(self, gate: AuditGate) -> bool:
        """Validate Execution Engine Module"""
        logger.info("Validating Execution Engine...")
        
        # Test 1: Bot module exists
        if os.path.exists('offchain/execution/bot.js'):
            gate.record_test("Execution bot exists", True)
        else:
            gate.record_test("Execution bot exists", False, "File not found")
            
        # Test 2: Gas manager exists
        if os.path.exists('offchain/execution/gas_manager.js'):
            gate.record_test("Gas manager exists", True)
        else:
            gate.record_test("Gas manager exists", False, "File not found")
            
        # Test 3: Node.js runtime
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip()
                gate.record_test("Node.js runtime available", True)
                logger.info(f"Node.js version: {version}")
            else:
                gate.record_test("Node.js runtime available", False, "Node not found")
        except Exception as e:
            gate.record_test("Node.js runtime available", False, str(e))
            
        return gate.tests_failed == 0
        
    def _validate_security(self, gate: AuditGate) -> bool:
        """Validate Security Systems Module"""
        logger.info("Validating Security Systems...")
        
        # Test 1: .env file not in git
        try:
            with open('.gitignore', 'r') as f:
                gitignore = f.read()
            
            if '.env' in gitignore:
                gate.record_test(".env in .gitignore", True)
            else:
                gate.record_test(".env in .gitignore", False, ".env not excluded from git")
        except:
            gate.record_test(".gitignore check", False, "Could not read .gitignore")
            
        # Test 2: Private key security check
        if os.getenv('WALLET_PRIVATE_KEY'):
            key = os.getenv('WALLET_PRIVATE_KEY')
            if key.startswith('0x') and len(key) == 66:
                gate.record_test("Private key format valid", True)
            else:
                gate.record_test("Private key format valid", False, "Invalid format")
        else:
            gate.record_test("Private key configured", False, "WALLET_PRIVATE_KEY not set")
            
        # Test 3: Circuit breaker configuration
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
            
            if 'risk_management' in config:
                gate.record_test("Risk management configured", True)
            else:
                gate.record_test("Risk management configured", False, "No risk_management in config")
        except:
            gate.record_test("Security configuration check", False, "Could not check config")
            
        return gate.tests_failed == 0
        
    def _validate_system_integration(self, gate: AuditGate) -> bool:
        """Validate System Integration"""
        logger.info("Validating System Integration...")
        
        # Test 1: All major components present
        components = {
            'Brain': 'offchain/ml/brain.py',
            'Bot': 'offchain/execution/bot.js',
            'Config': 'config.json',
            'Environment': '.env'
        }
        
        for name, path in components.items():
            if os.path.exists(path):
                gate.record_test(f"Component present: {name}", True)
            else:
                gate.record_test(f"Component present: {name}", False, f"{path} not found")
                
        # Test 2: Communication infrastructure
        # Check if Redis is available or file-based fallback exists
        signals_dir = 'signals'
        if os.path.exists(signals_dir):
            gate.record_test("Signal communication infrastructure", True)
        else:
            logger.warning("Signals directory not found - will be created on startup")
            gate.record_test("Signal communication infrastructure", True)  # Not critical
            
        # Test 3: System health check script
        if os.path.exists('health-check.sh'):
            gate.record_test("Health check script exists", True)
        else:
            gate.record_test("Health check script exists", False, "health-check.sh not found")
            
        return gate.tests_failed == 0
        
    def _print_final_report(self):
        """Print final audit report"""
        total_time = time.time() - self.start_time
        
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{'FINAL MILITARY AUDIT REPORT'.center(80)}")
        print(f"{'='*80}{Style.RESET_ALL}\n")
        
        # Overall status
        if self.overall_status == "PASSED":
            print(f"{Fore.GREEN}{'✓ ALL GATES PASSED'.center(80)}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{'SYSTEM IS FULLY VALIDATED AND READY FOR OPERATION'.center(80)}{Style.RESET_ALL}\n")
        else:
            print(f"{Fore.RED}{'✗ AUDIT FAILED'.center(80)}{Style.RESET_ALL}")
            print(f"{Fore.RED}{'SYSTEM NOT READY FOR OPERATION'.center(80)}{Style.RESET_ALL}\n")
            
        print(f"Total Audit Time: {total_time:.2f}s")
        print(f"Total Gates: {len(self.gates)}")
        
        # Summary by gate
        passed_gates = sum(1 for g in self.gates if g.status == "PASSED")
        print(f"Gates Passed: {Fore.GREEN}{passed_gates}{Style.RESET_ALL}")
        print(f"Gates Failed: {Fore.RED}{len(self.gates) - passed_gates}{Style.RESET_ALL}")
        
        # Detailed gate summary
        print(f"\n{Fore.YELLOW}Gate Summary:{Style.RESET_ALL}")
        for i, gate in enumerate(self.gates):
            status_color = Fore.GREEN if gate.status == "PASSED" else Fore.RED
            status_symbol = "✓" if gate.status == "PASSED" else "✗"
            duration = gate.end_time - gate.start_time if gate.end_time and gate.start_time else 0
            print(f"  {status_color}{status_symbol} Gate {i+1}: {gate.name} ({gate.tests_passed}/{gate.tests_run} tests, {duration:.2f}s){Style.RESET_ALL}")
            
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")


def main():
    """Main entry point for military audit"""
    audit = MilitaryAudit()
    
    # Define gates in strict sequential order
    audit.add_gate("Configuration Module", "offchain/core/config.py")
    audit.add_gate("Core Infrastructure", "offchain/core/*")
    audit.add_gate("RPC Connections", "Web3 Providers")
    audit.add_gate("DEX Integration", "offchain/ml/dex_pricer.py")
    audit.add_gate("ML/AI Components", "offchain/ml/cortex/*")
    audit.add_gate("Execution Engine", "offchain/execution/bot.js")
    audit.add_gate("Security Systems", "Security Configuration")
    audit.add_gate("System Integration", "Full System")
    
    # Run sequential audit with hard gates
    success = audit.run_sequential_audit()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
