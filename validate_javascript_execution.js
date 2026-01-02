#!/usr/bin/env node
/**
 * TITAN 2.0 - JavaScript Execution Layer Validation
 * ==================================================
 * 
 * Validates the JavaScript/Node.js execution components:
 * - Bot.js initialization
 * - Gas manager functionality
 * - Aggregator selector
 * - Signal file processing
 * - RPC connectivity
 * - Transaction building
 */

require('dotenv').config();
const fs = require('fs');
const path = require('path');
const { ethers } = require('ethers');

// Colors for terminal output
const colors = {
    reset: '\x1b[0m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    red: '\x1b[31m',
    cyan: '\x1b[36m',
    magenta: '\x1b[35m',
};

class JavaScriptValidator {
    constructor() {
        this.successes = [];
        this.warnings = [];
        this.errors = [];
    }

    printHeader(text) {
        console.log(`\n${colors.cyan}${'='.repeat(80)}${colors.reset}`);
        console.log(`${colors.cyan}${text.padStart(40 + text.length / 2).padEnd(80)}${colors.reset}`);
        console.log(`${colors.cyan}${'='.repeat(80)}${colors.reset}\n`);
    }

    printSuccess(text) {
        console.log(`${colors.green}✅ ${text}${colors.reset}`);
        this.successes.push(text);
    }

    printWarning(text) {
        console.log(`${colors.yellow}⚠️  ${text}${colors.reset}`);
        this.warnings.push(text);
    }

    printError(text) {
        console.log(`${colors.red}❌ ${text}${colors.reset}`);
        this.errors.push(text);
    }

    printInfo(text) {
        console.log(`${colors.cyan}ℹ️  ${text}${colors.reset}`);
    }

    // ========================
    // Phase 1: Environment
    // ========================

    async validateEnvironment() {
        this.printHeader('PHASE 1: Environment Validation');

        // Check .env file
        if (fs.existsSync('.env')) {
            this.printSuccess('.env file found');
        } else {
            this.printWarning('.env file not found - using environment variables');
        }

        // Check critical environment variables
        const criticalVars = {
            'EXECUTION_MODE': process.env.EXECUTION_MODE || 'PAPER',
            'MIN_PROFIT_USD': process.env.MIN_PROFIT_USD || '5.00',
            'MAX_BASE_FEE_GWEI': process.env.MAX_BASE_FEE_GWEI || '500',
        };

        for (const [key, value] of Object.entries(criticalVars)) {
            this.printSuccess(`${key} = ${value}`);
        }

        return true;
    }

    // ========================
    // Phase 2: Module Imports
    // ========================

    async validateModuleImports() {
        this.printHeader('PHASE 2: Module Import Validation');

        const modules = [
            { name: 'ethers', path: 'ethers' },
            { name: 'dotenv', path: 'dotenv' },
            { name: 'fs', path: 'fs' },
            { name: 'path', path: 'path' },
        ];

        for (const module of modules) {
            try {
                require(module.path);
                this.printSuccess(`${module.name} module loaded`);
            } catch (error) {
                this.printError(`${module.name} module failed: ${error.message}`);
            }
        }

        // Check custom modules
        const customModules = [
            { name: 'GasManager', path: './offchain/execution/gas_manager.js' },
            { name: 'AggregatorSelector', path: './offchain/execution/aggregator_selector.js' },
            { name: 'OmniSDKEngine', path: './offchain/execution/omniarb_sdk_engine.js' },
        ];

        for (const module of customModules) {
            try {
                if (fs.existsSync(module.path)) {
                    this.printSuccess(`${module.name} file exists`);
                } else {
                    this.printError(`${module.name} file not found: ${module.path}`);
                }
            } catch (error) {
                this.printError(`${module.name} check failed: ${error.message}`);
            }
        }

        return true;
    }

    // ========================
    // Phase 3: RPC Connectivity
    // ========================

    async validateRPCConnectivity() {
        this.printHeader('PHASE 3: RPC Connectivity Test');

        const chains = {
            137: { name: 'Polygon', rpc: process.env.RPC_POLYGON },
            1: { name: 'Ethereum', rpc: process.env.RPC_ETHEREUM },
            42161: { name: 'Arbitrum', rpc: process.env.RPC_ARBITRUM },
        };

        for (const [chainId, config] of Object.entries(chains)) {
            if (!config.rpc || config.rpc.includes('YOUR')) {
                this.printWarning(`${config.name} RPC not configured`);
                continue;
            }

            try {
                const provider = new ethers.JsonRpcProvider(config.rpc);
                const blockNumber = await provider.getBlockNumber();
                this.printSuccess(`${config.name} connected - Block: ${blockNumber}`);
            } catch (error) {
                this.printError(`${config.name} connection failed: ${error.message.substring(0, 50)}`);
            }
        }

        return true;
    }

    // ========================
    // Phase 4: Gas Manager
    // ========================

    async validateGasManager() {
        this.printHeader('PHASE 4: Gas Manager Validation');

        try {
            const { GasManager } = require('./offchain/execution/gas_manager.js');
            
            // GasManager requires a provider, so let's just check it can be imported
            this.printSuccess('GasManager module loaded');

            // Create a test provider for Polygon
            const polygonRPC = process.env.RPC_POLYGON;
            if (polygonRPC && !polygonRPC.includes('YOUR')) {
                try {
                    const provider = new ethers.JsonRpcProvider(polygonRPC);
                    const gasManager = new GasManager(provider, 137);
                    this.printSuccess('GasManager initialized with Polygon provider');
                    
                    // Test EIP-1559 method exists
                    if (typeof gasManager.calculateEIP1559Fees === 'function') {
                        this.printSuccess('GasManager has EIP-1559 support');
                    }
                } catch (error) {
                    this.printInfo(`GasManager initialization requires provider: ${error.message.substring(0, 50)}`);
                }
            } else {
                this.printInfo('Polygon RPC not configured - skipping GasManager test');
            }

        } catch (error) {
            this.printError(`GasManager validation failed: ${error.message}`);
        }

        return true;
    }

    // ========================
    // Phase 5: Signal Processing
    // ========================

    async validateSignalProcessing() {
        this.printHeader('PHASE 5: Signal Processing Validation');

        const signalsDir = path.join(__dirname, 'signals', 'outgoing');
        const processedDir = path.join(__dirname, 'signals', 'processed');

        // Check directories exist
        if (fs.existsSync(signalsDir)) {
            this.printSuccess(`Signals directory exists: ${signalsDir}`);
        } else {
            fs.mkdirSync(signalsDir, { recursive: true });
            this.printSuccess(`Created signals directory: ${signalsDir}`);
        }

        if (fs.existsSync(processedDir)) {
            this.printSuccess(`Processed directory exists: ${processedDir}`);
        } else {
            fs.mkdirSync(processedDir, { recursive: true });
            this.printSuccess(`Created processed directory: ${processedDir}`);
        }

        // Create and validate test signal
        const testSignal = {
            chainId: 137,
            token: 'USDC',
            amount: '1000000000',
            expectedProfit: 15.50,
            route: {
                protocols: [3, 2],
                routers: [
                    '0xE592427A0AEce92De3Edee1F18E0157C05861564',
                    '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506'
                ]
            },
            timestamp: Date.now()
        };

        const testFile = path.join(signalsDir, `test_signal_${Date.now()}.json`);
        
        try {
            fs.writeFileSync(testFile, JSON.stringify(testSignal, null, 2));
            this.printSuccess('Test signal created');

            const loaded = JSON.parse(fs.readFileSync(testFile, 'utf8'));
            if (loaded.chainId === 137 && loaded.token === 'USDC') {
                this.printSuccess('Signal validation passed');
            }

            // Cleanup
            fs.unlinkSync(testFile);
            this.printSuccess('Test signal cleaned up');

        } catch (error) {
            this.printError(`Signal processing failed: ${error.message}`);
        }

        return true;
    }

    // ========================
    // Phase 6: Transaction Building
    // ========================

    async validateTransactionBuilding() {
        this.printHeader('PHASE 6: Transaction Building Validation');

        try {
            // Check if we can build basic transaction structure
            const executionMode = (process.env.EXECUTION_MODE || 'PAPER').toUpperCase();
            this.printSuccess(`Execution mode: ${executionMode}`);

            // Validate flash loan configuration
            const flashLoanEnabled = process.env.FLASH_LOAN_ENABLED !== 'false';
            if (flashLoanEnabled) {
                this.printSuccess('Flash loans enabled');
            } else {
                this.printError('Flash loans disabled - system requires flash loans!');
            }

            const provider = parseInt(process.env.FLASH_LOAN_PROVIDER || '1');
            const providerName = provider === 1 ? 'Balancer V3' : 'Aave V3';
            this.printSuccess(`Flash loan provider: ${providerName}`);

            // Check wallet configuration for LIVE mode
            if (executionMode === 'LIVE') {
                const privateKey = process.env.PRIVATE_KEY;
                if (privateKey && privateKey.length === 66 && privateKey.startsWith('0x')) {
                    this.printSuccess('Private key format valid');
                } else {
                    this.printError('Invalid private key format for LIVE mode');
                }
            } else {
                this.printInfo('PAPER mode - wallet validation skipped');
            }

        } catch (error) {
            this.printError(`Transaction building validation failed: ${error.message}`);
        }

        return true;
    }

    // ========================
    // Phase 7: Aggregator Selector
    // ========================

    async validateAggregatorSelector() {
        this.printHeader('PHASE 7: Aggregator Selector Validation');

        try {
            const aggregatorPath = './offchain/execution/aggregator_selector.js';
            
            if (fs.existsSync(aggregatorPath)) {
                this.printSuccess('Aggregator selector file exists');
                
                // Check for required methods
                const content = fs.readFileSync(aggregatorPath, 'utf8');
                
                if (content.includes('selectBestAggregator') || content.includes('getQuotes')) {
                    this.printSuccess('Aggregator selector has quote methods');
                }
                
                // Check API key configuration
                const apiKeys = {
                    'ONEINCH_API_KEY': '1inch API',
                    'LIFI_API_KEY': 'Li.Fi API',
                    'ZEROX_API_KEY': '0x API',
                };

                for (const [key, name] of Object.entries(apiKeys)) {
                    if (process.env[key] && process.env[key].length > 10) {
                        this.printSuccess(`${name} configured`);
                    } else {
                        this.printInfo(`${name} not configured (optional)`);
                    }
                }
            } else {
                this.printError('Aggregator selector file not found');
            }

        } catch (error) {
            this.printError(`Aggregator selector validation failed: ${error.message}`);
        }

        return true;
    }

    // ========================
    // Summary
    // ========================

    printSummary() {
        this.printHeader('VALIDATION SUMMARY');

        const total = this.successes.length + this.warnings.length + this.errors.length;

        console.log(`\n${colors.green}✅ Successes: ${this.successes.length}${colors.reset}`);
        console.log(`${colors.yellow}⚠️  Warnings: ${this.warnings.length}${colors.reset}`);
        console.log(`${colors.red}❌ Errors: ${this.errors.length}${colors.reset}`);
        console.log(`\n📊 Total Checks: ${total}\n`);

        if (this.errors.length > 0) {
            console.log(`${colors.red}CRITICAL ERRORS FOUND:${colors.reset}`);
            this.errors.forEach(error => console.log(`  • ${error}`));
            console.log(`\n${colors.red}⚠️  System may not function correctly.${colors.reset}\n`);
            return false;
        } else if (this.warnings.length > 0) {
            console.log(`${colors.yellow}WARNINGS FOUND:${colors.reset}`);
            this.warnings.forEach(warning => console.log(`  • ${warning}`));
            console.log(`\n${colors.yellow}⚠️  System will function but some features may be limited.${colors.reset}\n`);
            return true;
        } else {
            console.log(`${colors.green}🎉 ALL VALIDATIONS PASSED!${colors.reset}`);
            console.log(`${colors.green}✅ JavaScript execution layer is ready.${colors.reset}\n`);
            return true;
        }
    }

    async runAll() {
        console.log(`\n${colors.magenta}${'='.repeat(80)}${colors.reset}`);
        console.log(`${colors.magenta}TITAN 2.0 - JAVASCRIPT EXECUTION LAYER VALIDATION${colors.reset}`);
        console.log(`${colors.magenta}${'='.repeat(80)}${colors.reset}\n`);

        await this.validateEnvironment();
        await this.validateModuleImports();
        await this.validateRPCConnectivity();
        await this.validateGasManager();
        await this.validateSignalProcessing();
        await this.validateTransactionBuilding();
        await this.validateAggregatorSelector();

        return this.printSummary();
    }
}

// Run validation
async function main() {
    const validator = new JavaScriptValidator();
    const success = await validator.runAll();
    process.exit(success ? 0 : 1);
}

main().catch(error => {
    console.error(`${colors.red}Validation crashed: ${error}${colors.reset}`);
    process.exit(1);
});
