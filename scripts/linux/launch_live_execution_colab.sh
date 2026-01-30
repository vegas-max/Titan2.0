#!/bin/bash

# TITAN 2.0 - Live Execution System Launcher for Google Colab
# This script opens the live execution notebook directly in Google Colab

echo "🚀 TITAN 2.0 - Live Execution System"
echo "===================================="
echo ""
echo "Opening Google Colab with Titan Live Execution Notebook..."
echo ""
echo "⚠️  WARNING: This notebook is for LIVE trading with REAL money!"
echo "   - Make sure you understand the risks"
echo "   - Use a dedicated wallet with minimal funds"
echo "   - Test in PAPER mode first"
echo ""

# GitHub repository details
GITHUB_REPO="vegas-max/Titan2.0"
NOTEBOOK_PATH="Titan_Live_Execution_Colab.ipynb"

# Construct Colab URL
COLAB_URL="https://colab.research.google.com/github/${GITHUB_REPO}/blob/main/${NOTEBOOK_PATH}"

echo "📱 Opening in your default browser..."
echo "   URL: $COLAB_URL"
echo ""

# Detect OS and open browser
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open "$COLAB_URL" 2>/dev/null || echo "❌ Could not open browser. Please navigate to: $COLAB_URL"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "$COLAB_URL" || echo "❌ Could not open browser. Please navigate to: $COLAB_URL"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    # Windows
    start "$COLAB_URL" || echo "❌ Could not open browser. Please navigate to: $COLAB_URL"
else
    echo "❌ Unsupported OS. Please navigate to: $COLAB_URL"
fi

echo ""
echo "✅ If browser didn't open, copy and paste this URL:"
echo "   $COLAB_URL"
echo ""
echo "📚 For more information, see:"
echo "   - README.md"
echo "   - GOOGLE_COLAB_STEP_BY_STEP.md"
echo "   - OPERATIONS_GUIDE.md"
echo ""
echo "Good luck and trade safely! 🚀"
