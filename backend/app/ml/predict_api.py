"""
FastAPI prediction service for drought risk forecasting
"""
try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
except ImportError as e:
    import sys
    print(f"ERROR: Required packages not installed: {e}")
    print("Please run: pip install fastapi uvicorn pydantic pandas numpy scikit-learn")
    sys.exit(1)

import pandas as pd
import numpy as np
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AquaHub Drought Risk API",
    description="Real-time drought risk predictions for Mexico City alcaldías",
    version="1.0.0"
)

# Load model on startup
try:
    # Try different paths
    import os
    possible_paths = [
        "backend/output/xgboost_model.pkl",
        "output/xgboost_model.pkl",
        os.path.join(os.path.dirname(__file__), "..", "..", "output", "xgboost_model.pkl"),
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "output", "xgboost_model.pkl")
    ]
    
    MODEL_PATH = None
    for path in possible_paths:
        if os.path.exists(path):
            MODEL_PATH = path
            logger.info(f"Found model at: {path}")
            break
    
    if MODEL_PATH is None:
        raise FileNotFoundError(f"Model not found in any of: {possible_paths}")
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    logger.info(f" Model loaded from {MODEL_PATH}")
except Exception as e:
    logger.error(f" Failed to load model: {e}")
    model = None

class PredictionRequest(BaseModel):
    latitude: float
    longitude: float
    population_density: Optional[float] = 15000.0
    elevation: Optional[float] = 2200.0
    days_to_predict: Optional[int] = 30

class PredictionResponse(BaseModel):
    location: Dict[str, float]
    risk_index: int
    risk_category: str
    confidence: float
    timestamp: str
    days_ahead: int

class ForecastResponse(BaseModel):
    location: Dict[str, float]
    forecast: List[Dict]
    generated_at: str

RISK_CATEGORIES = {
    0: "No Drought",
    1: "Abnormally Dry (D0)",
    2: "Moderate Drought (D1)",
    3: "Severe Drought (D2)",
    4: "Extreme Drought (D3)"
}

@app.get("/")
async def root():
    """API health check"""
    return {
        "service": "AquaHub Drought Risk API",
        "status": "healthy" if model else "unhealthy - model not loaded",
        "model_loaded": model is not None,
        "version": "1.0.0"
    }

@app.get("/alcaldias")
async def get_alcaldias():
    """List all 16 Mexico City alcaldías with coordinates"""
    alcaldias = [
        {"name": "Álvaro Obregón", "lat": 19.3861, "lon": -99.2234, "population": 823015},
        {"name": "Azcapotzalco", "lat": 19.4841, "lon": -99.1836, "population": 414711},
        {"name": "Benito Juárez", "lat": 19.3984, "lon": -99.1572, "population": 434153},
        {"name": "Coyoacán", "lat": 19.3502, "lon": -99.1621, "population": 620416},
        {"name": "Cuajimalpa", "lat": 19.3526, "lon": -99.2910, "population": 217686},
        {"name": "Cuauhtémoc", "lat": 19.4314, "lon": -99.1496, "population": 545884},
        {"name": "Gustavo A. Madero", "lat": 19.4827, "lon": -99.1138, "population": 1173351},
        {"name": "Iztacalco", "lat": 19.3947, "lon": -99.0976, "population": 404695},
        {"name": "Iztapalapa", "lat": 19.3491, "lon": -99.0539, "population": 1818086},
        {"name": "Magdalena Contreras", "lat": 19.3043, "lon": -99.2325, "population": 247622},
        {"name": "Miguel Hidalgo", "lat": 19.4072, "lon": -99.1902, "population": 414470},
        {"name": "Milpa Alta", "lat": 19.1860, "lon": -99.0236, "population": 152685},
        {"name": "Tláhuac", "lat": 19.2762, "lon": -99.0028, "population": 360265},
        {"name": "Tlalpan", "lat": 19.2872, "lon": -99.1634, "population": 677608},
        {"name": "Venustiano Carranza", "lat": 19.4242, "lon": -99.1130, "population": 443704},
        {"name": "Xochimilco", "lat": 19.2640, "lon": -99.1035, "population": 442178}
    ]
    return {"alcaldias": alcaldias, "count": len(alcaldias)}

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Predict drought risk for a specific location
    """
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Create feature vector (simplified - in production would fetch real weather data)
        features = generate_features(request.latitude, request.longitude, request.population_density, request.elevation)
        
        # Predict
        risk_index = int(model.predict(features)[0])
        
        # Get confidence (use max probability if available, otherwise default)
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(features)[0]
            confidence = float(np.max(proba))
        else:
            confidence = 0.85  # Default confidence
        
        return PredictionResponse(
            location={"lat": request.latitude, "lon": request.longitude},
            risk_index=risk_index,
            risk_category=RISK_CATEGORIES.get(risk_index, "Unknown"),
            confidence=confidence,
            timestamp=datetime.now().isoformat(),
            days_ahead=request.days_to_predict
        )
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/forecast", response_model=ForecastResponse)
async def forecast(request: PredictionRequest):
    """
    Generate 60-day drought risk forecast
    """
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        forecast_days = min(request.days_to_predict, 60)  # Max 60 days
        predictions = []
        
        base_date = datetime.now()
        
        for day in range(forecast_days):
            target_date = base_date + timedelta(days=day)
            
            # Generate features with temporal context
            features = generate_features(
                request.latitude, 
                request.longitude, 
                request.population_density, 
                request.elevation,
                date=target_date
            )
            
            # Predict
            risk_index = int(model.predict(features)[0])
            
            # Get confidence
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(features)[0]
                confidence = float(np.max(proba))
            else:
                confidence = 0.85
            
            predictions.append({
                "date": target_date.strftime("%Y-%m-%d"),
                "days_ahead": day,
                "risk_index": risk_index,
                "risk_category": RISK_CATEGORIES.get(risk_index, "Unknown"),
                "confidence": confidence
            })
        
        return ForecastResponse(
            location={"lat": request.latitude, "lon": request.longitude},
            forecast=predictions,
            generated_at=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Forecast error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/hotspots")
async def get_hotspots():
    """Get all drought hotspots from DBSCAN clustering"""
    try:
        import os
        # Try different paths
        possible_paths = [
            "backend/output/final_hotspots.csv",
            "output/final_hotspots.csv",
            os.path.join(os.path.dirname(__file__), "..", "..", "output", "final_hotspots.csv"),
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "output", "final_hotspots.csv")
        ]
        
        hotspots_path = None
        for path in possible_paths:
            if os.path.exists(path):
                hotspots_path = path
                logger.info(f"Found hotspots at: {path}")
                break
        
        if hotspots_path is None:
            raise FileNotFoundError(f"Hotspots file not found")
            
        hotspots_df = pd.read_csv(hotspots_path)
        hotspots = hotspots_df.to_dict('records')
        return {
            "hotspots": hotspots,
            "total": len(hotspots),
            "high_risk_count": len([h for h in hotspots if h.get('risk_index', 0) >= 2])
        }
    except Exception as e:
        logger.error(f"Hotspots error: {e}")
        raise HTTPException(status_code=500, detail="Failed to load hotspots data")

def generate_features(lat: float, lon: float, pop_density: float, elevation: float, date: datetime = None) -> np.ndarray:
    """
    Generate feature vector for prediction
    In production, this would fetch real-time data from:
    - OpenWeather API (weather features)
    - NASA POWER API (soil moisture)
    - Twitter CSV (social signals)
    """
    if date is None:
        date = datetime.now()
    
    # Temporal features
    month = date.month
    day_of_year = date.timetuple().tm_yday
    month_sin = np.sin(2 * np.pi * month / 12)
    month_cos = np.cos(2 * np.pi * month / 12)
    weekend_flag = 1 if date.weekday() >= 5 else 0
    
    # Mock weather features (in production, fetch from APIs)
    # Using typical CDMX values
    precip_7d = 15.0  # mm
    precip_30d = 45.0  # mm
    days_no_rain = 3
    temp_max = 25.0  # celsius
    soil_moisture = 0.60  # 0-1 scale
    
    # Social features (in production, fetch from Twitter analysis)
    social_report_count = 5
    social_stress_index = 0.3
    leak_flag = 0
    sentiment = -0.1
    pain_keywords = 2
    
    # Context features
    is_hotspot = 0  # Would be calculated based on DBSCAN results
    
    # Create feature array matching training format
    features = np.array([[
        precip_7d,
        precip_30d,
        days_no_rain,
        temp_max,
        soil_moisture,
        social_report_count,
        social_stress_index,
        leak_flag,
        sentiment,
        pain_keywords,
        lat,
        lon,
        is_hotspot,
        pop_density,
        elevation,
        weekend_flag,
        month_sin,
        month_cos
    ]])
    
    return features

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
