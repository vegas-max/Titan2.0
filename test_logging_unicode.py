#!/usr/bin/env python3
"""
Test script to validate Unicode encoding fix for logging with emoji characters.
This test ensures that emoji and other Unicode characters can be logged correctly
on all platforms, including Windows with cp1252 encoding.
"""

import os
import sys
import logging
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_logging_unicode():
    """Test that Unicode characters (emoji) can be logged correctly"""
    print("Testing logging with Unicode characters (emoji)...")
    
    # Create a temporary directory for test log files
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = Path(temp_dir)
        log_file = log_dir / 'test_emoji_log.log'
        
        # Configure logging with UTF-8 encoding (like the fixed code)
        print("\n1. Setting up logger with UTF-8 encoding...")
        test_logger = logging.Logger("TestLogger")
        test_logger.setLevel(logging.INFO)
        
        # Create handlers with UTF-8 encoding
        file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - [%(name)s] %(message)s'))
        
        # For stream handler, we need to ensure stdout is UTF-8 compatible
        if sys.platform == 'win32':
            # On Windows, reconfigure stdout to use UTF-8
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - [%(name)s] %(message)s'))
        
        test_logger.addHandler(file_handler)
        test_logger.addHandler(stream_handler)
        
        # Test logging various emoji characters
        test_cases = [
            ("🎮 Entering interactive mode...", "game controller"),
            ("🚀 APEX-OMEGA TITAN: SUPER AGENT SYSTEM", "rocket"),
            ("✅ Super agent system initialized successfully", "checkmark"),
            ("🔍 Running system health check...", "magnifying glass"),
            ("🛑 Stopping Titan system...", "stop sign"),
            ("🧪 Running tests...", "test tube"),
            ("🔨 Building project...", "hammer"),
            ("📊 SYSTEM STATUS", "chart"),
            ("💰 Profit calculation", "money bag"),
            ("⚠️  Warning message", "warning sign"),
        ]
        
        print("   Testing emoji logging...")
        try:
            for message, description in test_cases:
                test_logger.info(message)
                print(f"   ✅ Logged: {description}")
        except UnicodeEncodeError as e:
            print(f"   ❌ UnicodeEncodeError occurred: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            return False
        
        # Verify the log file contains the emoji
        print("\n2. Verifying log file contents...")
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            # Check for some key emoji
            if '🎮' in log_content and '🚀' in log_content and '✅' in log_content:
                print("   ✅ Log file verified - Unicode characters preserved")
            else:
                print("   ❌ Log file verification failed - emoji not found")
                return False
        except Exception as e:
            print(f"   ❌ Error reading log file: {e}")
            return False
    
    print("\n" + "="*60)
    print("✅ ALL LOGGING UNICODE TESTS PASSED!")
    print("="*60)
    return True


def test_super_agent_manager_import():
    """Test that super_agent_manager.py can be imported without errors"""
    print("\n\nTesting super_agent_manager.py import...")
    
    try:
        # This will execute the UTF-8 configuration at the top of the file
        from agents.super_agent_manager import SuperAgentManager
        print("   ✅ SuperAgentManager imported successfully")
        
        # Create an instance (this will call setup_logging)
        print("   Creating SuperAgentManager instance...")
        manager = SuperAgentManager()
        print("   ✅ SuperAgentManager instance created successfully")
        
        # Try logging an emoji message
        print("   Testing emoji logging through SuperAgentManager logger...")
        manager.logger.info("🎮 Test emoji message")
        print("   ✅ Emoji logged successfully")
        
        return True
    except UnicodeEncodeError as e:
        print(f"   ❌ UnicodeEncodeError occurred: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("="*60)
    print("Logging Unicode Encoding Fix Validation Test")
    print("="*60)
    print(f"Platform: {sys.platform}")
    print(f"Default encoding: {sys.getdefaultencoding()}")
    if hasattr(sys.stdout, 'encoding'):
        print(f"Stdout encoding: {sys.stdout.encoding}")
    print("="*60)
    
    test1_success = test_logging_unicode()
    test2_success = test_super_agent_manager_import()
    
    if test1_success and test2_success:
        print("\n✅ All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
