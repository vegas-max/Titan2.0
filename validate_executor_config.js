#!/usr/bin/env node

/**
 * Executor Contract Configuration Validator
 * 
 * This script validates that the flash loan and executor contract configuration
 * is correct and helps identify common misconfigurations.
 */

// Try to load dotenv if available, but continue without it
try {
    require('dotenv').config();
} catch (e) {
    // dotenv not available, use existing environment variables
}

console.log('═══════════════════════════════════════════════════════════════');
console.log('    EXECUTOR CONTRACT CONFIGURATION VALIDATOR');
console.log('═══════════════════════════════════════════════════════════════\n');

let errors = [];
let warnings = [];
let info = [];

// ============================================================================
// Check 1: Executor Address Configuration
// ============================================================================
const executorAddr = process.env.EXECUTOR_ADDRESS;
const hftAddr = process.env.HFT_CONTRACT_ADDRESS;
const routerAddr = process.env.ROUTER_CONTRACT_ADDRESS;

console.log('📋 Executor Contract Configuration:');
console.log(`   EXECUTOR_ADDRESS:       ${executorAddr || '(not set)'}`);
console.log(`   HFT_CONTRACT_ADDRESS:   ${hftAddr || '(not set)'}`);
console.log(`   ROUTER_CONTRACT_ADDRESS: ${routerAddr || '(not set)'}`);
console.log('');

if (!executorAddr) {
    errors.push('EXECUTOR_ADDRESS is not set - bot.js will fail to execute trades');
    console.log('❌ ERROR: EXECUTOR_ADDRESS is not configured');
} else {
    console.log('✅ EXECUTOR_ADDRESS is configured');
    info.push(`Using unified executor at ${executorAddr}`);
}

if (hftAddr || routerAddr) {
    warnings.push('HFT_CONTRACT_ADDRESS or ROUTER_CONTRACT_ADDRESS is set but NOT used by bot.js');
    console.log('⚠️  WARNING: HFT/Router addresses are configured but not used');
    console.log('   These are reference architecture only.');
    console.log('   bot.js uses EXECUTOR_ADDRESS, not HFT/Router contracts.');
    console.log('   See EXECUTOR_CONTRACTS_CLARIFICATION.md for details.');
} else {
    console.log('ℹ️  HFT/Router addresses not set (this is correct for current system)');
}

console.log('');

// ============================================================================
// Check 2: Flash Loan Provider Configuration
// ============================================================================
const flashLoanEnabled = process.env.FLASH_LOAN_ENABLED;
const flashLoanProvider = process.env.FLASH_LOAN_PROVIDER;

console.log('⚡ Flash Loan Configuration:');
console.log(`   FLASH_LOAN_ENABLED:  ${flashLoanEnabled || '(not set - defaults to true)'}`);
console.log(`   FLASH_LOAN_PROVIDER: ${flashLoanProvider || '(not set - defaults to 1)'}`);
console.log('');

// Check FLASH_LOAN_ENABLED
if (flashLoanEnabled === undefined) {
    console.log('ℹ️  FLASH_LOAN_ENABLED not set - will default to true (correct)');
    info.push('Flash loans will be enabled by default');
} else if (flashLoanEnabled === 'true') {
    console.log('✅ FLASH_LOAN_ENABLED=true (correct)');
    info.push('Flash loans are explicitly enabled');
} else if (flashLoanEnabled === 'false') {
    errors.push('FLASH_LOAN_ENABLED=false - bot will exit immediately at startup');
    console.log('❌ ERROR: FLASH_LOAN_ENABLED=false');
    console.log('   The system requires 100% flash-funded execution.');
    console.log('   Bot will exit immediately with this configuration.');
} else {
    warnings.push(`FLASH_LOAN_ENABLED has invalid value: ${flashLoanEnabled}`);
    console.log('⚠️  WARNING: FLASH_LOAN_ENABLED has unexpected value');
}

// Check FLASH_LOAN_PROVIDER
const providerNum = parseInt(flashLoanProvider || '1');
if (flashLoanProvider === undefined) {
    console.log('ℹ️  FLASH_LOAN_PROVIDER not set - will default to 1 (Balancer V3)');
    info.push('Using default flash loan provider: Balancer V3');
} else if (providerNum === 1) {
    console.log('✅ FLASH_LOAN_PROVIDER=1 (Balancer V3) - correct');
    info.push('Flash loans will be sourced from Balancer V3');
} else if (providerNum === 2) {
    console.log('✅ FLASH_LOAN_PROVIDER=2 (Aave V3) - correct');
    info.push('Flash loans will be sourced from Aave V3');
} else {
    errors.push(`FLASH_LOAN_PROVIDER=${flashLoanProvider} is invalid - must be 1 or 2`);
    console.log('❌ ERROR: FLASH_LOAN_PROVIDER has invalid value');
    console.log('   Must be 1 (Balancer V3) or 2 (Aave V3)');
    console.log('   Bot will exit immediately with this configuration.');
}

console.log('');

// ============================================================================
// Check 3: Understanding Check
// ============================================================================
console.log('🎓 Configuration Understanding Check:');
console.log('');

if (flashLoanProvider && (hftAddr || routerAddr)) {
    console.log('⚠️  POTENTIAL CONFUSION DETECTED:');
    console.log('');
    console.log('   You have configured BOTH:');
    console.log('   - FLASH_LOAN_PROVIDER (Balancer/Aave selection)');
    console.log('   - HFT/Router contract addresses');
    console.log('');
    console.log('   These are DIFFERENT concepts:');
    console.log('');
    console.log('   FLASH_LOAN_PROVIDER controls WHERE to borrow flash loans:');
    console.log('   • 1 = Balancer V3 (liquidity source)');
    console.log('   • 2 = Aave V3 (liquidity source)');
    console.log('');
    console.log('   HFT/Router addresses are reference architecture:');
    console.log('   • HFT_CONTRACT = Executor for simple V2 swaps (NOT used by bot.js)');
    console.log('   • ROUTER_CONTRACT = Executor for complex paths (NOT used by bot.js)');
    console.log('');
    console.log('   Current bot.js ONLY uses EXECUTOR_ADDRESS.');
    console.log('   HFT/Router contracts are NOT called - they are example code only.');
    console.log('');
    warnings.push('Mixed configuration detected - potential conceptual confusion');
}

// ============================================================================
// Summary
// ============================================================================
console.log('');
console.log('═══════════════════════════════════════════════════════════════');
console.log('    VALIDATION SUMMARY');
console.log('═══════════════════════════════════════════════════════════════');
console.log('');

if (errors.length > 0) {
    console.log('❌ ERRORS:');
    errors.forEach((err, i) => {
        console.log(`   ${i + 1}. ${err}`);
    });
    console.log('');
}

if (warnings.length > 0) {
    console.log('⚠️  WARNINGS:');
    warnings.forEach((warn, i) => {
        console.log(`   ${i + 1}. ${warn}`);
    });
    console.log('');
}

if (info.length > 0) {
    console.log('ℹ️  INFORMATION:');
    info.forEach((inf, i) => {
        console.log(`   ${i + 1}. ${inf}`);
    });
    console.log('');
}

// ============================================================================
// Recommendations
// ============================================================================
console.log('📚 RECOMMENDATIONS:');
console.log('');

if (errors.length > 0) {
    console.log('   ❌ Fix all errors before running bot.js');
    console.log('   ❌ Bot will exit immediately with current configuration');
}

if (warnings.length > 0 && !executorAddr) {
    console.log('   ⚠️  Configure EXECUTOR_ADDRESS in .env file');
}

if (hftAddr || routerAddr) {
    console.log('   ℹ️  HFT/Router addresses can be safely removed from .env');
    console.log('   ℹ️  They are not used by the current bot.js implementation');
}

console.log('   📖 Read EXECUTOR_CONTRACTS_CLARIFICATION.md for architecture details');
console.log('   📖 Read EXECUTOR_QUICK_REFERENCE.md for quick guidance');

console.log('');
console.log('═══════════════════════════════════════════════════════════════');

// Exit code
if (errors.length > 0) {
    console.log('   STATUS: ❌ CONFIGURATION HAS ERRORS');
    console.log('═══════════════════════════════════════════════════════════════\n');
    process.exit(1);
} else if (warnings.length > 0) {
    console.log('   STATUS: ⚠️  CONFIGURATION HAS WARNINGS');
    console.log('═══════════════════════════════════════════════════════════════\n');
    process.exit(0);
} else {
    console.log('   STATUS: ✅ CONFIGURATION IS VALID');
    console.log('═══════════════════════════════════════════════════════════════\n');
    process.exit(0);
}
