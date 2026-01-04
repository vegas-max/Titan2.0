/**
 * TWAP Accumulator - Time-Weighted Average Price tracking
 * 
 * Event-based TWAP calculation for institutional-grade validation.
 * This filters spoofed liquidity, avoids MEV bait pools, and enables
 * larger trade sizes safely with reduced revert rates.
 * 
 * Features:
 * - Lightweight sampling (no heavy storage)
 * - Time-weighted calculation
 * - Configurable window duration
 * - Automatic sample pruning
 */

interface PriceSample {
  /** Price value */
  p: number;
  /** Timestamp in milliseconds */
  t: number;
}

export interface TWAPConfig {
  /** Window duration in milliseconds (default: 30000 = 30 seconds) */
  windowMs?: number;
  /** Minimum samples required for TWAP calculation (default: 2) */
  minSamples?: number;
  /** Maximum samples to retain (default: 100) */
  maxSamples?: number;
}

/**
 * TWAPAccumulator - Calculates time-weighted average prices from event streams
 * 
 * Usage:
 * ```typescript
 * const twap = new TWAPAccumulator({ windowMs: 30000 });
 * 
 * // On Sync/Swap event
 * twap.push(calculatePriceFromReserves(reserve0, reserve1));
 * 
 * // Get current TWAP
 * const avgPrice = twap.value();
 * ```
 */
export class TWAPAccumulator {
  private samples: PriceSample[] = [];
  private readonly windowMs: number;
  private readonly minSamples: number;
  private readonly maxSamples: number;

  constructor(config: TWAPConfig = {}) {
    this.windowMs = config.windowMs ?? 30000; // 30 seconds default
    this.minSamples = config.minSamples ?? 2;
    this.maxSamples = config.maxSamples ?? 100;
  }

  /**
   * Add a new price sample
   * @param price - Price value to add
   */
  push(price: number): void {
    if (!isFinite(price) || price <= 0) {
      // Skip invalid prices
      return;
    }

    const now = Date.now();
    this.samples.push({ p: price, t: now });

    // Prune old samples outside the window
    this.samples = this.samples.filter(s => now - s.t < this.windowMs);

    // Enforce max samples limit (keep most recent)
    if (this.samples.length > this.maxSamples) {
      this.samples = this.samples.slice(-this.maxSamples);
    }
  }

  /**
   * Calculate time-weighted average price
   * @returns TWAP value, or the last price if insufficient samples
   */
  value(): number {
    if (this.samples.length === 0) {
      return 0;
    }

    // If we have only one sample, return it
    if (this.samples.length === 1) {
      return this.samples[0].p;
    }

    // Calculate time-weighted average
    let weightedSum = 0;
    let totalWeight = 0;

    for (let i = 1; i < this.samples.length; i++) {
      const dt = this.samples[i].t - this.samples[i - 1].t;
      // Weight is the time duration between samples
      weightedSum += this.samples[i].p * dt;
      totalWeight += dt;
    }

    if (totalWeight === 0) {
      // All samples at same timestamp, return latest
      return this.samples[this.samples.length - 1].p;
    }

    return weightedSum / totalWeight;
  }

  /**
   * Get the latest (spot) price
   * @returns Latest price or 0 if no samples
   */
  latest(): number {
    if (this.samples.length === 0) {
      return 0;
    }
    return this.samples[this.samples.length - 1].p;
  }

  /**
   * Check if TWAP is ready (has minimum samples)
   * @returns true if TWAP can be calculated reliably
   */
  isReady(): boolean {
    return this.samples.length >= this.minSamples;
  }

  /**
   * Get number of samples currently held
   * @returns Sample count
   */
  sampleCount(): number {
    return this.samples.length;
  }

  /**
   * Clear all samples
   */
  clear(): void {
    this.samples = [];
  }

  /**
   * Get price volatility (standard deviation)
   * @returns Standard deviation of prices, or 0 if insufficient samples
   */
  volatility(): number {
    if (this.samples.length < 2) {
      return 0;
    }

    const prices = this.samples.map(s => s.p);
    const mean = prices.reduce((sum, p) => sum + p, 0) / prices.length;
    const variance = prices.reduce((sum, p) => sum + Math.pow(p - mean, 2), 0) / prices.length;
    
    return Math.sqrt(variance);
  }

  /**
   * Get age of oldest sample in milliseconds
   * @returns Age in ms, or 0 if no samples
   */
  oldestSampleAge(): number {
    if (this.samples.length === 0) {
      return 0;
    }
    return Date.now() - this.samples[0].t;
  }

  /**
   * Calculate price deviation from TWAP
   * @param currentPrice - Current spot price
   * @returns Percentage deviation from TWAP (0-1 scale)
   */
  deviation(currentPrice: number): number {
    const twap = this.value();
    if (twap === 0) {
      return 0;
    }
    return Math.abs(currentPrice - twap) / twap;
  }

  /**
   * Check if current price is within acceptable bounds
   * @param currentPrice - Current spot price
   * @param maxDeviation - Maximum allowed deviation (0-1 scale, e.g., 0.05 = 5%)
   * @returns true if price is within bounds
   */
  isWithinBounds(currentPrice: number, maxDeviation: number = 0.05): boolean {
    if (!this.isReady()) {
      // Not enough data yet, accept the price
      return true;
    }
    return this.deviation(currentPrice) <= maxDeviation;
  }
}

/**
 * Multi-pool TWAP manager for tracking multiple token pairs
 */
export class MultiPoolTWAP {
  private pools: Map<string, TWAPAccumulator> = new Map();
  private readonly config: TWAPConfig;

  constructor(config: TWAPConfig = {}) {
    this.config = config;
  }

  /**
   * Get pool key from token addresses
   * @param tokenA - First token address
   * @param tokenB - Second token address
   * @returns Normalized pool key
   */
  private getPoolKey(tokenA: string, tokenB: string): string {
    // Normalize addresses and sort to ensure consistent key
    const a = tokenA.toLowerCase();
    const b = tokenB.toLowerCase();
    return a < b ? `${a}:${b}` : `${b}:${a}`;
  }

  /**
   * Get or create TWAP accumulator for a pool
   * @param tokenA - First token address
   * @param tokenB - Second token address
   * @returns TWAPAccumulator instance
   */
  getPool(tokenA: string, tokenB: string): TWAPAccumulator {
    const key = this.getPoolKey(tokenA, tokenB);
    
    if (!this.pools.has(key)) {
      this.pools.set(key, new TWAPAccumulator(this.config));
    }
    
    return this.pools.get(key)!;
  }

  /**
   * Add price sample to a specific pool
   * @param tokenA - First token address
   * @param tokenB - Second token address
   * @param price - Price value
   */
  push(tokenA: string, tokenB: string, price: number): void {
    this.getPool(tokenA, tokenB).push(price);
  }

  /**
   * Get TWAP value for a pool
   * @param tokenA - First token address
   * @param tokenB - Second token address
   * @returns TWAP value
   */
  value(tokenA: string, tokenB: string): number {
    return this.getPool(tokenA, tokenB).value();
  }

  /**
   * Check if pool TWAP is ready
   * @param tokenA - First token address
   * @param tokenB - Second token address
   * @returns true if ready
   */
  isReady(tokenA: string, tokenB: string): boolean {
    return this.getPool(tokenA, tokenB).isReady();
  }

  /**
   * Clear all pools
   */
  clearAll(): void {
    this.pools.clear();
  }

  /**
   * Get number of tracked pools
   * @returns Pool count
   */
  poolCount(): number {
    return this.pools.size;
  }
}
