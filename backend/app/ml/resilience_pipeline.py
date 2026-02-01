"""
AquaHub: Water Resilience Pipeline
==================================
A robust data ingestion pipeline that generates a Single-Row Feature Vector
representing the current water stress status of a specific geospatial location.

Uses scraped Twitter data from CSV file for social signals.

Author: AquaHub Team
Version: 2.0.0

API Keys Required:
------------------
1. OpenWeather API Key (Required)
   - Get free key at: https://openweathermap.org/api
   - Set in .env file: OPENWEATHER_API_KEY=your_key_here
   - Free tier: 1,000 calls/day

2. NASA POWER API (No key required)
   - Free public API for soil moisture data
   - Automatically used as fallback

Setup:
------
1. Copy .env.example to .env
2. Add your OpenWeather API key to .env
3. Or run: python backend/setup_api_keys.py

Usage:
------
    from backend.app.ml.resilience_pipeline import WaterStressIngestor
    
    # With API keys (live data)
    ingestor = WaterStressIngestor()
    vector = ingestor.get_vector(19.4326, -99.1332)
    
    # Without API keys (mock data)
    ingestor = WaterStressIngestor(use_mock_data=True)
    vector = ingestor.get_vector(19.4326, -99.1332)
"""

import os
import random
import math
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List, Tuple
import requests
import pandas as pd
import numpy as np
from textblob import TextBlob

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file manually
def _load_env_file():
    """Load .env file manually without python-dotenv dependency."""
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env_path = os.path.join(backend_dir, '.env')
    
    if not os.path.exists(env_path):
        # Try current directory
        env_path = os.path.join(os.getcwd(), '.env')
    
    if os.path.exists(env_path):
        logger.info(f"Loading environment from {env_path}")
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                # Parse KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    # Only set if not already in environment
                    if key not in os.environ:
                        os.environ[key] = value
        return True
    else:
        logger.warning(f"No .env file found at {env_path}")
        return False

# Load .env file
_env_loaded = _load_env_file()
if not _env_loaded:
    logger.info("Using system environment variables or mock data")


class WaterStressIngestor:
    """
    Orchestrates data collection from APIs and CSV data to output
    a clean, enriched water stress feature vector.
    
    Attributes:
        openweather_key (str): OpenWeatherMap API key
        use_mock_data (bool): If True, skip all network calls and return mock data
        location_context (str): Location name for social media queries (e.g., "Mexico City")
        csv_path (str): Path to CSV file with scraped Twitter data
        tweets_df (pd.DataFrame): Loaded and parsed tweet data
    """
    
    # Pain keywords for social signal detection (Mexico City specific)
    PAIN_KEYWORDS = ["sin agua", "tandeo", "no cae agua", "fuga de agua", 
                     "no hay agua", "falta agua", "cortaron el agua", 
                     "aguas con el agua", "torres de potrero", "coyuya",
                     "urgente sin agua", "sin suministro"]
    LEAK_KEYWORDS = ["fuga", "fuga de agua", "tubo roto", "gotera", "ruptura"]
    
    # NASA POWER Agroclimatology endpoint
    NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
    
    # Default CSV path - relative to backend directory
    # Try multiple possible locations
    _BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DEFAULT_CSV_PATH = os.environ.get(
        'CSV_DATA_PATH',
        os.path.join(_BASE_DIR, "data", "water_complaints_cdmx.csv")
    )
    
    def __init__(self, 
                 openweather_key: Optional[str] = None, 
                 use_mock_data: bool = None,
                 location_context: str = "Mexico City",
                 csv_path: Optional[str] = None):
        """
        Initialize the WaterStressIngestor.
        
        Args:
            openweather_key: OpenWeatherMap API key (or from env var OPENWEATHER_API_KEY)
            use_mock_data: If True, skip all network calls
            location_context: Location name for social media queries
            csv_path: Path to CSV file with scraped Twitter data. 
                     If None, uses default: backend/data/water_complaints_cdmx.csv
        """
        self.openweather_key = openweather_key or os.getenv("OPENWEATHER_API_KEY")
        
        # Handle mock mode: explicit param > env var > default False
        if use_mock_data is None:
            env_mock = os.getenv("USE_MOCK_DATA", "false").lower()
            self.use_mock_data = env_mock in ["true", "1", "yes"]
        else:
            self.use_mock_data = use_mock_data
            
        self.location_context = location_context
        
        # Use provided path or default path
        self.csv_path = csv_path or self.DEFAULT_CSV_PATH
        self.tweets_df = None
        
        # Load CSV data
        if self.csv_path and os.path.exists(self.csv_path):
            try:
                self._load_twitter_data(self.csv_path)
                logger.info(f"✓ Loaded {len(self.tweets_df)} tweets from {self.csv_path}")
            except Exception as e:
                logger.warning(f"Failed to load CSV data: {e}")
        else:
            logger.warning(f"CSV file not found: {self.csv_path}")
            logger.info(f"Expected CSV at: {self.DEFAULT_CSV_PATH}")
        
        if use_mock_data:
            logger.info("Mock mode enabled - no network calls will be made")
        elif not self.openweather_key:
            logger.warning("No OpenWeather API key provided - will use mock data fallback")
            
    def _load_twitter_data(self, csv_path: str) -> None:
        """
        Load and preprocess Twitter data from CSV file.
        
        Args:
            csv_path: Path to the CSV file with scraped tweets
        """
        # Load CSV
        df = pd.read_csv(csv_path)
        
        # Parse created_at dates
        # Format: "Sat Jan 31 13:22:20 +0000 2026"
        df['created_at'] = pd.to_datetime(df['created_at'], format='%a %b %d %H:%M:%S +0000 %Y')
        
        # Extract location information from text (neighborhoods/alcaldias mentioned)
        df['locations_mentioned'] = df['text'].apply(self._extract_locations_from_text)
        
        # Store processed dataframe
        self.tweets_df = df
        
    def _extract_locations_from_text(self, text: str) -> List[str]:
        """
        Extract location mentions from tweet text.
        
        Args:
            text: Tweet text
            
        Returns:
            List of location keywords found in text
        """
        text_lower = text.lower()
        locations = []
        
        # Common CDMX neighborhoods and areas
        location_keywords = {
            'coyoacán': ['coyoacán', 'coyoacan', 'alianza popular', 'villa panamericana', 'pedregal de carrasco'],
            'cuauhtémoc': ['cuauhtémoc', 'cuauhtemoc', 'roma', 'roma norte', 'centro', 'doctores'],
            'álamos': ['álamos', 'alamos', 'narvarte', 'del valle'],
            'tlahuac': ['tlahuac', 'tláhuac'],
            'xochimilco': ['xochimilco', 'santa cecilia tepetlapa', 'tepetlapa'],
            'gustavo a. madero': ['gustavo a. madero', 'zacatenco', 'san pedro zacatenco', 'ticoman'],
            'azcapotzalco': ['azcapotzalco', 'tlatilco'],
            'miguel hidalgo': ['miguel hidalgo', 'lomas de chapultepec', 'chapultepec', 'palmas'],
            'benito juárez': ['benito juárez', 'benito juarez', 'letrán valle', 'letran valle'],
            'iztapalapa': ['iztapalapa'],
            'tlalpan': ['tlalpan', 'jardines de tlalpan'],
            'ávaro obregón': ['álvaro obregón', 'alvaro obregon', 'torres de potrero', 'potrero'],
            'cuajimalpa': ['cuajimalpa', 'santa fe'],
            'iztacalco': ['iztacalco'],
            'milpa alta': ['milpa alta'],
            'magdalena contreras': ['magdalena contreras'],
            'tláhuac': ['tláhuac'],
        }
        
        for area, keywords in location_keywords.items():
            if any(kw in text_lower for kw in keywords):
                locations.append(area)
        
        return locations
            
    def get_vector(self, lat: float, lon: float, timestamp: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Generate a complete water stress feature vector for a given location.
        
        Args:
            lat: Latitude (-90 to 90)
            lon: Longitude (-180 to 180)
            timestamp: Optional specific time (default: now)
            
        Returns:
            Dictionary containing 15 water stress features (exact schema)
        """
        if timestamp is None:
            timestamp = datetime.now()
            
        if self.use_mock_data:
            return self._generate_mock_vector(timestamp)
        
        try:
            # --- BLOCK 1: HARD SENSORS ---
            hard_sensors = self._fetch_hard_sensors(lat, lon, timestamp)
            
            # --- BLOCK 2: SOFT SENSORS ---
            soft_sensors = self._fetch_soft_sensors(lat, lon, timestamp)
            
            # --- BLOCK 3: SPATIAL & TEMPORAL ---
            context_features = self._fetch_context_features(lat, lon, timestamp)
            
            # Merge all blocks
            vector = {**hard_sensors, **soft_sensors, **context_features}
            
            # Validate output
            self._validate_vector(vector)
            
            return vector
            
        except Exception as e:
            logger.error(f"Error generating feature vector: {e}")
            logger.info("Falling back to mock data")
            return self._generate_mock_vector(timestamp)
    
    def _fetch_hard_sensors(self, lat: float, lon: float, timestamp: datetime) -> Dict[str, Any]:
        """
        Fetch meteorological and soil moisture data.
        
        Returns:
            Dictionary with precip_roll_sum_7d, precip_roll_sum_30d, 
            days_since_last_rain, temp_max_24h, soil_moisture_root
        """
        logger.info(f"Fetching hard sensors for {lat}, {lon}")
        
        # Fetch OpenWeather 30-day history
        weather_data = self._fetch_openweather_history(lat, lon)
        
        if not weather_data:
            logger.warning("OpenWeather fetch failed, using synthetic weather")
            weather_data = self._generate_synthetic_weather_history(timestamp)
        
        # Calculate precipitation features
        precip_features = self._calculate_precipitation_features(weather_data, timestamp)
        
        # Get max temperature for today
        temp_max_24h = self._get_max_temperature(weather_data, timestamp)
        
        # Fetch NASA POWER soil moisture
        soil_moisture = self._fetch_nasa_soil_moisture(lat, lon, timestamp)
        
        return {
            'precip_roll_sum_7d': precip_features['precip_roll_sum_7d'],
            'precip_roll_sum_30d': precip_features['precip_roll_sum_30d'],
            'days_since_last_rain': precip_features['days_since_last_rain'],
            'temp_max_24h': temp_max_24h,
            'soil_moisture_root': soil_moisture
        }
    
    def _fetch_openweather_history(self, lat: float, lon: float) -> List[Dict]:
        """
        Fetch 30 days of daily weather history from OpenWeather OneCall API.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            List of daily weather records with 'date', 'precipitation', 'temp_max'
        """
        if not self.openweather_key:
            return []
        
        try:
            # OpenWeather API - FREE TIER (2.5)
            # One Call 3.0 requires paid subscription, so we use the free Current Weather API
            # Plus 5-day forecast API (both free with valid key)
            
            # 1. Get current weather (free)
            current_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={self.openweather_key}"
            logger.info(f"Fetching OpenWeather Current: lat={lat}, lon={lon}")
            current_response = requests.get(current_url, timeout=10)
            
            if current_response.status_code != 200:
                logger.warning(f"OpenWeather API error: {current_response.status_code} - {current_response.text[:100]}")
                return []
            
            current_data = current_response.json()
            logger.info(f"✓ OpenWeather Current API success: {current_data.get('name', 'Unknown')}")
            
            # 2. Get 5-day forecast (free) - provides 3-hour intervals, we'll aggregate to daily
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={self.openweather_key}"
            logger.info(f"Fetching OpenWeather Forecast...")
            forecast_response = requests.get(forecast_url, timeout=10)
            
            daily_records = []
            
            # Process current weather as "today"
            today = datetime.now()
            current_record = {
                'date': today,
                'precipitation': current_data.get('rain', {}).get('1h', 0) + current_data.get('snow', {}).get('1h', 0),
                'temp_max': current_data['main']['temp_max'],
                'temp_min': current_data['main']['temp_min'],
                'humidity': current_data['main']['humidity']
            }
            daily_records.append(current_record)
            
            # Process forecast data (aggregate 3-hour intervals to daily)
            if forecast_response.status_code == 200:
                forecast_data = forecast_response.json()
                forecast_list = forecast_data.get('list', [])
                
                # Group by date
                from collections import defaultdict
                daily_forecast = defaultdict(lambda: {'temps': [], 'precip': 0, 'humidity': []})
                
                for item in forecast_list:
                    date = datetime.fromtimestamp(item['dt']).date()
                    daily_forecast[date]['temps'].append(item['main']['temp'])
                    daily_forecast[date]['precip'] += item.get('rain', {}).get('3h', 0) + item.get('snow', {}).get('3h', 0)
                    daily_forecast[date]['humidity'].append(item['main']['humidity'])
                
                # Convert to records
                for date, data in daily_forecast.items():
                    if data['temps']:  # Only add if we have data
                        record = {
                            'date': datetime.combine(date, datetime.min.time()),
                            'precipitation': data['precip'],
                            'temp_max': max(data['temps']),
                            'temp_min': min(data['temps']),
                            'humidity': sum(data['humidity']) / len(data['humidity'])
                        }
                        daily_records.append(record)
                
                logger.info(f"✓ OpenWeather Forecast API: {len(daily_forecast)} days")
            else:
                logger.warning(f"Forecast API failed: {forecast_response.status_code}")
            
            # Sort by date and remove duplicates
            daily_records = sorted(daily_records, key=lambda x: x['date'])
            seen_dates = set()
            unique_records = []
            for record in daily_records:
                date_key = record['date'].date()
                if date_key not in seen_dates:
                    seen_dates.add(date_key)
                    unique_records.append(record)
            daily_records = unique_records
            
            # Pad with synthetic historical data to reach 30 days
            if len(daily_records) < 30:
                synthetic_start = daily_records[0]['date'] - timedelta(days=(30 - len(daily_records))) if daily_records else datetime.now() - timedelta(days=30)
                synthetic_days = self._generate_synthetic_weather_history(synthetic_start, days=30-len(daily_records))
                daily_records = synthetic_days + daily_records
            
            return daily_records[-30:]  # Return last 30 days
            
        except Exception as e:
            logger.error(f"OpenWeather fetch error: {e}")
            return []
    
    def _generate_synthetic_weather_history(self, start_date: datetime, days: int = 30) -> List[Dict]:
        """
        Generate realistic synthetic weather data for demo/fallback purposes.
        
        Args:
            start_date: Starting date for synthetic data
            days: Number of days to generate
            
        Returns:
            List of synthetic daily weather records
        """
        np.random.seed(42)  # Reproducible
        records = []
        
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            month = current_date.month
            
            # Seasonal patterns for Mexico City
            # Dry season: Nov-May (less rain)
            # Rainy season: Jun-Oct (more rain)
            is_rainy_season = 6 <= month <= 10
            
            # Base precipitation (mm)
            base_precip = 8.0 if is_rainy_season else 1.5
            precipitation = max(0, np.random.exponential(base_precip))
            
            # Temperature (Celsius) - Mexico City averages
            base_temp = 18.0
            seasonal_adjustment = 3.0 if is_rainy_season else 0.0
            temp_max = base_temp + seasonal_adjustment + np.random.normal(0, 3)
            temp_min = temp_max - 10 + np.random.normal(0, 2)
            
            records.append({
                'date': current_date,
                'precipitation': round(precipitation, 1),
                'temp_max': round(temp_max, 1),
                'temp_min': round(temp_min, 1),
                'humidity': int(np.random.uniform(40, 80))
            })
        
        return records
    
    def _calculate_precipitation_features(self, weather_data: List[Dict], 
                                          timestamp: datetime) -> Dict[str, float]:
        """
        Calculate rolling precipitation sums and days since last rain.
        
        Args:
            weather_data: List of daily weather records
            timestamp: Current timestamp
            
        Returns:
            Dictionary with precip_roll_sum_7d, precip_roll_sum_30d, days_since_last_rain
        """
        if not weather_data:
            return {
                'precip_roll_sum_7d': 0.0,
                'precip_roll_sum_30d': 0.0,
                'days_since_last_rain': 30
            }
        
        # Sort by date
        sorted_data = sorted(weather_data, key=lambda x: x['date'])
        
        # Extract precipitation values
        precip_values = [day['precipitation'] for day in sorted_data]
        
        # Calculate rolling sums (last 7 and 30 days)
        precip_roll_sum_7d = sum(precip_values[-7:]) if len(precip_values) >= 7 else sum(precip_values)
        precip_roll_sum_30d = sum(precip_values)
        
        # Calculate days since last rain (precip >= 1mm)
        days_since_last_rain = 0
        for day in reversed(sorted_data):
            if day['precipitation'] >= 1.0:
                break
            days_since_last_rain += 1
        
        return {
            'precip_roll_sum_7d': round(precip_roll_sum_7d, 1),
            'precip_roll_sum_30d': round(precip_roll_sum_30d, 1),
            'days_since_last_rain': min(days_since_last_rain, 30)
        }
    
    def _get_max_temperature(self, weather_data: List[Dict], timestamp: datetime) -> float:
        """Get maximum temperature from the most recent day."""
        if not weather_data:
            return 22.0  # Default for Mexico City
        
        # Get the most recent record
        latest = max(weather_data, key=lambda x: x['date'])
        return latest.get('temp_max', 22.0)
    
    def _fetch_nasa_soil_moisture(self, lat: float, lon: float, timestamp: datetime) -> float:
        """
        Fetch soil moisture from NASA POWER Agroclimatology API.
        
        Uses GWETPROF (Profile Soil Moisture) parameter which represents
        soil moisture in the root zone (0-1 scale, where 1 = saturated).
        
        Returns:
            Soil moisture as percentage (0-100), or estimated value if failed
        """
        try:
            # NASA POWER API parameters
            # GWETPROF = Profile Soil Moisture (fraction, 0-1)
            params = {
                'parameters': 'GWETPROF',
                'community': 'AG',
                'longitude': lon,
                'latitude': lat,
                'start': (timestamp - timedelta(days=7)).strftime('%Y%m%d'),
                'end': timestamp.strftime('%Y%m%d'),
                'format': 'JSON'
            }
            
            response = requests.get(self.NASA_POWER_URL, params=params, timeout=15)
            
            if response.status_code != 200:
                logger.warning(f"NASA POWER API error: {response.status_code}")
                return self._estimate_soil_moisture_from_weather(lat, lon, timestamp)
            
            data = response.json()
            
            # Check for API error messages
            if 'messages' in data.get('header', {}):
                errors = data['header']['messages']
                if errors:
                    logger.warning(f"NASA POWER API messages: {errors}")
            
            # Extract soil moisture from GWETPROF (Profile Soil Moisture)
            # GWETPROF is fraction 0-1, convert to percentage 0-100
            if 'properties' in data and 'parameter' in data['properties']:
                gwetprof_data = data['properties']['parameter'].get('GWETPROF', {})
                if gwetprof_data:
                    # Get most recent valid value (not -999.0 which is fill value)
                    valid_values = {k: v for k, v in gwetprof_data.items() if v != -999.0}
                    if valid_values:
                        latest_date = max(valid_values.keys())
                        soil_moisture_fraction = valid_values[latest_date]
                        # Convert fraction (0-1) to percentage (0-100)
                        soil_moisture_pct = min(100.0, max(0.0, soil_moisture_fraction * 100))
                        logger.info(f"NASA soil moisture: {soil_moisture_pct:.1f}% (from GWETPROF)")
                        return round(soil_moisture_pct, 1)
            
            logger.warning("No valid GWETPROF data found, using estimate")
            return self._estimate_soil_moisture_from_weather(lat, lon, timestamp)
            
        except Exception as e:
            logger.error(f"NASA soil moisture fetch error: {e}")
            return self._estimate_soil_moisture_from_weather(lat, lon, timestamp)
    
    def _estimate_soil_moisture_from_weather(self, lat: float, lon: float, 
                                              timestamp: datetime) -> float:
        """
        Estimate soil moisture from recent precipitation (fallback method).
        
        Simple model: Recent rain = higher soil moisture
        """
        # Fetch recent weather if available
        weather = self._fetch_openweather_history(lat, lon)
        if not weather:
            # Return reasonable default for Mexico City (~20-40%)
            return 25.0
        
        # Calculate weighted recent precipitation (more recent = more weight)
        total_weighted_precip = 0
        weights = [1.0, 0.8, 0.6, 0.4, 0.2]  # Last 5 days
        precip_values = sorted(weather, key=lambda x: x['date'])[-5:]
        
        for i, day in enumerate(precip_values):
            weight = weights[i] if i < len(weights) else 0.1
            total_weighted_precip += day['precipitation'] * weight
        
        # Convert to percentage (saturated ~50mm over 5 days = 100%)
        soil_moisture = min(100.0, max(5.0, (total_weighted_precip / 50.0) * 100))
        return round(soil_moisture, 1)
    
    def _fetch_soft_sensors(self, lat: float, lon: float, timestamp: datetime) -> Dict[str, Any]:
        """
        Fetch social signals from loaded CSV data.
        
        Args:
            lat: Latitude
            lon: Longitude
            timestamp: Current timestamp to filter recent tweets
            
        Returns:
            Dictionary with social_report_count, social_stress_index, 
            leak_mention_flag, sentiment_polarity, most_common_pain_keyword
        """
        logger.info(f"Fetching soft sensors for {lat}, {lon} at {timestamp}")
        
        try:
            # Use CSV data if available
            if self.tweets_df is not None and not self.tweets_df.empty:
                social_data = self._process_csv_tweets(lat, lon, timestamp)
                return social_data
            else:
                logger.warning("No CSV data loaded, using synthetic social signals")
                return self._generate_synthetic_social_signals()
            
        except Exception as e:
            logger.warning(f"Social signal processing failed: {e}")
            logger.info("Returning synthetic social sensor values")
            return self._generate_synthetic_social_signals()
    
    def _process_csv_tweets(self, lat: float, lon: float, timestamp: datetime) -> Dict[str, Any]:
        """
        Process tweets from loaded CSV data.
        
        Filters tweets by:
        1. Time window (last 7 days from timestamp)
        2. Location relevance (if location mentioned matches coordinates)
        
        Args:
            lat: Latitude
            lon: Longitude
            timestamp: Current timestamp
            
        Returns:
            Social signal features
        """
        if self.tweets_df is None or self.tweets_df.empty:
            return self._generate_synthetic_social_signals()
        
        # Filter by time window (last 7 days)
        time_window_start = timestamp - timedelta(days=7)
        recent_tweets = self.tweets_df[self.tweets_df['created_at'] >= time_window_start]
        
        if recent_tweets.empty:
            logger.info(f"No tweets in last 7 days from {timestamp}, using all available data")
            recent_tweets = self.tweets_df  # Fall back to all data
        
        # Determine which CDMX area this lat/lon corresponds to
        area = self._get_area_from_coordinates(lat, lon)
        
        # Filter by area if we can identify it
        if area:
            area_tweets = recent_tweets[recent_tweets['locations_mentioned'].apply(
                lambda x: area in x if isinstance(x, list) else False
            )]
            if not area_tweets.empty:
                recent_tweets = area_tweets
                logger.info(f"Filtered to {len(recent_tweets)} tweets for area: {area}")
        
        # Process the tweets
        return self._analyze_tweets(recent_tweets)
    
    def _get_area_from_coordinates(self, lat: float, lon: float) -> Optional[str]:
        """
        Map coordinates to CDMX area/alcaldia.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Area name or None
        """
        # CDMX area coordinate ranges (approximate)
        areas = {
            'coyoacán': (19.33, 19.37, -99.18, -99.12),
            'cuauhtémoc': (19.42, 19.46, -99.16, -99.12),
            'gustavo a. madero': (19.47, 19.52, -99.15, -99.08),
            'azcapotzalco': (19.47, 19.50, -99.20, -99.17),
            'miguel hidalgo': (19.40, 19.44, -99.22, -99.18),
            'benito juárez': (19.37, 19.41, -99.18, -99.14),
            'tlalpan': (19.27, 19.31, -99.20, -99.14),
            'iztapalapa': (19.34, 19.38, -99.08, -99.02),
            'tlahuac': (19.27, 19.31, -99.02, -98.96),
            'xochimilco': (19.24, 19.28, -99.14, -99.06),
            'ávaro obregón': (19.35, 19.39, -99.25, -99.19),
        }
        
        for area, (lat_min, lat_max, lon_min, lon_max) in areas.items():
            if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                return area
        
        return None
    
    def _analyze_tweets(self, tweets_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze tweet DataFrame to extract social signal features.
        
        Args:
            tweets_df: DataFrame of tweets
            
        Returns:
            Social signal features
        """
        if tweets_df.empty:
            return self._generate_synthetic_social_signals()
        
        # Count pain keyword occurrences
        keyword_counts = {kw: 0 for kw in self.PAIN_KEYWORDS}
        leak_count = 0
        sentiments = []
        
        for _, tweet in tweets_df.iterrows():
            text = str(tweet.get('text', '')).lower()
            
            # Count pain keywords
            for kw in self.PAIN_KEYWORDS:
                if kw in text:
                    keyword_counts[kw] += 1
            
            # Check for leak mentions
            if any(lk in text for lk in self.LEAK_KEYWORDS):
                leak_count += 1
            
            # Sentiment analysis
            try:
                blob = TextBlob(text)
                sentiments.append(blob.sentiment.polarity)
            except:
                sentiments.append(0.0)
        
        # Calculate metrics
        total_reports = len(tweets_df)  # Total tweets in the set
        pain_mentions = sum(keyword_counts.values())
        
        # Most common pain keyword (if any mentions found)
        if pain_mentions > 0:
            most_common_kw = max(keyword_counts.items(), key=lambda x: x[1])[0]
        else:
            most_common_kw = 'none'
        
        # Social stress index (0.0 to 1.0)
        # Based on: tweet count, pain mentions, and sentiment
        avg_sentiment = np.mean(sentiments) if sentiments else 0.0
        
        # Calculate stress components
        volume_factor = min(1.0, total_reports / 50.0)  # Normalize by 50 tweets
        pain_factor = min(1.0, pain_mentions / max(total_reports * 0.3, 1))  # % of tweets with pain
        sentiment_factor = (1.0 - (avg_sentiment + 1) / 2)  # Convert -1..1 to 0..1 (negative = higher stress)
        
        # Weighted combination
        stress_index = (volume_factor * 0.3 + pain_factor * 0.5 + sentiment_factor * 0.2)
        stress_index = min(1.0, max(0.0, stress_index))
        
        # Leak flag (>10% of reports mention leaks)
        leak_percentage = leak_count / max(total_reports, 1)
        leak_flag = 1 if leak_percentage > 0.1 else 0
        
        return {
            'social_report_count': total_reports,
            'social_stress_index': round(stress_index, 2),
            'leak_mention_flag': leak_flag,
            'sentiment_polarity': round(avg_sentiment, 2),
            'most_common_pain_keyword': most_common_kw
        }
    
    def _generate_synthetic_social_signals(self) -> Dict[str, Any]:
        """Generate realistic synthetic social signals for demo purposes."""
        # Simulate a moderately stressed day
        return {
            'social_report_count': random.randint(5, 25),
            'social_stress_index': round(random.uniform(0.2, 0.6), 2),
            'leak_mention_flag': random.choice([0, 0, 0, 1]),  # 25% chance
            'sentiment_polarity': round(random.uniform(-0.5, 0.2), 2),
            'most_common_pain_keyword': random.choice(['sin agua', 'tandeo', 'fuga de agua'])
        }
    
    def _fetch_context_features(self, lat: float, lon: float, 
                                 timestamp: datetime) -> Dict[str, Any]:
        """
        Fetch spatial and temporal context features.
        
        Returns:
            Dictionary with population_density, elevation_meters, 
            is_weekend, month_sin, month_cos
        """
        logger.info(f"Fetching context features for {lat}, {lon}")
        
        # Static/mock data for population and elevation
        # In production, fetch from GeoNames API or local database
        population_density = self._get_population_density(lat, lon)
        elevation = self._get_elevation(lat, lon)
        
        # Temporal features
        is_weekend = 1 if timestamp.weekday() >= 5 else 0
        
        # Cyclical month encoding
        month = timestamp.month
        month_sin = math.sin(2 * math.pi * month / 12)
        month_cos = math.cos(2 * math.pi * month / 12)
        
        return {
            'population_density': population_density,
            'elevation_meters': elevation,
            'is_weekend': is_weekend,
            'month_sin': round(month_sin, 4),
            'month_cos': round(month_cos, 4)
        }
    
    def _get_population_density(self, lat: float, lon: float) -> float:
        """
        Get population density for location.
        Mock implementation - returns realistic values for Mexico City area.
        """
        # Mexico City metropolitan area densities (people per km²)
        # Approximate based on coordinates
        
        # CDMX central area roughly: 19.2 to 19.6 lat, -99.3 to -98.9 lon
        if 19.2 <= lat <= 19.6 and -99.3 <= lon <= -98.9:
            # Densities vary by alcaldia
            return random.uniform(8000, 15000)
        else:
            # Outside central CDMX
            return random.uniform(1000, 5000)
    
    def _get_elevation(self, lat: float, lon: float) -> float:
        """
        Get elevation for location.
        Mock implementation - Mexico City is around 2,240m.
        """
        # Mexico City elevation varies by area
        base_elevation = 2240  # meters
        
        # Add some variation based on location
        variation = random.uniform(-200, 300)
        return round(base_elevation + variation, 1)
    
    def _generate_mock_vector(self, timestamp: datetime) -> Dict[str, Any]:
        """
        Generate a complete mock feature vector for hackathon/demo.
        Creates realistic scenarios: normal, dry, or crisis conditions.
        """
        logger.info("Generating mock feature vector")
        
        # Randomly choose a scenario
        scenario = random.choice(['normal', 'dry', 'crisis'])
        
        if scenario == 'normal':
            return {
                'precip_roll_sum_7d': round(random.uniform(20, 50), 1),
                'precip_roll_sum_30d': round(random.uniform(80, 150), 1),
                'days_since_last_rain': random.randint(0, 3),
                'temp_max_24h': round(random.uniform(20, 26), 1),
                'soil_moisture_root': round(random.uniform(35, 60), 1),
                'social_report_count': random.randint(0, 5),
                'social_stress_index': round(random.uniform(0.0, 0.2), 2),
                'leak_mention_flag': 0,
                'sentiment_polarity': round(random.uniform(-0.2, 0.5), 2),
                'most_common_pain_keyword': 'none',
                'population_density': random.uniform(8000, 15000),
                'elevation_meters': round(random.uniform(2100, 2400), 1),
                'is_weekend': random.choice([0, 1]),
                'month_sin': round(math.sin(2 * math.pi * timestamp.month / 12), 4),
                'month_cos': round(math.cos(2 * math.pi * timestamp.month / 12), 4)
            }
        
        elif scenario == 'dry':
            return {
                'precip_roll_sum_7d': round(random.uniform(0, 5), 1),
                'precip_roll_sum_30d': round(random.uniform(5, 25), 1),
                'days_since_last_rain': random.randint(10, 25),
                'temp_max_24h': round(random.uniform(26, 32), 1),
                'soil_moisture_root': round(random.uniform(10, 25), 1),
                'social_report_count': random.randint(10, 30),
                'social_stress_index': round(random.uniform(0.4, 0.7), 2),
                'leak_mention_flag': random.choice([0, 1]),
                'sentiment_polarity': round(random.uniform(-0.6, -0.1), 2),
                'most_common_pain_keyword': random.choice(['sin agua', 'tandeo']),
                'population_density': random.uniform(8000, 15000),
                'elevation_meters': round(random.uniform(2100, 2400), 1),
                'is_weekend': random.choice([0, 1]),
                'month_sin': round(math.sin(2 * math.pi * timestamp.month / 12), 4),
                'month_cos': round(math.cos(2 * math.pi * timestamp.month / 12), 4)
            }
        
        else:  # crisis
            return {
                'precip_roll_sum_7d': 0.0,
                'precip_roll_sum_30d': round(random.uniform(0, 8), 1),
                'days_since_last_rain': random.randint(25, 40),
                'temp_max_24h': round(random.uniform(30, 36), 1),
                'soil_moisture_root': round(random.uniform(5, 15), 1),
                'social_report_count': random.randint(40, 100),
                'social_stress_index': round(random.uniform(0.7, 1.0), 2),
                'leak_mention_flag': 1,
                'sentiment_polarity': round(random.uniform(-0.9, -0.4), 2),
                'most_common_pain_keyword': 'sin agua',
                'population_density': random.uniform(12000, 18000),
                'elevation_meters': round(random.uniform(2100, 2400), 1),
                'is_weekend': random.choice([0, 1]),
                'month_sin': round(math.sin(2 * math.pi * timestamp.month / 12), 4),
                'month_cos': round(math.cos(2 * math.pi * timestamp.month / 12), 4)
            }
    
    def _validate_vector(self, vector: Dict[str, Any]) -> bool:
        """
        Validate that the output vector matches the required schema.
        
        Raises:
            ValueError: If required keys are missing
        """
        required_keys = {
            'precip_roll_sum_7d', 'precip_roll_sum_30d', 'days_since_last_rain',
            'temp_max_24h', 'soil_moisture_root', 'social_report_count',
            'social_stress_index', 'leak_mention_flag', 'sentiment_polarity',
            'most_common_pain_keyword', 'population_density', 'elevation_meters',
            'is_weekend', 'month_sin', 'month_cos'
        }
        
        missing = required_keys - set(vector.keys())
        if missing:
            raise ValueError(f"Missing required keys in feature vector: {missing}")
        
        return True


# =============================================================================
# Usage Example & Testing
# =============================================================================

if __name__ == "__main__":
    # Example usage with CSV data
    print("=" * 60)
    print("AquaHub Water Resilience Pipeline - Test Run")
    print("=" * 60)
    
    # Default CSV path: backend/data/water_complaints_cdmx.csv
    # The ingestor will automatically look for the CSV in this location
    
    # Test 1: Mock mode (no CSV needed)
    print("\n[TEST 1] Mock Mode (No CSV)")
    print("-" * 40)
    
    ingestor_mock = WaterStressIngestor(use_mock_data=True)
    
    # Mexico City coordinates (Centro)
    lat, lon = 19.4326, -99.1332
    
    vector_mock = ingestor_mock.get_vector(lat, lon)
    
    print(f"Location: {lat}, {lon}")
    print(f"Generated {len(vector_mock)} features:")
    for key, value in list(vector_mock.items())[:5]:
        print(f"  {key}: {value}")
    print("  ...")
    
    # Test 2: Using default CSV path
    print("\n[TEST 2] Using Default CSV Data Path")
    print("-" * 40)
    print(f"Expected CSV location: {WaterStressIngestor.DEFAULT_CSV_PATH}")
    
    # Initialize with default path (automatically set)
    ingestor_csv = WaterStressIngestor(use_mock_data=False)
    
    if ingestor_csv.tweets_df is not None:
        # Test for Centro CDMX
        vector_csv = ingestor_csv.get_vector(lat, lon)
        print(f"✓ Loaded {len(ingestor_csv.tweets_df)} tweets from CSV")
        print(f"✓ Generated feature vector with real social data:")
        print(f"  social_report_count: {vector_csv['social_report_count']}")
        print(f"  social_stress_index: {vector_csv['social_stress_index']}")
        print(f"  most_common_pain_keyword: {vector_csv['most_common_pain_keyword']}")
    else:
        print(f"⚠ CSV file not found at default location")
        print(f"  Please place water_complaints_cdmx.csv in: backend/data/")
        print("  Run Test 1 (Mock Mode) instead")
    
    # Test 3: Multiple Locations with CSV
    print("\n[TEST 3] Multiple Locations (CSV Mode)")
    print("-" * 40)
    
    if ingestor_csv.tweets_df is not None:
        locations = [
            ("Centro CDMX", 19.4326, -99.1332),
            ("Coyoacán", 19.3467, -99.1617),
            ("Gustavo A. Madero", 19.4819, -99.1094),
        ]
        
        for name, lat, lon in locations:
            vector = ingestor_csv.get_vector(lat, lon)
            print(f"{name}:")
            print(f"  Reports: {vector['social_report_count']}, "
                  f"Stress: {vector['social_stress_index']}, "
                  f"Keyword: {vector['most_common_pain_keyword']}")
    
    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)
