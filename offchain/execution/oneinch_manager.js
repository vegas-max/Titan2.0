require('dotenv').config();
const BaseDEXManager = require('./base_dex_manager');

/**
 * OneInchManager - 1inch DEX Aggregator Integration
 * Uses 1inch Pathfinder for optimal routing across multiple DEXs
 * Best for: Fast single-chain arbitrage (<1s execution)
 * 
 * Extends BaseDEXManager for ARM-optimized performance (4 cores, 24GB RAM)
 */
class OneInchManager extends BaseDEXManager {
    /**
     * Initialize 1inch Manager
     * @param {number} chainId - EIP-155 Chain ID
     * @param {object} provider - Ethers provider (optional, for validation)
     */
    constructor(chainId, provider = null) {
        super('1inch', chainId, provider, {
            maxRetries: 3,
            rateLimit: 5, // 1inch has rate limits
            cacheTTL: 30000 // 30 second cache for quotes
        });
        
        this.apiKey = process.env.ONEINCH_API_KEY || "";
        this.referrerAddress = process.env.ONEINCH_REFERRER_ADDRESS || "0x0000000000000000000000000000000000000000";
    }
    
    /**
     * Get API URL (override from base class)
     */
    getApiUrl() {
        return "https://api.1inch.dev/swap/v6.0";
    }
    
    /**
     * Get the best swap quote from 1inch
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
            console.log("⚠️ 1inch: Invalid token address");
            return null;
        }
        
        if (!this.isValidAmount(amount)) {
            console.log("⚠️ 1inch: Invalid amount");
            return null;
        }
        
        try {
            const apiUrl = this.getApiUrl();
            const headers = this.apiKey ? { 'Authorization': `Bearer ${this.apiKey}` } : {};
            
            // Step 1: Get Quote using base class makeRequest
            const quoteUrl = `${apiUrl}/${this.chainId}/quote`;
            const quoteParams = new URLSearchParams({
                src: srcToken,
                dst: destToken,
                amount: amount
            });
            
            const quoteData = await this.makeRequest(`${quoteUrl}?${quoteParams}`, { headers });
            
            if (!quoteData || !quoteData.dstAmount) {
                console.log("⚠️ 1inch: No route found");
                return null;
            }
            
            const estimatedOutput = quoteData.dstAmount;
            
            // Step 2: Get Swap Transaction
            const swapUrl = `${apiUrl}/${this.chainId}/swap`;
            const swapParams = new URLSearchParams({
                src: srcToken,
                dst: destToken,
                amount: amount,
                from: userAddress,
                slippage: slippageBps / 100,
                referrer: this.referrerAddress,
                disableEstimate: 'false',
                allowPartialFill: 'false'
            });
            
            const swapData = await this.makeRequest(`${swapUrl}?${swapParams}`, { headers });
            
            if (!swapData || !swapData.tx) {
                console.log("⚠️ 1inch: Transaction building failed");
                return null;
            }
            
            const txData = swapData.tx;
            
            return {
                to: txData.to,
                data: txData.data,
                value: txData.value || "0",
                estimatedOutput: estimatedOutput,
                gasEstimate: txData.gas || "500000",
                protocols: swapData.protocols || []
            };
            
        } catch (error) {
            console.error(`❌ 1inch Error:`, this.formatError(error, 'getBestSwap'));
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
            const quoteUrl = `${apiUrl}/${this.chainId}/quote`;
            const quoteParams = new URLSearchParams({
                src: srcToken,
                dst: destToken,
                amount: amount
            });
            
            const headers = this.apiKey ? { 'Authorization': `Bearer ${this.apiKey}` } : {};
            const quoteData = await this.makeRequest(`${quoteUrl}?${quoteParams}`, { headers });
            
            if (!quoteData || !quoteData.dstAmount) {
                return null;
            }
            
            return {
                srcToken: srcToken,
                destToken: destToken,
                srcAmount: amount,
                destAmount: quoteData.dstAmount,
                estimatedGas: quoteData.estimatedGas || "500000",
                protocols: quoteData.protocols || []
            };
            
        } catch (error) {
            console.error(`❌ 1inch Quote Error:`, this.formatError(error, 'getQuote'));
            return null;
        }
    }
}

module.exports = { OneInchManager };
