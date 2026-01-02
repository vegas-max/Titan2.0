require('dotenv').config();
const { ethers } = require('ethers');
const EventEmitter = require('events');

/**
 * Custom RPC Manager with Sub-block Latency Support
 * Features:
 * - Multiple RPC endpoints per chain with priority tiers
 * - Latency monitoring and automatic failover
 * - WebSocket support for real-time updates
 * - Co-located node support for ultra-low latency
 */
class CustomRPCManager extends EventEmitter {
    constructor() {
        super();
        this.providers = {};
        this.wsProviders = {};
        this.latencyStats = {};
        this.rpcConfig = this.getRPCConfiguration();
        this.healthCheckInterval = 30000; // 30 seconds
        this.healthCheckTimers = {};
    }

    /**
     * RPC Configuration with priority tiers
     * Tier 1: Custom/Co-located nodes (lowest latency)
     * Tier 2: Premium RPC providers
     * Tier 3: Public RPC endpoints
     */
    getRPCConfiguration() {
        return {
            1: { // Ethereum
                name: 'Ethereum',
                endpoints: [
                    {
                        tier: 1,
                        name: 'Custom Node',
                        http: process.env.CUSTOM_RPC_ETHEREUM || process.env.RPC_ETHEREUM,
                        ws: process.env.CUSTOM_WSS_ETHEREUM || process.env.WSS_ETHEREUM,
                        priority: 100
                    },
                    {
                        tier: 2,
                        name: 'Alchemy',
                        http: process.env.ALCHEMY_RPC_ETHEREUM || `https://eth-mainnet.g.alchemy.com/v2/${process.env.ALCHEMY_API_KEY}`,
                        ws: process.env.ALCHEMY_WSS_ETHEREUM || `wss://eth-mainnet.g.alchemy.com/v2/${process.env.ALCHEMY_API_KEY}`,
                        priority: 80
                    },
                    {
                        tier: 2,
                        name: 'Infura',
                        http: process.env.INFURA_RPC_ETHEREUM || `https://mainnet.infura.io/v3/${process.env.INFURA_API_KEY}`,
                        ws: process.env.INFURA_WSS_ETHEREUM || `wss://mainnet.infura.io/ws/v3/${process.env.INFURA_API_KEY}`,
                        priority: 70
                    }
                ]
            },
            137: { // Polygon
                name: 'Polygon',
                endpoints: [
                    {
                        tier: 1,
                        name: 'Custom Node',
                        http: process.env.CUSTOM_RPC_POLYGON || process.env.RPC_POLYGON,
                        ws: process.env.CUSTOM_WSS_POLYGON || process.env.WSS_POLYGON,
                        priority: 100
                    },
                    {
                        tier: 2,
                        name: 'Alchemy',
                        http: process.env.ALCHEMY_RPC_POLYGON || `https://polygon-mainnet.g.alchemy.com/v2/${process.env.ALCHEMY_API_KEY}`,
                        ws: process.env.ALCHEMY_WSS_POLYGON || `wss://polygon-mainnet.g.alchemy.com/v2/${process.env.ALCHEMY_API_KEY}`,
                        priority: 80
                    },
                    {
                        tier: 3,
                        name: 'Public RPC',
                        http: 'https://polygon-rpc.com',
                        ws: null,
                        priority: 50
                    }
                ]
            },
            42161: { // Arbitrum
                name: 'Arbitrum',
                endpoints: [
                    {
                        tier: 1,
                        name: 'Custom Node',
                        http: process.env.CUSTOM_RPC_ARBITRUM || process.env.RPC_ARBITRUM,
                        ws: process.env.CUSTOM_WSS_ARBITRUM || process.env.WSS_ARBITRUM,
                        priority: 100
                    },
                    {
                        tier: 2,
                        name: 'Alchemy',
                        http: process.env.ALCHEMY_RPC_ARBITRUM || `https://arb-mainnet.g.alchemy.com/v2/${process.env.ALCHEMY_API_KEY}`,
                        ws: process.env.ALCHEMY_WSS_ARBITRUM || `wss://arb-mainnet.g.alchemy.com/v2/${process.env.ALCHEMY_API_KEY}`,
                        priority: 80
                    }
                ]
            },
            56: { // BSC
                name: 'BSC',
                endpoints: [
                    {
                        tier: 1,
                        name: 'Custom Node',
                        http: process.env.CUSTOM_RPC_BSC || process.env.RPC_BSC,
                        ws: process.env.CUSTOM_WSS_BSC || process.env.WSS_BSC,
                        priority: 100
                    },
                    {
                        tier: 3,
                        name: 'Public RPC',
                        http: 'https://bsc-dataseed.binance.org',
                        ws: null,
                        priority: 50
                    }
                ]
            },
            10: { // Optimism
                name: 'Optimism',
                endpoints: [
                    {
                        tier: 1,
                        name: 'Custom Node',
                        http: process.env.CUSTOM_RPC_OPTIMISM || process.env.RPC_OPTIMISM,
                        ws: process.env.CUSTOM_WSS_OPTIMISM || process.env.WSS_OPTIMISM,
                        priority: 100
                    },
                    {
                        tier: 2,
                        name: 'Alchemy',
                        http: process.env.ALCHEMY_RPC_OPTIMISM || `https://opt-mainnet.g.alchemy.com/v2/${process.env.ALCHEMY_API_KEY}`,
                        ws: process.env.ALCHEMY_WSS_OPTIMISM || `wss://opt-mainnet.g.alchemy.com/v2/${process.env.ALCHEMY_API_KEY}`,
                        priority: 80
                    }
                ]
            },
            8453: { // Base
                name: 'Base',
                endpoints: [
                    {
                        tier: 1,
                        name: 'Custom Node',
                        http: process.env.CUSTOM_RPC_BASE || process.env.RPC_BASE,
                        ws: process.env.CUSTOM_WSS_BASE || process.env.WSS_BASE,
                        priority: 100
                    },
                    {
                        tier: 2,
                        name: 'Alchemy',
                        http: process.env.ALCHEMY_RPC_BASE || `https://base-mainnet.g.alchemy.com/v2/${process.env.ALCHEMY_API_KEY}`,
                        ws: process.env.ALCHEMY_WSS_BASE || `wss://base-mainnet.g.alchemy.com/v2/${process.env.ALCHEMY_API_KEY}`,
                        priority: 80
                    }
                ]
            }
        };
    }

    /**
     * Initialize provider for chain with automatic failover
     */
    async initializeProvider(chainId) {
        const config = this.rpcConfig[chainId];
        if (!config) {
            throw new Error(`No RPC configuration for chain ${chainId}`);
        }

        // Sort endpoints by priority (highest first)
        const sortedEndpoints = config.endpoints
            .filter(ep => ep.http)
            .sort((a, b) => b.priority - a.priority);

        for (const endpoint of sortedEndpoints) {
            try {
                const provider = new ethers.JsonRpcProvider(endpoint.http);
                
                // Test connection
                const blockNumber = await this.testProvider(provider);
                
                if (blockNumber) {
                    this.providers[chainId] = {
                        provider,
                        endpoint,
                        config
                    };
                    
                    // Initialize latency tracking
                    this.latencyStats[chainId] = {
                        endpoint: endpoint.name,
                        tier: endpoint.tier,
                        avgLatency: 0,
                        samples: []
                    };
                    
                    console.log(`✅ Connected to ${config.name} via ${endpoint.name} (Tier ${endpoint.tier})`);
                    console.log(`   Block: ${blockNumber}`);
                    
                    // Start health monitoring
                    this.startHealthCheck(chainId);
                    
                    return this.providers[chainId].provider;
                }
            } catch (error) {
                console.warn(`⚠️ Failed to connect to ${endpoint.name} for ${config.name}:`, error.message);
                continue;
            }
        }

        throw new Error(`Failed to connect to any RPC endpoint for chain ${chainId}`);
    }

    /**
     * Initialize WebSocket provider for real-time updates
     */
    async initializeWebSocket(chainId) {
        const config = this.rpcConfig[chainId];
        if (!config) {
            throw new Error(`No RPC configuration for chain ${chainId}`);
        }

        // Sort endpoints by priority
        const sortedEndpoints = config.endpoints
            .filter(ep => ep.ws)
            .sort((a, b) => b.priority - a.priority);

        for (const endpoint of sortedEndpoints) {
            try {
                const wsProvider = new ethers.WebSocketProvider(endpoint.ws);
                
                // Test connection
                const blockNumber = await this.testProvider(wsProvider);
                
                if (blockNumber) {
                    this.wsProviders[chainId] = {
                        provider: wsProvider,
                        endpoint,
                        config
                    };
                    
                    // Setup event listeners
                    this.setupWebSocketListeners(chainId, wsProvider);
                    
                    console.log(`✅ WebSocket connected to ${config.name} via ${endpoint.name}`);
                    
                    return wsProvider;
                }
            } catch (error) {
                console.warn(`⚠️ Failed to connect WebSocket to ${endpoint.name}:`, error.message);
                continue;
            }
        }

        console.warn(`⚠️ No WebSocket connection available for chain ${chainId}`);
        return null;
    }

    /**
     * Setup WebSocket event listeners for real-time updates
     */
    setupWebSocketListeners(chainId, wsProvider) {
        // Listen for new blocks
        wsProvider.on('block', (blockNumber) => {
            this.emit('newBlock', { chainId, blockNumber });
        });

        // Listen for pending transactions (if supported)
        try {
            wsProvider.on('pending', (txHash) => {
                this.emit('pendingTx', { chainId, txHash });
            });
        } catch (error) {
            // Pending tx subscription not supported on all chains
        }

        // Handle errors
        wsProvider.on('error', (error) => {
            console.error(`❌ WebSocket error on chain ${chainId}:`, error.message);
            this.emit('wsError', { chainId, error });
        });
    }

    /**
     * Test provider connectivity and measure latency
     */
    async testProvider(provider, retries = 3) {
        for (let i = 0; i < retries; i++) {
            try {
                const start = Date.now();
                const blockNumber = await provider.getBlockNumber();
                const latency = Date.now() - start;
                
                return blockNumber;
            } catch (error) {
                if (i === retries - 1) throw error;
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }
        return null;
    }

    /**
     * Measure RPC latency
     */
    async measureLatency(chainId) {
        const providerInfo = this.providers[chainId];
        if (!providerInfo) return null;

        try {
            const start = Date.now();
            await providerInfo.provider.getBlockNumber();
            const latency = Date.now() - start;
            
            // Update stats
            const stats = this.latencyStats[chainId];
            stats.samples.push(latency);
            
            // Keep only last 100 samples
            if (stats.samples.length > 100) {
                stats.samples = stats.samples.slice(-100);
            }
            
            // Calculate average
            stats.avgLatency = stats.samples.reduce((a, b) => a + b, 0) / stats.samples.length;
            
            return latency;
        } catch (error) {
            console.error(`❌ Latency check failed for chain ${chainId}:`, error.message);
            return null;
        }
    }

    /**
     * Start health check monitoring
     */
    startHealthCheck(chainId) {
        if (this.healthCheckTimers[chainId]) {
            clearInterval(this.healthCheckTimers[chainId]);
        }

        this.healthCheckTimers[chainId] = setInterval(async () => {
            const latency = await this.measureLatency(chainId);
            
            if (latency === null) {
                console.warn(`⚠️ Health check failed for chain ${chainId}, attempting failover...`);
                await this.failoverToBackup(chainId);
            } else if (latency > 5000) {
                console.warn(`⚠️ High latency detected on chain ${chainId}: ${latency}ms`);
            }
        }, this.healthCheckInterval);
    }

    /**
     * Failover to backup RPC endpoint
     */
    async failoverToBackup(chainId) {
        console.log(`🔄 Initiating failover for chain ${chainId}...`);
        
        // Clear current provider
        if (this.healthCheckTimers[chainId]) {
            clearInterval(this.healthCheckTimers[chainId]);
        }
        
        delete this.providers[chainId];
        
        // Reinitialize with next available endpoint
        try {
            await this.initializeProvider(chainId);
            console.log(`✅ Failover successful for chain ${chainId}`);
        } catch (error) {
            console.error(`❌ Failover failed for chain ${chainId}:`, error.message);
        }
    }

    /**
     * Get provider for chain
     */
    getProvider(chainId) {
        const providerInfo = this.providers[chainId];
        return providerInfo ? providerInfo.provider : null;
    }

    /**
     * Get WebSocket provider for chain
     */
    getWebSocketProvider(chainId) {
        const wsInfo = this.wsProviders[chainId];
        return wsInfo ? wsInfo.provider : null;
    }

    /**
     * Get latency statistics
     */
    getLatencyStats(chainId) {
        return this.latencyStats[chainId] || null;
    }

    /**
     * Get all latency statistics
     */
    getAllLatencyStats() {
        return this.latencyStats;
    }

    /**
     * Cleanup resources
     */
    async cleanup() {
        // Clear health check timers
        for (const timer of Object.values(this.healthCheckTimers)) {
            clearInterval(timer);
        }
        
        // Close WebSocket connections
        for (const wsInfo of Object.values(this.wsProviders)) {
            try {
                await wsInfo.provider.destroy();
            } catch (error) {
                // Ignore cleanup errors
            }
        }
        
        this.providers = {};
        this.wsProviders = {};
        this.healthCheckTimers = {};
    }
}

module.exports = { CustomRPCManager };
