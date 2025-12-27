const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("FlashArbExecutor - End to End Verification", function () {
  let flashArbExecutor;
  let owner;
  let notOwner;
  let mockBalancerVault;
  let mockAavePool;
  let mockQuickswapRouter;
  let mockSushiswapRouter;
  let mockUniswapV3Router;
  let mockToken;
  
  const PROVIDER_BALANCER = 1;
  const PROVIDER_AAVE = 2;
  const DEX_UNIV2_QUICKSWAP = 1;
  const DEX_UNIV2_SUSHISWAP = 2;
  const DEX_UNIV3 = 3;
  
  beforeEach(async function () {
    [owner, notOwner] = await ethers.getSigners();
    
    // Deploy mock contracts
    const MockERC20 = await ethers.getContractFactory("MockERC20");
    mockToken = await MockERC20.deploy("Mock Token", "MOCK", ethers.parseEther("1000000"));
    
    const MockBalancerVault = await ethers.getContractFactory("MockBalancerVault");
    mockBalancerVault = await MockBalancerVault.deploy();
    
    const MockAavePool = await ethers.getContractFactory("MockAavePool");
    mockAavePool = await MockAavePool.deploy();
    
    const MockUniswapV2Router = await ethers.getContractFactory("MockUniswapV2Router");
    mockQuickswapRouter = await MockUniswapV2Router.deploy();
    mockSushiswapRouter = await MockUniswapV2Router.deploy();
    
    const MockUniswapV3Router = await ethers.getContractFactory("MockUniswapV3Router");
    mockUniswapV3Router = await MockUniswapV3Router.deploy();
    
    // Deploy FlashArbExecutor
    const FlashArbExecutor = await ethers.getContractFactory("FlashArbExecutor");
    flashArbExecutor = await FlashArbExecutor.deploy(
      await mockBalancerVault.getAddress(),
      await mockAavePool.getAddress(),
      await mockQuickswapRouter.getAddress(),
      await mockSushiswapRouter.getAddress(),
      await mockUniswapV3Router.getAddress(),
      ethers.parseEther("0.01") // minProfitWei
    );
  });
  
  describe("1. Constructor & Immutables", function () {
    it("should set owner correctly", async function () {
      expect(await flashArbExecutor.owner()).to.equal(owner.address);
    });
    
    it("should set balancerVault correctly", async function () {
      expect(await flashArbExecutor.balancerVault()).to.equal(await mockBalancerVault.getAddress());
    });
    
    it("should set aavePool correctly", async function () {
      expect(await flashArbExecutor.aavePool()).to.equal(await mockAavePool.getAddress());
    });
    
    it("should set DEX routers correctly", async function () {
      expect(await flashArbExecutor.dexRouter(DEX_UNIV2_QUICKSWAP)).to.equal(await mockQuickswapRouter.getAddress());
      expect(await flashArbExecutor.dexRouter(DEX_UNIV2_SUSHISWAP)).to.equal(await mockSushiswapRouter.getAddress());
      expect(await flashArbExecutor.dexRouter(DEX_UNIV3)).to.equal(await mockUniswapV3Router.getAddress());
    });
    
    it("should set minProfitWei correctly", async function () {
      expect(await flashArbExecutor.minProfitWei()).to.equal(ethers.parseEther("0.01"));
    });
  });
  
  describe("2. Access Control", function () {
    it("should allow owner to call executeFlashArb", async function () {
      const plan = createMockPlan(1, 0); // Valid plan with 1 step
      await expect(
        flashArbExecutor.executeFlashArb(
          PROVIDER_BALANCER,
          await mockToken.getAddress(),
          ethers.parseEther("100"),
          plan
        )
      ).to.not.be.revertedWithCustomError(flashArbExecutor, "NotOwner");
    });
    
    it("should revert when non-owner calls executeFlashArb", async function () {
      const plan = createMockPlan(1, 0);
      await expect(
        flashArbExecutor.connect(notOwner).executeFlashArb(
          PROVIDER_BALANCER,
          await mockToken.getAddress(),
          ethers.parseEther("100"),
          plan
        )
      ).to.be.revertedWithCustomError(flashArbExecutor, "NotOwner");
    });
    
    it("should allow owner to call admin functions", async function () {
      await expect(flashArbExecutor.setMinProfit(ethers.parseEther("0.02"))).to.not.be.reverted;
      await expect(flashArbExecutor.setDexRouter(4, owner.address)).to.not.be.reverted;
    });
    
    it("should revert when non-owner calls admin functions", async function () {
      await expect(
        flashArbExecutor.connect(notOwner).setMinProfit(ethers.parseEther("0.02"))
      ).to.be.revertedWithCustomError(flashArbExecutor, "NotOwner");
      
      await expect(
        flashArbExecutor.connect(notOwner).setDexRouter(4, owner.address)
      ).to.be.revertedWithCustomError(flashArbExecutor, "NotOwner");
    });
  });
  
  describe("3. Plan Validation", function () {
    it("should revert with InvalidPlan for plan shorter than 60 bytes", async function () {
      const shortPlan = "0x" + "00".repeat(59);
      await expect(
        flashArbExecutor.executeFlashArb(
          PROVIDER_BALANCER,
          await mockToken.getAddress(),
          ethers.parseEther("100"),
          shortPlan
        )
      ).to.be.revertedWithCustomError(flashArbExecutor, "InvalidPlan");
    });
    
    it("should accept plan with exactly 60 bytes", async function () {
      const validPlan = createMockPlan(0, 0); // 0 steps, but valid header
      await expect(
        flashArbExecutor.executeFlashArb(
          PROVIDER_BALANCER,
          await mockToken.getAddress(),
          ethers.parseEther("100"),
          validPlan
        )
      ).to.not.be.revertedWithCustomError(flashArbExecutor, "InvalidPlan");
    });
  });
  
  describe("4. Flash Loan Provider Validation", function () {
    it("should accept PROVIDER_BALANCER (1)", async function () {
      const plan = createMockPlan(0, 0);
      await expect(
        flashArbExecutor.executeFlashArb(
          PROVIDER_BALANCER,
          await mockToken.getAddress(),
          ethers.parseEther("100"),
          plan
        )
      ).to.not.be.revertedWithCustomError(flashArbExecutor, "InvalidProvider");
    });
    
    it("should accept PROVIDER_AAVE (2)", async function () {
      const plan = createMockPlan(0, 0);
      await expect(
        flashArbExecutor.executeFlashArb(
          PROVIDER_AAVE,
          await mockToken.getAddress(),
          ethers.parseEther("100"),
          plan
        )
      ).to.not.be.revertedWithCustomError(flashArbExecutor, "InvalidProvider");
    });
    
    it("should revert with InvalidProvider for invalid provider", async function () {
      const plan = createMockPlan(0, 0);
      await expect(
        flashArbExecutor.executeFlashArb(
          3, // Invalid provider
          await mockToken.getAddress(),
          ethers.parseEther("100"),
          plan
        )
      ).to.be.revertedWithCustomError(flashArbExecutor, "InvalidProvider");
    });
  });
  
  describe("5. Flash Loan Callback Security", function () {
    it("receiveFlashLoan should revert if not called by balancerVault", async function () {
      const tokens = [await mockToken.getAddress()];
      const amounts = [ethers.parseEther("100")];
      const feeAmounts = [ethers.parseEther("0.01")];
      const userData = "0x";
      
      await expect(
        flashArbExecutor.receiveFlashLoan(tokens, amounts, feeAmounts, userData)
      ).to.be.revertedWithCustomError(flashArbExecutor, "NotVault");
    });
    
    it("executeOperation should revert if not called by aavePool", async function () {
      await expect(
        flashArbExecutor.executeOperation(
          await mockToken.getAddress(),
          ethers.parseEther("100"),
          ethers.parseEther("0.01"),
          flashArbExecutor.target,
          "0x"
        )
      ).to.be.revertedWithCustomError(flashArbExecutor, "NotPool");
    });
  });
  
  describe("6. Admin Functions", function () {
    it("should allow owner to set minProfit", async function () {
      const newMinProfit = ethers.parseEther("0.05");
      await flashArbExecutor.setMinProfit(newMinProfit);
      expect(await flashArbExecutor.minProfitWei()).to.equal(newMinProfit);
    });
    
    it("should allow owner to set DEX router", async function () {
      const newRouter = notOwner.address;
      await flashArbExecutor.setDexRouter(4, newRouter);
      expect(await flashArbExecutor.dexRouter(4)).to.equal(newRouter);
    });
    
    it("should allow owner to withdraw tokens", async function () {
      // Send tokens to contract
      await mockToken.transfer(flashArbExecutor.target, ethers.parseEther("10"));
      
      const initialBalance = await mockToken.balanceOf(owner.address);
      await flashArbExecutor.withdrawToken(await mockToken.getAddress(), ethers.parseEther("5"));
      const finalBalance = await mockToken.balanceOf(owner.address);
      
      expect(finalBalance - initialBalance).to.equal(ethers.parseEther("5"));
    });
    
    it("should allow owner to withdraw all tokens", async function () {
      // Send tokens to contract
      const amount = ethers.parseEther("10");
      await mockToken.transfer(flashArbExecutor.target, amount);
      
      const initialBalance = await mockToken.balanceOf(owner.address);
      await flashArbExecutor.withdrawAllToken(await mockToken.getAddress());
      const finalBalance = await mockToken.balanceOf(owner.address);
      
      expect(finalBalance - initialBalance).to.equal(amount);
    });
    
    it("should allow owner to rescue ETH", async function () {
      // Send ETH to contract
      await owner.sendTransaction({
        to: flashArbExecutor.target,
        value: ethers.parseEther("1")
      });
      
      const initialBalance = await ethers.provider.getBalance(owner.address);
      const tx = await flashArbExecutor.rescueETH();
      const receipt = await tx.wait();
      const gasUsed = receipt.gasUsed * receipt.gasPrice;
      const finalBalance = await ethers.provider.getBalance(owner.address);
      
      expect(finalBalance + gasUsed - initialBalance).to.be.closeTo(ethers.parseEther("1"), ethers.parseEther("0.001"));
    });
  });
  
  describe("7. Event Emissions", function () {
    // Event tests would be more comprehensive with proper mock implementations
    // that trigger the actual callbacks
  });
  
  describe("8. Edge Cases", function () {
    it("should handle receive() function for native currency", async function () {
      await expect(
        owner.sendTransaction({
          to: flashArbExecutor.target,
          value: ethers.parseEther("1")
        })
      ).to.not.be.reverted;
    });
  });
  
  // Helper function to create mock plan data
  function createMockPlan(stepCount, deadline) {
    // Plan format (CORRECTED to match contract validation):
    // [0]: version (1 byte)
    // [1]: reserved (1 byte)
    // [2-6]: deadline (5 bytes for uint40)
    // [7-26]: baseToken (20 bytes)
    // [27-58]: minProfit (32 bytes)
    // [59]: stepCount (1 byte)
    // Total: 60 bytes header (minimum required by contract)
    
    const version = "01";
    const reserved = "00"; // 1 byte padding
    const deadlineHex = deadline.toString(16).padStart(10, "0"); // 5 bytes for uint40
    const baseToken = ethers.ZeroAddress.slice(2).padStart(40, "0"); // 20 bytes
    const minProfit = ethers.parseEther("0.01").toString(16).padStart(64, "0"); // 32 bytes
    const stepCountHex = stepCount.toString(16).padStart(2, "0"); // 1 byte
    
    return "0x" + version + reserved + deadlineHex + baseToken + minProfit + stepCountHex;
  }
});

// Mock contract factories would be implemented here
// These are simplified versions for testing
