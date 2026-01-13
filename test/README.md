# Test Suite

## Overview

The `test` directory contains test files for validating Titan system components. These tests ensure the arbitrage engine, flash loan enforcement, and other critical components work correctly.

## Purpose

This test suite provides:
- **Unit tests** for individual components
- **Integration tests** for component interactions
- **Functional tests** for end-to-end workflows
- **Validation** of critical system behaviors

## Project Structure

```
test/
├── ArbitrageEngine.test.js                # Arbitrage engine unit tests
├── arbitrage_engine_standalone_test.js    # Standalone engine tests
├── test_flash_loan_enforcement.js         # Flash loan validation tests
└── README.md                              # This file
```

## Test Files

### ArbitrageEngine.test.js

Comprehensive test suite for the arbitrage engine:
- Opportunity detection tests
- Profit calculation validation
- Execution logic verification
- Error handling tests

### arbitrage_engine_standalone_test.js

Tests for the standalone arbitrage engine:
- Independent operation validation
- Configuration testing
- Integration pattern verification
- Performance benchmarks

### test_flash_loan_enforcement.js

Flash loan specific tests:
- Flash loan provider integration
- Loan size optimization
- Repayment validation
- Fee calculation accuracy

## Running Tests

### Prerequisites

- Node.js 18+
- All dependencies installed (`npm install`)
- Test environment configured

### Run All Tests

```bash
# From repository root
npm test

# Or directly with node
node test/ArbitrageEngine.test.js
node test/arbitrage_engine_standalone_test.js
node test/test_flash_loan_enforcement.js
```

### Run Specific Test File

```bash
node test/ArbitrageEngine.test.js
```

### Run with Verbose Output

```bash
NODE_ENV=test node test/ArbitrageEngine.test.js
```

## Test Categories

### 1. Unit Tests
Test individual functions and methods in isolation:
- Configuration loading
- Data validation
- Calculation accuracy
- Utility functions

### 2. Integration Tests
Test component interactions:
- RPC connectivity
- Smart contract calls
- Event handling
- Data flow between modules

### 3. Functional Tests  
Test complete workflows:
- Opportunity detection to execution
- Flash loan borrowing and repayment
- Profit extraction
- Error recovery

## Test Configuration

### Environment Variables

Create a `.env.test` file for test-specific configuration:

```env
# Test RPC endpoints (use testnet)
RPC_POLYGON_TEST=https://rpc-mumbai.maticvigil.com
RPC_ETHEREUM_TEST=https://goerli.infura.io/v3/YOUR_KEY

# Test wallet (never use mainnet keys!)
TEST_PRIVATE_KEY=0x...

# Test mode
TEST_MODE=true
NETWORK=testnet
```

### Test Data

Some tests use mock data for faster execution:
- Mock RPC responses
- Simulated blockchain state
- Predefined opportunity data

## Writing New Tests

### Test File Template

```javascript
// test/my_component.test.js

const assert = require('assert');
const MyComponent = require('../path/to/component');

describe('MyComponent', () => {
    let component;
    
    before(() => {
        // Setup
        component = new MyComponent(config);
    });
    
    after(() => {
        // Cleanup
        component.shutdown();
    });
    
    it('should perform expected behavior', async () => {
        const result = await component.someMethod();
        assert.strictEqual(result.success, true);
    });
    
    it('should handle errors gracefully', async () => {
        try {
            await component.methodThatFails();
            assert.fail('Should have thrown error');
        } catch (error) {
            assert.ok(error.message.includes('Expected error'));
        }
    });
});
```

### Best Practices

1. **Use descriptive test names** that explain what is being tested
2. **Test both success and failure cases**
3. **Mock external dependencies** (RPC, APIs) when possible
4. **Clean up resources** in `after()` hooks
5. **Use assertions** to validate expectations
6. **Keep tests independent** - don't rely on test execution order
7. **Use test data** that represents real scenarios

## Continuous Integration

Tests should be run in CI/CD pipeline:
```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: npm install
      - run: npm test
```

## Test Coverage

To measure test coverage (requires coverage tool):

```bash
# Install coverage tool
npm install --save-dev nyc

# Run tests with coverage
npx nyc node test/ArbitrageEngine.test.js

# Generate coverage report
npx nyc report --reporter=html
```

## Performance Testing

For performance benchmarks:

```javascript
const start = Date.now();
await component.performOperation();
const duration = Date.now() - start;

assert.ok(duration < 1000, 'Operation should complete in under 1 second');
```

## Integration with Main System

Some tests require the full Titan system to be running:

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Brain
python3 offchain/ml/brain.py

# Terminal 3: Run integration tests
node test/integration_test.js
```

## Mock Services

For testing without external dependencies:

```javascript
// Mock RPC provider
class MockProvider {
    async getBalance(address) {
        return ethers.parseEther('100.0');
    }
    
    async getGasPrice() {
        return ethers.parseUnits('30', 'gwei');
    }
}

const engine = new ArbitrageEngine({
    provider: new MockProvider()
});
```

## Common Test Scenarios

### 1. Opportunity Detection
```javascript
it('should detect profitable opportunities', async () => {
    const opportunities = await engine.scanOpportunities();
    assert.ok(opportunities.length > 0);
    assert.ok(opportunities[0].profit > 0);
});
```

### 2. Profit Calculation
```javascript
it('should calculate profit accurately', () => {
    const profit = engine.calculateProfit({
        revenue: 1000,
        cost: 950,
        gasCost: 5,
        bridgeFee: 10
    });
    assert.strictEqual(profit, 35); // 1000 - 950 - 5 - 10
});
```

### 3. Flash Loan Execution
```javascript
it('should execute flash loan successfully', async () => {
    const result = await engine.executeFlashLoan({
        token: 'USDC',
        amount: 10000
    });
    assert.strictEqual(result.success, true);
    assert.ok(result.profit > 0);
});
```

## Debugging Tests

### Enable Debug Logging

```javascript
process.env.DEBUG = 'titan:*';
node test/ArbitrageEngine.test.js
```

### Use Breakpoints

```javascript
it('should do something', async () => {
    debugger; // Add breakpoint
    const result = await component.method();
    assert.ok(result);
});
```

Run with Node inspector:
```bash
node --inspect-brk test/ArbitrageEngine.test.js
```

## Further Documentation Needed

- [ ] Performance benchmark targets for each test
- [ ] Test data generation utilities documentation
- [ ] Advanced mocking strategies guide
- [ ] Stress testing procedures
- [ ] Security testing methodologies
- [ ] Testnet deployment test scenarios

## Troubleshooting

### Tests Failing

1. **Check dependencies**: Run `npm install`
2. **Verify environment**: Check `.env.test` configuration
3. **RPC access**: Ensure test RPC endpoints are accessible
4. **Redis running**: Some tests require Redis
5. **Clean state**: Clear any cached or stale data

### Timeout Errors

Increase test timeout:
```javascript
it('slow test', async function() {
    this.timeout(10000); // 10 seconds
    await slowOperation();
});
```

### RPC Rate Limits

Use mocks or local testnet:
```bash
# Run local testnet
npx hardhat node

# Point tests to local node
RPC_URL=http://localhost:8545
```

## Contributing

When adding tests:
1. Follow existing test structure
2. Add descriptive test names
3. Include both positive and negative test cases
4. Update this README with new test descriptions
5. Ensure tests pass in CI

## License

This test suite is part of the Titan 2.0 project and follows the same MIT License.

## Support

For test-related issues:
- Review test output for specific errors
- Check environment configuration
- Verify all dependencies are installed
- Try running tests individually

See main README.md for general support information.
