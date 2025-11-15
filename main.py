from Weather import Weather

w = Weather(55.7558, 37.6173)

current = w.get_current_weather()

# для завтра нужно брать 2 элемента
tomorrow = w.get_weather_for_some_days(2)
print(current)
print(tomorrow.get_weather_data_tomorrow())

