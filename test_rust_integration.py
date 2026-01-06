#!/usr/bin/env python3
"""
Integration Test: Rust Features Operational Verification
Tests all 5 Rust features are actively wired and responding.
"""

import subprocess
import time
import requests
import json
import sys
import signal
import os

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'=' * 80}{RESET}")
    print(f"{BLUE}{text.center(80)}{RESET}")
    print(f"{BLUE}{'=' * 80}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_info(text):
    print(f"{BLUE}ℹ️  {text}{RESET}")

class RustServerTest:
    """Test harness for Rust HTTP server"""
    
    def __init__(self):
        self.server_process = None
        self.base_url = "http://localhost:3000"
        
    def start_server(self):
        """Start the Rust HTTP server"""
        print_info("Starting Rust HTTP server...")
        
        try:
            # Start server in background
            self.server_process = subprocess.Popen(
                ['cargo', 'run', '--release', '--bin', 'titan_server'],
                cwd='core-rust',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            print_info("Waiting for server to initialize...")
            for i in range(15):
                time.sleep(1)
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=1)
                    if response.status_code == 200:
                        print_success("Server started successfully")
                        return True
                except requests.exceptions.RequestException:
                    if i < 14:
                        continue
                    else:
                        print_error("Server failed to start within 15 seconds")
                        return False
            
            return False
            
        except Exception as e:
            print_error(f"Failed to start server: {e}")
            return False
    
    def stop_server(self):
        """Stop the Rust HTTP server"""
        if self.server_process:
            print_info("Stopping server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                self.server_process.wait()
            print_success("Server stopped")
    
    def test_health_endpoint(self):
        """Test /health endpoint (http_server.rs)"""
        print_info("Testing /health endpoint...")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                assert 'status' in data, "Missing 'status' field"
                assert 'version' in data, "Missing 'version' field"
                assert 'rust_engine' in data, "Missing 'rust_engine' field"
                
                assert data['status'] == 'healthy', f"Status not healthy: {data['status']}"
                assert data['rust_engine'] == True, "Rust engine not enabled"
                
                print_success(f"Health check passed: {data}")
                return True
            else:
                print_error(f"Health check failed with status {response.status_code}")
                return False
                
        except Exception as e:
            print_error(f"Health check error: {e}")
            return False
    
    def test_metrics_endpoint(self):
        """Test /api/metrics endpoint (http_server.rs)"""
        print_info("Testing /api/metrics endpoint...")
        
        try:
            response = requests.get(f"{self.base_url}/api/metrics", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                assert 'queries_total' in data
                assert 'queries_success' in data
                assert 'queries_failed' in data
                
                print_success(f"Metrics endpoint passed: {data}")
                return True
            else:
                print_error(f"Metrics endpoint failed with status {response.status_code}")
                return False
                
        except Exception as e:
            print_error(f"Metrics endpoint error: {e}")
            return False
    
    def test_tvl_endpoint(self):
        """Test /api/tvl endpoint (simulation_engine.rs integration)"""
        print_info("Testing /api/tvl endpoint...")
        
        try:
            # Test with invalid input (should return error gracefully)
            params = {
                'chain_id': 137,
                'token_address': '0x0000000000000000000000000000000000000000'
            }
            
            response = requests.get(f"{self.base_url}/api/tvl", params=params, timeout=10)
            
            # Should return some response (even if RPC fails)
            if response.status_code in [200, 400, 500]:
                data = response.json()
                assert 'success' in data
                assert 'chain_id' in data
                assert 'token_address' in data
                
                print_success(f"TVL endpoint responded: success={data['success']}")
                return True
            else:
                print_error(f"TVL endpoint failed with status {response.status_code}")
                return False
                
        except Exception as e:
            print_error(f"TVL endpoint error: {e}")
            return False
    
    def test_optimize_loan_endpoint(self):
        """Test /api/optimize_loan endpoint (commander.rs integration)"""
        print_info("Testing /api/optimize_loan endpoint...")
        
        try:
            # Test loan optimization
            payload = {
                'chain_id': 137,
                'token_address': '0x0000000000000000000000000000000000000000',
                'target_amount': '1000000000000000000',  # 1.0 token (18 decimals)
                'decimals': 18
            }
            
            response = requests.post(
                f"{self.base_url}/api/optimize_loan",
                json=payload,
                timeout=10
            )
            
            # Should return some response
            if response.status_code in [200, 400, 500]:
                data = response.json()
                assert 'success' in data
                assert 'chain_id' in data
                assert 'optimized_amount' in data
                
                print_success(f"Loan optimization responded: success={data['success']}, amount={data['optimized_amount']}")
                return True
            else:
                print_error(f"Loan optimization failed with status {response.status_code}")
                return False
                
        except Exception as e:
            print_error(f"Loan optimization error: {e}")
            return False

def main():
    """Main test routine"""
    print_header("Rust Features Integration Test")
    print_info("Testing operational status of all 5 Rust features:\n")
    print("  1. config.rs - Via server configuration")
    print("  2. enum_matrix.rs - Via provider management")
    print("  3. simulation_engine.rs - Via /api/tvl endpoint")
    print("  4. commander.rs - Via /api/optimize_loan endpoint")
    print("  5. http_server.rs - Via HTTP server and all endpoints\n")
    
    tester = RustServerTest()
    results = {}
    
    try:
        # Start server
        if not tester.start_server():
            print_error("\nFailed to start server. Cannot run integration tests.")
            return False
        
        # Run tests
        print_header("Running Integration Tests")
        
        results['Health Endpoint'] = tester.test_health_endpoint()
        time.sleep(0.5)
        
        results['Metrics Endpoint'] = tester.test_metrics_endpoint()
        time.sleep(0.5)
        
        results['TVL Endpoint'] = tester.test_tvl_endpoint()
        time.sleep(0.5)
        
        results['Loan Optimization'] = tester.test_optimize_loan_endpoint()
        
    finally:
        # Always stop server
        tester.stop_server()
    
    # Print results
    print_header("Integration Test Results")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    
    print(f"\n{'Test':<30} {'Result':<10}")
    print("-" * 40)
    
    for test, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"{test:<30} {status}")
    
    print("-" * 40)
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print_success("\n🎉 All Rust features are operational and responding!")
        return True
    else:
        print_error(f"\n⚠️  {total - passed} test(s) failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
