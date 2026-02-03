#!/usr/bin/env python3
"""
AquaHub 60-Day Drought Forecast
================================

Predicts drought risk for the next 60 days for all 16 CDMX alcaldías.
Uses trained XGBoost model to forecast future conditions.

Usage: python3 predict_60_days.py
Output: backend/data/forecast_60_days.json
"""

import sys
sys.path.insert(0, '/Users/carlos/Documents/Hackaton/aqualink/aqualink-connect/backend')

import pandas as pd
import numpy as np
import joblib
import json
from datetime import datetime, timedelta
from app.ml.resilience_pipeline import WaterStressIngestor
import os

# Paths
MODEL_PATH = '/Users/carlos/Documents/Hackaton/aqualink/aqualink-connect/backend/models/xgboost_supervised_model.pkl'
OUTPUT_PATH = '/Users/carlos/Documents/Hackaton/aqualink/aqualink-connect/backend/data/forecast_60_days.json'

# All 16 alcaldías
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

# Risk colors and labels
RISK_COLORS = {
    1: '#22c55e',  # Green - No Risk
    2: '#84cc16',  # Light green - Low
    3: '#eab308',  # Yellow - Moderate
    4: '#f97316',  # Orange - High
    5: '#ef4444',  # Red - Critical
}

RISK_LABELS = {
    1: 'No Risk',
    2: 'Low Risk',
    3: 'Moderate Risk',
    4: 'High Risk',
    5: 'Critical Risk'
}

def load_model():
    """Load trained XGBoost model."""
    if not os.path.exists(MODEL_PATH):
        print(f"✗ Model not found: {MODEL_PATH}")
        print("  Train model first with: python3 train_supervised_model.py")
        return None, None
    
    print("Loading trained model...")
    model_data = joblib.load(MODEL_PATH)
    model = model_data['model']
    feature_cols = model_data['feature_columns']
    
    print(f"✓ Model loaded (trained on {model_data['training_samples']} samples)")
    print(f"✓ Accuracy: {model_data['accuracy']:.1%}")
    
    return model, feature_cols

def generate_60_day_forecast():
    """Generate 60-day drought forecast for all alcaldías."""
    print("=" * 80)
    print("AQUAHUB 60-DAY DROUGHT FORECAST")
    print("=" * 80)
    print()
    
    # Load model
    model, feature_cols = load_model()
    if model is None:
        return
    
    # Initialize ingestor
    print("Initializing pipeline...")
    ingestor = WaterStressIngestor(use_mock_data=False)
    print(f"✓ Loaded {len(ingestor.tweets_df)} tweets from CSV")
    print()
    
    # Generate dates (next 60 days from now)
    start_date = datetime.now()
    dates = [start_date + timedelta(days=i) for i in range(60)]
    
    print(f"Forecast period: {dates[0].strftime('%Y-%m-%d')} to {dates[-1].strftime('%Y-%m-%d')}")
    print(f"Locations: {len(ALCALDias)} alcaldías")
    print(f"Total predictions: {len(ALCALDias) * len(dates)}")
    print()
    
    # Generate predictions
    print("Generating predictions...")
    print("-" * 80)
    
    all_predictions = []
    
    for loc_name, (lat, lon) in ALCALDias.items():
        print(f"\n📍 {loc_name}:")
        loc_predictions = []
        
        for date in dates:
            try:
                # Generate feature vector for this date
                vector = ingestor.get_vector(lat, lon, timestamp=date)
                
                # Extract features
                features = np.array([[vector[col] for col in feature_cols]])
                
                # Predict
                risk_pred = model.predict(features)[0]
                risk_proba = model.predict_proba(features)[0]
                confidence = risk_proba[risk_pred - 1]
                
                prediction = {
                    'date': date.strftime('%Y-%m-%d'),
                    'day_of_week': date.strftime('%A'),
                    'risk_index': int(risk_pred),
                    'risk_label': RISK_LABELS[risk_pred],
                    'risk_color': RISK_COLORS[risk_pred],
                    'confidence': float(confidence),
                    'features': {
                        'precip_7d': vector['precip_roll_sum_7d'],
                        'precip_30d': vector['precip_roll_sum_30d'],
                        'days_no_rain': vector['days_since_last_rain'],
                        'temp_max': vector['temp_max_24h'],
                        'soil_moisture': vector['soil_moisture_root'],
                        'social_stress': vector['social_stress_index'],
                        'tweet_count': vector['social_report_count']
                    }
                }
                
                loc_predictions.append(prediction)
                
            except Exception as e:
                print(f"  ✗ Error on {date}: {e}")
                continue
        
        # Summary for this location
        risk_counts = pd.Series([p['risk_index'] for p in loc_predictions]).value_counts()
        most_common_risk = risk_counts.index[0]
        
        print(f"  Most common risk: {RISK_LABELS[most_common_risk]} ({risk_counts[most_common_risk]} days)")
        
        all_predictions.append({
            'alcaldia': loc_name,
            'coordinates': {'lat': lat, 'lon': lon},
            'forecast': loc_predictions,
            'summary': {
                'total_days': len(loc_predictions),
                'risk_distribution': risk_counts.to_dict(),
                'highest_risk': max([p['risk_index'] for p in loc_predictions]),
                'avg_social_stress': np.mean([p['features']['social_stress'] for p in loc_predictions])
            }
        })
    
    print()
    print("=" * 80)
    print("SAVING FORECAST")
    print("=" * 80)
    
    # Save to JSON
    output = {
        'forecast_period': {
            'start': dates[0].strftime('%Y-%m-%d'),
            'end': dates[-1].strftime('%Y-%m-%d'),
            'total_days': 60
        },
        'generated_at': datetime.now().isoformat(),
        'model_type': 'XGBoost (Supervised Learning)',
        'alcaldias': all_predictions
    }
    
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"✓ Forecast saved to: {OUTPUT_PATH}")
    
    # Also save CSV summary
    csv_data = []
    for loc_data in all_predictions:
        for day in loc_data['forecast']:
            csv_data.append({
                'alcaldia': loc_data['alcaldia'],
                'date': day['date'],
                'risk_index': day['risk_index'],
                'risk_label': day['risk_label'],
                'confidence': day['confidence']
            })
    
    csv_path = OUTPUT_PATH.replace('.json', '.csv')
    pd.DataFrame(csv_data).to_csv(csv_path, index=False)
    print(f"✓ CSV summary saved to: {csv_path}")
    
    print()
    print("=" * 80)
    print("FORECAST COMPLETE!")
    print("=" * 80)
    print()
    print("📊 Summary:")
    print(f"  • {len(ALCALDias)} locations")
    print(f"  • {len(dates)} days")
    print(f"  • {len(all_predictions) * len(dates)} total predictions")
    print()
    print("Usage:")
    print("  • JSON: For API/frontend")
    print("  • CSV: For analysis/spreadsheets")
    print()
    print("Files:")
    print(f"  • {OUTPUT_PATH}")
    print(f"  • {csv_path}")

def print_sample_forecast():
    """Print a sample of the forecast for verification."""
    if not os.path.exists(OUTPUT_PATH):
        return
    
    with open(OUTPUT_PATH, 'r') as f:
        data = json.load(f)
    
    print()
    print("=" * 80)
    print("SAMPLE FORECAST (First 3 alcaldías, first 7 days)")
    print("=" * 80)
    
    for loc in data['alcaldias'][:3]:
        print(f"\n{loc['alcaldia']}:")
        for day in loc['forecast'][:7]:
            print(f"  {day['date']} ({day['day_of_week'][:3]}): "
                  f"Risk {day['risk_index']} ({day['risk_label']}) "
                  f"| Confidence: {day['confidence']:.1%}")

if __name__ == "__main__":
    generate_60_day_forecast()
    print_sample_forecast()
