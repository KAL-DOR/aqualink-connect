#!/usr/bin/env python3
"""
Generate and save feature vectors for ML training
"""
import sys
sys.path.insert(0, '/Users/carlos/Documents/Hackaton/aqualink/aqualink-connect/backend')

from app.ml.resilience_pipeline import WaterStressIngestor
import pandas as pd
import json
from datetime import datetime

print("Generating feature vectors for ML training...")
print("=" * 70)

# Initialize
ingestor = WaterStressIngestor(use_mock_data=True)

# Generate vectors for multiple locations
locations = [
    ("Centro CDMX", 19.4326, -99.1332),
    ("Coyoacán", 19.3467, -99.1617),
    ("Gustavo A. Madero", 19.4819, -99.1094),
    ("Iztapalapa", 19.3550, -99.0630),
    ("Tlalpan", 19.2897, -99.1679),
    ("Xochimilco", 19.2608, -99.1039),
    ("Álvaro Obregón", 19.3594, -99.2029),
    ("Miguel Hidalgo", 19.4329, -99.2036),
]

data = []
for name, lat, lon in locations:
    vector = ingestor.get_vector(lat, lon)
    vector['location_name'] = name
    vector['lat'] = lat
    vector['lon'] = lon
    vector['timestamp'] = datetime.now().isoformat()
    data.append(vector)
    print(f"✓ Generated: {name}")

# Save to CSV (for ML training)
df = pd.DataFrame(data)
csv_path = '/Users/carlos/Documents/Hackaton/aqualink/aqualink-connect/backend/data/feature_vectors.csv'
df.to_csv(csv_path, index=False)
print(f"\n✓ Saved to CSV: {csv_path}")
print(f"  Shape: {df.shape} (rows, columns)")

# Save to JSON (for API usage)
json_path = '/Users/carlos/Documents/Hackaton/aqualink/aqualink-connect/backend/data/feature_vectors.json'
with open(json_path, 'w') as f:
    json.dump(data, f, indent=2)
print(f"✓ Saved to JSON: {json_path}")

print("\n" + "=" * 70)
print("SAMPLE DATA:")
print("=" * 70)
print(df[['location_name', 'social_stress_index', 'precip_roll_sum_7d', 'social_report_count']].to_string(index=False))

print("\n" + "=" * 70)
print("FEATURE VECTORS READY FOR ML!")
print("=" * 70)
