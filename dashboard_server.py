#!/usr/bin/env python3
"""
TITAN Multi-Page Interactive Dashboard Server
==============================================

Real-time dashboard server with WebSocket support for live updates.
Provides multi-page interface for monitoring and controlling the TITAN system.
"""

# Configure UTF-8 encoding for Windows console output
import sys
import os

if sys.platform == 'win32':
    # Set environment variable for Python IO encoding
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # Reconfigure stdout and stderr to use UTF-8 encoding
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    else:
        # Fallback for older Python versions
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

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
    
    async def deployment_config_handler(self, request):
        """API endpoint for cloud deployment configuration"""
        # Get current environment configuration
        config = {
            "execution_mode": os.getenv("EXECUTION_MODE", "PAPER"),
            "current_env": {
                "private_key_set": bool(os.getenv("PRIVATE_KEY")),
                "infura_configured": bool(os.getenv("INFURA_PROJECT_ID")),
                "alchemy_configured": bool(os.getenv("ALCHEMY_API_KEY")),
                "lifi_configured": bool(os.getenv("LIFI_API_KEY")),
                "redis_configured": bool(os.getenv("REDIS_URL")),
            },
            "cloud_providers": {
                "oracle_free_tier": {
                    "name": "Oracle Cloud Free Tier",
                    "specs": "4 vCPU, 24GB RAM (Ampere ARM)",
                    "cost": "Free Forever",
                    "recommended": True,
                    "deployment_guide": "ORACLE_CLOUD_DEPLOYMENT.md"
                },
                "aws_ec2": {
                    "name": "AWS EC2",
                    "specs": "t3.medium (2 vCPU, 4GB RAM)",
                    "cost": "$30-50/month",
                    "recommended": False,
                    "deployment_guide": "Deploy manually via AWS Console"
                },
                "gcp_compute": {
                    "name": "Google Cloud Compute",
                    "specs": "e2-medium (2 vCPU, 4GB RAM)",
                    "cost": "$25-40/month",
                    "recommended": False,
                    "deployment_guide": "Deploy manually via GCP Console"
                },
                "azure_vm": {
                    "name": "Azure Virtual Machine",
                    "specs": "B2s (2 vCPU, 4GB RAM)",
                    "cost": "$30-50/month",
                    "recommended": False,
                    "deployment_guide": "Deploy manually via Azure Portal"
                }
            }
        }
        return web.json_response(config)
    
    async def generate_deployment_script_handler(self, request):
        """Generate deployment script for selected cloud provider"""
        try:
            data = await request.json()
            provider = data.get('provider', 'oracle')
            config = data.get('config', {})
            
            if provider == 'oracle':
                script = self._generate_oracle_deployment_script(config)
            else:
                script = self._generate_generic_deployment_script(provider, config)
            
            return web.json_response({
                "success": True,
                "script": script,
                "filename": f"deploy_{provider}.sh"
            })
        except Exception as e:
            logger.error(f"Error generating deployment script: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    def _generate_oracle_deployment_script(self, config):
        """Generate Oracle Cloud deployment script"""
        return f"""#!/bin/bash
# TITAN 2.0 - Oracle Cloud Deployment Script
# Generated by TITAN Dashboard

set -e

echo "================================================"
echo "  TITAN 2.0 - Oracle Cloud Deployment"
echo "================================================"
echo ""

# Update system
echo "📦 Updating system packages..."
sudo apt-get update -qq
sudo apt-get upgrade -y

# Install Node.js
echo "📦 Installing Node.js 18.x..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python dependencies
echo "📦 Installing Python build tools..."
sudo apt-get install -y python3-pip python3-dev build-essential

# Install Redis (optional)
echo "📦 Installing Redis..."
sudo apt-get install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Clone repository
echo "📥 Cloning TITAN repository..."
cd ~
rm -rf Titan2.0
git clone https://github.com/vegas-max/Titan2.0.git
cd Titan2.0

# Install dependencies
echo "📦 Installing project dependencies..."
pip3 install -r requirements.txt
npm install --legacy-peer-deps

# Create .env file
echo "🔧 Creating configuration..."
cat > .env << 'EOF'
# TITAN Configuration - Oracle Cloud Deployment

EXECUTION_MODE={config.get('execution_mode', 'PAPER')}
PRIVATE_KEY={config.get('private_key', 'YOUR_PRIVATE_KEY')}

# RPC Providers
INFURA_PROJECT_ID={config.get('infura_id', 'YOUR_INFURA_ID')}
ALCHEMY_API_KEY={config.get('alchemy_key', 'YOUR_ALCHEMY_KEY')}

# API Keys
LIFI_API_KEY={config.get('lifi_key', 'YOUR_LIFI_KEY')}

# Redis
REDIS_URL=redis://localhost:6379

# Dashboard
DASHBOARD_PORT=8080

# Optional Features
ENABLE_CROSS_CHAIN=false
ENABLE_MEV_PROTECTION=false
ENABLE_REALTIME_TRAINING=true
EOF

# Setup systemd services
echo "🔧 Setting up systemd services..."

# Brain service
sudo tee /etc/systemd/system/titan-brain.service > /dev/null << 'EOF'
[Unit]
Description=TITAN Brain Service
After=network.target redis-server.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/Titan2.0
ExecStart=/usr/bin/python3 mainnet_orchestrator.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Bot service
sudo tee /etc/systemd/system/titan-bot.service > /dev/null << 'EOF'
[Unit]
Description=TITAN Bot Service
After=network.target titan-brain.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/Titan2.0
ExecStart=/usr/bin/node offchain/execution/bot.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Dashboard service
sudo tee /etc/systemd/system/titan-dashboard.service > /dev/null << 'EOF'
[Unit]
Description=TITAN Dashboard Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/Titan2.0
ExecStart=/usr/bin/python3 dashboard_server.py --host 0.0.0.0 --port 8080
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable titan-brain
sudo systemctl enable titan-bot
sudo systemctl enable titan-dashboard

echo ""
echo "✅ Deployment complete!"
echo ""
echo "To start TITAN:"
echo "  sudo systemctl start titan-brain"
echo "  sudo systemctl start titan-bot"
echo "  sudo systemctl start titan-dashboard"
echo ""
echo "To check status:"
echo "  sudo systemctl status titan-brain"
echo "  sudo systemctl status titan-bot"
echo "  sudo systemctl status titan-dashboard"
echo ""
echo "Dashboard will be available at:"
echo "  http://YOUR_INSTANCE_IP:8080"
echo ""
"""
    
    def _generate_generic_deployment_script(self, provider, config):
        """Generate generic deployment script for other providers"""
        return f"""#!/bin/bash
# TITAN 2.0 - {provider.upper()} Deployment Script
# Generated by TITAN Dashboard

set -e

echo "================================================"
echo "  TITAN 2.0 - {provider.upper()} Deployment"
echo "================================================"
echo ""

# Update system
sudo apt-get update -qq
sudo apt-get upgrade -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python and dependencies
sudo apt-get install -y python3-pip python3-dev build-essential redis-server

# Clone and setup
cd ~
git clone https://github.com/vegas-max/Titan2.0.git
cd Titan2.0
pip3 install -r requirements.txt
npm install --legacy-peer-deps

# Configure environment
cp .env.example .env
# Edit .env with your configuration

echo "✅ Basic setup complete!"
echo "Please edit .env file with your configuration and start the system."
"""
    
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
        self.app.router.add_get('/api/deployment-config', self.deployment_config_handler)
        self.app.router.add_post('/api/generate-deployment-script', self.generate_deployment_script_handler)
        
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
