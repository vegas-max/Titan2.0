require('dotenv').config();
const BaseDEXManager = require('./base_dex_manager');
const { ethers } = require('ethers');

/**
 * ParaSwapManager - DEX Aggregator Integration
 * Finds best swap routes across multiple DEXs using ParaSwap API
 * 
 * Extends BaseDEXManager for ARM-optimized performance (4 cores, 24GB RAM)
 */
class ParaSwapManager extends BaseDEXManager {
    /**
     * Initialize ParaSwap Manager
     * @param {number} chainId - EIP-155 Chain ID
     * @param {object} provider - Ethers provider (optional, for validation)
     * @param {number} slippageBps - Slippage tolerance in basis points (100 bps = 1%)
     */
    constructor(chainId, provider = null, slippageBps = 100) {
        super('ParaSwap', chainId, provider, {
            maxRetries: 3,
            rateLimit: 10, // ParaSwap allows higher rate limits
            cacheTTL: 30000 // 30 second cache
        });
        
        this.partnerAddress = process.env.PARASWAP_PARTNER_ADDRESS || "0x0000000000000000000000000000000000000000";
        this.slippageBps = slippageBps;
    }
    
    /**
     * Get API URL (override from base class)
     */
    getApiUrl() {
        return "https://apiv5.paraswap.io";
    }
    
    /**
     * Get the best swap quote from ParaSwap
     * @param {string} srcToken - Source token address
     * @param {string} destToken - Destination token address
     * @param {string} amount - Amount to swap (in wei as string)
     * @param {string} userAddress - User wallet address
     * @param {number} slippageBps - Optional slippage override in basis points (default: uses constructor value)
     * @returns {Promise<object|null>} Swap data or null if failed
     */
    async getBestSwap(srcToken, destToken, amount, userAddress, slippageBps = null) {
        // Validate inputs
        if (!this.isValidAddress(srcToken) || !this.isValidAddress(destToken)) {
            console.log("⚠️ ParaSwap: Invalid token address");
            return null;
        }
        
        if (!this.isValidAmount(amount)) {
            console.log("⚠️ ParaSwap: Invalid amount");
            return null;
        }
        
        try {
            const apiUrl = this.getApiUrl();
            
            // Fetch token decimals dynamically
            const srcDecimals = await this.getTokenDecimals(srcToken);
            const destDecimals = await this.getTokenDecimals(destToken);
            
            // Step 1: Get Price Quote using base class makeRequest
            const priceUrl = `${apiUrl}/prices`;
            const priceParams = new URLSearchParams({
                srcToken: srcToken,
                destToken: destToken,
                amount: amount,
                srcDecimals: srcDecimals.toString(),
                destDecimals: destDecimals.toString(),
                side: "SELL",
                network: this.chainId.toString(),
                partner: this.partnerAddress
            });
            
            const priceData = await this.makeRequest(`${priceUrl}?${priceParams}`);
            
            if (!priceData || !priceData.priceRoute) {
                console.log("⚠️ ParaSwap: No route found");
                return null;
            }
            
            const priceRoute = priceData.priceRoute;
            
            // Step 2: Build Transaction
            const txUrl = `${apiUrl}/transactions/${this.chainId}`;
            const txParams = {
                srcToken: srcToken,
                destToken: destToken,
                srcAmount: amount,
                destAmount: priceRoute.destAmount,
                priceRoute: priceRoute,
                userAddress: userAddress,
                partner: this.partnerAddress,
                slippage: slippageBps !== null ? slippageBps : this.slippageBps
            };
            
            const txData = await this.makeRequest(txUrl, {
                method: 'POST',
                data: txParams
            });
            
            if (!txData) {
                console.log("⚠️ ParaSwap: Transaction building failed");
                return null;
            }
            
            return {
                to: txData.to,
                data: txData.data,
                value: txData.value || "0",
                estimatedOutput: priceRoute.destAmount,
                gasEstimate: txData.gas || "500000"
            };
            
        } catch (error) {
            console.error(`❌ ParaSwap Error:`, this.formatError(error, 'getBestSwap'));
            return null;
        }
    }
    
    /**
     * Get token decimals (helper function)
     * @param {string} tokenAddress - Token contract address
     * @returns {Promise<number>} Token decimals
     */
    async getTokenDecimals(tokenAddress) {
        if (!this.provider) {
            return 18; // Default
        }
        
        try {
            const tokenContract = new ethers.Contract(
                tokenAddress,
                ['function decimals() view returns (uint8)'],
                this.provider
            );
            return await tokenContract.decimals();
        } catch (error) {
            return 18; // Default fallback
        }
    }
}

module.exports = { ParaSwapManager };
