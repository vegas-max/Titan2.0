require("@nomicfoundation/hardhat-toolbox");

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
    },
  },
  paths: {
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts",
  },
  networks: {
    hardhat: {
      chainId: 1337,
    },
    mainnet: {
      chainId: 1,
      url: process.env.MAINNET_RPC_URL || "",
    },
    polygon: {
      chainId: 137,
      url: process.env.POLYGON_RPC_URL || "",
    },
  },
};
