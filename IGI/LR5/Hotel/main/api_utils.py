import requests
from django.conf import settings
from datetime import datetime

def get_weather(city="Minsk", country_code="BY"):
    """
    Get current weather for the hotel's city using OpenWeather API
    """
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': f"{city},{country_code}",
            'appid': settings.OPENWEATHER_API_KEY,
            'units': 'metric'
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        weather_info = {
            'temperature': round(data['main']['temp']),
            'description': data['weather'][0]['description'],
            'icon': data['weather'][0]['icon'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
            'timestamp': datetime.now()
        }
        return weather_info
    except Exception as e:
        return None

def get_random_cat_fact():
    """
    Get a random cat fact using Cat Facts API
    """
    try:
        response = requests.get('https://catfact.ninja/fact')
        response.raise_for_status()
        return response.json()['fact']
    except Exception as e:
        return None 