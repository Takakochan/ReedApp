"""
Weather Service for Reed Django App
Fetches weather and location data using free APIs
"""
import requests
import os
from decimal import Decimal
from typing import Dict, Optional, Tuple


class WeatherService:
    """Service to fetch weather and location data"""
    
    def __init__(self):
        # OpenWeatherMap API (free tier: 1000 calls/day)
        # Sign up at https://openweathermap.org/api
        self.weather_api_key = os.environ.get('OPENWEATHER_API_KEY')
        self.weather_base_url = "https://api.openweathermap.org/data/2.5"
        
        # Alternative free APIs for location
        self.geocoding_url = "https://nominatim.openstreetmap.org/search"
        
    def get_location_from_name(self, location_name: str) -> Optional[Dict]:
        """
        Get coordinates and details from location name
        Uses OpenStreetMap Nominatim (free, no API key needed)
        """
        if not location_name:
            return None
            
        try:
            params = {
                'q': location_name,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1
            }
            
            headers = {
                'User-Agent': 'ReedTracker/1.0'  # Required by Nominatim
            }
            
            response = requests.get(
                self.geocoding_url, 
                params=params, 
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    location = data[0]
                    return {
                        'location': location.get('display_name', location_name),
                        'latitude': Decimal(location.get('lat', '0')),
                        'longitude': Decimal(location.get('lon', '0')),
                        'city': location.get('address', {}).get('city', ''),
                        'country': location.get('address', {}).get('country', '')
                    }
        except Exception as e:
            print(f"Error geocoding location: {e}")
        
        return None
    
    def get_location_name_from_coordinates(self, lat: float, lon: float) -> Optional[str]:
        """
        Get location name from coordinates (reverse geocoding)
        Uses OpenStreetMap Nominatim (free, no API key needed)
        """
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json',
                'addressdetails': 1
            }
            
            headers = {
                'User-Agent': 'ReedTracker/1.0'  # Required by Nominatim
            }
            
            response = requests.get(
                "https://nominatim.openstreetmap.org/reverse", 
                params=params, 
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    # Try to get a nice location name
                    address = data.get('address', {})
                    city = address.get('city') or address.get('town') or address.get('village')
                    country = address.get('country')
                    
                    if city and country:
                        return f"{city}, {country}"
                    elif country:
                        return country
                    else:
                        return data.get('display_name', '').split(',')[0]
        
        except Exception as e:
            print(f"Error reverse geocoding: {e}")
        
        return None
    
    def get_weather_by_coordinates(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Get current weather by coordinates
        Requires OpenWeatherMap API key
        """
        if not self.weather_api_key:
            # Return None so the calling function can still provide location/altitude
            print("No OpenWeatherMap API key provided - weather data unavailable")
            return None
            
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.weather_api_key,
                'units': 'metric'  # Celsius
            }
            
            response = requests.get(
                f"{self.weather_base_url}/weather",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'temperature': Decimal(str(data['main']['temp'])),
                    'humidity': Decimal(str(data['main']['humidity'])),
                    'air_pressure': Decimal(str(data['main']['pressure'])),
                    'weather_description': data['weather'][0]['description'],
                    'weather_main': data['weather'][0]['main']
                }
        except Exception as e:
            print(f"Error fetching weather: {e}")
        
        return None
    
    def get_weather_by_location_name(self, location_name: str) -> Optional[Dict]:
        """
        Get weather by location name
        First geocodes the location, then fetches weather
        """
        location_data = self.get_location_from_name(location_name)
        if not location_data:
            return None
        
        weather_data = self.get_weather_by_coordinates(
            float(location_data['latitude']),
            float(location_data['longitude'])
        )
        
        if weather_data:
            # Combine location and weather data
            return {
                **location_data,
                **weather_data
            }
        
        return location_data  # Return at least location data
    
    def get_altitude_estimate(self, lat: float, lon: float) -> Optional[int]:
        """
        Get altitude estimate using free elevation API
        Uses Open-Elevation API (free, no API key needed)
        """
        try:
            url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    return int(data['results'][0]['elevation'])
        except Exception as e:
            print(f"Error fetching altitude: {e}")
        
        return None


# Utility functions for views
def get_location_weather_data(location_name: str) -> Dict:
    """
    Main function to get comprehensive location and weather data
    Returns a dictionary with all available data
    """
    service = WeatherService()
    result = {
        'location': location_name,
        'latitude': None,
        'longitude': None,
        'altitude': None,
        'temperature': None,
        'humidity': None,
        'air_pressure': None,
        'weather_description': None,
        'error': None
    }
    
    try:
        # Get location and weather data
        data = service.get_weather_by_location_name(location_name)
        if data:
            result.update(data)
            
            # Try to get altitude if we have coordinates
            if result['latitude'] and result['longitude']:
                altitude = service.get_altitude_estimate(
                    float(result['latitude']),
                    float(result['longitude'])
                )
                if altitude:
                    result['altitude'] = altitude
    
    except Exception as e:
        result['error'] = str(e)
    
    return result


def get_weather_for_coordinates(lat: float, lon: float) -> Dict:
    """
    Get weather data for known coordinates
    """
    service = WeatherService()
    result = {
        'location': None,
        'temperature': None,
        'humidity': None,
        'air_pressure': None,
        'weather_description': None,
        'altitude': None,
        'error': None
    }
    
    try:
        # Get location name from coordinates (reverse geocoding)
        location_name = service.get_location_name_from_coordinates(lat, lon)
        if location_name:
            result['location'] = location_name
        
        # Get weather
        weather_data = service.get_weather_by_coordinates(lat, lon)
        if weather_data:
            result.update(weather_data)
        
        # Get altitude
        altitude = service.get_altitude_estimate(lat, lon)
        if altitude:
            result['altitude'] = altitude
    
    except Exception as e:
        result['error'] = str(e)
    
    return result