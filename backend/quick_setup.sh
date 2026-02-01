#!/bin/bash
# AquaHub Quick Setup Script
# ===========================
# One-command setup for API keys and configuration

echo "=========================================="
echo "AquaHub API Key Quick Setup"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "Error: Please run this script from the backend directory"
    echo "Usage: cd backend && ./quick_setup.sh"
    exit 1
fi

# Step 1: Check Python
echo "[1/5] Checking Python installation..."
if command -v python3 &> /dev/null; then
    echo "✓ Python3 found"
else
    echo "✗ Python3 not found. Please install Python 3.8 or higher"
    exit 1
fi

# Step 2: Install dependencies
echo ""
echo "[2/5] Installing dependencies..."
pip3 install -q python-dotenv requests pandas numpy textblob 2>/dev/null || pip install -q python-dotenv requests pandas numpy textblob
echo "✓ Dependencies installed"

# Step 3: Check for .env file
echo ""
echo "[3/5] Checking configuration..."
if [ -f ".env" ]; then
    echo "✓ .env file found"
    if grep -q "your_openweather_api_key" .env; then
        echo "⚠  API key not configured yet"
        echo ""
        echo "Please edit .env and add your OpenWeather API key:"
        echo "  OPENWEATHER_API_KEY=your_actual_key_here"
        echo ""
        echo "Get your free key at: https://openweathermap.org/api"
    else
        echo "✓ API key configured"
    fi
else
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "⚠  Please edit .env and add your OpenWeather API key:"
    echo "  OPENWEATHER_API_KEY=your_actual_key_here"
    echo ""
    echo "Get your free key at: https://openweathermap.org/api"
fi

# Step 4: Check for CSV data
echo ""
echo "[4/5] Checking data files..."
if [ -f "data/water_complaints_cdmx.csv" ]; then
    echo "✓ Twitter data CSV found"
else
    echo "⚠  Twitter data CSV not found"
    echo "   Expected: data/water_complaints_cdmx.csv"
    echo ""
    echo "Please copy your CSV file to:"
    echo "  backend/data/water_complaints_cdmx.csv"
fi

# Step 5: Test the setup
echo ""
echo "[5/5] Testing setup..."
python3 -c "
from app.ml.resilience_pipeline import WaterStressIngestor
print('✓ Pipeline module imports successfully')
print('✓ Ready to generate feature vectors')
" 2>/dev/null || echo "⚠  Module test skipped (run after configuring API key)"

echo ""
echo "=========================================="
echo "Setup Summary"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Get OpenWeather API Key:"
echo "   https://openweathermap.org/api"
echo ""
echo "2. Add key to backend/.env:"
echo "   OPENWEATHER_API_KEY=your_key_here"
echo ""
echo "3. Copy your CSV file:"
echo "   cp /path/to/water_complaints_cdmx.csv backend/data/"
echo ""
echo "4. Test the pipeline:"
echo "   python -m app.ml.resilience_pipeline"
echo ""
echo "For detailed help, see: API_SETUP_GUIDE.md"
echo ""
