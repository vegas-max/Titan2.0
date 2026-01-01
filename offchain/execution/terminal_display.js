/**
 * Terminal Display for JavaScript (Bot.js)
 * Provides real-time, informative terminal output for executions
 */

// Color codes for terminal output
const Colors = {
    BLUE: '\x1b[94m',
    GREEN: '\x1b[92m',
    YELLOW: '\x1b[93m',
    RED: '\x1b[91m',
    CYAN: '\x1b[96m',
    MAGENTA: '\x1b[95m',
    WHITE: '\x1b[97m',
    BOLD: '\x1b[1m',
    UNDERLINE: '\x1b[4m',
    END: '\x1b[0m'
};

class TerminalDisplay {
    constructor() {
        this.startTime = new Date();
        this.stats = {
            executionsAttempted: 0,
            executionsSuccessful: 0,
            executionsFailed: 0,
            paperTrades: 0,
            totalProfitUSD: 0.0,
            signalsProcessed: 0
        };
        this.recentExecutions = [];
        this.maxRecentExecutions = 10;
        
        // Disable colors if not in a TTY
        if (!process.stdout.isTTY) {
            Object.keys(Colors).forEach(key => Colors[key] = '');
        }
    }

    printHeader(mode = 'PAPER') {
        console.log('\n' + '='.repeat(80));
        console.log(`${Colors.BOLD}${Colors.CYAN}🚀 APEX-OMEGA TITAN - Execution Engine${Colors.END}`);
        console.log('='.repeat(80));
        console.log(`${Colors.BOLD}Execution Mode:${Colors.END} ${mode === 'PAPER' ? Colors.GREEN : Colors.RED}${mode}${Colors.END}`);
        console.log(`${Colors.BOLD}Started:${Colors.END} ${this.startTime.toISOString()}`);
        console.log('='.repeat(80) + '\n');
    }

    printStatsBar() {
        const runtime = new Date() - this.startTime;
        const hours = Math.floor(runtime / 3600000);
        const minutes = Math.floor((runtime % 3600000) / 60000);
        const runtimeStr = `${hours}h ${minutes}m`;

        const successRate = this.stats.executionsAttempted > 0 
            ? (this.stats.executionsSuccessful / this.stats.executionsAttempted) * 100 
            : 0;

        console.log(`${Colors.CYAN}┌─ EXECUTOR STATS ${Colors.END}${'─'.repeat(62)}`);
        console.log(`${Colors.CYAN}│${Colors.END} Runtime: ${runtimeStr} | ` +
            `Signals: ${this.stats.signalsProcessed} | ` +
            `Executed: ${this.stats.executionsAttempted} ` +
            `(✓${this.stats.executionsSuccessful} / ✗${this.stats.executionsFailed}, ${successRate.toFixed(0)}%)`);
        console.log(`${Colors.CYAN}│${Colors.END} Paper Trades: ${this.stats.paperTrades} | ` +
            `Total Profit: $${this.stats.totalProfitUSD.toFixed(2)}`);
        console.log(`${Colors.CYAN}└${'─'.repeat(78)}${Colors.END}\n`);
    }

    logSignalReceived(signalId, token, chainId, profitUSD) {
        this.stats.signalsProcessed++;
        const timestamp = new Date().toLocaleTimeString();
        const chainName = this._getChainName(chainId);
        
        console.log(`${Colors.BLUE}📨 [${timestamp}] SIGNAL RECEIVED: ${signalId}${Colors.END}`);
        console.log(`   Token: ${token} | Chain: ${chainName} | Expected Profit: $${profitUSD.toFixed(2)}`);
    }

    logExecutionStart(tradeId, token, chainId, amount, mode = 'PAPER') {
        this.stats.executionsAttempted++;
        if (mode === 'PAPER') {
            this.stats.paperTrades++;
        }

        const timestamp = new Date().toLocaleTimeString();
        const chainName = this._getChainName(chainId);
        const icon = mode === 'PAPER' ? '📝' : '🔴';
        const color = mode === 'PAPER' ? Colors.YELLOW : Colors.RED;

        console.log(`\n${color}${Colors.BOLD}${'─'.repeat(80)}${Colors.END}`);
        console.log(`${color}${icon} EXECUTION START${Colors.END} [${timestamp}] | ID: ${tradeId}`);
        console.log(`  Token: ${token} | Chain: ${chainName} | Amount: ${amount} | Mode: ${mode}`);
        console.log(`${color}${'─'.repeat(80)}${Colors.END}`);
    }

    logExecutionComplete(tradeId, status, durationMs, profitUSD = null, txHash = null, error = null) {
        const timestamp = new Date().toLocaleTimeString();
        
        let color, icon;
        if (status === 'SUCCESS' || status === 'SIMULATED') {
            this.stats.executionsSuccessful++;
            if (profitUSD) {
                this.stats.totalProfitUSD += profitUSD;
            }
            color = Colors.GREEN;
            icon = '✅';
        } else {
            this.stats.executionsFailed++;
            color = Colors.RED;
            icon = '❌';
        }

        console.log(`${color}${icon} EXECUTION COMPLETE${Colors.END} [${timestamp}] | ID: ${tradeId}`);
        console.log(`  Status: ${status} | Duration: ${durationMs}ms`);
        
        if (profitUSD !== null) {
            console.log(`  Profit: $${profitUSD.toFixed(2)}`);
        }
        
        if (txHash) {
            console.log(`  TX: ${txHash}`);
        }
        
        if (error) {
            console.log(`  Error: ${error}`);
        }
        
        console.log(`${color}${'─'.repeat(80)}${Colors.END}\n`);

        // Track recent executions
        this.recentExecutions.push({
            time: timestamp,
            id: tradeId,
            status,
            duration: durationMs
        });
        if (this.recentExecutions.length > this.maxRecentExecutions) {
            this.recentExecutions.shift();
        }
    }

    logGasEstimate(chainId, gasPrice, estimatedCostUSD, profitUSD) {
        const chainName = this._getChainName(chainId);
        const timestamp = new Date().toLocaleTimeString();
        
        const profitable = profitUSD > estimatedCostUSD;
        const color = profitable ? Colors.GREEN : Colors.YELLOW;
        const icon = profitable ? '⛽' : '⚠️';
        
        console.log(`${color}${icon} [${timestamp}] GAS CHECK: ${chainName}${Colors.END}`);
        console.log(`  Gas Price: ${gasPrice} gwei | Est. Cost: $${estimatedCostUSD.toFixed(2)} | Profit: $${profitUSD.toFixed(2)}`);
        
        if (!profitable) {
            console.log(`  ${Colors.YELLOW}⚠️ Warning: Gas cost exceeds profit margin${Colors.END}`);
        }
    }

    logDecision(decisionType, token, chainId, reason, details = {}) {
        const chainName = this._getChainName(chainId);
        const timestamp = new Date().toLocaleTimeString();
        
        const iconMap = {
            'APPROVE': ['✅', Colors.GREEN],
            'REJECT': ['❌', Colors.RED],
            'VALIDATE': ['🔍', Colors.CYAN],
            'SIMULATE': ['🧪', Colors.MAGENTA],
            'GAS_CHECK': ['⛽', Colors.YELLOW]
        };
        
        const [icon, color] = iconMap[decisionType] || ['ℹ️', Colors.WHITE];
        
        let msg = `${color}${icon} [${timestamp}] ${decisionType}: ${token} on ${chainName} | ${reason}`;
        
        if (Object.keys(details).length > 0) {
            const detailParts = Object.entries(details).map(([k, v]) => {
                if (typeof v === 'number') {
                    return `${k}=${v.toFixed(2)}`;
                }
                return `${k}=${v}`;
            });
            if (detailParts.length > 0) {
                msg += ` | ${detailParts.join(', ')}`;
            }
        }
        
        msg += Colors.END;
        console.log(msg);
    }

    logError(component, error, details = '') {
        const timestamp = new Date().toLocaleTimeString();
        console.log(`${Colors.RED}❌ [${timestamp}] ERROR in ${component}: ${error}${Colors.END}`);
        if (details) {
            console.log(`${Colors.RED}   Details: ${details}${Colors.END}`);
        }
    }

    logWarning(component, warning) {
        const timestamp = new Date().toLocaleTimeString();
        console.log(`${Colors.YELLOW}⚠️ [${timestamp}] WARNING in ${component}: ${warning}${Colors.END}`);
    }

    logInfo(message) {
        const timestamp = new Date().toLocaleTimeString();
        console.log(`${Colors.BLUE}ℹ️ [${timestamp}] ${message}${Colors.END}`);
    }

    _getChainName(chainId) {
        const chainNames = {
            1: 'Ethereum',
            137: 'Polygon',
            42161: 'Arbitrum',
            10: 'Optimism',
            8453: 'Base',
            56: 'BSC',
            43114: 'Avalanche',
            250: 'Fantom',
            59144: 'Linea',
            534352: 'Scroll',
            5000: 'Mantle',
            324: 'zkSync',
            81457: 'Blast',
            42220: 'Celo',
            204: 'opBNB'
        };
        return chainNames[chainId] || `Chain-${chainId}`;
    }
}

// Export singleton instance
const terminalDisplay = new TerminalDisplay();
module.exports = { terminalDisplay, TerminalDisplay };
