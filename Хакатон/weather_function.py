import requests

def get_weather(city):
    url = (f'https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&lang=ru&appid=79d1ca96933b0328e1c7e3e7a26cb347')
    weather_data = requests.get(url).json() #здесь данные с API преобразуются в понятные для нас
    if weather_data['cod'] != 200:
        return False, "В работе с API возникла ошибка."
    else:
        wind_speed = round(weather_data['wind']['speed']) #здесь указывается путь для получения данных по скорости ветра
        temperature = round(weather_data['main']['temp']) #здесь указывается путь для поулчения данных по температуре
        temperature_feels = round(weather_data['main']['feels_like']) #здесь указывается путь для получения данных по ощущению температуры
    # в функциях ниже выводим сообщения
        response = 'Сейчас в городе ' + city + ' ' + str(temperature) + ' градусов\n'
        response += 'Ощущается как ' + str(temperature_feels) + ' градусов\n'
        response += 'Скорость ветра ' + str(wind_speed) + ' м/с'
        return True, response




