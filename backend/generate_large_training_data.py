#!/usr/bin/env python3
"""
AquaHub Large-Scale Training Data Generator
============================================

Generates 1000+ training samples with real feature vectors from APIs.
Uses multiple dates per alcaldía to create temporal diversity.

Output: backend/data/large_training_dataset.csv
Samples: 1000+ (16 alcaldías × 65+ days)
Features: 15 real features from APIs
Target: Calculated risk score (1-5) based on feature thresholds
"""

import sys
sys.path.insert(0, '/Users/carlos/Documents/Hackaton/aqualink/aqualink-connect/backend')

from app.ml.resilience_pipeline import WaterStressIngestor
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import random

# All 16 CDMX Alcaldías with coordinates
ALCALDias = {
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

def calculate_risk_from_features(vector):
    """
    Calculate risk index (1-5) based on feature values.
    This creates synthetic ground truth labels for training.
    
    Scoring:
    - High social stress (>0.6): +20 points
    - Very high stress (>0.8): +40 points
    - Low rain 30d (<20mm): +20 points
    - Very low rain (<10mm): +40 points
    - Long dry spell (>14 days): +20 points
    - Very long dry (>21 days): +40 points
    - Low soil moisture (<20%): +20 points
    - Leak mentions: +10 points
    - Negative sentiment (<-0.3): +10 points
    
    Total 0-100 mapped to 1-5 scale
    """
    score = 0
    
    # Social stress (0-40 points)
    if vector['social_stress_index'] > 0.8:
        score += 40
    elif vector['social_stress_index'] > 0.6:
        score += 20
    elif vector['social_stress_index'] > 0.4:
        score += 10
    
    # Rain deficit (0-40 points)
    if vector['precip_roll_sum_30d'] < 10:
        score += 40
    elif vector['precip_roll_sum_30d'] < 20:
        score += 20
    elif vector['precip_roll_sum_30d'] < 40:
        score += 10
    
    # Dry spell (0-40 points)
    if vector['days_since_last_rain'] > 21:
        score += 40
    elif vector['days_since_last_rain'] > 14:
        score += 20
    elif vector['days_since_last_rain'] > 7:
        score += 10
    
    # Soil dryness (0-20 points)
    if vector['soil_moisture_root'] < 20:
        score += 20
    elif vector['soil_moisture_root'] < 30:
        score += 10
    
    # Infrastructure issues (0-10 points)
    if vector['leak_mention_flag'] == 1:
        score += 10
    
    # Sentiment (0-10 points)
    if vector['sentiment_polarity'] < -0.3:
        score += 10
    
    # Map 0-100 to 1-5
    if score >= 80:
        return 5  # Critical
    elif score >= 60:
        return 4  # High
    elif score >= 40:
        return 3  # Moderate
    elif score >= 20:
        return 2  # Low
    else:
        return 1  # No Risk

def generate_large_dataset(target_samples=1000):
    """Generate large training dataset with real API data."""
    print("=" * 80)
    print("AQUAHUB LARGE-SCALE TRAINING DATA GENERATOR")
    print("=" * 80)
    print()
    print(f"Target: {target_samples} samples")
    print(f"Alcaldías: {len(ALCALDias)} locations")
    print(f"Dates per location: ~{target_samples // len(ALCALDias)} days")
    print()
    
    # Calculate dates needed
    samples_per_location = target_samples // len(ALCALDias)
    days_per_location = samples_per_location
    
    # Initialize ingestor (using real APIs like in test_pipeline.py)
    print("Initializing WaterStressIngestor...")
    ingestor = WaterStressIngestor(use_mock_data=False)
    print(f"✓ Loaded {len(ingestor.tweets_df)} tweets from CSV")
    print()
    
    training_records = []
    base_date = datetime(2025, 12, 1)  # Start from Dec 1, 2025
    
    total_generated = 0
    
    for loc_idx, (location_name, (lat, lon)) in enumerate(ALCALDias.items(), 1):
        print(f"[{loc_idx:2d}/{len(ALCALDias)}] {location_name:25s} - Generating {days_per_location} days...")
        
        for day_offset in range(days_per_location):
            current_date = base_date + timedelta(days=day_offset)
            date_str = current_date.strftime('%Y-%m-%d')
            
            try:
                # Generate feature vector (this uses real APIs like in test_pipeline.py)
                vector = ingestor.get_vector(lat, lon, timestamp=current_date)
                
                # Calculate risk index from features
                risk_index = calculate_risk_from_features(vector)
                
                # Add metadata
                vector['location_name'] = location_name
                vector['date'] = date_str
                vector['lat'] = lat
                vector['lon'] = lon
                vector['risk_index'] = risk_index
                vector['day_of_year'] = current_date.timetuple().tm_yday
                vector['month'] = current_date.month
                
                training_records.append(vector)
                total_generated += 1
                
                # Progress update every 100 samples
                if total_generated % 100 == 0:
                    print(f"  ✓ Generated {total_generated} samples...")
                
            except Exception as e:
                print(f"  ✗ Error on {date_str}: {e}")
                continue
        
        print(f"  ✓ Completed: {days_per_location} samples")
    
    print()
    print("=" * 80)
    print("SAVING DATASET...")
    print("=" * 80)
    
    # Create DataFrame
    df = pd.DataFrame(training_records)
    
    # Reorder columns
    column_order = [
        'location_name', 'date', 'lat', 'lon', 'day_of_year', 'month',
        'precip_roll_sum_7d', 'precip_roll_sum_30d', 'days_since_last_rain',
        'temp_max_24h', 'soil_moisture_root',
        'social_report_count', 'social_stress_index', 'leak_mention_flag',
        'sentiment_polarity', 'most_common_pain_keyword',
        'population_density', 'elevation_meters', 'is_weekend',
        'month_sin', 'month_cos',
        'risk_index'
    ]
    
    df = df[column_order]
    
    # Save to CSV
    csv_path = '/Users/carlos/Documents/Hackaton/aqualink/aqualink-connect/backend/data/large_training_dataset.csv'
    df.to_csv(csv_path, index=False)
    print(f"✓ Saved to: {csv_path}")
    print(f"✓ Shape: {df.shape[0]} samples × {df.shape[1]} columns")
    
    # Save to JSON
    json_path = '/Users/carlos/Documents/Hackaton/aqualink/aqualink-connect/backend/data/large_training_dataset.json'
    df.to_json(json_path, orient='records', indent=2)
    print(f"✓ Saved to: {json_path}")
    
    print()
    print("=" * 80)
    print("DATASET SUMMARY")
    print("=" * 80)
    
    # Risk distribution
    risk_counts = df['risk_index'].value_counts().sort_index()
    print("\nRisk Index Distribution:")
    for risk, count in risk_counts.items():
        pct = (count / len(df)) * 100
        print(f"  Risk {risk}: {count:4d} samples ({pct:5.1f}%)")
    
    # Location distribution
    print("\nSamples per Alcaldía:")
    loc_counts = df['location_name'].value_counts()
    for loc, count in loc_counts.head().items():
        print(f"  {loc:25s}: {count} samples")
    
    # Feature statistics
    print("\nFeature Statistics (mean values):")
    print(f"  Social Stress Index: {df['social_stress_index'].mean():.2f}")
    print(f"  30-day Rainfall: {df['precip_roll_sum_30d'].mean():.1f}mm")
    print(f"  Days No Rain: {df['days_since_last_rain'].mean():.1f}")
    print(f"  Soil Moisture: {df['soil_moisture_root'].mean():.1f}%")
    
    print()
    print("=" * 80)
    print("LARGE TRAINING DATASET READY!")
    print("=" * 80)
    print()
    print("Usage:")
    print("  import pandas as pd")
    print("  df = pd.read_csv('backend/data/large_training_dataset.csv')")
    print()
    print("  # Features (X) - 15 features")
    print("  X = df.drop(['location_name', 'date', 'risk_index'], axis=1)")
    print("  y = df['risk_index']")
    print()
    print(f"✓ Total samples: {len(df)} (target was {target_samples})")
    print("✓ Ready for ML model training!")
    
    return df

if __name__ == "__main__":
    # Generate 1000+ samples
    df = generate_large_dataset(target_samples=1040)  # 16 locations × 65 days
