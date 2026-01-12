#!/usr/bin/env python3
"""
Cache Manager for Titan2.0 - SQLite-based replacement for Redis
Provides in-memory and persistent caching for gas prices, opportunities, and metrics
"""

import sqlite3
import json
import time
import os
from pathlib import Path
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import threading
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """
    SQLite-based cache manager with in-memory fallback.
    Replaces Redis for caching data with automatic expiration.
    """
    
    def __init__(self, db_path: str = None, in_memory: bool = False):
        """
        Initialize cache manager
        
        Args:
            db_path: Path to SQLite database file (default: data/cache.db)
            in_memory: Use in-memory SQLite database (for testing)
        """
        self.in_memory = in_memory
        
        if in_memory:
            # In-memory database - keep persistent connection
            self.db_path = ":memory:"
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        elif db_path:
            self.db_path = db_path
            self._conn = None  # Will create connections as needed
        else:
            # Default cache location
            cache_dir = Path(__file__).parent.parent.parent / "data" / "cache"
            cache_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = str(cache_dir / "titan_cache.db")
            self._conn = None  # Will create connections as needed
        
        self.lock = threading.Lock()
        self._init_db()
        
        logger.info(f"📦 Cache Manager initialized: {self.db_path}")
    
    def _get_conn(self):
        """Get a database connection"""
        if self._conn:
            # Use persistent in-memory connection
            return self._conn
        else:
            # Create new connection for file-based DB
            return sqlite3.connect(self.db_path)
    
    def _close_conn(self, conn):
        """Close connection if it's not the persistent one"""
        if conn is not self._conn:
            conn.close()
    
    def _init_db(self):
        """Initialize SQLite database with required tables"""
        with self.lock:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            # Main cache table with TTL
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    expires_at REAL NOT NULL,
                    created_at REAL NOT NULL
                )
            """)
            
            # Gas prices cache (optimized for frequent reads)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gas_prices (
                    chain_id INTEGER PRIMARY KEY,
                    price_gwei REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    expires_at REAL NOT NULL
                )
            """)
            
            # Metrics cache (for dashboards)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    metric_name TEXT PRIMARY KEY,
                    metric_value TEXT NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            
            # Create indices for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache(expires_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_gas_expires ON gas_prices(expires_at)")
            
            conn.commit()
            self._close_conn(conn)
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Set a cache value with TTL (time to live)
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default: 300 = 5 minutes)
            
        Returns:
            bool: True if successful
        """
        try:
            with self.lock:
                conn = self._get_conn()
                cursor = conn.cursor()
                
                now = time.time()
                expires_at = now + ttl
                value_json = json.dumps(value)
                
                cursor.execute("""
                    INSERT OR REPLACE INTO cache (key, value, expires_at, created_at)
                    VALUES (?, ?, ?, ?)
                """, (key, value_json, expires_at, now))
                
                conn.commit()
                self._close_conn(conn)
                
                return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a cache value
        
        Args:
            key: Cache key
            default: Default value if key not found or expired
            
        Returns:
            Cached value or default
        """
        try:
            with self.lock:
                conn = self._get_conn()
                cursor = conn.cursor()
                
                now = time.time()
                
                cursor.execute("""
                    SELECT value, expires_at FROM cache
                    WHERE key = ? AND expires_at > ?
                """, (key, now))
                
                row = cursor.fetchone()
                self._close_conn(conn)
                
                if row:
                    value_json, _ = row
                    return json.loads(value_json)
                
                return default
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return default
    
    def delete(self, key: str) -> bool:
        """Delete a cache key"""
        try:
            with self.lock:
                conn = self._get_conn()
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM cache WHERE key = ?", (key,))
                
                conn.commit()
                self._close_conn(conn)
                
                return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def set_gas_price(self, chain_id: int, price_gwei: float, ttl: int = 60) -> bool:
        """
        Set gas price for a chain with TTL
        
        Args:
            chain_id: Chain ID
            price_gwei: Gas price in gwei
            ttl: Time to live in seconds (default: 60)
            
        Returns:
            bool: True if successful
        """
        try:
            with self.lock:
                conn = self._get_conn()
                cursor = conn.cursor()
                
                now = time.time()
                expires_at = now + ttl
                
                cursor.execute("""
                    INSERT OR REPLACE INTO gas_prices (chain_id, price_gwei, updated_at, expires_at)
                    VALUES (?, ?, ?, ?)
                """, (chain_id, price_gwei, now, expires_at))
                
                conn.commit()
                self._close_conn(conn)
                
                return True
        except Exception as e:
            logger.error(f"Gas price cache error for chain {chain_id}: {e}")
            return False
    
    def get_gas_price(self, chain_id: int, default: float = 0.0) -> float:
        """
        Get cached gas price for a chain
        
        Args:
            chain_id: Chain ID
            default: Default value if not found or expired
            
        Returns:
            Gas price in gwei
        """
        try:
            with self.lock:
                conn = self._get_conn()
                cursor = conn.cursor()
                
                now = time.time()
                
                cursor.execute("""
                    SELECT price_gwei FROM gas_prices
                    WHERE chain_id = ? AND expires_at > ?
                """, (chain_id, now))
                
                row = cursor.fetchone()
                self._close_conn(conn)
                
                if row:
                    return row[0]
                
                return default
        except Exception as e:
            logger.error(f"Gas price get error for chain {chain_id}: {e}")
            return default
    
    def set_metric(self, metric_name: str, metric_value: Any) -> bool:
        """
        Set a metric value (never expires)
        
        Args:
            metric_name: Metric name
            metric_value: Metric value (will be JSON serialized)
            
        Returns:
            bool: True if successful
        """
        try:
            with self.lock:
                conn = self._get_conn()
                cursor = conn.cursor()
                
                now = time.time()
                value_json = json.dumps(metric_value)
                
                cursor.execute("""
                    INSERT OR REPLACE INTO metrics (metric_name, metric_value, updated_at)
                    VALUES (?, ?, ?)
                """, (metric_name, value_json, now))
                
                conn.commit()
                self._close_conn(conn)
                
                return True
        except Exception as e:
            logger.error(f"Metric set error for {metric_name}: {e}")
            return False
    
    def get_metric(self, metric_name: str, default: Any = None) -> Any:
        """
        Get a metric value
        
        Args:
            metric_name: Metric name
            default: Default value if not found
            
        Returns:
            Metric value or default
        """
        try:
            with self.lock:
                conn = self._get_conn()
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT metric_value FROM metrics
                    WHERE metric_name = ?
                """, (metric_name,))
                
                row = cursor.fetchone()
                self._close_conn(conn)
                
                if row:
                    return json.loads(row[0])
                
                return default
        except Exception as e:
            logger.error(f"Metric get error for {metric_name}: {e}")
            return default
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics as a dictionary"""
        try:
            with self.lock:
                conn = self._get_conn()
                cursor = conn.cursor()
                
                cursor.execute("SELECT metric_name, metric_value FROM metrics")
                
                metrics = {}
                for row in cursor.fetchall():
                    name, value_json = row
                    metrics[name] = json.loads(value_json)
                
                self._close_conn(conn)
                
                return metrics
        except Exception as e:
            logger.error(f"Get all metrics error: {e}")
            return {}
    
    def cleanup_expired(self) -> int:
        """
        Clean up expired cache entries
        
        Returns:
            Number of entries deleted
        """
        try:
            with self.lock:
                conn = self._get_conn()
                cursor = conn.cursor()
                
                now = time.time()
                
                # Clean cache table
                cursor.execute("DELETE FROM cache WHERE expires_at < ?", (now,))
                cache_deleted = cursor.rowcount
                
                # Clean gas prices table
                cursor.execute("DELETE FROM gas_prices WHERE expires_at < ?", (now,))
                gas_deleted = cursor.rowcount
                
                conn.commit()
                self._close_conn(conn)
                
                total_deleted = cache_deleted + gas_deleted
                if total_deleted > 0:
                    logger.debug(f"Cleaned up {total_deleted} expired cache entries")
                
                return total_deleted
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            return 0
    
    def clear_all(self) -> bool:
        """Clear all cache data"""
        try:
            with self.lock:
                conn = self._get_conn()
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM cache")
                cursor.execute("DELETE FROM gas_prices")
                cursor.execute("DELETE FROM metrics")
                
                conn.commit()
                self._close_conn(conn)
                
                logger.info("Cache cleared")
                return True
        except Exception as e:
            logger.error(f"Clear cache error: {e}")
            return False
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        try:
            with self.lock:
                conn = self._get_conn()
                cursor = conn.cursor()
                
                now = time.time()
                
                cursor.execute("SELECT COUNT(*) FROM cache WHERE expires_at > ?", (now,))
                active_cache = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM cache WHERE expires_at <= ?", (now,))
                expired_cache = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM gas_prices WHERE expires_at > ?", (now,))
                active_gas = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM metrics")
                total_metrics = cursor.fetchone()[0]
                
                self._close_conn(conn)
                
                return {
                    "active_cache_entries": active_cache,
                    "expired_cache_entries": expired_cache,
                    "active_gas_prices": active_gas,
                    "total_metrics": total_metrics
                }
        except Exception as e:
            logger.error(f"Get stats error: {e}")
            return {}


# Singleton instance
_cache_manager = None
_cache_lock = threading.Lock()


def get_cache_manager(db_path: str = None, in_memory: bool = False) -> CacheManager:
    """
    Get or create the singleton cache manager instance
    
    Args:
        db_path: Path to SQLite database file (only used on first call)
        in_memory: Use in-memory database (only used on first call)
        
    Returns:
        CacheManager instance
    """
    global _cache_manager
    
    with _cache_lock:
        if _cache_manager is None:
            _cache_manager = CacheManager(db_path=db_path, in_memory=in_memory)
        
        return _cache_manager


if __name__ == "__main__":
    # Test the cache manager
    logging.basicConfig(level=logging.INFO)
    
    cache = get_cache_manager(in_memory=True)
    
    # Test basic caching
    cache.set("test_key", {"value": 123}, ttl=10)
    print("Set test_key:", cache.get("test_key"))
    
    # Test gas price caching
    cache.set_gas_price(1, 30.5, ttl=60)
    cache.set_gas_price(137, 50.0, ttl=60)
    print("Gas price ETH:", cache.get_gas_price(1))
    print("Gas price Polygon:", cache.get_gas_price(137))
    
    # Test metrics
    cache.set_metric("total_trades", 42)
    cache.set_metric("total_profit", 123.45)
    print("Metrics:", cache.get_all_metrics())
    
    # Test stats
    print("Cache stats:", cache.get_stats())
    
    # Test cleanup
    time.sleep(11)  # Wait for test_key to expire
    deleted = cache.cleanup_expired()
    print(f"Cleaned up {deleted} expired entries")
    print("test_key after expiry:", cache.get("test_key", "NOT_FOUND"))
