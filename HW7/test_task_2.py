import unittest
from unittest.mock import patch, MagicMock
import requests
from io import StringIO
import sys


class TestTask2(unittest.TestCase):
    """Тесты для скрипта получения данных о погоде из OpenWeatherMap API"""
    
    @patch('builtins.input', return_value='Moscow')
    @patch('requests.get')
    def test_successful_weather_request(self, mock_get, mock_input):
        """Тест успешного получения данных о погоде"""
        # Подготовка mock данных
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'name': 'Moscow',
            'sys': {'country': 'RU'},
            'main': {
                'temp': 5.0,
                'feels_like': 2.0,
                'humidity': 70
            },
            'weather': [{'description': 'облачно'}],
            'wind': {'speed': 3.5}
        }
        mock_get.return_value = mock_response
        
        # Выполнение функции
        from task_2 import get_weather
        
        with patch('sys.stdout', new=StringIO()):
            get_weather()
        
        # Проверки
        self.assertEqual(mock_response.status_code, 200)
        data = mock_response.json()
        self.assertEqual(data['name'], 'Moscow')
        self.assertEqual(data['main']['temp'], 5.0)
    
    @patch('builtins.input', return_value='')
    def test_empty_city_input(self, mock_input):
        """Тест обработки пустого ввода города"""
        from task_2 import get_weather
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            get_weather()
            output = fake_out.getvalue()
            self.assertIn("Ошибка: название города не может быть пустым", output)
    
    @patch('builtins.input', return_value='NonexistentCity123')
    @patch('requests.get')
    def test_city_not_found(self, mock_get, mock_input):
        """Тест обработки ошибки города не найден (404)"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        from task_2 import get_weather
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            get_weather()
            output = fake_out.getvalue()
            self.assertIn("не найден", output)
    
    @patch('builtins.input', return_value='London')
    @patch('requests.get')
    def test_invalid_api_key(self, mock_get, mock_input):
        """Тест обработки ошибки неверного API ключа (401)"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        from task_2 import get_weather
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            get_weather()
            output = fake_out.getvalue()
            self.assertIn("неверный API ключ", output)
    
    @patch('builtins.input', return_value='Berlin')
    @patch('requests.get')
    def test_connection_error(self, mock_get, mock_input):
        """Тест обработки ошибки подключения"""
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        from task_2 import get_weather
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            get_weather()
            output = fake_out.getvalue()
            self.assertIn("невозможно подключиться", output)
    
    @patch('builtins.input', return_value='Paris')
    @patch('requests.get')
    def test_weather_data_extraction(self, mock_get, mock_input):
        """Тест корректного извлечения данных о погоде"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'name': 'Paris',
            'sys': {'country': 'FR'},
            'main': {
                'temp': 8.5,
                'feels_like': 6.0,
                'humidity': 65
            },
            'weather': [{'description': 'ясно'}],
            'wind': {'speed': 2.1}
        }
        mock_get.return_value = mock_response
        
        from task_2 import get_weather
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            get_weather()
            output = fake_out.getvalue()
            
            # Проверяем наличие информации в выводе
            self.assertIn("Paris", output)
            self.assertIn("FR", output)
            self.assertIn("8.5", output)
    
    @patch('builtins.input', return_value='Tokyo')
    @patch('requests.get')
    def test_api_parameters(self, mock_get, mock_input):
        """Тест что запрос отправляется с правильными параметрами"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'name': 'Tokyo',
            'sys': {'country': 'JP'},
            'main': {'temp': 15.0, 'feels_like': 14.0, 'humidity': 60},
            'weather': [{'description': 'переменная облачность'}],
            'wind': {'speed': 4.0}
        }
        mock_get.return_value = mock_response
        
        from task_2 import get_weather
        
        with patch('sys.stdout', new=StringIO()):
            get_weather()
        
        # Проверяем что GET был вызван
        mock_get.assert_called_once()
        
        # Проверяем параметры
        call_args = mock_get.call_args
        params = call_args.kwargs['params']
        
        self.assertEqual(params['q'], 'Tokyo')
        self.assertEqual(params['units'], 'metric')
        self.assertEqual(params['lang'], 'ru')
        self.assertIn('appid', params)


if __name__ == '__main__':
    unittest.main()
