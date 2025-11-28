# Weather API Test Script
import requests
import time

BASE_URL = "http://localhost:8000"

def test_weather_forecast():
    """Test the weather forecast endpoint"""
    print("\n🌤️  Testing Weather Forecast API...")
    
    # Test with Kansas City coordinates
    params = {
        "latitude": 39.0997,
        "longitude": -94.5786
    }
    
    response = requests.get(f"{BASE_URL}/api/weather/forecast", params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Location: {data['location']['city']}, {data['location']['state']}")
        print(f"   Forecast periods: {len(data['forecast'])}")
        if data['forecast']:
            first = data['forecast'][0]
            print(f"   {first['name']}: {first['temperature']}°{first['temperatureUnit']} - {first['shortForecast']}")
    else:
        print(f"❌ Failed with status {response.status_code}: {response.text}")

def test_current_conditions():
    """Test the current conditions endpoint"""
    print("\n🌡️  Testing Current Conditions API...")
    
    # Test with New York City weather station
    station_id = "KNYC"
    
    response = requests.get(f"{BASE_URL}/api/weather/current/{station_id}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Station: {data['station']}")
        print(f"   Temperature: {data['temperature']['value']}°C")
        print(f"   Conditions: {data['description']}")
    else:
        print(f"❌ Failed with status {response.status_code}: {response.text}")

def test_rate_limiting():
    """Test rate limiting on weather endpoints"""
    print("\n⏱️  Testing Rate Limiting...")
    
    for i in range(15):
        response = requests.get(
            f"{BASE_URL}/api/weather/forecast",
            params={"latitude": 39.0997, "longitude": -94.5786}
        )
        
        if response.status_code == 429:
            print(f"🚫 Request {i+1}: Rate limited (429)")
        elif response.status_code == 200:
            print(f"✅ Request {i+1}: Success")
        else:
            print(f"❌ Request {i+1}: Error {response.status_code}")
        
        time.sleep(0.5)

if __name__ == "__main__":
    print("=" * 60)
    print("Weather API Test Suite")
    print("=" * 60)
    
    try:
        # Test basic endpoints first
        test_weather_forecast()
        test_current_conditions()
        
        # Test rate limiting
        test_rate_limiting()
        
        print("\n" + "=" * 60)
        print("Test suite completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server.")
        print("   Make sure the FastAPI server is running on http://localhost:8000")
        print("   Run: uvicorn app.main:app --reload")
