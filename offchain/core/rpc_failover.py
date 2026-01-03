"""
CRITICAL FIX #10: RPC Failover Provider
Provides automatic failover between multiple RPC endpoints for robust mainnet operations
"""
import logging
import threading
from web3 import Web3
from typing import List, Optional

logger = logging.getLogger(__name__)

# Multiple RPC endpoints per chain for failover
RPC_ENDPOINTS = {
    # Ethereum Mainnet
    1: [
        "https://eth.llamarpc.com",
        "https://rpc.ankr.com/eth",
        "https://ethereum.publicnode.com",
        "https://eth-mainnet.public.blastapi.io"
    ],
    # Polygon
    137: [
        "https://polygon-rpc.com",
        "https://rpc-mainnet.matic.network",
        "https://polygon-mainnet.public.blastapi.io",
        "https://rpc.ankr.com/polygon"
    ],
    # Arbitrum
    42161: [
        "https://arb1.arbitrum.io/rpc",
        "https://rpc.ankr.com/arbitrum",
        "https://arbitrum-one.public.blastapi.io"
    ],
    # Optimism
    10: [
        "https://mainnet.optimism.io",
        "https://rpc.ankr.com/optimism",
        "https://optimism-mainnet.public.blastapi.io"
    ],
    # Base
    8453: [
        "https://mainnet.base.org",
        "https://base-mainnet.public.blastapi.io",
        "https://base.llamarpc.com"
    ],
    # BSC
    56: [
        "https://bsc-dataseed.binance.org",
        "https://rpc.ankr.com/bsc",
        "https://bsc-mainnet.public.blastapi.io"
    ],
    # Avalanche
    43114: [
        "https://api.avax.network/ext/bc/C/rpc",
        "https://rpc.ankr.com/avalanche",
        "https://avalanche-c-chain.publicnode.com"
    ]
}


class FailoverWeb3Provider:
    """
    Web3 provider with automatic failover between multiple RPC endpoints.
    
    Features:
    - Multiple RPC endpoints per chain
    - Automatic failover on connection failures
    - Health monitoring and recovery
    - Round-robin load balancing
    - Thread-safe operations
    """
    
    def __init__(self, chain_id: int, custom_endpoints: Optional[List[str]] = None, 
                 timeout: int = 10):
        """
        Initialize failover provider for a specific chain.
        
        Args:
            chain_id: The blockchain chain ID
            custom_endpoints: Optional list of custom RPC endpoints to use instead of defaults
            timeout: RPC request timeout in seconds (default: 10 for HFT operations)
        """
        self.chain_id = chain_id
        self.endpoints = custom_endpoints or RPC_ENDPOINTS.get(chain_id, [])
        self.timeout = timeout  # Configurable timeout
        
        if not self.endpoints:
            raise ValueError(f"No RPC endpoints configured for chain {chain_id}")
        
        self.current_idx = 0
        self.failed_endpoints = set()
        self.web3 = None
        self._lock = threading.Lock()  # Thread safety for multi-threaded operations
        self._connect()
    
    def _connect(self) -> bool:
        """
        Attempt to connect to an RPC endpoint.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        with self._lock:  # Thread-safe endpoint selection
            attempts = 0
            max_attempts = len(self.endpoints)
            
            while attempts < max_attempts:
                endpoint = self.endpoints[self.current_idx]
                
                # Skip recently failed endpoints (but retry eventually)
                if endpoint in self.failed_endpoints and attempts < max_attempts - 1:
                    self.current_idx = (self.current_idx + 1) % len(self.endpoints)
                    attempts += 1
                    continue
                
                try:
                    provider = Web3.HTTPProvider(
                        endpoint,
                        request_kwargs={'timeout': self.timeout}
                    )
                    test_web3 = Web3(provider)
                    
                    # Test connectivity by getting block number
                    block_number = test_web3.eth.block_number
                    
                    # Connection successful
                    self.web3 = test_web3
                    logger.info(f"✅ Connected to chain {self.chain_id} via {endpoint} (block: {block_number})")
                    
                    # Remove from failed set if it was there (endpoint recovered)
                    if endpoint in self.failed_endpoints:
                        self.failed_endpoints.discard(endpoint)  # Thread-safe remove
                        logger.info(f"🔄 RPC endpoint {endpoint} recovered")
                    
                    return True
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to connect to {endpoint}: {str(e)[:100]}")
                    self.failed_endpoints.add(endpoint)
                    self.current_idx = (self.current_idx + 1) % len(self.endpoints)
                    attempts += 1
            
            logger.error(f"❌ All RPC endpoints failed for chain {self.chain_id}")
            return False
    
    def get_web3(self) -> Optional[Web3]:
        """
        Get Web3 instance with automatic reconnection on failures.
        
        Returns:
            Web3 instance or None if all endpoints failed
        """
        if self.web3 is None:
            self._connect()
        
        return self.web3
    
    def health_check(self) -> bool:
        """
        Check if current connection is healthy with retry.
        
        Returns:
            bool: True if healthy, False otherwise
        """
        if self.web3 is None:
            return False
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Try to get latest block
                block_number = self.web3.eth.block_number
                logger.debug(f"Health check passed: block {block_number}")
                return True
            except Exception as e:
                logger.warning(f"Health check failed (attempt {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    # Wait a bit before retry
                    import time
                    time.sleep(1)
                else:
                    # Final attempt failed, try to reconnect
                    with self._lock:
                        current_endpoint = self.endpoints[self.current_idx]
                        self.failed_endpoints.add(current_endpoint)
                        logger.warning(f"⚠️ Marking endpoint as failed: {current_endpoint}")
                        self.current_idx = (self.current_idx + 1) % len(self.endpoints)
                    return self._connect()
        
        return False
    
    def automated_health_monitoring(self, interval_seconds: int = 60):
        """
        Start automated health monitoring in background thread.
        
        Args:
            interval_seconds: How often to run health checks (default: 60s)
        """
        import threading
        import time
        
        def monitor():
            while True:
                if not self.health_check():
                    logger.error(f"❌ Health check failed for chain {self.chain_id}, attempting recovery")
                else:
                    logger.debug(f"✅ Health check passed for chain {self.chain_id}")
                time.sleep(interval_seconds)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        logger.info(f"🏥 Started automated health monitoring for chain {self.chain_id} (interval: {interval_seconds}s)")
    
    def switch_endpoint(self):
        """Manually switch to next RPC endpoint (useful for load balancing)"""
        with self._lock:  # Thread-safe switching
            self.current_idx = (self.current_idx + 1) % len(self.endpoints)
        self._connect()


def get_failover_web3(chain_id: int, custom_endpoints: Optional[List[str]] = None,
                      timeout: int = 10) -> Optional[Web3]:
def get_failover_web3(chain_id: int, custom_endpoints: Optional[List[str]] = None,
                      timeout: int = 10) -> Optional[Web3]:
    """
    Convenience function to get a Web3 instance with failover support.
    
    Args:
        chain_id: The blockchain chain ID
        custom_endpoints: Optional list of custom RPC endpoints
        timeout: RPC request timeout in seconds (default: 10 for HFT)
        
    Returns:
        Web3 instance or None if all endpoints failed
    """
    provider = FailoverWeb3Provider(chain_id, custom_endpoints, timeout)
    return provider.get_web3()


if __name__ == "__main__":
    # Test the failover provider
    logging.basicConfig(level=logging.INFO)
    
    # Test Polygon failover
    logger.info("Testing Polygon failover...")
    web3 = get_failover_web3(137)
    if web3:
        logger.info(f"✅ Polygon connected, latest block: {web3.eth.block_number}")
    else:
        logger.error("❌ Failed to connect to Polygon")
    
    # Test Ethereum failover
    logger.info("\nTesting Ethereum failover...")
    web3 = get_failover_web3(1)
    if web3:
        logger.info(f"✅ Ethereum connected, latest block: {web3.eth.block_number}")
    else:
        logger.error("❌ Failed to connect to Ethereum")
