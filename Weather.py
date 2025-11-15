from turtledemo.penrose import start

import requests
import json
from CurrentWeather import CurrentWeather
from DailyWeather import DailyWeather
from HourlyWeather import HourlyWeather


class Weather:
    WEATHER_CODES = {
        0: "Ясно", 1: "Преимущественно ясно", 2: "Переменная облачность",
        3: "Пасмурно", 45: "Туман", 48: "Инейный туман",
        51: "Лежащая морось", 53: "Умеренная морось", 55: "Сильная морось",
        61: "Небольшой дождь", 63: "Умеренный дождь", 65: "Сильный дождь",
        80: "Ливень", 95: "Гроза", 96: "Гроза с градом"
    }

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

        current = data['current_weather']
        return CurrentWeather(current)

    def get_weather_for_some_days(self, days):
        data = self._make_request({
            "latitude": self.latitude,
            "longitude": self.longitude,
            'daily': 'temperature_2m_max,temperature_2m_min,weathercode,sunrise,sunset,wind_speed_10m_max',
            "forecast_days": days
        })

        return DailyWeather(data['daily'])

    def get_hourly_weather(self, date):
        data = self._make_request({
            'latitude': self.latitude,
            'longitude': self.longitude,
            'hourly': 'temperature_2m,weathercode,precipitation_probability,wind_speed_10m',
            "start_date": date,
            "end_date": date
        })

        return HourlyWeather(data['hourly'])
