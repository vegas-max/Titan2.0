#!/usr/bin/env python3
"""
Real-Time Market Analysis Configuration Validator

This script validates that the system is fully configured to analyze and
evaluate markets in real-time to provide accurate and usable signals.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

class ConfigValidator:
    """Validates real-time market analysis configuration"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed = []
        
    def validate_env_setting(self, name, expected=None, required=True):
        """Validate an environment variable setting"""
        value = os.getenv(name)
        
        if value is None:
            if required:
                self.errors.append(f"❌ Missing required setting: {name}")
                return False
            else:
                self.warnings.append(f"⚠️  Optional setting not configured: {name}")
                return False
        
        if expected is not None and value.lower() != expected.lower():
            self.errors.append(f"❌ {name}={value} (expected: {expected})")
            return False
            
        self.passed.append(f"✅ {name}={value}")
        return True
    
    def validate_real_time_data(self):
        """Validate real-time data pipeline configuration"""
        print("\n🔍 Validating Real-Time Data Pipeline...")
        print("=" * 70)
        
        # Core real-time settings
        self.validate_env_setting("USE_REAL_DATA", "true", required=True)
        self.validate_env_setting("USE_WEBSOCKETS", "true", required=True)
        self.validate_env_setting("REAL_DATA_POLLING_INTERVAL", required=True)
        self.validate_env_setting("REAL_TIME_DATA_ENABLED", "true", required=True)
        
        # Check polling interval value
        interval = os.getenv("REAL_DATA_POLLING_INTERVAL")
        if interval:
            try:
                interval_val = int(interval)
                if interval_val < 1 or interval_val > 60:
                    self.warnings.append(f"⚠️  REAL_DATA_POLLING_INTERVAL={interval}s (recommended: 1-10s)")
            except ValueError:
                self.errors.append(f"❌ Invalid REAL_DATA_POLLING_INTERVAL: {interval}")
    
    def validate_ml_configuration(self):
        """Validate ML and AI configuration"""
        print("\n🤖 Validating ML/AI Configuration...")
        print("=" * 70)
        
        # ML Models
        self.validate_env_setting("ENABLE_ML_MODELS", "true", required=True)
        self.validate_env_setting("ENABLE_REALTIME_TRAINING", "true", required=True)
        
        # ML settings
        ml_trained = os.getenv("ML_MODELS_TRAINED", "false")
        if ml_trained.lower() == "false":
            self.warnings.append("⚠️  ML_MODELS_TRAINED=false - Run train_ml_models.py to train models")
        
        # AI Scoring
        self.validate_env_setting("TAR_SCORING_ENABLED", "true", required=True)
        self.validate_env_setting("AI_PREDICTION_ENABLED", "true", required=True)
        self.validate_env_setting("CATBOOST_MODEL_ENABLED", "true", required=True)
        
        # Intelligence Features
        self.validate_env_setting("SELF_LEARNING_ENABLED", "true", required=True)
        self.validate_env_setting("ROUTE_INTELLIGENCE_ENABLED", "true", required=True)
        
        # Confidence Thresholds
        self.validate_env_setting("AI_PREDICTION_MIN_CONFIDENCE", required=True)
        self.validate_env_setting("HF_CONFIDENCE_THRESHOLD", required=True)
        self.validate_env_setting("ML_CONFIDENCE_THRESHOLD", required=True)
    
    def validate_execution_mode(self):
        """Validate execution mode configuration"""
        print("\n⚙️  Validating Execution Mode...")
        print("=" * 70)
        
        mode = os.getenv("EXECUTION_MODE", "PAPER").upper()
        if mode not in ["PAPER", "LIVE"]:
            self.errors.append(f"❌ Invalid EXECUTION_MODE: {mode} (must be PAPER or LIVE)")
        else:
            if mode == "LIVE":
                self.warnings.append("⚠️  EXECUTION_MODE=LIVE - Real money will be used!")
                self.warnings.append("⚠️  Ensure PRIVATE_KEY and EXECUTOR_ADDRESS are configured")
            else:
                self.passed.append(f"✅ EXECUTION_MODE={mode} (safe for testing)")
    
    def validate_rpc_connections(self):
        """Validate RPC endpoint configuration"""
        print("\n🌐 Validating RPC Connections...")
        print("=" * 70)
        
        chains = [
            ("RPC_ETHEREUM", "Ethereum"),
            ("RPC_POLYGON", "Polygon"),
            ("RPC_ARBITRUM", "Arbitrum"),
            ("RPC_OPTIMISM", "Optimism"),
            ("RPC_BASE", "Base"),
        ]
        
        configured_count = 0
        for rpc_var, chain_name in chains:
            if self.validate_env_setting(rpc_var, required=False):
                configured_count += 1
        
        if configured_count == 0:
            self.errors.append("❌ No RPC endpoints configured - at least one is required")
        else:
            self.passed.append(f"✅ {configured_count} RPC endpoints configured")
    
    def validate_rust_engine(self):
        """Validate Rust engine configuration"""
        print("\n⚡ Validating Rust Engine...")
        print("=" * 70)
        
        self.validate_env_setting("ENABLE_RUST_ENGINE", "true", required=False)
        self.validate_env_setting("RUST_SERVER_PORT", required=False)
        
        # Check if Rust engine is available
        try:
            import titan_core
            self.passed.append("✅ Rust engine (titan_core) is available")
        except ImportError:
            self.warnings.append("⚠️  Rust engine not installed - run ./build_rust_engine.sh")
    
    def validate_signal_output(self):
        """Validate signal output directory"""
        print("\n📡 Validating Signal Output...")
        print("=" * 70)
        
        signals_dir = Path("signals/outgoing")
        if signals_dir.exists():
            self.passed.append(f"✅ Signal output directory exists: {signals_dir}")
        else:
            self.warnings.append(f"⚠️  Signal output directory will be created: {signals_dir}")
    
    def validate_dependencies(self):
        """Validate critical dependencies are available"""
        print("\n📦 Validating Dependencies...")
        print("=" * 70)
        
        critical_deps = [
            ("web3", "Web3.py for blockchain interaction"),
            ("dotenv", "Environment variable loading"),
            ("rustworkx", "Graph algorithms for route finding"),
        ]
        
        for module, description in critical_deps:
            try:
                __import__(module)
                self.passed.append(f"✅ {module} available - {description}")
            except ImportError:
                self.errors.append(f"❌ Missing dependency: {module} - {description}")
    
    def run_validation(self):
        """Run all validation checks"""
        print("\n" + "=" * 70)
        print("  🔍 REAL-TIME MARKET ANALYSIS CONFIGURATION VALIDATOR")
        print("=" * 70)
        
        self.validate_execution_mode()
        self.validate_real_time_data()
        self.validate_ml_configuration()
        self.validate_rpc_connections()
        self.validate_rust_engine()
        self.validate_signal_output()
        self.validate_dependencies()
        
        # Print summary
        print("\n" + "=" * 70)
        print("  📊 VALIDATION SUMMARY")
        print("=" * 70)
        
        print(f"\n✅ Passed Checks: {len(self.passed)}")
        for item in self.passed:
            print(f"  {item}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings: {len(self.warnings)}")
            for item in self.warnings:
                print(f"  {item}")
        
        if self.errors:
            print(f"\n❌ Errors: {len(self.errors)}")
            for item in self.errors:
                print(f"  {item}")
            print("\n" + "=" * 70)
            print("  ❌ VALIDATION FAILED - Fix errors before running")
            print("=" * 70)
            return False
        else:
            print("\n" + "=" * 70)
            print("  ✅ VALIDATION PASSED - System is configured for real-time analysis")
            print("=" * 70)
            print("\n💡 Next Steps:")
            print("  1. Start the system: python mainnet_orchestrator.py")
            print("  2. Monitor signals: ls -la signals/outgoing/")
            print("  3. Review documentation: cat MAINNET_QUICKSTART.md")
            print("\n" + "=" * 70)
            return True


if __name__ == "__main__":
    validator = ConfigValidator()
    success = validator.run_validation()
    sys.exit(0 if success else 1)
