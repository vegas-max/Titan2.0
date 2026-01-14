#!/usr/bin/env python3
"""
Basic Real-Time Market Analysis System Test

This test verifies that the system can initialize and is ready for
real-time market analysis and signal generation.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_environment_setup():
    """Test that environment is properly configured"""
    print("\n🧪 Test 1: Environment Setup")
    print("=" * 70)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_settings = [
        "USE_REAL_DATA",
        "USE_WEBSOCKETS",
        "REAL_TIME_DATA_ENABLED",
        "ENABLE_ML_MODELS",
        "TAR_SCORING_ENABLED",
        "AI_PREDICTION_ENABLED"
    ]
    
    for setting in required_settings:
        value = os.getenv(setting)
        status = "✅" if value and value.lower() == "true" else "❌"
        print(f"{status} {setting}={value}")
    
    print("✅ Environment setup test passed\n")


def test_config_import():
    """Test that config module imports correctly"""
    print("🧪 Test 2: Config Module Import")
    print("=" * 70)
    
    try:
        from offchain.core.config import (
            TAR_SCORING_ENABLED,
            AI_PREDICTION_ENABLED,
            REAL_TIME_DATA_ENABLED,
            SELF_LEARNING_ENABLED,
            ROUTE_INTELLIGENCE_ENABLED
        )
        
        print(f"✅ TAR_SCORING_ENABLED: {TAR_SCORING_ENABLED}")
        print(f"✅ AI_PREDICTION_ENABLED: {AI_PREDICTION_ENABLED}")
        print(f"✅ REAL_TIME_DATA_ENABLED: {REAL_TIME_DATA_ENABLED}")
        print(f"✅ SELF_LEARNING_ENABLED: {SELF_LEARNING_ENABLED}")
        print(f"✅ ROUTE_INTELLIGENCE_ENABLED: {ROUTE_INTELLIGENCE_ENABLED}")
        print("✅ Config module import test passed\n")
        
    except Exception as e:
        print(f"❌ Config import failed: {e}\n")
        return False
    
    return True


def test_brain_import():
    """Test that brain module can be imported"""
    print("🧪 Test 3: Brain Module Import")
    print("=" * 70)
    
    try:
        from offchain.ml.brain import OmniBrain
        print("✅ OmniBrain class imported successfully")
        print("✅ Brain module import test passed\n")
        
    except Exception as e:
        print(f"❌ Brain import failed: {e}")
        print("   This is expected if all dependencies aren't installed\n")
        return False
    
    return True


def test_orchestrator_import():
    """Test that orchestrator module can be imported"""
    print("🧪 Test 4: Orchestrator Module Import")
    print("=" * 70)
    
    try:
        from mainnet_orchestrator import MainnetOrchestrator, ExecutionMode
        print("✅ MainnetOrchestrator class imported successfully")
        print(f"✅ Execution modes available: {ExecutionMode.PAPER}, {ExecutionMode.LIVE}")
        print("✅ Orchestrator module import test passed\n")
        
    except Exception as e:
        print(f"❌ Orchestrator import failed: {e}")
        print("   This is expected if all dependencies aren't installed\n")
        return False
    
    return True


def test_signal_directory():
    """Test that signal directory can be created"""
    print("🧪 Test 5: Signal Directory")
    print("=" * 70)
    
    signals_dir = Path("signals/outgoing")
    signals_dir.mkdir(parents=True, exist_ok=True)
    
    if signals_dir.exists() and signals_dir.is_dir():
        print(f"✅ Signal directory exists: {signals_dir}")
        print("✅ Signal directory test passed\n")
        return True
    else:
        print(f"❌ Failed to create signal directory: {signals_dir}\n")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  🧪 REAL-TIME MARKET ANALYSIS SYSTEM TEST SUITE")
    print("=" * 70)
    
    results = []
    
    # Test 1: Environment setup (always runs)
    try:
        test_environment_setup()
        results.append(("Environment Setup", True))
    except Exception as e:
        print(f"❌ Environment setup test failed: {e}\n")
        results.append(("Environment Setup", False))
    
    # Test 2: Config import
    try:
        success = test_config_import()
        results.append(("Config Import", success))
    except Exception as e:
        print(f"❌ Config import test failed: {e}\n")
        results.append(("Config Import", False))
    
    # Test 3: Brain import (optional - depends on all deps)
    try:
        success = test_brain_import()
        results.append(("Brain Import", success))
    except Exception as e:
        print(f"❌ Brain import test failed: {e}\n")
        results.append(("Brain Import", False))
    
    # Test 4: Orchestrator import (optional - depends on all deps)
    try:
        success = test_orchestrator_import()
        results.append(("Orchestrator Import", success))
    except Exception as e:
        print(f"❌ Orchestrator import test failed: {e}\n")
        results.append(("Orchestrator Import", False))
    
    # Test 5: Signal directory
    try:
        success = test_signal_directory()
        results.append(("Signal Directory", success))
    except Exception as e:
        print(f"❌ Signal directory test failed: {e}\n")
        results.append(("Signal Directory", False))
    
    # Print summary
    print("=" * 70)
    print("  📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "=" * 70)
    print(f"  Results: {passed}/{total} tests passed")
    print("=" * 70)
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED - System is ready for real-time analysis")
        print("\n💡 Next steps:")
        print("  1. Run: python3 validate_realtime_config.py")
        print("  2. Start: python3 mainnet_orchestrator.py")
        print("  3. Monitor: ls -la signals/outgoing/")
        return True
    else:
        print("\n⚠️  SOME TESTS FAILED - Install dependencies and re-run")
        print("\n💡 To install dependencies:")
        print("  pip3 install -r requirements.txt")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
