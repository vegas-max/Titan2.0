#!/usr/bin/env python3
"""
OmniArb Rust Engine Python Bridge
Provides Python interface to the high-performance Rust OmniArb engine
"""

import subprocess
import json
import os
import sys
from typing import List, Dict, Optional
import logging

logger = logging.getLogger("OmniArbBridge")


class OmniArbEngine:
    """
    Python bridge to the OmniArb Dual Turbo Rust Engine
    
    This class provides a Python interface to run the Rust engine
    and retrieve high-quality arbitrage opportunities.
    """
    
    def __init__(self, rust_binary_path: Optional[str] = None):
        """
        Initialize the OmniArb Engine bridge
        
        Args:
            rust_binary_path: Path to the compiled Rust binary
                            Defaults to core-rust/target/release/omniarb_engine
        """
        if rust_binary_path is None:
            # Default path relative to project root
            # This file is in offchain/core, so go up 2 levels to project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            self.project_root = project_root
            rust_binary_path = os.path.join(
                project_root, 
                "core-rust", 
                "target", 
                "release", 
                "omniarb_engine"
            )
        else:
            # Calculate project root from provided binary path
            self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(rust_binary_path))))
        
        self.rust_binary = rust_binary_path
        self.available = os.path.exists(rust_binary_path)
        
        if self.available:
            logger.info(f"✅ OmniArb Rust Engine available at {rust_binary_path}")
        else:
            logger.warning(f"⚠️  OmniArb Rust Engine not found at {rust_binary_path}")
            logger.warning("   Run: cd core-rust && cargo build --release --bin omniarb_engine")
    
    def is_available(self) -> bool:
        """Check if the Rust engine is available"""
        return self.available
    
    def run_engine(self, timeout: int = 30) -> Dict:
        """
        Run the OmniArb Rust engine and return results
        
        Args:
            timeout: Maximum execution time in seconds
            
        Returns:
            Dictionary containing:
                - success: bool
                - routes: List of top arbitrage routes
                - stats: Summary statistics
                - raw_output: Raw stdout from engine
        """
        if not self.available:
            return {
                "success": False,
                "error": "Rust engine not available",
                "routes": [],
                "stats": {}
            }
        
        try:
            logger.info("🚀 Running OmniArb Dual Turbo Rust Engine...")
            
            # Calculate project root (4 levels up from binary: binary -> release -> target -> core-rust -> project_root)
            
            result = subprocess.run(
                [self.rust_binary],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.project_root
            )
            
            if result.returncode != 0:
                logger.error(f"❌ Engine failed with exit code {result.returncode}")
                logger.error(f"stderr: {result.stderr}")
                return {
                    "success": False,
                    "error": result.stderr,
                    "routes": [],
                    "stats": {}
                }
            
            # Parse output
            routes = self._parse_output(result.stdout)
            stats = self._extract_stats(result.stdout)
            
            logger.info(f"✅ Engine completed: {len(routes)} high-quality routes found")
            
            return {
                "success": True,
                "routes": routes,
                "stats": stats,
                "raw_output": result.stdout
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Engine timeout after {timeout}s")
            return {
                "success": False,
                "error": "Timeout",
                "routes": [],
                "stats": {}
            }
        except Exception as e:
            logger.error(f"❌ Engine error: {e}")
            return {
                "success": False,
                "error": str(e),
                "routes": [],
                "stats": {}
            }
    
    def _parse_output(self, output: str) -> List[Dict]:
        """
        Parse the Rust engine output into structured route data
        
        Returns:
            List of route dictionaries with keys:
                - chain_origin, chain_dest, token, bridge
                - tar_score, onnx_score, flanker_score, liquidity
        """
        routes = []
        in_routes_section = False
        
        for line in output.split('\n'):
            line = line.strip()
            
            if "🔥 Top Arbitrage Routes" in line:
                in_routes_section = True
                continue
            
            if in_routes_section and line.startswith("Chain-"):
                # Parse route line
                parts = line.split()
                if len(parts) >= 8:
                    try:
                        route = {
                            "chain_origin": int(parts[0].replace("Chain-", "")),
                            "chain_dest": int(parts[1].replace("Chain-", "")),
                            "token": parts[2],
                            "bridge": parts[3],
                            "tar_score": float(parts[4]),
                            "onnx_score": float(parts[5]),
                            "flanker_score": float(parts[6]),
                            "liquidity": float(parts[7])
                        }
                        routes.append(route)
                    except (ValueError, IndexError) as e:
                        logger.warning(
                            f"Failed to parse route line: {line}\n"
                            f"  Error: {e}\n"
                            f"  Expected format: Chain-<origin> Chain-<dest> <token> <bridge> <tar> <onnx> <flanker> <liquidity>"
                        )
            
            if "📊 Summary Statistics" in line:
                in_routes_section = False
        
        return routes
    
    def _extract_stats(self, output: str) -> Dict:
        """Extract summary statistics from output"""
        stats = {
            "total_routes": 0,
            "high_quality_routes": 0,
            "average_tar_score": 0.0
        }
        
        for line in output.split('\n'):
            if "Total routes analyzed:" in line:
                stats["total_routes"] = int(line.split(':')[-1].strip())
            elif "High-quality routes" in line:
                stats["high_quality_routes"] = int(line.split(':')[-1].strip())
            elif "Average TAR score" in line:
                stats["average_tar_score"] = float(line.split(':')[-1].strip())
        
        return stats
    
    def get_top_opportunities(self, min_tar_score: float = 85.0, limit: int = 10) -> List[Dict]:
        """
        Get top arbitrage opportunities from the Rust engine
        
        Args:
            min_tar_score: Minimum TAR score threshold
            limit: Maximum number of routes to return
            
        Returns:
            List of top opportunities sorted by TAR score
        """
        result = self.run_engine()
        
        if not result["success"]:
            logger.warning(f"Engine failed: {result.get('error', 'Unknown error')}")
            return []
        
        routes = result["routes"]
        
        # Filter by minimum TAR score
        filtered = [r for r in routes if r["tar_score"] >= min_tar_score]
        
        # Sort by TAR score descending
        filtered.sort(key=lambda r: r["tar_score"], reverse=True)
        
        # Limit results
        return filtered[:limit]


def main():
    """Test the OmniArb engine bridge"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s'
    )
    
    print("=" * 80)
    print("  OmniArb Rust Engine Python Bridge - Test")
    print("=" * 80)
    print()
    
    engine = OmniArbEngine()
    
    if not engine.is_available():
        print("❌ Rust engine not available")
        print("   Build it with: cd core-rust && cargo build --release --bin omniarb_engine")
        sys.exit(1)
    
    print("Running engine...")
    print()
    
    result = engine.run_engine()
    
    if result["success"]:
        print("✅ Engine completed successfully")
        print()
        print(f"📊 Statistics:")
        print(f"   Total routes analyzed: {result['stats']['total_routes']}")
        print(f"   High-quality routes: {result['stats']['high_quality_routes']}")
        print(f"   Average TAR score: {result['stats']['average_tar_score']:.2f}")
        print()
        
        routes = result["routes"]
        if routes:
            print(f"🔥 Top {len(routes)} Routes:")
            print("-" * 80)
            for i, route in enumerate(routes[:5], 1):
                print(f"{i}. Chain {route['chain_origin']} → Chain {route['chain_dest']}")
                print(f"   Token: {route['token']}, Bridge: {route['bridge']}")
                print(f"   TAR: {route['tar_score']:.2f}, ONNX: {route['onnx_score']:.2f}, "
                      f"Flanker: {route['flanker_score']:.2f}")
                print()
    else:
        print(f"❌ Engine failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
