const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

/**
 * FlashArbExecutor Deployment Script
 * 
 * This script deploys the FlashArbExecutor contract to the specified network
 * with the correct flash loan provider addresses and DEX router addresses.
 */

// Network-specific configuration from config.json
const config = require("../config.json");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  const network = hre.network.name;
  
  console.log("\n===========================================");
  console.log("🚀 FLASH ARB EXECUTOR DEPLOYMENT");
  console.log("===========================================\n");
  console.log("Deploying to network:", network);
  console.log("Deploying from account:", deployer.address);
  console.log("Account balance:", hre.ethers.formatEther(await hre.ethers.provider.getBalance(deployer.address)), "ETH\n");

  // Get network configuration
  let networkConfig;
  let dexConfig;
  let minProfitWei;

  if (network === "polygon" || network === "hardhat") {
    networkConfig = config.networks.polygon;
    minProfitWei = hre.ethers.parseEther("5"); // 5 MATIC minimum profit
    
    // Get DEX addresses for Polygon
    const quickswapRouter = config.dex_endpoints.quickswap.polygon.router_v2;
    const sushiswapRouter = config.dex_endpoints.sushiswap.polygon.router;
    const uniswapV3Router = config.dex_endpoints.uniswap_v3.polygon.router;
    
    dexConfig = {
      quickswap: quickswapRouter,
      sushiswap: sushiswapRouter,
      uniswapV3: uniswapV3Router
    };
    
  } else if (network === "ethereum") {
    networkConfig = config.networks.ethereum;
    minProfitWei = hre.ethers.parseEther("0.002"); // 0.002 ETH minimum profit
    
    // Get DEX addresses for Ethereum
    const sushiswapRouter = config.dex_endpoints.sushiswap.ethereum.router;
    const uniswapV3Router = config.dex_endpoints.uniswap_v3.ethereum.router;
    
    dexConfig = {
      quickswap: hre.ethers.ZeroAddress, // Not available on Ethereum
      sushiswap: sushiswapRouter,
      uniswapV3: uniswapV3Router
    };
    
  } else if (network === "arbitrum") {
    networkConfig = config.networks.arbitrum;
    minProfitWei = hre.ethers.parseEther("0.002"); // 0.002 ETH minimum profit
    
    // Arbitrum DEX addresses (would need to be added to config.json)
    dexConfig = {
      quickswap: hre.ethers.ZeroAddress,
      sushiswap: "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506", // SushiSwap on Arbitrum
      uniswapV3: "0xE592427A0AEce92De3Edee1F18E0157C05861564" // Uniswap V3 on Arbitrum
    };
    
  } else {
    throw new Error(`Network ${network} not supported yet. Please add configuration.`);
  }

  console.log("Network Configuration:");
  console.log("  Chain ID:", networkConfig.chainId);
  console.log("  Balancer Vault:", networkConfig.flashloan_providers.balancer);
  console.log("  Aave Pool:", networkConfig.flashloan_providers.aave);
  console.log("\nDEX Routers:");
  console.log("  QuickSwap:", dexConfig.quickswap);
  console.log("  SushiSwap:", dexConfig.sushiswap);
  console.log("  Uniswap V3:", dexConfig.uniswapV3);
  console.log("\nMinimum Profit:", hre.ethers.formatEther(minProfitWei), networkConfig.currency, "\n");

  // Deploy FlashArbExecutor
  console.log("📝 Deploying FlashArbExecutor contract...\n");

  const FlashArbExecutor = await hre.ethers.getContractFactory("FlashArbExecutor");
  const flashArbExecutor = await FlashArbExecutor.deploy(
    networkConfig.flashloan_providers.balancer,
    networkConfig.flashloan_providers.aave,
    dexConfig.quickswap,
    dexConfig.sushiswap,
    dexConfig.uniswapV3,
    minProfitWei
  );

  await flashArbExecutor.waitForDeployment();
  const contractAddress = await flashArbExecutor.getAddress();

  console.log("✅ FlashArbExecutor deployed to:", contractAddress);
  console.log("   Owner:", deployer.address);
  console.log("   Transaction hash:", flashArbExecutor.deploymentTransaction().hash);
  console.log("\n===========================================");
  console.log("📋 DEPLOYMENT SUMMARY");
  console.log("===========================================\n");

  const deploymentInfo = {
    network: network,
    chainId: networkConfig.chainId,
    contractAddress: contractAddress,
    owner: deployer.address,
    deploymentTx: flashArbExecutor.deploymentTransaction().hash,
    timestamp: new Date().toISOString(),
    config: {
      balancerVault: networkConfig.flashloan_providers.balancer,
      aavePool: networkConfig.flashloan_providers.aave,
      quickswapRouter: dexConfig.quickswap,
      sushiswapRouter: dexConfig.sushiswap,
      uniswapV3Router: dexConfig.uniswapV3,
      minProfitWei: minProfitWei.toString()
    }
  };

  console.log(JSON.stringify(deploymentInfo, null, 2));

  // Save deployment info
  const deploymentsDir = path.join(__dirname, "../deployments");
  if (!fs.existsSync(deploymentsDir)) {
    fs.mkdirSync(deploymentsDir);
  }

  const deploymentFile = path.join(deploymentsDir, `FlashArbExecutor-${network}.json`);
  fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));
  console.log(`\n💾 Deployment info saved to: ${deploymentFile}`);

  console.log("\n===========================================");
  console.log("🔧 NEXT STEPS");
  console.log("===========================================\n");
  console.log(`1. Update your .env file with:`);
  console.log(`   FLASH_ARB_EXECUTOR_${network.toUpperCase()}=${contractAddress}\n`);
  console.log(`2. Fund the contract owner wallet (${deployer.address}) with:`);
  console.log(`   - Gas tokens (${networkConfig.currency})`);
  console.log(`   - Trading tokens (USDC, USDT, etc.)\n`);
  console.log(`3. Verify the contract on ${networkConfig.explorer}:`);
  if (network !== "hardhat") {
    console.log(`   npx hardhat verify --network ${network} ${contractAddress} \\`);
    console.log(`     "${networkConfig.flashloan_providers.balancer}" \\`);
    console.log(`     "${networkConfig.flashloan_providers.aave}" \\`);
    console.log(`     "${dexConfig.quickswap}" \\`);
    console.log(`     "${dexConfig.sushiswap}" \\`);
    console.log(`     "${dexConfig.uniswapV3}" \\`);
    console.log(`     "${minProfitWei}"\n`);
  }
  console.log(`4. Test the contract with a small arbitrage opportunity\n`);
  console.log("===========================================\n");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("\n❌ Deployment failed:");
    console.error(error);
    process.exit(1);
  });
