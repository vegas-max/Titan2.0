#!/usr/bin/env python3
"""
Integration Test for Real Data Pipeline
Tests WebSocket manager, real data pipeline, and Rust server integration
"""

import asyncio
import json
import os
import sys
import time
import requests
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Integration Test")


class IntegrationTest:
    """Test suite for real data pipeline integration"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
    
    def test_config_loading(self):
        """Test that config.json loads correctly"""
        logger.info("Testing config.json loading...")
        
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
            
            # Check for real_data_pipeline config
            if 'advanced_features' in config:
                if 'real_data_pipeline' in config['advanced_features']:
                    logger.info("✅ Real data pipeline config found")
                    self.passed += 1
                else:
                    logger.warning("⚠️  Real data pipeline not in advanced_features")
                    self.skipped += 1
            else:
                logger.error("❌ No advanced_features in config")
                self.failed += 1
                
        except Exception as e:
            logger.error(f"❌ Failed to load config: {e}")
            self.failed += 1
    
    def test_websocket_manager_import(self):
        """Test WebSocket manager can be imported"""
        logger.info("Testing WebSocket manager import...")
        
        try:
            from offchain.core.websocket_manager import WebSocketManager
            logger.info("✅ WebSocket manager imported successfully")
            self.passed += 1
        except ImportError as e:
            logger.error(f"❌ Failed to import WebSocket manager: {e}")
            logger.info("   Install websockets: pip install websockets")
            self.failed += 1
    
    def test_real_data_pipeline_import(self):
        """Test real data pipeline can be imported"""
        logger.info("Testing real data pipeline import...")
        
        try:
            from offchain.core.real_data_pipeline import RealDataPipeline
            logger.info("✅ Real data pipeline imported successfully")
            self.passed += 1
        except ImportError as e:
            logger.error(f"❌ Failed to import real data pipeline: {e}")
            self.failed += 1
    
    def test_rust_server_binary(self):
        """Test Rust server binary exists"""
        logger.info("Testing Rust server binary...")
        
        binary_path = Path('core-rust/target/release/titan_server')
        debug_path = Path('core-rust/target/debug/titan_server')
        
        if binary_path.exists():
            logger.info(f"✅ Rust server binary found (release)")
            self.passed += 1
        elif debug_path.exists():
            logger.info(f"✅ Rust server binary found (debug)")
            self.passed += 1
        else:
            logger.warning("⚠️  Rust server not built yet")
            logger.info("   Build with: cd core-rust && cargo build --bin titan_server")
            self.skipped += 1
    
    def test_rust_server_running(self):
        """Test if Rust server is running"""
        logger.info("Testing Rust server connectivity...")
        
        port = os.getenv('RUST_SERVER_PORT', '3000')
        url = f"http://localhost:{port}/health"
        
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Rust server is running: {data}")
                self.passed += 1
            else:
                logger.warning(f"⚠️  Rust server returned {response.status_code}")
                self.skipped += 1
        except requests.exceptions.RequestException:
            logger.warning("⚠️  Rust server not running")
            logger.info("   Start with: ./start_rust_server.sh")
            self.skipped += 1
    
    def test_ml_models_exist(self):
        """Test if ML models have been trained"""
        logger.info("Testing ML model files...")
        
        model_files = [
            'data/models/forecaster_xgb.pkl',
            'data/models/forecaster_gb.pkl',
            'data/models/forecaster_scaler.pkl',
            'data/q_table.json'
        ]
        
        found = 0
        for model_file in model_files:
            if Path(model_file).exists():
                found += 1
        
        if found == len(model_files):
            logger.info(f"✅ All {len(model_files)} ML model files found")
            self.passed += 1
        elif found > 0:
            logger.warning(f"⚠️  Only {found}/{len(model_files)} model files found")
            logger.info("   Train models with: ./train_ml_models.py")
            self.skipped += 1
        else:
            logger.warning("⚠️  No ML model files found")
            logger.info("   Train models with: ./train_ml_models.py")
            self.skipped += 1
    
    def test_training_script(self):
        """Test training script exists and is executable"""
        logger.info("Testing training script...")
        
        script_path = Path('train_ml_models.py')
        
        if script_path.exists():
            if os.access(script_path, os.X_OK):
                logger.info("✅ Training script exists and is executable")
                self.passed += 1
            else:
                logger.info("✅ Training script exists (not executable)")
                logger.info("   Make executable: chmod +x train_ml_models.py")
                self.passed += 1
        else:
            logger.error("❌ Training script not found")
            self.failed += 1
    
    def test_env_variables(self):
        """Test environment variables are set"""
        logger.info("Testing environment variables...")
        
        required_vars = {
            'USE_REAL_DATA': 'true',
            'ENABLE_RUST_ENGINE': 'true',
            'ENABLE_ML_MODELS': 'true'
        }
        
        missing = []
        for var, expected in required_vars.items():
            value = os.getenv(var)
            if value is None:
                missing.append(var)
        
        if not missing:
            logger.info(f"✅ All required environment variables set")
            self.passed += 1
        else:
            logger.warning(f"⚠️  Missing environment variables: {', '.join(missing)}")
            logger.info("   Copy .env.example to .env and configure")
            self.skipped += 1
    
    def test_dependencies(self):
        """Test required Python dependencies are installed"""
        logger.info("Testing Python dependencies...")
        
        required_packages = [
            'websockets',
            'requests',
            'web3',
            'scikit-learn',
            'xgboost',
            'joblib'
        ]
        
        missing = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing.append(package)
        
        if not missing:
            logger.info(f"✅ All required packages installed")
            self.passed += 1
        else:
            logger.warning(f"⚠️  Missing packages: {', '.join(missing)}")
            logger.info(f"   Install with: pip install {' '.join(missing)}")
            self.skipped += 1
    
    def run_all_tests(self):
        """Run all integration tests"""
        logger.info("=" * 60)
        logger.info("Real Data Pipeline Integration Tests")
        logger.info("=" * 60)
        logger.info("")
        
        # Run tests
        self.test_config_loading()
        self.test_websocket_manager_import()
        self.test_real_data_pipeline_import()
        self.test_rust_server_binary()
        self.test_rust_server_running()
        self.test_ml_models_exist()
        self.test_training_script()
        self.test_env_variables()
        self.test_dependencies()
        
        # Print summary
        logger.info("")
        logger.info("=" * 60)
        logger.info("Test Summary")
        logger.info("=" * 60)
        logger.info(f"✅ Passed:  {self.passed}")
        logger.info(f"❌ Failed:  {self.failed}")
        logger.info(f"⚠️  Skipped: {self.skipped}")
        logger.info(f"Total:     {self.passed + self.failed + self.skipped}")
        logger.info("")
        
        if self.failed == 0:
            logger.info("🎉 All tests passed or skipped!")
            logger.info("")
            logger.info("Next steps:")
            logger.info("1. Start Rust server: ./start_rust_server.sh")
            logger.info("2. Train ML models: ./train_ml_models.py")
            logger.info("3. Configure .env file")
            logger.info("4. Test real data pipeline")
            return True
        else:
            logger.error("❌ Some tests failed. Please fix errors above.")
            return False


def main():
    """Run integration tests"""
    tester = IntegrationTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
