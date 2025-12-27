require('dotenv').config();
const BaseDEXManager = require('./base_dex_manager');

/**
 * OpenOceanManager - OpenOcean DEX Aggregator Integration
 * Supports 30+ chains with intelligent split routing
 * Best for: Best price discovery across 30+ chains
 * 
 * Extends BaseDEXManager for ARM-optimized performance (4 cores, 24GB RAM)
 */
class OpenOceanManager extends BaseDEXManager {
    /**
     * Initialize OpenOcean Manager
     * @param {number} chainId - EIP-155 Chain ID
     * @param {object} provider - Ethers provider (optional, for validation)
     */
    constructor(chainId, provider = null) {
        super('OpenOcean', chainId, provider, {
            maxRetries: 3,
            rateLimit: 10, // OpenOcean supports good rate limits
            cacheTTL: 30000 // 30 second cache
        });
        
        this.apiKey = process.env.OPENOCEAN_API_KEY || "";
        this.chainName = this.getChainName(chainId);
    }
    
    /**
     * Get API URL (override from base class)
     */
    getApiUrl() {
        return "https://open-api.openocean.finance/v3";
    }
    
    /**
     * Get chain name for OpenOcean API (override from base class)
     */
    getChainName(chainId) {
        const chainNames = {
            1: "eth",
            137: "polygon",
            42161: "arbitrum",
            10: "optimism",
            8453: "base",
            56: "bsc",
            43114: "avax",
            250: "fantom",
            100: "xdai",
            42220: "celo",
            1284: "moonbeam",
            1285: "moonriver",
            25: "cronos",
            1313161554: "aurora"
        };
        return chainNames[chainId] || "eth";
    }
    
    /**
     * Get the best swap quote from OpenOcean
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
            console.log("⚠️ OpenOcean: Invalid token address");
            return null;
        }
        
        if (!this.isValidAmount(amount)) {
            console.log("⚠️ OpenOcean: Invalid amount");
            return null;
        }
        
        try {
            const apiUrl = this.getApiUrl();
            const swapUrl = `${apiUrl}/${this.chainName}/swap_quote`;
            const params = new URLSearchParams({
                inTokenAddress: srcToken,
                outTokenAddress: destToken,
                amount: amount,
                gasPrice: "5",
                slippage: (slippageBps / 100).toString(),
                account: userAddress
            });
            
            const headers = this.apiKey ? { 'Authorization': `Bearer ${this.apiKey}` } : {};
            const data = await this.makeRequest(`${swapUrl}?${params}`, { headers });
            
            if (!data || !data.data) {
                console.log("⚠️ OpenOcean: No route found");
                return null;
            }
            
            const swapData = data.data;
            
            return {
                to: swapData.to,
                data: swapData.data,
                value: swapData.value || "0",
                estimatedOutput: swapData.outAmount,
                gasEstimate: swapData.estimatedGas || "500000",
                minOutAmount: swapData.minOutAmount,
                path: swapData.path || []
            };
            
        } catch (error) {
            console.error(`❌ OpenOcean Error:`, this.formatError(error, 'getBestSwap'));
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
            const quoteUrl = `${apiUrl}/${this.chainName}/quote`;
            const params = new URLSearchParams({
                inTokenAddress: srcToken,
                outTokenAddress: destToken,
                amount: amount,
                gasPrice: "5"
            });
            
            const headers = this.apiKey ? { 'Authorization': `Bearer ${this.apiKey}` } : {};
            const responseData = await this.makeRequest(`${quoteUrl}?${params}`, { headers });
            
            if (!responseData || !responseData.data) {
                return null;
            }
            
            const data = responseData.data;
            
            return {
                srcToken: srcToken,
                destToken: destToken,
                srcAmount: amount,
                destAmount: data.outAmount,
                estimatedGas: data.estimatedGas || "500000",
                minOutAmount: data.minOutAmount,
                path: data.path || []
            };
            
        } catch (error) {
            console.error(`❌ OpenOcean Quote Error:`, this.formatError(error, 'getQuote'));
            return null;
        }
    }
}

module.exports = { OpenOceanManager };
