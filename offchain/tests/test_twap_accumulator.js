/**
 * Tests for TWAP Accumulator Module
 * 
 * Tests time-weighted average price calculation and multi-pool tracking
 */

const { TWAPAccumulator, MultiPoolTWAP } = require('../offchain/core/twapAccumulator');

describe('TWAP Accumulator', () => {
  describe('TWAPAccumulator Basic Operations', () => {
    test('Should initialize with default config', () => {
      const twap = new TWAPAccumulator();
      expect(twap.sampleCount()).toBe(0);
      expect(twap.value()).toBe(0);
      expect(twap.isReady()).toBe(false);
    });

    test('Should initialize with custom config', () => {
      const twap = new TWAPAccumulator({
        windowMs: 60000,
        minSamples: 5,
        maxSamples: 200
      });
      expect(twap.sampleCount()).toBe(0);
    });

    test('Should accept and store price samples', () => {
      const twap = new TWAPAccumulator();
      twap.push(100);
      twap.push(105);
      twap.push(102);
      
      expect(twap.sampleCount()).toBe(3);
      expect(twap.isReady()).toBe(true);
    });

    test('Should reject invalid prices', () => {
      const twap = new TWAPAccumulator();
      twap.push(NaN);
      twap.push(Infinity);
      twap.push(-100);
      twap.push(0);
      
      expect(twap.sampleCount()).toBe(0);
    });

    test('Should return latest price with single sample', () => {
      const twap = new TWAPAccumulator();
      twap.push(100);
      
      expect(twap.value()).toBe(100);
      expect(twap.latest()).toBe(100);
    });
  });

  describe('TWAP Calculation', () => {
    test('Should calculate time-weighted average', async () => {
      const twap = new TWAPAccumulator();
      
      twap.push(100);
      await new Promise(resolve => setTimeout(resolve, 100));
      twap.push(110);
      await new Promise(resolve => setTimeout(resolve, 100));
      twap.push(105);
      
      const avg = twap.value();
      // TWAP should be weighted by time
      expect(avg).toBeGreaterThan(100);
      expect(avg).toBeLessThan(110);
    });

    test('Should prune old samples outside window', async () => {
      const twap = new TWAPAccumulator({ windowMs: 100 });
      
      twap.push(100);
      await new Promise(resolve => setTimeout(resolve, 150));
      twap.push(110);
      
      // Old sample should be pruned
      expect(twap.sampleCount()).toBe(1);
    });

    test('Should enforce max samples limit', () => {
      const twap = new TWAPAccumulator({ maxSamples: 5 });
      
      for (let i = 0; i < 10; i++) {
        twap.push(100 + i);
      }
      
      expect(twap.sampleCount()).toBe(5);
      // Should keep most recent samples
      expect(twap.latest()).toBe(109);
    });
  });

  describe('Latest and Volatility', () => {
    test('Should return latest spot price', () => {
      const twap = new TWAPAccumulator();
      twap.push(100);
      twap.push(105);
      twap.push(102);
      
      expect(twap.latest()).toBe(102);
    });

    test('Should calculate volatility', () => {
      const twap = new TWAPAccumulator();
      twap.push(100);
      twap.push(100);
      twap.push(100);
      
      // Zero volatility for constant prices
      expect(twap.volatility()).toBe(0);
    });

    test('Should calculate non-zero volatility for varying prices', () => {
      const twap = new TWAPAccumulator();
      twap.push(90);
      twap.push(100);
      twap.push(110);
      
      expect(twap.volatility()).toBeGreaterThan(0);
    });
  });

  describe('Deviation and Bounds Checking', () => {
    test('Should calculate deviation from TWAP', () => {
      const twap = new TWAPAccumulator();
      twap.push(100);
      twap.push(100);
      
      const dev = twap.deviation(105);
      expect(dev).toBeCloseTo(0.05, 2); // 5% deviation
    });

    test('Should check if price is within bounds', () => {
      const twap = new TWAPAccumulator();
      twap.push(100);
      twap.push(100);
      
      expect(twap.isWithinBounds(103, 0.05)).toBe(true); // 3% < 5%
      expect(twap.isWithinBounds(107, 0.05)).toBe(false); // 7% > 5%
    });

    test('Should accept any price when not ready', () => {
      const twap = new TWAPAccumulator({ minSamples: 5 });
      twap.push(100);
      
      // Not enough samples, should accept any price
      expect(twap.isWithinBounds(200, 0.05)).toBe(true);
    });
  });

  describe('Clear and Age', () => {
    test('Should clear all samples', () => {
      const twap = new TWAPAccumulator();
      twap.push(100);
      twap.push(105);
      
      twap.clear();
      expect(twap.sampleCount()).toBe(0);
      expect(twap.value()).toBe(0);
    });

    test('Should track oldest sample age', async () => {
      const twap = new TWAPAccumulator();
      twap.push(100);
      
      await new Promise(resolve => setTimeout(resolve, 100));
      
      const age = twap.oldestSampleAge();
      expect(age).toBeGreaterThanOrEqual(100);
    });
  });
});

describe('Multi-Pool TWAP Manager', () => {
  const TOKEN_A = '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270'; // WMATIC
  const TOKEN_B = '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'; // USDC
  const TOKEN_C = '0xc2132D05D31c914a87C6611C10748AEb04B58e8F'; // USDT

  describe('Pool Management', () => {
    test('Should create and retrieve pools', () => {
      const manager = new MultiPoolTWAP();
      
      const pool = manager.getPool(TOKEN_A, TOKEN_B);
      expect(pool).toBeInstanceOf(TWAPAccumulator);
    });

    test('Should normalize pool keys (order-independent)', () => {
      const manager = new MultiPoolTWAP();
      
      const pool1 = manager.getPool(TOKEN_A, TOKEN_B);
      const pool2 = manager.getPool(TOKEN_B, TOKEN_A);
      
      // Should return the same pool instance
      expect(pool1).toBe(pool2);
    });

    test('Should track multiple pools independently', () => {
      const manager = new MultiPoolTWAP();
      
      manager.push(TOKEN_A, TOKEN_B, 100);
      manager.push(TOKEN_A, TOKEN_C, 200);
      
      expect(manager.value(TOKEN_A, TOKEN_B)).toBe(100);
      expect(manager.value(TOKEN_A, TOKEN_C)).toBe(200);
    });

    test('Should count tracked pools', () => {
      const manager = new MultiPoolTWAP();
      
      manager.push(TOKEN_A, TOKEN_B, 100);
      manager.push(TOKEN_A, TOKEN_C, 200);
      manager.push(TOKEN_B, TOKEN_C, 150);
      
      expect(manager.poolCount()).toBe(3);
    });
  });

  describe('Price Operations', () => {
    test('Should push and retrieve TWAP values', () => {
      const manager = new MultiPoolTWAP();
      
      manager.push(TOKEN_A, TOKEN_B, 100);
      manager.push(TOKEN_A, TOKEN_B, 105);
      
      const value = manager.value(TOKEN_A, TOKEN_B);
      expect(value).toBeGreaterThan(0);
    });

    test('Should check if pool is ready', () => {
      const manager = new MultiPoolTWAP({ minSamples: 3 });
      
      manager.push(TOKEN_A, TOKEN_B, 100);
      expect(manager.isReady(TOKEN_A, TOKEN_B)).toBe(false);
      
      manager.push(TOKEN_A, TOKEN_B, 105);
      expect(manager.isReady(TOKEN_A, TOKEN_B)).toBe(false);
      
      manager.push(TOKEN_A, TOKEN_B, 102);
      expect(manager.isReady(TOKEN_A, TOKEN_B)).toBe(true);
    });
  });

  describe('Clear Operations', () => {
    test('Should clear all pools', () => {
      const manager = new MultiPoolTWAP();
      
      manager.push(TOKEN_A, TOKEN_B, 100);
      manager.push(TOKEN_A, TOKEN_C, 200);
      
      manager.clearAll();
      expect(manager.poolCount()).toBe(0);
    });
  });

  describe('Case Sensitivity', () => {
    test('Should handle mixed-case addresses', () => {
      const manager = new MultiPoolTWAP();
      
      manager.push(TOKEN_A.toLowerCase(), TOKEN_B.toUpperCase(), 100);
      manager.push(TOKEN_A.toUpperCase(), TOKEN_B.toLowerCase(), 105);
      
      // Should be same pool regardless of case
      expect(manager.poolCount()).toBe(1);
    });
  });
});

console.log('✅ TWAP Accumulator tests completed');
