#!/bin/bash
# AquaHub Pipeline Runner
# =======================
# Usage: ./run_pipeline.sh [mode]
#   mode: mock | live | all

MODE=${1:-all}

echo "=========================================="
echo "AquaHub Water Resilience Pipeline"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
echo "Checking dependencies..."
pip install -q requests pandas numpy textblob python-dotenv 2>/dev/null || true

echo ""
echo "Running pipeline in mode: $MODE"
echo "----------------------------------------"
echo ""

# Run based on mode
if [ "$MODE" = "mock" ]; then
    # Mock mode only
    python3 -c "
import sys
sys.path.insert(0, '.')
import os
os.environ['USE_MOCK_DATA'] = 'true'
from app.ml.resilience_pipeline import WaterStressIngestor

print('[MOCK MODE - No API calls]')
print('='*50)

ingestor = WaterStressIngestor(use_mock_data=True)
vector = ingestor.get_vector(19.4326, -99.1332)

print('\nFeature Vector Generated:')
print('-'*50)
for key, value in vector.items():
    print(f'{key:30s}: {value}')
"

elif [ "$MODE" = "live" ]; then
    # Live mode with real APIs
    python3 -c "
import sys
sys.path.insert(0, '.')
from app.ml.resilience_pipeline import WaterStressIngestor

print('[LIVE MODE - Using real APIs and CSV]')
print('='*50)

ingestor = WaterStressIngestor(use_mock_data=False)

if ingestor.tweets_df is not None:
    print(f'✓ Loaded {len(ingestor.tweets_df)} tweets from CSV')
else:
    print('⚠ No CSV data loaded')

vector = ingestor.get_vector(19.4326, -99.1332)

print('\nFeature Vector Generated:')
print('-'*50)
for key, value in vector.items():
    print(f'{key:30s}: {value}')
"

else
    # Full test suite
    python3 -m app.ml.resilience_pipeline
fi

echo ""
echo "=========================================="
echo "Pipeline execution complete!"
echo "=========================================="
