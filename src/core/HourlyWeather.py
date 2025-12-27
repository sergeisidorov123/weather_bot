class HourlyWeather:
    def __init__(self, weather_data):
        self.weather = weather_data

    def get_weather_for_today(self, start_hour, end_hour):
        try:
            forecast = []
            hour_tuple = ()
            for i in range(start_hour, end_hour):
                hour_tuple = (
                    self.weather['time'][i],
                    self.weather['temperature_2m'][i],
                    self.weather['precipitation_probability'][i],
                    self.weather['weathercode'][i],
                )
                forecast.append(hour_tuple)
            return forecast
        except IndexError:
            return None
