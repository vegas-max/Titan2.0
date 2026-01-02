"""
MEV Detection Module
Detects sandwich attacks, frontrunning, and other MEV patterns before submission
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from decimal import Decimal, getcontext
from web3 import Web3
from eth_abi import decode
import time

logger = logging.getLogger("MEVDetector")
getcontext().prec = 28


@dataclass
class PendingTransaction:
    """Pending transaction in mempool"""
    hash: str
    from_address: str
    to_address: str
    value: int
    gas_price: int
    gas_limit: int
    data: str
    nonce: int
    timestamp: float


@dataclass
class MEVThreat:
    """Detected MEV threat"""
    threat_type: str  # 'sandwich', 'frontrun', 'backrun', 'liquidation'
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    affected_tokens: List[str]
    estimated_impact: Decimal  # Estimated profit loss in USD
    attacker_address: Optional[str]
    attacker_tx_hashes: List[str]
    timestamp: float
    
    def to_dict(self):
        return {
            'threat_type': self.threat_type,
            'severity': self.severity,
            'description': self.description,
            'affected_tokens': self.affected_tokens,
            'estimated_impact': float(self.estimated_impact),
            'attacker_address': self.attacker_address,
            'attacker_tx_hashes': self.attacker_tx_hashes,
            'timestamp': self.timestamp
        }


class MEVDetector:
    """
    Sophisticated MEV detection for sandwich attacks and frontrunning
    """
    
    def __init__(self, web3_connections: Dict[int, Web3]):
        self.web3 = web3_connections
        self.mempool_monitor = {}  # chainId -> list of pending txs
        self.known_mev_bots = self.load_known_mev_bots()
        self.detection_threshold = {
            'sandwich': Decimal('0.5'),  # 0.5% price impact threshold
            'frontrun': Decimal('1.0'),   # 1% profit threshold
        }
        
    def load_known_mev_bots(self) -> Dict[int, List[str]]:
        """
        Load known MEV bot addresses per chain
        This list should be updated regularly
        """
        return {
            1: [  # Ethereum
                '0x000000000035B5e5ad9019092C665357240f594e',  # Jaredfromsubway.eth
                '0x6b75d8AF000000e20B7a7DDf000Ba900b4009A80',  # MEV Bot
                '0x00000000003b3cc22aF3aE1EAc0440BcEe416B40',  # MEV Bot
                # Add more known MEV bots
            ],
            137: [  # Polygon
                '0x0000000000000000000000000000000000000000',  # Placeholder
                # Add known Polygon MEV bots
            ],
            56: [  # BSC
                '0x0000000000000000000000000000000000000000',  # Placeholder
                # Add known BSC MEV bots
            ]
        }
    
    def update_mempool(self, chain_id: int, pending_txs: List[Dict]):
        """
        Update mempool state with pending transactions
        
        Args:
            chain_id: Chain ID
            pending_txs: List of pending transaction dictionaries
        """
        if chain_id not in self.mempool_monitor:
            self.mempool_monitor[chain_id] = []
        
        current_time = time.time()
        
        # Convert to PendingTransaction objects
        parsed_txs = []
        for tx in pending_txs:
            try:
                parsed_tx = PendingTransaction(
                    hash=tx.get('hash', ''),
                    from_address=tx.get('from', ''),
                    to_address=tx.get('to', ''),
                    value=tx.get('value', 0),
                    gas_price=tx.get('gasPrice', 0),
                    gas_limit=tx.get('gas', 0),
                    data=tx.get('input', '0x'),
                    nonce=tx.get('nonce', 0),
                    timestamp=current_time
                )
                parsed_txs.append(parsed_tx)
            except Exception as e:
                logger.error(f"Failed to parse pending tx: {e}")
                continue
        
        # Keep only recent transactions (last 30 seconds)
        self.mempool_monitor[chain_id] = [
            tx for tx in self.mempool_monitor[chain_id]
            if current_time - tx.timestamp < 30
        ] + parsed_txs
        
        logger.debug(f"Mempool updated for chain {chain_id}: {len(self.mempool_monitor[chain_id])} pending txs")
    
    def detect_sandwich_attack(
        self,
        chain_id: int,
        our_tx: Dict,
        token_in: str,
        token_out: str,
        amount_in: Decimal
    ) -> Optional[MEVThreat]:
        """
        Detect potential sandwich attack targeting our transaction
        
        A sandwich attack consists of:
        1. Frontrun: Buy token_out before our trade (increases price)
        2. Our transaction: Executes at worse price
        3. Backrun: Sell token_out after our trade (profit from price difference)
        
        Args:
            chain_id: Chain ID
            our_tx: Our transaction dictionary
            token_in: Input token address
            token_out: Output token address
            amount_in: Our trade amount
            
        Returns:
            MEVThreat if detected, None otherwise
        """
        try:
            pending_txs = self.mempool_monitor.get(chain_id, [])
            
            if not pending_txs:
                return None
            
            our_gas_price = our_tx.get('gasPrice', 0)
            
            # Look for frontrun transactions (higher gas, same tokens, recent)
            potential_frontrun = []
            for tx in pending_txs:
                # Check if gas price is higher (frontrunning indicator)
                if tx.gas_price <= our_gas_price:
                    continue
                
                # Check if transaction involves same token pair
                # This is simplified - in production, decode tx.data to check tokens
                if self._involves_tokens(tx.data, [token_in, token_out]):
                    potential_frontrun.append(tx)
            
            # Look for backrun transactions (lower gas, same tokens, same sender as frontrun)
            for frontrun_tx in potential_frontrun:
                # Find matching backrun from same address
                backrun_txs = [
                    tx for tx in pending_txs
                    if tx.from_address == frontrun_tx.from_address
                    and tx.gas_price < our_gas_price
                    and tx.nonce > frontrun_tx.nonce
                    and self._involves_tokens(tx.data, [token_in, token_out])
                ]
                
                if backrun_txs:
                    # Sandwich detected!
                    estimated_impact = self._estimate_sandwich_impact(
                        amount_in,
                        frontrun_tx,
                        backrun_txs[0]
                    )
                    
                    severity = self._calculate_severity(estimated_impact)
                    
                    return MEVThreat(
                        threat_type='sandwich',
                        severity=severity,
                        description=f"Sandwich attack detected: {frontrun_tx.from_address} attempting to sandwich our {token_in}->{token_out} trade",
                        affected_tokens=[token_in, token_out],
                        estimated_impact=estimated_impact,
                        attacker_address=frontrun_tx.from_address,
                        attacker_tx_hashes=[frontrun_tx.hash, backrun_txs[0].hash],
                        timestamp=time.time()
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to detect sandwich attack: {e}")
            return None
    
    def detect_frontrunning(
        self,
        chain_id: int,
        our_tx: Dict,
        target_function: str
    ) -> Optional[MEVThreat]:
        """
        Detect frontrunning attempts
        
        Frontrunning: Someone sees our profitable transaction and submits
        the same transaction with higher gas to execute first
        
        Args:
            chain_id: Chain ID
            our_tx: Our transaction
            target_function: Function selector we're calling
            
        Returns:
            MEVThreat if detected, None otherwise
        """
        try:
            pending_txs = self.mempool_monitor.get(chain_id, [])
            
            if not pending_txs:
                return None
            
            our_gas_price = our_tx.get('gasPrice', 0)
            our_to = our_tx.get('to', '').lower()
            
            # Look for similar transactions with higher gas
            frontrun_candidates = []
            for tx in pending_txs:
                # Check if targeting same contract
                if tx.to_address.lower() != our_to:
                    continue
                
                # Check if gas price is significantly higher
                if tx.gas_price <= our_gas_price * 1.1:  # At least 10% higher
                    continue
                
                # Check if calling same function
                if tx.data[:10] == target_function[:10]:  # Function selector match
                    frontrun_candidates.append(tx)
            
            if frontrun_candidates:
                # Check if from known MEV bot
                known_bots = self.known_mev_bots.get(chain_id, [])
                
                for candidate in frontrun_candidates:
                    if candidate.from_address in known_bots:
                        return MEVThreat(
                            threat_type='frontrun',
                            severity='high',
                            description=f"Known MEV bot {candidate.from_address} attempting to frontrun our transaction",
                            affected_tokens=[],
                            estimated_impact=Decimal('0'),  # Hard to estimate
                            attacker_address=candidate.from_address,
                            attacker_tx_hashes=[candidate.hash],
                            timestamp=time.time()
                        )
                
                # Generic frontrun detection
                if len(frontrun_candidates) > 0:
                    return MEVThreat(
                        threat_type='frontrun',
                        severity='medium',
                        description=f"{len(frontrun_candidates)} transaction(s) with higher gas targeting same function",
                        affected_tokens=[],
                        estimated_impact=Decimal('0'),
                        attacker_address=frontrun_candidates[0].from_address,
                        attacker_tx_hashes=[tx.hash for tx in frontrun_candidates],
                        timestamp=time.time()
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to detect frontrunning: {e}")
            return None
    
    def analyze_transaction_safety(
        self,
        chain_id: int,
        our_tx: Dict,
        token_in: str,
        token_out: str,
        amount_in: Decimal
    ) -> Dict:
        """
        Comprehensive MEV safety analysis for a transaction
        
        Args:
            chain_id: Chain ID
            our_tx: Our transaction
            token_in: Input token
            token_out: Output token
            amount_in: Trade amount
            
        Returns:
            Safety analysis dictionary
        """
        threats = []
        
        # Check for sandwich attacks
        sandwich_threat = self.detect_sandwich_attack(
            chain_id, our_tx, token_in, token_out, amount_in
        )
        if sandwich_threat:
            threats.append(sandwich_threat)
        
        # Check for frontrunning
        frontrun_threat = self.detect_frontrunning(
            chain_id, our_tx, our_tx.get('data', '')[:10]
        )
        if frontrun_threat:
            threats.append(frontrun_threat)
        
        # Calculate overall safety score
        safety_score = self._calculate_safety_score(threats)
        
        return {
            'safe': len(threats) == 0,
            'safety_score': safety_score,  # 0-100, higher is safer
            'threats': [t.to_dict() for t in threats],
            'recommendation': self._get_recommendation(threats, safety_score),
            'timestamp': time.time()
        }
    
    def _involves_tokens(self, tx_data: str, tokens: List[str]) -> bool:
        """
        Check if transaction data involves specified tokens
        This is a simplified check - in production, decode calldata properly
        """
        try:
            if not tx_data or tx_data == '0x':
                return False
            
            # Simple check: see if token addresses appear in calldata
            for token in tokens:
                if token.lower()[2:] in tx_data.lower():
                    return True
            
            return False
        except:
            return False
    
    def _estimate_sandwich_impact(
        self,
        our_amount: Decimal,
        frontrun_tx: PendingTransaction,
        backrun_tx: PendingTransaction
    ) -> Decimal:
        """
        Estimate the impact of a sandwich attack on our trade
        This is simplified - real calculation needs pool state
        """
        # Simplified: assume 1-3% impact based on relative gas prices
        gas_ratio = Decimal(frontrun_tx.gas_price) / Decimal(backrun_tx.gas_price)
        
        # Higher gas ratio = more aggressive sandwich
        if gas_ratio > 2:
            impact_pct = Decimal('3')
        elif gas_ratio > 1.5:
            impact_pct = Decimal('2')
        else:
            impact_pct = Decimal('1')
        
        return our_amount * (impact_pct / Decimal('100'))
    
    def _calculate_severity(self, estimated_impact: Decimal) -> str:
        """Calculate threat severity based on estimated impact"""
        if estimated_impact > 100:
            return 'critical'
        elif estimated_impact > 50:
            return 'high'
        elif estimated_impact > 10:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_safety_score(self, threats: List[MEVThreat]) -> int:
        """
        Calculate overall safety score (0-100, higher is safer)
        """
        if not threats:
            return 100
        
        # Deduct points based on threat severity
        score = 100
        severity_weights = {
            'critical': 50,
            'high': 30,
            'medium': 15,
            'low': 5
        }
        
        for threat in threats:
            score -= severity_weights.get(threat.severity, 10)
        
        return max(0, score)
    
    def _get_recommendation(self, threats: List[MEVThreat], safety_score: int) -> str:
        """
        Get recommendation based on threats and safety score
        """
        if safety_score >= 90:
            return "SAFE - Proceed with transaction"
        elif safety_score >= 70:
            return "CAUTION - Consider using private relay"
        elif safety_score >= 50:
            return "WARNING - Use private relay or adjust gas/amount"
        else:
            return "DANGER - Do not submit, high MEV risk detected"
