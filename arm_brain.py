#!/usr/bin/env python3
"""
ARM-Optimized Brain Wrapper
============================

Multiprocessing wrapper for the Titan brain optimized for ARM architecture (4 cores, 24GB RAM).
Distributes chain scanning across multiple processes to maximize parallelism.
"""

import os
import sys
import json
import time
import signal
import logging
import multiprocessing as mp
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Import configuration
config_path = Path(__file__).parent / 'config' / 'arm_optimization.json'
try:
    with open(config_path) as f:
        ARM_CONFIG = json.load(f)
except Exception:
    # Fallback to defaults if config not found
    ARM_CONFIG = {
        "performance": {
            "worker_pool": {"python_workers": 3},
            "memory_limits": {"python_process_mb": 6144},
            "concurrency": {"max_concurrent_scans": 4}
        }
    }

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [ARM-BRAIN] %(message)s'
)
logger = logging.getLogger("ARMBrain")


class ChainScanner:
    """Worker process for scanning a specific chain"""
    
    def __init__(self, chain_id: int, chain_name: str):
        self.chain_id = chain_id
        self.chain_name = chain_name
        
    def scan(self, token_list: List[str]) -> Dict[str, Any]:
        """
        Scan tokens on this chain for arbitrage opportunities.
        This would typically call into the existing brain.py logic.
        """
        logger.info(f"Worker scanning {self.chain_name} (chain {self.chain_id}) with {len(token_list)} tokens")
        
        # Import here to avoid issues with multiprocessing
        try:
            from offchain.ml.brain import OmniBrain
            
            # Create brain instance
            brain = OmniBrain()
            
            # Scan for opportunities (simplified - actual implementation would be more complex)
            opportunities = []
            
            # This is a placeholder - actual implementation would scan the chain
            logger.info(f"Completed scan of {self.chain_name}")
            
            return {
                "chain_id": self.chain_id,
                "chain_name": self.chain_name,
                "opportunities": opportunities,
                "tokens_scanned": len(token_list),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scanning {self.chain_name}: {e}")
            return {
                "chain_id": self.chain_id,
                "chain_name": self.chain_name,
                "error": str(e),
                "opportunities": []
            }


def scan_chain_worker(chain_id: int, chain_name: str, token_list: List[str]) -> Dict[str, Any]:
    """
    Worker function for multiprocessing.
    Scans a single chain and returns results.
    """
    scanner = ChainScanner(chain_id, chain_name)
    return scanner.scan(token_list)


class ARMOptimizedBrain:
    """
    ARM-optimized brain that distributes work across multiple cores.
    Optimized for 4 ARM cores with 24GB RAM.
    """
    
    def __init__(self):
        self.num_workers = ARM_CONFIG["performance"]["worker_pool"]["python_workers"]
        self.max_concurrent = ARM_CONFIG["performance"]["concurrency"]["max_concurrent_scans"]
        
        # Chain configuration
        self.chains = {
            1: "Ethereum",
            137: "Polygon",
            42161: "Arbitrum",
            10: "Optimism",
            8453: "Base",
            56: "BSC",
            43114: "Avalanche"
        }
        
        # Token lists per chain (would be loaded from config in production)
        self.token_lists = self._load_token_lists()
        
        logger.info(f"ARM-Optimized Brain initialized with {self.num_workers} workers")
        logger.info(f"Target architecture: ARM with 4 cores, 24GB RAM")
        
    def _load_token_lists(self) -> Dict[int, List[str]]:
        """Load token lists for each chain"""
        # This is a placeholder - in production would load from actual token lists
        token_lists = {}
        for chain_id in self.chains.keys():
            # Placeholder - would load actual token addresses
            token_lists[chain_id] = []
        return token_lists
    
    def scan_all_chains_parallel(self) -> List[Dict[str, Any]]:
        """
        Scan all chains in parallel using multiprocessing.
        Optimized for 4-core ARM architecture.
        """
        logger.info("Starting parallel chain scanning...")
        
        # Prepare tasks
        tasks = []
        for chain_id, chain_name in self.chains.items():
            token_list = self.token_lists.get(chain_id, [])
            tasks.append((chain_id, chain_name, token_list))
        
        # Execute in parallel using process pool
        results = []
        
        # Use at most num_workers processes
        with mp.Pool(processes=self.num_workers) as pool:
            # Use starmap for multiple arguments
            results = pool.starmap(scan_chain_worker, tasks)
        
        logger.info(f"Completed scanning {len(results)} chains")
        
        return results
    
    def scan_all_chains_sequential(self) -> List[Dict[str, Any]]:
        """
        Scan all chains sequentially (fallback mode).
        """
        logger.info("Starting sequential chain scanning...")
        
        results = []
        for chain_id, chain_name in self.chains.items():
            token_list = self.token_lists.get(chain_id, [])
            result = scan_chain_worker(chain_id, chain_name, token_list)
            results.append(result)
        
        logger.info(f"Completed scanning {len(results)} chains")
        
        return results
    
    def aggregate_opportunities(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate opportunities from all chains.
        """
        total_opportunities = 0
        opportunities_by_chain = {}
        errors = []
        
        for result in results:
            chain_name = result.get("chain_name", "Unknown")
            opportunities = result.get("opportunities", [])
            
            total_opportunities += len(opportunities)
            opportunities_by_chain[chain_name] = len(opportunities)
            
            if "error" in result:
                errors.append({
                    "chain": chain_name,
                    "error": result["error"]
                })
        
        return {
            "total_opportunities": total_opportunities,
            "opportunities_by_chain": opportunities_by_chain,
            "errors": errors,
            "timestamp": datetime.now().isoformat()
        }
    
    def run_continuous_scan(self, interval_seconds: int = 60):
        """
        Run continuous scanning loop.
        """
        logger.info(f"Starting continuous scan with {interval_seconds}s interval")
        
        try:
            while True:
                start_time = time.time()
                
                # Scan all chains in parallel
                results = self.scan_all_chains_parallel()
                
                # Aggregate results
                summary = self.aggregate_opportunities(results)
                
                elapsed_time = time.time() - start_time
                
                logger.info(f"Scan completed in {elapsed_time:.2f}s")
                logger.info(f"Total opportunities: {summary['total_opportunities']}")
                logger.info(f"By chain: {summary['opportunities_by_chain']}")
                
                if summary['errors']:
                    logger.warning(f"Errors encountered: {len(summary['errors'])}")
                
                # Sleep until next interval
                sleep_time = max(0, interval_seconds - elapsed_time)
                if sleep_time > 0:
                    logger.info(f"Sleeping for {sleep_time:.2f}s until next scan")
                    time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            logger.info("Scan interrupted by user")
        except Exception as e:
            logger.error(f"Error in continuous scan: {e}")
            raise


def signal_handler(signum, frame):
    """Handle termination signals"""
    logger.info("Received termination signal, shutting down...")
    sys.exit(0)


def main():
    """Main entry point"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Set multiprocessing start method (important for ARM)
    mp.set_start_method('spawn', force=True)
    
    logger.info("="*70)
    logger.info("ARM-Optimized Titan Brain")
    logger.info("="*70)
    logger.info(f"Architecture: ARM (4 cores, 24GB RAM)")
    logger.info(f"Workers: {ARM_CONFIG['performance']['worker_pool']['python_workers']}")
    logger.info(f"Memory per process: {ARM_CONFIG['performance']['memory_limits']['python_process_mb']} MB")
    logger.info("="*70)
    
    # Create and run brain
    brain = ARMOptimizedBrain()
    brain.run_continuous_scan(interval_seconds=60)


if __name__ == "__main__":
    main()
