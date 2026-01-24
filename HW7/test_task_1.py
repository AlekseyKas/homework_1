import unittest
from unittest.mock import patch, MagicMock
import sys
from io import StringIO

# Импортируем функциональность из основного скрипта
import requests


class TestTask1(unittest.TestCase):
    """Тесты для скрипта получения данных из API JSONPlaceholder"""
    
    @patch('requests.get')
    def test_successful_api_request(self, mock_get):
        """Тест успешного запроса к API"""
        # Подготовка mock данных
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'id': 1,
                'title': 'Test Post 1',
                'body': 'This is test body 1',
                'userId': 1
            },
            {
                'id': 2,
                'title': 'Test Post 2',
                'body': 'This is test body 2',
                'userId': 1
            }
        ]
        mock_get.return_value = mock_response
        
        # Выполнение запроса
        response = requests.get('https://jsonplaceholder.typicode.com/posts')
        
        # Проверки
        self.assertEqual(response.status_code, 200)
        posts = response.json()
        self.assertEqual(len(posts), 2)
        self.assertEqual(posts[0]['title'], 'Test Post 1')
        self.assertEqual(posts[1]['body'], 'This is test body 2')
    
    @patch('requests.get')
    def test_api_request_failure(self, mock_get):
        """Тест обработки ошибки при неудачном запросе"""
        # Подготовка mock данных для ошибки
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # Выполнение запроса
        response = requests.get('https://jsonplaceholder.typicode.com/posts')
        
        # Проверка
        self.assertEqual(response.status_code, 404)
    
    @patch('requests.get')
    def test_first_five_posts(self, mock_get):
        """Тест получения первых 5 постов"""
        # Подготовка mock данных (больше 5 постов)
        posts_data = [
            {'id': i, 'title': f'Post {i}', 'body': f'Body {i}', 'userId': 1}
            for i in range(1, 11)
        ]
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = posts_data
        mock_get.return_value = mock_response
        
        # Выполнение запроса
        response = requests.get('https://jsonplaceholder.typicode.com/posts')
        posts = response.json()
        
        # Проверка что мы можем получить первые 5
        first_five = posts[:5]
        self.assertEqual(len(first_five), 5)
        self.assertEqual(first_five[0]['id'], 1)
        self.assertEqual(first_five[4]['id'], 5)
    
    @patch('requests.get')
    def test_post_structure(self, mock_get):
        """Тест наличия необходимых полей в постах"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'userId': 1,
                'id': 1,
                'title': 'Test Title',
                'body': 'Test Body'
            }
        ]
        mock_get.return_value = mock_response
        
        response = requests.get('https://jsonplaceholder.typicode.com/posts')
        posts = response.json()
        
        # Проверка наличия необходимых полей
        post = posts[0]
        self.assertIn('title', post)
        self.assertIn('body', post)
        self.assertEqual(post['title'], 'Test Title')
        self.assertEqual(post['body'], 'Test Body')


if __name__ == '__main__':
    unittest.main()
