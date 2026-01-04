/**
 * Centralized Token Configuration System
 * 
 * This module provides a single source of truth for token addresses, IDs, and types
 * across all supported chains. It enables consistent token handling throughout the system.
 * 
 * Token ID Convention:
 * - 0-10: Universal tokens (consistent across chains)
 * - 11-50: Chain-specific tokens
 * - 51-255: Available for expansion
 */

// Token Type enum (matches Solidity enum)
const TokenType = {
  CANONICAL: 0,  // Native to the chain
  BRIDGED: 1,    // Bridged version (e.g., USDC.e)
  WRAPPED: 2     // Wrapped native (WETH, WMATIC, etc.)
};

// Universal token IDs (consistent across chains)
const UniversalTokenIds = {
  WNATIVE: 0,   // Wrapped native token
  USDC: 1,      // USD Coin
  USDT: 2,      // Tether USD
  DAI: 3,       // Dai Stablecoin
  WBTC: 4,      // Wrapped Bitcoin
  WETH: 5       // Wrapped Ether (for non-Ethereum chains)
};

// Chain-specific token IDs (11-50)
const ChainTokenIds = {
  UNI: 11,
  LINK: 12,
  AAVE: 13,
  CRV: 14,
  SUSHI: 15,
  BAL: 16,
  QUICK: 17,    // QuickSwap (Polygon)
  GHST: 18,     // Aavegotchi (Polygon)
  OP: 19,       // Optimism
  ARB: 20,      // Arbitrum
  AVAX: 21,     // Avalanche
  FTM: 22       // Fantom
};

// Token configurations per chain
const CHAIN_CONFIGS = {
  // Ethereum (Chain ID 1)
  1: {
    tokens: [
      { id: UniversalTokenIds.WETH, type: TokenType.WRAPPED, address: "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2" },
      { id: UniversalTokenIds.USDC, type: TokenType.CANONICAL, address: "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48" },
      { id: UniversalTokenIds.USDT, type: TokenType.CANONICAL, address: "0xdAC17F958D2ee523a2206206994597C13D831ec7" },
      { id: UniversalTokenIds.DAI, type: TokenType.CANONICAL, address: "0x6B175474E89094C44Da98b954EedeAC495271d0F" },
      { id: UniversalTokenIds.WBTC, type: TokenType.CANONICAL, address: "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599" },
      { id: ChainTokenIds.UNI, type: TokenType.CANONICAL, address: "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984" },
      { id: ChainTokenIds.LINK, type: TokenType.CANONICAL, address: "0x514910771AF9Ca656af840dff83E8264EcF986CA" },
      { id: ChainTokenIds.AAVE, type: TokenType.CANONICAL, address: "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9" }
    ]
  },

  // Polygon (Chain ID 137)
  137: {
    tokens: [
      { id: UniversalTokenIds.WNATIVE, type: TokenType.WRAPPED, address: "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270" }, // WMATIC
      { id: UniversalTokenIds.USDC, type: TokenType.CANONICAL, address: "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359" },
      { id: UniversalTokenIds.USDC, type: TokenType.BRIDGED, address: "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174" }, // USDC.e
      { id: UniversalTokenIds.USDT, type: TokenType.CANONICAL, address: "0xc2132D05D31c914a87C6611C10748AEb04B58e8F" },
      { id: UniversalTokenIds.DAI, type: TokenType.CANONICAL, address: "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063" },
      { id: UniversalTokenIds.WBTC, type: TokenType.CANONICAL, address: "0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6" },
      { id: UniversalTokenIds.WETH, type: TokenType.BRIDGED, address: "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619" },
      { id: ChainTokenIds.QUICK, type: TokenType.CANONICAL, address: "0xB5C064F955D8e7F38fE0460C556a72987494eE17" },
      { id: ChainTokenIds.GHST, type: TokenType.CANONICAL, address: "0x385Eeac5cB85A38A9a07A70c73e0a3271CfB54A7" }
    ]
  },

  // Arbitrum (Chain ID 42161)
  42161: {
    tokens: [
      { id: UniversalTokenIds.WETH, type: TokenType.WRAPPED, address: "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1" },
      { id: UniversalTokenIds.USDC, type: TokenType.CANONICAL, address: "0xaf88d065e77c8cC2239327C5EDb3A432268e5831" },
      { id: UniversalTokenIds.USDC, type: TokenType.BRIDGED, address: "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8" }, // USDC.e
      { id: UniversalTokenIds.USDT, type: TokenType.CANONICAL, address: "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9" },
      { id: UniversalTokenIds.DAI, type: TokenType.CANONICAL, address: "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1" },
      { id: UniversalTokenIds.WBTC, type: TokenType.CANONICAL, address: "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f" },
      { id: ChainTokenIds.ARB, type: TokenType.CANONICAL, address: "0x912CE59144191C1204E64559FE8253a0e49E6548" }
    ]
  },

  // Optimism (Chain ID 10)
  10: {
    tokens: [
      { id: UniversalTokenIds.WETH, type: TokenType.WRAPPED, address: "0x4200000000000000000000000000000000000006" },
      { id: UniversalTokenIds.USDC, type: TokenType.CANONICAL, address: "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85" },
      { id: UniversalTokenIds.USDC, type: TokenType.BRIDGED, address: "0x7F5c764cBc14f9669B88837ca1490cCa17c31607" }, // USDC.e
      { id: UniversalTokenIds.USDT, type: TokenType.CANONICAL, address: "0x94b008aA00579c1307B0EF2c499aD98a8ce58e58" },
      { id: UniversalTokenIds.DAI, type: TokenType.CANONICAL, address: "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1" },
      { id: UniversalTokenIds.WBTC, type: TokenType.CANONICAL, address: "0x68f180fcCe6836688e9084f035309E29Bf0A2095" },
      { id: ChainTokenIds.OP, type: TokenType.CANONICAL, address: "0x4200000000000000000000000000000000000042" }
    ]
  },

  // Base (Chain ID 8453)
  8453: {
    tokens: [
      { id: UniversalTokenIds.WETH, type: TokenType.WRAPPED, address: "0x4200000000000000000000000000000000000006" },
      { id: UniversalTokenIds.USDC, type: TokenType.CANONICAL, address: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913" },
      { id: UniversalTokenIds.USDC, type: TokenType.BRIDGED, address: "0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA" }, // USDbC
      { id: UniversalTokenIds.DAI, type: TokenType.CANONICAL, address: "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb" }
    ]
  }
};

/**
 * Get all tokens for a specific chain
 * @param {number} chainId - EIP-155 Chain ID
 * @returns {Array} Array of token configurations
 */
function getChainTokens(chainId) {
  const config = CHAIN_CONFIGS[chainId];
  return config ? config.tokens : [];
}

/**
 * Get token address by ID and type
 * @param {number} chainId - EIP-155 Chain ID
 * @param {number} tokenId - Token ID (0-255)
 * @param {number} tokenType - Token type (CANONICAL, BRIDGED, WRAPPED)
 * @returns {string|null} Token address or null if not found
 */
function getTokenAddress(chainId, tokenId, tokenType = TokenType.CANONICAL) {
  const tokens = getChainTokens(chainId);
  const token = tokens.find(t => t.id === tokenId && t.type === tokenType);
  return token ? token.address : null;
}

/**
 * Get token ID and type from address
 * @param {number} chainId - EIP-155 Chain ID
 * @param {string} address - Token address
 * @returns {Object|null} {id, type} or null if not found
 */
function getTokenIdFromAddress(chainId, address) {
  const tokens = getChainTokens(chainId);
  const normalizedAddress = address.toLowerCase();
  const token = tokens.find(t => t.address.toLowerCase() === normalizedAddress);
  return token ? { id: token.id, type: token.type } : null;
}

/**
 * Get all addresses for a token ID (all types)
 * @param {number} chainId - EIP-155 Chain ID
 * @param {number} tokenId - Token ID
 * @returns {Array} Array of {address, type} objects
 */
function getAllTokenAddresses(chainId, tokenId) {
  const tokens = getChainTokens(chainId);
  return tokens
    .filter(t => t.id === tokenId)
    .map(t => ({ address: t.address, type: t.type }));
}

/**
 * Check if a token is registered
 * @param {number} chainId - EIP-155 Chain ID
 * @param {string} address - Token address
 * @returns {boolean} true if token is registered
 */
function isTokenRegistered(chainId, address) {
  return getTokenIdFromAddress(chainId, address) !== null;
}

/**
 * Get token symbol from universal/chain token IDs
 * @param {number} tokenId - Token ID
 * @returns {string|null} Token symbol or null
 */
function getTokenSymbol(tokenId) {
  // Universal tokens
  for (const [symbol, id] of Object.entries(UniversalTokenIds)) {
    if (id === tokenId) return symbol;
  }
  // Chain-specific tokens
  for (const [symbol, id] of Object.entries(ChainTokenIds)) {
    if (id === tokenId) return symbol;
  }
  return null;
}

/**
 * Get all supported chain IDs
 * @returns {Array<number>} Array of chain IDs
 */
function getSupportedChains() {
  return Object.keys(CHAIN_CONFIGS).map(Number);
}

module.exports = {
  TokenType,
  UniversalTokenIds,
  ChainTokenIds,
  CHAIN_CONFIGS,
  getChainTokens,
  getTokenAddress,
  getTokenIdFromAddress,
  getAllTokenAddresses,
  isTokenRegistered,
  getTokenSymbol,
  getSupportedChains
};
