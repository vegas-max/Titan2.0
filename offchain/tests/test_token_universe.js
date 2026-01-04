/**
 * Tests for Token Universe Module
 * 
 * Tests canonical token definitions and trading pair management
 */

const { 
  TOKENS, 
  PAIRS, 
  getTokenAddress, 
  getAvailablePairs, 
  getTokenSymbol,
  isPairSupported,
  getChainTokens 
} = require('../offchain/core/tokenUniverse');

// Mock config if needed
const CFG = {
  chainId: 137,
  http: process.env.RPC_POLYGON || 'https://polygon-rpc.com'
};

describe('Token Universe Module', () => {
  describe('Token Definitions', () => {
    test('Should have tokens for Polygon (137)', () => {
      expect(TOKENS[137]).toBeDefined();
      expect(TOKENS[137].WMATIC).toBe('0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270');
      expect(TOKENS[137].USDC).toBe('0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174');
      expect(TOKENS[137].WETH).toBe('0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619');
    });

    test('Should have tokens for Ethereum (1)', () => {
      expect(TOKENS[1]).toBeDefined();
      expect(TOKENS[1].WETH).toBe('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2');
      expect(TOKENS[1].USDC).toBe('0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48');
    });

    test('Should have tokens for Arbitrum (42161)', () => {
      expect(TOKENS[42161]).toBeDefined();
      expect(TOKENS[42161].WETH).toBe('0x82aF49447D8a07e3bd95BD0d56f35241523fBab1');
      expect(TOKENS[42161].USDC).toBe('0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8');
    });
  });

  describe('Trading Pairs', () => {
    test('Should have major WETH pairs', () => {
      expect(PAIRS).toContainEqual(['WETH', 'USDC']);
      expect(PAIRS).toContainEqual(['WETH', 'USDT']);
      expect(PAIRS).toContainEqual(['WETH', 'DAI']);
    });

    test('Should have stablecoin pairs', () => {
      expect(PAIRS).toContainEqual(['USDC', 'USDT']);
      expect(PAIRS).toContainEqual(['USDC', 'DAI']);
      expect(PAIRS).toContainEqual(['USDT', 'DAI']);
    });

    test('Should have WMATIC pairs for Polygon', () => {
      expect(PAIRS).toContainEqual(['WMATIC', 'USDC']);
      expect(PAIRS).toContainEqual(['WMATIC', 'WETH']);
    });

    test('Should have DeFi token pairs', () => {
      expect(PAIRS).toContainEqual(['LINK', 'USDC']);
      expect(PAIRS).toContainEqual(['AAVE', 'WETH']);
      expect(PAIRS).toContainEqual(['UNI', 'USDC']);
    });
  });

  describe('getTokenAddress', () => {
    test('Should return token address for valid chain and symbol', () => {
      const wmaticAddress = getTokenAddress(137, 'WMATIC');
      expect(wmaticAddress).toBe('0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270');
    });

    test('Should return null for invalid chain', () => {
      const address = getTokenAddress(999, 'WMATIC');
      expect(address).toBeNull();
    });

    test('Should return null for invalid symbol', () => {
      const address = getTokenAddress(137, 'INVALID');
      expect(address).toBeNull();
    });

    test('Should work for all supported chains', () => {
      expect(getTokenAddress(1, 'WETH')).toBeTruthy();
      expect(getTokenAddress(137, 'WMATIC')).toBeTruthy();
      expect(getTokenAddress(42161, 'WETH')).toBeTruthy();
    });
  });

  describe('getAvailablePairs', () => {
    test('Should return available pairs for Polygon', () => {
      const pairs = getAvailablePairs(137);
      expect(pairs.length).toBeGreaterThan(0);
      
      // Should include WMATIC pairs (specific to Polygon)
      const wmaticUsdcPair = pairs.find(([a, b]) => 
        (a.toLowerCase() === TOKENS[137].WMATIC.toLowerCase() && 
         b.toLowerCase() === TOKENS[137].USDC.toLowerCase()) ||
        (b.toLowerCase() === TOKENS[137].WMATIC.toLowerCase() && 
         a.toLowerCase() === TOKENS[137].USDC.toLowerCase())
      );
      expect(wmaticUsdcPair).toBeDefined();
    });

    test('Should return available pairs for Ethereum', () => {
      const pairs = getAvailablePairs(1);
      expect(pairs.length).toBeGreaterThan(0);
      
      // Should NOT include WMATIC pairs (not on Ethereum)
      const wmaticPair = pairs.find(([a, b]) => 
        a.toLowerCase().includes('wmatic') || b.toLowerCase().includes('wmatic')
      );
      expect(wmaticPair).toBeUndefined();
    });

    test('Should return empty array for unsupported chain', () => {
      const pairs = getAvailablePairs(999);
      expect(pairs).toEqual([]);
    });

    test('Should return unique pairs', () => {
      const pairs = getAvailablePairs(137);
      const pairSet = new Set(pairs.map(p => p.join('-')));
      expect(pairSet.size).toBe(pairs.length);
    });
  });

  describe('getTokenSymbol', () => {
    test('Should return symbol for valid address', () => {
      const symbol = getTokenSymbol(137, '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270');
      expect(symbol).toBe('WMATIC');
    });

    test('Should be case-insensitive', () => {
      const symbol = getTokenSymbol(137, '0x0D500B1D8E8EF31E21C99D1DB9A6444D3ADF1270');
      expect(symbol).toBe('WMATIC');
    });

    test('Should return null for invalid address', () => {
      const symbol = getTokenSymbol(137, '0x0000000000000000000000000000000000000000');
      expect(symbol).toBeNull();
    });

    test('Should return null for invalid chain', () => {
      const symbol = getTokenSymbol(999, TOKENS[137].WMATIC);
      expect(symbol).toBeNull();
    });
  });

  describe('isPairSupported', () => {
    test('Should return true for supported pairs', () => {
      const supported = isPairSupported(
        137,
        TOKENS[137].WMATIC,
        TOKENS[137].USDC
      );
      expect(supported).toBe(true);
    });

    test('Should return true regardless of token order', () => {
      const supported1 = isPairSupported(137, TOKENS[137].WMATIC, TOKENS[137].USDC);
      const supported2 = isPairSupported(137, TOKENS[137].USDC, TOKENS[137].WMATIC);
      expect(supported1).toBe(true);
      expect(supported2).toBe(true);
    });

    test('Should return false for unsupported pairs', () => {
      const supported = isPairSupported(
        137,
        TOKENS[137].WMATIC,
        '0x0000000000000000000000000000000000000000'
      );
      expect(supported).toBe(false);
    });

    test('Should be case-insensitive', () => {
      const supported = isPairSupported(
        137,
        TOKENS[137].WMATIC.toUpperCase(),
        TOKENS[137].USDC.toLowerCase()
      );
      expect(supported).toBe(true);
    });
  });

  describe('getChainTokens', () => {
    test('Should return all tokens for a chain', () => {
      const tokens = getChainTokens(137);
      expect(Object.keys(tokens).length).toBeGreaterThan(0);
      expect(tokens.WMATIC).toBe(TOKENS[137].WMATIC);
      expect(tokens.USDC).toBe(TOKENS[137].USDC);
    });

    test('Should return empty object for invalid chain', () => {
      const tokens = getChainTokens(999);
      expect(tokens).toEqual({});
    });

    test('Should return a copy (not mutate original)', () => {
      const tokens = getChainTokens(137);
      tokens.TEST = '0x0000000000000000000000000000000000000000';
      
      const tokens2 = getChainTokens(137);
      expect(tokens2.TEST).toBeUndefined();
    });
  });
});

console.log('✅ Token Universe tests completed');
