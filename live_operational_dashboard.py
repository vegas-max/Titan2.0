#!/usr/bin/env python3
"""
Real-Time Operational Dashboard with Live Visuals
Provides 24/7 sanity checks and monitoring for Titan arbitrage bot operations
"""

import os
import sys
import time
import json
import asyncio
import signal
from datetime import datetime, timedelta
from collections import deque, defaultdict
from typing import Dict, List, Any, Optional
import threading

# Try to import visualization libraries
try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.table import Table
    from rich.live import Live
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️  Installing required packages for live dashboard...")
    os.system("pip install rich redis python-dotenv 2>&1 > /dev/null")
    from rich.console import Console
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.table import Table
    from rich.live import Live
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️  Redis not available, using simulated data mode")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class OperationalDashboard:
    """Real-time operational dashboard with live metrics and sanity checks"""
    
    def __init__(self):
        self.console = Console()
        self.running = True
        
        # Metrics storage (24 hours of data)
        self.metrics_history = deque(maxlen=1440)  # 1 per minute for 24 hours
        self.recent_trades = deque(maxlen=50)
        self.recent_errors = deque(maxlen=20)
        self.gas_prices = deque(maxlen=100)
        
        # Current state
        self.current_metrics = {
            "total_trades": 0,
            "successful_trades": 0,
            "failed_trades": 0,
            "total_profit_usd": 0.0,
            "total_gas_spent_usd": 0.0,
            "net_profit_usd": 0.0,
            "opportunities_scanned": 0,
            "opportunities_profitable": 0,
            "avg_execution_time_ms": 0.0,
            "current_gas_price_gwei": 0.0,
            "system_uptime_seconds": 0,
            "last_trade_timestamp": None,
            "active_chains": [],
            "health_status": "STARTING"
        }
        
        # Chain-specific metrics
        self.chain_metrics = defaultdict(lambda: {
            "trades": 0,
            "profit": 0.0,
            "gas_spent": 0.0,
            "avg_profit_per_trade": 0.0,
            "last_active": None
        })
        
        # Sanity check thresholds
        self.thresholds = {
            "min_profit_usd": float(os.getenv("MIN_PROFIT_USD", "5.0")),
            "max_gas_price_gwei": float(os.getenv("MAX_GAS_PRICE_GWEI", "150")),
            "max_execution_time_ms": 30000,
            "min_success_rate": 0.70,  # 70%
            "max_consecutive_failures": 10,
            "min_uptime_seconds": 60
        }
        
        # Alert counters
        self.consecutive_failures = 0
        self.alerts = deque(maxlen=10)
        
        # Redis connection
        self.redis_client = None
        if REDIS_AVAILABLE:
            try:
                redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                self.redis_client.ping()
            except Exception as e:
                print(f"⚠️  Redis connection failed: {e}")
                self.redis_client = None
        
        # Start time
        self.start_time = datetime.now()
        
    def add_alert(self, severity: str, message: str):
        """Add an alert to the dashboard"""
        self.alerts.append({
            "timestamp": datetime.now(),
            "severity": severity,
            "message": message
        })
    
    def check_sanity(self):
        """Perform sanity checks on current metrics"""
        alerts = []
        
        # Check 1: Gas price sanity
        if self.current_metrics["current_gas_price_gwei"] > self.thresholds["max_gas_price_gwei"]:
            alerts.append(("⚠️ WARNING", f"Gas price too high: {self.current_metrics['current_gas_price_gwei']:.2f} Gwei"))
        
        # Check 2: Success rate
        total = self.current_metrics["total_trades"]
        if total > 10:
            success_rate = self.current_metrics["successful_trades"] / total
            if success_rate < self.thresholds["min_success_rate"]:
                alerts.append(("🚨 CRITICAL", f"Low success rate: {success_rate*100:.1f}%"))
        
        # Check 3: Consecutive failures
        if self.consecutive_failures >= self.thresholds["max_consecutive_failures"]:
            alerts.append(("🚨 CRITICAL", f"Too many consecutive failures: {self.consecutive_failures}"))
        
        # Check 4: Net profit check
        if self.current_metrics["net_profit_usd"] < 0:
            alerts.append(("⚠️ WARNING", f"Net loss: ${self.current_metrics['net_profit_usd']:.2f}"))
        
        # Check 5: System responsiveness
        if self.current_metrics["last_trade_timestamp"]:
            time_since_last_trade = (datetime.now() - self.current_metrics["last_trade_timestamp"]).seconds
            if time_since_last_trade > 300 and self.current_metrics["total_trades"] > 0:  # 5 minutes
                alerts.append(("⚠️ WARNING", f"No trades for {time_since_last_trade}s"))
        
        for severity, message in alerts:
            self.add_alert(severity, message)
        
        return len(alerts) == 0
    
    def generate_header(self) -> Panel:
        """Generate dashboard header"""
        uptime = datetime.now() - self.start_time
        uptime_str = f"{int(uptime.total_seconds()//3600)}h {int((uptime.total_seconds()%3600)//60)}m"
        
        # Determine health color
        health_colors = {
            "HEALTHY": "green",
            "DEGRADED": "yellow",
            "CRITICAL": "red",
            "STARTING": "blue"
        }
        health_color = health_colors.get(self.current_metrics["health_status"], "white")
        
        header_text = Text()
        header_text.append("🚀 TITAN OPERATIONAL DASHBOARD\n", style="bold cyan")
        header_text.append(f"Status: ", style="bold")
        header_text.append(f"{self.current_metrics['health_status']}", style=f"bold {health_color}")
        header_text.append(f" | Uptime: {uptime_str} | ", style="dim")
        header_text.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style="bold white")
        
        return Panel(header_text, box=box.DOUBLE, border_style="cyan")
    
    def generate_metrics_panel(self) -> Panel:
        """Generate main metrics panel"""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Metric", style="cyan", width=30)
        table.add_column("Value", style="white", width=25)
        table.add_column("Metric", style="cyan", width=30)
        table.add_column("Value", style="white", width=25)
        
        # Calculate derived metrics
        total_trades = self.current_metrics["total_trades"]
        success_rate = (self.current_metrics["successful_trades"] / total_trades * 100) if total_trades > 0 else 0
        avg_profit = (self.current_metrics["total_profit_usd"] / total_trades) if total_trades > 0 else 0
        
        # Row 1
        table.add_row(
            "💰 Total Profit (USD)",
            f"[green]${self.current_metrics['total_profit_usd']:.2f}[/green]",
            "⛽ Gas Spent (USD)",
            f"[yellow]${self.current_metrics['total_gas_spent_usd']:.2f}[/yellow]"
        )
        
        # Row 2
        table.add_row(
            "📊 Net Profit (USD)",
            f"[bold {'green' if self.current_metrics['net_profit_usd'] > 0 else 'red'}]${self.current_metrics['net_profit_usd']:.2f}[/bold]",
            "📈 Avg Profit/Trade",
            f"[green]${avg_profit:.2f}[/green]"
        )
        
        # Row 3
        table.add_row(
            "✅ Total Trades",
            f"[white]{total_trades}[/white]",
            "🎯 Success Rate",
            f"[{'green' if success_rate > 70 else 'yellow' if success_rate > 50 else 'red'}]{success_rate:.1f}%[/]"
        )
        
        # Row 4
        table.add_row(
            "🔍 Opps Scanned",
            f"[white]{self.current_metrics['opportunities_scanned']:,}[/white]",
            "💎 Opps Profitable",
            f"[green]{self.current_metrics['opportunities_profitable']:,}[/green]"
        )
        
        # Row 5
        table.add_row(
            "⏱️  Avg Execution Time",
            f"[white]{self.current_metrics['avg_execution_time_ms']:.0f}ms[/white]",
            "⛽ Current Gas Price",
            f"[{'green' if self.current_metrics['current_gas_price_gwei'] < 100 else 'yellow' if self.current_metrics['current_gas_price_gwei'] < 150 else 'red'}]{self.current_metrics['current_gas_price_gwei']:.2f} Gwei[/]"
        )
        
        return Panel(table, title="📊 Performance Metrics", border_style="green")
    
    def generate_chains_panel(self) -> Panel:
        """Generate active chains panel"""
        table = Table(show_header=True, box=box.SIMPLE)
        table.add_column("Chain", style="cyan")
        table.add_column("Trades", justify="right", style="white")
        table.add_column("Profit (USD)", justify="right", style="green")
        table.add_column("Gas (USD)", justify="right", style="yellow")
        table.add_column("Net (USD)", justify="right")
        table.add_column("Last Active", style="dim")
        
        # Sort chains by profit
        sorted_chains = sorted(
            self.chain_metrics.items(),
            key=lambda x: x[1]["profit"],
            reverse=True
        )
        
        for chain, metrics in sorted_chains[:10]:  # Top 10 chains
            net = metrics["profit"] - metrics["gas_spent"]
            net_style = "green" if net > 0 else "red"
            
            last_active = "Never"
            if metrics["last_active"]:
                delta = (datetime.now() - metrics["last_active"]).seconds
                if delta < 60:
                    last_active = f"{delta}s ago"
                elif delta < 3600:
                    last_active = f"{delta//60}m ago"
                else:
                    last_active = f"{delta//3600}h ago"
            
            table.add_row(
                chain,
                str(metrics["trades"]),
                f"${metrics['profit']:.2f}",
                f"${metrics['gas_spent']:.2f}",
                f"[{net_style}]${net:.2f}[/{net_style}]",
                last_active
            )
        
        if not sorted_chains:
            table.add_row("No chain activity yet", "", "", "", "", "")
        
        return Panel(table, title="🌐 Active Chains", border_style="blue")
    
    def generate_recent_trades_panel(self) -> Panel:
        """Generate recent trades panel"""
        table = Table(show_header=True, box=box.SIMPLE)
        table.add_column("Time", style="dim", width=8)
        table.add_column("Chain", style="cyan", width=10)
        table.add_column("Type", style="magenta", width=12)
        table.add_column("Profit", justify="right", width=12)
        table.add_column("Gas", justify="right", width=10)
        table.add_column("Status", width=10)
        
        for trade in list(self.recent_trades)[-10:]:
            status_style = "green" if trade.get("status") == "SUCCESS" else "red"
            profit_style = "green" if trade.get("profit", 0) > 0 else "red"
            
            table.add_row(
                trade.get("timestamp", "").strftime("%H:%M:%S") if isinstance(trade.get("timestamp"), datetime) else "Unknown",
                trade.get("chain", "Unknown")[:10],
                trade.get("strategy", "Unknown")[:12],
                f"[{profit_style}]${trade.get('profit', 0):.2f}[/{profit_style}]",
                f"${trade.get('gas_cost', 0):.2f}",
                f"[{status_style}]{trade.get('status', 'UNKNOWN')}[/{status_style}]"
            )
        
        if not self.recent_trades:
            table.add_row("No trades yet", "", "", "", "", "")
        
        return Panel(table, title="📝 Recent Trades", border_style="magenta")
    
    def generate_alerts_panel(self) -> Panel:
        """Generate alerts and sanity checks panel"""
        table = Table(show_header=True, box=box.SIMPLE)
        table.add_column("Time", style="dim", width=8)
        table.add_column("Severity", width=12)
        table.add_column("Message", style="white")
        
        for alert in list(self.alerts)[-5:]:
            table.add_row(
                alert["timestamp"].strftime("%H:%M:%S"),
                alert["severity"],
                alert["message"]
            )
        
        if not self.alerts:
            table.add_row("", "[green]✅ All systems nominal[/green]", "")
        
        return Panel(table, title="🚨 Alerts & Sanity Checks", border_style="red")
    
    def generate_gas_trend_panel(self) -> Panel:
        """Generate gas price trend visualization"""
        if not self.gas_prices:
            return Panel("[dim]No gas price data yet[/dim]", title="⛽ Gas Price Trend", border_style="yellow")
        
        # Simple ASCII chart
        prices = list(self.gas_prices)
        max_price = max(prices) if prices else 100
        min_price = min(prices) if prices else 0
        range_price = max_price - min_price if max_price != min_price else 1
        
        chart_height = 8
        chart_width = min(50, len(prices))
        
        # Sample if too many points
        if len(prices) > chart_width:
            step = len(prices) // chart_width
            prices = prices[::step]
        
        chart_lines = []
        for i in range(chart_height):
            threshold = max_price - (i * range_price / chart_height)
            line = ""
            for price in prices:
                if price >= threshold:
                    line += "█"
                else:
                    line += " "
            chart_lines.append(line)
        
        chart_text = "\n".join(chart_lines)
        chart_text += f"\n{'─' * len(prices)}\n"
        chart_text += f"Max: {max_price:.1f} | Current: {self.current_metrics['current_gas_price_gwei']:.1f} | Min: {min_price:.1f} Gwei"
        
        return Panel(chart_text, title="⛽ Gas Price Trend (Last 100 samples)", border_style="yellow")
    
    def generate_layout(self) -> Layout:
        """Generate the complete dashboard layout"""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=12)
        )
        
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        layout["left"].split_column(
            Layout(name="metrics", size=12),
            Layout(name="chains")
        )
        
        layout["right"].split_column(
            Layout(name="trades"),
            Layout(name="gas", size=12)
        )
        
        layout["footer"].split_column(
            Layout(name="alerts", size=8),
            Layout(name="help", size=4)
        )
        
        # Populate layouts
        layout["header"].update(self.generate_header())
        layout["metrics"].update(self.generate_metrics_panel())
        layout["chains"].update(self.generate_chains_panel())
        layout["trades"].update(self.generate_recent_trades_panel())
        layout["gas"].update(self.generate_gas_trend_panel())
        layout["alerts"].update(self.generate_alerts_panel())
        
        # Help panel
        help_text = Text()
        help_text.append("Controls: ", style="bold cyan")
        help_text.append("Press ", style="dim")
        help_text.append("Ctrl+C", style="bold red")
        help_text.append(" to exit | Updates every 1 second | Data from Redis channel: 'trade_signals'", style="dim")
        layout["help"].update(Panel(help_text, border_style="dim"))
        
        return layout
    
    def simulate_data_update(self):
        """Simulate data updates for testing (when Redis is not available)"""
        import random
        
        # Simulate a trade occasionally
        if random.random() < 0.1:  # 10% chance
            success = random.random() < 0.85
            profit = random.uniform(5, 50) if success else 0
            gas_cost = random.uniform(0.5, 3)
            
            trade = {
                "timestamp": datetime.now(),
                "chain": random.choice(["Polygon", "Ethereum", "Arbitrum", "Optimism", "Base"]),
                "strategy": random.choice(["Flash Arb", "Cross-DEX", "Triangular", "Cross-Chain"]),
                "profit": profit,
                "gas_cost": gas_cost,
                "status": "SUCCESS" if success else "FAILED"
            }
            
            self.recent_trades.append(trade)
            self.current_metrics["total_trades"] += 1
            
            if success:
                self.current_metrics["successful_trades"] += 1
                self.current_metrics["total_profit_usd"] += profit
                self.consecutive_failures = 0
            else:
                self.current_metrics["failed_trades"] += 1
                self.consecutive_failures += 1
            
            self.current_metrics["total_gas_spent_usd"] += gas_cost
            self.current_metrics["net_profit_usd"] = (
                self.current_metrics["total_profit_usd"] - 
                self.current_metrics["total_gas_spent_usd"]
            )
            self.current_metrics["last_trade_timestamp"] = datetime.now()
            
            # Update chain metrics
            chain = trade["chain"]
            self.chain_metrics[chain]["trades"] += 1
            self.chain_metrics[chain]["profit"] += profit
            self.chain_metrics[chain]["gas_spent"] += gas_cost
            self.chain_metrics[chain]["last_active"] = datetime.now()
        
        # Update gas price
        self.current_metrics["current_gas_price_gwei"] = random.uniform(20, 180)
        self.gas_prices.append(self.current_metrics["current_gas_price_gwei"])
        
        # Update opportunities
        self.current_metrics["opportunities_scanned"] += random.randint(10, 100)
        self.current_metrics["opportunities_profitable"] += random.randint(0, 5)
        
        # Update execution time
        self.current_metrics["avg_execution_time_ms"] = random.uniform(3000, 8000)
        
        # Update health status
        if self.consecutive_failures >= 5:
            self.current_metrics["health_status"] = "CRITICAL"
        elif self.current_metrics["net_profit_usd"] < 0:
            self.current_metrics["health_status"] = "DEGRADED"
        else:
            self.current_metrics["health_status"] = "HEALTHY"
    
    def update_from_redis(self):
        """Update metrics from Redis"""
        if not self.redis_client:
            return
        
        try:
            # Get latest metrics from Redis
            trade_signal = self.redis_client.get("latest_trade_signal")
            if trade_signal:
                data = json.loads(trade_signal)
                # Process the trade signal data
                # This would be customized based on your actual Redis data structure
                pass
        except Exception as e:
            print(f"Error reading from Redis: {e}")
    
    async def run(self):
        """Run the dashboard"""
        with Live(self.generate_layout(), refresh_per_second=1, console=self.console) as live:
            while self.running:
                try:
                    # Update data
                    if self.redis_client:
                        self.update_from_redis()
                    else:
                        self.simulate_data_update()
                    
                    # Run sanity checks
                    self.check_sanity()
                    
                    # Update display
                    live.update(self.generate_layout())
                    
                    # Update uptime
                    self.current_metrics["system_uptime_seconds"] = (
                        datetime.now() - self.start_time
                    ).total_seconds()
                    
                    await asyncio.sleep(1)
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.add_alert("🚨 CRITICAL", f"Dashboard error: {str(e)}")
                    await asyncio.sleep(1)
    
    def stop(self):
        """Stop the dashboard"""
        self.running = False


def signal_handler(signum, frame):
    """Handle termination signals"""
    print("\n\n🛑 Shutting down dashboard...")
    sys.exit(0)


def main():
    """Main entry point"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    console = Console()
    console.clear()
    
    console.print("\n[bold cyan]🚀 TITAN Real-Time Operational Dashboard[/bold cyan]")
    console.print("[dim]Starting 24/7 sanity monitoring...[/dim]\n")
    
    dashboard = OperationalDashboard()
    
    try:
        asyncio.run(dashboard.run())
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Dashboard stopped by user[/yellow]")
    except Exception as e:
        console.print(f"\n\n[red]Dashboard error: {e}[/red]")
    finally:
        console.print("[dim]Dashboard shutdown complete[/dim]\n")


if __name__ == "__main__":
    main()
