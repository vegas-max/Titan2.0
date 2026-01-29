#!/usr/bin/env python3
"""
APEX-OMEGA TITAN: SYSTEM CONFIGURATION VALIDATOR
=================================================

Validates that the system is fully equipped and configured for:
1. Real transaction execution
2. Advanced routing (cross-chain, multi-aggregator)
3. Real-time monitoring

This script checks all critical configuration settings and reports
any issues that need to be addressed.
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    """Print section header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'=' * 80}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text:^80}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'=' * 80}{Colors.END}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    """Print info message"""
    print(f"   {text}")

def check_env_var(var_name, expected_value=None, optional=False):
    """Check if environment variable is set and optionally validate its value"""
    value = os.getenv(var_name)
    
    if value is None:
        if optional:
            print_warning(f"{var_name} is not set (optional)")
            return None
        else:
            print_error(f"{var_name} is not set")
            return None
    
    if expected_value is not None:
        if value == expected_value:
            print_success(f"{var_name} = {value}")
            return value
        else:
            print_warning(f"{var_name} = {value} (expected: {expected_value})")
            return value
    else:
        print_success(f"{var_name} = {value}")
        return value

def validate_transaction_execution():
    """Validate transaction execution configuration"""
    print_header("1. TRANSACTION EXECUTION CONFIGURATION")
    
    passed = 0
    failed = 0
    warnings = 0
    
    # Check execution mode
    mode = os.getenv('EXECUTION_MODE', 'PAPER')
    if mode in ['PAPER', 'LIVE']:
        print_success(f"EXECUTION_MODE = {mode}")
        passed += 1
    else:
        print_error(f"EXECUTION_MODE = {mode} (invalid, must be PAPER or LIVE)")
        failed += 1
    
    # Check flash loan configuration
    flash_enabled = os.getenv('FLASH_LOAN_ENABLED', 'true').lower() == 'true'
    if flash_enabled:
        print_success("FLASH_LOAN_ENABLED = true")
        passed += 1
    else:
        print_error("FLASH_LOAN_ENABLED = false (CRITICAL: Must be enabled)")
        failed += 1
    
    # Check simulation enforcement
    enforce_sim = os.getenv('ENFORCE_SIMULATION', 'true').lower() == 'true'
    if enforce_sim:
        print_success("ENFORCE_SIMULATION = true")
        passed += 1
    else:
        print_warning("ENFORCE_SIMULATION = false (Recommended: true for safety)")
        warnings += 1
    
    # Check nonce management
    auto_nonce = os.getenv('AUTO_NONCE_MANAGEMENT', 'true').lower() == 'true'
    if auto_nonce:
        print_success("AUTO_NONCE_MANAGEMENT = true")
        passed += 1
    else:
        print_warning("AUTO_NONCE_MANAGEMENT = false")
        warnings += 1
    
    # Check transaction retry
    retry_attempts = os.getenv('TRANSACTION_RETRY_ATTEMPTS', '3')
    print_success(f"TRANSACTION_RETRY_ATTEMPTS = {retry_attempts}")
    passed += 1
    
    # Check transaction timeout
    timeout = os.getenv('TRANSACTION_TIMEOUT', '180')
    print_success(f"TRANSACTION_TIMEOUT = {timeout}s")
    passed += 1
    
    # Check simulation before execution
    sim_before = os.getenv('SIMULATION_BEFORE_EXECUTION', 'true').lower() == 'true'
    if sim_before:
        print_success("SIMULATION_BEFORE_EXECUTION = true")
        passed += 1
    else:
        print_warning("SIMULATION_BEFORE_EXECUTION = false (Recommended: true)")
        warnings += 1
    
    return passed, failed, warnings

def validate_advanced_routing():
    """Validate advanced routing configuration"""
    print_header("2. ADVANCED ROUTING CONFIGURATION")
    
    passed = 0
    failed = 0
    warnings = 0
    
    # Check cross-chain routing
    cross_chain = os.getenv('ENABLE_CROSS_CHAIN', 'false').lower() == 'true'
    if cross_chain:
        print_success("ENABLE_CROSS_CHAIN = true")
        passed += 1
        
        # Check Li.Fi API key
        lifi_key = os.getenv('LIFI_API_KEY')
        if lifi_key and lifi_key != 'your_lifi_key_here':
            print_success(f"LIFI_API_KEY = {lifi_key[:20]}...")
            passed += 1
        else:
            print_warning("LIFI_API_KEY not configured (optional for free tier)")
            warnings += 1
        
        # Check intent-based bridge preference
        intent_based = os.getenv('PREFER_INTENT_BASED_BRIDGES', 'true').lower() == 'true'
        if intent_based:
            print_success("PREFER_INTENT_BASED_BRIDGES = true")
            passed += 1
        else:
            print_info("PREFER_INTENT_BASED_BRIDGES = false")
            passed += 1
    else:
        print_warning("ENABLE_CROSS_CHAIN = false (Feature not enabled)")
        warnings += 1
    
    # Check multi-aggregator routing
    multi_agg = os.getenv('MULTI_AGGREGATOR_ROUTING', 'false').lower() == 'true'
    if multi_agg:
        print_success("MULTI_AGGREGATOR_ROUTING = true")
        passed += 1
        
        # Check max routing hops
        max_hops = os.getenv('MAX_ROUTING_HOPS', '3')
        print_success(f"MAX_ROUTING_HOPS = {max_hops}")
        passed += 1
    else:
        print_warning("MULTI_AGGREGATOR_ROUTING = false (Feature not enabled)")
        warnings += 1
    
    # Check bridge aggregation
    bridge_agg = os.getenv('ENABLE_BRIDGE_AGGREGATION', 'false').lower() == 'true'
    if bridge_agg:
        print_success("ENABLE_BRIDGE_AGGREGATION = true")
        passed += 1
    else:
        print_warning("ENABLE_BRIDGE_AGGREGATION = false (Feature not enabled)")
        warnings += 1
    
    # Check route intelligence
    route_intel = os.getenv('ROUTE_INTELLIGENCE_ENABLED', 'true').lower() == 'true'
    if route_intel:
        print_success("ROUTE_INTELLIGENCE_ENABLED = true")
        passed += 1
    else:
        print_warning("ROUTE_INTELLIGENCE_ENABLED = false")
        warnings += 1
    
    return passed, failed, warnings

def validate_real_time_monitoring():
    """Validate real-time monitoring configuration"""
    print_header("3. REAL-TIME MONITORING CONFIGURATION")
    
    passed = 0
    failed = 0
    warnings = 0
    
    # Check monitoring enabled
    monitoring = os.getenv('MONITORING_ENABLED', 'false').lower() == 'true'
    if monitoring:
        print_success("MONITORING_ENABLED = true")
        passed += 1
    else:
        print_warning("MONITORING_ENABLED = false (Feature not enabled)")
        warnings += 1
    
    # Check dashboard enabled
    dashboard = os.getenv('DASHBOARD_ENABLED', 'false').lower() == 'true'
    if dashboard:
        print_success("DASHBOARD_ENABLED = true")
        passed += 1
        
        # Check dashboard configuration
        port = os.getenv('DASHBOARD_PORT', '8080')
        host = os.getenv('DASHBOARD_HOST', '0.0.0.0')
        print_success(f"DASHBOARD_PORT = {port}")
        print_success(f"DASHBOARD_HOST = {host}")
        passed += 2
    else:
        print_warning("DASHBOARD_ENABLED = false (Feature not enabled)")
        warnings += 1
    
    # Check metrics collection
    metrics = os.getenv('METRICS_COLLECTION_ENABLED', 'false').lower() == 'true'
    if metrics:
        print_success("METRICS_COLLECTION_ENABLED = true")
        passed += 1
    else:
        print_warning("METRICS_COLLECTION_ENABLED = false")
        warnings += 1
    
    # Check health check interval
    health_interval = os.getenv('HEALTH_CHECK_INTERVAL', '60')
    print_success(f"HEALTH_CHECK_INTERVAL = {health_interval}s")
    passed += 1
    
    # Check execution metrics tracking
    exec_metrics = os.getenv('TRACK_EXECUTION_METRICS', 'false').lower() == 'true'
    if exec_metrics:
        print_success("TRACK_EXECUTION_METRICS = true")
        passed += 1
    else:
        print_warning("TRACK_EXECUTION_METRICS = false")
        warnings += 1
    
    # Check MEV metrics tracking
    mev_metrics = os.getenv('TRACK_MEV_METRICS', 'false').lower() == 'true'
    if mev_metrics:
        print_success("TRACK_MEV_METRICS = true")
        passed += 1
    else:
        print_warning("TRACK_MEV_METRICS = false")
        warnings += 1
    
    # Check alert configuration
    alerts = os.getenv('ALERT_ON_ERRORS', 'false').lower() == 'true'
    if alerts:
        print_success("ALERT_ON_ERRORS = true")
        passed += 1
    else:
        print_warning("ALERT_ON_ERRORS = false")
        warnings += 1
    
    # Check real-time data enabled
    realtime_data = os.getenv('REAL_TIME_DATA_ENABLED', 'true').lower() == 'true'
    if realtime_data:
        print_success("REAL_TIME_DATA_ENABLED = true")
        passed += 1
    else:
        print_warning("REAL_TIME_DATA_ENABLED = false")
        warnings += 1
    
    return passed, failed, warnings

def validate_config_json():
    """Validate config.json settings"""
    print_header("4. CONFIG.JSON VALIDATION")
    
    passed = 0
    failed = 0
    warnings = 0
    
    config_path = Path('config.json')
    if not config_path.exists():
        print_error("config.json not found")
        return 0, 1, 0
    
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        print_success("config.json loaded successfully")
        passed += 1
        
        # Check advanced features
        if 'advanced_features' in config:
            features = config['advanced_features']
            
            # Check cross-chain routing
            if 'cross_chain_routing' in features and features['cross_chain_routing'].get('enabled'):
                print_success("Cross-chain routing enabled in config.json")
                passed += 1
            else:
                print_warning("Cross-chain routing not enabled in config.json")
                warnings += 1
            
            # Check multi-aggregator routing
            if 'multi_aggregator_routing' in features and features['multi_aggregator_routing'].get('enabled'):
                print_success("Multi-aggregator routing enabled in config.json")
                passed += 1
            else:
                print_warning("Multi-aggregator routing not enabled in config.json")
                warnings += 1
            
            # Check real-time monitoring
            if 'real_time_monitoring' in features and features['real_time_monitoring'].get('enabled'):
                print_success("Real-time monitoring enabled in config.json")
                passed += 1
            else:
                print_warning("Real-time monitoring not enabled in config.json")
                warnings += 1
            
            # Check transaction execution
            if 'transaction_execution' in features and features['transaction_execution'].get('enabled'):
                print_success("Transaction execution enabled in config.json")
                passed += 1
            else:
                print_warning("Transaction execution not enabled in config.json")
                warnings += 1
        
        # Check monitoring section
        if 'monitoring' in config:
            monitoring = config['monitoring']
            
            if monitoring.get('enabled'):
                print_success("Monitoring enabled in config.json")
                passed += 1
            else:
                print_warning("Monitoring not enabled in config.json")
                warnings += 1
            
            if 'dashboard' in monitoring and monitoring['dashboard'].get('enabled'):
                print_success("Dashboard enabled in config.json")
                passed += 1
            else:
                print_warning("Dashboard not enabled in config.json")
                warnings += 1
        
    except json.JSONDecodeError as e:
        print_error(f"config.json has invalid JSON: {e}")
        failed += 1
    except Exception as e:
        print_error(f"Error reading config.json: {e}")
        failed += 1
    
    return passed, failed, warnings

def validate_rpc_connections():
    """Validate RPC endpoint configuration"""
    print_header("5. RPC ENDPOINT CONFIGURATION")
    
    passed = 0
    failed = 0
    warnings = 0
    
    # Check primary RPC endpoints
    chains = ['ETHEREUM', 'POLYGON', 'ARBITRUM', 'OPTIMISM', 'BASE']
    
    for chain in chains:
        rpc = os.getenv(f'RPC_{chain}')
        wss = os.getenv(f'WSS_{chain}')
        
        if rpc and rpc != f'https://your-{chain.lower()}-rpc-url':
            print_success(f"RPC_{chain} configured")
            passed += 1
        else:
            print_warning(f"RPC_{chain} not configured")
            warnings += 1
        
        if wss and wss != f'wss://your-{chain.lower()}-wss-url':
            print_success(f"WSS_{chain} configured")
            passed += 1
        else:
            print_info(f"WSS_{chain} not configured (optional)")
    
    return passed, failed, warnings

def main():
    """Main validation routine"""
    print(f"\n{Colors.BOLD}{'=' * 80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}APEX-OMEGA TITAN: SYSTEM CONFIGURATION VALIDATOR{Colors.END}")
    print(f"{Colors.BOLD}{'=' * 80}{Colors.END}")
    print(f"\nValidating system configuration for:")
    print(f"  1. Real Transaction Execution")
    print(f"  2. Advanced Routing (Cross-Chain, Multi-Aggregator)")
    print(f"  3. Real-Time Monitoring")
    
    total_passed = 0
    total_failed = 0
    total_warnings = 0
    
    # Run all validation checks
    p, f, w = validate_transaction_execution()
    total_passed += p
    total_failed += f
    total_warnings += w
    
    p, f, w = validate_advanced_routing()
    total_passed += p
    total_failed += f
    total_warnings += w
    
    p, f, w = validate_real_time_monitoring()
    total_passed += p
    total_failed += f
    total_warnings += w
    
    p, f, w = validate_config_json()
    total_passed += p
    total_failed += f
    total_warnings += w
    
    p, f, w = validate_rpc_connections()
    total_passed += p
    total_failed += f
    total_warnings += w
    
    # Print summary
    print_header("VALIDATION SUMMARY")
    
    print(f"{Colors.GREEN}✅ Passed: {total_passed}{Colors.END}")
    print(f"{Colors.YELLOW}⚠️  Warnings: {total_warnings}{Colors.END}")
    print(f"{Colors.RED}❌ Failed: {total_failed}{Colors.END}")
    
    print()
    
    if total_failed > 0:
        print(f"{Colors.RED}{Colors.BOLD}VALIDATION FAILED{Colors.END}")
        print(f"{Colors.RED}Please fix the errors above before proceeding.{Colors.END}")
        return 1
    elif total_warnings > 5:
        print(f"{Colors.YELLOW}{Colors.BOLD}VALIDATION PASSED WITH WARNINGS{Colors.END}")
        print(f"{Colors.YELLOW}Consider enabling the features mentioned above for full functionality.{Colors.END}")
        return 0
    else:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ VALIDATION SUCCESSFUL{Colors.END}")
        print(f"{Colors.GREEN}System is fully configured for real transaction execution,{Colors.END}")
        print(f"{Colors.GREEN}advanced routing, and real-time monitoring.{Colors.END}")
        return 0

if __name__ == '__main__':
    sys.exit(main())
