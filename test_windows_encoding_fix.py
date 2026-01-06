#!/usr/bin/env python3
"""
Test Windows UTF-8 Encoding Fix
================================

This test validates that the UTF-8 encoding fix properly handles emoji
and Unicode characters on Windows systems with cp1252 encoding.

The fix configures stdout/stderr to use UTF-8 encoding before any logging
is initialized, which allows emoji characters to be logged correctly.
"""

import sys
import os

def test_utf8_configuration():
    """Test that UTF-8 configuration is applied correctly"""
    print("Testing UTF-8 configuration...")
    
    # Check if stdout has UTF-8 encoding
    if hasattr(sys.stdout, 'encoding'):
        print(f"  Stdout encoding: {sys.stdout.encoding}")
        if sys.stdout.encoding.lower() in ['utf-8', 'utf8']:
            print("  ✅ Stdout is using UTF-8 encoding")
        else:
            print(f"  ⚠️  Stdout encoding is {sys.stdout.encoding}, not UTF-8")
    
    # Check PYTHONIOENCODING environment variable
    if 'PYTHONIOENCODING' in os.environ:
        print(f"  PYTHONIOENCODING: {os.environ['PYTHONIOENCODING']}")
        print("  ✅ PYTHONIOENCODING is set")
    else:
        print("  ⚠️  PYTHONIOENCODING not set (may be ok on non-Windows)")
    
    print()


def test_emoji_output():
    """Test that emoji can be printed correctly"""
    print("Testing emoji output...")
    
    test_emojis = [
        ("🚀", "rocket"),
        ("✅", "checkmark"),
        ("🔨", "hammer"),
        ("🦀", "crab"),
        ("🎮", "game controller"),
        ("🛑", "stop sign"),
        ("🔍", "magnifying glass"),
        ("⚠️", "warning"),
        ("❌", "cross mark"),
        ("💰", "money bag"),
        ("📊", "chart"),
        ("🧪", "test tube"),
        ("📈", "chart increasing"),
    ]
    
    try:
        for emoji, name in test_emojis:
            print(f"  {emoji} {name}")
        print("  ✅ All emoji printed successfully")
    except UnicodeEncodeError as e:
        print(f"  ❌ UnicodeEncodeError: {e}")
        return False
    
    print()
    return True


def test_module_imports():
    """Test that modules with UTF-8 fixes import correctly"""
    print("Testing module imports with UTF-8 fix...")
    
    modules_to_test = [
        ("agents.super_agent_manager", "SuperAgentManager"),
        ("agents.specialized.orchestrator_agent", "OrchestratorAgent"),
    ]
    
    all_passed = True
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"  ✅ {module_name}.{class_name} imported successfully")
        except Exception as e:
            print(f"  ❌ Failed to import {module_name}.{class_name}: {e}")
            all_passed = False
    
    print()
    return all_passed


def test_logging_with_emoji():
    """Test that logging with emoji works correctly"""
    print("Testing logging with emoji...")
    
    import logging
    import tempfile
    from pathlib import Path
    
    # Create a temporary log file
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = Path(temp_dir) / 'test_emoji.log'
        
        # Configure logging
        test_logger = logging.Logger("TestLogger")
        test_logger.setLevel(logging.INFO)
        
        # File handler with UTF-8
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setFormatter(logging.Formatter('%(message)s'))
        
        # Stream handler (uses reconfigured stdout)
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(logging.Formatter('%(message)s'))
        
        test_logger.addHandler(fh)
        test_logger.addHandler(sh)
        
        # Test logging emoji
        test_messages = [
            "🚀 Starting test...",
            "✅ Test passed",
            "🔨 Building project...",
            "💰 Total profit: $1000",
        ]
        
        try:
            print("  Logging emoji messages:")
            for msg in test_messages:
                test_logger.info(f"    {msg}")
            print("  ✅ Logging with emoji successful")
            
            # Verify file contents
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if '🚀' in content and '✅' in content:
                print("  ✅ Log file contains emoji correctly")
            else:
                print("  ❌ Log file missing emoji")
                return False
            
        except UnicodeEncodeError as e:
            print(f"  ❌ UnicodeEncodeError during logging: {e}")
            return False
    
    print()
    return True


def main():
    """Run all tests"""
    print("="*70)
    print("Windows UTF-8 Encoding Fix Validation")
    print("="*70)
    print(f"Platform: {sys.platform}")
    print(f"Python version: {sys.version}")
    print(f"Default encoding: {sys.getdefaultencoding()}")
    print("="*70)
    print()
    
    # Run tests
    test_utf8_configuration()
    
    result1 = test_emoji_output()
    result2 = test_module_imports()
    result3 = test_logging_with_emoji()
    
    print("="*70)
    if result1 and result2 and result3:
        print("✅ ALL TESTS PASSED")
        print("="*70)
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("="*70)
        return 1


if __name__ == '__main__':
    sys.exit(main())
