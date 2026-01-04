/**
 * Token Universe - Canonical token definitions shared across JS + Python
 * 
 * Provides a single source of truth for token addresses and trading pairs
 * across all supported chains. This enables clean expansion of trading
 * strategies without breaking existing functionality.
 * 
 * NOTE: This module now uses the centralized token_config for comprehensive
 * token management with support for multiple token types (CANONICAL, BRIDGED, WRAPPED)
 */

const tokenConfig = require('./token_config');

// Build token lookup by symbol for backward compatibility
function buildTokenLookup() {
  const TOKENS = {};
  
  for (const chainId of tokenConfig.getSupportedChains()) {
    const tokens = tokenConfig.getChainTokens(chainId);
    TOKENS[chainId] = {};
    
    for (const token of tokens) {
      const symbol = tokenConfig.getTokenSymbol(token.id);
      if (symbol) {
        // Store primary address (prefer CANONICAL over BRIDGED)
        if (!TOKENS[chainId][symbol] || token.type === tokenConfig.TokenType.CANONICAL) {
          TOKENS[chainId][symbol] = token.address;
        }
      }
    }
    
    // Add special aliases for native tokens
    if (chainId === 137) {
      TOKENS[chainId].WMATIC = TOKENS[chainId].WNATIVE || "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270";
    }
  }
  
  // Add legacy symbols for chains not in token_config yet
  // Polygon (137) - enhanced with all available tokens
  if (!TOKENS[137]) TOKENS[137] = {};
  TOKENS[137] = {
    ...TOKENS[137],
    LINK: TOKENS[137].LINK || "0x53E0bca35eC356BD5ddDFebbD1Fc0fD03FaBad39",
    UNI: TOKENS[137].UNI || "0xb33EaAd8d922B1083446DC23f610c2567fB5180f"
  };
  
  // Arbitrum (42161) - enhanced with all available tokens
  if (!TOKENS[42161]) TOKENS[42161] = {};
  TOKENS[42161] = {
    ...TOKENS[42161],
    LINK: TOKENS[42161].LINK || "0xf97f4df75117a78c1A5a0DBb814Af92458539FB4",
    UNI: TOKENS[42161].UNI || "0xFa7F8980b0f1E64A2062791cc3b0871572f1F7f0"
  };
  
  // Ethereum (1) - Already complete from token_config
  
  return TOKENS;
}

const TOKENS = buildTokenLookup();

// Standard trading pairs for arbitrage discovery
const PAIRS = [
  // Major pairs with WETH
  ["WETH", "USDC"],
  ["WETH", "USDT"],
  ["WETH", "DAI"],
  
  // Native token pairs (WMATIC on Polygon)
  ["WMATIC", "USDC"],
  ["WMATIC", "USDT"],
  ["WMATIC", "WETH"],
  
  // Stablecoin triangles (Curve-optimized)
  ["USDC", "USDT"],
  ["USDC", "DAI"],
  ["USDT", "DAI"],
  
  // WBTC pairs
  ["WBTC", "USDC"],
  ["WBTC", "WETH"],
  
  // Blue-chip DeFi tokens
  ["LINK", "USDC"],
  ["LINK", "WETH"],
  ["AAVE", "USDC"],
  ["AAVE", "WETH"],
  ["UNI", "USDC"],
  ["UNI", "WETH"]
];

/**
 * Get token address for a given chain and symbol
 * @param {number} chainId - EIP-155 Chain ID
 * @param {string} symbol - Token symbol (e.g., "WETH", "USDC")
 * @returns {string|null} Token address or null if not found
 */
function getTokenAddress(chainId, symbol) {
  const chainTokens = TOKENS[chainId];
  if (!chainTokens) return null;
  
  return chainTokens[symbol] || null;
}

/**
 * Get all available pairs for a specific chain
 * Filters out pairs where tokens don't exist on the chain
 * @param {number} chainId - EIP-155 Chain ID
 * @returns {Array<[string, string]>} Array of [tokenA_address, tokenB_address] pairs
 */
function getAvailablePairs(chainId) {
  const chainTokens = TOKENS[chainId];
  if (!chainTokens) return [];
  
  const availablePairs = [];
  
  for (const [symbolA, symbolB] of PAIRS) {
    const addressA = getTokenAddress(chainId, symbolA);
    const addressB = getTokenAddress(chainId, symbolB);
    
    // Only include pair if both tokens exist on this chain
    if (addressA && addressB) {
      availablePairs.push([addressA, addressB]);
    }
  }
  
  return availablePairs;
}

/**
 * Get token symbol from address
 * @param {number} chainId - EIP-155 Chain ID
 * @param {string} address - Token contract address
 * @returns {string|null} Token symbol or null if not found
 */
function getTokenSymbol(chainId, address) {
  const chainTokens = TOKENS[chainId];
  if (!chainTokens) return null;
  
  const normalizedAddress = address.toLowerCase();
  
  for (const [symbol, addr] of Object.entries(chainTokens)) {
    if (addr.toLowerCase() === normalizedAddress) {
      return symbol;
    }
  }
  
  return null;
}

/**
 * Check if a token pair is supported
 * @param {number} chainId - EIP-155 Chain ID
 * @param {string} tokenA - Token A address
 * @param {string} tokenB - Token B address
 * @returns {boolean} true if pair is supported, false otherwise
 */
function isPairSupported(chainId, tokenA, tokenB) {
  const availablePairs = getAvailablePairs(chainId);
  const normalizedA = tokenA.toLowerCase();
  const normalizedB = tokenB.toLowerCase();
  
  return availablePairs.some(([a, b]) => 
    (a.toLowerCase() === normalizedA && b.toLowerCase() === normalizedB) ||
    (a.toLowerCase() === normalizedB && b.toLowerCase() === normalizedA)
  );
}

/**
 * Get all tokens for a specific chain
 * @param {number} chainId - EIP-155 Chain ID
 * @returns {Object} Object mapping symbol to address
 */
function getChainTokens(chainId) {
  const chainTokens = TOKENS[chainId];
  if (!chainTokens) return {};
  
  return { ...chainTokens };
}

module.exports = {
  TOKENS,
  PAIRS,
  getTokenAddress,
  getAvailablePairs,
  getTokenSymbol,
  isPairSupported,
  getChainTokens,
  // Export token_config utilities for advanced usage
  tokenConfig
};
