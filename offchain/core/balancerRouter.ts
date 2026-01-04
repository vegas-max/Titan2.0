/**
 * Balancer Multi-Hop Router - Generalized multi-leg routing support
 * 
 * Extends existing Balancer integration to support complex routing:
 * - Multi-hop paths (e.g., WMATIC → WETH → USDC)
 * - Stable basket routing
 * - Pre-execution simulation via queryBatchSwap
 * - Zero execution risk with quote validation
 */

import { ethers } from 'ethers';

/**
 * Balancer Swap Leg definition
 */
export interface BalSwapLeg {
  /** Pool ID (bytes32) */
  poolId: string;
  /** Index of input asset in assets array */
  assetInIndex: number;
  /** Index of output asset in assets array */
  assetOutIndex: number;
  /** Amount to swap (for first leg, or 0 for subsequent legs in multi-hop) */
  amount: string;
  /** User data (typically empty "0x" for standard swaps) */
  userData: string;
}

/**
 * Balancer Swap Kind enum
 */
export enum SwapKind {
  GIVEN_IN = 0,
  GIVEN_OUT = 1
}

/**
 * Balancer Funds Struct
 */
export interface FundManagement {
  sender: string;
  fromInternalBalance: boolean;
  recipient: string;
  toInternalBalance: boolean;
}

/**
 * Build Balancer swap legs for a multi-hop route
 * 
 * @param poolId - Balancer pool ID (same for all legs in single-pool routing)
 * @param assets - Array of token addresses in the route
 * @param path - Indices defining the path through assets array
 * @param amountIn - Initial input amount (in wei)
 * @returns Array of BalSwapLeg objects
 * 
 * @example
 * // Route: WMATIC (idx 0) → WETH (idx 1) → USDC (idx 2)
 * const legs = buildBalancerLegs(
 *   poolId,
 *   [WMATIC, WETH, USDC],
 *   [0, 1, 2],
 *   ethers.utils.parseEther("100")
 * );
 */
export function buildBalancerLegs(
  poolId: string,
  assets: string[],
  path: number[],
  amountIn: bigint | string
): BalSwapLeg[] {
  if (path.length < 2) {
    throw new Error("Path must have at least 2 indices");
  }

  const legs: BalSwapLeg[] = [];
  
  // First leg uses the input amount
  // Subsequent legs use 0 (indicating "use output of previous leg")
  for (let k = 0; k < path.length - 1; k++) {
    legs.push({
      poolId,
      assetInIndex: path[k],
      assetOutIndex: path[k + 1],
      amount: k === 0 ? amountIn.toString() : "0",
      userData: "0x"
    });
  }

  return legs;
}

/**
 * Build Balancer swap legs for multi-pool routing
 * Supports different pools for each leg
 * 
 * @param poolIds - Array of pool IDs, one per leg
 * @param assets - Array of all token addresses involved
 * @param path - Indices defining the path through assets array
 * @param amountIn - Initial input amount (in wei)
 * @returns Array of BalSwapLeg objects
 * 
 * @example
 * // Route through different pools:
 * // WMATIC → WETH (pool1) → USDC (pool2)
 * const legs = buildMultiPoolBalancerLegs(
 *   [pool1Id, pool2Id],
 *   [WMATIC, WETH, USDC],
 *   [0, 1, 2],
 *   ethers.utils.parseEther("100")
 * );
 */
export function buildMultiPoolBalancerLegs(
  poolIds: string[],
  assets: string[],
  path: number[],
  amountIn: bigint | string
): BalSwapLeg[] {
  if (path.length - 1 !== poolIds.length) {
    throw new Error("Number of pools must equal number of hops (path.length - 1)");
  }

  const legs: BalSwapLeg[] = [];
  
  for (let k = 0; k < path.length - 1; k++) {
    legs.push({
      poolId: poolIds[k],
      assetInIndex: path[k],
      assetOutIndex: path[k + 1],
      amount: k === 0 ? amountIn.toString() : "0",
      userData: "0x"
    });
  }

  return legs;
}

/**
 * Query Balancer batch swap without executing
 * 
 * @param vaultAddress - Balancer Vault contract address
 * @param provider - Ethers provider
 * @param swapKind - GIVEN_IN or GIVEN_OUT
 * @param swaps - Array of swap legs
 * @param assets - Array of asset addresses
 * @param funds - Fund management struct
 * @returns Promise<bigint[]> - Array of deltas for each asset (negative = sent, positive = received)
 */
export async function queryBatchSwap(
  vaultAddress: string,
  provider: ethers.Provider,
  swapKind: SwapKind,
  swaps: BalSwapLeg[],
  assets: string[],
  funds: FundManagement
): Promise<bigint[]> {
  const vaultAbi = [
    "function queryBatchSwap(uint8 kind, tuple(bytes32 poolId, uint256 assetInIndex, uint256 assetOutIndex, uint256 amount, bytes userData)[] swaps, address[] assets, tuple(address sender, bool fromInternalBalance, address recipient, bool toInternalBalance) funds) external returns (int256[] assetDeltas)"
  ];

  const vault = new ethers.Contract(vaultAddress, vaultAbi, provider);

  try {
    const assetDeltas = await vault.queryBatchSwap(
      swapKind,
      swaps,
      assets,
      funds
    );

    // Convert to bigint array
    return assetDeltas.map((delta: any) => BigInt(delta.toString()));
  } catch (error: any) {
    throw new Error(`Balancer queryBatchSwap failed: ${error.message}`);
  }
}

/**
 * Calculate expected output from queryBatchSwap result
 * 
 * @param assetDeltas - Array of deltas returned from queryBatchSwap
 * @param outputAssetIndex - Index of the output asset
 * @returns Expected output amount (positive value)
 */
export function getOutputFromDeltas(assetDeltas: bigint[], outputAssetIndex: number): bigint {
  const delta = assetDeltas[outputAssetIndex];
  // Output is positive in the deltas array
  return delta > 0n ? delta : 0n;
}

/**
 * Build standard funds struct for queries
 * 
 * @param sender - Address initiating the swap
 * @returns FundManagement struct suitable for queries
 */
export function buildQueryFunds(sender: string = ethers.ZeroAddress): FundManagement {
  return {
    sender,
    fromInternalBalance: false,
    recipient: sender,
    toInternalBalance: false
  };
}

/**
 * High-level function to quote a Balancer multi-hop route
 * 
 * @param vaultAddress - Balancer Vault address
 * @param provider - Ethers provider
 * @param poolId - Pool ID (for single-pool routing)
 * @param assets - Array of token addresses in route
 * @param path - Indices defining the path
 * @param amountIn - Input amount in wei
 * @returns Promise<bigint> - Expected output amount
 * 
 * @example
 * const output = await quoteBalancerMultiHop(
 *   BALANCER_VAULT,
 *   provider,
 *   poolId,
 *   [WMATIC, WETH, USDC],
 *   [0, 1, 2],
 *   ethers.parseEther("100")
 * );
 */
export async function quoteBalancerMultiHop(
  vaultAddress: string,
  provider: ethers.Provider,
  poolId: string,
  assets: string[],
  path: number[],
  amountIn: bigint | string
): Promise<bigint> {
  const legs = buildBalancerLegs(poolId, assets, path, amountIn);
  const funds = buildQueryFunds();

  const deltas = await queryBatchSwap(
    vaultAddress,
    provider,
    SwapKind.GIVEN_IN,
    legs,
    assets,
    funds
  );

  // Output is the last asset in the path
  const outputIndex = path[path.length - 1];
  return getOutputFromDeltas(deltas, outputIndex);
}

/**
 * Quote multi-pool Balancer route
 * 
 * @param vaultAddress - Balancer Vault address
 * @param provider - Ethers provider
 * @param poolIds - Array of pool IDs
 * @param assets - Array of token addresses
 * @param path - Indices defining the path
 * @param amountIn - Input amount in wei
 * @returns Promise<bigint> - Expected output amount
 */
export async function quoteBalancerMultiPool(
  vaultAddress: string,
  provider: ethers.Provider,
  poolIds: string[],
  assets: string[],
  path: number[],
  amountIn: bigint | string
): Promise<bigint> {
  const legs = buildMultiPoolBalancerLegs(poolIds, assets, path, amountIn);
  const funds = buildQueryFunds();

  const deltas = await queryBatchSwap(
    vaultAddress,
    provider,
    SwapKind.GIVEN_IN,
    legs,
    assets,
    funds
  );

  const outputIndex = path[path.length - 1];
  return getOutputFromDeltas(deltas, outputIndex);
}

/**
 * Validate that a Balancer route is profitable
 * 
 * @param amountIn - Input amount
 * @param amountOut - Output amount from queryBatchSwap
 * @param minProfitBps - Minimum profit in basis points (e.g., 10 = 0.1%)
 * @returns true if profitable
 */
export function isBalancerRouteProfitable(
  amountIn: bigint,
  amountOut: bigint,
  minProfitBps: number = 10
): boolean {
  if (amountIn === 0n) return false;
  
  const profitBps = ((amountOut - amountIn) * 10000n) / amountIn;
  return profitBps >= BigInt(minProfitBps);
}
