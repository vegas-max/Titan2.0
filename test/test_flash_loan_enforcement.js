/**
 * Test: Flash Loan Enforcement
 * 
 * This test verifies that the bot correctly enforces 100% flash-funded execution
 * and rejects any configuration that would bypass flash loans.
 */

const { spawn } = require('child_process');
const path = require('path');

const botPath = path.join(__dirname, '..', 'offchain', 'execution', 'bot.js');

let passedTests = 0;
let failedTests = 0;

function runTest(testName, testFn) {
    console.log(`\n🧪 Running: ${testName}`);
    return testFn()
        .then(() => {
            console.log(`✅ PASSED: ${testName}`);
            passedTests++;
        })
        .catch((error) => {
            console.error(`❌ FAILED: ${testName}`);
            console.error(`   Error: ${error.message}`);
            failedTests++;
        });
}

async function testRejectsDisabledFlashLoans() {
    return new Promise((resolve, reject) => {
        const env = Object.assign({}, process.env, {
            FLASH_LOAN_ENABLED: 'false',
            EXECUTION_MODE: 'PAPER'
        });
        
        const child = spawn('node', [botPath], {
            env: env,
            stdio: 'pipe'
        });
        
        let output = '';
        let hasExited = false;
        
        child.stdout.on('data', (data) => {
            output += data.toString();
        });
        
        child.stderr.on('data', (data) => {
            output += data.toString();
        });
        
        child.on('exit', (code) => {
            hasExited = true;
            clearTimeout(timeoutId);
            
            if (code === 1 && output.includes('Flash loans are DISABLED')) {
                resolve();
            } else if (code === 1 && output.includes('100% flash-funded')) {
                resolve();
            } else {
                reject(new Error(`Expected exit code 1 with flash loan error, got code ${code}. Output: ${output.substring(0, 200)}`));
            }
        });
        
        const timeoutId = setTimeout(() => {
            if (!hasExited) {
                child.kill();
                reject(new Error('Test timeout - bot did not exit'));
            }
        }, 5000);
    });
}

async function testRejectsInvalidProvider() {
    return new Promise((resolve, reject) => {
        const env = Object.assign({}, process.env, {
            FLASH_LOAN_ENABLED: 'true',
            FLASH_LOAN_PROVIDER: '99',
            EXECUTION_MODE: 'PAPER'
        });
        
        const child = spawn('node', [botPath], {
            env: env,
            stdio: 'pipe'
        });
        
        let output = '';
        let hasExited = false;
        
        child.stdout.on('data', (data) => {
            output += data.toString();
        });
        
        child.stderr.on('data', (data) => {
            output += data.toString();
        });
        
        child.on('exit', (code) => {
            hasExited = true;
            clearTimeout(timeoutId);
            
            if (code === 1 && output.includes('Invalid flash loan provider')) {
                resolve();
            } else {
                reject(new Error(`Expected exit code 1 with invalid provider error, got code ${code}. Output: ${output.substring(0, 200)}`));
            }
        });
        
        const timeoutId = setTimeout(() => {
            if (!hasExited) {
                child.kill();
                reject(new Error('Test timeout - bot did not exit'));
            }
        }, 5000);
    });
}

async function testAcceptsBalancerProvider() {
    return new Promise((resolve, reject) => {
        const env = Object.assign({}, process.env, {
            FLASH_LOAN_ENABLED: 'true',
            FLASH_LOAN_PROVIDER: '1',
            EXECUTION_MODE: 'PAPER'
        });
        
        const child = spawn('node', [botPath], {
            env: env,
            stdio: 'pipe'
        });
        
        let output = '';
        
        child.stdout.on('data', (data) => {
            output += data.toString();
        });
        
        child.stderr.on('data', (data) => {
            output += data.toString();
        });
        
        setTimeout(() => {
            child.kill();
            
            if (output.includes('Flash Loan Configuration') && output.includes('Balancer V3')) {
                resolve();
            } else {
                reject(new Error('Bot did not start with Balancer configuration'));
            }
        }, 2000);
    });
}

async function testAcceptsAaveProvider() {
    return new Promise((resolve, reject) => {
        const env = Object.assign({}, process.env, {
            FLASH_LOAN_ENABLED: 'true',
            FLASH_LOAN_PROVIDER: '2',
            EXECUTION_MODE: 'PAPER'
        });
        
        const child = spawn('node', [botPath], {
            env: env,
            stdio: 'pipe'
        });
        
        let output = '';
        
        child.stdout.on('data', (data) => {
            output += data.toString();
        });
        
        child.stderr.on('data', (data) => {
            output += data.toString();
        });
        
        setTimeout(() => {
            child.kill();
            
            if (output.includes('Flash Loan Configuration') && output.includes('Aave V3')) {
                resolve();
            } else {
                reject(new Error('Bot did not start with Aave configuration'));
            }
        }, 2000);
    });
}

async function testDefaultsToFlashLoansEnabled() {
    return new Promise((resolve, reject) => {
        // Don't set FLASH_LOAN_ENABLED - should default to true
        const env = Object.assign({}, process.env, {
            EXECUTION_MODE: 'PAPER'
        });
        
        // Remove FLASH_LOAN_ENABLED if it exists
        delete env.FLASH_LOAN_ENABLED;
        
        const child = spawn('node', [botPath], {
            env: env,
            stdio: 'pipe'
        });
        
        let output = '';
        
        child.stdout.on('data', (data) => {
            output += data.toString();
        });
        
        child.stderr.on('data', (data) => {
            output += data.toString();
        });
        
        setTimeout(() => {
            child.kill();
            
            if (output.includes('Flash Loan Configuration') && 
                output.includes('ENABLED') &&
                !output.includes('Flash loans are DISABLED')) {
                resolve();
            } else {
                reject(new Error('Bot did not default to flash loans enabled: ' + output.substring(0, 300)));
            }
        }, 2000);
    });
}

// Run all tests
async function runAllTests() {
    console.log('═══════════════════════════════════════════════════════');
    console.log('     FLASH LOAN ENFORCEMENT TEST SUITE');
    console.log('═══════════════════════════════════════════════════════');
    
    await runTest('Rejects when FLASH_LOAN_ENABLED=false', testRejectsDisabledFlashLoans);
    await runTest('Rejects when FLASH_LOAN_PROVIDER is invalid', testRejectsInvalidProvider);
    await runTest('Accepts when FLASH_LOAN_PROVIDER=1 (Balancer)', testAcceptsBalancerProvider);
    await runTest('Accepts when FLASH_LOAN_PROVIDER=2 (Aave)', testAcceptsAaveProvider);
    await runTest('Defaults to flash loans ENABLED when not set', testDefaultsToFlashLoansEnabled);
    
    console.log('\n═══════════════════════════════════════════════════════');
    console.log(`     TEST RESULTS: ${passedTests} passed, ${failedTests} failed`);
    console.log('═══════════════════════════════════════════════════════\n');
    
    process.exit(failedTests > 0 ? 1 : 0);
}

runAllTests().catch((error) => {
    console.error('Test suite failed:', error);
    process.exit(1);
});
