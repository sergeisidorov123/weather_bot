from Weather import Weather

w = Weather(38, 56)

current = w.get_current_weather()

tomorrow = w.get_weather_for_some_days(5)
today = w.get_hourly_weather("2025-11-22")
print(current)
print(tomorrow.get_weather_data_tomorrow())
print(tomorrow.get_weather_data_forecast())
print(today.get_weather_for_today(10, 12))

#TODO
# обработка ошибок
# город по кордам