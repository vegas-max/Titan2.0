/**
 * Example Integration: Arbitrage Engine with Bot
 * 
 * This example shows how to integrate the arbitrage engine into the existing bot.js
 * execution flow for optimal contract selection and payload generation.
 */

const { ethers } = require('ethers');
const { ArbitrageEngine } = require('./arbitrage_engine');

/**
 * Example: Enhanced Trade Execution with Arbitrage Engine
 * 
 * This function demonstrates how to integrate the arbitrage engine
 * into the existing executeTrade workflow.
 */
async function executeTradeWithArbitrageEngine(signal, provider, wallet) {
    const chainId = signal.chainId;
    
    console.log(`\n🎯 Processing arbitrage signal for chain ${chainId}`);
    console.log(`   Signal Type: ${signal.type || 'STANDARD'}`);
    
    // Initialize arbitrage engine
    const arbEngine = new ArbitrageEngine(provider, chainId);
    
    // Prepare opportunity data structure
    const opportunity = {
        // Token path (e.g., [WETH, USDC, WETH])
        path: signal.path || [signal.token, signal.destToken, signal.token],
        
        // Exchange names (e.g., ['Quickswap', 'Sushiswap'])
        exchanges: signal.exchanges || extractExchangeNames(signal.routers),
        
        // Router addresses for path-based execution
        routers: signal.routers || [],
        
        // Pool addresses for HFT direct execution (if available)
        poolAddressA: signal.poolAddressA || signal.poolAddress_A,
        poolAddressB: signal.poolAddressB || signal.poolAddress_B,
        
        // Amount in WEI
        amountIn: signal.amount || ethers.parseEther('1.0'),
        
        // Additional metadata
        profit: signal.metrics?.profit_usd || 0,
        gasPrice: signal.gasPrice || 0
    };
    
    try {
        // Run arbitrage engine decision logic
        console.log('🔍 Running arbitrage engine...');
        const decision = await arbEngine.selectExecutionEngine(opportunity);
        
        console.log(`✅ Decision made:`);
        console.log(`   Target Contract: ${decision.target}`);
        console.log(`   Gate: ${decision.gate}`);
        console.log(`   Reason: ${decision.reason}`);
        
        if (decision.gasHFT && decision.gasRouter) {
            console.log(`   Gas Estimates: HFT=${decision.gasHFT}, Router=${decision.gasRouter}`);
        }
        
        // Prepare transaction with selected contract and payload
        const txRequest = {
            to: decision.target,
            data: decision.payload,
            gasLimit: 500000, // Will be estimated properly
        };
        
        // Add gas price/fees
        const feeData = await provider.getFeeData();
        if (feeData.maxFeePerGas) {
            txRequest.maxFeePerGas = feeData.maxFeePerGas;
            txRequest.maxPriorityFeePerGas = feeData.maxPriorityFeePerGas;
        } else {
            txRequest.gasPrice = feeData.gasPrice;
        }
        
        // Estimate gas with the selected payload
        const estimatedGas = await provider.estimateGas(txRequest);
        txRequest.gasLimit = estimatedGas * 120n / 100n; // 20% buffer
        
        console.log(`   Estimated Gas: ${estimatedGas.toString()}`);
        
        // Execute transaction
        console.log('🚀 Submitting transaction...');
        const tx = await wallet.sendTransaction(txRequest);
        
        console.log(`✅ Transaction submitted: ${tx.hash}`);
        
        // Wait for confirmation
        const receipt = await tx.wait();
        
        if (receipt.status === 1) {
            console.log(`✅ Transaction confirmed in block ${receipt.blockNumber}`);
            return {
                success: true,
                txHash: tx.hash,
                blockNumber: receipt.blockNumber,
                gasUsed: receipt.gasUsed.toString(),
                decision: decision
            };
        } else {
            console.log(`❌ Transaction failed`);
            return {
                success: false,
                txHash: tx.hash,
                decision: decision
            };
        }
        
    } catch (error) {
        console.error(`❌ Execution failed:`, error.message);
        return {
            success: false,
            error: error.message
        };
    }
}

/**
 * Helper: Extract exchange names from router addresses
 * This is a simplified version - in production, use a proper registry
 */
function extractExchangeNames(routers) {
    if (!routers || routers.length === 0) return [];
    
    // Map of known router addresses to exchange names (example for Polygon)
    const ROUTER_REGISTRY = {
        // Polygon mainnet
        '0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff': 'Quickswap',
        '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506': 'Sushiswap',
        // Add more as needed
    };
    
    return routers.map(router => {
        const normalized = router.toLowerCase();
        for (const [addr, name] of Object.entries(ROUTER_REGISTRY)) {
            if (normalized === addr.toLowerCase()) {
                return name;
            }
        }
        return 'Unknown'; // Fallback to Router execution
    });
}

/**
 * Example Usage in Bot Context
 */
async function exampleBotIntegration() {
    // Setup
    const RPC_URL = process.env.RPC_POLYGON;
    const PRIVATE_KEY = process.env.PRIVATE_KEY;
    
    const provider = new ethers.JsonRpcProvider(RPC_URL);
    const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
    
    // Example signal from brain
    const signal = {
        chainId: 137, // Polygon
        token: '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619', // WETH
        destToken: '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174', // USDC
        path: [
            '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619', // WETH
            '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174', // USDC
            '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619'  // WETH
        ],
        exchanges: ['Quickswap', 'Sushiswap'],
        routers: [
            '0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff', // Quickswap
            '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506'  // Sushiswap
        ],
        amount: ethers.parseEther('1.0'),
        metrics: {
            profit_usd: 50.00
        }
    };
    
    // Execute with arbitrage engine
    const result = await executeTradeWithArbitrageEngine(signal, provider, wallet);
    
    console.log('\n📊 Execution Result:');
    console.log(JSON.stringify(result, null, 2));
}

/**
 * Simplified Integration Point for bot.js
 * 
 * Add this to your existing executeTrade function:
 */
async function integrateIntoExistingBot(signal, provider, wallet, chainId) {
    // 1. Initialize engine
    const arbEngine = new ArbitrageEngine(provider, chainId);
    
    // 2. Prepare opportunity from signal
    const opportunity = {
        path: signal.path,
        exchanges: signal.exchanges,
        routers: signal.routers,
        poolAddressA: signal.poolAddressA,
        poolAddressB: signal.poolAddressB,
        amountIn: signal.amount
    };
    
    // 3. Get decision
    const decision = await arbEngine.selectExecutionEngine(opportunity);
    
    // 4. Use decision.target and decision.payload instead of manually building
    const tx = await wallet.sendTransaction({
        to: decision.target,
        data: decision.payload,
        // ... gas params
    });
    
    return tx;
}

// Export functions
module.exports = {
    executeTradeWithArbitrageEngine,
    extractExchangeNames,
    integrateIntoExistingBot
};

// Run example if executed directly
if (require.main === module) {
    console.log('🔧 Arbitrage Engine Integration Example\n');
    console.log('This is an example file. To use:');
    console.log('1. Set environment variables (RPC_POLYGON, PRIVATE_KEY)');
    console.log('2. Deploy HFT and Router contracts');
    console.log('3. Set HFT_CONTRACT_ADDRESS and ROUTER_CONTRACT_ADDRESS');
    console.log('4. Integrate into bot.js executeTrade function\n');
}
