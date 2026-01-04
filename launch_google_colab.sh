#!/bin/bash
# ==============================================================================
# TITAN 2.0 - Google Colab Launcher (Linux/Mac)
# ==============================================================================
# Opens the Google Colab notebook for easy setup and deployment

set -e

echo ""
echo "============================================================"
echo "   TITAN 2.0 - Google Colab Setup"
echo "============================================================"
echo ""
echo "This will help you open the TITAN Google Colab notebook."
echo ""
echo "The notebook provides:"
echo "  - One-click system installation"
echo "  - Interactive configuration interface"
echo "  - Full TITAN system (Brain + Bot + Dashboard)"
echo "  - Cloud deployment configuration"
echo "  - Oracle Free Tier deployment wizard"
echo ""
echo "============================================================"
echo ""

# Check if the notebook file exists
if [ ! -f "Titan_Google_Colab.ipynb" ]; then
    echo "❌ Error: Titan_Google_Colab.ipynb not found"
    echo "Please ensure you're in the Titan2.0 directory"
    exit 1
fi

echo "✅ Notebook file found"
echo ""
echo "📋 Instructions:"
echo ""
echo "Option 1: Upload to Google Colab"
echo "  1. Go to https://colab.research.google.com/"
echo "  2. Click 'Upload' and select Titan_Google_Colab.ipynb"
echo "  3. Follow the step-by-step cells in the notebook"
echo ""
echo "Option 2: Direct Link (if available)"
echo "  - Open the shared Colab link"
echo "  - Make a copy to your Google Drive"
echo "  - Run the cells in order"
echo ""
echo "📝 Next Steps:"
echo "  1. Configure your API keys when prompted"
echo "  2. Start the system components"
echo "  3. Access the dashboard"
echo "  4. Configure cloud deployment"
echo ""

# Try to open the file or URL
if command -v xdg-open > /dev/null; then
    # Linux
    echo "🌐 Opening Google Colab in browser..."
    xdg-open "https://colab.research.google.com/" || true
elif command -v open > /dev/null; then
    # macOS
    echo "🌐 Opening Google Colab in browser..."
    open "https://colab.research.google.com/" || true
else
    echo "⚠️  Could not automatically open browser"
    echo "Please manually visit: https://colab.research.google.com/"
fi

echo ""
echo "📁 Notebook location: $(pwd)/Titan_Google_Colab.ipynb"
echo ""
echo "For detailed instructions, see: GOOGLE_COLAB_GUIDE.md"
echo ""
