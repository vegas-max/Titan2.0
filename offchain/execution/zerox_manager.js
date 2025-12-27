require('dotenv').config();
const BaseDEXManager = require('./base_dex_manager');

/**
 * ZeroXManager - 0x/Matcha DEX Aggregator Integration
 * Supports multi-chain routing and limit orders
 * Best for: Multi-chain routing and limit orders
 * 
 * Extends BaseDEXManager for ARM-optimized performance (4 cores, 24GB RAM)
 */
class ZeroXManager extends BaseDEXManager {
    /**
     * Initialize 0x Manager
     * @param {number} chainId - EIP-155 Chain ID
     * @param {object} provider - Ethers provider (optional, for validation)
     */
    constructor(chainId, provider = null) {
        super('0x', chainId, provider, {
            maxRetries: 3,
            rateLimit: 5, // 0x has moderate rate limits
            cacheTTL: 30000 // 30 second cache
        });
        
        this.apiKey = process.env.ZEROX_API_KEY || "";
    }
    
    /**
     * Get API URL for specific chain (override from base class)
     */
    getApiUrl() {
        const baseUrls = {
            1: "https://api.0x.org", // Ethereum
            137: "https://polygon.api.0x.org", // Polygon
            42161: "https://arbitrum.api.0x.org", // Arbitrum
            10: "https://optimism.api.0x.org", // Optimism
            8453: "https://base.api.0x.org", // Base
            56: "https://bsc.api.0x.org", // BSC
            43114: "https://avalanche.api.0x.org" // Avalanche
        };
        return baseUrls[this.chainId] || "https://api.0x.org";
    }
    
    /**
     * Get the best swap quote from 0x
     * @param {string} srcToken - Source token address
     * @param {string} destToken - Destination token address
     * @param {string} amount - Amount to swap (in wei as string)
     * @param {string} userAddress - User wallet address
     * @param {number} slippageBps - Slippage in basis points (default: 100 = 1%)
     * @returns {Promise<object|null>} Swap data or null if failed
     */
    async getBestSwap(srcToken, destToken, amount, userAddress, slippageBps = 100) {
        // Validate inputs
        if (!this.isValidAddress(srcToken) || !this.isValidAddress(destToken)) {
            console.log("⚠️ 0x: Invalid token address");
            return null;
        }
        
        if (!this.isValidAmount(amount)) {
            console.log("⚠️ 0x: Invalid amount");
            return null;
        }
        
        try {
            const apiUrl = this.getApiUrl();
            const swapUrl = `${apiUrl}/swap/v1/quote`;
            const params = new URLSearchParams({
                buyToken: destToken,
                sellToken: srcToken,
                sellAmount: amount,
                takerAddress: userAddress,
                slippagePercentage: (slippageBps / 10000).toString(),
                skipValidation: 'false',
                enableSlippageProtection: 'true'
            });
            
            const headers = this.apiKey ? { '0x-api-key': this.apiKey } : {};
            const data = await this.makeRequest(`${swapUrl}?${params}`, { headers });
            
            if (!data || !data.to) {
                console.log("⚠️ 0x: No route found");
                return null;
            }
            
            return {
                to: data.to,
                data: data.data,
                value: data.value || "0",
                estimatedOutput: data.buyAmount,
                gasEstimate: data.estimatedGas || data.gas || "500000",
                price: data.price,
                guaranteedPrice: data.guaranteedPrice,
                sources: data.sources || []
            };
            
        } catch (error) {
            console.error(`❌ 0x Error:`, this.formatError(error, 'getBestSwap'));
            return null;
        }
    }
    
    /**
     * Get a quote without building transaction (faster, implements base class method)
     * @param {string} srcToken - Source token address
     * @param {string} destToken - Destination token address
     * @param {string} amount - Amount to swap (in wei as string)
     * @returns {Promise<object|null>} Quote data or null if failed
     */
    async getQuote(srcToken, destToken, amount) {
        // Validate inputs
        if (!this.isValidAddress(srcToken) || !this.isValidAddress(destToken)) {
            return null;
        }
        
        if (!this.isValidAmount(amount)) {
            return null;
        }
        
        try {
            const apiUrl = this.getApiUrl();
            const priceUrl = `${apiUrl}/swap/v1/price`;
            const params = new URLSearchParams({
                buyToken: destToken,
                sellToken: srcToken,
                sellAmount: amount
            });
            
            const headers = this.apiKey ? { '0x-api-key': this.apiKey } : {};
            const data = await this.makeRequest(`${priceUrl}?${params}`, { headers });
            
            if (!data || !data.buyAmount) {
                return null;
            }
            
            return {
                srcToken: srcToken,
                destToken: destToken,
                srcAmount: amount,
                destAmount: data.buyAmount,
                estimatedGas: data.estimatedGas || data.gas || "500000",
                price: data.price,
                sources: data.sources || []
            };
            
        } catch (error) {
            console.error(`❌ 0x Quote Error:`, this.formatError(error, 'getQuote'));
            return null;
        }
    }
}

module.exports = { ZeroXManager };
