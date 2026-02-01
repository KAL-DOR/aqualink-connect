#!/usr/bin/env python3
"""
Test .env loading without dependencies
"""
import os

def load_env_file(env_path):
    """Load .env file manually."""
    if not os.path.exists(env_path):
        return False
    
    print(f"✓ Found .env file: {env_path}")
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key not in os.environ:
                    os.environ[key] = value
    return True

# Test loading
env_path = '/Users/carlos/Documents/Hackaton/aqualink/aqualink-connect/backend/.env'
loaded = load_env_file(env_path)

print("\n" + "="*60)
print("ENVIRONMENT VARIABLES LOADED")
print("="*60)

api_key = os.getenv('OPENWEATHER_API_KEY', 'NOT SET')
print(f"OPENWEATHER_API_KEY: {api_key[:25]}..." if api_key != 'NOT SET' else "OPENWEATHER_API_KEY: NOT SET")

use_mock = os.getenv('USE_MOCK_DATA', 'not set')
print(f"USE_MOCK_DATA: {use_mock}")

nasa_user = os.getenv('NASA_EARTHDATA_USERNAME', 'not set')
print(f"NASA_EARTHDATA_USERNAME: {nasa_user}")

copernicus_key = os.getenv('COPERNICUS_CDS_API_KEY', 'not set')
if copernicus_key != 'not set':
    print(f"COPERNICUS_CDS_API_KEY: {copernicus_key[:30]}...")

print("="*60)

# Test the API key
if api_key and api_key != 'NOT SET':
    print(f"\n✓ API Key loaded: {api_key[:10]}...{api_key[-6:]}")
    print(f"  Length: {len(api_key)} characters")
    print(f"  Format: {'Valid (32 chars)' if len(api_key) == 32 else 'Invalid length!'}")
else:
    print("\n✗ No API key found in .env!")
