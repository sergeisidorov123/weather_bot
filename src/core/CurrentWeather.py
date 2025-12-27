class CurrentWeather:
    def __init__(self, weather_data):
        self.weather = weather_data

    def __str__(self):
        return f"{self.temperature, self.windspeed, self.weathercode}"

    @property
    def temperature(self):
        return self.weather['temperature']

    @property
    def windspeed(self):
        return self.weather['windspeed']

    @property
    def weathercode(self):
        return self.weather['weathercode']