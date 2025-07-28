#!/bin/bash
"""
Run the Nutanix Documentation Style Checker Streamlit App

This script sets up and runs the web-based style checker interface.
"""

echo "🚀 Starting Nutanix Documentation Style Checker Web App..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .styleguide.yaml exists
if [ ! -f ".styleguide.yaml" ]; then
    echo "⚠️  Warning: .styleguide.yaml not found!"
    echo "   The app will still run but may not have full functionality."
    echo "   Make sure the style guide configuration file is present."
fi

# Run Streamlit app
echo "🌐 Starting Streamlit app..."
echo "   The app will open in your default browser."
echo "   If it doesn't open automatically, go to: http://localhost:8501"
echo ""

streamlit run streamlit_style_checker.py