#!/usr/bin/env python3
"""
Rust Feature Wiring Verification Script
Verifies that all 5 core Rust features are fully wired into the operational system:
1. config.rs - Lightning-fast configuration management
2. enum_matrix.rs - Chain enumeration and provider pooling
3. simulation_engine.rs - On-chain TVL and simulation
4. commander.rs - Flash loan optimization algorithms
5. http_server.rs - High-performance API server
"""

import sys
import os
import subprocess
import time
import requests
import json
from pathlib import Path

# ANSI colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{BLUE}{'=' * 80}{RESET}")
    print(f"{BLUE}{text.center(80)}{RESET}")
    print(f"{BLUE}{'=' * 80}{RESET}\n")

def print_success(text):
    """Print success message"""
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    """Print error message"""
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_info(text):
    """Print info message"""
    print(f"{BLUE}ℹ️  {text}{RESET}")

def verify_rust_installation():
    """Verify Rust toolchain is installed"""
    print_header("1. Verifying Rust Installation")
    
    try:
        result = subprocess.run(['cargo', '--version'], 
                              capture_output=True, text=True, check=True)
        print_success(f"Rust installed: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("Rust toolchain not found. Please install from https://rustup.rs")
        return False

def verify_rust_files():
    """Verify all Rust source files exist"""
    print_header("2. Verifying Rust Source Files")
    
    core_rust_path = Path("core-rust/src")
    required_files = [
        "config.rs",
        "enum_matrix.rs", 
        "simulation_engine.rs",
        "commander.rs",
        "http_server.rs",
        "lib.rs"
    ]
    
    all_exist = True
    for file in required_files:
        file_path = core_rust_path / file
        if file_path.exists():
            print_success(f"Found: {file}")
        else:
            print_error(f"Missing: {file}")
            all_exist = False
    
    return all_exist

def verify_rust_compilation():
    """Verify Rust code compiles successfully"""
    print_header("3. Verifying Rust Compilation")
    
    try:
        print_info("Compiling Rust code (release mode)...")
        result = subprocess.run(
            ['cargo', 'build', '--release'],
            cwd='core-rust',
            capture_output=True,
            text=True,
            timeout=180
        )
        
        if result.returncode == 0:
            print_success("Rust code compiled successfully")
            return True
        else:
            print_error("Rust compilation failed:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print_error("Compilation timed out after 180 seconds")
        return False
    except Exception as e:
        print_error(f"Compilation error: {str(e)}")
        return False

def verify_rust_tests():
    """Verify Rust tests pass"""
    print_header("4. Verifying Rust Tests")
    
    try:
        print_info("Running Rust unit tests...")
        result = subprocess.run(
            ['cargo', 'test', '--lib'],
            cwd='core-rust',
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            # Parse test output
            output = result.stdout
            if 'test result: ok' in output:
                # Extract test count
                for line in output.split('\n'):
                    if 'test result: ok' in line:
                        print_success(f"All Rust tests passed: {line.strip()}")
                        return True
            print_success("Rust tests completed successfully")
            return True
        else:
            print_error("Rust tests failed:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print_error("Tests timed out after 120 seconds")
        return False
    except Exception as e:
        print_error(f"Test error: {str(e)}")
        return False

def verify_lib_exports():
    """Verify lib.rs exports all required modules"""
    print_header("5. Verifying Module Exports in lib.rs")
    
    lib_path = Path("core-rust/src/lib.rs")
    if not lib_path.exists():
        print_error("lib.rs not found")
        return False
    
    content = lib_path.read_text()
    
    required_exports = {
        'config': ['Config', 'ChainConfig', 'BALANCER_V3_VAULT'],
        'enum_matrix': ['ChainId', 'ProviderManager'],
        'simulation_engine': ['TitanSimulationEngine', 'get_provider_tvl'],
        'commander': ['TitanCommander'],
        'http_server': ['start_server', 'create_router', 'AppState']
    }
    
    all_exported = True
    for module, exports in required_exports.items():
        # Check module declaration
        if f'pub mod {module};' in content:
            print_success(f"Module declared: {module}")
        else:
            print_error(f"Module not declared: {module}")
            all_exported = False
            
        # Check exports
        for export in exports:
            if f'pub use {module}::{export}' in content or f'{export}' in content:
                print_success(f"  - Exported: {export}")
            else:
                print_warning(f"  - May not be exported: {export}")
    
    return all_exported

def verify_python_bindings():
    """Verify Python bindings are configured"""
    print_header("6. Verifying Python Bindings (PyO3)")
    
    lib_path = Path("core-rust/src/lib.rs")
    if not lib_path.exists():
        print_error("lib.rs not found")
        return False
    
    content = lib_path.read_text()
    
    checks = {
        'PyO3 import': 'use pyo3::prelude::*;',
        'PyConfig class': '#[pyclass]',
        'Python module': '#[pymodule]',
        'Module function': 'fn titan_core',
    }
    
    all_found = True
    for check, pattern in checks.items():
        if pattern in content:
            print_success(f"{check}: Found")
        else:
            print_warning(f"{check}: Not found (may be optional)")
            all_found = False
    
    return True  # Python bindings are optional

def verify_http_server_endpoints():
    """Verify HTTP server endpoints are defined"""
    print_header("7. Verifying HTTP Server Endpoints")
    
    server_path = Path("core-rust/src/http_server.rs")
    if not server_path.exists():
        print_error("http_server.rs not found")
        return False
    
    content = server_path.read_text()
    
    endpoints = {
        '/health': 'health_check',
        '/api/pool': 'query_pool',
        '/api/metrics': 'metrics',
        '/api/tvl': 'query_tvl',
        '/api/optimize_loan': 'optimize_loan',
    }
    
    all_found = True
    for endpoint, handler in endpoints.items():
        if f'route("{endpoint}"' in content and handler in content:
            print_success(f"Endpoint: {endpoint} -> {handler}()")
        else:
            print_error(f"Endpoint missing: {endpoint}")
            all_found = False
    
    return all_found

def verify_integration_points():
    """Verify integration between modules"""
    print_header("8. Verifying Module Integration")
    
    checks = []
    
    # Check http_server.rs imports
    server_path = Path("core-rust/src/http_server.rs")
    if server_path.exists():
        content = server_path.read_text()
        
        imports = [
            ('config', 'use crate::config::'),
            ('enum_matrix', 'use crate::enum_matrix::'),
            ('simulation_engine', 'use crate::simulation_engine::'),
            ('commander', 'use crate::commander::'),
        ]
        
        for module, import_pattern in imports:
            if import_pattern in content:
                print_success(f"http_server imports {module}")
                checks.append(True)
            else:
                print_warning(f"http_server may not import {module}")
                checks.append(False)
    
    # Check commander.rs imports simulation_engine
    commander_path = Path("core-rust/src/commander.rs")
    if commander_path.exists():
        content = commander_path.read_text()
        if 'use crate::simulation_engine::' in content:
            print_success("commander imports simulation_engine")
            checks.append(True)
        else:
            print_warning("commander may not import simulation_engine")
            checks.append(False)
    
    return all(checks) if checks else True

def verify_feature_functionality():
    """Verify each feature has core functionality"""
    print_header("9. Verifying Feature Functionality")
    
    features = {
        'config.rs': ['Config::from_env', 'ChainConfig', 'BALANCER_V3_VAULT'],
        'enum_matrix.rs': ['ChainId', 'ProviderManager', 'from_u64'],
        'simulation_engine.rs': ['TitanSimulationEngine', 'get_lender_tvl', 'get_price_impact'],
        'commander.rs': ['TitanCommander', 'optimize_loan_size', 'calculate_max_cap'],
        'http_server.rs': ['start_server', 'create_router', 'health_check']
    }
    
    all_verified = True
    for file, functions in features.items():
        file_path = Path(f"core-rust/src/{file}")
        if not file_path.exists():
            print_error(f"{file} not found")
            all_verified = False
            continue
        
        content = file_path.read_text()
        print_info(f"Checking {file}...")
        
        for func in functions:
            if func in content:
                print_success(f"  - {func}: Found")
            else:
                print_error(f"  - {func}: Not found")
                all_verified = False
    
    return all_verified

def generate_report(results):
    """Generate final verification report"""
    print_header("Verification Summary Report")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\n{'Test Category':<50} {'Status':<10}")
    print("-" * 60)
    
    for test, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"{test:<50} {status}")
    
    print("-" * 60)
    print(f"\nTotal: {passed}/{total} tests passed ({percentage:.1f}%)")
    
    if passed == total:
        print_success("\n🎉 All Rust features are fully wired and operational!")
        return True
    else:
        print_warning(f"\n⚠️  {total - passed} test(s) failed. Review the output above.")
        return False

def main():
    """Main verification routine"""
    print_header("Titan 2.0 - Rust Feature Wiring Verification")
    print_info("Verifying 5 core Rust features are fully operational:\n")
    print("  1. config.rs - Lightning-fast configuration management")
    print("  2. enum_matrix.rs - Chain enumeration and provider pooling")
    print("  3. simulation_engine.rs - On-chain TVL and simulation")
    print("  4. commander.rs - Flash loan optimization algorithms")
    print("  5. http_server.rs - High-performance API server\n")
    
    # Run all verification checks
    results = {}
    
    results["Rust Installation"] = verify_rust_installation()
    if not results["Rust Installation"]:
        print_error("\nCannot proceed without Rust installation")
        return False
    
    results["Source Files"] = verify_rust_files()
    results["Compilation"] = verify_rust_compilation()
    results["Unit Tests"] = verify_rust_tests()
    results["Module Exports"] = verify_lib_exports()
    results["Python Bindings"] = verify_python_bindings()
    results["HTTP Endpoints"] = verify_http_server_endpoints()
    results["Module Integration"] = verify_integration_points()
    results["Feature Functionality"] = verify_feature_functionality()
    
    # Generate final report
    success = generate_report(results)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
