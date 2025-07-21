#!/bin/bash

echo "🆓 LAUNCHING ZERO-COST TWITTER BOT MAC APP"
echo "==========================================="
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    exit 1
fi

echo "✅ Python 3 found"

# Check if required packages are available
echo "🔍 Checking dependencies..."

python3 -c "import tkinter" 2>/dev/null && echo "✅ tkinter: OK" || echo "❌ tkinter: Missing"
python3 -c "import PIL" 2>/dev/null && echo "✅ Pillow: OK" || echo "⚠️  Pillow: Missing (images won't work)"
python3 -c "import matplotlib" 2>/dev/null && echo "✅ matplotlib: OK" || echo "⚠️  matplotlib: Missing (charts won't work)"
python3 -c "import requests" 2>/dev/null && echo "✅ requests: OK" || echo "⚠️  requests: Missing (API calls won't work)"

echo ""
echo "🚀 Starting Mac App..."
echo "💡 The app window should open shortly!"
echo ""

# Launch the app
python3 mac_app_with_timeline.py

echo ""
echo "👋 App closed. Thanks for using Zero-Cost Twitter Bot!"