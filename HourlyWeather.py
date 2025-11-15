class HourlyWeather:
    def __init__(self, weather_data):
        self.weather = weather_data

    def get_weather_for_today(self):
        result = []
        for i in range(24):
            result.append({
                'time': self.weather['time'][i],
                'temperature': self.weather['temperature_2m'][i],
                'precipitation_chance': self.weather['precipitation_probability'][i]
            })
            return result