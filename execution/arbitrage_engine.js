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

// Known Uniswap V2 forks per chainId
// This structure is intentionally chain-indexed so that isV2Compatible()
// and related methods can safely access V2_COMPATIBLE_DEXES[this.chainId].
const V2_COMPATIBLE_DEXES = {
    // Ethereum Mainnet
    1: [
        'UNISWAP_V2',
        'SUSHISWAP'
    ],
    // Binance Smart Chain
    56: [
        'PANCAKESWAP'
    ],
    // Polygon
    137: [
        'QUICKSWAP'
    ],
    // Avalanche
    43114: [
        'TRADERJOE'
    ]
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
     * If route length > 2, it's a multi-hop (triangular) arbitrage
     * HFT only supports direct pair swaps (route length = 2)
     * 
     * @param {Object} opportunity - Arbitrage opportunity data
     * @returns {Object|null} - Decision object or null to continue
     */
    _gate1_topologyCheck(opportunity) {
        const routeLength = opportunity.route ? opportunity.route.length : opportunity.path_length;
        
        if (routeLength > 2) {
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
        // Extract exchanges from route or use exchanges array
        let exchanges = [];
        if (opportunity.route) {
            exchanges = opportunity.route.map(r => r.exchange);
        } else if (opportunity.exchanges) {
            exchanges = opportunity.exchanges;
        }
        
        // Check if all exchanges are V2 compatible
        for (const exchange of exchanges) {
            // Use exact matching with uppercase exchange names
            const exchangeUpper = exchange.toUpperCase();
            const isV2 = V2_COMPATIBLE_DEXES.includes(exchangeUpper);
            
            if (!isV2) {
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
        
        // Extract pool addresses from route structure or fallback to direct properties
        let poolA, poolB;

        const hasRoutePools =
            Array.isArray(opportunity.route) &&
            opportunity.route.length >= 2 &&
            opportunity.route[0] &&
            opportunity.route[1] &&
            opportunity.route[0].pool_address &&
            opportunity.route[1].pool_address;

        if (hasRoutePools) {
            poolA = opportunity.route[0].pool_address;
            poolB = opportunity.route[1].pool_address;
        } else {
            poolA = opportunity.poolAddressA || opportunity.poolAddress_A || opportunity.pool_address_1;
            poolB = opportunity.poolAddressB || opportunity.poolAddress_B || opportunity.pool_address_2;
        }

        if (!poolA || !poolB) {
            throw new Error('HFT payload requires both poolA and poolB addresses');
        }
        
        const amount = opportunity.amountIn || opportunity.amount || opportunity.amount_in_wei;

        if (!amount) {
            throw new Error('HFT_PAYLOAD: Missing amount for arbitrage opportunity');
        }
        
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
        
        // Extract token path and routers from route structure or use direct arrays
        let path, routers;
        if (opportunity.route && opportunity.route.length > 0) {
            // Build path from route tokens
            path = opportunity.route.map(r => r.token);
            // Build routers array from provided router addresses
            // Note: In real implementation, you'd map exchanges to their router addresses
            if (opportunity.routers && opportunity.routers.length > 0) {
                routers = opportunity.routers;
            } else {
                throw new Error('Router execution requires opportunity.routers (router contract addresses); pool_address values must not be used as routers.');
            }
        } else {
            path = opportunity.path;
            routers = opportunity.routers;
        }

        // Validate path and routers arrays before encoding
        if (!Array.isArray(path) || !Array.isArray(routers) || path.length < 2) {
            throw new Error('Router payload requires valid path and routers arrays with at least 2 tokens in path');
        }
        // For path-based routing, routers are typically one less than path length
        if (routers.length !== path.length - 1) {
            throw new Error('Router payload requires routers.length to equal path.length - 1');
        }
        
        const amount = opportunity.amountIn || opportunity.amount || opportunity.amount_in_wei;
        
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
        if (!opportunity) {
            throw new Error('Invalid opportunity structure: opportunity is null or undefined');
        }
        
        // Support both route-based and legacy path-based structures
        if (!opportunity.route && (!opportunity.path || !opportunity.exchanges)) {
            throw new Error('Invalid opportunity structure: missing route, or legacy path/exchanges');
        }
        
        console.log('\n🔍 ARBITRAGE ENGINE: Evaluating opportunity...');
        if (opportunity.route) {
            const formattedRoute = Array.isArray(opportunity.route)
                ? opportunity.route.map((r, idx) => {
                    if (!r || (typeof r !== 'object')) {
                        return `entry#${idx}`;
                    }
                    const token = r.token !== undefined && r.token !== null ? r.token : 'unknown-token';
                    const exchange = r.exchange !== undefined && r.exchange !== null ? r.exchange : 'unknown-exchange';
                    return `${token} via ${exchange}`;
                }).join(' → ')
                : String(opportunity.route);
            console.log(`   Route: ${formattedRoute}`);
        } else {
            console.log(`   Path: ${opportunity.path.join(' → ')}`);
            console.log(`   Exchanges: ${(opportunity.exchanges || []).join(', ')}`);
        }
        console.log(`   Amount: ${opportunity.amountIn || opportunity.amount || opportunity.amount_in_wei}`);
        
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
