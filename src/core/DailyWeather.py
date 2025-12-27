class DailyWeather:
    def __init__(self, daily_weather_data):
        self.weather = daily_weather_data

    def get_weather_data_tomorrow(self):
            return (
                self.weather['time'][1],
                self.weather['temperature_2m_max'][1],
                self.weather['temperature_2m_min'][1],
                self.weather['sunrise'][1],
                self.weather['sunset'][1],
                self.weather['wind_speed_10m_max'][1],
                self.weather['weathercode'][1]
            )

    def get_weather_data_forecast(self):
        forecast = []
        for i in range(len(self.weather['time'])):
            day_tuple = (
                self.weather['time'][i],
                self.weather['temperature_2m_max'][i],
                self.weather['temperature_2m_min'][i],
                self.weather['sunrise'][i],
                self.weather['sunset'][i],
                self.weather['wind_speed_10m_max'][i],
                self.weather['weathercode'][i]
            )
            forecast.append(day_tuple)
        return forecast