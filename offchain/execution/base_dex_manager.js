require('dotenv').config();
const axios = require('axios');
const { ethers } = require('ethers');

/**
 * BaseDEXManager - Abstract base class for DEX aggregator integrations
 * 
 * Optimized for ARM architecture (4 cores, 24GB RAM) with:
 * - Efficient retry mechanisms with exponential backoff
 * - Request pooling and rate limiting
 * - Memory-efficient caching
 * - Parallel request handling where appropriate
 * 
 * All DEX managers should extend this class to reduce code duplication.
 */
class BaseDEXManager {
    /**
     * Initialize Base DEX Manager
     * @param {string} name - Name of the DEX/aggregator
     * @param {number} chainId - EIP-155 Chain ID
     * @param {object} provider - Ethers provider (optional)
     * @param {object} config - Additional configuration
     */
    constructor(name, chainId, provider = null, config = {}) {
        this.name = name;
        this.chainId = chainId;
        this.provider = provider;
        
        // Configuration with ARM optimization defaults
        this.config = {
            maxRetries: config.maxRetries || 3,
            retryDelay: config.retryDelay || 1000,
            timeout: config.timeout || 10000,
            rateLimit: config.rateLimit || 10, // requests per second
            cacheTTL: config.cacheTTL || 60000, // 1 minute cache
            enableCache: config.enableCache !== false,
            ...config
        };
        
        // Rate limiting state
        this.requestQueue = [];
        this.lastRequestTime = 0;
        this.requestInterval = 1000 / this.config.rateLimit;
        
        // Simple in-memory cache (memory efficient for 24GB RAM)
        this.cache = new Map();
        this.cacheTimestamps = new Map();
        
        // Stats tracking
        this.stats = {
            totalRequests: 0,
            successfulRequests: 0,
            failedRequests: 0,
            cacheHits: 0,
            cacheMisses: 0,
            avgResponseTime: 0,
            lastError: null
        };
    }
    
    /**
     * Get chain name from chain ID (override in subclass if needed)
     */
    getChainName(chainId) {
        const chainNames = {
            1: "ethereum",
            137: "polygon",
            42161: "arbitrum",
            10: "optimism",
            8453: "base",
            56: "bsc",
            43114: "avalanche",
            250: "fantom",
            59144: "linea",
            534352: "scroll",
            324: "zksync",
            1101: "polygonzkevm"
        };
        return chainNames[chainId] || "ethereum";
    }
    
    /**
     * Check if cached data is still valid
     */
    isCacheValid(key) {
        if (!this.config.enableCache) return false;
        if (!this.cache.has(key)) return false;
        
        const timestamp = this.cacheTimestamps.get(key);
        const now = Date.now();
        return (now - timestamp) < this.config.cacheTTL;
    }
    
    /**
     * Get data from cache
     */
    getFromCache(key) {
        if (this.isCacheValid(key)) {
            this.stats.cacheHits++;
            return this.cache.get(key);
        }
        this.stats.cacheMisses++;
        return null;
    }
    
    /**
     * Store data in cache with automatic cleanup
     */
    setCache(key, value) {
        if (!this.config.enableCache) return;
        
        // Memory management: limit cache size to prevent memory bloat
        const MAX_CACHE_SIZE = 1000;
        if (this.cache.size >= MAX_CACHE_SIZE) {
            // Remove oldest entry
            const oldestKey = this.cache.keys().next().value;
            this.cache.delete(oldestKey);
            this.cacheTimestamps.delete(oldestKey);
        }
        
        this.cache.set(key, value);
        this.cacheTimestamps.set(key, Date.now());
    }
    
    /**
     * Clear cache (useful for testing or manual refresh)
     */
    clearCache() {
        this.cache.clear();
        this.cacheTimestamps.clear();
    }
    
    /**
     * Rate-limited HTTP request with retry logic
     */
    async makeRequest(url, options = {}) {
        // Check cache first
        const cacheKey = `${url}:${JSON.stringify(options)}`;
        const cached = this.getFromCache(cacheKey);
        if (cached) {
            return cached;
        }
        
        // Rate limiting
        await this.waitForRateLimit();
        
        const startTime = Date.now();
        let lastError = null;
        
        for (let attempt = 0; attempt <= this.config.maxRetries; attempt++) {
            try {
                this.stats.totalRequests++;
                
                const response = await axios({
                    url,
                    timeout: this.config.timeout,
                    ...options
                });
                
                // Update stats
                this.stats.successfulRequests++;
                const responseTime = Date.now() - startTime;
                this.stats.avgResponseTime = 
                    (this.stats.avgResponseTime * (this.stats.successfulRequests - 1) + responseTime) / 
                    this.stats.successfulRequests;
                
                // Cache successful response
                this.setCache(cacheKey, response.data);
                
                return response.data;
                
            } catch (error) {
                lastError = error;
                this.stats.failedRequests++;
                this.stats.lastError = {
                    message: error.message,
                    timestamp: new Date().toISOString(),
                    url: url
                };
                
                // Don't retry on 4xx errors (client errors)
                if (error.response && error.response.status >= 400 && error.response.status < 500) {
                    throw error;
                }
                
                // Exponential backoff for retries
                if (attempt < this.config.maxRetries) {
                    const delay = this.config.retryDelay * Math.pow(2, attempt);
                    await this.sleep(delay);
                }
            }
        }
        
        // All retries exhausted
        throw lastError;
    }
    
    /**
     * Wait for rate limit compliance
     */
    async waitForRateLimit() {
        const now = Date.now();
        const timeSinceLastRequest = now - this.lastRequestTime;
        
        if (timeSinceLastRequest < this.requestInterval) {
            const waitTime = this.requestInterval - timeSinceLastRequest;
            await this.sleep(waitTime);
        }
        
        this.lastRequestTime = Date.now();
    }
    
    /**
     * Sleep utility
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    /**
     * Validate token address
     */
    isValidAddress(address) {
        try {
            return ethers.isAddress(address);
        } catch {
            return false;
        }
    }
    
    /**
     * Validate amount
     */
    isValidAmount(amount) {
        try {
            const bn = BigInt(amount);
            return bn > 0n;
        } catch {
            return false;
        }
    }
    
    /**
     * Format error for logging
     */
    formatError(error, context = '') {
        return {
            manager: this.name,
            chainId: this.chainId,
            context: context,
            message: error.message,
            code: error.code,
            response: error.response?.data,
            timestamp: new Date().toISOString()
        };
    }
    
    /**
     * Get manager statistics
     */
    getStats() {
        return {
            ...this.stats,
            cacheSize: this.cache.size,
            hitRate: this.stats.cacheHits / (this.stats.cacheHits + this.stats.cacheMisses) || 0,
            successRate: this.stats.successfulRequests / this.stats.totalRequests || 0
        };
    }
    
    /**
     * Abstract methods to be implemented by subclasses
     */
    
    /**
     * Get swap quote - MUST be implemented by subclass
     * @param {string} srcToken - Source token address
     * @param {string} destToken - Destination token address
     * @param {string} amount - Amount to swap (in wei as string)
     * @param {string} [userAddress] - Optional user wallet address (some APIs require it)
     * @param {number} [slippageBps] - Optional slippage in basis points
     * @returns {Promise<object|null>} Swap data or null if failed
     */
    async getQuote(srcToken, destToken, amount, userAddress = null, slippageBps = 100) {
        throw new Error(`${this.name}: getQuote() must be implemented by subclass`);
    }
    
    /**
     * Execute swap - MAY be implemented by subclass
     * @param {object} quoteData - Quote data from getQuote
     * @param {object} wallet - Ethers wallet for signing
     * @returns {Promise<object|null>} Transaction result or null
     */
    async executeSwap(quoteData, wallet) {
        throw new Error(`${this.name}: executeSwap() not implemented`);
    }
    
    /**
     * Check if chain is supported - MAY be overridden by subclass
     * @returns {boolean}
     */
    isChainSupported() {
        return true; // Default: assume all chains supported unless overridden
    }
    
    /**
     * Get API endpoint - SHOULD be implemented by subclass
     * @returns {string} Base API URL
     */
    getApiUrl() {
        throw new Error(`${this.name}: getApiUrl() must be implemented by subclass`);
    }
    
    /**
     * Get token decimals (common utility method)
     * @param {string} tokenAddress - Token contract address
     * @returns {Promise<number>} Token decimals
     */
    async getTokenDecimals(tokenAddress) {
        if (!this.provider) {
            return 18; // Default for most ERC20 tokens
        }
        
        // Check cache first
        const cacheKey = `decimals:${tokenAddress}`;
        const cached = this.getFromCache(cacheKey);
        if (cached !== null) {
            return cached;
        }
        
        try {
            const { ethers } = require('ethers');
            const tokenContract = new ethers.Contract(
                tokenAddress,
                ['function decimals() view returns (uint8)'],
                this.provider
            );
            const decimals = await tokenContract.decimals();
            
            // Cache decimals indefinitely (they don't change)
            this.setCache(cacheKey, decimals);
            
            return decimals;
        } catch (error) {
            // Return default on error
            return 18;
        }
    }
}

module.exports = BaseDEXManager;
