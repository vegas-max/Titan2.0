"""
Trade History Database
Tracks all trade executions, profits, losses, and performance metrics
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class TradeDatabase:
    """
    SQLite database for tracking trade history and performance metrics
    """
    
    def __init__(self, db_path: str = "data/trade_history.db"):
        """
        Initialize trade database
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        logger.info(f"📊 Trade database initialized: {db_path}")
    
    def _init_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Trades table - main execution records
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT UNIQUE NOT NULL,
                timestamp REAL NOT NULL,
                chain_id INTEGER NOT NULL,
                token_in TEXT NOT NULL,
                token_out TEXT NOT NULL,
                amount_in TEXT NOT NULL,
                amount_out TEXT,
                expected_profit_usd REAL,
                actual_profit_usd REAL,
                gas_cost_usd REAL,
                net_profit_usd REAL,
                execution_mode TEXT NOT NULL,
                status TEXT NOT NULL,
                tx_hash TEXT,
                error_message TEXT,
                route_info TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Performance metrics table - aggregated statistics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                chain_id INTEGER,
                total_trades INTEGER DEFAULT 0,
                successful_trades INTEGER DEFAULT 0,
                failed_trades INTEGER DEFAULT 0,
                total_profit_usd REAL DEFAULT 0,
                total_loss_usd REAL DEFAULT 0,
                total_gas_cost_usd REAL DEFAULT 0,
                net_profit_usd REAL DEFAULT 0,
                avg_profit_per_trade REAL DEFAULT 0,
                best_trade_profit REAL DEFAULT 0,
                worst_trade_loss REAL DEFAULT 0,
                success_rate REAL DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, chain_id)
            )
        ''')
        
        # Circuit breaker events table - track system health
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS circuit_breaker_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                event_type TEXT NOT NULL,
                consecutive_failures INTEGER,
                recovery_time REAL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # RPC failover events table - track RPC reliability
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rpc_failover_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                chain_id INTEGER NOT NULL,
                failed_endpoint TEXT NOT NULL,
                new_endpoint TEXT NOT NULL,
                failure_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indices for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_trades_timestamp 
            ON trades(timestamp DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_trades_chain_id 
            ON trades(chain_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_trades_status 
            ON trades(status)
        ''')
        
        conn.commit()
        conn.close()
    
    def record_trade(self, trade_data: Dict) -> bool:
        """
        Record a trade execution
        
        Args:
            trade_data: Dictionary containing trade information
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert route info to JSON string
            route_info = json.dumps(trade_data.get('route_info', {}))
            
            cursor.execute('''
                INSERT INTO trades (
                    trade_id, timestamp, chain_id, token_in, token_out,
                    amount_in, amount_out, expected_profit_usd, actual_profit_usd,
                    gas_cost_usd, net_profit_usd, execution_mode, status,
                    tx_hash, error_message, route_info
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade_data.get('trade_id'),
                trade_data.get('timestamp'),
                trade_data.get('chain_id'),
                trade_data.get('token_in'),
                trade_data.get('token_out'),
                str(trade_data.get('amount_in', '')),
                str(trade_data.get('amount_out', '')),
                trade_data.get('expected_profit_usd'),
                trade_data.get('actual_profit_usd'),
                trade_data.get('gas_cost_usd'),
                trade_data.get('net_profit_usd'),
                trade_data.get('execution_mode', 'UNKNOWN'),
                trade_data.get('status', 'UNKNOWN'),
                trade_data.get('tx_hash'),
                trade_data.get('error_message'),
                route_info
            ))
            
            conn.commit()
            conn.close()
            
            # Update daily metrics
            self._update_daily_metrics(trade_data)
            
            logger.info(f"✅ Trade recorded: {trade_data.get('trade_id')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record trade: {e}")
            return False
    
    def _update_daily_metrics(self, trade_data: Dict):
        """Update daily performance metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            date = datetime.fromtimestamp(trade_data.get('timestamp', 0)).strftime('%Y-%m-%d')
            chain_id = trade_data.get('chain_id')
            
            # Get current metrics
            cursor.execute('''
                SELECT total_trades, successful_trades, failed_trades,
                       total_profit_usd, total_loss_usd, total_gas_cost_usd,
                       best_trade_profit, worst_trade_loss
                FROM performance_metrics
                WHERE date = ? AND chain_id = ?
            ''', (date, chain_id))
            
            row = cursor.fetchone()
            
            if row:
                total_trades, successful, failed, total_profit, total_loss, total_gas, best_profit, worst_loss = row
            else:
                total_trades = successful = failed = 0
                total_profit = total_loss = total_gas = 0
                best_profit = worst_loss = 0
            
            # Update counters
            total_trades += 1
            is_success = trade_data.get('status') == 'SUCCESS'
            if is_success:
                successful += 1
            else:
                failed += 1
            
            # Update profit/loss
            net_profit = trade_data.get('net_profit_usd', 0) or 0
            gas_cost = trade_data.get('gas_cost_usd', 0) or 0
            
            if net_profit > 0:
                total_profit += net_profit
                best_profit = max(best_profit, net_profit)
            else:
                total_loss += abs(net_profit)
                worst_loss = min(worst_loss, net_profit)
            
            total_gas += gas_cost
            
            # Calculate metrics
            net_total = total_profit - total_loss
            avg_profit = net_total / total_trades if total_trades > 0 else 0
            success_rate = (successful / total_trades * 100) if total_trades > 0 else 0
            
            # Upsert metrics
            cursor.execute('''
                INSERT INTO performance_metrics (
                    date, chain_id, total_trades, successful_trades, failed_trades,
                    total_profit_usd, total_loss_usd, total_gas_cost_usd, net_profit_usd,
                    avg_profit_per_trade, best_trade_profit, worst_trade_loss, success_rate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(date, chain_id) DO UPDATE SET
                    total_trades = excluded.total_trades,
                    successful_trades = excluded.successful_trades,
                    failed_trades = excluded.failed_trades,
                    total_profit_usd = excluded.total_profit_usd,
                    total_loss_usd = excluded.total_loss_usd,
                    total_gas_cost_usd = excluded.total_gas_cost_usd,
                    net_profit_usd = excluded.net_profit_usd,
                    avg_profit_per_trade = excluded.avg_profit_per_trade,
                    best_trade_profit = excluded.best_trade_profit,
                    worst_trade_loss = excluded.worst_trade_loss,
                    success_rate = excluded.success_rate,
                    updated_at = CURRENT_TIMESTAMP
            ''', (
                date, chain_id, total_trades, successful, failed,
                total_profit, total_loss, total_gas, net_total,
                avg_profit, best_profit, worst_loss, success_rate
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to update daily metrics: {e}")
    
    def record_circuit_breaker_event(self, event_type: str, consecutive_failures: int, 
                                     recovery_time: Optional[float] = None, 
                                     details: Optional[str] = None):
        """Record circuit breaker event"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO circuit_breaker_events (
                    timestamp, event_type, consecutive_failures, recovery_time, details
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now().timestamp(),
                event_type,
                consecutive_failures,
                recovery_time,
                details
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Circuit breaker event recorded: {event_type}")
            
        except Exception as e:
            logger.error(f"Failed to record circuit breaker event: {e}")
    
    def record_rpc_failover(self, chain_id: int, failed_endpoint: str, 
                           new_endpoint: str, failure_reason: Optional[str] = None):
        """Record RPC failover event"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO rpc_failover_events (
                    timestamp, chain_id, failed_endpoint, new_endpoint, failure_reason
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now().timestamp(),
                chain_id,
                failed_endpoint,
                new_endpoint,
                failure_reason
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"RPC failover recorded for chain {chain_id}: {failed_endpoint} -> {new_endpoint}")
            
        except Exception as e:
            logger.error(f"Failed to record RPC failover: {e}")
    
    def get_recent_trades(self, limit: int = 100, chain_id: Optional[int] = None) -> List[Dict]:
        """Get recent trades"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if chain_id:
                cursor.execute('''
                    SELECT * FROM trades 
                    WHERE chain_id = ?
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (chain_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM trades 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
            
            columns = [desc[0] for desc in cursor.description]
            trades = []
            
            for row in cursor.fetchall():
                trade = dict(zip(columns, row))
                # Parse JSON fields
                if trade.get('route_info'):
                    try:
                        trade['route_info'] = json.loads(trade['route_info'])
                    except:
                        pass
                trades.append(trade)
            
            conn.close()
            return trades
            
        except Exception as e:
            logger.error(f"Failed to get recent trades: {e}")
            return []
    
    def get_daily_metrics(self, days: int = 7) -> List[Dict]:
        """Get daily performance metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM performance_metrics 
                ORDER BY date DESC 
                LIMIT ?
            ''', (days,))
            
            columns = [desc[0] for desc in cursor.description]
            metrics = []
            
            for row in cursor.fetchall():
                metrics.append(dict(zip(columns, row)))
            
            conn.close()
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get daily metrics: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """Get overall statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Overall stats
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as successful,
                    SUM(CASE WHEN status != 'SUCCESS' THEN 1 ELSE 0 END) as failed,
                    SUM(net_profit_usd) as total_net_profit,
                    AVG(net_profit_usd) as avg_profit,
                    MAX(net_profit_usd) as best_trade,
                    MIN(net_profit_usd) as worst_trade,
                    SUM(gas_cost_usd) as total_gas_cost
                FROM trades
            ''')
            
            row = cursor.fetchone()
            
            stats = {
                'total_trades': row[0] or 0,
                'successful_trades': row[1] or 0,
                'failed_trades': row[2] or 0,
                'total_net_profit_usd': row[3] or 0,
                'avg_profit_usd': row[4] or 0,
                'best_trade_usd': row[5] or 0,
                'worst_trade_usd': row[6] or 0,
                'total_gas_cost_usd': row[7] or 0,
                'success_rate': (row[1] / row[0] * 100) if row[0] > 0 else 0
            }
            
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}


# Singleton instance
_db_instance = None


def get_trade_database(db_path: str = "data/trade_history.db") -> TradeDatabase:
    """
    Get singleton instance of trade database
    
    Args:
        db_path: Path to database file
        
    Returns:
        TradeDatabase instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = TradeDatabase(db_path)
    return _db_instance
