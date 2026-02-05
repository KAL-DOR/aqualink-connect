#!/usr/bin/env python3
"""
Quick test script for the Water Resilience Pipeline
"""
import sys
import os

# Add backend to path
sys.path.insert(0, '/Users/carlos/Documents/Hackaton/aqualink/aqualink-connect/backend')

# Set CSV path explicitly
os.environ['CSV_DATA_PATH'] = '/Users/carlos/Documents/Hackaton/aqualink/aqualink-connect/backend/data/water_complaints_cdmx.csv'

print("=" * 60)
print("AquaHub Pipeline - Quick Test")
print("=" * 60)

# Test 1: Check imports
print("\n[1] Testing imports...")
try:
    from app.ml.resilience_pipeline import WaterStressIngestor
    print("✓ Pipeline module imported successfully")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Initialize with mock mode
print("\n[2] Testing mock mode...")
try:
    ingestor = WaterStressIngestor(use_mock_data=True)
    vector = ingestor.get_vector(19.4326, -99.1332)
    print(f"✓ Mock vector generated: {len(vector)} features")
    print(f"  Sample: precip_7d={vector['precip_roll_sum_7d']}, "
          f"soil={vector['soil_moisture_root']}%")
except Exception as e:
    print(f"✗ Mock mode failed: {e}")

# Test 3: Check CSV loading
print("\n[3] Testing CSV data loading...")
try:
    csv_path = '/Users/carlos/Documents/Hackaton/aqualink/aqualink-connect/backend/data/water_complaints_cdmx.csv'
    if os.path.exists(csv_path):
        import pandas as pd
        df = pd.read_csv(csv_path)
        print(f"✓ CSV loaded: {len(df)} tweets")
        print(f"  Date range: {df['created_at'].min()} to {df['created_at'].max()}")
    else:
        print(f"✗ CSV not found: {csv_path}")
except Exception as e:
    print(f"✗ CSV test failed: {e}")

# Test 4: Test with real data (if API key available)
print("\n[4] Testing with real data...")
try:
    ingestor = WaterStressIngestor(use_mock_data=False)
    if ingestor.tweets_df is not None:
        print(f"✓ Loaded {len(ingestor.tweets_df)} tweets from CSV")
        vector = ingestor.get_vector(19.4326, -99.1332)
        print(f"✓ Real vector generated")
        print(f"  Social reports: {vector['social_report_count']}")
        print(f"  Social stress: {vector['social_stress_index']}")
        print(f"  Top keyword: {vector['most_common_pain_keyword']}")
    else:
        print("⚠ No CSV data loaded (check file path)")
except Exception as e:
    print(f"⚠ Real data test: {e}")

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)
