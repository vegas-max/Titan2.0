"""
Test Suite for Li.Fi Integration - Intent-Based Bridging

Tests the Python wrapper for Li.Fi SDK and bridge oracle functionality.
"""

import unittest
from decimal import Decimal
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routing.lifi_wrapper import LiFiWrapper
from ml.bridge_oracle import BridgeOracle


class TestLiFiWrapper(unittest.TestCase):
    """Test Li.Fi Python wrapper functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.wrapper = LiFiWrapper()
    
    def test_estimate_bridge_time_intent_based(self):
        """Test timing estimates for intent-based bridges"""
        # Across should be fastest (30 seconds)
        self.assertEqual(self.wrapper.estimate_bridge_time('across'), 30)
        
        # Stargate should be 60 seconds
        self.assertEqual(self.wrapper.estimate_bridge_time('stargate'), 60)
        
        # Hop should be 120 seconds
        self.assertEqual(self.wrapper.estimate_bridge_time('hop'), 120)
    
    def test_is_intent_based_bridge(self):
        """Test intent-based bridge detection"""
        # Intent-based bridges should return True
        self.assertTrue(self.wrapper.is_intent_based_bridge('across'))
        self.assertTrue(self.wrapper.is_intent_based_bridge('stargate'))
        self.assertFalse(self.wrapper.is_intent_based_bridge('synapse'))


class TestBridgeOracle(unittest.TestCase):
    """Test Bridge Oracle with Li.Fi integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.oracle = BridgeOracle(min_profit_threshold_usd=5.0)
    
    def test_estimate_bridge_time_uses_lifi(self):
        """Test that bridge oracle uses Li.Fi wrapper for timing"""
        time_across = self.oracle._estimate_bridge_time('across')
        self.assertEqual(time_across, 30)


if __name__ == '__main__':
    unittest.main(verbosity=2)
