import unittest
import json
import os
import tempfile
import shutil
from unittest.mock import patch, mock_open, MagicMock
import sys

# Добавляем путь к основному скрипту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from threat_monitor import Config, ThreatMonitoringTool, send_email_notification


class TestConfig(unittest.TestCase):
    """Тесты для класса Config"""

    def setUp(self):
        """Создание временного файла конфигурации для тестов"""
        self.test_config = {
            "virustotal_api_key": "test_key",
            "vulners_api_key": "test_vulners_key",
            "api_timeout": 5,
            "max_ip_checks": 5,
            "log_level": "DEBUG",
            "email_enabled": True,
            "smtp_server": "smtp.test.com",
            "smtp_port": 587,
            "email_from": "test@example.com",
            "email_to": "admin@example.com",
            "email_password": "test_password"
        }

    def test_load_config_success(self):
        """Тест успешной загрузки конфигурации"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_config, f)
            config_file = f.name

        try:
            config = Config(config_file)
            self.assertEqual(config.get('virustotal_api_key'), 'test_key')
            self.assertEqual(config.get('api_timeout'), 5)
            self.assertEqual(config.get('email_enabled'), True)
        finally:
            os.unlink(config_file)

    def test_load_config_missing_file(self):
        """Тест обработки отсутствующего файла конфигурации"""
        with self.assertRaises(FileNotFoundError):
            Config('nonexistent_config.json')

    def test_load_config_invalid_json(self):
        """Тест обработки некорректного JSON"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            config_file = f.name

        try:
            with self.assertRaises(ValueError):
                Config(config_file)
        finally:
            os.unlink(config_file)

    def test_load_config_missing_required_key(self):
        """Тест обработки отсутствующего обязательного ключа"""
        config_without_key = self.test_config.copy()
        del config_without_key['virustotal_api_key']

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_without_key, f)
            config_file = f.name

        try:
            with self.assertRaises(ValueError):
                Config(config_file)
        finally:
            os.unlink(config_file)


class TestThreatMonitoringTool(unittest.TestCase):
    """Тесты для класса ThreatMonitoringTool"""

    def setUp(self):
        """Создание тестового экземпляра и mock данных"""
        self.tool = ThreatMonitoringTool()

        # Mock данные для Suricata логов с достаточным количеством алертов
        self.mock_alerts = [
            {
                "src_ip": "192.168.1.100",
                "dest_ip": "10.0.0.1",
                "alert": {
                    "category": "Web Application Attack",
                    "signature": "SQL Injection attempt",
                    "severity": 3
                },
                "timestamp": "2023-01-01T10:00:00"
            },
            {
                "src_ip": "192.168.1.100",
                "dest_ip": "10.0.0.1",
                "alert": {
                    "category": "Web Application Attack",
                    "signature": "SQL Injection attempt 2",
                    "severity": 3
                },
                "timestamp": "2023-01-01T10:01:00"
            },
            {
                "src_ip": "192.168.1.100",
                "dest_ip": "10.0.0.1",
                "alert": {
                    "category": "Web Application Attack",
                    "signature": "SQL Injection attempt 3",
                    "severity": 3
                },
                "timestamp": "2023-01-01T10:02:00"
            },
            {
                "src_ip": "192.168.1.100",
                "dest_ip": "10.0.0.1",
                "alert": {
                    "category": "Web Application Attack",
                    "signature": "SQL Injection attempt 4",
                    "severity": 3
                },
                "timestamp": "2023-01-01T10:03:00"
            },
            {
                "src_ip": "192.168.1.100",
                "dest_ip": "10.0.0.1",
                "alert": {
                    "category": "Web Application Attack",
                    "signature": "SQL Injection attempt 5",
                    "severity": 3
                },
                "timestamp": "2023-01-01T10:04:00"
            },
            {
                "src_ip": "192.168.1.100",
                "dest_ip": "10.0.0.1",
                "alert": {
                    "category": "Web Application Attack",
                    "signature": "SQL Injection attempt 7",
                    "severity": 3
                },
                "timestamp": "2023-01-01T10:06:00"
            },
            {
                "src_ip": "10.0.0.2",
                "dest_ip": "192.168.1.1",
                "alert": {
                    "category": "Attempted Information Leak",
                    "signature": "Suspicious file download",
                    "severity": 1
                },
                "timestamp": "2023-01-01T10:05:00"
            }
        ]

    def tearDown(self):
        """Очистка после тестов"""
        # Удаляем созданные директории отчетов
        if hasattr(self.tool, 'report_dir') and os.path.exists(self.tool.report_dir):
            shutil.rmtree(self.tool.report_dir)

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    def test_load_suricata_logs_empty(self, mock_file, mock_exists):
        """Тест загрузки пустых логов Suricata"""
        mock_exists.return_value = True

        self.tool.load_suricata_logs()

        self.assertEqual(len(self.tool.alerts_data), 0)

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_suricata_logs_with_data(self, mock_file, mock_exists):
        """Тест загрузки логов Suricata с данными"""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(self.mock_alerts)

        # Mock для json.load - возвращаем mock_alerts для каждого файла
        with patch('json.load', return_value=self.mock_alerts):
            self.tool.load_suricata_logs()

        # Проверяем, что данные загружены (7 алертов * 4 файла = 28)
        self.assertEqual(len(self.tool.alerts_data), 28)

    def test_analyze_ip_addresses(self):
        """Тест анализа IP адресов"""
        self.tool.alerts_data = self.mock_alerts

        self.tool.analyze_ip_addresses()

        # Проверяем, что подозрительные IP найдены (192.168.1.100 имеет 6 алертов, что > 5)
        self.assertIn("192.168.1.100", self.tool.suspicious_ips)
        self.assertEqual(self.tool.suspicious_ips["192.168.1.100"]["alert_count"], 6)

    @patch('requests.get')
    def test_check_virustotal_ip_success(self, mock_get):
        """Тест успешной проверки IP через VirusTotal"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "attributes": {
                    "last_analysis_stats": {
                        "malicious": 5,
                        "suspicious": 1,
                        "harmless": 60,
                        "undetected": 10
                    },
                    "country": "US",
                    "as_owner": "Test ISP",
                    "reputation": -10
                }
            }
        }
        mock_get.return_value = mock_response

        result = self.tool.check_virustotal_ip("192.168.1.100")

        self.assertEqual(result["ip"], "192.168.1.100")
        self.assertEqual(result["malicious"], 5)
        self.assertEqual(result["country"], "US")

    @patch('requests.get')
    def test_check_virustotal_ip_error(self, mock_get):
        """Тест обработки ошибки при проверке IP через VirusTotal"""
        mock_get.side_effect = Exception("Connection error")

        result = self.tool.check_virustotal_ip("192.168.1.100")

        self.assertEqual(result["ip"], "192.168.1.100")
        self.assertIn("error", result)

    @patch('threat_monitor.vulners_api')
    def test_search_vulners_success(self, mock_vulners):
        """Тест успешного поиска уязвимостей через Vulners"""
        mock_result = [
            {
                "cvelist": ["CVE-2023-1234"],
                "cvss": {"score": 7.5, "severity": "HIGH"},
                "title": "Test vulnerability"
            }
        ]
        mock_vulners.search.search_bulletins.return_value = mock_result

        result = self.tool.search_vulners("test query")

        self.assertNotIn("error", result)
        self.assertEqual(result["data"]["search"][0]["cvelist"][0], "CVE-2023-1234")

    @patch('threat_monitor.vulners_api')
    def test_search_vulners_error(self, mock_vulners):
        """Тест обработки ошибки при поиске через Vulners"""
        mock_vulners.search.search_bulletins.side_effect = Exception("API error")

        result = self.tool.search_vulners("test query")

        self.assertIn("error", result)

    def test_analyze_vulnerabilities_no_api(self):
        """Тест анализа уязвимостей без Vulners API"""
        self.tool.alerts_data = self.mock_alerts

        with patch.object(self.tool, 'search_vulners', return_value={"error": "API not configured"}):
            self.tool.analyze_vulnerabilities()

        # Должны быть найдены уязвимости через паттерн-матчинг
        self.assertGreater(len(self.tool.vulnerabilities), 0)

    def test_respond_to_threats(self):
        """Тест реагирования на угрозы"""
        # Настройка тестовых данных
        self.tool.suspicious_ips = {
            "192.168.1.100": {
                "alert_count": 15,
                "categories": {"Web Application Attack": 10},
                "max_severity": 3,
                "timestamps": ["2023-01-01T10:00:00"]
            }
        }

        self.tool.virustotal_reports = {
            "192.168.1.100": {
                "malicious": 10,
                "country": "RU",
                "as_owner": "Test ISP"
            }
        }

        self.tool.vulnerabilities = [
            {
                "cve_id": "CVE-2023-0001",
                "cvss_score": 9.5,
                "title": "Critical vulnerability",
                "severity": "CRITICAL"
            }
        ]

        responses = self.tool.respond_to_threats()

        # Проверяем, что реакции сгенерированы
        self.assertGreater(len(responses), 0)

        # Проверяем наличие критических реакций
        critical_responses = [r for r in responses if r.get("severity") == "critical"]
        self.assertGreater(len(critical_responses), 0)

    def test_generate_report(self):
        """Тест генерации отчета"""
        # Настройка тестовых данных
        self.tool.alerts_data = self.mock_alerts
        self.tool.suspicious_ips = {"192.168.1.100": {"alert_count": 2}}
        self.tool.virustotal_reports = {"192.168.1.100": {"malicious": 5}}
        self.tool.vulnerabilities = [{"cve_id": "CVE-2023-0001", "cvss_score": 7.5}]

        report = self.tool.generate_report()

        # Проверяем структуру отчета
        self.assertIn("timestamp", report)
        self.assertIn("summary", report)
        self.assertIn("suspicious_ips", report)
        self.assertIn("vulnerabilities", report)

        # Проверяем, что файлы созданы
        self.assertTrue(os.path.exists(os.path.join(self.tool.report_dir, "threat_report.json")))

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_create_visualizations(self, mock_close, mock_savefig):
        """Тест создания визуализаций"""
        # Настройка тестовых данных
        self.tool.suspicious_ips = {
            "192.168.1.100": {"alert_count": 10},
            "192.168.1.101": {"alert_count": 5}
        }
        self.tool.alerts_data = self.mock_alerts
        self.tool.vulnerabilities = [
            {"cvss_score": 7.5, "type": "SQL Injection"},
            {"cvss_score": 8.0, "type": "XSS"}
        ]

        self.tool.create_visualizations()

        # Проверяем, что savefig был вызван несколько раз
        self.assertGreater(mock_savefig.call_count, 0)


class TestEmailNotifications(unittest.TestCase):
    """Тесты для email уведомлений"""

    @patch('threat_monitor.EMAIL_ENABLED', False)
    def test_send_email_disabled(self):
        """Тест отправки email при отключенной функциональности"""
        result = send_email_notification("Test Subject", "Test Message")
        self.assertFalse(result)

    @patch('threat_monitor.EMAIL_ENABLED', True)
    @patch('threat_monitor.EMAIL_FROM', '')
    def test_send_email_no_from_address(self):
        """Тест отправки email без адреса отправителя"""
        result = send_email_notification("Test Subject", "Test Message")
        self.assertFalse(result)

    @patch('threat_monitor.EMAIL_ENABLED', True)
    @patch('threat_monitor.EMAIL_FROM', 'test@example.com')
    @patch('threat_monitor.EMAIL_TO', 'admin@example.com')
    @patch('threat_monitor.EMAIL_PASSWORD', 'password')
    @patch('threat_monitor.SMTP_SERVER', 'smtp.test.com')
    @patch('threat_monitor.SMTP_PORT', 587)
    @patch('smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        """Тест успешной отправки email"""
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        result = send_email_notification("Test Subject", "Test Message")

        self.assertTrue(result)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.sendmail.assert_called_once()

    @patch('threat_monitor.EMAIL_ENABLED', True)
    @patch('threat_monitor.EMAIL_FROM', 'test@example.com')
    @patch('threat_monitor.EMAIL_TO', 'admin@example.com')
    @patch('threat_monitor.EMAIL_PASSWORD', 'password')
    @patch('threat_monitor.SMTP_SERVER', 'smtp.test.com')
    @patch('threat_monitor.SMTP_PORT', 587)
    @patch('smtplib.SMTP')
    def test_send_email_smtp_error(self, mock_smtp):
        """Тест обработки ошибки SMTP"""
        mock_smtp.side_effect = Exception("SMTP connection failed")

        result = send_email_notification("Test Subject", "Test Message")

        self.assertFalse(result)


if __name__ == '__main__':
    # Настройка для более подробного вывода
    unittest.main(verbosity=2)