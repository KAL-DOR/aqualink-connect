#!/usr/bin/env python3
"""
AquaHub ML Training Data Generator
==================================

Generates labeled training dataset for drought prediction model.
Uses the provided risk indices as target variables.

Output: backend/data/training_dataset.csv
Features: 15 water stress features
Target: risk_index (1-5 scale)
"""

import sys
sys.path.insert(0, '/Users/carlos/Documents/Hackaton/aqualink/aqualink-connect/backend')

from app.ml.resilience_pipeline import WaterStressIngestor
from datetime import datetime
import pandas as pd
import json

# Training data with risk indices (ground truth labels)
TRAINING_DATA = [
    {'location_name': 'Azcapotzalco', 'date': '2025-12-31', 'risk_index': 4},
    {'location_name': 'Azcapotzalco', 'date': '2026-01-15', 'risk_index': 5},
    {'location_name': 'Coyoacán', 'date': '2025-12-31', 'risk_index': 3},
    {'location_name': 'Coyoacán', 'date': '2026-01-15', 'risk_index': 5},
    {'location_name': 'Cuajimalpa de Morelos', 'date': '2025-12-31', 'risk_index': 5},
    {'location_name': 'Cuajimalpa de Morelos', 'date': '2026-01-15', 'risk_index': 2},
    {'location_name': 'Gustavo A. Madero', 'date': '2025-12-31', 'risk_index': 3},
    {'location_name': 'Gustavo A. Madero', 'date': '2026-01-15', 'risk_index': 3},
    {'location_name': 'Iztacalco', 'date': '2025-12-31', 'risk_index': 3},
    {'location_name': 'Iztacalco', 'date': '2026-01-15', 'risk_index': 5},
    {'location_name': 'Iztapalapa', 'date': '2025-12-31', 'risk_index': 4},
    {'location_name': 'Iztapalapa', 'date': '2026-01-15', 'risk_index': 3},
    {'location_name': 'La Magdalena Contreras', 'date': '2025-12-31', 'risk_index': 5},
    {'location_name': 'La Magdalena Contreras', 'date': '2026-01-15', 'risk_index': 2},
    {'location_name': 'Milpa Alta', 'date': '2025-12-31', 'risk_index': 4},
    {'location_name': 'Milpa Alta', 'date': '2026-01-15', 'risk_index': 2},
    {'location_name': 'Álvaro Obregón', 'date': '2025-12-31', 'risk_index': 4},
    {'location_name': 'Álvaro Obregón', 'date': '2026-01-15', 'risk_index': 5},
    {'location_name': 'Tláhuac', 'date': '2025-12-31', 'risk_index': 1},
    {'location_name': 'Tláhuac', 'date': '2026-01-15', 'risk_index': 4},
    {'location_name': 'Tlalpan', 'date': '2025-12-31', 'risk_index': 2},
    {'location_name': 'Tlalpan', 'date': '2026-01-15', 'risk_index': 5},
    {'location_name': 'Xochimilco', 'date': '2025-12-31', 'risk_index': 4},
    {'location_name': 'Xochimilco', 'date': '2026-01-15', 'risk_index': 1},
    {'location_name': 'Benito Juárez', 'date': '2025-12-31', 'risk_index': 1},
    {'location_name': 'Benito Juárez', 'date': '2026-01-15', 'risk_index': 3},
    {'location_name': 'Cuauhtémoc', 'date': '2025-12-31', 'risk_index': 3},
    {'location_name': 'Cuauhtémoc', 'date': '2026-01-15', 'risk_index': 2},
    {'location_name': 'Miguel Hidalgo', 'date': '2025-12-31', 'risk_index': 4},
    {'location_name': 'Miguel Hidalgo', 'date': '2026-01-15', 'risk_index': 4},
    {'location_name': 'Venustiano Carranza', 'date': '2025-12-31', 'risk_index': 3},
    {'location_name': 'Venustiano Carranza', 'date': '2026-01-15', 'risk_index': 4}
]

# Coordinates for each alcaldía
ALCALDIA_COORDINATES = {
    'Azcapotzalco': (19.4869, -99.1838),
    'Coyoacán': (19.3467, -99.1617),
    'Cuajimalpa de Morelos': (19.3556, -99.2914),
    'Gustavo A. Madero': (19.4819, -99.1094),
    'Iztacalco': (19.3953, -99.0975),
    'Iztapalapa': (19.3550, -99.0630),
    'La Magdalena Contreras': (19.3221, -99.2310),
    'Milpa Alta': (19.1924, -99.0230),
    'Álvaro Obregón': (19.3594, -99.2029),
    'Tláhuac': (19.2869, -99.0030),
    'Tlalpan': (19.2897, -99.1679),
    'Xochimilco': (19.2608, -99.1039),
    'Benito Juárez': (19.3984, -99.1676),
    'Cuauhtémoc': (19.4326, -99.1332),
    'Miguel Hidalgo': (19.4329, -99.2036),
    'Venustiano Carranza': (19.4239, -99.1074)
}

# Risk index to color mapping for frontend
RISK_COLORS = {
    1: '#22c55e',  # Green - No risk
    2: '#84cc16',  # Light green - Low risk
    3: '#eab308',  # Yellow - Moderate risk
    4: '#f97316',  # Orange - High risk
    5: '#ef4444',  # Red - Critical risk
}

RISK_LABELS = {
    1: 'No Risk',
    2: 'Low Risk',
    3: 'Moderate Risk',
    4: 'High Risk',
    5: 'Critical Risk'
}

def generate_training_dataset():
    """Generate training dataset with feature vectors and risk indices."""
    print("=" * 80)
    print("AQUAHUB ML TRAINING DATA GENERATOR")
    print("=" * 80)
    print()
    print(f"Generating {len(TRAINING_DATA)} training samples...")
    print(f"  • {len(ALCALDIA_COORDINATES)} unique alcaldías")
    print(f"  • 2 dates per location")
    print(f"  • 15 features per sample")
    print(f"  • 1 target variable (risk_index)")
    print()
    
    # Initialize ingestor
    ingestor = WaterStressIngestor(use_mock_data=False)
    
    training_records = []
    
    for i, record in enumerate(TRAINING_DATA, 1):
        location_name = record['location_name']
        date_str = record['date']
        risk_index = record['risk_index']
        
        # Get coordinates
        lat, lon = ALCALDIA_COORDINATES[location_name]
        
        # Parse date
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        
        print(f"[{i:2d}/{len(TRAINING_DATA)}] {location_name:25s} | {date_str} | Risk: {risk_index}")
        
        # Generate feature vector
        vector = ingestor.get_vector(lat, lon, timestamp=date_obj)
        
        # Add metadata
        vector['location_name'] = location_name
        vector['date'] = date_str
        vector['lat'] = lat
        vector['lon'] = lon
        vector['risk_index'] = risk_index
        vector['risk_label'] = RISK_LABELS[risk_index]
        vector['risk_color'] = RISK_COLORS[risk_index]
        
        training_records.append(vector)
    
    print()
    print("=" * 80)
    print("SAVING TRAINING DATASET...")
    print("=" * 80)
    
    # Create DataFrame
    df = pd.DataFrame(training_records)
    
    # Reorder columns: metadata first, then features, then target
    column_order = [
        'location_name', 'date', 'lat', 'lon',
        'precip_roll_sum_7d', 'precip_roll_sum_30d', 'days_since_last_rain',
        'temp_max_24h', 'soil_moisture_root',
        'social_report_count', 'social_stress_index', 'leak_mention_flag',
        'sentiment_polarity', 'most_common_pain_keyword',
        'population_density', 'elevation_meters', 'is_weekend',
        'month_sin', 'month_cos',
        'risk_index', 'risk_label', 'risk_color'
    ]
    
    df = df[column_order]
    
    # Save to CSV
    csv_path = '/Users/carlos/Documents/Hackaton/aqualink/aqualink-connect/backend/data/training_dataset.csv'
    df.to_csv(csv_path, index=False)
    print(f"✓ Saved to: {csv_path}")
    print(f"✓ Shape: {df.shape[0]} samples × {df.shape[1]} columns")
    
    # Also save to JSON for API usage
    json_path = '/Users/carlos/Documents/Hackaton/aqualink/aqualink-connect/backend/data/training_dataset.json'
    df.to_json(json_path, orient='records', indent=2)
    print(f"✓ Saved to: {json_path}")
    
    print()
    print("=" * 80)
    print("DATASET SUMMARY")
    print("=" * 80)
    
    # Show risk distribution
    risk_counts = df['risk_index'].value_counts().sort_index()
    print("\nRisk Index Distribution:")
    for risk, count in risk_counts.items():
        color = RISK_COLORS[risk]
        label = RISK_LABELS[risk]
        print(f"  {risk} ({label:15s}): {count:2d} samples {color}")
    
    print()
    print("Sample Features (first 3 columns):")
    print(df[['location_name', 'date', 'risk_index', 'social_stress_index', 'precip_roll_sum_7d']].head().to_string(index=False))
    
    print()
    print("=" * 80)
    print("TRAINING DATASET READY!")
    print("=" * 80)
    print()
    print("Usage in Python:")
    print("  import pandas as pd")
    print("  df = pd.read_csv('backend/data/training_dataset.csv')")
    print()
    print("  # Features (X)")
    print("  feature_cols = ['precip_roll_sum_7d', 'social_stress_index', ...]")
    print("  X = df[feature_cols]")
    print()
    print("  # Target (y)")
    print("  y = df['risk_index']")
    print()
    print("  # Train model")
    print("  from sklearn.ensemble import RandomForestClassifier")
    print("  model = RandomForestClassifier()")
    print("  model.fit(X, y)")
    
    return df

if __name__ == "__main__":
    df = generate_training_dataset()
