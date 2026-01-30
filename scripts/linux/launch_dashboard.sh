#!/bin/bash
# Launch Operational Dashboards for 24/7 Monitoring

echo "🚀 TITAN Operational Dashboard Launcher"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Install required Python packages
echo "📦 Installing required packages..."
pip install rich redis python-dotenv 2>&1 > /dev/null || {
    echo "⚠️  Some packages failed to install, continuing anyway..."
}

# Check if web server is available
WEB_PORT=3001
if command -v python3 &> /dev/null; then
    echo "✅ Python available for web server"
fi

echo ""
echo "Select dashboard mode:"
echo "1) Terminal Dashboard (CLI - recommended for SSH/remote)"
echo "2) Web Dashboard (Browser - requires port $WEB_PORT)"
echo "3) Both (Terminal + Web)"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo ""
        echo "🖥️  Launching Terminal Dashboard..."
        echo "Press Ctrl+C to exit"
        echo ""
        python3 live_operational_dashboard.py
        ;;
    2)
        echo ""
        echo "🌐 Launching Web Dashboard..."
        echo "Dashboard will be available at: http://localhost:$WEB_PORT"
        echo "Press Ctrl+C to stop"
        echo ""
        python3 -m http.server $WEB_PORT --bind 127.0.0.1 &
        WEB_PID=$!
        sleep 2
        if command -v xdg-open &> /dev/null; then
            xdg-open "http://localhost:$WEB_PORT/operational_dashboard.html" 2>/dev/null &
        elif command -v open &> /dev/null; then
            open "http://localhost:$WEB_PORT/operational_dashboard.html" 2>/dev/null &
        fi
        echo "✅ Web server started (PID: $WEB_PID)"
        echo "🌐 Open http://localhost:$WEB_PORT/operational_dashboard.html in your browser"
        wait $WEB_PID
        ;;
    3)
        echo ""
        echo "🚀 Launching Both Dashboards..."
        echo ""
        # Start web server in background
        python3 -m http.server $WEB_PORT --bind 127.0.0.1 > /dev/null 2>&1 &
        WEB_PID=$!
        echo "✅ Web Dashboard: http://localhost:$WEB_PORT/operational_dashboard.html (PID: $WEB_PID)"
        
        sleep 2
        
        # Open browser if available
        if command -v xdg-open &> /dev/null; then
            xdg-open "http://localhost:$WEB_PORT/operational_dashboard.html" 2>/dev/null &
        elif command -v open &> /dev/null; then
            open "http://localhost:$WEB_PORT/operational_dashboard.html" 2>/dev/null &
        fi
        
        echo ""
        echo "🖥️  Starting Terminal Dashboard..."
        echo "Press Ctrl+C to exit both dashboards"
        echo ""
        
        # Cleanup function
        cleanup() {
            echo ""
            echo "🛑 Shutting down dashboards..."
            kill $WEB_PID 2>/dev/null
            echo "✅ Cleanup complete"
            exit 0
        }
        
        trap cleanup INT TERM
        
        # Start terminal dashboard in foreground
        python3 live_operational_dashboard.py
        
        # Cleanup on exit
        cleanup
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
