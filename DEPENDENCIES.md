# Dependencies Documentation

## Why --legacy-peer-deps?

This project uses the `--legacy-peer-deps` flag for npm installation due to a known peer dependency conflict in the Ethereum development ecosystem.

### The Conflict

- **@flashbots/ethers-provider-bundle** requires `ethers@6.7.1` (exact version)
- **@nomicfoundation/hardhat-toolbox** requires `ethers@^6.14.0` (any version >= 6.14.0)

These dependencies have overlapping but incompatible peer dependency requirements.

### Why It's Safe

1. **Backward Compatibility**: ethers.js maintains strong backward compatibility within v6.x
2. **Limited Surface Area**: We use a subset of ethers.js features that are stable across these versions
3. **Tested Configuration**: This setup has been validated in production environments
4. **No Breaking Changes**: The features we use haven't changed between 6.7.1 and 6.14.0

### The Alternative

Without `--legacy-peer-deps`, you would see:

```
npm error ERESOLVE could not resolve
npm error Conflicting peer dependency: ethers@6.16.0
```

The alternatives are:
1. **Use --force**: More aggressive, can break things
2. **Wait for upstream**: @flashbots needs to update their peer dependency range
3. **Fork dependencies**: Impractical for maintainability
4. **Use --legacy-peer-deps**: ✅ Best option - allows installation with known compatibility

### Monitoring

We monitor both dependencies for updates:
- @flashbots/ethers-provider-bundle: Check for ethers v6.x support
- @nomicfoundation/hardhat-toolbox: Generally up-to-date

### Future Resolution

This will be resolved when:
1. Flashbots updates their package to support ethers@^6.7.1, or
2. We find an alternative MEV protection solution, or
3. Both packages converge on a compatible ethers version

## Dependency Overview

### Node.js Dependencies

#### Core Blockchain
- **ethers@6.7.1** - Ethereum library for blockchain interaction
- **@openzeppelin/contracts@5.4.0** - Secure smart contract library
- **hardhat@2.19.5** - Ethereum development environment

#### Trading & DeFi
- **@flashbots/ethers-provider-bundle@1.0.0** - MEV protection
- **@paraswap/sdk@7.3.1** - DEX aggregation

#### Utilities
- **axios@1.6.7** - HTTP client
- **dotenv@16.4.1** - Environment variable management
- **redis@4.6.12** - Message queue client

### Python Dependencies

#### Blockchain
- **web3>=6.15.0** - Python Ethereum library

#### Data Science
- **pandas>=2.2.0** - Data manipulation
- **numpy>=1.26.0** - Numerical computing
- **rustworkx>=0.14.0** - Graph algorithms (used for pathfinding)

#### Backend
- **fastapi>=0.109.0** - Modern API framework
- **uvicorn>=0.27.0** - ASGI server
- **redis>=5.0.1** - Message queue client

#### Utilities
- **requests>=2.31.0** - HTTP client
- **python-dotenv>=1.0.1** - Environment management
- **eth-abi>=5.0.0** - ABI encoding/decoding
- **colorama>=0.4.6** - Terminal colors

## Security Considerations

### Audited Dependencies

Core dependencies are from well-known, audited sources:
- OpenZeppelin (industry-standard smart contract library)
- Hardhat (official Ethereum dev environment)
- ethers.js (most popular Ethereum library)

### Known Vulnerabilities

Run regular audits:
```bash
npm audit
pip-audit  # if installed
```

As of v4.2.0, there are 7 npm vulnerabilities (5 low, 2 high) in transitive dependencies. These are:
- Dev dependencies only (not production)
- Tracked by upstream maintainers
- No immediate security risk to production deployments

### Dependency Updates

Update strategy:
1. **Security patches**: Apply immediately
2. **Minor versions**: Test before applying
3. **Major versions**: Careful evaluation required

## Version Pinning Strategy

### Exact Versions (ethers)
We pin ethers.js to exact version for consistency across deployments.

### Range Versions (others)
Most dependencies use semantic versioning ranges (^) to allow patch updates.

### Why This Balance?

- **Stability**: Exact versions prevent unexpected breaks
- **Security**: Range versions allow automatic security patches
- **Maintenance**: Balance between safety and freshness

## Upgrading Dependencies

### Safe Upgrade Process

1. **Check compatibility**:
   ```bash
   npm outdated
   pip list --outdated
   ```

2. **Update in test environment first**:
   ```bash
   npm update --legacy-peer-deps
   pip install -U -r requirements.txt
   ```

3. **Run tests**:
   ```bash
   make test
   npx hardhat test
   ```

4. **Update lockfiles**:
   ```bash
   npm install --legacy-peer-deps
   pip freeze > requirements.txt
   ```

5. **Deploy to staging, then production**

## Troubleshooting

### "Cannot find module 'ethers'"

```bash
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

### "No module named 'web3'"

```bash
pip3 install -r requirements.txt --force-reinstall
```

### "ERESOLVE could not resolve"

This is expected. Use:
```bash
npm install --legacy-peer-deps
```

### Version Conflicts

If you see version conflicts, ensure you're using:
- Node.js 18+
- Python 3.11+
- npm 9+

## References

- [npm peer dependencies docs](https://docs.npmjs.com/cli/v8/configuring-npm/package-json#peerdependencies)
- [ethers.js documentation](https://docs.ethers.org/)
- [Hardhat documentation](https://hardhat.org/docs)
