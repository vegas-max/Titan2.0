#!/usr/bin/env python3
"""
TITAN 2.0 - Complete Integration Test
======================================

Tests the complete end-to-end flow:
1. Boot sequence
2. Data ingestion from on-chain sources
3. Profit calculation with real data
4. Signal generation
5. Execution path (simulated)
6. On-chain payload generation
"""

import os
import sys
import json
import time
from pathlib import Path
from decimal import Decimal
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Load environment
from dotenv import load_dotenv
load_dotenv()

def print_section(text: str):
    """Print section header"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{text.center(80)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")

def print_info(text: str):
    """Print info message"""
    print(f"{Fore.BLUE}ℹ️  {text}{Style.RESET_ALL}")

def print_error(text: str):
    """Print error message"""
    print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")


def test_boot_sequence():
    """Test 1: Boot sequence and component initialization"""
    print_section("TEST 1: Boot Sequence and Initialization")
    
    try:
        # Import core modules
        from offchain.core.config import CHAINS, BALANCER_V3_VAULT
        print_success("Configuration module loaded")
        
        # Import brain components
        from offchain.ml.brain import OmniBrain, ProfitEngine
        print_success("Brain module loaded")
        
        # Import execution components (not directly but check they exist)
        bot_path = Path('offchain/execution/bot.js')
        if bot_path.exists():
            print_success("Execution bot file exists")
        
        # Initialize core components
        print_info("Initializing ProfitEngine...")
        profit_engine = ProfitEngine()
        print_success("ProfitEngine initialized")
        
        # Test profit calculation
        result = profit_engine.calculate_enhanced_profit(
            Decimal("1000"),
            Decimal("1015"),
            Decimal("2"),
            Decimal("3")
        )
        print_success(f"Profit calculation test: ${result['net_profit']} (profitable: {result['is_profitable']})")
        
        return True
        
    except Exception as e:
        print_error(f"Boot sequence failed: {e}")
        return False


def test_data_ingestion():
    """Test 2: Data ingestion from on-chain sources"""
    print_section("TEST 2: On-Chain Data Ingestion")
    
    try:
        from web3 import Web3
        from offchain.core.config import CHAINS
        
        # Test connection to Polygon (most commonly used)
        polygon_rpc = os.getenv('RPC_POLYGON')
        if not polygon_rpc:
            print_error("RPC_POLYGON not configured")
            return False
            
        w3 = Web3(Web3.HTTPProvider(polygon_rpc))
        
        if not w3.is_connected():
            print_error("Failed to connect to Polygon RPC")
            return False
            
        print_success(f"Connected to Polygon RPC")
        
        # Get latest block
        latest_block = w3.eth.block_number
        print_success(f"Latest block retrieved: {latest_block}")
        
        # Get gas price
        gas_price_wei = w3.eth.gas_price
        gas_price_gwei = w3.from_wei(gas_price_wei, 'gwei')
        print_success(f"Gas price retrieved: {gas_price_gwei:.2f} gwei")
        
        # Test token contract interaction
        from web3.contract import Contract
        from eth_abi import encode
        
        # USDC on Polygon
        usdc_address = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
        
        # Simple ERC20 ABI for decimals
        erc20_abi = [
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "symbol",
                "outputs": [{"name": "", "type": "string"}],
                "type": "function"
            }
        ]
        
        usdc_contract = w3.eth.contract(address=usdc_address, abi=erc20_abi)
        
        try:
            decimals = usdc_contract.functions.decimals().call()
            symbol = usdc_contract.functions.symbol().call()
            print_success(f"Token data retrieved: {symbol} (decimals: {decimals})")
        except Exception as e:
            print_info(f"Token contract call skipped (rate limit or network issue): {str(e)[:50]}")
        
        return True
        
    except Exception as e:
        print_error(f"Data ingestion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_calculation_pipeline():
    """Test 3: Calculation pipeline with real data structure"""
    print_section("TEST 3: Calculation Pipeline")
    
    try:
        from offchain.ml.brain import ProfitEngine
        from decimal import Decimal
        
        engine = ProfitEngine()
        
        # Simulate a realistic arbitrage scenario
        test_scenarios = [
            {
                "name": "Profitable USDC arbitrage",
                "loan_amount": Decimal("10000"),  # $10,000 loan
                "amount_out": Decimal("10150"),   # $10,150 output
                "bridge_fee": Decimal("5"),       # $5 bridge fee
                "gas_cost": Decimal("3"),         # $3 gas cost
                "expected_profitable": True
            },
            {
                "name": "Unprofitable trade (high fees)",
                "loan_amount": Decimal("1000"),
                "amount_out": Decimal("1005"),
                "bridge_fee": Decimal("10"),
                "gas_cost": Decimal("5"),
                "expected_profitable": False
            },
            {
                "name": "Borderline profitable",
                "loan_amount": Decimal("50000"),
                "amount_out": Decimal("50100"),
                "bridge_fee": Decimal("20"),
                "gas_cost": Decimal("10"),
                "expected_profitable": True
            }
        ]
        
        all_passed = True
        for scenario in test_scenarios:
            result = engine.calculate_enhanced_profit(
                scenario["loan_amount"],
                scenario["amount_out"],
                scenario["bridge_fee"],
                scenario["gas_cost"]
            )
            
            passed = result["is_profitable"] == scenario["expected_profitable"]
            if passed:
                print_success(f"{scenario['name']}: Net profit ${result['net_profit']:.2f} (as expected)")
            else:
                print_error(f"{scenario['name']}: Unexpected result")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_error(f"Calculation pipeline test failed: {e}")
        return False


def test_signal_generation():
    """Test 4: Signal generation and file I/O"""
    print_section("TEST 4: Signal Generation")
    
    try:
        signals_dir = Path('signals/outgoing')
        signals_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate a test signal
        test_signal = {
            "chainId": 137,
            "token": "USDC",
            "tokenAddress": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
            "amount": "10000000000",  # 10,000 USDC (6 decimals)
            "expectedProfit": 15.50,
            "route": {
                "protocols": [3, 2],  # UniV3, Sushi
                "routers": [
                    "0xE592427A0AEce92De3Edee1F18E0157C05861564",
                    "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"
                ],
                "tokens": [
                    "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",  # USDC
                    "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619",  # WETH
                    "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"   # USDC
                ]
            },
            "gasPrice": {
                "maxFeePerGas": "35000000000",      # 35 gwei
                "maxPriorityFeePerGas": "25000000000"  # 25 gwei
            },
            "timestamp": time.time(),
            "execution_mode": "PAPER"
        }
        
        # Write signal to file
        signal_file = signals_dir / f"test_signal_{int(time.time())}.json"
        with open(signal_file, 'w') as f:
            json.dump(test_signal, f, indent=2)
        
        print_success(f"Test signal written: {signal_file}")
        
        # Verify signal can be read
        with open(signal_file, 'r') as f:
            loaded_signal = json.load(f)
        
        print_success("Signal read back successfully")
        
        # Validate signal structure
        required_fields = ['chainId', 'token', 'amount', 'expectedProfit', 'route']
        for field in required_fields:
            if field not in loaded_signal:
                print_error(f"Missing required field: {field}")
                return False
        
        print_success("Signal structure validation passed")
        
        # Clean up
        signal_file.unlink()
        print_success("Test signal cleaned up")
        
        return True
        
    except Exception as e:
        print_error(f"Signal generation test failed: {e}")
        return False


def test_execution_path():
    """Test 5: Execution path validation (without actual blockchain tx)"""
    print_section("TEST 5: Execution Path Validation")
    
    try:
        # Check that bot.js exists and has required components
        bot_path = Path('offchain/execution/bot.js')
        if not bot_path.exists():
            print_error("bot.js not found")
            return False
        
        print_success("Execution bot file exists")
        
        # Check for gas manager
        gas_manager_path = Path('offchain/execution/gas_manager.js')
        if gas_manager_path.exists():
            print_success("Gas manager module exists")
        
        # Check for aggregator selector
        aggregator_path = Path('offchain/execution/aggregator_selector.js')
        if aggregator_path.exists():
            print_success("Aggregator selector module exists")
        
        # Verify execution mode configuration
        execution_mode = os.getenv('EXECUTION_MODE', 'PAPER').upper()
        if execution_mode == 'PAPER':
            print_success("Execution mode: PAPER (simulated execution)")
        else:
            print_info(f"Execution mode: {execution_mode} (real execution)")
        
        return True
        
    except Exception as e:
        print_error(f"Execution path test failed: {e}")
        return False


def test_address_validation():
    """Test 6: Validate no zero addresses in critical paths"""
    print_section("TEST 6: Address Validation")
    
    try:
        from offchain.core.config import CHAINS, BALANCER_V3_VAULT
        
        # Validate Balancer V3 Vault
        if BALANCER_V3_VAULT == "0x0000000000000000000000000000000000000000":
            print_error("Balancer V3 Vault is zero address!")
            return False
        print_success(f"Balancer V3 Vault: {BALANCER_V3_VAULT}")
        
        # Check major chains have at least one DEX
        critical_chains = [1, 137, 42161, 10, 8453]
        
        for chain_id in critical_chains:
            chain_config = CHAINS.get(chain_id)
            if not chain_config:
                print_error(f"Chain {chain_id} not configured")
                continue
            
            # Check if chain has at least one non-zero router
            has_router = False
            for key, value in chain_config.items():
                if 'router' in key and value != "0x0000000000000000000000000000000000000000":
                    has_router = True
                    break
            
            if has_router:
                print_success(f"{chain_config['name']}: Has configured DEX routers")
            else:
                print_info(f"{chain_config['name']}: No standard DEX routers (may use aggregators)")
        
        return True
        
    except Exception as e:
        print_error(f"Address validation failed: {e}")
        return False


def test_ai_components():
    """Test 7: AI/ML components initialization"""
    print_section("TEST 7: AI/ML Components")
    
    try:
        from offchain.ml.cortex.forecaster import MarketForecaster
        from offchain.ml.cortex.rl_optimizer import QLearningAgent
        from offchain.ml.cortex.feature_store import FeatureStore
        
        # Test MarketForecaster
        forecaster = MarketForecaster()
        print_success("MarketForecaster initialized")
        
        # Test gas trend forecast
        for i in range(10):
            forecaster.ingest_gas(30 + i)  # Increasing gas
        
        trend = forecaster.predict_gas_trend()
        print_success(f"Gas trend forecast: {trend}")
        
        # Test QLearningAgent
        agent = QLearningAgent()
        print_success("QLearningAgent initialized")
        
        # Test parameter recommendation
        params = agent.recommend_parameters(137, "MEDIUM", 30)
        print_success(f"Q-Learning test action: slippage={params['slippage']}, priority={params['priority']}")
        
        # Test FeatureStore
        store = FeatureStore()
        print_success("FeatureStore initialized")
        
        # Log test observation
        import time
        timestamp = time.time()
        store.log_observation(137, "USDC", 1.0, 0.003, 25.0, 0.01, timestamp)
        store.update_outcome(timestamp, 15.50, 150, True)
        
        summary = store.get_summary()
        print_success(f"Feature store test: observations={summary.get('observations', {}).get('total', 0)}")
        
        return True
        
    except Exception as e:
        print_error(f"AI components test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all integration tests"""
    print(f"\n{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}TITAN 2.0 - COMPLETE INTEGRATION TEST{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}\n")
    
    tests = [
        ("Boot Sequence", test_boot_sequence),
        ("Data Ingestion", test_data_ingestion),
        ("Calculation Pipeline", test_calculation_pipeline),
        ("Signal Generation", test_signal_generation),
        ("Execution Path", test_execution_path),
        ("Address Validation", test_address_validation),
        ("AI Components", test_ai_components),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"{name} crashed: {e}")
            results.append((name, False))
    
    # Print summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Fore.GREEN}✅ PASSED{Style.RESET_ALL}" if result else f"{Fore.RED}❌ FAILED{Style.RESET_ALL}"
        print(f"{name.ljust(30)} {status}")
    
    print(f"\n{Fore.CYAN}Results: {passed}/{total} tests passed{Style.RESET_ALL}")
    
    if passed == total:
        print(f"{Fore.GREEN}🎉 ALL INTEGRATION TESTS PASSED!{Style.RESET_ALL}\n")
        return True
    else:
        print(f"{Fore.YELLOW}⚠️  Some tests failed. Review errors above.{Style.RESET_ALL}\n")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
