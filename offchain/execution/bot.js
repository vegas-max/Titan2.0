require('dotenv').config();
const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');
const { GasManager } = require('./gas_manager');
const { BloxRouteManager } = require('./bloxroute_manager');
const { AggregatorSelector } = require('./aggregator_selector');
const { OmniSDKEngine } = require('./omniarb_sdk_engine');
const { LifiExecutionEngine } = require('./lifi_manager');
const { terminalDisplay } = require('./terminal_display');

const SIGNALS_DIR = path.join(__dirname, '..', 'signals', 'outgoing');
const PROCESSED_DIR = path.join(__dirname, '..', 'signals', 'processed');
const EXECUTOR_ADDR = process.env.EXECUTOR_ADDRESS;
const PRIVATE_KEY = process.env.PRIVATE_KEY;
// TITAN_EXECUTION_MODE takes precedence (set by orchestrator), fallback to EXECUTION_MODE (.env)
const EXECUTION_MODE = (process.env.TITAN_EXECUTION_MODE || process.env.EXECUTION_MODE || 'PAPER').toUpperCase();

// CRITICAL: Flash loan configuration - ensures 100% flash-funded execution
// This system is designed to operate with ZERO capital requirements (only gas fees)
// All arbitrage trades MUST use flash loans to maintain capital efficiency
const FLASH_LOAN_ENABLED = process.env.FLASH_LOAN_ENABLED === 'true' || process.env.FLASH_LOAN_ENABLED === undefined; // Default: true if not set
const FLASH_LOAN_PROVIDER = parseInt(process.env.FLASH_LOAN_PROVIDER || '1'); // 1=Balancer, 2=Aave

const RPC_MAP = {
    1: process.env.RPC_ETHEREUM,
    137: process.env.RPC_POLYGON,
    42161: process.env.RPC_ARBITRUM,
    10: process.env.RPC_OPTIMISM,
    8453: process.env.RPC_BASE,
    56: process.env.RPC_BSC,
    43114: process.env.RPC_AVALANCHE,
    250: process.env.RPC_FANTOM,
    59144: process.env.RPC_LINEA,
    534352: process.env.RPC_SCROLL,
    5000: process.env.RPC_MANTLE,
    324: process.env.RPC_ZKSYNC,
    81457: process.env.RPC_BLAST,
    42220: process.env.RPC_CELO,
    204: process.env.RPC_OPBNB
};

class TitanBot {
    constructor() {
        this.signalsDir = SIGNALS_DIR;
        this.processedDir = PROCESSED_DIR;
        this.bloxRoute = new BloxRouteManager();
        this.privateRelay = new PrivateRelayManager();
        this.rpcManager = new CustomRPCManager();
        this.activeProviders = {};
        this.crossChainEnabled = this._parseBooleanEnv(process.env.ENABLE_CROSS_CHAIN);
        this.executionMode = EXECUTION_MODE;
        this.paperTrades = [];
        this.paperTradeCount = 0;
        this.processedSignals = new Set();
        this.display = terminalDisplay;
        
        // Advanced features configuration
        this.usePrivateRelay = this._parseBooleanEnv(process.env.USE_PRIVATE_RELAY || 'true');
        this.useMEVDetection = this._parseBooleanEnv(process.env.USE_MEV_DETECTION || 'true');
        
        // Ensure directories exist
        if (!fs.existsSync(this.signalsDir)) {
            fs.mkdirSync(this.signalsDir, { recursive: true });
        }
        if (!fs.existsSync(this.processedDir)) {
            fs.mkdirSync(this.processedDir, { recursive: true });
        }
    }
    
    /**
     * Parse boolean environment variables safely
     * @param {string} value - Environment variable value
     * @returns {boolean} - Parsed boolean value
     */
    _parseBooleanEnv(value) {
        if (!value) return false;
        const normalized = value.toLowerCase().trim();
        return normalized === 'true' || normalized === '1' || normalized === 'yes';
    }

    async init() {
        // Print header with terminal display
        this.display.printHeader(this.executionMode);
        
        console.log("🤖 Titan Bot Starting...");
        console.log(`📋 Execution Mode: ${this.executionMode}`);
        
        if (this.executionMode === 'PAPER') {
            console.log("📝 PAPER MODE: Trades will be simulated (no blockchain execution)");
            console.log("   • Real-time data: ✓");
            console.log("   • Real calculations: ✓");
            console.log("   • Execution: SIMULATED");
        } else {
            console.log("🔴 LIVE MODE: Real blockchain execution enabled");
            console.log("   ⚠️  WARNING: Real funds will be used!");
        }
        console.log("");
        
        // CRITICAL: Validate flash loan configuration
        if (!FLASH_LOAN_ENABLED) {
            console.error('❌ CRITICAL: Flash loans are DISABLED');
            console.error('   This system requires 100% flash-funded execution!');
            console.error('   Set FLASH_LOAN_ENABLED=true in .env file');
            process.exit(1);
        }
        
        if (FLASH_LOAN_PROVIDER !== 1 && FLASH_LOAN_PROVIDER !== 2) {
            console.error('❌ CRITICAL: Invalid flash loan provider');
            console.error(`   FLASH_LOAN_PROVIDER=${FLASH_LOAN_PROVIDER} is not valid`);
            console.error('   Must be 1 (Balancer) or 2 (Aave)');
            process.exit(1);
        }
        
        console.log("⚡ Flash Loan Configuration:");
        console.log(`   • Flash loans: ENABLED (mandatory for zero-capital operation)`);
        console.log(`   • Provider: ${FLASH_LOAN_PROVIDER === 1 ? 'Balancer V3' : 'Aave V3'}`);
        console.log(`   • Capital requirement: ZERO (only gas fees needed)`);
        console.log("");
        
        // Validate configuration (only required for LIVE mode)
        if (this.executionMode === 'LIVE') {
            if (!PRIVATE_KEY || !/^0x[0-9a-fA-F]{64}$/.test(PRIVATE_KEY)) {
                this.display.logError('BOT', 'Invalid private key format in .env', 
                    'Must be 64 hex characters with 0x prefix');
                console.error('❌ CRITICAL: Invalid private key format in .env');
                console.error('   Must be 64 hex characters with 0x prefix (e.g., 0x1234...)');
                process.exit(1);
            }
            
            if (!EXECUTOR_ADDR || !/^0x[0-9a-fA-F]{40}$/.test(EXECUTOR_ADDR)) {
                this.display.logError('BOT', 'Invalid executor address format in .env',
                    'Must be 40 hex characters with 0x prefix');
                console.error('❌ CRITICAL: Invalid executor address format in .env');
                console.error('   Must be 40 hex characters with 0x prefix (e.g., 0xabcd...)');
                process.exit(1);
            }
        } else {
            this.display.logInfo("Paper mode: Skipping wallet validation");
            console.log("ℹ️  Paper mode: Skipping wallet validation");
        }
        
        // Validate gas configuration
        const maxBaseFee = parseFloat(process.env.MAX_BASE_FEE_GWEI);
        if (isNaN(maxBaseFee) || maxBaseFee <= 0) {
            console.warn('⚠️ Invalid MAX_BASE_FEE_GWEI, using default 500 gwei');
        }
        
        console.log(`✅ Signal monitoring directory: ${this.signalsDir}`);
        console.log(`✅ Processed signals directory: ${this.processedDir}`);
        console.log("🚀 Titan Bot Online - Monitoring for signals...\n");
        
        // Start signal file watcher
        this.startSignalWatcher();
        
        // Set up graceful shutdown
        process.on('SIGINT', () => {
            console.log('\n🛑 Shutting down gracefully...');
            process.exit(0);
        });
    }
    
    /**
     * Watch for new signal files and process them
     */
    startSignalWatcher() {
        console.log("👀 Starting signal file watcher...");
        this.display.logInfo("Signal monitoring started");
        
        let lastStatsPrint = Date.now();
        
        // Check for signals every second
        setInterval(() => {
            try {
                // Print stats every 60 seconds
                if (Date.now() - lastStatsPrint > 60000) {
                    this.display.printStatsBar();
                    lastStatsPrint = Date.now();
                }
                
                const files = fs.readdirSync(this.signalsDir)
                    .filter(f => f.endsWith('.json') && !this.processedSignals.has(f))
                    .sort(); // Process oldest first
                
                for (const file of files) {
                    this.processSignalFile(file);
                }
            } catch (error) {
                console.error('Error reading signals directory:', error.message);
                this.display.logError('WATCHER', 'Error reading signals directory', error.message);
            }
        }, 1000);
    }
    
    /**
     * Process a single signal file
     */
    async processSignalFile(filename) {
        const filepath = path.join(this.signalsDir, filename);
        
        try {
            // Mark as processing
            this.processedSignals.add(filename);
            
            // Read signal file
            const signalData = fs.readFileSync(filepath, 'utf8');
            const signal = JSON.parse(signalData);
            
            // Log signal reception
            const signalId = path.basename(filename, '.json');
            const profitUSD = signal.metrics?.profit_usd || 0;
            const tokenSymbol = signal.token_symbol || signal.token || 'UNKNOWN';
            this.display.logSignalReceived(signalId, tokenSymbol, signal.chainId, profitUSD);
            
            // Execute trade (paper or live)
            await this.executeTrade(signal);
            
            // Move to processed directory
            const processedPath = path.join(this.processedDir, filename);
            fs.renameSync(filepath, processedPath);
            
        } catch (error) {
            console.error(`❌ Error processing signal file ${filename}:`, error.message);
            this.display.logError('BOT', `Error processing signal ${filename}`, error.message);
            // Remove from processed set so we can retry
            this.processedSignals.delete(filename);
        }
    }

    /**
     * Execute a paper trade (simulation only, no blockchain interaction)
     */
    async executePaperTrade(signal) {
        const startTime = Date.now();
        
        try {
            // Validate signal
            if (!signal || !signal.chainId || !signal.token || !signal.amount) {
                console.error('❌ Invalid signal structure:', signal);
                this.display.logError('PAPER_TRADE', 'Invalid signal structure');
                return;
            }
            
            this.paperTradeCount++;
            const tradeId = `PAPER-${this.paperTradeCount}-${Date.now()}`;
            const tokenSymbol = signal.token_symbol || signal.token;
            
            // Log execution start
            this.display.logExecutionStart(tradeId, tokenSymbol, signal.chainId, signal.amount, 'PAPER');
            
            console.log(`\n📝 Paper Trade #${this.paperTradeCount} - ${new Date().toISOString()}`);
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
            console.log(`   Trade ID: ${tradeId}`);
            console.log(`   Chain: ${signal.chainId}`);
            console.log(`   Token: ${tokenSymbol}`);
            console.log(`   Amount: ${signal.amount}`);
            console.log(`   Type: ${signal.type || 'INTRA_CHAIN'}`);
            console.log(`   Expected Profit: $${signal.metrics?.profit_usd?.toFixed(2) || 'N/A'}`);
            
            // Simulate execution delay (realistic timing)
            await new Promise(resolve => setTimeout(resolve, 100));
            
            const duration = Date.now() - startTime;
            const profitUSD = signal.metrics?.profit_usd || 0;
            
            // Record paper trade
            const paperTrade = {
                id: tradeId,
                timestamp: new Date().toISOString(),
                signal: signal,
                status: 'SIMULATED',
                duration_ms: duration,
                mode: 'PAPER'
            };
            
            this.paperTrades.push(paperTrade);
            
            // Keep only last 100 paper trades in memory
            if (this.paperTrades.length > 100) {
                this.paperTrades.shift();
            }
            
            console.log(`   Status: ✅ SIMULATED`);
            console.log(`   Duration: ${duration}ms`);
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
            
            // Log execution complete
            this.display.logExecutionComplete(tradeId, 'SIMULATED', duration, profitUSD);
            
        } catch (e) {
            console.error('❌ Paper trade error:', e.message);
            this.display.logError('PAPER_TRADE', e.message);
        }
    }

    async executeTrade(signal) {
        // Route to paper execution if in PAPER mode
        if (this.executionMode === 'PAPER') {
            return await this.executePaperTrade(signal);
        }
        
        // Otherwise, execute real trade (LIVE mode)
        const startTime = Date.now();
        let executionStatus = 'UNKNOWN';
        
        try {
            // Validate signal
            if (!signal || !signal.chainId || !signal.token || !signal.amount) {
                console.error('❌ Invalid signal structure:', signal);
                return;
            }
            
            const chainId = signal.chainId;
            
            // Validate RPC exists
            if (!RPC_MAP[chainId]) {
                console.error(`❌ No RPC configured for chain ${chainId}`);
                return;
            }
            
            // Validate credentials - check if it's a valid 64-character hex string
            if (!PRIVATE_KEY || PRIVATE_KEY.length < 64 || !/^0x[0-9a-fA-F]{64}$/.test(PRIVATE_KEY)) {
                console.error('❌ Invalid private key format - must be 64 hex characters with 0x prefix');
                return;
            }
            
            if (!EXECUTOR_ADDR || EXECUTOR_ADDR === '0xYOUR_DEPLOYED_CONTRACT_ADDRESS_HERE') {
                console.error('❌ Executor address not configured');
                return;
            }
            
            console.log(`\n🎯 Processing trade signal for chain ${chainId} at ${new Date().toISOString()}`);
            console.log(`   Token: ${signal.token}, Amount: ${signal.amount}`);
            console.log(`   Expected Profit: $${signal.metrics?.profit_usd || 'N/A'}`);
            console.log(`   Strategy Type: ${signal.strategy_type || 'SINGLE_CHAIN'}`);
            
            // Check if this is a cross-chain arbitrage signal
            if (signal.strategy_type === 'CROSS_CHAIN' && this.crossChainEnabled) {
                return await this.executeCrossChainArbitrage(signal);
            }
            
            const provider = new ethers.JsonRpcProvider(RPC_MAP[chainId]);
            const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
            const gasMgr = new GasManager(provider, chainId);
            const simulator = new OmniSDKEngine(chainId, RPC_MAP[chainId]);
            
            // Check wallet balance
            try {
                const balance = await provider.getBalance(wallet.address);
                if (balance === 0n) {
                    console.error('❌ Wallet has zero balance, cannot execute');
                    return;
                }
                console.log(`   Wallet balance: ${ethers.formatEther(balance)} native token`);
            } catch (e) {
                console.error('⚠️ Could not check wallet balance:', e.message);
            }
            
            // 1. Route construction with validation
            let routeData;
            try {
                // Use intelligent aggregator selection for DEX aggregation
                // Note: use_paraswap flag maintained for backward compatibility
                // Both flags route through the new multi-aggregator system
                if (signal.use_aggregator || signal.use_paraswap) {
                    const aggregatorSelector = new AggregatorSelector(chainId, provider);
                    
                    // Prepare trade object for aggregator
                    const trade = {
                        chainId: chainId,
                        token: signal.token,
                        destToken: signal.path[0],
                        amount: signal.amount,
                        userAddress: wallet.address,
                        valueUSD: signal.metrics?.profit_usd || 0,
                        priority: signal.ai_params?.priority > 50 ? 'SPEED' : 'STANDARD',
                        slippageBps: signal.slippageBps || 100
                    };
                    
                    // Try to get best route from aggregators
                    const swap = await aggregatorSelector.executeTrade(trade);
                    if (!swap) {
                        console.log('🛑 No aggregator route available');
                        return;
                    }
                    
                    routeData = ethers.AbiCoder.defaultAbiCoder().encode(
                        ["uint8[]", "address[]", "address[]", "bytes[]"],
                        [[4], [swap.to], [signal.path[0]], [swap.data]]
                    );
                } else {
                    // Validate routers are not zero addresses
                    for (const router of signal.routers) {
                        if (router === '0x0000000000000000000000000000000000000000') {
                            console.log('🛑 Invalid router address detected (zero address)');
                            return;
                        }
                    }
                    
                    routeData = ethers.AbiCoder.defaultAbiCoder().encode(
                        ["uint8[]", "address[]", "address[]", "bytes[]"],
                        [signal.protocols, signal.routers, signal.path, signal.extras]
                    );
                }
            } catch (e) {
                console.error('❌ Route construction failed:', e.message);
                return;
            }

            // 2. Build TX with validation
            let txRequest;
            try {
                // CRITICAL: Always use flash loans for zero-capital execution
                // This ensures 100% flash-funded operation (no wallet capital needed)
                const contract = new ethers.Contract(EXECUTOR_ADDR, ["function execute(uint8,address,uint256,bytes) external"], wallet);
                
                // Validate flash loan is enabled (double-check at execution time)
                if (!FLASH_LOAN_ENABLED) {
                    console.error('❌ CRITICAL: Attempted execution without flash loans enabled');
                    console.error('   This violates the zero-capital requirement');
                    return;
                }
                
                // Get gas fees with strategy based on signal priority
                const gasStrategy = signal.ai_params?.priority > 50 ? 'RAPID' : 'STANDARD';
                const fees = await gasMgr.getDynamicGasFees(gasStrategy);
                
                // Validate gas fees are reasonable (using same limit as GasManager)
                const MAX_GAS_FEE_GWEI = parseFloat(process.env.MAX_BASE_FEE_GWEI || '500');
                const maxFeeGwei = parseFloat(ethers.formatUnits(fees.maxFeePerGas || fees.gasPrice || 0n, 'gwei'));
                
                if (maxFeeGwei > MAX_GAS_FEE_GWEI) {
                    console.log(`🛑 Gas fees too high (${maxFeeGwei} gwei), aborting. Max allowed: ${MAX_GAS_FEE_GWEI} gwei`);
                    return;
                }
                
                // Build transaction using configured flash loan provider
                // flashSource: 1=Balancer, 2=Aave (from FLASH_LOAN_PROVIDER env var)
                txRequest = await contract.execute.populateTransaction(
                    FLASH_LOAN_PROVIDER, signal.token, signal.amount, routeData, { ...fees }
                );
                
                console.log(`   Flash Loan Provider: ${FLASH_LOAN_PROVIDER === 1 ? 'Balancer V3' : 'Aave V3'}`);
                
                // Create route info object for intelligent gas estimation
                const routeInfo = {
                    protocols: signal.protocols || [],
                    routerCount: (signal.routers || []).length,
                    hasAggregator: signal.use_aggregator || signal.use_paraswap || false
                };
                
                // Get gas limit with route-aware fallback
                const gasLimit = await gasMgr.estimateGasWithBuffer(txRequest, routeInfo);
                txRequest.gasLimit = gasLimit;
                
                // Calculate and log expected cost
                const gasPrice = fees.maxFeePerGas || fees.gasPrice;
                const estimatedCostUSD = gasMgr.estimateGasCostUSD(gasLimit, gasPrice);
                
                console.log(`   Gas limit: ${gasLimit.toString()}`);
                console.log(`   Estimated cost: $${estimatedCostUSD.toFixed(2)}`);
                
                // Profit check with gas costs
                const expectedProfit = signal.metrics?.profit_usd || 0;
                if (expectedProfit < estimatedCostUSD * 2) {
                    console.log(`⚠️ Profit margin too thin: $${expectedProfit} vs $${estimatedCostUSD.toFixed(2)} gas`);
                    return;
                }
                
            } catch (e) {
                console.error('❌ Transaction building failed:', e.message);
                return;
            }

            // 3. Comprehensive Pre-Broadcast Simulation
            console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
            console.log('🧪 PRE-BROADCAST SIMULATION & VALIDATION');
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
            
            let simulationResult = null;
            let isSafe = false;
            
            try {
                console.log('   Step 1: Simulating transaction execution...');
                
                // Perform full transaction simulation
                simulationResult = await simulator.simulateTransaction(txRequest);
                
                if (!simulationResult.success) {
                    console.log('   ❌ Simulation FAILED - Transaction would revert on-chain');
                    console.log(`   Reason: ${simulationResult.error}`);
                    console.log('   ⚠️  Aborting transaction to prevent wasted gas fees');
                    executionStatus = 'SIMULATION_FAILED';
                    return;
                }
                
                console.log('   ✅ Step 1: Transaction simulation PASSED');
                console.log(`   Estimated gas usage: ${simulationResult.gasUsed.toString()}`);
                
                // Additional validation step
                console.log('   Step 2: Validating simulation results...');
                isSafe = await simulator.simulateExecution(EXECUTOR_ADDR, txRequest.data, wallet.address);
                
                if (!isSafe) {
                    console.log('   ❌ Validation FAILED - Secondary check detected issues');
                    executionStatus = 'VALIDATION_FAILED';
                    return;
                }
                
                console.log('   ✅ Step 2: Simulation validation PASSED');
                
                // Final safety checks before broadcast
                console.log('   Step 3: Final pre-broadcast checks...');
                
                // Check if gas estimate is reasonable
                const gasLimit = txRequest.gasLimit || 0n;
                const estimatedGas = simulationResult.gasUsed || 0n;
                
                if (estimatedGas > gasLimit) {
                    console.log(`   ⚠️  Warning: Estimated gas (${estimatedGas}) exceeds limit (${gasLimit})`);
                    console.log('   Adjusting gas limit to prevent out-of-gas failure...');
                    txRequest.gasLimit = estimatedGas * 120n / 100n; // 20% buffer
                }
                
                console.log('   ✅ Step 3: Pre-broadcast checks COMPLETE');
                console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
                console.log('✅ ALL SIMULATIONS PASSED - Transaction ready for broadcast');
                console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
                
            } catch (e) {
                console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
                console.error('   ❌ Simulation error:', e.message);
                console.log('   Stack:', e.stack);
                console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
                executionStatus = 'SIMULATION_ERROR';
                return;
            }

            // 4. Execute with proper error handling (only if simulation passed)
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
            console.log('📡 TRANSACTION BROADCAST');
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
            console.log(`   Chain ID: ${chainId}`);
            console.log(`   Token: ${signal.token}`);
            console.log(`   Amount: ${signal.amount}`);
            console.log(`   Expected Profit: $${signal.metrics?.profit_usd?.toFixed(2) || 'N/A'}`);
            console.log(`   Gas Limit: ${txRequest.gasLimit?.toString() || 'N/A'}`);
            console.log(`   Estimated Cost: $${estimatedCostUSD.toFixed(2)}`);
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
            
            executionStatus = 'EXECUTING';
            try {
                if (chainId === 137 || chainId === 56) {
                    // Use BloxRoute for MEV protection
                    console.log('🔐 Using BloxRoute for MEV-protected broadcast...');
                    try {
                        const signedTx = await wallet.signTransaction(txRequest);
                        const blockNumber = await provider.getBlockNumber();
                        console.log(`   Submitting bundle for block ${blockNumber + 1}...`);
                        
                        const res = await this.bloxRoute.submitBundle([signedTx], blockNumber);
                        
                        if (res && res.result) {
                            console.log(`\n🚀 BloxRoute bundle submitted successfully!`);
                            console.log(`   Bundle Hash: ${res.result}`);
                            executionStatus = 'BLOXROUTE_SUBMITTED';
                        } else {
                            console.log('⚠️ BloxRoute submission uncertain, falling back to public mempool');
                            console.log('📡 Broadcasting to public mempool...');
                            const tx = await wallet.sendTransaction(txRequest);
                            console.log(`\n✅ Transaction broadcast successfully!`);
                            console.log(`   TX Hash: ${tx.hash}`);
                            executionStatus = 'PUBLIC_MEMPOOL';
                            
                            // Monitor transaction
                            this._monitorTransaction(tx, provider, signal);
                        }
                    } catch (bloxError) {
                        console.error('⚠️ BloxRoute failed:', bloxError.message);
                        console.log('📡 Falling back to public mempool broadcast...');
                        const tx = await wallet.sendTransaction(txRequest);
                        console.log(`\n✅ Transaction broadcast successfully!`);
                        console.log(`   TX Hash: ${tx.hash}`);
                        executionStatus = 'PUBLIC_MEMPOOL';
                        
                        // Monitor transaction
                        this._monitorTransaction(tx, provider, signal);
                    }
                } else {
                    // Standard public mempool broadcast
                    console.log('📡 Broadcasting to public mempool...');
                    const tx = await wallet.sendTransaction(txRequest);
                    console.log(`\n✅ Transaction broadcast successfully!`);
                    console.log(`   TX Hash: ${tx.hash}`);
                    console.log(`   Explorer: ${this._getExplorerUrl(chainId, tx.hash)}`);
                    executionStatus = 'PUBLIC_MEMPOOL';
                    
                    // Monitor transaction
                    this._monitorTransaction(tx, provider, signal);
                }
                
                console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
                console.log('✅ BROADCAST COMPLETE - Monitoring for confirmation...');
                console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
                
            } catch (e) {
                console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
                console.error('❌ Transaction broadcast failed:', e.message);
                console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
                if (e.code === 'NONCE_EXPIRED' || e.code === 'REPLACEMENT_UNDERPRICED') {
                    console.log('⚠️ Nonce conflict detected, signal may be stale');
                    executionStatus = 'NONCE_CONFLICT';
                } else if (e.code === 'INSUFFICIENT_FUNDS') {
                    console.log('❌ Insufficient funds for transaction');
                    executionStatus = 'INSUFFICIENT_FUNDS';
                } else {
                    executionStatus = 'EXECUTION_FAILED';
                }
                return;
            }
            
        } catch (e) {
            console.error('❌ Unexpected error in executeTrade:', e);
            executionStatus = 'UNEXPECTED_ERROR';
        } finally {
            const duration = Date.now() - startTime;
            console.log(`⏱️ Execution completed in ${duration}ms with status: ${executionStatus}\n`);
        }
    }

    /**
     * Execute cross-chain arbitrage using Li.Fi for intent-based bridging.
     * 
     * Flow:
     * 1. Bridge assets from source chain to destination chain (via Li.Fi)
     * 2. Wait for bridge completion (intent-based = ~60s)
     * 3. Execute arbitrage trade on destination chain
     * 4. Optional: Bridge profits back or leave on destination chain
     */
    async executeCrossChainArbitrage(signal) {
        const startTime = Date.now();
        console.log('\n🌉 CROSS-CHAIN ARBITRAGE EXECUTION');
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        
        try {
            // Validate cross-chain signal structure
            if (!signal.source_chain || !signal.dest_chain) {
                console.error('❌ Invalid cross-chain signal: missing source/dest chains');
                return;
            }

            const srcChain = signal.source_chain;
            const dstChain = signal.dest_chain;
            const token = signal.token;
            const amount = signal.amount;

            // Validate chain IDs
            if (!RPC_MAP[srcChain] || !RPC_MAP[dstChain]) {
                console.error(`❌ Unsupported chain ID: ${srcChain} or ${dstChain}`);
                return;
            }

            // Validate token address
            if (!token || !ethers.utils.isAddress(token)) {
                console.error(`❌ Invalid token address: ${token}`);
                return;
            }

            // Validate amount
            if (
                amount === undefined ||
                amount === null ||
                isNaN(amount) ||
                (typeof amount === 'string' && amount.trim() === '') ||
                BigInt(amount) <= 0n
            ) {
                console.error(`❌ Invalid amount: ${amount}`);
                return;
            }
            
            console.log(`   Source Chain: ${srcChain}`);
            console.log(`   Destination Chain: ${dstChain}`);
            console.log(`   Token: ${token}`);
            console.log(`   Amount: ${amount}`);
            console.log(`   Expected Bridge Time: ${signal.bridge_time || '60'}s`);
            console.log(`   Expected Profit: $${signal.metrics?.profit_usd || 'N/A'}`);
            
            // Step 1: Bridge assets using Li.Fi
            console.log('\n📤 Step 1: Initiating bridge transaction via Li.Fi...');
            const bridgeResult = await LifiExecutionEngine.bridgeAssets(
                srcChain,
                dstChain,
                token,
                signal.dest_token || token, // Use same token for arbitrage
                amount,
                {
                    order: 'FASTEST',      // Optimize for speed
                    slippage: 0.005,       // 0.5% slippage
                    preferIntentBased: true // Use Across/Stargate for speed
                }
            );
            
            if (!bridgeResult.success) {
                console.error(`❌ Bridge initiation failed: ${bridgeResult.error}`);
                return;
            }
            
            console.log(`✅ Bridge transaction submitted!`);
            console.log(`   TX Hash: ${bridgeResult.transactionHash}`);
            console.log(`   Bridge: ${bridgeResult.bridgeName}`);
            console.log(`   Est. Time: ${bridgeResult.estimatedTime}s`);
            console.log(`   Gas Cost: $${bridgeResult.gasCostUSD}`);
            
            // Step 2: Monitor bridge completion
            console.log(`\n⏳ Step 2: Monitoring bridge completion...`);
            const completionResult = await LifiExecutionEngine.waitForCompletion(
                bridgeResult.transactionHash,
                srcChain,
                dstChain,
                600,  // 10 minute max wait
                5     // Check every 5 seconds
            );
            
            if (!completionResult.success) {
                console.error(`❌ Bridge failed or timed out: ${completionResult.error}`);
                return;
            }
            
            console.log(`✅ Bridge completed successfully!`);
            console.log(`   Completion Time: ${completionResult.completedAt}`);
            
            // Step 3: Execute arbitrage trade on destination chain
            console.log(`\n💹 Step 3: Executing arbitrage trade on destination chain...`);
            
            // Create a new signal for destination chain execution
            const dstSignal = {
                ...signal,
                chainId: dstChain,
                token: signal.dest_token || token,
                strategy_type: 'SINGLE_CHAIN' // Execute as normal trade now
            };
            
            // Execute the trade on destination chain
            await this.executeTrade(dstSignal);
            
            const totalDuration = Date.now() - startTime;
            console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
            console.log(`✅ CROSS-CHAIN ARBITRAGE COMPLETED in ${totalDuration}ms`);
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
            
        } catch (error) {
            console.error('❌ Cross-chain arbitrage failed:', error.message);
            console.error(error.stack);
        }
    }
    
    async _monitorTransaction(tx, provider, signal) {
        try {
            console.log('⏳ Monitoring transaction...');
            const receipt = await tx.wait(1);
            
            if (receipt.status === 1) {
                console.log('✅ Transaction confirmed successfully');
                console.log(`   Gas used: ${receipt.gasUsed.toString()}`);
                console.log(`   Block: ${receipt.blockNumber}`);
                
                // Calculate actual profit (simplified)
                const gasUsed = receipt.gasUsed;
                const gasPrice = receipt.gasPrice || tx.maxFeePerGas;
                const gasCostWei = gasUsed * gasPrice;
                const gasCostEth = ethers.formatEther(gasCostWei);
                
                console.log(`   Gas cost: ${gasCostEth} ETH`);
                
                if (signal.metrics?.profit_usd) {
                    console.log(`   Expected profit: $${signal.metrics.profit_usd}`);
                }
            } else {
                console.log('❌ Transaction reverted on-chain');
            }
        } catch (e) {
            console.log('⚠️ Transaction monitoring failed:', e.message);
            console.log('   Transaction may still succeed, check explorer');
        }
    }
    
    /**
     * Get block explorer URL for a transaction hash
     * @param {number} chainId - The chain ID
     * @param {string} txHash - The transaction hash
     * @returns {string} Block explorer URL
     */
    _getExplorerUrl(chainId, txHash) {
        const explorers = {
            1: 'https://etherscan.io/tx/',
            137: 'https://polygonscan.com/tx/',
            42161: 'https://arbiscan.io/tx/',
            10: 'https://optimistic.etherscan.io/tx/',
            8453: 'https://basescan.org/tx/',
            56: 'https://bscscan.com/tx/',
            43114: 'https://snowtrace.io/tx/',
            250: 'https://ftmscan.com/tx/',
            59144: 'https://lineascan.build/tx/',
            534352: 'https://scrollscan.com/tx/',
            5000: 'https://explorer.mantle.xyz/tx/',
            324: 'https://explorer.zksync.io/tx/',
            81457: 'https://blastscan.io/tx/',
            42220: 'https://celoscan.io/tx/',
            204: 'https://opbnbscan.com/tx/'
        };
        
        return (explorers[chainId] || 'https://etherscan.io/tx/') + txHash;
    }
}

new TitanBot().init();