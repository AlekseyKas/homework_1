import requests

def get_weather():
    """
    Получает данные о погоде для города, введённого пользователем
    """
    # API ключ (нужно получить бесплатный на https://openweathermap.org/api)
    # Используйте ваш собственный API ключ
    api_key = "0182784a2646cde8529c0e22ef1e5c82"  # Замените на ваш API ключ
    
    # URL API OpenWeatherMap
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    # Получаем название города от пользователя
    city = input("Введите название города: ").strip()
    
    if not city:
        print("Ошибка: название города не может быть пустым")
        return
    
    # Параметры запроса
    params = {
        'q': city,              # Название города
        'appid': api_key,       # API ключ
        'units': 'metric',      # Температура в Цельсиях
        'lang': 'ru'            # Язык ответа русский
    }
    
    try:
        # Отправляем GET-запрос
        response = requests.get(base_url, params=params)
        
        # Проверяем статус ответа
        if response.status_code == 200:
            # Получаем данные в формате JSON
            weather_data = response.json()
            
            # Извлекаем необходимую информацию
            city_name = weather_data['name']
            country = weather_data['sys']['country']
            temperature = weather_data['main']['temp']
            description = weather_data['weather'][0]['description']
            feels_like = weather_data['main']['feels_like']
            humidity = weather_data['main']['humidity']
            wind_speed = weather_data['wind']['speed']
            
            # Выводим информацию
            print(f"\n{'='*50}")
            print(f"Погода в городе {city_name}, {country}")
            print(f"{'='*50}")
            print(f"Описание: {description.capitalize()}")
            print(f"Температура: {temperature}°C")
            print(f"Ощущается как: {feels_like}°C")
            print(f"Влажность: {humidity}%")
            print(f"Скорость ветра: {wind_speed} м/с")
            print(f"{'='*50}\n")
            
        elif response.status_code == 404:
            print(f"Ошибка: город '{city}' не найден")
        elif response.status_code == 401:
            print("Ошибка: неверный API ключ")
        else:
            print(f"Ошибка: статус код {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("Ошибка: невозможно подключиться к серверу")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")
    except KeyError:
        print("Ошибка: неполные данные в ответе API")


if __name__ == "__main__":
    get_weather()
