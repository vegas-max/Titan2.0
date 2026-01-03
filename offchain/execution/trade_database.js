const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

/**
 * Trade Database Manager (JavaScript wrapper for Python SQLite database)
 * Records trade executions, profits, and performance metrics
 */
class TradeDatabase {
    constructor() {
        this.pythonScript = path.join(__dirname, '..', 'core', 'trade_database.py');
        this.enabled = this._checkDatabaseAvailable();
        
        if (this.enabled) {
            console.log('✅ Trade history database enabled');
        } else {
            console.log('⚠️ Trade history database not available (Python module missing)');
        }
    }

    /**
     * Check if database module is available
     */
    _checkDatabaseAvailable() {
        try {
            // Check if Python file exists
            return fs.existsSync(this.pythonScript);
        } catch (e) {
            return false;
        }
    }

    /**
     * Record a trade execution
     * @param {object} tradeData - Trade information
     * @returns {Promise<boolean>} Success status
     */
    async recordTrade(tradeData) {
        if (!this.enabled) {
            return false;
        }

        try {
            const trade = {
                trade_id: tradeData.tradeId || `trade-${Date.now()}`,
                timestamp: tradeData.timestamp || Date.now() / 1000,
                chain_id: tradeData.chainId,
                token_in: tradeData.tokenIn,
                token_out: tradeData.tokenOut || tradeData.tokenIn,
                amount_in: tradeData.amountIn,
                amount_out: tradeData.amountOut,
                expected_profit_usd: tradeData.expectedProfit || 0,
                actual_profit_usd: tradeData.actualProfit,
                gas_cost_usd: tradeData.gasCost || 0,
                net_profit_usd: tradeData.netProfit,
                execution_mode: tradeData.executionMode || 'PAPER',
                status: tradeData.status || 'UNKNOWN',
                tx_hash: tradeData.txHash,
                error_message: tradeData.error,
                route_info: {
                    protocols: tradeData.protocols || [],
                    routers: tradeData.routers || [],
                    path: tradeData.path || []
                }
            };

            // Write trade data to temporary file for Python to read
            const tempFile = path.join('/tmp', `trade_${Date.now()}.json`);
            fs.writeFileSync(tempFile, JSON.stringify(trade));

            // Execute Python script to record trade
            await this._executePythonCommand('record_trade', tempFile);
            
            // Cleanup temp file
            fs.unlinkSync(tempFile);
            
            console.log(`📊 Trade recorded in database: ${trade.trade_id}`);
            return true;

        } catch (error) {
            console.error('Failed to record trade in database:', error.message);
            return false;
        }
    }

    /**
     * Record circuit breaker event
     */
    async recordCircuitBreakerEvent(eventType, consecutiveFailures, recoveryTime = null, details = null) {
        if (!this.enabled) return false;

        try {
            const data = {
                event_type: eventType,
                consecutive_failures: consecutiveFailures,
                recovery_time: recoveryTime,
                details: details
            };

            const tempFile = path.join('/tmp', `circuit_breaker_${Date.now()}.json`);
            fs.writeFileSync(tempFile, JSON.stringify(data));
            
            await this._executePythonCommand('record_circuit_breaker', tempFile);
            fs.unlinkSync(tempFile);
            
            return true;
        } catch (error) {
            console.error('Failed to record circuit breaker event:', error.message);
            return false;
        }
    }

    /**
     * Record RPC failover event
     */
    async recordRPCFailover(chainId, failedEndpoint, newEndpoint, failureReason = null) {
        if (!this.enabled) return false;

        try {
            const data = {
                chain_id: chainId,
                failed_endpoint: failedEndpoint,
                new_endpoint: newEndpoint,
                failure_reason: failureReason
            };

            const tempFile = path.join('/tmp', `rpc_failover_${Date.now()}.json`);
            fs.writeFileSync(tempFile, JSON.stringify(data));
            
            await this._executePythonCommand('record_rpc_failover', tempFile);
            fs.unlinkSync(tempFile);
            
            return true;
        } catch (error) {
            console.error('Failed to record RPC failover:', error.message);
            return false;
        }
    }

    /**
     * Get statistics
     */
    async getStatistics() {
        if (!this.enabled) {
            return {
                total_trades: 0,
                successful_trades: 0,
                failed_trades: 0,
                total_net_profit_usd: 0,
                success_rate: 0
            };
        }

        try {
            const result = await this._executePythonCommand('get_statistics');
            return JSON.parse(result);
        } catch (error) {
            console.error('Failed to get statistics:', error.message);
            return {};
        }
    }

    /**
     * Execute Python command
     * @private
     */
    _executePythonCommand(command, dataFile = null) {
        return new Promise((resolve, reject) => {
            const args = [this.pythonScript, command];
            if (dataFile) {
                args.push(dataFile);
            }

            const python = spawn('python3', args);
            let output = '';
            let errorOutput = '';

            python.stdout.on('data', (data) => {
                output += data.toString();
            });

            python.stderr.on('data', (data) => {
                errorOutput += data.toString();
            });

            python.on('close', (code) => {
                if (code !== 0) {
                    reject(new Error(`Python process exited with code ${code}: ${errorOutput}`));
                } else {
                    resolve(output.trim());
                }
            });

            python.on('error', (error) => {
                reject(error);
            });
        });
    }
}

module.exports = { TradeDatabase };
