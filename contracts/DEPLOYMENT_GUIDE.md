# FlashArbExecutor Deployment Guide

## Quick Reference

**Recommended Version:** FlashArbExecutorV2  
**Compiler:** Solidity ^0.8.24  
**License:** MIT  
**Audit Status:** Pending (REQUIRED before mainnet)

---

## Deployment Parameters

### Constructor Arguments

```solidity
constructor(
    address _balancerVault,    // Balancer V2 Vault address
    address _aavePool,         // Aave V3 Pool address
    address _quickswapRouter,  // QuickSwap Router address
    address _sushiswapRouter,  // SushiSwap Router address
    address _uniswapV3Router,  // Uniswap V3 Router address
    uint256 _minProfitWei      // Minimum profit threshold in wei
)
```

### Mainnet Addresses (Polygon)

```javascript
const POLYGON_ADDRESSES = {
    balancerVault: "0xBA12222222228d8Ba445958a75a0704d566BF2C8",
    aavePool: "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
    quickswapRouter: "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff",
    sushiswapRouter: "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506",
    uniswapV3Router: "0xE592427A0AEce92De3Edee1F18E0157C05861564",
    minProfitWei: ethers.parseEther("0.01") // 0.01 MATIC minimum
};
```

### Deployment Script

```javascript
// scripts/deploy_flasharb.js
const { ethers } = require("hardhat");

async function main() {
    const [deployer] = await ethers.getSigners();
    console.log("Deploying FlashArbExecutorV2 with account:", deployer.address);
    console.log("Account balance:", (await ethers.provider.getBalance(deployer.address)).toString());

    // Polygon addresses
    const balancerVault = "0xBA12222222228d8Ba445958a75a0704d566BF2C8";
    const aavePool = "0x794a61358D6845594F94dc1DB02A252b5b4814aD";
    const quickswapRouter = "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff";
    const sushiswapRouter = "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506";
    const uniswapV3Router = "0xE592427A0AEce92De3Edee1F18E0157C05861564";
    const minProfitWei = ethers.parseEther("0.01"); // 0.01 MATIC

    const FlashArbExecutorV2 = await ethers.getContractFactory("FlashArbExecutorV2");
    const flashArb = await FlashArbExecutorV2.deploy(
        balancerVault,
        aavePool,
        quickswapRouter,
        sushiswapRouter,
        uniswapV3Router,
        minProfitWei
    );

    await flashArb.waitForDeployment();
    const address = await flashArb.getAddress();

    console.log("FlashArbExecutorV2 deployed to:", address);
    console.log("Owner:", await flashArb.owner());
    console.log("Min Profit Wei:", (await flashArb.minProfitWei()).toString());

    // Verify on Polygonscan
    console.log("\nVerification command:");
    console.log(`npx hardhat verify --network polygon ${address} "${balancerVault}" "${aavePool}" "${quickswapRouter}" "${sushiswapRouter}" "${uniswapV3Router}" "${minProfitWei}"`);
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });
```

---

## Post-Deployment Configuration

### 1. Verify Contract on Etherscan

```bash
npx hardhat verify --network polygon <CONTRACT_ADDRESS> \
    "0xBA12222222228d8Ba445958a75a0704d566BF2C8" \
    "0x794a61358D6845594F94dc1DB02A252b5b4814aD" \
    "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff" \
    "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506" \
    "0xE592427A0AEce92De3Edee1F18E0157C05861564" \
    "10000000000000000"
```

### 2. Configure Additional DEX Routers (Optional)

```javascript
// If you want to add more DEX routers
await flashArb.setDexRouter(4, CURVE_ROUTER_ADDRESS);
await flashArb.setDexRouter(5, BALANCER_ROUTER_ADDRESS);
```

### 3. Set Initial Parameters

```javascript
// Adjust minimum profit if needed
await flashArb.setMinProfit(ethers.parseEther("0.02")); // 0.02 MATIC

// Contract starts unpaused, but you can pause if needed
await flashArb.setPaused(false);
```

---

## Execution Example

### Build an Arbitrage Plan

```javascript
// Plan encoding example
function buildArbPlan(steps) {
    // Header (60 bytes)
    const version = 1;
    const deadline = Math.floor(Date.now() / 1000) + 3600; // 1 hour from now
    const minProfit = ethers.parseEther("0.01");
    const stepCount = steps.length;

    let plan = ethers.solidityPacked(
        ["uint8", "uint8", "uint40", "address", "uint256", "uint8"],
        [version, 0, deadline, ethers.ZeroAddress, minProfit, stepCount]
    );

    // Add each step (108 + auxLen bytes each)
    for (const step of steps) {
        const stepData = ethers.solidityPacked(
            ["uint8", "uint8", "address", "address", "uint256", "uint256", "uint16"],
            [
                step.dexId,
                step.action,
                step.tokenIn,
                step.tokenOut,
                step.amountIn,
                step.minOut,
                step.auxData.length
            ]
        );
        plan = ethers.concat([plan, stepData, step.auxData]);
    }

    return plan;
}

// Example: USDC -> WETH -> USDC arbitrage
const steps = [
    {
        dexId: 1, // QuickSwap
        action: 0,
        tokenIn: USDC_ADDRESS,
        tokenOut: WETH_ADDRESS,
        amountIn: 0, // Use full balance
        minOut: ethers.parseEther("0.09"), // Minimum WETH out
        auxData: ethers.AbiCoder.defaultAbiCoder().encode(
            ["address[]"],
            [[USDC_ADDRESS, WETH_ADDRESS]]
        )
    },
    {
        dexId: 2, // SushiSwap
        action: 0,
        tokenIn: WETH_ADDRESS,
        tokenOut: USDC_ADDRESS,
        amountIn: 0, // Use full balance
        minOut: ethers.parseUnits("101", 6), // Minimum USDC out (profit)
        auxData: ethers.AbiCoder.defaultAbiCoder().encode(
            ["address[]"],
            [[WETH_ADDRESS, USDC_ADDRESS]]
        )
    }
];

const plan = buildArbPlan(steps);
```

### Execute Arbitrage

```javascript
// Execute with Balancer flash loan
await flashArb.executeFlashArb(
    1, // PROVIDER_BALANCER
    USDC_ADDRESS,
    ethers.parseUnits("100", 6), // Borrow 100 USDC
    plan
);

// Or execute with Aave flash loan
await flashArb.executeFlashArb(
    2, // PROVIDER_AAVE
    USDC_ADDRESS,
    ethers.parseUnits("100", 6), // Borrow 100 USDC
    plan
);
```

---

## Monitoring Setup

### Event Listeners

```javascript
// Listen for successful arbitrage
flashArb.on("ArbExecuted", (provider, loanToken, loanAmount, profit, event) => {
    console.log("Arbitrage executed!");
    console.log("Provider:", provider === 1 ? "Balancer" : "Aave");
    console.log("Loan Token:", loanToken);
    console.log("Loan Amount:", ethers.formatUnits(loanAmount, 6));
    console.log("Profit:", ethers.formatUnits(profit, 6));
    console.log("Tx Hash:", event.transactionHash);
});

// Listen for step execution
flashArb.on("StepExecuted", (stepIndex, dexId, tokenIn, tokenOut, amountIn, amountOut) => {
    console.log(`Step ${stepIndex}: ${getDexName(dexId)}`);
    console.log(`  In: ${ethers.formatUnits(amountIn, 18)} of ${tokenIn}`);
    console.log(`  Out: ${ethers.formatUnits(amountOut, 18)} of ${tokenOut}`);
});
```

### Health Checks

```javascript
// Periodic health check
async function healthCheck() {
    const paused = await flashArb.paused();
    const minProfit = await flashArb.minProfitWei();
    const owner = await flashArb.owner();

    console.log("Contract Health:");
    console.log("  Paused:", paused);
    console.log("  Min Profit:", ethers.formatEther(minProfit), "MATIC");
    console.log("  Owner:", owner);

    // Check DEX routers
    for (let i = 1; i <= 3; i++) {
        const router = await flashArb.dexRouter(i);
        console.log(`  DEX ${i} Router:`, router);
    }
}

// Run every 5 minutes
setInterval(healthCheck, 5 * 60 * 1000);
```

---

## Emergency Procedures

### Pause Contract

```javascript
// In case of emergency, pause the contract
await flashArb.setPaused(true);
console.log("Contract paused!");
```

### Withdraw Stuck Tokens

```javascript
// If tokens get stuck in the contract
await flashArb.withdrawAllToken(TOKEN_ADDRESS);
console.log("Tokens withdrawn!");
```

### Rescue ETH/MATIC

```javascript
// If native currency gets stuck
await flashArb.rescueETH();
console.log("ETH/MATIC rescued!");
```

---

## Gas Optimization Tips

### 1. Batch Operations
- Execute multiple arbitrages in sequence when gas is low
- Monitor gas prices and pause during high-fee periods

### 2. Efficient Plans
- Minimize step count (2-3 hops ideal)
- Use direct token pairs when possible
- Avoid unnecessary intermediate tokens

### 3. Smart Timing
- Execute during off-peak hours
- Monitor mempool for opportunities
- Use MEV protection (private RPC)

---

## Security Best Practices

### 1. Key Management
- Use hardware wallet for owner key
- Consider multi-sig for high-value deployments
- Never share private keys

### 2. Testing
- Always test on testnet first
- Start with small amounts on mainnet
- Gradually scale up operations

### 3. Monitoring
- Set up 24/7 monitoring
- Configure alerts for failures
- Track all transactions

### 4. Regular Audits
- Review contract state monthly
- Check router addresses
- Verify profit thresholds

---

## Troubleshooting

### Common Errors

#### `NotOwner()`
**Cause:** Transaction not sent by owner  
**Solution:** Use owner account

#### `Paused()`
**Cause:** Contract is paused  
**Solution:** Unpause with `setPaused(false)`

#### `InvalidPlan()`
**Cause:** Malformed plan data  
**Solution:** Verify plan encoding

#### `ProfitTooLow(got, need)`
**Cause:** Arbitrage not profitable enough  
**Solution:** Adjust minOut or skip opportunity

#### `InsufficientRepayment()`
**Cause:** Not enough tokens to repay flash loan  
**Solution:** Verify swap routes and slippage

#### `DeadlineExpired()`
**Cause:** Plan deadline passed  
**Solution:** Create fresh plan with future deadline

---

## Performance Benchmarks

### Typical Gas Costs (Polygon)

| Operation | Gas Used | Cost @ 100 Gwei |
|-----------|----------|-----------------|
| Deploy V2 | ~520,000 | ~0.052 MATIC |
| 2-hop Arb (Balancer) | ~300,000 | ~0.030 MATIC |
| 2-hop Arb (Aave) | ~280,000 | ~0.028 MATIC |
| 3-hop Arb | ~450,000 | ~0.045 MATIC |
| Config Update | ~40,000 | ~0.004 MATIC |

### Break-Even Analysis

For profitable arbitrage on Polygon:
- Gas cost: ~0.03 MATIC (~$0.03 @ $1/MATIC)
- Flash loan fee (Balancer): 0%
- Flash loan fee (Aave): 0.05%
- Minimum profit needed: > 0.05% + gas costs

---

## Upgrade Path

### To Deploy New Version
1. Deploy new contract
2. Pause old contract
3. Withdraw all funds from old contract
4. Update off-chain systems to use new address
5. Monitor new contract for 24-48 hours

### Version History
- **V1:** Original with basic features
- **V2:** Enhanced with reentrancy guards, pause, limits ✅ CURRENT

---

## Support & Resources

### Documentation
- [Verification Report](./FLASHARBEXECUTOR_VERIFICATION_REPORT.md)
- [Security Improvements](./SECURITY_IMPROVEMENTS.md)
- [Mainnet Readiness](./MAINNET_READINESS_FINAL.md)

### External Resources
- Balancer V2 Docs: https://docs.balancer.fi/
- Aave V3 Docs: https://docs.aave.com/
- Uniswap V2 Docs: https://docs.uniswap.org/
- Uniswap V3 Docs: https://docs.uniswap.org/

---

## Checklist

### Pre-Deployment ✅
- [x] Contract code reviewed
- [x] Tests created and passing
- [x] Security analysis completed
- [ ] Professional audit completed
- [ ] Testnet deployment successful
- [ ] All addresses verified

### Deployment Day ✅
- [ ] Deploy to mainnet
- [ ] Verify on block explorer
- [ ] Configure parameters
- [ ] Test with small amount
- [ ] Set up monitoring
- [ ] Document contract address

### Post-Deployment ✅
- [ ] Monitor first 24 hours
- [ ] Track all transactions
- [ ] Review gas costs
- [ ] Adjust parameters as needed
- [ ] Scale gradually
- [ ] Regular health checks

---

**Last Updated:** 2025-12-27  
**Version:** 1.0  
**Maintainer:** Development Team
