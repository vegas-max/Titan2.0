"""
Parallel Route Simulation Engine
Simulates 10+ trading routes simultaneously for optimal path selection
"""

import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Tuple
from decimal import Decimal, getcontext
import time
from dataclasses import dataclass, field

logger = logging.getLogger("ParallelSimulator")
getcontext().prec = 28


@dataclass
class RouteSimulationResult:
    """Result of a single route simulation"""
    route_id: str
    path: List[str]  # Token addresses
    dexes: List[str]  # DEX names
    estimated_output: Decimal
    gas_estimate: int
    expected_profit: Decimal
    price_impact: Decimal
    success: bool
    error: Optional[str] = None
    simulation_time: float = 0.0
    score: Decimal = field(init=False)
    
    def __post_init__(self):
        """Calculate route score after initialization"""
        self.calculate_score()
    
    def calculate_score(self):
        """
        Calculate route score based on multiple factors
        Score = profit * (1 - price_impact/100) * (1 / gas_cost_factor)
        """
        if not self.success or self.expected_profit <= 0:
            self.score = Decimal('0')
            return
        
        # Normalize price impact (lower is better)
        impact_penalty = Decimal('1') - (self.price_impact / Decimal('100'))
        impact_penalty = max(Decimal('0'), impact_penalty)
        
        # Normalize gas cost (lower is better)
        # Assume base gas is 100k, anything above reduces score
        gas_factor = Decimal('100000') / max(Decimal(self.gas_estimate), Decimal('100000'))
        
        # Calculate final score
        self.score = self.expected_profit * impact_penalty * gas_factor
        
        logger.debug(f"Route {self.route_id} score: {self.score} (profit={self.expected_profit}, impact={self.price_impact}%, gas={self.gas_estimate})")


class ParallelSimulationEngine:
    """
    Parallel simulation engine for testing multiple trading routes simultaneously
    """
    
    def __init__(self, max_workers: int = 20):
        """
        Initialize parallel simulation engine
        
        Args:
            max_workers: Maximum number of parallel workers (default: 20)
        """
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.simulation_cache = {}
        self.cache_duration = 5  # Cache results for 5 seconds
        
    def simulate_route(
        self,
        route_id: str,
        path: List[str],
        dexes: List[str],
        amount_in: Decimal,
        simulator_func,
        **kwargs
    ) -> RouteSimulationResult:
        """
        Simulate a single trading route
        
        Args:
            route_id: Unique route identifier
            path: List of token addresses in the route
            dexes: List of DEX names for each hop
            amount_in: Input amount to simulate
            simulator_func: Function to call for simulation (e.g., omniSDK.simulate)
            **kwargs: Additional arguments for simulator
            
        Returns:
            RouteSimulationResult object
        """
        start_time = time.time()
        
        try:
            # Check cache
            cache_key = f"{route_id}_{amount_in}"
            if cache_key in self.simulation_cache:
                cached_result, cached_time = self.simulation_cache[cache_key]
                if time.time() - cached_time < self.cache_duration:
                    logger.debug(f"Using cached simulation for route {route_id}")
                    return cached_result
            
            # Run simulation
            logger.debug(f"Simulating route {route_id}: {' -> '.join(dexes)}")
            
            result = simulator_func(
                path=path,
                dexes=dexes,
                amount_in=amount_in,
                **kwargs
            )
            
            # Parse result
            if result.get('success'):
                sim_result = RouteSimulationResult(
                    route_id=route_id,
                    path=path,
                    dexes=dexes,
                    estimated_output=Decimal(str(result.get('amountOut', 0))),
                    gas_estimate=result.get('gasEstimate', 300000),
                    expected_profit=Decimal(str(result.get('profit', 0))),
                    price_impact=Decimal(str(result.get('priceImpact', 0))),
                    success=True,
                    simulation_time=time.time() - start_time
                )
            else:
                sim_result = RouteSimulationResult(
                    route_id=route_id,
                    path=path,
                    dexes=dexes,
                    estimated_output=Decimal('0'),
                    gas_estimate=0,
                    expected_profit=Decimal('0'),
                    price_impact=Decimal('100'),
                    success=False,
                    error=result.get('error', 'Unknown error'),
                    simulation_time=time.time() - start_time
                )
            
            # Cache result
            self.simulation_cache[cache_key] = (sim_result, time.time())
            
            return sim_result
            
        except Exception as e:
            logger.error(f"Simulation failed for route {route_id}: {e}")
            return RouteSimulationResult(
                route_id=route_id,
                path=path,
                dexes=dexes,
                estimated_output=Decimal('0'),
                gas_estimate=0,
                expected_profit=Decimal('0'),
                price_impact=Decimal('100'),
                success=False,
                error=str(e),
                simulation_time=time.time() - start_time
            )
    
    def simulate_routes_parallel(
        self,
        routes: List[Dict],
        amount_in: Decimal,
        simulator_func,
        **kwargs
    ) -> List[RouteSimulationResult]:
        """
        Simulate multiple routes in parallel
        
        Args:
            routes: List of route dictionaries containing:
                - route_id: str
                - path: List[str]
                - dexes: List[str]
            amount_in: Input amount for all routes
            simulator_func: Simulation function
            **kwargs: Additional arguments for simulator
            
        Returns:
            List of RouteSimulationResult objects sorted by score (best first)
        """
        logger.info(f"🔄 Simulating {len(routes)} routes in parallel...")
        
        start_time = time.time()
        futures = []
        
        # Submit all simulations to thread pool
        for route in routes:
            future = self.executor.submit(
                self.simulate_route,
                route['route_id'],
                route['path'],
                route['dexes'],
                amount_in,
                simulator_func,
                **kwargs
            )
            futures.append(future)
        
        # Collect results as they complete
        results = []
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
                
                if result.success:
                    logger.info(f"✅ Route {result.route_id}: Profit=${result.expected_profit} Impact={result.price_impact}% Gas={result.gas_estimate}")
                else:
                    logger.debug(f"❌ Route {result.route_id}: Failed - {result.error}")
                    
            except Exception as e:
                logger.error(f"Failed to get simulation result: {e}")
        
        # Sort by score (best first)
        results.sort(key=lambda x: x.score, reverse=True)
        
        elapsed = time.time() - start_time
        successful = sum(1 for r in results if r.success)
        
        logger.info(f"✅ Parallel simulation complete: {successful}/{len(routes)} successful in {elapsed:.2f}s")
        
        return results
    
    def get_best_route(
        self,
        routes: List[Dict],
        amount_in: Decimal,
        simulator_func,
        min_profit: Decimal = Decimal('0'),
        max_price_impact: Decimal = Decimal('5'),
        **kwargs
    ) -> Optional[RouteSimulationResult]:
        """
        Get the best route based on simulation results
        
        Args:
            routes: List of route dictionaries
            amount_in: Input amount
            simulator_func: Simulation function
            min_profit: Minimum acceptable profit
            max_price_impact: Maximum acceptable price impact (%)
            **kwargs: Additional arguments
            
        Returns:
            Best RouteSimulationResult or None if no viable routes
        """
        results = self.simulate_routes_parallel(
            routes,
            amount_in,
            simulator_func,
            **kwargs
        )
        
        # Filter by constraints
        viable_routes = [
            r for r in results
            if r.success
            and r.expected_profit >= min_profit
            and r.price_impact <= max_price_impact
        ]
        
        if not viable_routes:
            logger.warning("⚠️ No viable routes found matching criteria")
            return None
        
        best_route = viable_routes[0]  # Already sorted by score
        
        logger.info(f"🎯 Best route selected: {best_route.route_id}")
        logger.info(f"   Profit: ${best_route.expected_profit}")
        logger.info(f"   Impact: {best_route.price_impact}%")
        logger.info(f"   Gas: {best_route.gas_estimate}")
        logger.info(f"   Score: {best_route.score}")
        
        return best_route
    
    def simulate_with_different_amounts(
        self,
        route: Dict,
        amounts: List[Decimal],
        simulator_func,
        **kwargs
    ) -> List[RouteSimulationResult]:
        """
        Simulate the same route with different input amounts
        Useful for finding optimal trade size
        
        Args:
            route: Route dictionary
            amounts: List of amounts to test
            simulator_func: Simulation function
            **kwargs: Additional arguments
            
        Returns:
            List of results for each amount
        """
        logger.info(f"🔍 Testing route {route['route_id']} with {len(amounts)} different amounts...")
        
        futures = []
        for amount in amounts:
            future = self.executor.submit(
                self.simulate_route,
                f"{route['route_id']}_amt{amount}",
                route['path'],
                route['dexes'],
                amount,
                simulator_func,
                **kwargs
            )
            futures.append((amount, future))
        
        results = []
        for amount, future in futures:
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to simulate with amount {amount}: {e}")
        
        # Sort by profit
        results.sort(key=lambda x: x.expected_profit, reverse=True)
        
        if results and results[0].success:
            logger.info(f"💰 Optimal amount: {amounts[0]} -> Profit=${results[0].expected_profit}")
        
        return results
    
    def clear_cache(self):
        """Clear simulation cache"""
        self.simulation_cache = {}
        logger.info("🧹 Simulation cache cleared")
    
    def shutdown(self):
        """Shutdown the executor"""
        self.executor.shutdown(wait=True)
        logger.info("🛑 Parallel simulation engine shut down")


# Example usage
if __name__ == "__main__":
    # This is just an example - actual simulator_func needs to be provided
    def mock_simulator(path, dexes, amount_in, **kwargs):
        """Mock simulator for testing"""
        import random
        return {
            'success': random.choice([True, False]),
            'amountOut': float(amount_in) * random.uniform(0.95, 1.05),
            'gasEstimate': random.randint(200000, 400000),
            'profit': float(amount_in) * random.uniform(-0.01, 0.03),
            'priceImpact': random.uniform(0, 3)
        }
    
    # Create engine
    engine = ParallelSimulationEngine(max_workers=10)
    
    # Create test routes
    routes = [
        {
            'route_id': 'route_1',
            'path': ['USDC', 'WETH', 'USDT'],
            'dexes': ['uniswap', 'sushiswap']
        },
        {
            'route_id': 'route_2',
            'path': ['USDC', 'DAI', 'USDT'],
            'dexes': ['curve', 'curve']
        },
        {
            'route_id': 'route_3',
            'path': ['USDC', 'WETH', 'WBTC', 'USDT'],
            'dexes': ['uniswap', 'sushiswap', 'balancer']
        }
    ]
    
    # Simulate
    best = engine.get_best_route(
        routes,
        Decimal('10000'),
        mock_simulator,
        min_profit=Decimal('5')
    )
    
    if best:
        print(f"Best route: {best.route_id} with profit ${best.expected_profit}")
    
    engine.shutdown()
