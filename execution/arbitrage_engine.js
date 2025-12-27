/**
 * Arbitrage Engine - Strict Deterministic Logic for Arbitrage Opportunities
 * 
 * This module implements a rigid decision matrix to evaluate arbitrage opportunities
 * and select the optimal execution path between HFT and Router contracts.
 */

const { ethers } = require('ethers');

// Contract addresses (to be set via environment or config)
const CONTRACT_HFT = process.env.HFT_CONTRACT_ADDRESS || '0xAF00000000000000000000000000000000000000';
const CONTRACT_ROUTER = process.env.ROUTER_CONTRACT_ADDRESS || '0x4400000000000000000000000000000000000000';

// Known Uniswap V2 forks by chain
const V2_COMPATIBLE_DEXES = {
    1: ['uniswap', 'sushiswap', 'shibaswap'], // Ethereum
    137: ['quickswap', 'sushiswap', 'apeswap'], // Polygon
    56: ['pancakeswap', 'apeswap', 'biswap'], // BSC
    42161: ['sushiswap', 'camelot'], // Arbitrum
    10: ['velodrome', 'zipswap'], // Optimism
    8453: ['baseswap', 'aerodrome'], // Base
    43114: ['traderjoe', 'pangolin'], // Avalanche
    250: ['spookyswap', 'spiritswap'] // Fantom
};

// HFT Contract ABI
const HFT_ABI = [
    {
        "constant": false,
        "inputs": [
            {"name": "_poolA", "type": "address"},
            {"name": "_poolB", "type": "address"},
            {"name": "_amount", "type": "uint256"}
        ],
        "name": "startArbitrage",
        "outputs": [],
        "type": "function"
    }
];

// Router Contract ABI
const ROUTER_ABI = [
    {
        "constant": false,
        "inputs": [
            {"name": "_path", "type": "address[]"},
            {"name": "_routers", "type": "address[]"},
            {"name": "_amount", "type": "uint256"}
        ],
        "name": "startArbitrage",
        "outputs": [],
        "type": "function"
    }
];

/**
 * ArbitrageEngine - Main decision engine class
 */
class ArbitrageEngine {
    constructor(provider, chainId) {
        this.provider = provider;
        this.chainId = chainId;
        this.hftContract = CONTRACT_HFT;
        this.routerContract = CONTRACT_ROUTER;
    }

    /**
     * Gate 1: Topology Check (Hard Constraint)
     * 
     * If path length > 2, it's a multi-hop (triangular) arbitrage
     * HFT only supports direct pair swaps (path length = 2)
     * 
     * @param {Object} opportunity - Arbitrage opportunity data
     * @returns {Object|null} - Decision object or null to continue
     */
    _gate1_topologyCheck(opportunity) {
        const pathLength = opportunity.path.length;
        
        if (pathLength > 2) {
            // Multi-hop path - must use Router
            return {
                target: this.routerContract,
                reason: 'TOPOLOGY_CHECK: Path length > 2 requires Router for multi-hop execution',
                gate: 'GATE_1'
            };
        }
        
        // Simple swap - proceed to next gate
        return null;
    }

    /**
     * Gate 2: Liquidity Source Check (Technology Constraint)
     * 
     * Check if both exchanges are standard Uniswap V2 forks
     * HFT uses IUniswapV2Pair ABI and will revert on non-V2 pools
     * 
     * @param {Object} opportunity - Arbitrage opportunity data
     * @returns {Object|null} - Decision object or null to continue
     */
    _gate2_liquiditySourceCheck(opportunity) {
        const exchanges = opportunity.exchanges || [];
        const v2Compatible = V2_COMPATIBLE_DEXES[this.chainId] || [];
        
        // Check if all exchanges are V2 compatible
        for (const exchange of exchanges) {
            const exchangeName = exchange.toLowerCase();
            const isV2 = v2Compatible.some(dex => exchangeName.includes(dex));
            
            // Check for known non-V2 protocols
            const isNonV2 = exchangeName.includes('v3') || 
                          exchangeName.includes('curve') || 
                          exchangeName.includes('balancer');
            
            if (isNonV2 || !isV2) {
                // Non-V2 exchange detected - must use Router
                return {
                    target: this.routerContract,
                    reason: `LIQUIDITY_CHECK: Exchange ${exchange} is not V2 compatible`,
                    gate: 'GATE_2'
                };
            }
        }
        
        // All exchanges are V2 compatible - proceed to next gate
        return null;
    }

    /**
     * Gate 3: Gas Simulation (Economic Determinism)
     * 
     * Simulate gas usage for both HFT and Router contracts
     * Select the one with lower gas consumption
     * 
     * @param {Object} opportunity - Arbitrage opportunity data
     * @returns {Object} - Decision object
     */
    async _gate3_gasSimulation(opportunity) {
        try {
            // Build payloads for both contracts
            const hftPayload = this._buildHFTPayload(opportunity);
            const routerPayload = this._buildRouterPayload(opportunity);
            
            // Estimate gas for HFT contract
            let gasHFT;
            try {
                gasHFT = await this.provider.estimateGas({
                    to: this.hftContract,
                    data: hftPayload
                });
            } catch (e) {
                // HFT estimation failed - use Router
                return {
                    target: this.routerContract,
                    payload: routerPayload,
                    reason: 'GAS_SIMULATION: HFT estimation failed, using Router',
                    gate: 'GATE_3'
                };
            }
            
            // Estimate gas for Router contract
            let gasRouter;
            try {
                gasRouter = await this.provider.estimateGas({
                    to: this.routerContract,
                    data: routerPayload
                });
            } catch (e) {
                // Router estimation failed - use HFT (already validated)
                return {
                    target: this.hftContract,
                    payload: hftPayload,
                    gasHFT: gasHFT.toString(),
                    reason: 'GAS_SIMULATION: Router estimation failed, using HFT',
                    gate: 'GATE_3'
                };
            }
            
            // Compare gas costs
            if (gasHFT < gasRouter) {
                return {
                    target: this.hftContract,
                    payload: hftPayload,
                    gasHFT: gasHFT.toString(),
                    gasRouter: gasRouter.toString(),
                    reason: 'GAS_SIMULATION: HFT is more gas efficient',
                    gate: 'GATE_3'
                };
            } else {
                return {
                    target: this.routerContract,
                    payload: routerPayload,
                    gasHFT: gasHFT.toString(),
                    gasRouter: gasRouter.toString(),
                    reason: 'GAS_SIMULATION: Router is more gas efficient or equal',
                    gate: 'GATE_3'
                };
            }
            
        } catch (error) {
            // On any error, fallback to Router for safety
            return {
                target: this.routerContract,
                payload: this._buildRouterPayload(opportunity),
                reason: `GAS_SIMULATION: Error occurred (${error.message}), using Router for safety`,
                gate: 'GATE_3'
            };
        }
    }

    /**
     * Build HFT payload for direct pool interaction
     * Function signature: startArbitrage(address,address,uint256)
     * 
     * @param {Object} opportunity - Arbitrage opportunity data
     * @returns {string} - Encoded transaction data
     */
    _buildHFTPayload(opportunity) {
        const iface = new ethers.Interface(HFT_ABI);
        
        // For HFT, we need pool addresses, not router addresses
        // Assuming opportunity has poolAddressA and poolAddressB
        const poolA = opportunity.poolAddressA || opportunity.poolAddress_A;
        const poolB = opportunity.poolAddressB || opportunity.poolAddress_B;
        const amount = opportunity.amountIn || opportunity.amount;
        
        return iface.encodeFunctionData('startArbitrage', [
            poolA,
            poolB,
            amount
        ]);
    }

    /**
     * Build Router payload for path-based execution
     * Function signature: startArbitrage(address[],address[],uint256)
     * 
     * @param {Object} opportunity - Arbitrage opportunity data
     * @returns {string} - Encoded transaction data
     */
    _buildRouterPayload(opportunity) {
        const iface = new ethers.Interface(ROUTER_ABI);
        
        const path = opportunity.path;
        const routers = opportunity.routers;
        const amount = opportunity.amountIn || opportunity.amount;
        
        return iface.encodeFunctionData('startArbitrage', [
            path,
            routers,
            amount
        ]);
    }

    /**
     * Main selection logic - runs all gates in sequence
     * 
     * @param {Object} opportunity - Arbitrage opportunity data structure
     * @returns {Promise<Object>} - {target: address, payload: data, reason: string}
     */
    async selectExecutionEngine(opportunity) {
        // Validate opportunity structure
        if (!opportunity || !opportunity.path || !opportunity.exchanges) {
            throw new Error('Invalid opportunity structure: missing path or exchanges');
        }
        
        console.log('\n🔍 ARBITRAGE ENGINE: Evaluating opportunity...');
        console.log(`   Path: ${opportunity.path.join(' → ')}`);
        console.log(`   Exchanges: ${opportunity.exchanges.join(', ')}`);
        console.log(`   Amount: ${opportunity.amountIn || opportunity.amount}`);
        
        // --- Gate 1: Topology Check ---
        const gate1Result = this._gate1_topologyCheck(opportunity);
        if (gate1Result) {
            console.log(`   ✓ ${gate1Result.reason}`);
            gate1Result.payload = this._buildRouterPayload(opportunity);
            return gate1Result;
        }
        
        // --- Gate 2: Liquidity Source Check ---
        const gate2Result = this._gate2_liquiditySourceCheck(opportunity);
        if (gate2Result) {
            console.log(`   ✓ ${gate2Result.reason}`);
            gate2Result.payload = this._buildRouterPayload(opportunity);
            return gate2Result;
        }
        
        // --- Gate 3: Gas Simulation ---
        const gate3Result = await this._gate3_gasSimulation(opportunity);
        console.log(`   ✓ ${gate3Result.reason}`);
        if (gate3Result.gasHFT && gate3Result.gasRouter) {
            console.log(`   Gas comparison: HFT=${gate3Result.gasHFT}, Router=${gate3Result.gasRouter}`);
        }
        
        return gate3Result;
    }

    /**
     * Check if an exchange is V2 compatible
     * 
     * @param {string} exchangeName - Name of the exchange
     * @returns {boolean} - True if V2 compatible
     */
    isV2Compatible(exchangeName) {
        const v2Compatible = V2_COMPATIBLE_DEXES[this.chainId] || [];
        const name = exchangeName.toLowerCase();
        
        // Check whitelist
        const isWhitelisted = v2Compatible.some(dex => name.includes(dex));
        
        // Check blacklist
        const isBlacklisted = name.includes('v3') || 
                            name.includes('curve') || 
                            name.includes('balancer');
        
        return isWhitelisted && !isBlacklisted;
    }

    /**
     * Utility: Check if exchanges are V2 compatible
     * 
     * @param {Array<string>} exchanges - Array of exchange names
     * @returns {boolean} - True if all are V2 compatible
     */
    areAllExchangesV2Compatible(exchanges) {
        return exchanges.every(ex => this.isV2Compatible(ex));
    }
}

module.exports = { ArbitrageEngine, CONTRACT_HFT, CONTRACT_ROUTER };
