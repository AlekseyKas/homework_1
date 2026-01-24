import requests

# URL публичного API JSONPlaceholder
url = "https://jsonplaceholder.typicode.com/posts"

# Отправляем GET-запрос
response = requests.get(url)

# Проверяем статус ответа
if response.status_code == 200:
    # Получаем данные в формате JSON
    posts = response.json()
    
    # Извлекаем и выводим заголовки и тела первых 5 постов
    for i, post in enumerate(posts[:5], 1):
        print(f"Пост {i}:")
        print(f"  Заголовок: {post['title']}")
        print(f"  Тело: {post['body']}")
        print()
else:
    print(f"Ошибка: статус код {response.status_code}")
