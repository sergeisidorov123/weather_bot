from Weather import Weather

w = Weather(55.7558, 37.6173)

current = w.get_current_weather()

# для завтра нужно брать 2 элемента
tomorrow = w.get_weather_for_some_days(2)

today = w.get_hourly_weather("2025-11-16")
# print(current)
# print(tomorrow.get_weather_data_tomorrow())
print(today.get_weather_for_today(12, 11))

