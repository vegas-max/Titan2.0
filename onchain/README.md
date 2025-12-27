# On-Chain System Components

This directory contains all blockchain-executable smart contracts and deployment infrastructure.

## Structure

```
onchain/
├── contracts/           # Solidity smart contracts
│   ├── OmniArbExecutor.sol      # Main arbitrage executor
│   ├── FlashArbExecutor.sol     # Flash arbitrage executor (V1)
│   ├── FlashArbExecutorV2.sol   # Flash arbitrage executor (V2)
│   ├── OmniArbDecoder.sol       # Route decoding utilities
│   ├── interfaces/              # Contract interfaces
│   │   ├── IAaveV3.sol          # Aave V3 flash loan interface
│   │   ├── IB3.sol              # Balancer V3 interface
│   │   ├── IUniV2.sol           # Uniswap V2 interface
│   │   ├── IUniV3.sol           # Uniswap V3 interface
│   │   └── ICurve.sol           # Curve pool interface
│   ├── modules/                 # Reusable contract modules
│   │   └── SwapHandler.sol      # Universal swap execution
│   └── mocks/                   # Test contract mocks
├── scripts/             # Deployment and setup scripts
│   ├── deploy.js                # Main deployment script
│   ├── deployFlashArbExecutor.js # Flash arb deployer
│   ├── setupTokenRegistry.js    # Token registry setup
│   └── configureTokenRanks.js   # Token ranking configuration
└── test/                # Contract tests (Hardhat)
    ├── FlashArbExecutor.test.js # Flash executor tests
    ├── OmniArbDecoder.test.js   # Decoder tests
    └── test_route_encoding.js   # Route encoding tests
```

## Smart Contracts

### OmniArbExecutor
The core smart contract that orchestrates flash loan arbitrage:
- **Flash Loan Sources**: Balancer V3 (0% fee), Aave V3 (0.05-0.09% fee)
- **Route Engine**: Multi-hop swap execution across DEXs
- **Protocol Support**: UniV2, UniV3, Curve
- **Security**: Owner-only execution, SafeERC20, validation checks

### FlashArbExecutor (V1 & V2)
Simplified flash arbitrage executors with:
- Gas-optimized execution paths
- Multi-DEX support (QuickSwap, SushiSwap, Uniswap V3)
- Profit verification and repayment

### SwapHandler Module
Reusable swap execution primitive supporting:
- UniV2-style routers (QuickSwap, SushiSwap, etc.)
- UniV3 routers with fee tiers
- Curve pools with exchange indices

## Deployment

Deploy contracts to any supported network:

```bash
# Compile contracts
npm run compile

# Deploy to Polygon
npm run deploy:polygon

# Deploy to Arbitrum
npm run deploy:arbitrum

# Deploy Flash Arb Executor
npm run deploy:flasharb:polygon
```

## Testing

Run contract tests:

```bash
# Run all tests
npx hardhat test

# Run specific test
npx hardhat test onchain/test/FlashArbExecutor.test.js

# Test with gas reporting
REPORT_GAS=true npx hardhat test
```

## Configuration

Update `hardhat.config.js` at the project root to:
- Add new networks
- Configure compiler settings
- Set up verification keys

## Gas Optimization

Contracts are optimized for gas efficiency:
- **Compiler Optimization**: 200 runs
- **Via IR**: Enabled for complex routes
- **Minimal Storage**: No persistent state beyond addresses
- **Efficient Encoding**: ABI-encoded routes for minimal calldata

## Security Features

1. **Owner-only execution**: Only contract owner can trigger arbitrage
2. **Flash loan callback authentication**: Validates msg.sender
3. **SafeERC20 usage**: Prevents approval/transfer failures
4. **Zero-amount checks**: Validates swap outputs
5. **Route length limits**: Maximum 5 hops to prevent gas exhaustion

## Documentation

- [SystemArchitecture.md](contracts/SystemArchitecture.md) - System design overview
- [RouteEncodingSpec.md](contracts/RouteEncodingSpec.md) - Route encoding specification
- [DEPLOYMENT_GUIDE.md](contracts/DEPLOYMENT_GUIDE.md) - Deployment instructions
