from collections import namedtuple
from datetime import timedelta


class DailyWeather:
    def __init__(self, daily_weather_data):
        self.weather = daily_weather_data

    def get_weather_data_forecast(self):
        try:
            DayForecast = namedtuple('DayForecast',
                                 ['time', 'temperature_2m_max', 'temperature_2m_min',
                                  'wind_speed_10m_max', 'weathercode'])
            forecast = []
            for i in range(len(self.weather['time'])):
                day_tuple = DayForecast(
                    self.weather['time'][i],
                    self.weather['temperature_2m_max'][i],
                    self.weather['temperature_2m_min'][i],
                    self.weather['wind_speed_10m_max'][i],
                    self.weather['weathercode'][i]
                )
                forecast.append(day_tuple)
            return forecast
        except IndexError:
            return None