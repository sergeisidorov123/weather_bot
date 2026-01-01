import requests
from src.core.CurrentWeather import CurrentWeather
from src.core.DailyWeather import DailyWeather
from src.core.HourlyWeather import HourlyWeather


class Weather:
    WEATHER_CODES = {
        0: "Ясно",
        1: "Преимущественно ясно",
        2: "Переменная облачность",
        3: "Пасмурно",
        45: "Туман",
        48: "Инейный туман",
        51: "Легкая морось",
        53: "Умеренная морось",
        55: "Сильная морось",
        56: "Легкая ледяная морось",
        57: "Сильная ледяная морось",
        61: "Небольшой дождь",
        63: "Умеренный дождь",
        65: "Сильный дождь",
        66: "Легкий ледяной дождь",
        67: "Сильный ледяной дождь",
        71: "Небольшой снег",
        73: "Умеренный снег",
        75: "Сильный снег",
        77: "Град",
        80: "Небольшой ливень",
        81: "Умеренный ливень",
        82: "Сильный ливень",
        85: "Небольшой снегопад",
        86: "Сильный снегопад",
        95: "Гроза",
        96: "Гроза с небольшим градом",
        99: "Гроза с сильным градом"
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
        current['weathercode'] = self.WEATHER_CODES[current['weathercode']]
        return CurrentWeather(current)

    def get_weather_for_some_days(self, start_date, end_date):
        data = self._make_request({
            "latitude": self.latitude,
            "longitude": self.longitude,
            'daily': 'temperature_2m_max,temperature_2m_min,weathercode,wind_speed_10m_max',
            "start_date": start_date,
            "end_date": end_date
        })
        for day in range(len(data['daily']['time'])):
            data['daily']['weathercode'][day] = self.WEATHER_CODES[data['daily']['weathercode'][day]]
        return DailyWeather(data['daily'])

    def get_hourly_weather(self, date):
        data = self._make_request({
            'latitude': self.latitude,
            'longitude': self.longitude,
            'hourly': 'temperature_2m,weathercode,precipitation_probability,wind_speed_10m',
            "start_date": date,
            "end_date": date
        })
        for i in range(24):
             data['hourly']['weathercode'][i] = self.WEATHER_CODES[data['hourly']['weathercode'][i]]
        return HourlyWeather(data['hourly'])
