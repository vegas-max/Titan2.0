#!/usr/bin/env python3
"""
TITAN Multi-Page Interactive Dashboard Server
==============================================

Real-time dashboard server with WebSocket support for live updates.
Provides multi-page interface for monitoring and controlling the TITAN system.
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from collections import deque, defaultdict

try:
    from aiohttp import web
    import aiohttp_cors
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    print("WARNING: aiohttp not installed. Install with: pip install aiohttp aiohttp-cors")

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    try:
        import redis
        REDIS_AVAILABLE = True
    except ImportError:
        REDIS_AVAILABLE = False
        print("WARNING: redis not installed. Install with: pip install redis")

from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DashboardServer:
    """
    Multi-page dashboard server with real-time updates via WebSocket
    """
    
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.app = None
        self.websockets = set()
        self.redis_client = None
        
        # Data stores (optimized for real-time display)
        self.market_opportunities = deque(maxlen=100)
        self.executable_txs = deque(maxlen=50)
        self.recent_executions = deque(maxlen=100)
        self.system_metrics = {
            "status": "STARTING",
            "uptime": 0,
            "total_scans": 0,
            "opportunities_found": 0,
            "txs_executed": 0,
            "total_profit": 0.0,
            "total_gas": 0.0,
            "net_profit": 0.0,
            "success_rate": 0.0,
            "avg_profit_per_tx": 0.0,
            "current_gas_price": 0.0
        }
        self.chain_status = {}
        
        # ML Metrics
        self.ml_metrics = {
            "forecaster": {
                "predictions_made": 0,
                "accuracy": 0.0,
                "current_trend": "STABLE",
                "volatility": "LOW",
                "predicted_gas": 30.0
            },
            "rl_optimizer": {
                "total_episodes": 0,
                "avg_reward": 0.0,
                "success_rate": 0.0,
                "epsilon": 0.1,
                "states_explored": 0
            },
            "feature_store": {
                "total_observations": 0,
                "profitable_trades": 0,
                "avg_profit": 0.0,
                "best_chain": None,
                "best_token": None
            }
        }
        
        # ML models (lazy initialization)
        self._ml_models = None
        
        # Start time
        self.start_time = datetime.now()
        
    async def setup_redis(self):
        """Setup Redis connection for live data"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available - running in simulation mode")
            return
        
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            if REDIS_AVAILABLE and 'asyncio' in dir(redis):
                self.redis_client = await redis.from_url(redis_url, decode_responses=True)
            else:
                import redis as redis_sync
                self.redis_client = redis_sync.from_url(redis_url, decode_responses=True)
            
            # Test connection
            if hasattr(self.redis_client, 'ping'):
                if asyncio.iscoroutinefunction(self.redis_client.ping):
                    await self.redis_client.ping()
                else:
                    self.redis_client.ping()
            
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Running in simulation mode.")
            self.redis_client = None
    
    def _get_ml_models(self):
        """Lazy load ML models"""
        if self._ml_models is None:
            try:
                from offchain.ml.cortex.forecaster import MarketForecaster
                from offchain.ml.cortex.rl_optimizer import QLearningAgent
                from offchain.ml.cortex.feature_store import FeatureStore
                
                self._ml_models = {
                    'forecaster': MarketForecaster(),
                    'optimizer': QLearningAgent(),
                    'feature_store': FeatureStore()
                }
            except Exception as e:
                logger.warning(f"Could not load ML models: {e}")
                self._ml_models = {}
        
        return self._ml_models
    
    async def get_ml_metrics(self):
        """Get current ML model metrics"""
        models = self._get_ml_models()
        
        if not models:
            return self.ml_metrics
        
        try:
            # Update forecaster metrics
            if 'forecaster' in models:
                forecaster_metrics = models['forecaster'].get_metrics()
                self.ml_metrics['forecaster'].update({
                    'predictions_made': forecaster_metrics.get('predictions_made', 0),
                    'accuracy': forecaster_metrics.get('accuracy', 0.0),
                    'current_trend': forecaster_metrics.get('trend', 'STABLE'),
                    'volatility': forecaster_metrics.get('volatility', 'LOW'),
                    'predicted_gas': forecaster_metrics.get('predicted_gas', 30.0)
                })
            
            # Update RL optimizer metrics
            if 'optimizer' in models:
                rl_metrics = models['optimizer'].get_metrics()
                self.ml_metrics['rl_optimizer'].update({
                    'total_episodes': rl_metrics.get('total_episodes', 0),
                    'avg_reward': rl_metrics.get('avg_reward', 0.0),
                    'success_rate': rl_metrics.get('success_rate', 0.0),
                    'epsilon': rl_metrics.get('current_epsilon', 0.1),
                    'states_explored': rl_metrics.get('states_explored', 0)
                })
            
            # Update feature store metrics
            if 'feature_store' in models:
                fs_summary = models['feature_store'].get_summary()
                self.ml_metrics['feature_store'].update({
                    'total_observations': fs_summary.get('total_observations', 0),
                    'profitable_trades': fs_summary.get('profitable_trades', 0),
                    'avg_profit': fs_summary.get('avg_profit', 0.0),
                    'best_chain': fs_summary.get('best_chain'),
                    'best_token': fs_summary.get('best_token')
                })
        except Exception as e:
            logger.error(f"Error getting ML metrics: {e}")
        
        return self.ml_metrics
    
    async def websocket_handler(self, request):
        """Handle WebSocket connections for real-time updates"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.websockets.add(ws)
        logger.info(f"WebSocket client connected. Total clients: {len(self.websockets)}")
        
        try:
            # Send initial data
            await ws.send_json({
                "type": "initial_state",
                "data": {
                    "metrics": self.system_metrics,
                    "ml_metrics": await self.get_ml_metrics(),
                    "market_opportunities": list(self.market_opportunities),
                    "executable_txs": list(self.executable_txs),
                    "recent_executions": list(self.recent_executions),
                    "chain_status": self.chain_status
                }
            })
            
            # Keep connection alive and listen for messages
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    await self.handle_client_message(data, ws)
                elif msg.type == web.WSMsgType.ERROR:
                    logger.error(f'WebSocket connection closed with exception {ws.exception()}')
        finally:
            self.websockets.discard(ws)
            logger.info(f"WebSocket client disconnected. Total clients: {len(self.websockets)}")
        
        return ws
    
    async def handle_client_message(self, data: dict, ws):
        """Handle messages from dashboard clients"""
        msg_type = data.get('type')
        
        if msg_type == 'control':
            action = data.get('action')
            await self.handle_control_action(action, ws)
        elif msg_type == 'filter':
            # Handle filter updates
            filters = data.get('filters', {})
            await self.send_filtered_data(filters, ws)
    
    async def handle_control_action(self, action: str, ws):
        """Handle control button actions from dashboard"""
        logger.info(f"Control action received: {action}")
        
        if action == 'pause_scanning':
            # Publish pause command to Redis
            if self.redis_client:
                try:
                    if asyncio.iscoroutinefunction(self.redis_client.publish):
                        await self.redis_client.publish('system_control', json.dumps({'action': 'pause'}))
                    else:
                        self.redis_client.publish('system_control', json.dumps({'action': 'pause'}))
                    await ws.send_json({"type": "control_response", "success": True, "message": "Scanning paused"})
                except Exception as e:
                    await ws.send_json({"type": "control_response", "success": False, "message": str(e)})
        
        elif action == 'resume_scanning':
            if self.redis_client:
                try:
                    if asyncio.iscoroutinefunction(self.redis_client.publish):
                        await self.redis_client.publish('system_control', json.dumps({'action': 'resume'}))
                    else:
                        self.redis_client.publish('system_control', json.dumps({'action': 'resume'}))
                    await ws.send_json({"type": "control_response", "success": True, "message": "Scanning resumed"})
                except Exception as e:
                    await ws.send_json({"type": "control_response", "success": False, "message": str(e)})
        
        elif action == 'emergency_stop':
            if self.redis_client:
                try:
                    if asyncio.iscoroutinefunction(self.redis_client.publish):
                        await self.redis_client.publish('system_control', json.dumps({'action': 'emergency_stop'}))
                    else:
                        self.redis_client.publish('system_control', json.dumps({'action': 'emergency_stop'}))
                    await ws.send_json({"type": "control_response", "success": True, "message": "Emergency stop activated"})
                except Exception as e:
                    await ws.send_json({"type": "control_response", "success": False, "message": str(e)})
    
    async def send_filtered_data(self, filters: dict, ws):
        """Send filtered data based on client filters"""
        # Apply filters to market opportunities
        filtered_opps = list(self.market_opportunities)
        
        if filters.get('min_profit'):
            min_profit = float(filters['min_profit'])
            filtered_opps = [opp for opp in filtered_opps if opp.get('profit', 0) >= min_profit]
        
        if filters.get('chain'):
            chain = filters['chain']
            filtered_opps = [opp for opp in filtered_opps if opp.get('chain') == chain]
        
        await ws.send_json({
            "type": "filtered_data",
            "data": {
                "market_opportunities": filtered_opps
            }
        })
    
    async def broadcast_update(self, update_type: str, data: dict):
        """Broadcast updates to all connected WebSocket clients"""
        if not self.websockets:
            return
        
        message = {
            "type": update_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Send to all connected clients
        dead_ws = set()
        for ws in self.websockets:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to WebSocket: {e}")
                dead_ws.add(ws)
        
        # Clean up dead connections
        self.websockets -= dead_ws
    
    async def simulate_data(self):
        """Simulate real-time data for testing"""
        import random
        
        chains = ['Ethereum', 'Polygon', 'Arbitrum', 'Optimism', 'Base', 'BSC', 'Avalanche']
        tokens = ['USDC', 'USDT', 'DAI', 'WETH', 'WBTC', 'LINK', 'UNI']
        strategies = ['Flash Arbitrage', 'Cross-DEX', 'Triangular', 'Cross-Chain']
        
        while True:
            # Simulate market scan
            if random.random() < 0.3:  # 30% chance
                opportunity = {
                    "id": f"opp_{datetime.now().timestamp()}",
                    "timestamp": datetime.now().isoformat(),
                    "chain": random.choice(chains),
                    "token_pair": f"{random.choice(tokens)}/{random.choice(tokens)}",
                    "strategy": random.choice(strategies),
                    "profit_usd": round(random.uniform(5, 150), 2),
                    "gas_cost": round(random.uniform(0.5, 5), 2),
                    "net_profit": 0,
                    "executable": random.random() < 0.4,  # 40% executable
                    "dex_a": random.choice(['Uniswap V3', 'SushiSwap', 'Curve', 'Balancer']),
                    "dex_b": random.choice(['Uniswap V3', 'SushiSwap', 'Curve', 'Balancer']),
                    "spread_bps": round(random.uniform(10, 200), 1)
                }
                opportunity["net_profit"] = round(opportunity["profit_usd"] - opportunity["gas_cost"], 2)
                
                self.market_opportunities.append(opportunity)
                self.system_metrics["opportunities_found"] += 1
                
                # Broadcast to clients
                await self.broadcast_update("market_opportunity", opportunity)
                
                # If executable, add to executable queue
                if opportunity["executable"] and opportunity["net_profit"] > 5:
                    executable = {
                        **opportunity,
                        "status": "PENDING",
                        "queued_at": datetime.now().isoformat()
                    }
                    self.executable_txs.append(executable)
                    await self.broadcast_update("executable_tx", executable)
            
            # Simulate transaction execution
            if self.executable_txs and random.random() < 0.2:  # 20% chance
                tx = self.executable_txs.popleft()
                
                # Simulate execution
                success = random.random() < 0.85  # 85% success rate
                execution = {
                    **tx,
                    "status": "SUCCESS" if success else "FAILED",
                    "executed_at": datetime.now().isoformat(),
                    "tx_hash": f"0x{''.join(random.choices('0123456789abcdef', k=64))}",
                    "gas_used": round(random.uniform(250000, 450000)),
                    "actual_profit": round(tx["net_profit"] * (0.95 if success else 0), 2)
                }
                
                self.recent_executions.append(execution)
                self.system_metrics["txs_executed"] += 1
                
                if success:
                    self.system_metrics["total_profit"] += execution["actual_profit"]
                    self.system_metrics["total_gas"] += execution["gas_cost"]
                
                await self.broadcast_update("execution_result", execution)
            
            # Update metrics
            self.system_metrics["uptime"] = int((datetime.now() - self.start_time).total_seconds())
            self.system_metrics["total_scans"] += random.randint(5, 20)
            self.system_metrics["net_profit"] = round(
                self.system_metrics["total_profit"] - self.system_metrics["total_gas"], 2
            )
            
            if self.system_metrics["txs_executed"] > 0:
                success_count = sum(1 for ex in self.recent_executions if ex.get("status") == "SUCCESS")
                self.system_metrics["success_rate"] = round(
                    success_count / min(len(self.recent_executions), self.system_metrics["txs_executed"]) * 100, 1
                )
                self.system_metrics["avg_profit_per_tx"] = round(
                    self.system_metrics["total_profit"] / self.system_metrics["txs_executed"], 2
                )
            
            self.system_metrics["current_gas_price"] = round(random.uniform(20, 180), 2)
            self.system_metrics["status"] = "OPERATIONAL"
            
            # Simulate ML metrics updates
            self.ml_metrics["forecaster"]["predictions_made"] += random.randint(1, 5)
            self.ml_metrics["forecaster"]["accuracy"] = round(random.uniform(75, 95), 1)
            self.ml_metrics["forecaster"]["current_trend"] = random.choice(["STABLE", "RISING_FAST", "DROPPING_FAST"])
            self.ml_metrics["forecaster"]["volatility"] = random.choice(["LOW", "MEDIUM", "HIGH"])
            self.ml_metrics["forecaster"]["predicted_gas"] = round(random.uniform(20, 150), 2)
            
            self.ml_metrics["rl_optimizer"]["total_episodes"] += random.randint(0, 2)
            self.ml_metrics["rl_optimizer"]["avg_reward"] = round(random.uniform(-5, 50), 2)
            self.ml_metrics["rl_optimizer"]["success_rate"] = round(random.uniform(70, 90), 1)
            self.ml_metrics["rl_optimizer"]["epsilon"] = max(0.01, self.ml_metrics["rl_optimizer"]["epsilon"] * 0.999)
            
            self.ml_metrics["feature_store"]["total_observations"] += random.randint(5, 15)
            if random.random() < 0.3:
                self.ml_metrics["feature_store"]["profitable_trades"] += 1
            
            # Broadcast metrics update
            await self.broadcast_update("metrics_update", self.system_metrics)
            await self.broadcast_update("ml_metrics_update", self.ml_metrics)
            
            await asyncio.sleep(2)  # Update every 2 seconds
    
    async def index_handler(self, request):
        """Serve the main dashboard HTML"""
        html_path = Path(__file__).parent / 'interactive_dashboard.html'
        if html_path.exists():
            return web.FileResponse(html_path)
        else:
            return web.Response(text="Dashboard HTML not found", status=404)
    
    async def ml_metrics_handler(self, request):
        """API endpoint for ML metrics"""
        ml_metrics = await self.get_ml_metrics()
        return web.json_response(ml_metrics)
    
    async def feature_importance_handler(self, request):
        """API endpoint for feature importance"""
        models = self._get_ml_models()
        if 'feature_store' in models:
            importance = models['feature_store'].get_feature_importance()
            return web.json_response(importance)
        return web.json_response({})
    
    async def chain_performance_handler(self, request):
        """API endpoint for chain performance metrics"""
        models = self._get_ml_models()
        if 'feature_store' in models:
            performance = models['feature_store'].get_performance_by_chain()
            return web.json_response(performance)
        return web.json_response({})
    
    async def token_performance_handler(self, request):
        """API endpoint for token performance metrics"""
        models = self._get_ml_models()
        if 'feature_store' in models:
            performance = models['feature_store'].get_performance_by_token()
            return web.json_response(performance)
        return web.json_response({})
    
    async def start(self):
        """Start the dashboard server"""
        if not AIOHTTP_AVAILABLE:
            logger.error("aiohttp not installed. Cannot start server.")
            return
        
        # Setup Redis
        await self.setup_redis()
        
        # Create web application
        self.app = web.Application()
        
        # Setup CORS
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        })
        
        # Add routes
        self.app.router.add_get('/', self.index_handler)
        self.app.router.add_get('/ws', self.websocket_handler)
        self.app.router.add_get('/api/ml-metrics', self.ml_metrics_handler)
        self.app.router.add_get('/api/feature-importance', self.feature_importance_handler)
        self.app.router.add_get('/api/chain-performance', self.chain_performance_handler)
        self.app.router.add_get('/api/token-performance', self.token_performance_handler)
        
        # Add static file serving for the dashboard
        dashboard_dir = Path(__file__).parent
        self.app.router.add_static('/static', dashboard_dir, show_index=False)
        
        # Enable CORS for all routes
        for route in list(self.app.router.routes()):
            if not isinstance(route.resource, web.StaticResource):
                cors.add(route)
        
        # Start data tasks
        if self.redis_client:
            # Use Redis listener for live data
            asyncio.create_task(self.redis_listener())
            logger.info("Using Redis for live data")
        else:
            # Use simulation for testing
            asyncio.create_task(self.simulate_data())
            logger.info("Using simulation data (Redis not available)")
        
        # Start server
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        logger.info(f"🚀 Dashboard server started at http://{self.host}:{self.port}")
        logger.info(f"   WebSocket endpoint: ws://{self.host}:{self.port}/ws")
        logger.info(f"   Open in browser: http://localhost:{self.port}")
        
        # Keep running
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Shutting down dashboard server...")
            await runner.cleanup()


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="TITAN Interactive Dashboard Server")
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    
    args = parser.parse_args()
    
    server = DashboardServer(host=args.host, port=args.port)
    await server.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Dashboard server stopped")
