"""
Зарегистрироваться на https://openweathermap.org/api и написать функцию,
которая получает погоду в данный момент для города, название которого получается
 через input. https://openweathermap.org/current
"""


def metcast(city_name, country_code):
    import os
    import requests
    from dotenv import load_dotenv

    try:
        load_dotenv("D:/Learning/Project/web_scaping/.env")
        key = "key_openweathermap"
        API_key = os.getenv(key, None)
        # Ввод кода страны, для отсева дублирующихся наименований городов.
        country_code = input(' Введите код страны "Россия - RU": ')
        city_name = input(" Введите международное название города: ")
        # url для запроса
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name},{country_code}\
        &units=metric&lang=ru&appid={API_key}"
        respons = requests.get(url)
        data = respons.json()
        # pprint.pprint(data)
        # pprint.pprint(data['main'])
        description = data["weather"][0]["description"]
        temp_min = data["main"]["temp_min"]
        temp_max = data["main"]["temp_max"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        metcast_rez = f" Сегодня в городе: {city_name}, {description}.\n\
         В течение суток температура от {temp_min} до {temp_max}.\n \
         В данный момент температура {temp}, ощущается как {feels_like}.\n\
          Влажность: {humidity} Давление: {pressure}"
        return print(metcast_rez)
    except:
        print(" Нет данных по городу ", city_name)


# Проверка
if __name__ == "__main__":
    metcast("", "")
