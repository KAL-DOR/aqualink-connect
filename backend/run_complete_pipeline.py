#!/usr/bin/env python3
"""
AquaHub Complete ML Pipeline with Temporal Alignment
======================================================

Solves three issues:
1. Temporal mismatch: Daily weather variables vs 15-day risk index
2. XGBoost output format with feature importance
3. DBSCAN clustering with hotspot detection

Pipeline: Feature Extraction → XGBoost → DBSCAN Clustering
"""

import sys
sys.path.insert(0, '/Users/carlos/Documents/Hackaton/aqualink/aqualink-connect/backend')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.ml.resilience_pipeline import WaterStressIngestor
import xgboost as xgb
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import json
import os
from collections import defaultdict

# Paths
DATA_DIR = '/Users/carlos/Documents/Hackaton/aqualink/aqualink-connect/backend/data'
OUTPUT_DIR = '/Users/carlos/Documents/Hackaton/aqualink/aqualink-connect/backend/output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# All 16 alcaldías with coordinates
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

# Risk mapping
drought_map = {'D0': 1, 'D1': 2, 'D2': 3, 'D3': 4, 'D4': 5}

def extract_temporal_dataset():
    """
    Issue #1: Handle temporal mismatch
    - Extract daily weather variables for Nov-Dec 2025
    - Risk index available every 15 days (coherent with repetition)
    """
    print(">>> 1. Loading Data with Temporal Alignment...")
    print("=" * 70)
    
    # Copy Excel from Downloads if not in data dir
    excel_source = '/Users/carlos/Downloads/Ciudad_de_Mexico_Sequia.xlsx'
    excel_path = f'{DATA_DIR}/Ciudad_de_Mexico_Sequia.xlsx'
    
    if not os.path.exists(excel_path) and os.path.exists(excel_source):
        import shutil
        shutil.copy(excel_source, excel_path)
        print(f"✓ Copied Excel file to: {excel_path}")
    
    # Read Excel with drought classifications
    df_excel = pd.read_excel(excel_path)
    
    # Get most recent dates with actual drought data (not NaN)
    # Data available up to mid-2024, so use the 4 most recent measurements
    all_date_cols = [col for col in df_excel.columns if isinstance(col, str) 
                     and len(col) == 10 and col[4] == '-' and col[7] == '-']
    
    # Find the last 4 dates that have non-NaN data for at least one municipality
    valid_dates = []
    for col in reversed(all_date_cols):
        has_data = df_excel[col].notna().any()
        if has_data:
            valid_dates.append(col)
            if len(valid_dates) >= 4:
                break
    
    date_cols = list(reversed(valid_dates))  # Put back in chronological order
    
    print(f"Risk measurement dates: {date_cols}")
    print(f"Total risk measurements: {len(date_cols)}")
    print("Note: Risk index every ~15 days, weather data daily")
    
    # Initialize ingestor
    ingestor = WaterStressIngestor(use_mock_data=False)
    
    training_records = []
    
    # Process each municipality
    for idx, row in df_excel.iterrows():
        municipio = row['NOMBRE_MUN']
        if municipio not in ALCALDias:
            continue
            
        lat, lon = ALCALDias[municipio]
        
        print(f"  Processing {municipio}...")
        
        # Process each risk measurement period
        for i, date_col in enumerate(date_cols):
            risk_value = row[date_col]
            if pd.isna(risk_value):
                continue
            
            risk_code = str(risk_value).strip()
            if risk_code not in drought_map:
                continue
                
            risk_index = drought_map[risk_code]
            current_date = datetime.strptime(date_col, '%Y-%m-%d')
            
            # Determine period end (next measurement or 15 days)
            if i + 1 < len(date_cols):
                next_date = datetime.strptime(date_cols[i + 1], '%Y-%m-%d')
                period_days = (next_date - current_date).days
            else:
                period_days = 15  # Default period
            
            # Generate daily samples for this period with same risk index
            for day_offset in range(period_days):
                daily_date = current_date + timedelta(days=day_offset)
                daily_date_str = daily_date.strftime('%Y-%m-%d')
                
                try:
                    # Generate daily feature vector - use historical mode to disable temporal filtering
                    vector = ingestor.get_vector(lat, lon, timestamp=daily_date, use_historical_mode=True)
                    
                    # Add metadata
                    vector['location_name'] = municipio
                    vector['date'] = daily_date_str
                    vector['lat'] = lat
                    vector['lon'] = lon
                    vector['risk_index'] = risk_index  # Same risk for entire period
                    vector['risk_code'] = risk_code
                    vector['measurement_date'] = date_col  # Original measurement
                    vector['day_in_period'] = day_offset
                    
                    training_records.append(vector)
                    
                except Exception as e:
                    print(f"    ✗ Error for {municipio} on {daily_date_str}: {e}")
                    continue
            
            print(f"    Period {date_col}: {period_days} days, Risk {risk_index}")
    
    df = pd.DataFrame(training_records)
    
    print(f"\n✓ Extracted {len(df)} daily samples")
    print(f"✓ Features: {len(df.columns)} columns")
    print(f"✓ Data Shape: {df.shape}")
    
    if len(df) > 0:
        # Show temporal distribution
        print("\nTemporal Distribution:")
        print(df['date'].value_counts().sort_index().head(10).to_string())
        
        print("\nRisk Distribution:")
        print(df['risk_index'].value_counts().sort_index().to_string())
    else:
        print("\n✗ Warning: No samples extracted!")
    
    return df

def train_xgboost_model(df):
    """
    Issue #2: Fix XGBoost output format
    Show data loading, training, and top 5 feature importance
    """
    print("\n>>> 2. Training XGBoost Model...")
    print("=" * 70)
    
    # Define features (exclude non-feature columns)
    # NOTE: Removed lat/lon to prevent overfitting - model should learn weather/social patterns, not memorize locations
    feature_cols = [
        'precip_roll_sum_7d', 'precip_roll_sum_30d', 'days_since_last_rain',
        'temp_max_24h', 'soil_moisture_root', 'social_report_count',
        'social_stress_index', 'leak_mention_flag', 'sentiment_polarity',
        'population_density', 'elevation_meters', 'is_weekend',
        'month_sin', 'month_cos'
    ]
    
    X = df[feature_cols]
    y = df['risk_index'] - 1  # Convert 1-5 to 0-4 for XGBoost
    
    print(f"    Data Shape: {df.shape}")
    print(f"    Features Used: {len(feature_cols)}")
    
    # Split - use time-based split to prevent data leakage
    # Sort by date and use first 80% for training, last 20% for testing
    df_sorted = df.sort_values('date')
    split_idx = int(len(df_sorted) * 0.8)
    
    train_df = df_sorted.iloc[:split_idx]
    test_df = df_sorted.iloc[split_idx:]
    
    X_train = train_df[feature_cols]
    y_train = train_df['risk_index'] - 1
    X_test = test_df[feature_cols]
    y_test = test_df['risk_index'] - 1
    
    print(f"    Train set: {len(train_df)} samples (dates: {train_df['date'].min()} to {train_df['date'].max()})")
    print(f"    Test set: {len(test_df)} samples (dates: {test_df['date'].min()} to {test_df['date'].max()})")
    
    # Train with regularization to prevent overfitting
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.05,
        objective='multi:softprob',
        num_class=5,
        eval_metric='mlogloss',
        random_state=42,
        reg_alpha=0.1,  # L1 regularization
        reg_lambda=1.0,  # L2 regularization
        min_child_weight=3,  # Minimum sum of instance weight needed in a child
        subsample=0.8,  # Subsample ratio of training instances
        colsample_bytree=0.8  # Subsample ratio of columns when constructing each tree
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n    Model Accuracy: {accuracy:.2f}")
    
    # Feature importance - Top 5
    importance_df = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False).head(5)
    
    print("\n    Top 5 Drivers of Water Shortage Prediction:")
    for idx, row in importance_df.iterrows():
        print(f"    - {row['feature']}: {row['importance']:.4f}")
    
    return model, feature_cols, df

def run_dbscan_clustering(df):
    """
    Issue #3: DBSCAN clustering with proper output format
    Show hotspots with lat, lon, risk_index, location_name, estimated_total_reports
    """
    print("\n>>> 3. Running Clustering (Goal 3)...")
    print("=" * 70)
    
    # Prepare data for clustering
    X_cluster = df[['lat', 'lon', 'risk_index', 'social_report_count']].values
    
    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_cluster)
    
    # DBSCAN
    dbscan = DBSCAN(eps=0.5, min_samples=5)
    cluster_labels = dbscan.fit_predict(X_scaled)
    
    df['cluster_label'] = cluster_labels
    
    # Analyze clusters
    n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
    total_reports = int(df['social_report_count'].sum())
    
    print(f"    Total Individual Reports Processed: {total_reports}")
    print(f"    Identified {n_clusters} High-Density 'Hotspots'.")
    print("    (These clusters represent specific neighborhoods reporting issues)")
    
    # Create hotspot summary
    hotspots = []
    unique_clusters = sorted(set(cluster_labels))
    
    for cluster_id in unique_clusters:
        if cluster_id == -1:  # Skip noise
            continue
            
        cluster_data = df[df['cluster_label'] == cluster_id]
        
        hotspot = {
            'cluster_label': cluster_id,
            'lat': cluster_data['lat'].mean(),
            'lon': cluster_data['lon'].mean(),
            'risk_index': cluster_data['risk_index'].mean(),
            'location_name': cluster_data['location_name'].mode()[0] if len(cluster_data) > 0 else 'Unknown',
            'estimated_total_reports': int(cluster_data['social_report_count'].sum()),
            'sample_count': len(cluster_data)
        }
        hotspots.append(hotspot)
    
    # Create DataFrame for output
    hotspots_df = pd.DataFrame(hotspots)
    
    # Save to CSV
    csv_path = f'{OUTPUT_DIR}/final_hotspots.csv'
    hotspots_df.to_csv(csv_path, index=False)
    print(f"\n    ✓ Hotspots saved to: {csv_path}")
    
    return hotspots_df

def print_final_output(hotspots_df):
    """Print the final output in the requested format."""
    print("\n>>> FINAL HOTSPOTS DETECTED <<<")
    print("=" * 70)
    
    # Reorder columns to match requested format
    output_df = hotspots_df[['cluster_label', 'lat', 'lon', 'risk_index', 
                              'location_name', 'estimated_total_reports']].copy()
    
    # Set cluster_label as index for display
    output_df_display = output_df.set_index('cluster_label')
    
    print(output_df_display.to_string())
    print("\n" + "=" * 70)
    
    # Also save a nicely formatted version
    json_path = f'{OUTPUT_DIR}/final_hotspots.json'
    output_df.to_json(json_path, orient='records', indent=2)
    print(f"✓ JSON output saved to: {json_path}")

def main():
    """Main execution pipeline."""
    print("=" * 70)
    print("AQUAHUB COMPLETE ML PIPELINE")
    print("Temporal Alignment → XGBoost → DBSCAN Clustering")
    print("=" * 70)
    print()
    
    # Step 1: Extract data with temporal alignment
    df = extract_temporal_dataset()
    
    if len(df) == 0:
        print("✗ No data extracted!")
        return
    
    # Save intermediate dataset
    df.to_csv(f'{OUTPUT_DIR}/training_dataset_temporal.csv', index=False)
    print(f"\n✓ Dataset saved: {OUTPUT_DIR}/training_dataset_temporal.csv")
    
    # Step 2: Train XGBoost
    model, feature_cols, df = train_xgboost_model(df)
    
    # Save model
    model_path = f'{OUTPUT_DIR}/xgboost_model.pkl'
    joblib.dump({'model': model, 'features': feature_cols}, model_path)
    print(f"\n✓ Model saved: {model_path}")
    
    # Step 3: DBSCAN Clustering
    hotspots_df = run_dbscan_clustering(df)
    
    # Print final output
    print_final_output(hotspots_df)
    
    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE!")
    print("=" * 70)
    print(f"\nOutput files in: {OUTPUT_DIR}/")
    print("  - training_dataset_temporal.csv")
    print("  - xgboost_model.pkl")
    print("  - final_hotspots.csv")
    print("  - final_hotspots.json")

if __name__ == "__main__":
    main()
