import requests
import json

# https://api.open-meteo.com/v1/forecast?
#   latitude=55.7558&
#   longitude=37.6173&
#   daily=temperature_2m_max,temperature_2m_min,weathercode&
#   timezone=auto&
#   forecast_days=7

# - для многодневгого

class Weather:
    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, longitude, latitude):
        self.longitude = longitude
        self.latitude = latitude

    def _make_request(self, params):
        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        return response.json()

    def get_current_weather(self):
        data = self._make_request({
            "latitude": self.latitude,
            "longitude": self.longitude,
            "current_weather": 'true'
        })

        return data['current_weather']

    def get_weather_for_some_days(self, days):
        data = self._make_request({
            "latitude": self.latitude,
            "longitude": self.longitude,
            'daily': 'temperature_2m_max,temperature_2m_min,weathercode,sunrise,sunset',
            "forecast_days": days
        })

        return data['daily']


