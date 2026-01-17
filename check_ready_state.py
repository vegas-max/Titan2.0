#!/usr/bin/env python3
"""
Simple script to check if the system is ready for benchmarking and live trading.
Returns exit code 0 if ready, 1 if not ready.
"""
import json
import sys
from pathlib import Path

def check_ready_state():
    """Check if the system is ready for benchmarking and live trading"""
    config_path = Path('config.json')
    
    if not config_path.exists():
        print("❌ config.json not found")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        system_status = config.get('system_status', {})
        ready_state = system_status.get('ready_for_benchmarking_and_live_trading', False)
        status_message = system_status.get('status_message', 'No status message')
        last_validated = system_status.get('last_validated', 'Never')
        
        print("\n" + "="*70)
        print("  🎯 SYSTEM READY STATE CHECK")
        print("="*70)
        
        if ready_state:
            print("  ✅ READY FOR BENCHMARKING AND LIVE TRADING: TRUE")
        else:
            print("  ❌ READY FOR BENCHMARKING AND LIVE TRADING: FALSE")
        
        print(f"  Status Message: {status_message}")
        print(f"  Last Validated: {last_validated}")
        print("="*70)
        print()
        
        return ready_state
        
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Error reading config: {e}")
        return False

if __name__ == "__main__":
    ready = check_ready_state()
    sys.exit(0 if ready else 1)
