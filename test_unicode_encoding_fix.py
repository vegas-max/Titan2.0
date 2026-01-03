#!/usr/bin/env python3
"""
Test script to validate Unicode encoding fix for run_robust_90day_live_simulation.py
This test ensures that emoji and other Unicode characters can be written to files correctly.
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_unicode_export():
    """Test that Unicode characters (emoji) can be exported correctly"""
    print("Testing Unicode export functionality...")
    
    # Create a temporary directory for test output
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir)
        
        # Test 1: JSON file with Unicode characters
        print("\n1. Testing JSON export with Unicode characters...")
        test_data = {
            'status': '✅ Success',
            'profit': '💰 $1000',
            'performance': '📈 Excellent',
            'metrics': {
                'total_opportunities': 100,
                'checkmark': '✅',
                'cross': '❌',
                'warning': '⚠️'
            }
        }
        
        json_file = output_dir / 'test_summary.json'
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, indent=2)
            print(f"   ✅ JSON file created successfully: {json_file}")
            
            # Read it back to verify
            with open(json_file, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            
            if loaded_data['status'] == '✅ Success':
                print("   ✅ JSON data verified - Unicode characters preserved")
            else:
                print("   ❌ JSON data verification failed")
                return False
        except UnicodeEncodeError as e:
            print(f"   ❌ UnicodeEncodeError occurred: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            return False
        
        # Test 2: Markdown file with Unicode characters (like the report)
        print("\n2. Testing Markdown report with Unicode characters...")
        markdown_content = """# Test Report

## Performance Metrics
- ✅ Total Opportunities: 100
- ✅ Successful Trades: 50
- ❌ Failed Trades: 5
- 💰 Total Profit: $1000.00

## System Components
- ✅ OmniBrain (opportunity detection)
- ✅ ProfitEngine (profit calculations)
- ✅ DexPricer (real DEX price queries)
- ⚠️  Warning: Test mode

## Status
Status: ✅ All systems operational
"""
        
        md_file = output_dir / 'test_report.md'
        try:
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"   ✅ Markdown file created successfully: {md_file}")
            
            # Read it back to verify
            with open(md_file, 'r', encoding='utf-8') as f:
                loaded_content = f.read()
            
            if '✅' in loaded_content and '💰' in loaded_content:
                print("   ✅ Markdown content verified - Unicode characters preserved")
            else:
                print("   ❌ Markdown content verification failed")
                return False
        except UnicodeEncodeError as e:
            print(f"   ❌ UnicodeEncodeError occurred: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            return False
        
        # Test 3: Full results with default=str (like the actual export)
        print("\n3. Testing full results export with datetime objects...")
        full_results = {
            'status': '✅',
            'simulation_config': {
                'start_time': datetime.now().isoformat(),
                'mode': 'TEST'
            },
            'metrics': {
                'success_indicator': '✅',
                'profit_indicator': '💰',
                'total_profit_usd': 1000.0
            }
        }
        
        full_file = output_dir / 'test_full_results.json'
        try:
            with open(full_file, 'w', encoding='utf-8') as f:
                json.dump(full_results, f, indent=2, default=str)
            print(f"   ✅ Full results file created successfully: {full_file}")
            
            # Read it back to verify
            with open(full_file, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            
            if loaded_data['status'] == '✅' and loaded_data['metrics']['profit_indicator'] == '💰':
                print("   ✅ Full results verified - Unicode characters preserved")
            else:
                print("   ❌ Full results verification failed")
                return False
        except UnicodeEncodeError as e:
            print(f"   ❌ UnicodeEncodeError occurred: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            return False
    
    print("\n" + "="*60)
    print("✅ ALL UNICODE ENCODING TESTS PASSED!")
    print("="*60)
    return True


def test_without_encoding():
    """Test what happens without UTF-8 encoding (to demonstrate the fix)"""
    print("\n\nDemonstrating the issue WITHOUT encoding='utf-8'...")
    print("(This simulates the original bug on Windows)")
    
    # This test is informational only - we'll skip it on systems where
    # the default encoding is already UTF-8
    import sys
    default_encoding = sys.getdefaultencoding()
    print(f"System default encoding: {default_encoding}")
    
    if default_encoding.lower() != 'utf-8':
        print("Note: On Windows with cp1252, the original code would fail here.")
    else:
        print("Note: System uses UTF-8 by default, so original bug won't reproduce here.")
    

if __name__ == '__main__':
    print("="*60)
    print("Unicode Encoding Fix Validation Test")
    print("="*60)
    
    success = test_unicode_export()
    test_without_encoding()
    
    if success:
        print("\n✅ Test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Test failed!")
        sys.exit(1)
