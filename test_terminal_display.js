#!/usr/bin/env node
/**
 * Test script for JavaScript terminal display functionality
 */

const path = require('path');
const { terminalDisplay } = require(path.join(__dirname, 'offchain', 'execution', 'terminal_display.js'));

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function testTerminalDisplay() {
    console.log('\n' + '='.repeat(80));
    console.log('Testing JavaScript Terminal Display Module');
    console.log('='.repeat(80) + '\n');

    // Test 1: Header
    console.log('Test 1: Header Display');
    terminalDisplay.printHeader('PAPER');
    await sleep(1000);

    // Test 2: Signal Reception
    console.log('\nTest 2: Signal Reception');
    terminalDisplay.logSignalReceived('signal_123', 'USDC', 137, 12.50);
    await sleep(500);

    // Test 3: Execution Start
    console.log('\nTest 3: Execution Start');
    terminalDisplay.logExecutionStart('PAPER-1-123456', 'USDC', 137, '1000000000', 'PAPER');
    await sleep(500);

    // Test 4: Gas Estimate
    console.log('\nTest 4: Gas Estimate');
    terminalDisplay.logGasEstimate(137, '30', 5.50, 12.50);
    await sleep(500);

    // Test 5: Decision
    console.log('\nTest 5: Decision Logging');
    terminalDisplay.logDecision('APPROVE', 'USDC', 137, 'Profitable trade', { profit: 12.50, gas: 30 });
    await sleep(500);

    // Test 6: Execution Complete
    console.log('\nTest 6: Execution Complete');
    terminalDisplay.logExecutionComplete('PAPER-1-123456', 'SIMULATED', 150, 12.50);
    await sleep(1000);

    // Test 7: Stats Bar
    console.log('\nTest 7: Stats Bar');
    // Simulate some activity
    terminalDisplay.stats.signalsProcessed = 25;
    terminalDisplay.stats.executionsAttempted = 20;
    terminalDisplay.stats.executionsSuccessful = 18;
    terminalDisplay.stats.executionsFailed = 2;
    terminalDisplay.stats.paperTrades = 20;
    terminalDisplay.stats.totalProfitUSD = 250.75;
    terminalDisplay.printStatsBar();
    await sleep(1000);

    // Test 8: Warnings and Errors
    console.log('\nTest 8: Warnings and Errors');
    terminalDisplay.logWarning('BOT', 'Low balance detected');
    terminalDisplay.logError('BOT', 'Failed to execute', 'Insufficient gas');
    await sleep(1000);

    // Test 9: Info messages
    console.log('\nTest 9: Info Messages');
    terminalDisplay.logInfo('Execution engine started successfully');
    await sleep(1000);

    console.log('\n' + '='.repeat(80));
    console.log('✅ All JavaScript Terminal Display Tests Passed!');
    console.log('='.repeat(80) + '\n');
}

testTerminalDisplay().catch(err => {
    console.error('Test failed:', err);
    process.exit(1);
});
