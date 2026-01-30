# 🚀 TITAN Multi-Page Interactive Dashboard

## Overview

The TITAN Multi-Page Interactive Dashboard is a comprehensive, real-time monitoring and control interface for the TITAN arbitrage system. It provides live updates on market opportunities, executable transactions, and system performance through an intuitive web interface.

## Features

### 🎯 Multi-Page Navigation
- **Overview**: System status, key metrics, and recent executions
- **Market Scanner**: Real-time market opportunities as they're discovered
- **Executable TXs**: Queue of profitable transactions ready for execution
- **Live Execution**: Real-time transaction execution monitoring
- **Analytics**: Performance metrics and chain-specific statistics

### ⚡ Real-Time Updates
- WebSocket-based live data streaming
- Sub-second update latency
- Automatic reconnection on connection loss
- No page refresh required

### 🎮 Interactive Controls
- **Resume Scanning**: Restart market scanning
- **Pause Scanning**: Temporarily halt scanning
- **Emergency Stop**: Immediately stop all operations
- Real-time control feedback

### 📊 Live Data Display
- **Market Opportunities**: Real-time arbitrage opportunities with profit calculations
- **Executable Transactions**: Queue of transactions ready for execution
- **Transaction Monitor**: Live execution status and results
- **Performance Metrics**: Success rates, profit/loss, gas costs

### 🔍 Filtering & Search
- Filter by minimum profit threshold
- Filter by blockchain network
- Filter by arbitrage strategy
- Real-time filter application

## Installation

### Prerequisites

```bash
# Python 3.8+ required
python3 --version

# Required Python packages
pip install aiohttp aiohttp-cors redis python-dotenv
```

### Quick Start

1. **One-line launcher:**
   ```bash
   ./launch_interactive_dashboard.sh
   ```

2. **Using npm:**
   ```bash
   npm run dashboard:interactive
   ```

3. **Direct Python:**
   ```bash
   python3 dashboard_server.py
   ```

4. **Custom port/host:**
   ```bash
   ./launch_interactive_dashboard.sh --port 3000 --host 127.0.0.1
   ```

## Usage

### Access the Dashboard

After starting the server, open your browser to:
- Local: `http://localhost:8080`
- Network: `http://YOUR_IP:8080` (if using host 0.0.0.0)

### Dashboard Pages

#### 1. Overview
- **System Status**: Overall health indicator
- **Key Metrics**: Total profit, gas spent, net profit, success rate
- **Recent Executions**: Last 10 completed transactions
- **Control Buttons**: System control interface

#### 2. Market Scanner
- **Live Opportunities**: Real-time arbitrage opportunities
- **Filters**: Min profit, chain, strategy
- **Details**: DEX routing, spreads, profitability
- **Auto-updates**: New opportunities appear instantly

#### 3. Executable TXs
- **Transaction Queue**: Profitable TXs ready to execute
- **Expected Profit**: Estimated profit after gas
- **Status Tracking**: Queue position and pending time
- **Auto-removal**: Executed TXs removed automatically

#### 4. Live Execution
- **Real-Time Monitor**: TX execution as it happens
- **Status Updates**: Pending → Executing → Success/Failed
- **Gas Usage**: Actual gas consumed
- **Transaction Hashes**: With blockchain explorer links

#### 5. Analytics
- **Performance Metrics**: Avg profit/TX, conversion rate
- **Chain Performance**: Per-chain statistics
- **Success Rates**: Historical success rates
- **Execution Times**: Average execution duration

### Interactive Controls

#### Resume Scanning
Restart the market scanning engine after a pause.

```javascript
// Sends control message to backend
{ "type": "control", "action": "resume_scanning" }
```

#### Pause Scanning
Temporarily halt market scanning (does not affect running executions).

```javascript
{ "type": "control", "action": "pause_scanning" }
```

#### Emergency Stop
Immediately stop all operations including scanning and execution queue.

```javascript
{ "type": "control", "action": "emergency_stop" }
```

### Filtering

Apply filters to focus on specific opportunities:

1. **Min Profit Filter**: Show only opportunities above threshold
2. **Chain Filter**: Filter by specific blockchain
3. **Strategy Filter**: Filter by arbitrage strategy type

Filters are applied in real-time without page refresh.

## Architecture

### Server Components

#### WebSocket Server (`dashboard_server.py`)
- Handles WebSocket connections for real-time updates
- Manages data stores (opportunities, executions, metrics)
- Broadcasts updates to all connected clients
- Handles control messages from dashboard

#### Data Flow
```
TITAN System (Brain/Bot)
    ↓
Redis PubSub
    ↓
Dashboard Server
    ↓
WebSocket
    ↓
Dashboard Web UI
```

### Client Components

#### Interactive Dashboard (`interactive_dashboard.html`)
- Multi-page SPA with navigation
- WebSocket client for live updates
- Real-time data visualization
- Interactive control interface

### Data Stores

The dashboard maintains several in-memory data stores:

- **Market Opportunities**: Last 100 scanned opportunities
- **Executable TXs**: Last 50 executable transactions
- **Recent Executions**: Last 100 completed executions
- **System Metrics**: Current system state and statistics

## Configuration

### Environment Variables

Create or update `.env` file:

```bash
# Redis connection (optional - falls back to simulation)
REDIS_URL=redis://localhost:6379

# Minimum profit threshold
MIN_PROFIT_USD=5.00

# Maximum gas price alert threshold
MAX_GAS_PRICE_GWEI=150
```

### Server Configuration

```bash
# Default configuration
HOST=0.0.0.0      # Bind to all interfaces
PORT=8080         # Default port

# Custom configuration
./launch_interactive_dashboard.sh --port 3000 --host 127.0.0.1
```

## Integration with TITAN System

### Live Data Mode (with Redis)

When Redis is running and the TITAN system is active:

1. Start Redis: `redis-server`
2. Start TITAN brain: `python3 offchain/ml/brain.py`
3. Start TITAN bot: `node offchain/execution/bot.js`
4. Start dashboard: `./launch_interactive_dashboard.sh`

The dashboard will automatically connect to Redis and display live system data.

### Simulation Mode (without Redis)

For testing or demonstration without the full TITAN system:

1. Start dashboard: `./launch_interactive_dashboard.sh`
2. Dashboard generates realistic simulated data
3. All features work with simulated data

## WebSocket API

### Message Types (Server → Client)

#### Initial State
```json
{
  "type": "initial_state",
  "data": {
    "metrics": { ... },
    "market_opportunities": [ ... ],
    "executable_txs": [ ... ],
    "recent_executions": [ ... ]
  }
}
```

#### Market Opportunity
```json
{
  "type": "market_opportunity",
  "data": {
    "id": "opp_123456789",
    "timestamp": "2024-01-01T12:00:00",
    "chain": "Polygon",
    "token_pair": "USDC/USDT",
    "strategy": "Flash Arbitrage",
    "profit_usd": 12.50,
    "gas_cost": 2.30,
    "net_profit": 10.20,
    "executable": true,
    "dex_a": "Uniswap V3",
    "dex_b": "Curve",
    "spread_bps": 45.2
  }
}
```

#### Executable Transaction
```json
{
  "type": "executable_tx",
  "data": {
    "id": "tx_123456789",
    "status": "PENDING",
    "queued_at": "2024-01-01T12:00:00",
    ...opportunity_data
  }
}
```

#### Execution Result
```json
{
  "type": "execution_result",
  "data": {
    "id": "tx_123456789",
    "status": "SUCCESS",
    "executed_at": "2024-01-01T12:00:05",
    "tx_hash": "0xabc123...",
    "gas_used": 320000,
    "actual_profit": 10.15
  }
}
```

#### Metrics Update
```json
{
  "type": "metrics_update",
  "data": {
    "status": "OPERATIONAL",
    "uptime": 3600,
    "total_scans": 15000,
    "opportunities_found": 250,
    "txs_executed": 42,
    "total_profit": 525.30,
    "total_gas": 95.20,
    "net_profit": 430.10,
    "success_rate": 85.7,
    "current_gas_price": 45.2
  }
}
```

### Message Types (Client → Server)

#### Control Action
```json
{
  "type": "control",
  "action": "pause_scanning"  // or "resume_scanning", "emergency_stop"
}
```

#### Filter Update
```json
{
  "type": "filter",
  "filters": {
    "min_profit": "10.00",
    "chain": "Polygon",
    "strategy": "Flash Arbitrage"
  }
}
```

## Troubleshooting

### Dashboard won't start

**Error**: `aiohttp not installed`
```bash
pip install aiohttp aiohttp-cors
```

**Error**: Port already in use
```bash
# Use a different port
./launch_interactive_dashboard.sh --port 3000
```

### No live data

**Issue**: Dashboard shows "Waiting for data..."

**Solutions**:
1. Check if Redis is running: `redis-cli ping`
2. Check if TITAN brain is running
3. Dashboard will work in simulation mode without Redis

### WebSocket connection fails

**Issue**: Status shows "Reconnecting..."

**Solutions**:
1. Check firewall settings
2. Ensure dashboard server is running
3. Check browser console for errors
4. Try different port: `--port 3000`

### Filters not working

**Issue**: Filters don't apply

**Solutions**:
1. Click "Apply Filters" button
2. Check browser console for errors
3. Ensure WebSocket connection is active

## Performance

### Resource Usage

- **Memory**: ~50-100 MB for server process
- **CPU**: <5% idle, ~10-15% during active updates
- **Network**: ~10-50 KB/s per connected client
- **Storage**: In-memory only, no disk usage

### Scalability

- Supports 50+ concurrent dashboard clients
- WebSocket broadcasts to all clients simultaneously
- Optimized data structures with deque (maxlen limits)
- Automatic cleanup of old data

### Update Frequency

- Metrics: Every 2 seconds
- Market opportunities: Real-time as discovered
- Executions: Real-time as completed
- Overall refresh rate: 0.5-2 seconds

## Security

### Production Deployment

For production deployment, consider:

1. **HTTPS**: Use reverse proxy (nginx/Apache) with SSL
2. **Authentication**: Add auth layer (OAuth, JWT)
3. **Rate Limiting**: Limit WebSocket connections
4. **CORS**: Configure allowed origins
5. **Firewall**: Restrict dashboard port access

### Example nginx config

```nginx
server {
    listen 443 ssl;
    server_name dashboard.example.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## Development

### Adding New Pages

1. Create HTML section with `class="page"`
2. Add navigation tab with `data-page` attribute
3. Implement update function for page data
4. Add WebSocket message handler if needed

### Adding New Metrics

1. Add metric to `system_metrics` dict in server
2. Create metric card in HTML
3. Add update logic in `updateMetrics()` function

### Customizing UI

All styles are in `<style>` section of HTML:
- CSS variables in `:root` for colors
- Grid layouts responsive by default
- Easy to customize without breaking functionality

## Support

### Getting Help

- **Documentation**: This README
- **Issues**: [GitHub Issues](https://github.com/vegas-max/Titan2.0/issues)
- **Main Documentation**: [README.md](README.md)

### Common Issues

See [Troubleshooting](#troubleshooting) section above.

## License

MIT License - See main repository LICENSE file.

---

**Built with ❤️ for the TITAN arbitrage system**

🚀 **Multi-page dashboard**  
⚡ **Real-time updates**  
🎮 **Interactive controls**  
📊 **Live market data**  
💰 **Executable transactions**  
🎯 **Transaction monitoring**
