require('dotenv').config();
const { createConfig, EVM, executeRoute, getRoutes } = require('@lifi/sdk');
const { ethers } = require('ethers');

// === 1. SDK CONFIGURATION ===
// This maps your .env RPCs to the Li.Fi SDK Providers
const config = createConfig({
  integrator: 'Apex-Omega-Titan',
  providers: [
    EVM({
      getWalletClient: async (chainId) => {
        // Dynamic Wallet Switcher based on Chain ID
        let rpcUrl = '';
        switch (chainId) {
          case 1: rpcUrl = process.env.RPC_ETHEREUM; break;
          case 137: rpcUrl = process.env.RPC_POLYGON; break;
          case 42161: rpcUrl = process.env.RPC_ARBITRUM; break;
          case 10: rpcUrl = process.env.RPC_OPTIMISM; break;
          case 56: rpcUrl = process.env.RPC_BSC; break;
          case 43114: rpcUrl = process.env.RPC_AVALANCHE; break;
          case 8453: rpcUrl = process.env.RPC_BASE; break;
          case 250: rpcUrl = process.env.RPC_FANTOM; break;
          case 59144: rpcUrl = process.env.RPC_LINEA; break;
          case 534352: rpcUrl = process.env.RPC_SCROLL; break;
          default: throw new Error(`Unsupported Chain: ${chainId}`);
        }
        
        // Return a Viem-compatible wallet client (wrapped ethers for SDK compatibility)
        const provider = new ethers.JsonRpcProvider(rpcUrl);
        const signer = new ethers.Wallet(process.env.PRIVATE_KEY, provider);
        return signer;
      },
    }),
  ],
});

// === 2. EXECUTION ENGINE ===
class LifiExecutionEngine {
  
  /**
   * Finds the best route and executes it immediately.
   * @param {number} fromChainId - Source Chain ID (e.g., 137)
   * @param {number} toChainId - Destination Chain ID (e.g., 42161)
   * @param {string} fromToken - Address of token to sell
   * @param {string} toToken - Address of token to buy
   * @param {string} amount - Raw amount (e.g., "1000000")
   */
  static async bridgeAssets(fromChainId, toChainId, fromToken, toToken, amount) {
    console.log(`🌉 Li.Fi: Calculating best route from ${fromChainId} to ${toChainId}...`);

    try {
      // A. Get Route (Quote)
      const routeResponse = await getRoutes({
        fromChainId,
        toChainId,
        fromTokenAddress: fromToken,
        toTokenAddress: toToken,
        fromAmount: amount,
        options: {
          integrator: 'Apex-Omega-Titan',
          order: 'CHEAPEST', // Optimize for Profit Margin
          slippage: 0.005,   // 0.5% Slippage Tolerance
        },
      });

      const bestRoute = routeResponse.routes[0];
      if (!bestRoute) {
        console.log('❌ Li.Fi: No route found.');
        return null;
      }

      console.log(`✅ Route Found: Via ${bestRoute.steps[0].tool} | Gas Cost: $${bestRoute.gasCostUSD}`);

      // B. Execute Route
      // The SDK handles Approvals -> Swap -> Bridge automatically
      const executedRoute = await executeRoute(bestRoute, config);

      console.log('🚀 Bridge Transaction Sent!');
      return executedRoute;

    } catch (error) {
      console.error('❌ Li.Fi Execution Failed:', error.message);
      return null;
    }
  }
}

module.exports = { LifiExecutionEngine };