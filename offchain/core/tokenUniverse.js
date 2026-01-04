/**
 * Token Universe - Canonical token definitions shared across JS + Python
 * 
 * Provides a single source of truth for token addresses and trading pairs
 * across all supported chains. This enables clean expansion of trading
 * strategies without breaking existing functionality.
 */

// Token configuration by chain ID
const TOKENS = {
  // Polygon (137)
  137: {
    WMATIC: "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",
    WETH: "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619",
    USDC: "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
    USDT: "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
    DAI: "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063",
    WBTC: "0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6",
    LINK: "0x53E0bca35eC356BD5ddDFebbD1Fc0fD03FaBad39",
    AAVE: "0xD6DF932A45C0f255f85145f286eA0b292B21C90B",
    UNI: "0xb33EaAd8d922B1083446DC23f610c2567fB5180f"
  },
  // Ethereum (1)
  1: {
    WETH: "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    USDC: "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    USDT: "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    DAI: "0x6B175474E89094C44Da98b954EedeAC495271d0F",
    WBTC: "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
    LINK: "0x514910771AF9Ca656af840dff83E8264EcF986CA",
    AAVE: "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
    UNI: "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"
  },
  // Arbitrum (42161)
  42161: {
    WETH: "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
    USDC: "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8",
    USDT: "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
    DAI: "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1",
    WBTC: "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f",
    LINK: "0xf97f4df75117a78c1A5a0DBb814Af92458539FB4",
    AAVE: "0xba5DdD1f9d7F570dc94a51479a000E3BCE967196",
    UNI: "0xFa7F8980b0f1E64A2062791cc3b0871572f1F7f0"
  }
};

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
  getChainTokens
};
