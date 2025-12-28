from collections import namedtuple


class HourlyWeather:
    def __init__(self, weather_data):
        self.weather = weather_data

    def get_weather_for_today(self, start_hour, end_hour):
        try:
            HourForecast = namedtuple('HourForecast',
                                      ['time', 'windspeed','temperature', 'precipitation', 'weathercode'])
            forecast = []
            for i in range(start_hour, end_hour):
                hour_forecast = HourForecast(
                    self.weather['time'][i],
                    self.weather['wind_speed_10m'][i],
                    self.weather['temperature_2m'][i],
                    self.weather['precipitation_probability'][i],
                    self.weather['weathercode'][i],
                )
                forecast.append(hour_forecast)
            return forecast
        except IndexError:
            return None
