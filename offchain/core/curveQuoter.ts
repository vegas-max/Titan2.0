/**
 * Curve Enhanced Quote Module
 * 
 * Dynamic Curve pair discovery with underlying token support.
 * Enables stablecoin loops (USDC ⇄ USDT ⇄ DAI) with deep liquidity
 * and lower slippage for larger optimal trade sizes.
 */

import { ethers } from 'ethers';

// Curve Pool ABI - includes coins, get_dy, and get_dy_underlying
const CURVE_ABI = [
  {
    "stateMutability": "view",
    "type": "function",
    "name": "coins",
    "inputs": [{"name": "arg0", "type": "uint256"}],
    "outputs": [{"name": "", "type": "address"}]
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "get_dy",
    "inputs": [
      {"name": "i", "type": "int128"},
      {"name": "j", "type": "int128"},
      {"name": "dx", "type": "uint256"}
    ],
    "outputs": [{"name": "", "type": "uint256"}]
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "get_dy_underlying",
    "inputs": [
      {"name": "i", "type": "int128"},
      {"name": "j", "type": "int128"},
      {"name": "dx", "type": "uint256"}
    ],
    "outputs": [{"name": "", "type": "uint256"}]
  }
];

// Maximum coins to scan safely in a Curve pool
const MAX_CURVE_COINS = 8;

/**
 * Dynamically discover token indices in a Curve pool
 * 
 * @param poolAddress - Curve pool contract address
 * @param provider - Ethers provider
 * @param tokenIn - Input token address
 * @param tokenOut - Output token address
 * @returns Promise<[number, number] | null> - Token indices [i, j] or null if not found
 */
export async function discoverCurveIndices(
  poolAddress: string,
  provider: ethers.Provider,
  tokenIn: string,
  tokenOut: string
): Promise<[number, number] | null> {
  const pool = new ethers.Contract(poolAddress, CURVE_ABI, provider);
  
  const normalizedIn = tokenIn.toLowerCase();
  const normalizedOut = tokenOut.toLowerCase();
  
  let indexIn = -1;
  let indexOut = -1;

  // Scan pool coins to find token indices
  for (let k = 0; k < MAX_CURVE_COINS; k++) {
    try {
      const coinAddress = await pool.coins(k);
      const normalizedCoin = coinAddress.toLowerCase();
      
      if (normalizedCoin === normalizedIn) {
        indexIn = k;
      }
      if (normalizedCoin === normalizedOut) {
        indexOut = k;
      }
      
      // Early exit if both found
      if (indexIn >= 0 && indexOut >= 0) {
        break;
      }
    } catch (error) {
      // No more coins at this index
      break;
    }
  }

  if (indexIn < 0 || indexOut < 0) {
    return null;
  }

  return [indexIn, indexOut];
}

/**
 * Quote Curve swap by token addresses (not indices)
 * Automatically tries get_dy_underlying for better routing on stablecoin pools
 * 
 * @param poolAddress - Curve pool contract address
 * @param provider - Ethers provider
 * @param amountIn - Input amount (in wei)
 * @param tokenIn - Input token address
 * @param tokenOut - Output token address
 * @returns Promise<bigint | null> - Expected output amount or null if failed
 * 
 * @example
 * const output = await curveQuoteByTokens(
 *   CURVE_POOL,
 *   provider,
 *   ethers.parseUnits("1000", 6), // 1000 USDC
 *   USDC_ADDRESS,
 *   USDT_ADDRESS
 * );
 */
export async function curveQuoteByTokens(
  poolAddress: string,
  provider: ethers.Provider,
  amountIn: bigint,
  tokenIn: string,
  tokenOut: string
): Promise<bigint | null> {
  try {
    // Discover token indices
    const indices = await discoverCurveIndices(poolAddress, provider, tokenIn, tokenOut);
    
    if (!indices) {
      console.warn(`Curve: Tokens not found in pool ${poolAddress}`);
      return null;
    }

    const [i, j] = indices;
    const pool = new ethers.Contract(poolAddress, CURVE_ABI, provider);

    // Try get_dy_underlying first (better for stablecoin pools with underlying assets)
    try {
      const output = await pool.get_dy_underlying(i, j, amountIn);
      return BigInt(output.toString());
    } catch (underlyingError) {
      // get_dy_underlying not available or failed, try regular get_dy
      try {
        const output = await pool.get_dy(i, j, amountIn);
        return BigInt(output.toString());
      } catch (dyError) {
        console.error(`Curve get_dy failed: ${dyError}`);
        return null;
      }
    }
  } catch (error: any) {
    console.error(`Curve quote failed: ${error.message}`);
    return null;
  }
}

/**
 * Quote Curve swap using known indices (legacy mode)
 * 
 * @param poolAddress - Curve pool contract address
 * @param provider - Ethers provider
 * @param amountIn - Input amount (in wei)
 * @param i - Input token index
 * @param j - Output token index
 * @param useUnderlying - Whether to use get_dy_underlying
 * @returns Promise<bigint | null> - Expected output amount or null if failed
 */
export async function curveQuoteByIndices(
  poolAddress: string,
  provider: ethers.Provider,
  amountIn: bigint,
  i: number,
  j: number,
  useUnderlying: boolean = false
): Promise<bigint | null> {
  try {
    const pool = new ethers.Contract(poolAddress, CURVE_ABI, provider);
    
    const method = useUnderlying ? pool.get_dy_underlying : pool.get_dy;
    const output = await method(i, j, amountIn);
    
    return BigInt(output.toString());
  } catch (error: any) {
    console.error(`Curve quote by indices failed: ${error.message}`);
    return null;
  }
}

/**
 * Get all coin addresses from a Curve pool
 * Useful for discovering what tokens are available
 * 
 * @param poolAddress - Curve pool contract address
 * @param provider - Ethers provider
 * @returns Promise<string[]> - Array of coin addresses
 */
export async function getCurvePoolCoins(
  poolAddress: string,
  provider: ethers.Provider
): Promise<string[]> {
  const pool = new ethers.Contract(poolAddress, CURVE_ABI, provider);
  const coins: string[] = [];

  for (let k = 0; k < MAX_CURVE_COINS; k++) {
    try {
      const coinAddress = await pool.coins(k);
      coins.push(coinAddress);
    } catch (error) {
      // No more coins
      break;
    }
  }

  return coins;
}

/**
 * Check if a Curve pool supports a token pair
 * 
 * @param poolAddress - Curve pool contract address
 * @param provider - Ethers provider
 * @param tokenA - First token address
 * @param tokenB - Second token address
 * @returns Promise<boolean> - true if both tokens are in the pool
 */
export async function isCurvePairSupported(
  poolAddress: string,
  provider: ethers.Provider,
  tokenA: string,
  tokenB: string
): Promise<boolean> {
  const indices = await discoverCurveIndices(poolAddress, provider, tokenA, tokenB);
  return indices !== null;
}
