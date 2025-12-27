require('dotenv').config();
const BaseDEXManager = require('./base_dex_manager');

/**
 * RangoManager - Rango Exchange Integration
 * Supports 70+ chains with cross-chain bridge aggregation
 * Best for: Complex cross-chain arbitrage paths
 * 
 * Extends BaseDEXManager for ARM-optimized performance (4 cores, 24GB RAM)
 */
class RangoManager extends BaseDEXManager {
    /**
     * Initialize Rango Manager
     * @param {number} chainId - EIP-155 Chain ID
     * @param {object} provider - Ethers provider (optional, for validation)
     */
    constructor(chainId, provider = null) {
        super('Rango', chainId, provider, {
            maxRetries: 3,
            rateLimit: 5, // Rango has moderate rate limits
            cacheTTL: 30000 // 30 second cache
        });
        
        this.apiKey = process.env.RANGO_API_KEY || "";
    }
    
    /**
     * Get API URL (override from base class)
     */
    getApiUrl() {
        return "https://api.rango.exchange";
    }
    
    /**
     * Get Rango blockchain identifier from chain ID
     */
    getBlockchainId(chainId) {
        const blockchainIds = {
            1: "ETH",
            137: "POLYGON",
            42161: "ARBITRUM",
            10: "OPTIMISM",
            8453: "BASE",
            56: "BSC",
            43114: "AVAX_CCHAIN",
            250: "FANTOM"
        };
        return blockchainIds[chainId] || "ETH";
    }
    
    /**
     * Get the best swap quote from Rango
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
            console.log("⚠️ Rango: Invalid token address");
            return null;
        }
        
        if (!this.isValidAmount(amount)) {
            console.log("⚠️ Rango: Invalid amount");
            return null;
        }
        
        try {
            const apiUrl = this.getApiUrl();
            const swapUrl = `${apiUrl}/basic/swap`;
            const params = {
                from: {
                    blockchain: this.getBlockchainId(this.chainId),
                    symbol: srcToken,
                    address: srcToken
                },
                to: {
                    blockchain: this.getBlockchainId(this.chainId),
                    symbol: destToken,
                    address: destToken
                },
                amount: amount,
                fromAddress: userAddress,
                toAddress: userAddress,
                slippage: slippageBps / 100
            };
            
            const headers = this.apiKey ? { 'API-KEY': this.apiKey } : {};
            const data = await this.makeRequest(swapUrl, { 
                method: 'POST',
                data: params,
                headers
            });
            
            if (!data || !data.route) {
                console.log("⚠️ Rango: No route found");
                return null;
            }
            
            const route = data.route;
            
            return {
                to: route.to || userAddress,
                data: route.data || "0x",
                value: route.value || "0",
                estimatedOutput: route.outputAmount || "0",
                gasEstimate: "500000",
                routeId: data.requestId
            };
            
        } catch (error) {
            console.error(`❌ Rango Error:`, this.formatError(error, 'getBestSwap'));
            return null;
        }
    }
    
    /**
     * Get a quote without building transaction (implements base class method)
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
            // For now, use the same swap endpoint but extract quote only
            const result = await this.getBestSwap(
                srcToken, 
                destToken, 
                amount, 
                "0x0000000000000000000000000000000000000001", 
                100
            );
            
            if (!result) {
                return null;
            }
            
            return {
                srcToken: srcToken,
                destToken: destToken,
                srcAmount: amount,
                destAmount: result.estimatedOutput,
                estimatedGas: "500000"
            };
            
        } catch (error) {
            console.error(`❌ Rango Quote Error:`, this.formatError(error, 'getQuote'));
            return null;
        }
    }
}

module.exports = { RangoManager };
