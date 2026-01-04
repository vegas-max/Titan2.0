/**
 * TWAP Accumulator - Time-Weighted Average Price tracking
 * 
 * Event-based TWAP calculation for institutional-grade validation.
 * This filters spoofed liquidity, avoids MEV bait pools, and enables
 * larger trade sizes safely with reduced revert rates.
 */

/**
 * TWAPAccumulator - Calculates time-weighted average prices from event streams
 */
class TWAPAccumulator {
  constructor(config = {}) {
    this.windowMs = config.windowMs || 30000; // 30 seconds default
    this.minSamples = config.minSamples || 2;
    this.maxSamples = config.maxSamples || 100;
    this.samples = [];
  }

  /**
   * Add a new price sample
   * @param {number} price - Price value to add
   */
  push(price) {
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
   * @returns {number} TWAP value, or the last price if insufficient samples
   */
  value() {
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
   * @returns {number} Latest price or 0 if no samples
   */
  latest() {
    if (this.samples.length === 0) {
      return 0;
    }
    return this.samples[this.samples.length - 1].p;
  }

  /**
   * Check if TWAP is ready (has minimum samples)
   * @returns {boolean} true if TWAP can be calculated reliably
   */
  isReady() {
    return this.samples.length >= this.minSamples;
  }

  /**
   * Get number of samples currently held
   * @returns {number} Sample count
   */
  sampleCount() {
    return this.samples.length;
  }

  /**
   * Clear all samples
   */
  clear() {
    this.samples = [];
  }

  /**
   * Get price volatility (standard deviation)
   * @returns {number} Standard deviation of prices, or 0 if insufficient samples
   */
  volatility() {
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
   * @returns {number} Age in ms, or 0 if no samples
   */
  oldestSampleAge() {
    if (this.samples.length === 0) {
      return 0;
    }
    return Date.now() - this.samples[0].t;
  }

  /**
   * Calculate price deviation from TWAP
   * @param {number} currentPrice - Current spot price
   * @returns {number} Percentage deviation from TWAP (0-1 scale)
   */
  deviation(currentPrice) {
    const twap = this.value();
    if (twap === 0) {
      return 0;
    }
    return Math.abs(currentPrice - twap) / twap;
  }

  /**
   * Check if current price is within acceptable bounds
   * @param {number} currentPrice - Current spot price
   * @param {number} maxDeviation - Maximum allowed deviation (0-1 scale, e.g., 0.05 = 5%)
   * @returns {boolean} true if price is within bounds
   */
  isWithinBounds(currentPrice, maxDeviation = 0.05) {
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
class MultiPoolTWAP {
  constructor(config = {}) {
    this.config = config;
    this.pools = new Map();
  }

  /**
   * Get pool key from token addresses
   * @param {string} tokenA - First token address
   * @param {string} tokenB - Second token address
   * @returns {string} Normalized pool key
   */
  _getPoolKey(tokenA, tokenB) {
    // Normalize addresses and sort to ensure consistent key
    const a = tokenA.toLowerCase();
    const b = tokenB.toLowerCase();
    return a < b ? `${a}:${b}` : `${b}:${a}`;
  }

  /**
   * Get or create TWAP accumulator for a pool
   * @param {string} tokenA - First token address
   * @param {string} tokenB - Second token address
   * @returns {TWAPAccumulator} TWAPAccumulator instance
   */
  getPool(tokenA, tokenB) {
    const key = this._getPoolKey(tokenA, tokenB);
    
    if (!this.pools.has(key)) {
      this.pools.set(key, new TWAPAccumulator(this.config));
    }
    
    return this.pools.get(key);
  }

  /**
   * Add price sample to a specific pool
   * @param {string} tokenA - First token address
   * @param {string} tokenB - Second token address
   * @param {number} price - Price value
   */
  push(tokenA, tokenB, price) {
    this.getPool(tokenA, tokenB).push(price);
  }

  /**
   * Get TWAP value for a pool
   * @param {string} tokenA - First token address
   * @param {string} tokenB - Second token address
   * @returns {number} TWAP value
   */
  value(tokenA, tokenB) {
    return this.getPool(tokenA, tokenB).value();
  }

  /**
   * Check if pool TWAP is ready
   * @param {string} tokenA - First token address
   * @param {string} tokenB - Second token address
   * @returns {boolean} true if ready
   */
  isReady(tokenA, tokenB) {
    return this.getPool(tokenA, tokenB).isReady();
  }

  /**
   * Clear all pools
   */
  clearAll() {
    this.pools.clear();
  }

  /**
   * Get number of tracked pools
   * @returns {number} Pool count
   */
  poolCount() {
    return this.pools.size;
  }
}

module.exports = {
  TWAPAccumulator,
  MultiPoolTWAP
};
