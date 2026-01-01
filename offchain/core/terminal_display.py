#!/usr/bin/env python3
"""
Unified Terminal Display for Titan System
Provides real-time, informative terminal output for opportunities, decisions, and executions
"""

import sys
import time
from datetime import datetime
from collections import deque
from typing import Dict, Any, Optional
import threading
import os

# Color codes for terminal output
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    
    @staticmethod
    def disable():
        """Disable colors (for environments that don't support ANSI)"""
        Colors.BLUE = ''
        Colors.GREEN = ''
        Colors.YELLOW = ''
        Colors.RED = ''
        Colors.CYAN = ''
        Colors.MAGENTA = ''
        Colors.WHITE = ''
        Colors.BOLD = ''
        Colors.UNDERLINE = ''
        Colors.END = ''


class TerminalDisplay:
    """
    Unified terminal display for all Titan components.
    Shows opportunities, system logic/decisions, and executions in real-time.
    """
    
    def __init__(self):
        self.start_time = datetime.now()
        self.stats = {
            'opportunities_scanned': 0,
            'opportunities_profitable': 0,
            'opportunities_signaled': 0,
            'total_profit_usd': 0.0,
            'executions_attempted': 0,
            'executions_successful': 0,
            'executions_failed': 0,
            'paper_trades': 0
        }
        self.recent_opportunities = deque(maxlen=5)
        self.recent_decisions = deque(maxlen=5)
        self.recent_executions = deque(maxlen=5)
        self.lock = threading.Lock()
        
        # Disable colors if not in a terminal
        if not sys.stdout.isatty():
            Colors.disable()
    
    def print_header(self, mode: str = "PAPER"):
        """Print the system header"""
        print("\n" + "=" * 80)
        print(f"{Colors.BOLD}{Colors.CYAN}🚀 APEX-OMEGA TITAN - Multi-Chain Arbitrage System{Colors.END}")
        print("=" * 80)
        print(f"{Colors.BOLD}Execution Mode:{Colors.END} {Colors.GREEN if mode == 'PAPER' else Colors.RED}{mode}{Colors.END}")
        print(f"{Colors.BOLD}Started:{Colors.END} {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80 + "\n")
    
    def print_stats_bar(self):
        """Print a compact stats bar"""
        runtime = datetime.now() - self.start_time
        runtime_str = f"{int(runtime.total_seconds() // 3600)}h {int((runtime.total_seconds() % 3600) // 60)}m"
        
        with self.lock:
            success_rate = 0
            if self.stats['executions_attempted'] > 0:
                success_rate = (self.stats['executions_successful'] / self.stats['executions_attempted']) * 100
            
            profit_rate = 0
            if self.stats['opportunities_scanned'] > 0:
                profit_rate = (self.stats['opportunities_profitable'] / self.stats['opportunities_scanned']) * 100
            
            print(f"{Colors.CYAN}┌─ STATS {Colors.END}" + "─" * 69)
            print(f"{Colors.CYAN}│{Colors.END} Runtime: {runtime_str} | "
                  f"Scanned: {self.stats['opportunities_scanned']} | "
                  f"Profitable: {self.stats['opportunities_profitable']} ({profit_rate:.1f}%) | "
                  f"Signaled: {self.stats['opportunities_signaled']}")
            print(f"{Colors.CYAN}│{Colors.END} Executions: {self.stats['executions_attempted']} "
                  f"(✓{self.stats['executions_successful']} / ✗{self.stats['executions_failed']}, "
                  f"{success_rate:.0f}% success) | "
                  f"Paper: {self.stats['paper_trades']} | "
                  f"Profit: ${self.stats['total_profit_usd']:.2f}")
            print(f"{Colors.CYAN}└{'─' * 78}{Colors.END}\n")
    
    def log_opportunity_scan(self, token: str, chain_id: int, dex1: str, dex2: str, 
                            amount_usd: float, profitable: bool = False, profit_usd: float = 0.0,
                            gas_gwei: float = 0.0, details: str = ""):
        """Log an opportunity scan"""
        with self.lock:
            self.stats['opportunities_scanned'] += 1
            if profitable:
                self.stats['opportunities_profitable'] += 1
        
        chain_name = self._get_chain_name(chain_id)
        status_icon = "💰" if profitable else "🔍"
        color = Colors.GREEN if profitable else Colors.WHITE
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        msg = (f"{color}{status_icon} [{timestamp}] SCAN: {token} on {chain_name} "
               f"({dex1}↔{dex2}) | ${amount_usd:.0f}")
        
        if profitable:
            msg += f" | {Colors.BOLD}PROFIT: ${profit_usd:.2f}{Colors.END}"
        
        if gas_gwei > 0:
            msg += f" | Gas: {gas_gwei:.1f}gwei"
        
        if details:
            msg += f" | {details}"
        
        msg += Colors.END
        
        print(msg)
        
        with self.lock:
            self.recent_opportunities.append({
                'time': timestamp,
                'token': token,
                'chain': chain_name,
                'profitable': profitable,
                'profit': profit_usd
            })
    
    def log_decision(self, decision_type: str, token: str, chain_id: int, 
                    reason: str, details: Dict[str, Any] = None):
        """Log a system decision (approve, reject, optimize, etc.)"""
        chain_name = self._get_chain_name(chain_id)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        icon_map = {
            'APPROVE': ('✅', Colors.GREEN),
            'REJECT': ('❌', Colors.RED),
            'SIGNAL': ('📡', Colors.CYAN),
            'OPTIMIZE': ('⚙️', Colors.YELLOW),
            'GAS_CHECK': ('⛽', Colors.YELLOW),
            'SLIPPAGE': ('📊', Colors.MAGENTA),
            'AI_TUNE': ('🧠', Colors.BLUE)
        }
        
        icon, color = icon_map.get(decision_type, ('ℹ️', Colors.WHITE))
        
        msg = f"{color}{icon} [{timestamp}] {decision_type}: {token} on {chain_name} | {reason}"
        
        if details:
            detail_parts = []
            for k, v in details.items():
                if isinstance(v, float):
                    detail_parts.append(f"{k}={v:.2f}")
                else:
                    detail_parts.append(f"{k}={v}")
            if detail_parts:
                msg += f" | {', '.join(detail_parts)}"
        
        msg += Colors.END
        
        print(msg)
        
        with self.lock:
            self.recent_decisions.append({
                'time': timestamp,
                'type': decision_type,
                'token': token,
                'reason': reason
            })
    
    def log_signal_generated(self, token: str, chain_id: int, profit_usd: float, 
                            route: list, gas_gwei: float, execution_params: Dict[str, Any] = None):
        """Log when a signal is generated for execution"""
        with self.lock:
            self.stats['opportunities_signaled'] += 1
            self.stats['total_profit_usd'] += profit_usd
        
        chain_name = self._get_chain_name(chain_id)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        route_str = " → ".join(route) if route else "N/A"
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}{'=' * 80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}⚡ SIGNAL GENERATED{Colors.END} [{timestamp}]")
        print(f"{Colors.CYAN}Token:{Colors.END} {token} on {chain_name}")
        print(f"{Colors.CYAN}Expected Profit:{Colors.END} ${profit_usd:.2f}")
        print(f"{Colors.CYAN}Route:{Colors.END} {route_str}")
        print(f"{Colors.CYAN}Gas Price:{Colors.END} {gas_gwei:.1f} gwei")
        
        if execution_params:
            print(f"{Colors.CYAN}Execution Params:{Colors.END}")
            for key, value in execution_params.items():
                if isinstance(value, float):
                    print(f"  • {key}: {value:.4f}")
                else:
                    print(f"  • {key}: {value}")
        
        print(f"{Colors.BOLD}{Colors.GREEN}{'=' * 80}{Colors.END}\n")
    
    def log_execution_start(self, trade_id: str, token: str, chain_id: int, 
                           amount: str, mode: str = "PAPER"):
        """Log execution start"""
        with self.lock:
            self.stats['executions_attempted'] += 1
            if mode == "PAPER":
                self.stats['paper_trades'] += 1
        
        chain_name = self._get_chain_name(chain_id)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        icon = "📝" if mode == "PAPER" else "🔴"
        color = Colors.YELLOW if mode == "PAPER" else Colors.RED
        
        print(f"\n{color}{Colors.BOLD}{'─' * 80}{Colors.END}")
        print(f"{color}{icon} EXECUTION START{Colors.END} [{timestamp}] | ID: {trade_id}")
        print(f"  Token: {token} | Chain: {chain_name} | Amount: {amount} | Mode: {mode}")
        print(f"{color}{'─' * 80}{Colors.END}")
    
    def log_execution_complete(self, trade_id: str, status: str, duration_ms: int,
                              profit_usd: float = None, tx_hash: str = None, 
                              error: str = None):
        """Log execution completion"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if status == "SUCCESS":
            with self.lock:
                self.stats['executions_successful'] += 1
            color = Colors.GREEN
            icon = "✅"
        elif status == "SIMULATED":
            with self.lock:
                self.stats['executions_successful'] += 1
            color = Colors.GREEN
            icon = "✅"
        else:
            with self.lock:
                self.stats['executions_failed'] += 1
            color = Colors.RED
            icon = "❌"
        
        print(f"{color}{icon} EXECUTION COMPLETE{Colors.END} [{timestamp}] | ID: {trade_id}")
        print(f"  Status: {status} | Duration: {duration_ms}ms")
        
        if profit_usd is not None:
            print(f"  Profit: ${profit_usd:.2f}")
        
        if tx_hash:
            print(f"  TX: {tx_hash}")
        
        if error:
            print(f"  Error: {error}")
        
        print(f"{color}{'─' * 80}{Colors.END}\n")
        
        with self.lock:
            self.recent_executions.append({
                'time': timestamp,
                'id': trade_id,
                'status': status,
                'duration': duration_ms
            })
    
    def log_gas_update(self, chain_id: int, gas_gwei: float, threshold: float):
        """Log gas price updates"""
        chain_name = self._get_chain_name(chain_id)
        
        if gas_gwei > threshold:
            color = Colors.RED
            icon = "⚠️"
        elif gas_gwei > threshold * 0.8:
            color = Colors.YELLOW
            icon = "⚡"
        else:
            color = Colors.GREEN
            icon = "⛽"
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{color}{icon} [{timestamp}] GAS UPDATE: {chain_name} = {gas_gwei:.1f} gwei "
              f"(threshold: {threshold:.1f}){Colors.END}")
    
    def log_error(self, component: str, error: str, details: str = ""):
        """Log an error"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Colors.RED}❌ [{timestamp}] ERROR in {component}: {error}{Colors.END}")
        if details:
            print(f"{Colors.RED}   Details: {details}{Colors.END}")
    
    def log_warning(self, component: str, warning: str):
        """Log a warning"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Colors.YELLOW}⚠️ [{timestamp}] WARNING in {component}: {warning}{Colors.END}")
    
    def log_info(self, message: str):
        """Log general information"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Colors.BLUE}ℹ️ [{timestamp}] {message}{Colors.END}")
    
    def print_summary(self):
        """Print a summary of recent activity"""
        print(f"\n{Colors.CYAN}{'=' * 80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}📊 RECENT ACTIVITY SUMMARY{Colors.END}")
        print(f"{Colors.CYAN}{'=' * 80}{Colors.END}")
        
        with self.lock:
            if self.recent_opportunities:
                print(f"\n{Colors.BOLD}Recent Opportunities:{Colors.END}")
                for opp in list(self.recent_opportunities)[-5:]:
                    status = f"{Colors.GREEN}PROFITABLE: ${opp['profit']:.2f}{Colors.END}" if opp['profitable'] else "scanned"
                    print(f"  [{opp['time']}] {opp['token']} on {opp['chain']} - {status}")
            
            if self.recent_decisions:
                print(f"\n{Colors.BOLD}Recent Decisions:{Colors.END}")
                for dec in list(self.recent_decisions)[-5:]:
                    print(f"  [{dec['time']}] {dec['type']}: {dec['token']} - {dec['reason']}")
            
            if self.recent_executions:
                print(f"\n{Colors.BOLD}Recent Executions:{Colors.END}")
                for exe in list(self.recent_executions)[-5:]:
                    print(f"  [{exe['time']}] {exe['id']} - {exe['status']} ({exe['duration']}ms)")
        
        print(f"\n{Colors.CYAN}{'=' * 80}{Colors.END}\n")
    
    def _get_chain_name(self, chain_id: int) -> str:
        """Get human-readable chain name"""
        chain_names = {
            1: "Ethereum",
            137: "Polygon",
            42161: "Arbitrum",
            10: "Optimism",
            8453: "Base",
            56: "BSC",
            43114: "Avalanche",
            250: "Fantom",
            59144: "Linea",
            534352: "Scroll",
            5000: "Mantle",
            324: "zkSync",
            81457: "Blast",
            42220: "Celo",
            204: "opBNB"
        }
        return chain_names.get(chain_id, f"Chain-{chain_id}")


# Global singleton instance
_terminal_display = None

def get_terminal_display() -> TerminalDisplay:
    """Get or create the global terminal display instance"""
    global _terminal_display
    if _terminal_display is None:
        _terminal_display = TerminalDisplay()
    return _terminal_display
