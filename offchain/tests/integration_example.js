/**
 * Integration Example - DEX Scanner Enhancement
 * 
 * Demonstrates how to use the new modules together:
 * - Token Universe for canonical pairs
 * - TWAP Accumulator for price validation
 * - Curve Quoter for multi-coin pools
 * - Balancer Router for multi-hop routing
 * 
 * Run with: node offchain/tests/integration_example.js
 */

require('dotenv').config();
const { ethers } = require('ethers');

// Import our new modules
const { 
  TOKENS, 
  getAvailablePairs, 
  getTokenSymbol 
} = require('../core/tokenUniverse');

const { 
  TWAPAccumulator, 
  MultiPoolTWAP 
} = require('../core/twapAccumulator');

const {
  curveQuoteByTokens,
  getCurvePoolCoins
} = require('../core/curveQuoter');

const {
  buildBalancerLegs,
  quoteBalancerMultiHop
} = require('../core/balancerRouter');

// Configuration
const POLYGON_RPC = process.env.RPC_POLYGON || 'https://polygon-rpc.com';
const CHAIN_ID = 137;

// Known contract addresses on Polygon
const CURVE_AAVE_POOL = '0x445FE580eF8d70FF569aB36e80c647af338db351';
const BALANCER_VAULT = '0xBA12222222228d8Ba445958a75a0704d566BF2C8';

async function demonstrateTokenUniverse() {
  console.log('\n=== Token Universe Demo ===\n');
  
  // Get available pairs for Polygon
  const pairs = getAvailablePairs(CHAIN_ID);
  console.log(`Found ${pairs.length} trading pairs on Polygon`);
  
  // Show first 5 pairs
  console.log('\nFirst 5 pairs:');
  for (let i = 0; i < Math.min(5, pairs.length); i++) {
    const [tokenA, tokenB] = pairs[i];
    const symbolA = getTokenSymbol(CHAIN_ID, tokenA);
    const symbolB = getTokenSymbol(CHAIN_ID, tokenB);
    console.log(`  ${symbolA}/${symbolB}: ${tokenA} <-> ${tokenB}`);
  }
  
  // Show stablecoin pairs (Curve-optimized)
  console.log('\nStablecoin pairs (Curve-optimized):');
  const stablecoins = ['USDC', 'USDT', 'DAI'];
  for (const tokenA of stablecoins) {
    for (const tokenB of stablecoins) {
      if (tokenA < tokenB) {
        const addrA = TOKENS[CHAIN_ID][tokenA];
        const addrB = TOKENS[CHAIN_ID][tokenB];
        if (addrA && addrB) {
          console.log(`  ${tokenA}/${tokenB}`);
        }
      }
    }
  }
}

async function demonstrateTWAPAccumulator() {
  console.log('\n=== TWAP Accumulator Demo ===\n');
  
  // Single pool TWAP
  const twap = new TWAPAccumulator({ windowMs: 30000, minSamples: 2 });
  
  console.log('Simulating price updates for WMATIC/USDC:');
  const prices = [0.85, 0.86, 0.84, 0.87, 0.85];
  
  for (const price of prices) {
    twap.push(price);
    console.log(`  Price: $${price}, TWAP: $${twap.value().toFixed(4)}, Samples: ${twap.sampleCount()}`);
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  
  console.log(`\nFinal TWAP: $${twap.value().toFixed(4)}`);
  console.log(`Latest spot: $${twap.latest().toFixed(4)}`);
  console.log(`Volatility: ${(twap.volatility() * 100).toFixed(2)}%`);
  console.log(`Is ready: ${twap.isReady()}`);
  
  // Multi-pool TWAP
  console.log('\n--- Multi-Pool TWAP Manager ---');
  const manager = new MultiPoolTWAP();
  
  const WMATIC = TOKENS[CHAIN_ID].WMATIC;
  const USDC = TOKENS[CHAIN_ID].USDC;
  const USDT = TOKENS[CHAIN_ID].USDT;
  
  manager.push(WMATIC, USDC, 0.85);
  manager.push(WMATIC, USDT, 0.86);
  manager.push(USDC, USDT, 1.0001);
  
  console.log(`Tracking ${manager.poolCount()} pools`);
  console.log(`WMATIC/USDC TWAP: $${manager.value(WMATIC, USDC).toFixed(4)}`);
  console.log(`WMATIC/USDT TWAP: $${manager.value(WMATIC, USDT).toFixed(4)}`);
  console.log(`USDC/USDT TWAP: $${manager.value(USDC, USDT).toFixed(6)}`);
}

async function demonstrateCurveQuoter() {
  console.log('\n=== Curve Multi-Coin Quoter Demo ===\n');
  
  try {
    const provider = new ethers.JsonRpcProvider(POLYGON_RPC);
    
    // Get coins in Curve aave pool
    console.log(`Querying Curve pool: ${CURVE_AAVE_POOL}`);
    const coins = await getCurvePoolCoins(CURVE_AAVE_POOL, provider);
    
    console.log(`Found ${coins.length} coins in pool:`);
    for (let i = 0; i < coins.length; i++) {
      const symbol = getTokenSymbol(CHAIN_ID, coins[i]) || 'UNKNOWN';
      console.log(`  [${i}] ${symbol}: ${coins[i]}`);
    }
    
    // Quote a swap
    if (coins.length >= 2) {
      const amountIn = ethers.parseUnits('1000', 6); // 1000 USDC
      console.log(`\nQuoting: 1000 USDC -> USDT`);
      
      const USDC = TOKENS[CHAIN_ID].USDC;
      const USDT = TOKENS[CHAIN_ID].USDT;
      
      const output = await curveQuoteByTokens(
        CURVE_AAVE_POOL,
        provider,
        amountIn,
        USDC,
        USDT
      );
      
      if (output) {
        const outputFormatted = ethers.formatUnits(output, 6);
        console.log(`Expected output: ${outputFormatted} USDT`);
        console.log(`Price impact: ${((1000 - parseFloat(outputFormatted)) / 1000 * 100).toFixed(4)}%`);
      } else {
        console.log('Quote failed (tokens may not be in pool)');
      }
    }
  } catch (error) {
    console.log(`Note: Live Curve query requires RPC access: ${error.message}`);
  }
}

async function demonstrateBalancerRouter() {
  console.log('\n=== Balancer Multi-Hop Router Demo ===\n');
  
  try {
    const provider = new ethers.JsonRpcProvider(POLYGON_RPC);
    
    // Example: WMATIC -> WETH -> USDC route
    const WMATIC = TOKENS[CHAIN_ID].WMATIC;
    const WETH = TOKENS[CHAIN_ID].WETH;
    const USDC = TOKENS[CHAIN_ID].USDC;
    
    const assets = [WMATIC, WETH, USDC];
    const path = [0, 1, 2]; // WMATIC(0) -> WETH(1) -> USDC(2)
    const amountIn = ethers.parseEther('100'); // 100 WMATIC
    
    console.log('Building multi-hop route:');
    console.log(`  ${getTokenSymbol(CHAIN_ID, WMATIC)} -> ${getTokenSymbol(CHAIN_ID, WETH)} -> ${getTokenSymbol(CHAIN_ID, USDC)}`);
    console.log(`  Input: ${ethers.formatEther(amountIn)} WMATIC`);
    
    // Build legs (using a mock pool ID for demonstration)
    const mockPoolId = '0x' + '0'.repeat(64);
    const legs = buildBalancerLegs(mockPoolId, assets, path, amountIn);
    
    console.log(`\nGenerated ${legs.length} swap legs:`);
    for (let i = 0; i < legs.length; i++) {
      const leg = legs[i];
      console.log(`  Leg ${i + 1}: asset[${leg.assetInIndex}] -> asset[${leg.assetOutIndex}]`);
      console.log(`    Amount: ${leg.amount}`);
    }
    
    console.log('\nNote: Live Balancer query requires valid pool ID and RPC access');
  } catch (error) {
    console.log(`Note: Balancer router demo requires RPC access: ${error.message}`);
  }
}

async function demonstrateIntegration() {
  console.log('\n=== Full Integration Example ===\n');
  
  console.log('This example shows how all components work together:');
  console.log('1. Token Universe provides canonical token pairs');
  console.log('2. TWAP Accumulator validates prices over time');
  console.log('3. Curve Quoter handles stablecoin loops efficiently');
  console.log('4. Balancer Router enables complex multi-hop routes');
  
  // Simulated arbitrage scan workflow
  console.log('\n--- Simulated Arbitrage Scan Workflow ---\n');
  
  // Step 1: Get tradable pairs
  const pairs = getAvailablePairs(CHAIN_ID);
  console.log(`Step 1: Found ${pairs.length} tradable pairs`);
  
  // Step 2: Initialize TWAP tracking
  const twapManager = new MultiPoolTWAP({ windowMs: 30000 });
  console.log('Step 2: TWAP manager initialized');
  
  // Step 3: Simulate price updates from DEX events
  console.log('Step 3: Processing Sync events and updating TWAPs...');
  const WMATIC = TOKENS[CHAIN_ID].WMATIC;
  const USDC = TOKENS[CHAIN_ID].USDC;
  
  twapManager.push(WMATIC, USDC, 0.85);
  twapManager.push(WMATIC, USDC, 0.86);
  twapManager.push(WMATIC, USDC, 0.84);
  
  const twap = twapManager.value(WMATIC, USDC);
  console.log(`  WMATIC/USDC TWAP: $${twap.toFixed(4)}`);
  
  // Step 4: Validate spot price against TWAP
  const spotPrice = 0.87;
  const deviation = Math.abs(spotPrice - twap) / twap;
  console.log(`\nStep 4: Validating spot price against TWAP`);
  console.log(`  Spot: $${spotPrice}, TWAP: $${twap.toFixed(4)}`);
  console.log(`  Deviation: ${(deviation * 100).toFixed(2)}%`);
  console.log(`  Within 5% bounds: ${deviation <= 0.05 ? '✅ Yes' : '❌ No'}`);
  
  // Step 5: Route optimization
  console.log('\nStep 5: Route optimization');
  console.log('  - For stablecoins: Use Curve (deep liquidity, low slippage)');
  console.log('  - For multi-hop: Use Balancer (efficient batching)');
  console.log('  - For simple swaps: Use Uniswap V3 (best for most pairs)');
  
  console.log('\n✅ Integration example completed successfully!');
}

// Run all demonstrations
async function main() {
  console.log('╔═══════════════════════════════════════════════════════════╗');
  console.log('║   DEX Scanner Enhancement - Integration Example          ║');
  console.log('╚═══════════════════════════════════════════════════════════╝');
  
  try {
    await demonstrateTokenUniverse();
    await demonstrateTWAPAccumulator();
    await demonstrateCurveQuoter();
    await demonstrateBalancerRouter();
    await demonstrateIntegration();
    
    console.log('\n╔═══════════════════════════════════════════════════════════╗');
    console.log('║   All demonstrations completed successfully! 🎉           ║');
    console.log('╚═══════════════════════════════════════════════════════════╝\n');
  } catch (error) {
    console.error('Error in demonstration:', error);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  main().catch(console.error);
}

module.exports = { main };
