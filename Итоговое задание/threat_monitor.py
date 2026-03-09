import json
import requests
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
import os
from datetime import datetime
import vulners
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Config:
    """Класс для управления конфигурацией"""
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        """Загрузка конфигурации из файла"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Конфигурационный файл '{self.config_file}' не найден!")

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Проверка обязательных параметров
            required_keys = ['virustotal_api_key']
            for key in required_keys:
                if key not in config or not config[key]:
                    raise ValueError(f"Обязательный параметр '{key}' отсутствует в конфигурационном файле!")

            return config

        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка чтения JSON файла: {e}")

    def get(self, key, default=None):
        """Получение значения из конфигурации"""
        return self.config.get(key, default)

# Загрузка конфигурации
try:
    config = Config()
    VIRUSTOTAL_API_KEY = config.get('virustotal_api_key')
    VULNERS_API_KEY = config.get('vulners_api_key', '')  # Vulners API key (опционально)
    API_TIMEOUT = config.get('api_timeout', 10)
    MAX_IP_CHECKS = config.get('max_ip_checks', 10)
    LOG_LEVEL = config.get('log_level', 'INFO')
    EMAIL_ENABLED = config.get('email_enabled', False)
    SMTP_SERVER = config.get('smtp_server', 'smtp.gmail.com')
    SMTP_PORT = config.get('smtp_port', 587)
    EMAIL_FROM = config.get('email_from', '')
    EMAIL_TO = config.get('email_to', '')
    EMAIL_PASSWORD = config.get('email_password', '')
except (FileNotFoundError, ValueError) as e:
    print(str(e))
    print("\nСоздайте файл config.json со следующим содержимым:")
    print("""
{
  "virustotal_api_key": "ваш_ключ_здесь",
  "vulners_api_key": "",
  "api_timeout": 10,
  "max_ip_checks": 10,
  "log_level": "INFO",
  "email_enabled": false,
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "email_from": "",
  "email_to": "",
  "email_password": ""
}
""")
    exit(1)

def send_email_notification(subject, message):
    """Отправка email уведомления о угрозе"""
    if not EMAIL_ENABLED or not EMAIL_FROM or not EMAIL_TO:
        return False

    try:
        # Создание сообщения
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        msg['Subject'] = f"Threat Monitor Alert: {subject}"

        # Добавление текста сообщения
        body = f"""
Threat Monitoring System Alert
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{message}

This is an automated notification from the Threat Monitoring System.
"""
        msg.attach(MIMEText(body, 'plain'))

        # Подключение к SMTP серверу
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_FROM, EMAIL_TO, text)
        server.quit()

        print(f"Email уведомление отправлено на {EMAIL_TO}")
        return True

    except Exception as e:
        print(f"Ошибка отправки email: {e}")
        return False

# Инициализация Vulners API клиента
vulners_api = vulners.VulnersApi(api_key=VULNERS_API_KEY) if VULNERS_API_KEY else None

class ThreatMonitoringTool:
    def __init__(self):
        self.alerts_data = []
        self.suspicious_ips = {}
        self.vulnerabilities = []
        self.virustotal_reports = {}
        self.sample_dirs = [
            'suricata-sample-data/samples/first-org-conf-2015',
            'suricata-sample-data/samples/honeypot-2018',
            'suricata-sample-data/samples/wrccdc-2017',
            'suricata-sample-data/samples/wrccdc-2018'
        ]
        # Создаем уникальную директорию для результатов
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.report_dir = f'report_{timestamp}'
        os.makedirs(self.report_dir, exist_ok=True)

    def load_suricata_logs(self):
        """Загрузка логов Suricata из всех образцов"""
        print("Загрузка логов Suricata...")

        for sample_dir in self.sample_dirs:
            alerts_file = os.path.join(sample_dir, 'alerts-only.json')
            if os.path.exists(alerts_file):
                try:
                    with open(alerts_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.alerts_data.extend(data)
                        print(f"Загружено {len(data)} алертов из {sample_dir}")
                except Exception as e:
                    print(f"Ошибка загрузки {alerts_file}: {e}")

        print(f"Всего загружено {len(self.alerts_data)} алертов")

    def analyze_ip_addresses(self):
        """Анализ IP адресов на подозрительную активность"""
        print("Анализ IP адресов...")

        ip_alert_counts = Counter()
        ip_categories = defaultdict(Counter)
        ip_timestamps = defaultdict(list)

        for alert in self.alerts_data:
            src_ip = alert.get('src_ip')
            dest_ip = alert.get('dest_ip')
            category = alert.get('alert', {}).get('category', 'Unknown')
            severity = alert.get('alert', {}).get('severity', 0)
            timestamp = alert.get('timestamp')

            # Анализируем source IP
            if src_ip:
                ip_alert_counts[src_ip] += 1
                ip_categories[src_ip][category] += 1
                if timestamp:
                    ip_timestamps[src_ip].append(timestamp)

            # Анализируем destination IP (если это не локальный адрес)
            if dest_ip and not dest_ip.startswith('192.168.') and not dest_ip.startswith('10.'):
                ip_alert_counts[dest_ip] += 1
                ip_categories[dest_ip][category] += 1
                if timestamp:
                    ip_timestamps[dest_ip].append(timestamp)

        # Определяем подозрительные IP (более 5 алертов или высокая severity)
        for ip, count in ip_alert_counts.items():
            if count > 5:  # Порог подозрительной активности
                categories = ip_categories[ip]
                max_severity = max([alert.get('alert', {}).get('severity', 0)
                                  for alert in self.alerts_data
                                  if alert.get('src_ip') == ip or alert.get('dest_ip') == ip])

                self.suspicious_ips[ip] = {
                    'alert_count': count,
                    'categories': dict(categories),
                    'max_severity': max_severity,
                    'timestamps': sorted(ip_timestamps[ip]) if ip in ip_timestamps else []
                }

        print(f"Найдено {len(self.suspicious_ips)} подозрительных IP адресов")

    def check_virustotal_ip(self, ip):
        """Проверка IP через VirusTotal API"""
        try:
            url = f'https://www.virustotal.com/api/v3/ip_addresses/{ip}'
            headers = {'x-apikey': VIRUSTOTAL_API_KEY}

            response = requests.get(url, headers=headers, timeout=API_TIMEOUT)

            if response.status_code == 200:
                data = response.json()
                attributes = data.get('data', {}).get('attributes', {})

                return {
                    'ip': ip,
                    'malicious': attributes.get('last_analysis_stats', {}).get('malicious', 0),
                    'suspicious': attributes.get('last_analysis_stats', {}).get('suspicious', 0),
                    'harmless': attributes.get('last_analysis_stats', {}).get('harmless', 0),
                    'undetected': attributes.get('last_analysis_stats', {}).get('undetected', 0),
                    'country': attributes.get('country'),
                    'as_owner': attributes.get('as_owner'),
                    'reputation': attributes.get('reputation', 0)
                }
            else:
                return {'ip': ip, 'error': f'API Error: {response.status_code}'}

        except Exception as e:
            return {'ip': ip, 'error': str(e)}

    def check_suspicious_ips_virustotal(self):
        """Проверка всех подозрительных IP через VirusTotal"""
        print("Проверка подозрительных IP через VirusTotal...")

        for ip in list(self.suspicious_ips.keys())[:MAX_IP_CHECKS]:  # Ограничиваем по настройкам
            print(f"Проверка IP: {ip}")
            vt_report = self.check_virustotal_ip(ip)
            self.virustotal_reports[ip] = vt_report

            # Небольшая пауза между запросами
            import time
            time.sleep(1)

        print(f"Проверено {len(self.virustotal_reports)} IP через VirusTotal")

    def search_vulners(self, query, size=10):
        """Поиск уязвимостей через Vulners API"""
        if not vulners_api:
            return {'error': 'Vulners API key not configured'}

        try:
            results = vulners_api.search.search_bulletins(query, limit=size)
            return {'data': {'search': results}}
        except Exception as e:
            return {'error': str(e)}

    def get_cve_details(self, cve_id):
        """Получение деталей CVE через Vulners API"""
        if not vulners_api:
            return {'error': 'Vulners API key not configured'}

        try:
            result = vulners_api.get_bulletin(cve_id)
            return {'data': result}
        except Exception as e:
            print(f"Error getting CVE {cve_id}: {e}")  # Отладка
            return {'error': str(e)}

    def analyze_vulnerabilities(self):
        """Анализ уязвимостей с использованием Vulners API"""
        print("Анализ уязвимостей...")

        # Извлекаем информацию о продуктах и версиях из алертов
        products_versions = set()

        for alert in self.alerts_data:
            # Ищем упоминания продуктов в сигнатурах
            signature = alert.get('alert', {}).get('signature', '').lower()

            # Простой парсинг для извлечения потенциальных продуктов
            if 'apache' in signature:
                products_versions.add(('apache', ''))
            elif 'nginx' in signature:
                products_versions.add(('nginx', ''))
            elif 'mysql' in signature:
                products_versions.add(('mysql', ''))
            elif 'php' in signature:
                products_versions.add(('php', ''))
            elif 'windows' in signature:
                products_versions.add(('windows', ''))
            elif 'linux' in signature:
                products_versions.add(('linux', ''))

        # Ищем уязвимости для найденных продуктов
        for product, version in products_versions:
            print(f"Поиск уязвимостей для продукта: {product}")

            query = f"affectedSoftware.name:{product}"
            if version:
                query += f" AND affectedSoftware.version:{version}"

            vulners_result = self.search_vulners(query, size=5)

            if 'error' not in vulners_result:
                vulnerabilities = vulners_result.get('data', {}).get('search', [])

                for vuln_data in vulnerabilities:
                    cve_list = vuln_data.get('cvelist', [])
                    cve_id = cve_list[0] if cve_list else None
                    cvss_score = vuln_data.get('cvss', {}).get('score', 0)

                    if cve_id:
                        # Получаем детали CVE
                        cve_details = self.get_cve_details(cve_id)

                        if 'error' not in cve_details:
                            vuln_info = cve_details.get('data', {})

                            self.vulnerabilities.append({
                                'cve_id': cve_id,
                                'type': vuln_data.get('type', 'Unknown'),
                                'title': vuln_data.get('title', ''),
                                'cvss_score': cvss_score,
                                'severity': vuln_data.get('cvss', {}).get('severity', 'Unknown'),
                                'published': vuln_data.get('published', ''),
                                'description': vuln_info.get('description', ''),
                                'references': vuln_info.get('references', []),
                                'product': product,
                                'version': version
                            })

        # Если Vulners API недоступен или не настроен, используем паттерн-матчинг
        if not self.vulnerabilities:
            print("Vulners API недоступен, используем паттерн-матчинг...")

            vulnerability_patterns = {
                'SQL Injection': ['SQL', 'Injection', 'SELECT', 'UNION'],
                'XSS': ['Cross Site Scripting', 'Script', 'onmouseover'],
                'Command Execution': ['cmd.exe', 'command', 'exec'],
                'Directory Traversal': ['system32', 'protected directory'],
                'Scan': ['SCAN', 'Nessus', 'scan']
            }

            for alert in self.alerts_data:
                signature = alert.get('alert', {}).get('signature', '')
                severity = alert.get('alert', {}).get('severity', 3)

                for vuln_type, patterns in vulnerability_patterns.items():
                    if any(pattern.lower() in signature.lower() for pattern in patterns):
                        self.vulnerabilities.append({
                            'type': vuln_type,
                            'signature': signature,
                            'severity': severity,
                            'src_ip': alert.get('src_ip'),
                            'dest_ip': alert.get('dest_ip'),
                            'timestamp': alert.get('timestamp'),
                            'cvss_score': severity * 2.0  # Имитируем CVSS score
                        })
                        break

        print(f"Найдено {len(self.vulnerabilities)} потенциальных уязвимостей")

    def respond_to_threats(self):
        """Реагирование на обнаруженные угрозы"""
        print("Реагирование на угрозы...")

        responses = []

        # Реагируем на подозрительные IP
        for ip, data in self.suspicious_ips.items():
            vt_data = self.virustotal_reports.get(ip, {})

            if vt_data.get('malicious', 0) > 0:
                response = f"КРИТИЧНАЯ УГРОЗА: IP {ip} помечен как malicious в VirusTotal ({vt_data['malicious']} детекций)"
                print(response)
                # Отправка email уведомления для критических угроз
                email_subject = f"Critical Threat: Malicious IP {ip}"
                email_message = f"""IP Address: {ip}
Malicious Detections: {vt_data['malicious']}
Country: {vt_data.get('country', 'Unknown')}
AS Owner: {vt_data.get('as_owner', 'Unknown')}

Immediate action required: Block this IP address."""
                send_email_notification(email_subject, email_message)
                responses.append({
                    'type': 'ip_block',
                    'ip': ip,
                    'action': 'block',
                    'reason': f'Malicious IP detected by {vt_data["malicious"]} engines',
                    'severity': 'critical'
                })
            elif data['alert_count'] > 10:
                response = f"ПОДОЗРИТЕЛЬНАЯ АКТИВНОСТЬ: IP {ip} сгенерировал {data['alert_count']} алертов"
                print(response)
                responses.append({
                    'type': 'ip_monitor',
                    'ip': ip,
                    'action': 'monitor',
                    'reason': f'High alert count: {data["alert_count"]}',
                    'severity': 'warning'
                })

        # Реагируем на уязвимости
        for vuln in self.vulnerabilities:
            cvss_score = vuln.get('cvss_score', 0)
            vuln_type = vuln.get('type', 'Unknown')
            cve_id = vuln.get('cve_id', '')

            if cvss_score >= 9.0:
                response = f"КРИТИЧЕСКАЯ УЯЗВИМОСТЬ: {cve_id or vuln_type} (CVSS: {cvss_score}) - {vuln.get('title', '')}"
                print(response)
                # Отправка email уведомления для критических уязвимостей
                email_subject = f"Critical Vulnerability: {cve_id or vuln_type}"
                email_message = f"""Vulnerability: {cve_id or vuln_type}
CVSS Score: {cvss_score}
Title: {vuln.get('title', 'N/A')}
Severity: {vuln.get('severity', 'Unknown')}
Product: {vuln.get('product', 'Unknown')}

IMMEDIATE ACTION REQUIRED: Apply security patches immediately."""
                send_email_notification(email_subject, email_message)
                responses.append({
                    'type': 'vulnerability_critical',
                    'vulnerability': cve_id or vuln_type,
                    'cvss_score': cvss_score,
                    'title': vuln.get('title', ''),
                    'action': 'immediate_patch',
                    'severity': 'critical'
                })
            elif cvss_score >= 7.0:
                response = f"ВЫСОКОРИСКОВАЯ УЯЗВИМОСТЬ: {cve_id or vuln_type} (CVSS: {cvss_score}) - {vuln.get('title', '')}"
                print(response)
                responses.append({
                    'type': 'vulnerability_high',
                    'vulnerability': cve_id or vuln_type,
                    'cvss_score': cvss_score,
                    'title': vuln.get('title', ''),
                    'action': 'schedule_patch',
                    'severity': 'high'
                })
            elif cvss_score >= 4.0:
                response = f"СРЕДНИЙ РИСК: {cve_id or vuln_type} (CVSS: {cvss_score})"
                print(response)
                responses.append({
                    'type': 'vulnerability_medium',
                    'vulnerability': cve_id or vuln_type,
                    'cvss_score': cvss_score,
                    'action': 'monitor',
                    'severity': 'medium'
                })

        return responses

    def generate_report(self):
        """Генерация отчета в JSON формате"""
        print("Генерация отчета...")

        # Определяем, использовался ли Vulners API
        vulners_used = any('cve_id' in v for v in self.vulnerabilities)

        report = {
            'timestamp': datetime.now().isoformat(),
            'analysis_config': {
                'virustotal_enabled': bool(VIRUSTOTAL_API_KEY),
                'vulners_enabled': bool(VULNERS_API_KEY and vulners_used),
                'max_ip_checks': MAX_IP_CHECKS,
                'api_timeout': API_TIMEOUT
            },
            'summary': {
                'total_alerts': len(self.alerts_data),
                'suspicious_ips_count': len(self.suspicious_ips),
                'vulnerabilities_count': len(self.vulnerabilities),
                'virustotal_checks': len(self.virustotal_reports),
                'vulners_cves_found': len([v for v in self.vulnerabilities if 'cve_id' in v])
            },
            'suspicious_ips': self.suspicious_ips,
            'virustotal_reports': self.virustotal_reports,
            'vulnerabilities': self.vulnerabilities,
            'top_alert_categories': dict(Counter([alert.get('alert', {}).get('category', 'Unknown')
                                                for alert in self.alerts_data]).most_common(10)),
            'top_signatures': dict(Counter([alert.get('alert', {}).get('signature', 'Unknown')
                                          for alert in self.alerts_data]).most_common(10)),
            'vulnerability_stats': {
                'by_severity': dict(Counter([v.get('severity', 'Unknown') for v in self.vulnerabilities])),
                'by_type': dict(Counter([v.get('type', 'Unknown') for v in self.vulnerabilities])),
                'high_risk_count': len([v for v in self.vulnerabilities if v.get('cvss_score', 0) >= 7.0])
            }
        }

        # Сохраняем отчет в JSON
        json_path = os.path.join(self.report_dir, 'threat_report.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Сохраняем в CSV для удобства анализа
        if self.vulnerabilities:
            vuln_df = pd.DataFrame(self.vulnerabilities)
            csv_path = os.path.join(self.report_dir, 'vulnerabilities_report.csv')
            vuln_df.to_csv(csv_path, index=False)

        print(f"Отчет сохранен в {json_path} и {csv_path}")

        return report

    def create_visualizations(self):
        """Создание графиков для визуализации результатов"""
        print("Создание визуализаций...")

        # График 1: Топ-10 подозрительных IP по количеству алертов
        if self.suspicious_ips:
            ip_data = sorted(self.suspicious_ips.items(), key=lambda x: x[1]['alert_count'], reverse=True)[:10]
            ips = [ip for ip, _ in ip_data]
            counts = [data['alert_count'] for _, data in ip_data]

            plt.figure(figsize=(12, 6))
            plt.bar(ips, counts)
            plt.title('Топ-10 подозрительных IP адресов')
            plt.xlabel('IP адрес')
            plt.ylabel('Количество алертов')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(os.path.join(self.report_dir, 'suspicious_ips_chart.png'), dpi=300, bbox_inches='tight')
            plt.close()

        # График 2: Распределение категорий алертов
        categories = Counter([alert.get('alert', {}).get('category', 'Unknown')
                            for alert in self.alerts_data])

        if categories:
            plt.figure(figsize=(10, 8))
            plt.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%')
            plt.title('Распределение категорий алертов')
            plt.axis('equal')
            plt.savefig(os.path.join(self.report_dir, 'alert_categories_pie.png'), dpi=300, bbox_inches='tight')
            plt.close()

        # График 3: CVSS scores уязвимостей
        if self.vulnerabilities:
            cvss_scores = [v['cvss_score'] for v in self.vulnerabilities]

            plt.figure(figsize=(10, 6))
            plt.hist(cvss_scores, bins=10, edgecolor='black')
            plt.title('Распределение CVSS scores уязвимостей')
            plt.xlabel('CVSS Score')
            plt.ylabel('Количество уязвимостей')
            plt.grid(True, alpha=0.3)
            plt.savefig(os.path.join(self.report_dir, 'vulnerabilities_cvss_histogram.png'), dpi=300, bbox_inches='tight')
            plt.close()

        # График 4: Распределение типов уязвимостей
        if self.vulnerabilities:
            vuln_types = Counter([v.get('type', 'Unknown') for v in self.vulnerabilities])

            plt.figure(figsize=(12, 6))
            plt.bar(vuln_types.keys(), vuln_types.values())
            plt.title('Распределение типов уязвимостей')
            plt.xlabel('Тип уязвимости')
            plt.ylabel('Количество')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(os.path.join(self.report_dir, 'vulnerability_types_chart.png'), dpi=300, bbox_inches='tight')
            plt.close()

        # График 5: CVSS scores по severity уровням
        if self.vulnerabilities:
            severity_counts = Counter([v.get('severity', 'Unknown') for v in self.vulnerabilities])

            plt.figure(figsize=(8, 8))
            plt.pie(severity_counts.values(), labels=severity_counts.keys(), autopct='%1.1f%%')
            plt.title('Распределение severity уровней уязвимостей')
            plt.axis('equal')
            plt.savefig(os.path.join(self.report_dir, 'vulnerability_severity_pie.png'), dpi=300, bbox_inches='tight')
            plt.close()

        print(f"Графики сохранены в директорию {self.report_dir}/")

    def run_analysis(self):
        """Запуск полного анализа"""
        print("Запуск анализа угроз...")
        print("=" * 50)

        # Этап 1: Загрузка данных
        self.load_suricata_logs()

        # Этап 2: Анализ IP адресов
        self.analyze_ip_addresses()

        # Этап 3: Проверка через VirusTotal
        self.check_suspicious_ips_virustotal()

        # Этап 4: Анализ уязвимостей
        self.analyze_vulnerabilities()

        # Этап 5: Реагирование на угрозы
        responses = self.respond_to_threats()

        # Этап 6: Генерация отчета
        report = self.generate_report()

        # Этап 7: Визуализация
        self.create_visualizations()

        print("=" * 50)
        print("Анализ завершен!")
        print(f"Обработано {len(self.alerts_data)} алертов")
        print(f"Найдено {len(self.suspicious_ips)} подозрительных IP")
        print(f"Обнаружено {len(self.vulnerabilities)} уязвимостей")
        print(f"Созданы отчеты и графики")

        return report, responses


if __name__ == "__main__":
    # Создаем и запускаем инструмент мониторинга
    monitor = ThreatMonitoringTool()
    report, responses = monitor.run_analysis()

    print("\nКраткое описание работы скрипта:")
    print("- Загружает логи Suricata из образцов данных")
    print("- Анализирует IP адреса на подозрительную активность")
    print("- Проверяет подозрительные IP через VirusTotal API")
    print("- Ищет уязвимости через Vulners API и паттерн-матчинг")
    print("- Имитирует реагирование на угрозы с учетом CVSS scores")
    print("- Отправляет email уведомления для критических угроз")
    print("- Генерирует JSON и CSV отчеты с детальной информацией")
    print("- Создает визуализации результатов анализа")