/**
 * Tests for Arbitrage Engine
 * 
 * Tests the strict deterministic logic for arbitrage opportunity evaluation
 */

const { expect } = require('chai');
const { ethers } = require('hardhat');
const { ArbitrageEngine } = require('../execution/arbitrage_engine');

describe('ArbitrageEngine - Decision Logic Tests', function () {
    let engine;
    let provider;
    let mockHFTContract;
    let mockRouterContract;
    
    const CHAIN_ID_ETHEREUM = 1;
    const CHAIN_ID_POLYGON = 137;
    
    beforeEach(async function () {
        // Get provider from hardhat
        provider = ethers.provider;
        
        // Create engine instance
        engine = new ArbitrageEngine(provider, CHAIN_ID_POLYGON);
    });

    describe('Gate 1: Topology Check', function () {
        it('should select Router for path length > 2 (triangular arbitrage)', async function () {
            const opportunity = {
                path: ['0xToken1', '0xToken2', '0xToken3', '0xToken1'], // 4 tokens = multi-hop
                exchanges: ['Quickswap', 'Sushiswap', 'Quickswap'],
                routers: ['0xRouter1', '0xRouter2', '0xRouter3'],
                amountIn: ethers.parseEther('1.0')
            };
            
            const result = engine._gate1_topologyCheck(opportunity);
            
            expect(result).to.not.be.null;
            expect(result.target).to.equal(engine.routerContract);
            expect(result.reason).to.include('TOPOLOGY_CHECK');
            expect(result.gate).to.equal('GATE_1');
        });

        it('should return null for path length = 2 (simple swap)', async function () {
            const opportunity = {
                path: ['0xToken1', '0xToken2'], // 2 tokens = simple swap
                exchanges: ['Quickswap', 'Sushiswap'],
                routers: ['0xRouter1', '0xRouter2'],
                amountIn: ethers.parseEther('1.0')
            };
            
            const result = engine._gate1_topologyCheck(opportunity);
            
            expect(result).to.be.null;
        });

        it('should select Router for 3-token path (A→B→A)', async function () {
            const opportunity = {
                path: ['0xWETH', '0xUSDC', '0xWETH'], // 3 tokens
                exchanges: ['Quickswap', 'Sushiswap'],
                routers: ['0xRouter1', '0xRouter2'],
                amountIn: ethers.parseEther('1.0')
            };
            
            const result = engine._gate1_topologyCheck(opportunity);
            
            expect(result).to.not.be.null;
            expect(result.target).to.equal(engine.routerContract);
        });
    });

    describe('Gate 2: Liquidity Source Check', function () {
        it('should select Router for Uniswap V3', async function () {
            const opportunity = {
                path: ['0xToken1', '0xToken2'],
                exchanges: ['Uniswap V3'], // Non-V2
                routers: ['0xRouter1'],
                amountIn: ethers.parseEther('1.0')
            };
            
            const result = engine._gate2_liquiditySourceCheck(opportunity);
            
            expect(result).to.not.be.null;
            expect(result.target).to.equal(engine.routerContract);
            expect(result.reason).to.include('LIQUIDITY_CHECK');
            expect(result.gate).to.equal('GATE_2');
        });

        it('should select Router for Curve', async function () {
            const opportunity = {
                path: ['0xToken1', '0xToken2'],
                exchanges: ['Curve'], // Non-V2
                routers: ['0xRouter1'],
                amountIn: ethers.parseEther('1.0')
            };
            
            const result = engine._gate2_liquiditySourceCheck(opportunity);
            
            expect(result).to.not.be.null;
            expect(result.target).to.equal(engine.routerContract);
        });

        it('should select Router for Balancer', async function () {
            const opportunity = {
                path: ['0xToken1', '0xToken2'],
                exchanges: ['Balancer'], // Non-V2
                routers: ['0xRouter1'],
                amountIn: ethers.parseEther('1.0')
            };
            
            const result = engine._gate2_liquiditySourceCheck(opportunity);
            
            expect(result).to.not.be.null;
            expect(result.target).to.equal(engine.routerContract);
        });

        it('should return null for V2 compatible exchanges (Quickswap)', async function () {
            const opportunity = {
                path: ['0xToken1', '0xToken2'],
                exchanges: ['Quickswap'], // V2 compatible
                routers: ['0xRouter1'],
                amountIn: ethers.parseEther('1.0')
            };
            
            const result = engine._gate2_liquiditySourceCheck(opportunity);
            
            expect(result).to.be.null;
        });

        it('should return null for V2 compatible exchanges (Sushiswap)', async function () {
            const opportunity = {
                path: ['0xToken1', '0xToken2'],
                exchanges: ['Sushiswap'], // V2 compatible
                routers: ['0xRouter1'],
                amountIn: ethers.parseEther('1.0')
            };
            
            const result = engine._gate2_liquiditySourceCheck(opportunity);
            
            expect(result).to.be.null;
        });

        it('should return null for multiple V2 compatible exchanges', async function () {
            const opportunity = {
                path: ['0xToken1', '0xToken2'],
                exchanges: ['Quickswap', 'Sushiswap'], // Both V2
                routers: ['0xRouter1', '0xRouter2'],
                amountIn: ethers.parseEther('1.0')
            };
            
            const result = engine._gate2_liquiditySourceCheck(opportunity);
            
            expect(result).to.be.null;
        });
    });

    describe('Payload Building', function () {
        it('should build HFT payload correctly', function () {
            const opportunity = {
                poolAddressA: '0x1111111111111111111111111111111111111111',
                poolAddressB: '0x2222222222222222222222222222222222222222',
                amountIn: ethers.parseEther('1.0')
            };
            
            const payload = engine._buildHFTPayload(opportunity);
            
            // Check that payload is a hex string
            expect(payload).to.match(/^0x[0-9a-f]+$/i);
            
            // Decode and verify
            const iface = new ethers.Interface([
                'function startArbitrage(address,address,uint256)'
            ]);
            const decoded = iface.decodeFunctionData('startArbitrage', payload);
            
            expect(decoded[0]).to.equal(opportunity.poolAddressA);
            expect(decoded[1]).to.equal(opportunity.poolAddressB);
            expect(decoded[2]).to.equal(opportunity.amountIn);
        });

        it('should build Router payload correctly', function () {
            const opportunity = {
                path: [
                    '0x1111111111111111111111111111111111111111',
                    '0x2222222222222222222222222222222222222222',
                    '0x1111111111111111111111111111111111111111'
                ],
                routers: [
                    '0x3333333333333333333333333333333333333333',
                    '0x4444444444444444444444444444444444444444'
                ],
                amountIn: ethers.parseEther('1.0')
            };
            
            const payload = engine._buildRouterPayload(opportunity);
            
            // Check that payload is a hex string
            expect(payload).to.match(/^0x[0-9a-f]+$/i);
            
            // Decode and verify
            const iface = new ethers.Interface([
                'function startArbitrage(address[],address[],uint256)'
            ]);
            const decoded = iface.decodeFunctionData('startArbitrage', payload);
            
            expect(decoded[0]).to.deep.equal(opportunity.path);
            expect(decoded[1]).to.deep.equal(opportunity.routers);
            expect(decoded[2]).to.equal(opportunity.amountIn);
        });
    });

    describe('V2 Compatibility Check', function () {
        it('should recognize Quickswap as V2 compatible on Polygon', function () {
            const engine = new ArbitrageEngine(provider, CHAIN_ID_POLYGON);
            expect(engine.isV2Compatible('Quickswap')).to.be.true;
        });

        it('should recognize Sushiswap as V2 compatible', function () {
            const engine = new ArbitrageEngine(provider, CHAIN_ID_POLYGON);
            expect(engine.isV2Compatible('Sushiswap')).to.be.true;
        });

        it('should reject Uniswap V3 as non-V2', function () {
            const engine = new ArbitrageEngine(provider, CHAIN_ID_POLYGON);
            expect(engine.isV2Compatible('Uniswap V3')).to.be.false;
        });

        it('should reject Curve as non-V2', function () {
            const engine = new ArbitrageEngine(provider, CHAIN_ID_POLYGON);
            expect(engine.isV2Compatible('Curve')).to.be.false;
        });

        it('should reject Balancer as non-V2', function () {
            const engine = new ArbitrageEngine(provider, CHAIN_ID_POLYGON);
            expect(engine.isV2Compatible('Balancer')).to.be.false;
        });

        it('should check multiple exchanges correctly', function () {
            const engine = new ArbitrageEngine(provider, CHAIN_ID_POLYGON);
            expect(engine.areAllExchangesV2Compatible(['Quickswap', 'Sushiswap'])).to.be.true;
            expect(engine.areAllExchangesV2Compatible(['Quickswap', 'Uniswap V3'])).to.be.false;
            expect(engine.areAllExchangesV2Compatible(['Curve', 'Balancer'])).to.be.false;
        });
    });

    describe('Full Integration: selectExecutionEngine', function () {
        it('should reject invalid opportunity structure', async function () {
            try {
                await engine.selectExecutionEngine({});
                expect.fail('Should have thrown error');
            } catch (error) {
                expect(error.message).to.include('Invalid opportunity structure');
            }
        });

        it('should handle Gate 1 decision (multi-hop)', async function () {
            const opportunity = {
                path: ['0xToken1', '0xToken2', '0xToken3', '0xToken1'],
                exchanges: ['Quickswap', 'Sushiswap', 'Quickswap'],
                routers: ['0xRouter1', '0xRouter2', '0xRouter3'],
                amountIn: ethers.parseEther('1.0')
            };
            
            const result = await engine.selectExecutionEngine(opportunity);
            
            expect(result.target).to.equal(engine.routerContract);
            expect(result.gate).to.equal('GATE_1');
            expect(result.payload).to.exist;
        });

        it('should handle Gate 2 decision (non-V2 exchange)', async function () {
            const opportunity = {
                path: ['0xToken1', '0xToken2'],
                exchanges: ['Curve'],
                routers: ['0xRouter1'],
                amountIn: ethers.parseEther('1.0')
            };
            
            const result = await engine.selectExecutionEngine(opportunity);
            
            expect(result.target).to.equal(engine.routerContract);
            expect(result.gate).to.equal('GATE_2');
            expect(result.payload).to.exist;
        });
    });

    describe('Chain-Specific V2 DEX Lists', function () {
        it('should have V2 DEXes for Ethereum', function () {
            const engineEth = new ArbitrageEngine(provider, CHAIN_ID_ETHEREUM);
            expect(engineEth.isV2Compatible('Uniswap')).to.be.true;
            expect(engineEth.isV2Compatible('Sushiswap')).to.be.true;
        });

        it('should have V2 DEXes for Polygon', function () {
            const enginePoly = new ArbitrageEngine(provider, CHAIN_ID_POLYGON);
            expect(enginePoly.isV2Compatible('Quickswap')).to.be.true;
            expect(enginePoly.isV2Compatible('Sushiswap')).to.be.true;
        });
    });
});
