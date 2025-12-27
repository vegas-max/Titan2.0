/**
 * Standalone tests for Arbitrage Engine
 * Run with: node test/arbitrage_engine_standalone_test.js
 */

const { ethers } = require('ethers');
const { ArbitrageEngine } = require('../execution/arbitrage_engine');

// Test counter
let testsRun = 0;
let testsPassed = 0;
let testsFailed = 0;

// Simple assert function
function assert(condition, message) {
    testsRun++;
    if (condition) {
        testsPassed++;
        console.log(`  ✓ ${message}`);
    } else {
        testsFailed++;
        console.log(`  ✗ ${message}`);
    }
}

function assertEquals(actual, expected, message) {
    testsRun++;
    if (actual === expected) {
        testsPassed++;
        console.log(`  ✓ ${message}`);
    } else {
        testsFailed++;
        console.log(`  ✗ ${message}`);
        console.log(`    Expected: ${expected}, Got: ${actual}`);
    }
}

function assertNotNull(value, message) {
    testsRun++;
    if (value !== null && value !== undefined) {
        testsPassed++;
        console.log(`  ✓ ${message}`);
    } else {
        testsFailed++;
        console.log(`  ✗ ${message} (value was null/undefined)`);
    }
}

function assertNull(value, message) {
    testsRun++;
    if (value === null) {
        testsPassed++;
        console.log(`  ✓ ${message}`);
    } else {
        testsFailed++;
        console.log(`  ✗ ${message} (value was not null)`);
    }
}

// Mock provider for testing
const mockProvider = {
    estimateGas: async (tx) => {
        // Mock estimation - Router typically costs more than HFT
        if (tx.to === '0xAF00000000000000000000000000000000000000') {
            return BigInt(150000); // HFT uses less gas
        } else {
            return BigInt(200000); // Router uses more gas
        }
    }
};

async function runTests() {
    console.log('\n🧪 Running Arbitrage Engine Tests...\n');

    const CHAIN_ID_POLYGON = 137;
    const engine = new ArbitrageEngine(mockProvider, CHAIN_ID_POLYGON);

    // Test 1: Gate 1 - Multi-hop path should select Router
    console.log('📋 Gate 1: Topology Check Tests');
    {
        const opportunity = {
            path: ['0xToken1', '0xToken2', '0xToken3', '0xToken1'],
            exchanges: ['Quickswap', 'Sushiswap', 'Quickswap'],
            routers: ['0xRouter1', '0xRouter2', '0xRouter3'],
            amountIn: ethers.parseEther('1.0')
        };
        
        const result = engine._gate1_topologyCheck(opportunity);
        assertNotNull(result, 'Multi-hop path (length > 2) returns decision');
        assertEquals(result?.target, engine.routerContract, 'Multi-hop selects Router contract');
        assertEquals(result?.gate, 'GATE_1', 'Decision from Gate 1');
    }

    {
        const opportunity = {
            path: ['0xToken1', '0xToken2'],
            exchanges: ['Quickswap', 'Sushiswap'],
            routers: ['0xRouter1', '0xRouter2'],
            amountIn: ethers.parseEther('1.0')
        };
        
        const result = engine._gate1_topologyCheck(opportunity);
        assertNull(result, 'Simple swap (length = 2) proceeds to next gate');
    }

    // Test 2: Gate 2 - Liquidity Source Check
    console.log('\n📋 Gate 2: Liquidity Source Check Tests');
    {
        const opportunity = {
            path: ['0xToken1', '0xToken2'],
            exchanges: ['Uniswap V3'],
            routers: ['0xRouter1'],
            amountIn: ethers.parseEther('1.0')
        };
        
        const result = engine._gate2_liquiditySourceCheck(opportunity);
        assertNotNull(result, 'Uniswap V3 returns decision');
        assertEquals(result?.target, engine.routerContract, 'V3 selects Router contract');
        assertEquals(result?.gate, 'GATE_2', 'Decision from Gate 2');
    }

    {
        const opportunity = {
            path: ['0xToken1', '0xToken2'],
            exchanges: ['Curve'],
            routers: ['0xRouter1'],
            amountIn: ethers.parseEther('1.0')
        };
        
        const result = engine._gate2_liquiditySourceCheck(opportunity);
        assertNotNull(result, 'Curve returns decision');
        assertEquals(result?.target, engine.routerContract, 'Curve selects Router contract');
    }

    {
        const opportunity = {
            path: ['0xToken1', '0xToken2'],
            exchanges: ['Quickswap'],
            routers: ['0xRouter1'],
            amountIn: ethers.parseEther('1.0')
        };
        
        const result = engine._gate2_liquiditySourceCheck(opportunity);
        assertNull(result, 'V2 compatible (Quickswap) proceeds to next gate');
    }

    {
        const opportunity = {
            path: ['0xToken1', '0xToken2'],
            exchanges: ['Sushiswap'],
            routers: ['0xRouter1'],
            amountIn: ethers.parseEther('1.0')
        };
        
        const result = engine._gate2_liquiditySourceCheck(opportunity);
        assertNull(result, 'V2 compatible (Sushiswap) proceeds to next gate');
    }

    // Test 3: V2 Compatibility Helper
    console.log('\n📋 V2 Compatibility Helper Tests');
    {
        assert(engine.isV2Compatible('Quickswap'), 'Quickswap is V2 compatible');
        assert(engine.isV2Compatible('Sushiswap'), 'Sushiswap is V2 compatible');
        assert(!engine.isV2Compatible('Uniswap V3'), 'Uniswap V3 is not V2 compatible');
        assert(!engine.isV2Compatible('Curve'), 'Curve is not V2 compatible');
        assert(!engine.isV2Compatible('Balancer'), 'Balancer is not V2 compatible');
    }

    {
        assert(
            engine.areAllExchangesV2Compatible(['Quickswap', 'Sushiswap']),
            'Multiple V2 exchanges recognized'
        );
        assert(
            !engine.areAllExchangesV2Compatible(['Quickswap', 'Uniswap V3']),
            'Mixed V2/V3 rejected'
        );
    }

    // Test 4: Payload Building
    console.log('\n📋 Payload Building Tests');
    {
        const opportunity = {
            poolAddressA: '0x1111111111111111111111111111111111111111',
            poolAddressB: '0x2222222222222222222222222222222222222222',
            amountIn: ethers.parseEther('1.0')
        };
        
        const payload = engine._buildHFTPayload(opportunity);
        assert(payload.startsWith('0x'), 'HFT payload is hex string');
        assert(payload.length > 10, 'HFT payload has content');
        
        // Verify encoding
        const iface = new ethers.Interface([
            'function startArbitrage(address,address,uint256)'
        ]);
        const decoded = iface.decodeFunctionData('startArbitrage', payload);
        assertEquals(decoded[0], opportunity.poolAddressA, 'HFT payload poolA correct');
        assertEquals(decoded[1], opportunity.poolAddressB, 'HFT payload poolB correct');
        assertEquals(decoded[2].toString(), opportunity.amountIn.toString(), 'HFT payload amount correct');
    }

    {
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
        assert(payload.startsWith('0x'), 'Router payload is hex string');
        assert(payload.length > 10, 'Router payload has content');
        
        // Verify encoding
        const iface = new ethers.Interface([
            'function startArbitrage(address[],address[],uint256)'
        ]);
        const decoded = iface.decodeFunctionData('startArbitrage', payload);
        assertEquals(decoded[0].length, opportunity.path.length, 'Router payload path length correct');
        assertEquals(decoded[1].length, opportunity.routers.length, 'Router payload routers length correct');
        assertEquals(decoded[2].toString(), opportunity.amountIn.toString(), 'Router payload amount correct');
    }

    // Test 5: Gate 3 - Gas Simulation
    console.log('\n📋 Gate 3: Gas Simulation Tests');
    {
        const opportunity = {
            path: [
                '0x1111111111111111111111111111111111111111',
                '0x2222222222222222222222222222222222222222'
            ],
            exchanges: ['Quickswap'],
            routers: ['0x3333333333333333333333333333333333333333'],
            poolAddressA: '0x1111111111111111111111111111111111111111',
            poolAddressB: '0x2222222222222222222222222222222222222222',
            amountIn: ethers.parseEther('1.0')
        };
        
        const result = await engine._gate3_gasSimulation(opportunity);
        assertNotNull(result, 'Gate 3 returns decision');
        assertEquals(result.gate, 'GATE_3', 'Decision from Gate 3');
        assert(result.target !== undefined, 'Target contract selected');
        assert(result.payload !== undefined, 'Payload generated');
        
        // With our mock, HFT should be cheaper
        assertEquals(result.target, engine.hftContract, 'HFT selected (lower gas)');
        assertNotNull(result.gasHFT, 'HFT gas estimate provided');
        assertNotNull(result.gasRouter, 'Router gas estimate provided');
    }

    // Test 6: Full Integration Test
    console.log('\n📋 Full Integration Tests');
    {
        const opportunity = {
            path: [
                '0x1111111111111111111111111111111111111111',
                '0x2222222222222222222222222222222222222222',
                '0x3333333333333333333333333333333333333333',
                '0x1111111111111111111111111111111111111111'
            ],
            exchanges: ['Quickswap', 'Sushiswap', 'Quickswap'],
            routers: [
                '0x4444444444444444444444444444444444444444',
                '0x5555555555555555555555555555555555555555',
                '0x6666666666666666666666666666666666666666'
            ],
            amountIn: ethers.parseEther('1.0')
        };
        
        const result = await engine.selectExecutionEngine(opportunity);
        assertEquals(result.target, engine.routerContract, 'Multi-hop selects Router (Gate 1)');
        assertEquals(result.gate, 'GATE_1', 'Stopped at Gate 1');
        assertNotNull(result.payload, 'Payload generated');
    }

    {
        const opportunity = {
            path: [
                '0x1111111111111111111111111111111111111111',
                '0x2222222222222222222222222222222222222222'
            ],
            exchanges: ['Curve'],
            routers: ['0x3333333333333333333333333333333333333333'],
            amountIn: ethers.parseEther('1.0')
        };
        
        const result = await engine.selectExecutionEngine(opportunity);
        assertEquals(result.target, engine.routerContract, 'Non-V2 selects Router (Gate 2)');
        assertEquals(result.gate, 'GATE_2', 'Stopped at Gate 2');
        assertNotNull(result.payload, 'Payload generated');
    }

    {
        const opportunity = {
            path: [
                '0x1111111111111111111111111111111111111111',
                '0x2222222222222222222222222222222222222222'
            ],
            exchanges: ['Quickswap'],
            routers: ['0x3333333333333333333333333333333333333333'],
            poolAddressA: '0x1111111111111111111111111111111111111111',
            poolAddressB: '0x2222222222222222222222222222222222222222',
            amountIn: ethers.parseEther('1.0')
        };
        
        const result = await engine.selectExecutionEngine(opportunity);
        // Should reach Gate 3 and select HFT (lower gas in mock)
        assertEquals(result.gate, 'GATE_3', 'Reached Gate 3');
        assertEquals(result.target, engine.hftContract, 'HFT selected (Gate 3 gas comparison)');
        assertNotNull(result.payload, 'Payload generated');
    }

    // Print summary
    console.log('\n' + '='.repeat(60));
    console.log('📊 Test Summary');
    console.log('='.repeat(60));
    console.log(`Total tests run: ${testsRun}`);
    console.log(`Passed: ${testsPassed} ✓`);
    console.log(`Failed: ${testsFailed} ✗`);
    console.log('='.repeat(60));
    
    if (testsFailed === 0) {
        console.log('\n🎉 All tests passed!\n');
        process.exit(0);
    } else {
        console.log('\n❌ Some tests failed!\n');
        process.exit(1);
    }
}

// Run tests
runTests().catch(error => {
    console.error('Test execution error:', error);
    process.exit(1);
});
