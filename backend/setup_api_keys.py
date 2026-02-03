#!/usr/bin/env python3
"""
AquaHub API Key Setup Script
============================

This script helps you configure the API keys needed for the Water Resilience Pipeline.

Usage:
    python setup_api_keys.py

The script will:
1. Check for existing .env file
2. Guide you through obtaining API keys
3. Create or update the .env file with your keys
4. Test the API connections
"""

import os
import sys
from pathlib import Path

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def print_step(number, text):
    """Print a step indicator."""
    print(f"\n[Step {number}] {text}")
    print("-" * 70)

def get_yes_no(prompt):
    """Get yes/no input from user."""
    while True:
        response = input(f"{prompt} (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        print("Please enter 'yes' or 'no'")

def get_input(prompt, required=True):
    """Get input from user."""
    while True:
        value = input(f"{prompt}: ").strip()
        if value or not required:
            return value
        print("This field is required. Please enter a value.")

def check_existing_env():
    """Check if .env file already exists."""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        print("⚠️  Found existing .env file")
        with open(env_path, 'r') as f:
            content = f.read()
            if 'OPENWEATHER_API_KEY' in content and 'your_openweather' not in content:
                print("✓ API keys already configured in .env")
                return True, content
    return False, None

def setup_openweather():
    """Guide user through OpenWeather API setup."""
    print_step(1, "OpenWeather API Setup (REQUIRED)")
    
    print("""
The OpenWeather API provides essential weather data (temperature, precipitation,
humidity) needed for the water stress calculations.

To get your free API key:
1. Visit: https://openweathermap.org/api
2. Click "Sign Up" to create a free account
3. After registration, go to your account dashboard
4. Copy your API key (it looks like: 32 hex characters)

Free tier includes:
- 1,000 API calls/day (sufficient for our pipeline)
- Current weather + 5-day forecast

Note: The free tier does NOT include historical data, so we'll supplement
with synthetic historical data for the 30-day rolling calculations.
""")
    
    if get_yes_no("Do you have an OpenWeather API key?"):
        api_key = get_input("Enter your OpenWeather API key")
        print("✓ API key received")
        return api_key
    else:
        print("""
⚠️  No API key provided. You can still run the pipeline in MOCK MODE,
    which generates realistic synthetic data for testing.
    
    To use mock mode, set USE_MOCK_DATA=true in your .env file.
""")
        return None

def create_env_file(openweather_key=None):
    """Create the .env file with configured keys."""
    print_step(3, "Creating .env Configuration File")
    
    env_path = Path(__file__).parent / ".env"
    example_path = Path(__file__).parent / ".env.example"
    
    # Read example file as template
    with open(example_path, 'r') as f:
        template = f.read()
    
    # Replace placeholder with actual key
    if openweather_key:
        content = template.replace(
            'OPENWEATHER_API_KEY=your_openweather_api_key_here',
            f'OPENWEATHER_API_KEY={openweather_key}'
        )
        content = content.replace(
            'USE_MOCK_DATA=false',
            'USE_MOCK_DATA=false'
        )
    else:
        content = template.replace(
            'OPENWEATHER_API_KEY=your_openweather_api_key_here',
            'OPENWEATHER_API_KEY='  # Empty key
        )
        content = content.replace(
            'USE_MOCK_DATA=false',
            'USE_MOCK_DATA=true'  # Enable mock mode
        )
    
    # Write the .env file
    with open(env_path, 'w') as f:
        f.write(content)
    
    print(f"✓ Created .env file at: {env_path}")
    return env_path

def test_api_key(api_key):
    """Test if the OpenWeather API key works."""
    print_step(4, "Testing API Connection")
    
    try:
        import requests
        
        # Test with Mexico City coordinates
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'lat': 19.4326,
            'lon': -99.1332,
            'appid': api_key,
            'units': 'metric'
        }
        
        print("Testing connection to OpenWeather API...")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            city = data['name']
            print(f"✓ API connection successful!")
            print(f"  Current weather in {city}: {temp}°C")
            return True
        elif response.status_code == 401:
            print("✗ API Error: Invalid API key")
            print("  Please check your key and try again")
            return False
        else:
            print(f"✗ API Error: Status code {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

def print_next_steps(env_path, api_key_works):
    """Print next steps for the user."""
    print_step(5, "Next Steps")
    
    print(f"""
✓ Setup complete! Your configuration is saved at:
  {env_path}

To use the Water Resilience Pipeline:

1. Install dependencies:
   cd backend
   pip install -r requirements.txt

2. Run the pipeline:
   cd backend
   python -m app.ml.resilience_pipeline

3. Or use in your code:
   from app.ml.resilience_pipeline import WaterStressIngestor
   
   ingestor = WaterStressIngestor()
   vector = ingestor.get_vector(19.4326, -99.1332)
   print(vector)

Optional API Keys (for future enhancements):
- NASA Earthdata: For GRACE groundwater data
- Copernicus CDS: For ERA5 high-quality weather data
- INEGI: For Mexico socioeconomic data

See .env.example for configuration options.
""")
    
    if not api_key_works:
        print("""
⚠️  Your API key didn't work in the test, but the .env file was created.
    You can:
    1. Edit the .env file manually and fix the OPENWEATHER_API_KEY
    2. Use mock mode (set USE_MOCK_DATA=true) for testing without API calls
    3. Re-run this script after getting a valid key
""")

def main():
    """Main setup flow."""
    print_header("AquaHub API Key Setup")
    
    print("""
Welcome! This script will help you configure the API keys needed for the
AquaHub Water Resilience Pipeline.

The pipeline requires weather data to calculate water stress indicators.
We'll set up the minimum required configuration.
""")
    
    # Check for existing config
    has_config, existing_content = check_existing_env()
    
    if has_config:
        if get_yes_no("API keys already configured. Reconfigure?"):
            pass  # Continue with setup
        else:
            print("\n✓ Keeping existing configuration. Setup complete!")
            return
    
    # Step 1: OpenWeather API
    api_key = setup_openweather()
    
    # Step 2: Create .env file
    env_path = create_env_file(api_key)
    
    # Step 3: Test API key (if provided)
    api_works = False
    if api_key:
        api_works = test_api_key(api_key)
    
    # Step 4: Print next steps
    print_next_steps(env_path, api_works)
    
    print("\n" + "=" * 70)
    print("  Setup Complete!")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
