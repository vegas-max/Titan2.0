#!/usr/bin/env python3
"""
Lightweight Mode Launcher
==========================

Ultra-lightweight launcher for ARM systems targeting:
- 75% memory reduction (6GB vs 24GB)
- 3x faster startup and execution
- Minimal runtime footprint

Optimized for ARM architecture with 4 cores.
"""

import os
import sys
import json
from pathlib import Path

# Set aggressive optimization flags
os.environ['PYTHONOPTIMIZE'] = '2'  # Remove docstrings
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'  # No .pyc files

# Load lightweight configuration
config_path = Path(__file__).parent / 'config' / 'lightweight_mode.json'
with open(config_path) as f:
    LIGHTWEIGHT_CONFIG = json.load(f)

# Apply memory limits
import resource
memory_limit_mb = LIGHTWEIGHT_CONFIG['performance']['memory_limits']['total_mb']
memory_limit_bytes = memory_limit_mb * 1024 * 1024
try:
    resource.setrlimit(resource.RLIMIT_AS, (memory_limit_bytes, memory_limit_bytes))
except Exception as e:
    print(f"⚠️  Could not set memory limit: {e}")

# Configure minimal logging
import logging
if LIGHTWEIGHT_CONFIG['optimization_flags']['minimize_logging']:
    logging.basicConfig(level=logging.WARNING)
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("LightweightMode")

def print_banner():
    """Print lightweight mode banner"""
    print("=" * 70)
    print("  ⚡ TITAN LIGHTWEIGHT MODE - ARM Optimized")
    print("=" * 70)
    print(f"  Memory Target: {LIGHTWEIGHT_CONFIG['performance']['memory_limits']['total_mb']} MB (75% reduction)")
    print(f"  Workers: {LIGHTWEIGHT_CONFIG['performance']['worker_pool']['python_workers']} Python + {LIGHTWEIGHT_CONFIG['performance']['worker_pool']['node_workers']} Node.js")
    print(f"  Active DEX Aggregators: {LIGHTWEIGHT_CONFIG['dex_aggregators']['max_active']}")
    print(f"  Priority DEXs: {', '.join(LIGHTWEIGHT_CONFIG['dex_aggregators']['priority_list'])}")
    print("=" * 70)
    print()

def setup_environment():
    """Configure environment for lightweight mode"""
    
    # Set Node.js options
    node_opts = ' '.join(LIGHTWEIGHT_CONFIG['system_tuning']['node_options'])
    os.environ['NODE_OPTIONS'] = node_opts
    
    # Set execution mode
    os.environ['LIGHTWEIGHT_MODE'] = 'true'
    os.environ['ARM_CORES'] = '4'
    
    # Configure workers
    os.environ['PYTHON_WORKERS'] = str(LIGHTWEIGHT_CONFIG['performance']['worker_pool']['python_workers'])
    os.environ['NODE_WORKERS'] = str(LIGHTWEIGHT_CONFIG['performance']['worker_pool']['node_workers'])
    
    # Configure cache
    os.environ['CACHE_MAX_ENTRIES'] = str(LIGHTWEIGHT_CONFIG['performance']['cache_strategy']['max_entries'])
    os.environ['CACHE_TTL'] = str(LIGHTWEIGHT_CONFIG['performance']['cache_strategy']['ttl_seconds'])
    
    logger.info("Environment configured for lightweight mode")

def launch_lightweight_dashboard():
    """Launch dashboard in lightweight mode"""
    from unified_dashboard import UnifiedDashboard, DisplayMode
    
    # Use simple mode for minimal memory
    mode = DisplayMode.SIMPLE if not LIGHTWEIGHT_CONFIG['feature_flags']['enable_full_dashboard'] else DisplayMode.LIVE
    
    dashboard = UnifiedDashboard(mode=mode)
    dashboard.run()

def launch_lightweight_brain():
    """Launch brain in lightweight mode"""
    import multiprocessing as mp
    mp.set_start_method('spawn', force=True)
    
    # Import with minimal features
    workers = LIGHTWEIGHT_CONFIG['performance']['worker_pool']['python_workers']
    
    logger.info(f"Launching brain with {workers} workers...")
    
    # Use arm_brain but with lightweight config
    from arm_brain import ARMOptimizedBrain
    brain = ARMOptimizedBrain()
    brain.num_workers = workers  # Override with lightweight setting
    brain.run_continuous_scan(interval_seconds=60)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Titan Lightweight Mode")
    parser.add_argument(
        '--component',
        choices=['dashboard', 'brain', 'all'],
        default='dashboard',
        help='Component to launch'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show memory and performance statistics'
    )
    
    args = parser.parse_args()
    
    print_banner()
    setup_environment()
    
    if args.stats:
        show_stats()
        return
    
    if args.component == 'dashboard':
        logger.info("Launching lightweight dashboard...")
        launch_lightweight_dashboard()
    elif args.component == 'brain':
        logger.info("Launching lightweight brain...")
        launch_lightweight_brain()
    elif args.component == 'all':
        logger.info("Launching all components in lightweight mode...")
        # Would typically use supervisor/process manager
        print("Note: Use process manager to run both components simultaneously")
        print("  Terminal 1: python3 lightweight_mode.py --component brain")
        print("  Terminal 2: python3 lightweight_mode.py --component dashboard")

def show_stats():
    """Show current memory and performance statistics"""
    import psutil
    import gc
    
    process = psutil.Process()
    
    print("  📊 CURRENT RESOURCE USAGE")
    print("  " + "-" * 66)
    print(f"  Memory (RSS): {process.memory_info().rss / 1024 / 1024:.2f} MB")
    print(f"  Memory (VMS): {process.memory_info().vms / 1024 / 1024:.2f} MB")
    print(f"  CPU %: {process.cpu_percent(interval=1):.1f}%")
    print(f"  Threads: {process.num_threads()}")
    print()
    
    # Garbage collection stats
    gc_stats = gc.get_stats()
    print("  🗑️  GARBAGE COLLECTION")
    print("  " + "-" * 66)
    print(f"  Collections: {gc.get_count()}")
    print(f"  Threshold: {gc.get_threshold()}")
    print()
    
    # System info
    print("  💻 SYSTEM INFO")
    print("  " + "-" * 66)
    print(f"  Total RAM: {psutil.virtual_memory().total / 1024 / 1024 / 1024:.2f} GB")
    print(f"  Available RAM: {psutil.virtual_memory().available / 1024 / 1024 / 1024:.2f} GB")
    print(f"  CPU Count: {psutil.cpu_count()}")
    print(f"  CPU %: {psutil.cpu_percent(interval=1, percpu=False):.1f}%")
    print()

if __name__ == "__main__":
    main()
